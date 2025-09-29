from qiskit_aer import AerSimulator
from services.distancia import Distancia
import copy
from services.tempo_execucao import TempoExecucao
from core.abstract.algoritmo_base import AlgoritmoBase
import numpy as np
from typing import List, Tuple
from core.dto.algoritmos_dto import PontoDTO
import random
from qiskit import transpile
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import SamplerV2, EstimatorV2, QiskitRuntimeService,Sampler,Estimator
from scipy.optimize import minimize
from services.sequencia_execucao import SequenciaExecucao
from services.metrica_preco import MetricaPreco
from services.metrica_memoria import UsoMemoria
from services.metrica_circuito_img import CircuitoQuanticoImagem

from core.enum.tipos_algoritmos import TipoAlgoritmo
class AlgoritmoQAOA(AlgoritmoBase):
    TIPO_ALGORITMO = TipoAlgoritmo.QAOA
    circuito_transpilado = None    

    BACKEND = AerSimulator()#aqui setei como simulador em vez do computador quantico da ibm
    REPS = 1
    
    def _executar_logica_algoritmo(self, dist_matrix: np.ndarray, pontos: List[PontoDTO]) -> Tuple[List[PontoDTO], float]:
        """
        Resolve TSP usando QAOAAnsatz diretamente
        """
        print("Matriz de Adjacência:")
        for i, row in enumerate(dist_matrix):
            print(f"Cidade {i}: {row}")
        print()
        
        # Converter para QUBO
        hamiltonian = self.adjacency_matrix_to_qubo(dist_matrix)
        print(f"Hamiltoniano criado com {len(hamiltonian)} termos")

        simulator = self.BACKEND
        
        # Criar ansatz QAOA
        qaoa_ansatz = QAOAAnsatz(hamiltonian, reps=self.REPS)
        qaoa_ansatz = transpile(qaoa_ansatz,backend=simulator,optimization_level=1)
        self.circuito_transpilado = qaoa_ansatz
        hamiltonian = hamiltonian.apply_layout(qaoa_ansatz.layout) 
        print(f"Circuito QAOA criado com {qaoa_ansatz.num_qubits} qubits e {qaoa_ansatz.num_parameters} parâmetros")
    
        estimator = EstimatorV2(mode=simulator)
        sampler = SamplerV2(mode=simulator)
        
        # Parâmetros iniciais aleatórios
        initial_params = np.random.uniform(0, 2*np.pi, qaoa_ansatz.num_parameters)
        
        print("Iniciando otimização clássica...")
        
        # Otimização clássica
        result = minimize(
            self.cost_function,
            initial_params,
            args=(qaoa_ansatz, hamiltonian, estimator),
            method='COBYLA',
            options={'maxiter': 2,}
        )
        
        optimal_params = result.x
        optimal_value = result.fun
        
        print(f"\nOtimização concluída!")
        print(f"Valor ótimo encontrado: {optimal_value:.4f}")
        print(f"Sucesso: {result.success}")
        
        # Criar circuito com parâmetros ótimos e medições
        optimal_circuit = qaoa_ansatz.assign_parameters(optimal_params)

        optimal_circuit.measure_all()
        
        print(f"Executando circuito no simulador...")
        
        job = sampler.run([optimal_circuit], shots=4)
        result = job.result()#.get_counts()
        counts = result[0].data.meas.get_counts()
        
        print(f"Top 5 resultados mais prováveis:")
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for i, (bitstring, count) in enumerate(sorted_counts[:5]):
            print(f"{i+1}. {bitstring}: {count} vezes ({count/1024*100:.1f}%)")
        
        # Decodificar solução
        counts_filtred = self.extract_relevant_qubits(counts, [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
        order, solution_matrix = self.decode_solution(counts_filtred,len(dist_matrix))
        
        print("\nMatriz de Solução (cidade x tempo):")
        print("Linhas = Cidades, Colunas = Ordem de Visita")
        for i, row in enumerate(solution_matrix):
            print(f"Cidade {i}: {row}")
        print()
        
        # Calcular distância da solução QAOA
        qaoa_distance = self.calculate_path_distance(order, dist_matrix)
        
        print(f"Ordem encontrada pelo QAOA: {order}")
        print(f"Distância do caminho QAOA: {qaoa_distance}")
        
        best_path_dto: List[PontoDTO] = []
        if order is not None:  # Verifica se um caminho válido foi encontrado
            for idx in order + [0]:  # adiciona a cidade inicial no fim
                best_path_dto.append(pontos[idx])

        return best_path_dto, qaoa_distance
        
    def cost_function(self,params, ansatz, hamiltonian, estimator):
        bound_circuit = ansatz.assign_parameters(params)
        job = estimator.run([(bound_circuit, hamiltonian)])
        result = job.result()
        return result[0].data.evs

    def fix_invalid_solution(self,solution_matrix, n):
        """Corrige uma solução inválida para criar um ciclo hamiltoniano válido"""
        print("Aplicando heurística de correção...")
        order = []
        used_cities = set()
        for pos in range(n):
            best_city = None
            for city in range(n):
                if city not in used_cities:
                    if best_city is None:
                        best_city = city
                    elif solution_matrix[city][pos] > solution_matrix[best_city][pos]:
                        best_city = city
            if best_city is not None:
                order.append(best_city)
                used_cities.add(best_city)
        for city in range(n):
            if city not in used_cities:
                order.append(city)
        order = order[:n]
        print(f"Ordem corrigida: {order}")
        return order

    def decode_solution(self,counts, n=4):
        """Decodifica a solução quântica para ordem das cidades garantindo ciclo hamiltoniano"""
        # Pega as 5 soluções com maior probabilidade para tentar encontrar uma válida
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        for bitstring, count in sorted_counts[:10]:  # Tenta as 10 melhores
            print(f"Tentando bitstring: {bitstring} (probabilidade: {count/1024*100:.1f}%)")
            
            # Converte string binária para matriz
            solution_matrix = np.zeros((n, n), dtype=int)
            for i, bit in enumerate(bitstring):
                if bit == '1':
                    row = i // n
                    col = i % n
                    solution_matrix[row][col] = 1
            
            print("Matriz de solução:")
            for i, row in enumerate(solution_matrix):
                print(f"Cidade {i}: {row}")
            
            # Verifica se é uma solução válida (cada linha e coluna soma 1)
            row_sums = np.sum(solution_matrix, axis=1)
            col_sums = np.sum(solution_matrix, axis=0)
            
            print(f"Somas das linhas (cada cidade): {row_sums}")
            print(f"Somas das colunas (cada posição): {col_sums}")
            
            # Solução válida: cada cidade aparece exatamente uma vez, cada posição tem exatamente uma cidade
            if np.all(row_sums == 1) and np.all(col_sums == 1):
                # Extrai a ordem das cidades
                order = []
                for time_step in range(n):
                    for city in range(n):
                        if solution_matrix[city][time_step] == 1:
                            order.append(city)
                            break
                return order, solution_matrix
            else:
                print("Solução inválida, tentando próxima...")
                print()
        
        print("Nenhuma solução válida encontrada, usando heurística para corrigir a melhor...")
        # Se não encontrou solução válida, usa a melhor e corrige
        best_bitstring = sorted_counts[0][0]
        solution_matrix = np.zeros((n, n), dtype=int)
        for i, bit in enumerate(best_bitstring):
            if bit == '1':
                row = i // n
                col = i % n
                solution_matrix[row][col] = 1
        
        # Heurística de correção: criar um tour válido
        order = self.fix_invalid_solution(solution_matrix, n)
        
        # Criar nova matriz válida
        fixed_matrix = np.zeros((n, n), dtype=int)
        for pos, city in enumerate(order):
            fixed_matrix[city][pos] = 1
        
        return order, fixed_matrix

    def adjacency_matrix_to_qubo(self,adj_matrix):
        """
        Converte matriz de adjacência para formulação QUBO do TSP
        Para 4 cidades, usamos 16 qubits (4x4 matriz binária)
        x_ij = 1 se visitamos cidade i na posição j do tour
        """
        n = len(adj_matrix)
        
        pauli_list = []
        
        # Função objetivo minimizar distâncias entre cidades consecutivas
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    if i != j:
                        # Cidade i na posição k e cidade j na posição seguinte (k+1)%n
                        qubit1 = i * n + k
                        qubit2 = j * n + ((k + 1) % n)
                        
                        # Adicionar termo de distância (queremos minimizar, então coeficiente positivo)
                        pauli_str = ['I'] * (n * n)
                        pauli_str[qubit1] = 'Z'
                        pauli_str[qubit2] = 'Z'
                        # Usar (1-Z)/2 para converter de {-1,1} para {0,1}
                        # Mas aqui já trabalhamos com ZZ que dá +1 quando ambos são |1⟩
                        pauli_list.append((''.join(reversed(pauli_str)), adj_matrix[i][j] / 4))
                        
                        # Termos lineares para implementar (1-Z_i)/2 * (1-Z_j)/2
                        pauli_str1 = ['I'] * (n * n)
                        pauli_str1[qubit1] = 'Z'
                        pauli_list.append((''.join(reversed(pauli_str1)), -adj_matrix[i][j] / 4))
                        
                        pauli_str2 = ['I'] * (n * n)
                        pauli_str2[qubit2] = 'Z'
                        pauli_list.append((''.join(reversed(pauli_str2)), -adj_matrix[i][j] / 4))
                        
                        # Termo constante
                        pauli_str_const = ['I'] * (n * n)
                        pauli_list.append((''.join(pauli_str_const), adj_matrix[i][j] / 4))
        
        # RESTRIÇÕES com penalidades altas
        penalty = 100000  # Penalidade muito alta para violações
        
        # Restrição 1: Exatamente uma cidade por posição no tour
        for k in range(n):
            # Penalizar se mais de uma cidade na posição k
            for i in range(n):
                for j in range(i+1, n):
                    qubit1 = i * n + k
                    qubit2 = j * n + k
                    pauli_str = ['I'] * (n * n)
                    pauli_str[qubit1] = 'Z'
                    pauli_str[qubit2] = 'Z'
                    pauli_list.append((''.join(reversed(pauli_str)), penalty))
            
            # Penalizar se nenhuma cidade na posição k
            for i in range(n):
                qubit = i * n + k
                pauli_str = ['I'] * (n * n)
                pauli_str[qubit] = 'Z'
                pauli_list.append((''.join(reversed(pauli_str)), -penalty))
            
            # Termo constante para garantir exatamente 1
            pauli_str_const = ['I'] * (n * n)
            pauli_list.append((''.join(pauli_str_const), penalty))
        
        # Restrição 2: Cada cidade aparece exatamente uma vez no tour
        for i in range(n):
            # Penalizar se cidade i aparece em mais de uma posição
            for k in range(n):
                for l in range(k+1, n):
                    qubit1 = i * n + k
                    qubit2 = i * n + l
                    pauli_str = ['I'] * (n * n)
                    pauli_str[qubit1] = 'Z'
                    pauli_str[qubit2] = 'Z'
                    pauli_list.append((''.join(reversed(pauli_str)), penalty))
            
            # Penalizar se cidade i não aparece em nenhuma posição
            for k in range(n):
                qubit = i * n + k
                pauli_str = ['I'] * (n * n)
                pauli_str[qubit] = 'Z'
                pauli_list.append((''.join(reversed(pauli_str)), -penalty))
            
            # Termo constante para garantir exatamente 1
            pauli_str_const = ['I'] * (n * n)
            pauli_list.append((''.join(pauli_str_const), penalty))
        hamiltonian = SparsePauliOp.from_list(pauli_list, num_qubits=n*n)
        return hamiltonian
    
    def calculate_path_distance(self,order, adj_matrix):
        """Calcula a distância total do caminho"""
        distance = 0
        n = len(order)
        for i in range(n):
            distance += adj_matrix[order[i]][order[(i+1) % n]]
        return distance
    
    def extract_relevant_qubits(self, counts, qubit_indices):
        """
        Extrai apenas os bits dos qubits relevantes
        qubit_indices: lista dos índices dos qubits que você está usando
        """
        filtered_counts = {}
        needed_length = max(qubit_indices) + 1
        for bitstring, count in counts.items():
            padded = bitstring.zfill(needed_length)  # garante tamanho mínimo
            relevant_bits = ''.join([padded[-(i + 1)] for i in qubit_indices])
            filtered_counts[relevant_bits] = filtered_counts.get(relevant_bits, 0) + count
        return filtered_counts
    
def get_algoritmo_QAOA() -> AlgoritmoQAOA:
    service =  AlgoritmoQAOA()
    service.adicionar_metrica(TempoExecucao())
    service.adicionar_metrica(SequenciaExecucao())
    service.adicionar_metrica(Distancia())
    service.adicionar_metrica(MetricaPreco(tipo_recurso='qpu')) # <--- NOVO
    service.adicionar_metrica(UsoMemoria())
    service.adicionar_metrica(CircuitoQuanticoImagem())      
      
    return service
        