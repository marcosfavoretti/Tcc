# Versão HÍBRIDA IQAOA: Otimização local (clássica) + Execução final na QPU (quântica)
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
from pennylane.devices import Device
from services.metrica_tasks import MetricaQuantidadeTaskQuanticas
from services.metrica_shots import MetricaQuantidadeShotsQuanticas
from services.metrica_qubits import MetricaQubits
import itertools # <--- MUDANÇA IQAOA: Necessário para o decodificador

class AlgoritmoIQAOAAmazon(AlgoritmoBase):
    """
    Implementação do iQAOA (Indirect QAOA) para o TSP usando PennyLane.
    Esta abordagem reduz drasticamente o número de qubits necessários (de n² para n).

    1. Otimização de parâmetros: Realizada em um simulador local de alta performance.
    2. Amostragem final: Executada no simulador ou em uma QPU real da AWS Braket.
    """
    TIPO_ALGORITMO = "iQAOA REAL" # <--- MUDANÇA IQAOA
    locale = ''

    # --- Painel de Controle ---
    _REPS = 2 # Aumentado, pois o circuito é mais simples
    _OPTIMIZER_MAX_ITER = 50 # Aumentado para permitir uma otimização real
    _OPTIMIZER_METHOD = 'COBYLA' # COBYLA é ótimo para VQAs
    _TOTAL_SHOTS_FINAL = 1024 # Aumentado para amostragem estatisticamente relevante

    # --- CHAVE PRINCIPAL: Alterne entre Simulador e Nuvem ---
    _USE_QPU = False  # Mude para True para executar na AWS. Requer ARN e S3 preenchidos.
    
    # --- Configurações para Execução em Hardware Real (AWS Braket) ---
    _QPU_ARN = ""  # PREENCHA com o ARN da QPU desejada
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
        """Orquestra a execução completa do algoritmo iQAOA híbrido."""
        self._log("=====================================================")
        self._log("🚀 INICIANDO ALGORITMO iQAOA HÍBRIDO (PENNYLANE)")
        self._log("=====================================================")
        
        cost_h, mixer_h, n_qubits = self._1_preparar_problema(dist_matrix)
        
        # A função de custo agora precisa da matriz de distância para o cálculo clássico
        # <--- MUDANÇA IQAOA
        cost_function = self._create_classical_cost_function(dist_matrix, n_qubits)
        
        optimal_params = self._2_otimizacao_local(cost_function, n_qubits)
        
        # O circuito de amostragem agora não precisa mais do cost_h, apenas do mixer_h
        # <--- MUDANÇA IQAOA
        counts = self._3_amostragem_final(optimal_params, cost_h, mixer_h, n_qubits)
        
        rota_final, distancia_final = self._4_processar_resultados(counts, dist_matrix, pontos)
        
        self._log("\n✅ ALGORITMO iQAOA HÍBRIDO CONCLUÍDO!")
        return rota_final, distancia_final

    # --------------------------------------------------------------------------
    # PASSOS DETALHADOS DO FLUXO
    # --------------------------------------------------------------------------
    def _1_preparar_problema(self, dist_matrix: np.ndarray) -> Tuple[qml.Hamiltonian, qml.Hamiltonian, int]:
        """Cria os Hamiltonianos para a abordagem iQAOA."""
        self._log("\n--- PASSO 1: Preparando o Problema e os Hamiltonianos (iQAOA) ---")
        n_cidades = len(dist_matrix)
        
        # <--- MUDANÇA IQAOA: Número de qubits é n, não n*n
        n_qubits = n_cidades 
        
        self._log(f"Problema de {n_cidades} cidades, necessitando de {n_qubits} qubits (codificação indireta).", 1)
        
        # <--- MUDANÇA IQAOA: O Hamiltoniano de custo agora representa as distâncias entre cidades no grafo
        cost_h = self.tsp_hamiltonian(dist_matrix, n_qubits)
        
        # O mixer continua o mesmo, agindo sobre os n qubits
        mixer_h = qml.Hamiltonian([1] * n_qubits, [qml.PauliX(i) for i in range(n_qubits)])
        
        self._log(f"Hamiltoniano de custo criado com {len(cost_h.ops)} termos.", 1)
        self._log(f"Hamiltoniano de mixer criado.", 1)
        return cost_h, mixer_h, n_qubits

    def _create_classical_cost_function(self, dist_matrix: np.ndarray, n_qubits: int):
        """
        <--- MUDANÇA IQAOA: Cria a função de custo que será passada ao otimizador.
        Esta função engloba a execução quântica e o cálculo de custo clássico.
        """
        dev = qml.device("lightning.qubit", wires=n_qubits)
        
        @qml.qnode(dev)
        def probability_circuit(params, cost_h, mixer_h):
            self._qaoa_circuito(params, cost_h, mixer_h, n_qubits)
            return qml.probs(wires=range(n_qubits))

        def cost_function(params):
            cost_h, mixer_h, _ = self._1_preparar_problema(dist_matrix)
            probs = probability_circuit(params, cost_h, mixer_h)
            
            expected_cost = 0.0
            for i, prob in enumerate(probs):
                if prob > 1e-6: # Considerar apenas estados com probabilidade significativa
                    bitstring = format(i, f'0{n_qubits}b')
                    
                    # Decodifica a permutação e calcula sua distância
                    perm = self.decode_permutation(bitstring)
                    dist = self.calculate_path_distance(perm, dist_matrix)
                    expected_cost += prob * dist
            
            return expected_cost
        
        return cost_function

    def _2_otimizacao_local(self, cost_function, n_qubits: int) -> np.ndarray:
        """Executa a otimização de parâmetros em um simulador local."""
        self._log(f"\n--- PASSO 2: Otimização em Simulador Local ---")
        self._log(f"Otimizador: '{self._OPTIMIZER_METHOD}', p={self._REPS}, max_iter={self._OPTIMIZER_MAX_ITER}", 1)

        initial_params = np.random.uniform(0, 2 * np.pi, 2 * self._REPS)
        
        result = minimize(cost_function, initial_params, method=self._OPTIMIZER_METHOD, options={'maxiter': self._OPTIMIZER_MAX_ITER})
        
        optimal_params = result.x
        self._log("Otimização local concluída!", 1)
        self._log(f"  - Custo final (energia esperada): {result.fun:.4f}", 2)
        self._log(f"  - Parâmetros ótimos encontrados: {optimal_params}", 2)
        return optimal_params

    def _3_amostragem_final(self, optimal_params: np.ndarray, cost_h: qml.Hamiltonian, mixer_h: qml.Hamiltonian, n_qubits: int) -> dict:
        """Executa o circuito final com os parâmetros otimizados para obter amostras."""
        self._log("\n--- PASSO 3: Amostragem Final ---")
        
        try:
            dev_sampler = self._get_sampling_device(n_qubits)
        except ValueError as e:
            self._log(f"Falha ao criar o dispositivo de amostragem: {e}", 1)
            return {}
            
        self.circuito_transpilado = dev_sampler
        
        @qml.qnode(dev_sampler)
        def count_qnode(params):
            self._qaoa_circuito(params, cost_h, mixer_h, n_qubits)
            return qml.counts(wires=range(n_qubits))

        self._log("Executando o circuito no dispositivo selecionado...", 1)
        counts = count_qnode(optimal_params)
        self._log("Execução final concluída.", 1)
        
        return counts

    def _4_processar_resultados(self, counts: dict, dist_matrix: np.ndarray, pontos: List[PontoDTO]) -> Tuple[List[PontoDTO], float]:
        """Decodifica os resultados da amostragem para encontrar a melhor rota."""
        self._log("\n--- PASSO 4: Processando Resultados ---")
        if not counts:
             self._log("AVISO: Nenhuma contagem recebida da amostragem. Não é possível processar.", 1)
             return [], 0.0

        # Encontra a melhor rota válida entre as amostras obtidas
        best_dist = float('inf')
        best_perm = []

        sorted_counts = sorted([item for item in counts.items() if item[1] > 0], key=lambda x: x[1], reverse=True)

        self._log("Top 5 resultados mais prováveis:", 1)
        for i, (bitstring, count) in enumerate(sorted_counts[:5]):
            prob = (count / self._TOTAL_SHOTS_FINAL) * 100
            self._log(f"{i+1}. '{bitstring}': {count} vezes ({prob:.1f}%)", 2)

        for bitstring, count in sorted_counts:
            # <--- MUDANÇA IQAOA: Usa o novo decodificador
            perm = self.decode_permutation(bitstring)
            dist = self.calculate_path_distance(perm, dist_matrix)
            if dist < best_dist:
                best_dist = dist
                best_perm = perm
        
        if not best_perm:
            self._log("AVISO: Nenhuma rota válida foi decodificada.", 1)
            return [], 0.0

        ordem_normalizada = self._normalizar_rota(best_perm)
        self._log(f"\nMelhor rota encontrada nas amostras: {best_perm}", 1)
        self._log(f"Rota final (normalizada): {ordem_normalizada}", 1)
        self._log(f"Distância do caminho: {best_dist:.2f}", 1)
        
        rota_dto = [pontos[idx] for idx in ordem_normalizada]
        rota_dto.append(pontos[ordem_normalizada[0]])
        return rota_dto, best_dist

    # --------------------------------------------------------------------------
    # FÁBRICA DE DISPOSITIVOS E DEFINIÇÃO DE CIRCUITO
    # --------------------------------------------------------------------------
    def _get_sampling_device(self, n_qubits: int) -> Device:
        """Fábrica de dispositivos com base nas configurações da classe."""
        if not self._USE_QPU:
            self._log(f"Executando em simulador local com {self._TOTAL_SHOTS_FINAL} shots.", 1)
            return qml.device("lightning.qubit", wires=n_qubits, shots=self._TOTAL_SHOTS_FINAL)
        
        self._log(f"Tentando configurar dispositivo de nuvem: {self._QPU_ARN}", 1)
        if not self._QPU_ARN or not self._S3_BUCKET:
            self._log("❌ ERRO: Para usar a QPU, _QPU_ARN e _S3_BUCKET devem ser preenchidos.", 2)
            raise ValueError("Configuração da AWS para a QPU está incompleta.")
        
        s3_folder = (self._S3_BUCKET, "iqaoa-tsp-results")
        self._log(f"Enviando para a QPU: {self._QPU_ARN}", 2)
        self._log(f"Resultados serão salvos em S3: {s3_folder}", 2)
        return qml.device(
            "braket.aws.qubit", # Nome correto para dispositivos AWS
            device_arn=self._QPU_ARN,
            wires=n_qubits,
            s3_destination_folder=s3_folder,
            shots=self._TOTAL_SHOTS_FINAL,
        )

    def _qaoa_circuito(self, params: np.ndarray, cost_h: qml.Hamiltonian, mixer_h: qml.Hamiltonian, n_qubits: int):
        """Define a estrutura do circuito QAOA (ansatz)."""
        gammas = params[:self._REPS]
        betas = params[self._REPS:]
        
        for i in range(n_qubits):
            qml.Hadamard(wires=i)
            
        for i in range(self._REPS):
            qml.qaoa.cost_layer(gammas[i], cost_h)
            qml.qaoa.mixer_layer(betas[i], mixer_h)

    # --------------------------------------------------------------------------
    # MÉTODOS DE DECODIFICAÇÃO E CÁLCULO (Atualizados para iQAOA)
    # --------------------------------------------------------------------------

    def tsp_hamiltonian(self, dist_matrix: np.ndarray, n_qubits: int) -> qml.Hamiltonian:
        """
        <--- MUDANÇA IQAOA: Cria o Hamiltoniano de custo para a codificação indireta.
        Ele simplesmente mapeia as distâncias para interações entre qubits.
        """
        coeffs, ops = [], []
        for i in range(n_qubits):
            for j in range(i + 1, n_qubits):
                coeffs.append(dist_matrix[i, j] / 2)
                ops.append(qml.PauliZ(i) @ qml.PauliZ(j))
        return qml.Hamiltonian(coeffs, ops)

    def decode_permutation(self, bitstring: str) -> List[int]:
        """
        <--- MUDANÇA IQAOA: Decodifica uma bitstring para uma permutação de cidades.
        Uma heurística simples: ordena as cidades com base nos bits '1' e depois adiciona as restantes.
        """
        perm = [i for i, bit in enumerate(bitstring) if bit == '1']
        remaining = [i for i, bit in enumerate(bitstring) if bit == '0']
        final_perm = perm + remaining
        
        # Garante que temos todas as cidades, mesmo que a bitstring seja inválida
        if len(set(final_perm)) != len(bitstring):
             return list(range(len(bitstring)))

        return final_perm

    def _normalizar_rota(self, ordem: List[int]) -> List[int]:
        """Garante que a rota (ciclo) sempre comece pela cidade 0."""
        if not ordem or 0 not in ordem:
            return ordem
        idx_zero = ordem.index(0)
        return ordem[idx_zero:] + ordem[:idx_zero]

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
def get_algoritmo_IQAOA_Amazon() -> AlgoritmoIQAOAAmazon:
    service = AlgoritmoIQAOAAmazon()
    service.adicionar_metrica(TempoExecucao())
    service.adicionar_metrica(SequenciaExecucao())
    service.adicionar_metrica(Distancia())
    service.adicionar_metrica(MetricaPreco(tipo_recurso='qpu', provider="anka")) 
    service.adicionar_metrica(MetricaQubits())
    service.adicionar_metrica(MetricaQuantidadeTaskQuanticas())
    service.adicionar_metrica(MetricaQuantidadeShotsQuanticas())
    return service