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
from services.metrica_memoria import UsoMemoria
from services.metrica_qubits import MetricaQubits
import pennylane as qml
from pennylane import numpy as np
from scipy.optimize import minimize
import json
import os

class AlgoritmoProcessadorJson(AlgoritmoBase):
    """
    Classe que segue o contrato AlgoritmoBase, mas sua única função
    é carregar resultados de um arquivo JSON e processá-los para encontrar a melhor rota.
    Não executa simulação nem otimização.
    """
    TIPO_ALGORITMO = "IQAOA Quântico"

    # --- CONFIGURAÇÃO ---
    _ARQUIVO_RESULTADOS_PATH = "C:/Users/marco/OneDrive/Documentos/TCC/dev/application/RoutezAPI/src/services/results_amazon/tsp-10.json"  # Caminho para o arquivo JSON

    def __init__(self):
        super().__init__()
        # Verificação inicial se o arquivo existe
        if not os.path.exists(self._ARQUIVO_RESULTADOS_PATH):
            raise FileNotFoundError(
                f"Arquivo de resultados não encontrado no caminho: {os.path.abspath(self._ARQUIVO_RESULTADOS_PATH)}"
            )

    def _log(self, message: str, level: int = 0):
        indent = "  " * level
        print(f"{indent}{message}")

    def _executar_logica_algoritmo(self, dist_matrix: np.ndarray, pontos: List[PontoDTO]) -> Tuple[List[PontoDTO], float]:
        self._log("=====================================================")
        self._log("🚀 INICIANDO PROCESSADOR DE RESULTADOS IQAOA (JSON)")
        self._log("=====================================================")
        
        # Passo 1: Carregar e converter o JSON para o formato 'counts'
        counts = self._carregar_counts_do_json()
        
        # Passo 2: Processar o 'counts' para encontrar a melhor rota
        rota_final, distancia_final = self._encontrar_melhor_rota(counts, dist_matrix, pontos)
        
        self._log("\n✅ PROCESSAMENTO DE RESULTADOS CONCLUÍDO!")
        return rota_final, distancia_final

    def _carregar_counts_do_json(self) -> dict:
        self._log(f"\n--- PASSO 1: Carregando resultados de '{self._ARQUIVO_RESULTADOS_PATH}' ---")
        
        try:
            with open(self._ARQUIVO_RESULTADOS_PATH, 'r') as f:
                resultados_json = json.load(f)
                raw_samples = resultados_json['measurements']
            self._log("Arquivo JSON carregado com sucesso.", 1)
        except Exception as e:
            self._log(f"ERRO CRÍTICO ao ler o arquivo JSON: {e}", 1)
            return {}

        counts = {}
        if raw_samples:
            self._log("Convertendo amostras brutas em contagens...", 1)
            for sample in raw_samples:
                bitstring = "".join(map(str, sample))
                counts[bitstring] = counts.get(bitstring, 0) + 1
            self._log(f"Conversão concluída. {len(counts)} resultados únicos encontrados.", 2)
        
        return counts

    def _encontrar_melhor_rota(self, counts: dict, dist_matrix: np.ndarray, pontos: List[PontoDTO]) -> Tuple[List[PontoDTO], float]:
        self._log("\n--- PASSO 2: Encontrando a melhor rota nos resultados ---")
        if not counts:
             self._log("AVISO: Nenhuma contagem para processar.", 1)
             return [], 0.0
             
        best_dist = float('inf')
        best_perm = []
        total_shots = sum(counts.values()) or 1
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        self._log("Top 5 resultados mais prováveis do arquivo:", 1)
        for i, (bitstring, count) in enumerate(sorted_counts[:5]):
            prob = (count / total_shots) * 100
            self._log(f"{i+1}. '{bitstring}': {count} vezes ({prob:.1f}%)", 2)
            
        for bitstring, _ in sorted_counts:
            perm = self.decode_permutation(bitstring, len(pontos))
            dist = self.calculate_path_distance(perm, dist_matrix)
            if dist < best_dist:
                best_dist = dist
                best_perm = perm
                
        if not best_perm:
            self._log("AVISO: Nenhuma rota válida foi decodificada.", 1)
            return [], 0.0
            
        ordem_normalizada = self._normalizar_rota(best_perm)
        self._log(f"\nMelhor rota encontrada nos resultados: {best_perm}", 1)
        self._log(f"Rota final (normalizada): {ordem_normalizada}", 1)
        self._log(f"Distância do caminho: {best_dist:.2f}", 1)
        
        rota_dto = [pontos[idx] for idx in ordem_normalizada]
        rota_dto.append(pontos[ordem_normalizada[0]]) # Volta para o início
        return rota_dto, best_dist

    # --- Funções de Ajuda para Processamento ---

    def decode_permutation(self, bitstring: str, n_qubits: int) -> List[int]:
        perm = [i for i, bit in enumerate(bitstring) if bit == '1']
        remaining = [i for i, bit in enumerate(bitstring) if bit == '0']
        final_perm = perm + remaining
        if len(set(final_perm)) != n_qubits: return list(range(n_qubits))
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

def get_algoritmo_IQAOA_AmazonSimUpload() -> AlgoritmoProcessadorJson:
    service = AlgoritmoProcessadorJson()
    service.adicionar_metrica(TempoExecucao())
    service.adicionar_metrica(SequenciaExecucao())
    service.adicionar_metrica(Distancia())
    service.adicionar_metrica(UsoMemoria())
    service.adicionar_metrica(MetricaPreco(tipo_recurso='qpu', provider="anka")) 
    service.adicionar_metrica(MetricaQubits(tipo='IQAOA'))
    return service