from itertools import permutations
import numpy as np
from core.dto.algoritmos_dto import PontoDTO
from typing import List, Tuple
from core.abstract.algoritmo_base import AlgoritmoBase
from .tempo_execucao import TempoExecucao
from services.distancia import Distancia
from services.sequencia_execucao import SequenciaExecucao 
from core.enum.tipos_algoritmos import TipoAlgoritmo
from services.metrica_preco import MetricaPreco
from services.metrica_memoria import UsoMemoria

class ForcaBrutaService(AlgoritmoBase):
    TIPO_ALGORITMO = TipoAlgoritmo.FORCA_BRUTA # <-- Implementar propriedade
    
    def __init__(self):
        super().__init__()
    
    def _executar_logica_algoritmo(self, dist_matrix: np.ndarray, pontos: List[PontoDTO]) -> Tuple[List[PontoDTO], float]:
        
        n = len(pontos)
        min_distance = float('inf')
        best_path_indices = None # Armazena os índices do melhor caminho na matriz
        point_indices_for_permutation = list(range(1, n)) 
        
        if not point_indices_for_permutation:
            return [pontos[0]], 0.0

        for perm in permutations(point_indices_for_permutation):
            path_indices = [0] + list(perm) + [0]
            total_distance = 0

            for i in range(len(path_indices) - 1):
                from_idx = path_indices[i]
                to_idx = path_indices[i+1]
                dist = dist_matrix[from_idx][to_idx]
                
                if dist == float('inf'):
                    total_distance = float('inf')
                    break
                
                total_distance += dist

            if total_distance < min_distance:
                min_distance = total_distance
                best_path_indices = path_indices

        best_path_dto: List[PontoDTO] = []
        if best_path_indices is not None: # Verifica se um caminho válido foi encontrado
            for idx in best_path_indices:
                best_path_dto.append(pontos[idx])
        else:
            # Caso não encontre nenhum caminho válido (todos os caminhos resultaram em infinito)
            print("Aviso: Nenhum caminho válido encontrado. Retornando lista vazia e distância infinita.")
            return [], float('inf')
        
        return best_path_dto, min_distance
    
def get_forca_bruta_service() -> ForcaBrutaService:
    service =  ForcaBrutaService()
    service.adicionar_metrica(TempoExecucao())
    service.adicionar_metrica(SequenciaExecucao())
    service.adicionar_metrica(Distancia())
    service.adicionar_metrica(MetricaPreco(tipo_recurso='cpu')) # <--- NOVO
    service.adicionar_metrica(UsoMemoria())     
    return service