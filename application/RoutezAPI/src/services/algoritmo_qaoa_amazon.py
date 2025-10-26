# Versão HÍBRIDA: Otimização local (clássica) + Execução final na QPU (quântica)
import pennylane as qml
from pennylane import numpy as np
from scipy.optimize import minimize
from services.distancia import Distancia
from services.tempo_execucao import TempoExecucao
from core.abstract.algoritmo_base import AlgoritmoBase
from typing import List, Tuple
from core.dto.algoritmos_dto import PontoDTO
from services.sequencia_execucao import SequenciaExecucao
from services.metrica_preco import MetricaPreco
from services.metrica_memoria import UsoMemoria
from services.metrica_circuito_img import CircuitoQuanticoImagem
from pennylane.devices  import Device
from services.metrica_tasks import MetricaQuantidadeTaskQuanticas
from services.metrica_shots import MetricaQuantidadeShotsQuanticas
from services.metrica_qubits import MetricaQubits
class AlgoritmoQAOAAmazon(AlgoritmoBase):
    """
    Implementação do QAOA para o TSP usando PennyLane em uma abordagem híbrida.
    
    1. Otimização de parâmetros: Realizada em um simulador local de alta performance.
    2. Amostragem final: Executada no simulador ou em uma QPU real da AWS Braket.
    """
    TIPO_ALGORITMO = "QAOA REAL"
    locale = ''
    # --- Painel de Controle ---
    _REPS = 1
    _OPTIMIZER_MAX_ITER = 50
    _OPTIMIZER_METHOD = 'Nelder-Mead'
    _PENALTY_FACTOR = 1000.0
    _TOTAL_SHOTS_FINAL = 2_000

    # --- CHAVE PRINCIPAL: Alterne entre Simulador e Nuvem ---
    _USE_QPU = False  # Mude para True para executar na AWS. Requer ARN e S3 preenchidos.
    
    # --- Configurações para Execução em Hardware Real (AWS Braket) ---
    _QPU_ARN = "lightning.qubit"  # PREENCHA com o ARN da QPU desejada
    _S3_BUCKET = "" # PREENCHA com o nome do seu bucket S3
    
    def __init__(self):
        super().__init__()
        self.circuito_transpilado = None

    def _log(self, message: str, level: int = 0):
        """Função auxiliar para logs formatados."""
        indent = "  " * level
        print(f"{indent}{message}")

    # --------------------------------------------------------------------------
    # FLUXO PRINCIPAL DE EXECUÇÃO
    # --------------------------------------------------------------------------
    def _executar_logica_algoritmo(self, dist_matrix: np.ndarray, pontos: List[PontoDTO]) -> Tuple[List[PontoDTO], float]:
        """Orquestra a execução completa do algoritmo QAOA híbrido."""
        self._log("=====================================================")
        self._log("🚀 INICIANDO ALGORITMO QAOA HÍBRIDO (PENNYLANE)")
        self._log("=====================================================")
        cost_h, mixer_h, n_qubits = self._1_preparar_problema(dist_matrix)
        optimal_params = self._2_otimizacao_local(cost_h, mixer_h, n_qubits)
        counts = self._3_amostragem_final(optimal_params, cost_h, mixer_h, n_qubits)
        rota_final, distancia_final = self._4_processar_resultados(counts, dist_matrix, pontos)
        self._log("\n✅ ALGORITMO QAOA HÍBRIDO CONCLUÍDO!")
        return rota_final, distancia_final

    # --------------------------------------------------------------------------
    # PASSOS DETALHADOS DO FLUXO
    # --------------------------------------------------------------------------
    def _1_preparar_problema(self, dist_matrix: np.ndarray) -> Tuple[qml.Hamiltonian, qml.Hamiltonian, int]:
        """Cria os Hamiltonianos de custo e mixer para o problema do TSP."""
        self._log("\n--- PASSO 1: Preparando o Problema e os Hamiltonianos ---")
        n_cidades = len(dist_matrix)
        n_qubits = n_cidades * n_cidades
        self._log(f"Problema de {n_cidades} cidades, necessitando de {n_qubits} qubits.", 1)
        cost_h, mixer_h = self.adjacency_matrix_to_hamiltonian(dist_matrix)
        self._log(f"Hamiltoniano de custo criado com {len(cost_h.ops)} termos.", 1)
        self._log(f"Hamiltoniano de mixer criado.", 1)
        return cost_h, mixer_h, n_qubits

    def _2_otimizacao_local(self, cost_h: qml.Hamiltonian, mixer_h: qml.Hamiltonian, n_qubits: int) -> np.ndarray:
        """Executa a otimização de parâmetros em um simulador local."""
        self._log(f"\n--- PASSO 2: Otimização em Simulador Local ---")
        # self._log(f"Otimizador: '{self._OPTIMIZER_METHOD}', p={self._REPS}, max_iter={self._MAX_ITER_OTIMIZACAO}", 1)
        dev_optimizer = qml.device("lightning.qubit", wires=n_qubits)
        @qml.qnode(dev_optimizer)
        def cost_qnode(params):
            self._qaoa_circuito(params, cost_h, mixer_h, n_qubits)
            return qml.expval(cost_h)
        initial_params = np.random.uniform(0, 2 * np.pi, 2 * self._REPS)
        result = minimize(cost_qnode, initial_params, method=self._OPTIMIZER_METHOD, options={'maxiter': self._OPTIMIZER_MAX_ITER})
        optimal_params = result.x
        self._log("Otimização local concluída!", 1)
        self._log(f"  - Custo final (energia): {result.fun:.4f}", 2)
        self._log(f"  - Parâmetros ótimos encontrados: {optimal_params}", 2)
        return optimal_params

    def _3_amostragem_final(self, optimal_params: np.ndarray, cost_h: qml.Hamiltonian, mixer_h: qml.Hamiltonian, n_qubits: int) -> dict:
        """Executa o circuito final com os parâmetros otimizados para obter amostras."""
        self._log("\n--- PASSO 3: Amostragem Final ---")
        
        try:
            # 1. O dispositivo é obtido da mesma forma (ele já está configurado com 'shots')
            dev_sampler = self._get_sampling_device(n_qubits)
        except ValueError as e:
            self._log(f"Falha ao criar o dispositivo de amostragem: {e}", 1)
            return {}
            
        self.circuito_transpilado = dev_sampler
        
        # 2. O QNode agora é definido para retornar as contagens diretamente
        @qml.qnode(dev_sampler)
        def count_qnode(params):
            """Este QNode retorna um dicionário de contagens."""
            self._qaoa_circuito(params, cost_h, mixer_h, n_qubits)
            return qml.counts(wires=range(n_qubits)) # ALTERAÇÃO PRINCIPAL AQUI

        self._log("Executando o circuito no dispositivo selecionado...", 1)
        
        # 3. A chamada ao QNode agora retorna diretamente o dicionário de contagens.
        #    Formato do dicionário: {'01011': 50, '11001': 35, ...}
        counts = count_qnode(optimal_params)
        
        self._log("Execução final concluída.", 1)
        
        # 4. A linha de conversão manual foi REMOVIDA, pois não é mais necessária.
        
        return counts

    def _4_processar_resultados(self, counts: dict, dist_matrix: np.ndarray, pontos: List[PontoDTO]) -> Tuple[List[PontoDTO], float]:
        """Decodifica os resultados da amostragem para encontrar a melhor rota."""
        self._log("\n--- PASSO 4: Processando Resultados ---")
        if not counts:
             self._log("AVISO: Nenhuma contagem recebida da amostragem. Não é possível processar.", 1)
             return [], 0.0
        n_cidades = len(dist_matrix)
        sorted_counts = sorted([item for item in counts.items() if item[1] > 0], key=lambda x: x[1], reverse=True)
        self._log("Top 5 resultados mais prováveis:", 1)
        for i, (bitstring, count) in enumerate(sorted_counts[:5]):
            prob = (count / self._TOTAL_SHOTS_FINAL) * 100
            self._log(f"{i+1}. '{bitstring}': {count} vezes ({prob:.1f}%)", 2)
        ordem_bruta, _ = self.decode_solution(counts, n_cidades)
        if not ordem_bruta:
            self._log("AVISO: Nenhuma rota válida foi decodificada.", 1)
            return [], 0.0
        ordem_normalizada = self._normalizar_rota(ordem_bruta)
        distancia_final = self.calculate_path_distance(ordem_normalizada, dist_matrix)
        self._log(f"\nRota bruta decodificada: {ordem_bruta}", 1)
        self._log(f"Rota final (normalizada): {ordem_normalizada}", 1)
        self._log(f"Distância do caminho: {distancia_final:.2f}", 1)
        rota_dto = [pontos[idx] for idx in ordem_normalizada]
        rota_dto.append(pontos[ordem_normalizada[0]])
        return rota_dto, distancia_final

    # --------------------------------------------------------------------------
    # FÁBRICA DE DISPOSITIVOS E DEFINIÇÃO DE CIRCUITO
    # --------------------------------------------------------------------------
    def _get_sampling_device(self, n_qubits: int) -> Device: # CORRECTED TYPE HINT
        """
        Fábrica de dispositivos: cria e retorna o dispositivo PennyLane apropriado
        com base nas configurações da classe (_USE_QPU).
        """
        if not self._USE_QPU:
            self._log(f"Executando em simulador local com {self._TOTAL_SHOTS_FINAL} shots.", 1)
            return qml.device("lightning.qubit", wires=n_qubits, shots=self._TOTAL_SHOTS_FINAL)
        
        self._log(f"Tentando configurar dispositivo de nuvem: {self._QPU_ARN}", 1)
        if not self._QPU_ARN or not self._S3_BUCKET:
            self._log("❌ ERRO: Para usar a QPU, _QPU_ARN e _S3_BUCKET devem ser preenchidos.", 2)
            raise ValueError("Configuração da AWS para a QPU está incompleta.")
        s3_folder = (self._S3_BUCKET, "qaoa-tsp-results")
        self._log(f"Enviando para a QPU: {self._QPU_ARN}", 2)
        self._log(f"Resultados serão salvos em S3: {s3_folder}", 2)
        return qml.device(
            "default.qubit",
            device_arn=self._QPU_ARN,
            wires=n_qubits,
            s3_destination_folder=s3_folder,
            shots=self._TOTAL_SHOTS_FINAL,
        )
        
    def _qaoa_circuito(self, params: np.ndarray, cost_h: qml.Hamiltonian, mixer_h: qml.Hamiltonian, n_qubits: int):
        """
        Define a estrutura do circuito QAOA (ansatz) usando operações explícitas
        para garantir compatibilidade com hardware real (AWS Braket).
        """
        # O Scipy Optimizer trabalha com um array 1D, então separamos os parâmetros aqui.
        gammas = params[:self._REPS]
        betas = params[self._REPS:]
        
        # 1. Inicia em estado de superposição uniforme (sem alteração)
        for i in range(n_qubits):
            qml.Hadamard(wires=i)
            
        # 2. Aplica as camadas de custo e mixer
        for i in range(self._REPS):
            # --- CORREÇÃO APLICADA AQUI ---
            # Substituímos qml.qaoa.cost_layer pela sua forma explícita e robusta.
            qml.ApproxTimeEvolution(cost_h, gammas[i], 1)
            
            # Substituímos qml.qaoa.mixer_layer pela sua decomposição em gates RX.
            # Isso é matematicamente equivalente para o mixer padrão e muito mais compatível.
            for wire_idx in range(n_qubits):
                qml.RX(2 * betas[i], wires=wire_idx)
            
    def adjacency_matrix_to_hamiltonian(self, adj_matrix: np.ndarray) -> Tuple[qml.Hamiltonian, qml.Hamiltonian]:
        """Converte a matriz de adjacência do TSP para Hamiltonianos de custo e mixer."""
        n = len(adj_matrix)
        n_qubits = n * n
        cost_ops, cost_coeffs = [], []

        for i in range(n):
            for j in range(i + 1, n):
                for k in range(n):
                    q1_idx = i * n + k
                    q2_idx = j * n + ((k + 1) % n)
                    op = qml.PauliZ(q1_idx) @ qml.PauliZ(q2_idx)
                    cost_ops.append(op)
                    cost_coeffs.append(0.5 * adj_matrix[i][j])
        
        for i in range(n):
            for k in range(n):
                for l in range(k + 1, n):
                    op = qml.PauliZ(i * n + k) @ qml.PauliZ(i * n + l)
                    cost_ops.append(op)
                    cost_coeffs.append(self._PENALTY_FACTOR)

        for k in range(n):
            for i in range(n):
                for j in range(i + 1, n):
                    op = qml.PauliZ(i * n + k) @ qml.PauliZ(j * n + k)
                    cost_ops.append(op)
                    cost_coeffs.append(self._PENALTY_FACTOR)
        
        cost_hamiltonian = qml.Hamiltonian(cost_coeffs, cost_ops)
        
        mixer_ops = [qml.PauliX(i) for i in range(n_qubits)]
        mixer_hamiltonian = qml.Hamiltonian([-0.5] * n_qubits, mixer_ops)
        
        return cost_hamiltonian, mixer_hamiltonian

    # --------------------------------------------------------------------------
    # MÉTODOS DE DECODIFICAÇÃO E CÁLCULO
    # --------------------------------------------------------------------------
    def _normalizar_rota(self, ordem: List[int]) -> List[int]:
        """Garante que a rota (ciclo) sempre comece pela cidade 0."""
        if not ordem or 0 not in ordem:
            return ordem
        idx_zero = ordem.index(0)
        return ordem[idx_zero:] + ordem[:idx_zero]

    def decode_solution(self, counts: dict, n: int) -> Tuple[List[int], np.ndarray]:
        """Decodifica a string de bits mais provável em uma rota de TSP."""
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        for bitstring, _ in sorted_counts[:20]:
            if len(bitstring) != n*n: continue
            solution_matrix = np.reshape([int(b) for b in bitstring], (n, n))
            if all(np.sum(solution_matrix, axis=0) == 1) and all(np.sum(solution_matrix, axis=1) == 1):
                order = [np.argmax(col) for col in solution_matrix.T]
                return order, solution_matrix
        
        if not sorted_counts: return [], np.zeros((n,n))
        best_bitstring = sorted_counts[0][0]
        solution_matrix = np.reshape([int(b) for b in best_bitstring], (n, n))
        order = self.fix_invalid_solution(solution_matrix, n)
        fixed_matrix = np.zeros((n, n), dtype=int)
        for pos, city in enumerate(order):
            fixed_matrix[city][pos] = 1
        return order, fixed_matrix

    def fix_invalid_solution(self, solution_matrix: np.ndarray, n: int) -> List[int]:
        """Heurística para forçar uma matriz de solução a se tornar um tour válido."""
        order = []
        used_cities = set()
        for pos in range(n):
            possible_cities = [(city, solution_matrix[city][pos]) for city in range(n) if city not in used_cities]
            if possible_cities:
                best_city = max(possible_cities, key=lambda item: item[1])[0]
                order.append(best_city)
                used_cities.add(best_city)
        if len(order) < n:
            order.extend(list(set(range(n)) - used_cities))
        return order

    def calculate_path_distance(self, order: List[int], adj_matrix: np.ndarray) -> float:
        """Calcula a distância total de uma rota, incluindo o retorno à origem."""
        if not order: return 0.0
        dist = 0.0
        for i in range(len(order)):
            u, v = order[i], order[(i + 1) % len(order)]
            dist += adj_matrix[u][v]
        return dist

# --------------------------------------------------------------------------
# FUNÇÃO FACTORY
# --------------------------------------------------------------------------
def get_algoritmo_QAOA_Amazon() -> AlgoritmoQAOAAmazon:
    service = AlgoritmoQAOAAmazon()
    service.adicionar_metrica(TempoExecucao())
    service.adicionar_metrica(SequenciaExecucao())
    service.adicionar_metrica(Distancia())
    service.adicionar_metrica(MetricaPreco(tipo_recurso='qpu', provider='anka'))
    service.adicionar_metrica(MetricaQubits(tipo="QAOA"))
    service.adicionar_metrica(MetricaQuantidadeTaskQuanticas())
    service.adicionar_metrica(MetricaQuantidadeShotsQuanticas())

    # service.adicionar_metrica(UsoMemoria())
    # A métrica de imagem do circuito pode não funcionar tão bem com a estrutura do PennyLane
    # service.adicionar_metrica(CircuitoQuanticoImagem())
    return service