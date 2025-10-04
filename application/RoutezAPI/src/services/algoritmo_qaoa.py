# [Imports permanecem os mesmos]
from qiskit_aer import AerSimulator
from services.distancia import Distancia
import copy
from services.tempo_execucao import TempoExecucao
from core.abstract.algoritmo_base import AlgoritmoBase
import numpy as np
from typing import List, Tuple
from core.dto.algoritmos_dto import PontoDTO
import random
from qiskit import transpile, QuantumCircuit
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import SamplerV2, EstimatorV2
from scipy.optimize import minimize
from services.sequencia_execucao import SequenciaExecucao
from services.metrica_preco import MetricaPreco
from services.metrica_memoria import UsoMemoria
from services.metrica_circuito_img import CircuitoQuanticoImagem
from services.metrica_quanticas import MetricasQuanticas
from services.metrica_tasks import MetricaQuantidadeTaskQuanticas
from services.metrica_shots import MetricaQuantidadeShotsQuanticas
from services.metrica_qubits import MetricaQubits

class AlgoritmoQAOA(AlgoritmoBase):
    """
    Implementação do algoritmo QAOA para resolver o Problema do Caixeiro Viajante (TSP).
    """
    TIPO_ALGORITMO = "QAOA"
    _QPU_ARN = ''
    device_arn = ''
    # --- Parâmetros de Configuração do Algoritmo ---
    _BACKEND = AerSimulator()
    _REPS = 1
    _OPTIMIZER_METHOD = 'COBYLA'
    _OPTIMIZER_MAX_ITER = 1
    _TOTAL_SHOTS_FINAL = 1
    _PENALTY_FACTOR = 1

    def __init__(self):
        super().__init__()
        self.circuito_transpilado = None

    def _log(self, message: str, level: int = 0):
        """Função auxiliar para logs formatados."""
        indent = "  " * level
        print(f"{indent}{message}")

    # ... [Todos os outros métodos de _executar_logica_algoritmo a _calculate_path_distance permanecem os mesmos] ...

    # --------------------------------------------------------------------------
    # FLUXO PRINCIPAL DE EXECUÇÃO
    # --------------------------------------------------------------------------

    def _executar_logica_algoritmo(self, dist_matrix: np.ndarray, pontos: List[PontoDTO]) -> Tuple[List[PontoDTO], float]:
        """
        Orquestra a execução completa do algoritmo QAOA para o TSP.
        """
        self._log("=====================================================")
        self._log("🚀 INICIANDO ALGORITMO QAOA PARA O TSP")
        self._log("=====================================================")

        hamiltonian = self._1_construir_hamiltoniano(dist_matrix)
        ansatz, hamiltonian_mapeado, estimator, sampler = self._2_preparar_infraestrutura_quantica(hamiltonian)
        self.circuito_transpilado = ansatz
        otimizacao_result = self._3_executar_otimizacao_classica(ansatz, hamiltonian_mapeado, estimator)
        counts = self._4_amostrar_solucao_otima(otimizacao_result.x, ansatz, sampler)
        rota_final, distancia_final = self._5_decodificar_e_validar_rota(counts, dist_matrix, pontos)

        self._log("\n✅ ALGORITMO QAOA CONCLUÍDO!")
        return rota_final, distancia_final

    # --------------------------------------------------------------------------
    # MÉTODOS AUXILIARES DO FLUXO PRINCIPAL
    # --------------------------------------------------------------------------

    def _1_construir_hamiltoniano(self, dist_matrix: np.ndarray) -> SparsePauliOp:
        self._log("\n--- PASSO 1: Construindo o Hamiltoniano ---")
        n_cidades = len(dist_matrix)
        self._log(f"Problema com {n_cidades} cidades, usando {n_cidades**2} qubits.", 1)
        
        objetivo = self._criar_objetivo_hamiltoniano(dist_matrix, n_cidades)
        restricoes = self._criar_restricoes_hamiltoniano(n_cidades)
        
        hamiltonian = objetivo + restricoes

        # --- INÍCIO DA CORREÇÃO ---
        # O SparsePauliOp, por padrão, armazena coeficientes como 'numpy.complex128'.
        # O QAOAAnsatz requer que os coeficientes sejam explicitamente do tipo real (float).
        # Verificamos se as partes imaginárias são todas zero e, em caso afirmativo,
        # reconstruímos o operador usando apenas as partes reais dos coeficientes.
        if np.all(hamiltonian.coeffs.imag == 0):
            self._log("Convertendo coeficientes do Hamiltoniano para o tipo real.", 1)
            hamiltonian = SparsePauliOp(hamiltonian.paulis, coeffs=hamiltonian.coeffs.real)
        else:
            # Este 'else' é uma salvaguarda. Para o problema do TSP, os coeficientes
            # nunca deveriam ter uma parte imaginária diferente de zero.
            self._log("AVISO: O Hamiltoniano contém coeficientes genuinamente complexos!", 1)
            raise ValueError("Hamiltoniano possui coeficientes complexos não nulos, o que não é esperado.")

        # --- FIM DA CORREÇÃO ---

        self._log(f"Hamiltoniano criado com {len(hamiltonian)} termos.", 1)
        return hamiltonian
    
    def _2_preparar_infraestrutura_quantica(self, hamiltonian: SparsePauliOp) -> Tuple[QuantumCircuit, SparsePauliOp, EstimatorV2, SamplerV2]:
        self._log("\n--- PASSO 2: Preparando o Circuito e Backend ---")
        ansatz = QAOAAnsatz(hamiltonian, reps=self._REPS)
        self._log(f"Ansatz QAOA criado com {ansatz.num_qubits} qubits e {ansatz.num_parameters} parâmetros (reps={self._REPS}).", 1)
        self._log(f"Transpilando circuito para o backend '{self._BACKEND.name}'...", 1)
        ansatz_transpilado = transpile(ansatz, backend=self._BACKEND, optimization_level=1)
        hamiltonian_mapeado = hamiltonian.apply_layout(ansatz_transpilado.layout)
        estimator = EstimatorV2(mode=self._BACKEND)
        sampler = SamplerV2(mode=self._BACKEND)
        self._log("Estimator e Sampler V2 inicializados.", 1)
        return ansatz_transpilado, hamiltonian_mapeado, estimator, sampler

    def _3_executar_otimizacao_classica(self, ansatz: QuantumCircuit, hamiltonian: SparsePauliOp, estimator: EstimatorV2):
        self._log("\n--- PASSO 3: Otimização Clássica dos Parâmetros ---")
        params_iniciais = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)
        self._log(f"Iniciando otimização com o método '{self._OPTIMIZER_METHOD}' (max_iter={self._OPTIMIZER_MAX_ITER}).", 1)
        result = minimize(self._cost_function, params_iniciais, args=(ansatz, hamiltonian, estimator), method=self._OPTIMIZER_METHOD, options={'maxiter': self._OPTIMIZER_MAX_ITER})
        self._log("Otimização concluída!", 1)
        self._log(f"  - Sucesso: {result.success}", 2)
        self._log(f"  - Valor de energia final (custo): {result.fun:.4f}", 2)
        return result

    def _4_amostrar_solucao_otima(self, params_otimos: np.ndarray, ansatz: QuantumCircuit, sampler: SamplerV2) -> dict:
        self._log("\n--- PASSO 4: Amostragem da Solução Ótima ---")
        circuito_otimo = ansatz.assign_parameters(params_otimos)
        circuito_otimo.measure_all()
        self._log(f"Executando circuito no sampler com {self._TOTAL_SHOTS_FINAL} shots...", 1)
        job = sampler.run([circuito_otimo], shots=self._TOTAL_SHOTS_FINAL)
        result = job.result()
        counts = result[0].data.meas.get_counts()
        self._log("Resultados mais prováveis:", 1)
        sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        for i, (bitstring, count) in enumerate(sorted_counts[:5]):
            prob = (count / self._TOTAL_SHOTS_FINAL) * 100
            self._log(f"{i+1}. Bitstring '{bitstring}': {count} vezes ({prob:.2f}%)", 2)
        return counts

    def _5_decodificar_e_validar_rota(self, counts: dict, dist_matrix: np.ndarray, pontos: List[PontoDTO]) -> Tuple[List[PontoDTO], float]:
        """Decodifica a string de bits, valida e normaliza a rota do TSP."""
        self._log("\n--- PASSO 5: Decodificando, Validando e Normalizando a Rota ---")
        n_cidades = len(dist_matrix)
        
        qubit_indices = list(range(n_cidades**2))
        counts_filtrados = self._ajustar_ordenacao_bits(counts, qubit_indices)

        ordem_bruta, _ = self._decode_solution(counts_filtrados, n_cidades)
        
        if not ordem_bruta:
            self._log("AVISO: Não foi possível decodificar uma rota válida.", 1)
            return [], float('inf')

        self._log(f"Rota bruta decodificada: {ordem_bruta}", 2)
        ordem = self._normalizar_rota_comecando_por_zero(ordem_bruta)

        distancia = self._calculate_path_distance(ordem, dist_matrix)
        
        self._log(f"Rota final (normalizada): {ordem}", 1)
        self._log(f"Distância total da rota: {distancia:.2f}", 1)
        
        rota_dto = [pontos[idx] for idx in ordem]
        rota_dto.append(pontos[ordem[0]])
        
        return rota_dto, distancia
    
    # --------------------------------------------------------------------------
    # LÓGICA DO HAMILTONIANO (QUBO) - SEM ALTERAÇÕES
    # --------------------------------------------------------------------------

    def _criar_objetivo_hamiltoniano(self, dist_matrix: np.ndarray, n: int) -> SparsePauliOp:
        pauli_list = []
        for i in range(n):
            for j in range(n):
                if i == j: continue
                for k in range(n):
                    qubit1 = i * n + k
                    qubit2 = j * n + ((k + 1) % n)
                    pauli_str = ['I'] * (n * n); pauli_str[qubit1] = 'Z'; pauli_str[qubit2] = 'Z'
                    pauli_list.append((''.join(reversed(pauli_str)), dist_matrix[i][j] / 4.0))
                    pauli_str1 = ['I'] * (n * n); pauli_str1[qubit1] = 'Z'
                    pauli_list.append((''.join(reversed(pauli_str1)), -dist_matrix[i][j] / 4.0))
                    pauli_str2 = ['I'] * (n * n); pauli_str2[qubit2] = 'Z'
                    pauli_list.append((''.join(reversed(pauli_str2)), -dist_matrix[i][j] / 4.0))
        return SparsePauliOp.from_list(pauli_list)

    def _criar_restricoes_hamiltoniano(self, n: int) -> SparsePauliOp:
        pauli_list = []
        for i in range(n):
            for k in range(n):
                qubit1 = i * n + k
                pauli_str = ['I'] * (n * n); pauli_str[qubit1] = 'Z'
                pauli_list.append((''.join(reversed(pauli_str)), -self._PENALTY_FACTOR))
                for l in range(k + 1, n):
                    qubit2 = i * n + l
                    pauli_str_zz = ['I'] * (n * n); pauli_str_zz[qubit1] = 'Z'; pauli_str_zz[qubit2] = 'Z'
                    pauli_list.append((''.join(reversed(pauli_str_zz)), 2 * self._PENALTY_FACTOR))
        for k in range(n):
            for i in range(n):
                qubit1 = i * n + k
                pauli_str = ['I'] * (n * n); pauli_str[qubit1] = 'Z'
                pauli_list.append((''.join(reversed(pauli_str)), -self._PENALTY_FACTOR))
                for j in range(i + 1, n):
                    qubit2 = j * n + k
                    pauli_str_zz = ['I'] * (n * n); pauli_str_zz[qubit1] = 'Z'; pauli_str_zz[qubit2] = 'Z'
                    pauli_list.append((''.join(reversed(pauli_str_zz)), 2 * self._PENALTY_FACTOR))
        return SparsePauliOp.from_list(pauli_list)
    
    # --------------------------------------------------------------------------
    # FUNÇÕES DE APOIO E DECODIFICAÇÃO
    # --------------------------------------------------------------------------
    def _cost_function(self, params, ansatz, hamiltonian, estimator):
        """Função de custo para o otimizador clássico."""
        pub = (ansatz.assign_parameters(params), hamiltonian)
        result = estimator.run([pub]).result()
        
        # CORREÇÃO: O nome correto do atributo é 'evs' (Expected ValueS).
        return result[0].data.evs


    def _decode_solution(self, counts: dict, n: int) -> Tuple[List[int], np.ndarray]:
        sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        self._log("Analisando as 10 soluções mais prováveis para encontrar um tour válido...", 1)
        for bitstring, _ in sorted_counts[:10]:
            solution_matrix = np.reshape([int(bit) for bit in bitstring], (n, n))
            row_sums = np.sum(solution_matrix, axis=1)
            col_sums = np.sum(solution_matrix, axis=0)
            if np.all(row_sums == 1) and np.all(col_sums == 1):
                self._log(f"Solução válida encontrada com o bitstring '{bitstring}'!", 2)
                order = [np.where(row == 1)[0][0] for row in solution_matrix.T]
                return order, solution_matrix
        self._log("Nenhuma solução perfeitamente válida encontrada. Aplicando heurística de correção na melhor solução.", 1)
        best_bitstring = sorted_counts[0][0]
        best_solution_matrix = np.reshape([int(bit) for bit in best_bitstring], (n, n))
        order = self._fix_invalid_solution(best_solution_matrix, n)
        fixed_matrix = np.zeros((n, n), dtype=int)
        for pos, city in enumerate(order):
            fixed_matrix[city][pos] = 1
        return order, fixed_matrix

    def _fix_invalid_solution(self, solution_matrix: np.ndarray, n: int) -> List[int]:
        self._log("Executando heurística de correção...", 2)
        order = []
        visited_cities = set()
        for pos in range(n):
            city_probs = []
            for city in range(n):
                if city not in visited_cities:
                    city_probs.append((city, solution_matrix[city][pos]))
            if not city_probs: continue
            best_city = max(city_probs, key=lambda item: item[1])[0]
            order.append(best_city)
            visited_cities.add(best_city)
        for city in range(n):
            if city not in visited_cities:
                order.append(city)
        self._log(f"Rota corrigida gerada: {order}", 2)
        return order

    def _calculate_path_distance(self, order: List[int], dist_matrix: np.ndarray) -> float:
        distance = 0
        n = len(order)
        for i in range(n):
            cidade_atual = order[i]
            proxima_cidade = order[(i + 1) % n]
            distance += dist_matrix[cidade_atual][proxima_cidade]
        return distance

    def _ajustar_ordenacao_bits(self, counts: dict, qubit_indices: List[int]) -> dict:
        filtered_counts = {}
        num_qubits = max(qubit_indices) + 1
        for bitstring, count in counts.items():
            reversed_bitstring = bitstring[::-1]
            padded = reversed_bitstring.ljust(num_qubits, '0')
            relevant_bits = "".join(padded[i] for i in qubit_indices)
            filtered_counts[relevant_bits] = filtered_counts.get(relevant_bits, 0) + count
        return filtered_counts
    
    def _normalizar_rota_comecando_por_zero(self, ordem: List[int]) -> List[int]:
        """
        Garante que a rota (ciclo) sempre comece pela cidade 0 para padronização.
        """
        if 0 not in ordem:
            self._log(f"AVISO: A cidade 0 não está na rota decodificada {ordem}. Retornando rota original.", 2)
            return ordem
        
        start_index = ordem.index(0)
        
        if start_index == 0:
            return ordem
        
        return ordem[start_index:] + ordem[:start_index]

# ... [Função get_algoritmo_QAOA() permanece a mesma] ...
def get_algoritmo_QAOA() -> AlgoritmoQAOA:
    service = AlgoritmoQAOA()
    service.adicionar_metrica(TempoExecucao())
    service.adicionar_metrica(SequenciaExecucao())
    service.adicionar_metrica(Distancia())
    service.adicionar_metrica(MetricaPreco(tipo_recurso='qpu', provider='anka'))
    service.adicionar_metrica(MetricaQubits())
    service.adicionar_metrica(MetricaQuantidadeTaskQuanticas())
    service.adicionar_metrica(MetricaQuantidadeShotsQuanticas())
    # service.adicionar_metrica(UsoMemoria())
    # service.adicionar_metrica(MetricasQuanticas())
    service.adicionar_metrica(CircuitoQuanticoImagem())
    return service