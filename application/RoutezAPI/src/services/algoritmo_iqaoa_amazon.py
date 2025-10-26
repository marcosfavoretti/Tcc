# Versão HÍBRIDA FINAL E ROBUSTA
import time
from braket.aws import AwsQuantumTask
from pennylane.operation import Operator
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
from services.metrica_qubits import MetricaQubits
from services.metrica_tasks import MetricaQuantidadeTaskQuanticas
from services.metrica_shots import MetricaQuantidadeShotsQuanticas

class AlgoritmoIQAOAAmazon(AlgoritmoBase):
    TIPO_ALGORITMO = "IQAOA QUÂNTICO"
    locale = ''

    # --- Painel de Controle ---
    _REPS = 1
    _OPTIMIZER_MAX_ITER = 50
    _OPTIMIZER_METHOD = 'COBYLA'
    _TOTAL_SHOTS_FINAL = 2000

    # --- CHAVE PRINCIPAL: Alterne entre Simulador (False) e Nuvem (True) ---
    _USE_QPU = False

    # --- Configurações para Execução em Hardware Real (AWS Braket) ---
    _QPU_ARN = "arn:aws:braket:us-west-1::device/qpu/rigetti/Ankaa-3"
    
    # CORREÇÃO CRÍTICA: Use apenas o nome do bucket, não o ARN completo.
    # Certifique-se de que este bucket está na mesma região da QPU (neste caso, us-west-1).
    _S3_BUCKET = "amazon-braket-tcc-iqaoa"

    def __init__(self):
        super().__init__()
        self.circuito_transpilado = None
        self.dist_matrix = None

    def _log(self, message: str, level: int = 0):
        indent = "  " * level
        print(f"{indent}{message}")

    def _executar_logica_algoritmo(self, dist_matrix: np.ndarray, pontos: List[PontoDTO]) -> Tuple[List[PontoDTO], float]:
        self._log("=====================================================")
        self._log("🚀 INICIANDO ALGORITMO iQAOA HÍBRIDO (com qml.sample)")
        self._log("=====================================================")
        
        self.dist_matrix = dist_matrix 
        cost_h, mixer_h, n_qubits = self._1_preparar_problema(dist_matrix)
        
        if n_qubits == 0:
            self._log("AVISO: Problema com 0 cidades. Retornando resultado vazio.", 1)
            return [], 0.0

        cost_function = self._create_classical_cost_function(n_qubits, cost_h, mixer_h)
        optimal_params = self._2_otimizacao_local(cost_function)
        counts = self._3_amostragem_final(optimal_params, cost_h, mixer_h, n_qubits)
        rota_final, distancia_final = self._4_processar_resultados(counts, dist_matrix, pontos)
        
        self._log("\n✅ ALGORITMO iQAOA HÍBRIDO CONCLUÍDO!")
        return rota_final, distancia_final

    def _1_preparar_problema(self, dist_matrix: np.ndarray) -> Tuple[qml.Hamiltonian, qml.Hamiltonian, int]:
        self._log("\n--- PASSO 1: Preparando o Problema e os Hamiltonianos (iQAOA) ---")
        n_cidades = len(dist_matrix)
        n_qubits = n_cidades
        self._log(f"Problema de {n_cidades} cidades, usando {n_qubits} qubits.", 1)
        if n_qubits == 0: return qml.Hamiltonian([],[]), qml.Hamiltonian([],[]), n_qubits
        coeffs, ops = self.tsp_hamiltonian_ops(dist_matrix, n_qubits)
        cost_h = qml.Hamiltonian(coeffs, ops)
        mixer_ops = [qml.PauliX(i) for i in range(n_qubits)]
        mixer_h = qml.Hamiltonian([1] * n_qubits, mixer_ops)
        return cost_h, mixer_h, n_qubits

    def _create_classical_cost_function(self, n_qubits: int, cost_h: qml.Hamiltonian, mixer_h: qml.Hamiltonian):
        dev = qml.device("default.qubit", wires=n_qubits)
        @qml.qnode(dev)
        def probability_circuit(params):
            self._qaoa_circuito(params, n_qubits, cost_h, mixer_h)
            return qml.probs(wires=range(n_qubits))
        def cost_function(params):
            probs = probability_circuit(params)
            expected_cost = 0.0
            for i, prob in enumerate(probs):
                if prob > 1e-6:
                    bitstring = format(i, f'0{n_qubits}b')
                    perm = self.decode_permutation(bitstring)
                    dist = self.calculate_path_distance(perm, self.dist_matrix)
                    expected_cost += prob * dist
            return expected_cost
        return cost_function

    def _2_otimizacao_local(self, cost_function) -> np.ndarray:
        self._log(f"\n--- PASSO 2: Otimização em Simulador Local ---")
        self._log(f"Otimizador: '{self._OPTIMIZER_METHOD}', p={self._REPS}, max_iter={self._OPTIMIZER_MAX_ITER}", 1)
        initial_params = np.random.uniform(0, 2 * np.pi, 2 * self._REPS)
        result = minimize(cost_function, initial_params, method=self._OPTIMIZER_METHOD, options={'maxiter': self._OPTIMIZER_MAX_ITER})
        optimal_params = result.x
        self._log("Otimização local concluída!", 1)
        self._log(f"  - Custo final (distância esperada): {result.fun:.4f}", 2)
        self._log(f"  - Parâmetros ótimos encontrados: {optimal_params}", 2)
        return optimal_params

    def _3_amostragem_final(self, optimal_params: np.ndarray, cost_h: qml.Hamiltonian, mixer_h: qml.Hamiltonian, n_qubits: int) -> dict:
        self._log("\n--- PASSO 3: Amostragem Final via Heurística de expval(PauliZ) APRIMORADA ---")
        
        dev = None
        if not self._USE_QPU:
            self._log("Configurando dispositivo: Simulador local (default.qubit)...", 1)
            dev = qml.device("default.qubit", wires=n_qubits, shots=self._TOTAL_SHOTS_FINAL)
        else:
            self._log("Configurando dispositivo: QPU da AWS (braket.aws.qubit)...", 1)
            dev = qml.device(
                "braket.aws.qubit",
                device_arn=self._QPU_ARN,
                wires=n_qubits,
                s3_destination_folder=(self._S3_BUCKET, "iqaoa-tsp-results-9"),
                shots=self._TOTAL_SHOTS_FINAL,
            )

        @qml.qnode(dev)
        def expval_z_qnode(params):
            self._qaoa_circuito(params, n_qubits, cost_h, mixer_h)
            return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]

        expval_results = None
        if not self._USE_QPU:
            self._log("Executando no simulador...", 1)
            expval_results = expval_z_qnode(optimal_params)
        else:
            self._log("Enviando tarefa para a QPU...", 1)
            task = expval_z_qnode(optimal_params)
            self._log(f"  - Tarefa enviada. ID: {task.id}", 2)
            self._log("  - Aguardando a conclusão...", 2)
            while task.state() not in AwsQuantumTask.TERMINAL_STATES:
                print(f"    Status atual: {task.state()}")
                time.sleep(5)
            
            final_status = task.state()
            self._log(f"  - Tarefa concluída com status: {final_status}", 2)
            if final_status == 'COMPLETED':
                self._log("  - Atraso de 3s para sincronização com S3...", 2)
                time.sleep(3)
                expval_results = task.result()
            else:
                raise Exception(f"AWS Quantum Task falhou com status {final_status}")

        self._log(f"Valores de expval(Z) recebidos: {expval_results}", 1)
        self._log("Construindo distribuição de probabilidade aproximada...", 1)
        
        # --- HEURÍSTICA APRIMORADA ---
        
        # 1. Calcula a probabilidade de cada qubit ser '0' ou '1'
        # P(qi=0) = (1 + <Zi>) / 2
        # P(qi=1) = (1 - <Zi>) / 2
        prob_0 = (1 + np.array(expval_results)) / 2
        prob_1 = (1 - np.array(expval_results)) / 2
        
        counts = {}
        
        # 2. Itera por todos os 2^n bitstrings possíveis
        num_bitstrings = 2**n_qubits
        self._log(f"Calculando a probabilidade para {num_bitstrings} bitstrings possíveis...", 2)
        
        # CUIDADO: Se n_qubits for > 20, este loop pode ser muito lento.
        if n_qubits > 20:
             self._log("AVISO: Número de qubits muito alto para a heurística completa. O resultado pode ser limitado.", 2)

        for i in range(num_bitstrings):
            bitstring = format(i, f'0{n_qubits}b')
            
            # 3. Calcula a probabilidade do bitstring (assumindo independência)
            prob_total = 1.0
            for qubit_idx, bit in enumerate(bitstring):
                if bit == '0':
                    prob_total *= prob_0[qubit_idx]
                else:
                    prob_total *= prob_1[qubit_idx]
            
            # 4. Converte a probabilidade em uma contagem de shots, se for relevante
            count = int(round(float(prob_total) * self._TOTAL_SHOTS_FINAL))
            if count > 0:
                counts[bitstring] = count
        
        self._log("Dicionário de contagens aproximado foi gerado.", 2)
        # --- FIM DA HEURÍSTICA APRIMORADA ---
        
        self._log("Execução final (com heurística expval aprimorada) concluída.", 1)
        return counts
    
    def _4_processar_resultados(self, counts, dist_matrix, pontos):
        self._log("\n--- PASSO 4: Processando Resultados ---")
        if not counts:
             self._log("AVISO: Nenhuma contagem recebida.", 1)
             return [], 0.0
        best_dist = float('inf')
        best_perm = []
        total_shots = sum(counts.values()) if sum(counts.values()) > 0 else 1
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        self._log("Top 5 resultados mais prováveis:", 1)
        for i, (bitstring, count) in enumerate(sorted_counts[:5]):
            prob = (count / total_shots) * 100
            self._log(f"{i+1}. '{bitstring}': {count} vezes ({prob:.1f}%)", 2)
        for bitstring, _ in sorted_counts:
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

    def _qaoa_circuito(self, params: np.ndarray, n_qubits: int, cost_h: qml.Hamiltonian, mixer_h: qml.Hamiltonian):
        gammas = params[:self._REPS]
        betas = params[self._REPS:]
        for i in range(n_qubits):
            qml.Hadamard(wires=i)
        for i in range(self._REPS):
            self._manual_cost_layer(gammas[i], cost_h)
            self._manual_mixer_layer(betas[i], n_qubits)

    def _manual_cost_layer(self, gamma, cost_h):
        for coeff, op in zip(cost_h.coeffs, cost_h.ops):
            if len(op.wires) == 2:
                wire1, wire2 = op.wires.tolist()
                qml.CNOT(wires=[wire1, wire2])
                qml.RZ(2 * gamma * coeff, wires=wire2)
                qml.CNOT(wires=[wire1, wire2])

    def _manual_mixer_layer(self, beta, n_qubits):
        for i in range(n_qubits):
            qml.RX(2 * beta, wires=i)

    def tsp_hamiltonian_ops(self, dist_matrix: np.ndarray, n_qubits: int) -> Tuple[List[float], List[Operator]]:
        coeffs, ops = [], []
        for i in range(n_qubits):
            for j in range(i + 1, n_qubits):
                if not np.isclose(dist_matrix[i, j], 0):
                    coeffs.append(dist_matrix[i, j] / 2.0)
                    ops.append(qml.PauliZ(i) @ qml.PauliZ(j))
        if not ops and n_qubits > 0:
            coeffs.append(0.0)
            ops.append(qml.PauliZ(0))
        return coeffs, ops
    
    def decode_permutation(self, bitstring: str) -> List[int]:
        perm = [int(i) for i, bit in enumerate(bitstring) if bit == '1']
        remaining = [int(i) for i, bit in enumerate(bitstring) if bit == '0']
        final_perm = perm + remaining
        if len(set(final_perm)) != len(bitstring): return list(range(len(bitstring)))
        return final_perm

    def _normalizar_rota(self, ordem: List[int]) -> List[int]:
        if not ordem or 0 not in ordem: return ordem
        idx_zero = ordem.index(0)
        return ordem[idx_zero:] + ordem[:idx_zero]

    def calculate_path_distance(self, order: List[int], adj_matrix: np.ndarray) -> float:
        if not order: return 0.0
        dist = 0.0
        for i in range(len(order)):
            u, v = order[i], order[(i + 1) % len(order)]
            dist += adj_matrix[u][v]
        return dist

def get_algoritmo_IQAOA_Amazon() -> AlgoritmoIQAOAAmazon:
    service = AlgoritmoIQAOAAmazon()
    service.adicionar_metrica(TempoExecucao())
    service.adicionar_metrica(SequenciaExecucao())
    service.adicionar_metrica(Distancia())
    service.adicionar_metrica(MetricaPreco(tipo_recurso='qpu', provider="anka")) 
    service.adicionar_metrica(MetricaQubits(tipo='IQAOA'))
    service.adicionar_metrica(MetricaQuantidadeTaskQuanticas())
    service.adicionar_metrica(MetricaQuantidadeShotsQuanticas())
    return service