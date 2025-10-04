import numpy as np
import random
import math
from typing import List, Tuple

from core.abstract.algoritmo_base import AlgoritmoBase
from core.dto.algoritmos_dto import PontoDTO
from services.distancia import Distancia
from services.tempo_execucao import TempoExecucao
from services.sequencia_execucao import SequenciaExecucao
from services.metrica_memoria import UsoMemoria
from services.metrica_preco import MetricaPreco
class AlgoritmoSimulatedAnnealing(AlgoritmoBase):
    """
    Implementação do algoritmo Simulated Annealing para resolver o Problema do Caixeiro Viajante (TSP).
    """
    TIPO_ALGORITMO = "SIMULATE ANNEALING"
    def __init__(self, temp_inicial=10000, taxa_resfriamento=0.995, iteracoes_por_temp=100):
        super().__init__()
        self.temp_inicial = temp_inicial
        self.taxa_resfriamento = taxa_resfriamento
        self.iteracoes_por_temp = iteracoes_por_temp

    def _executar_logica_algoritmo(self, dist_matrix: np.ndarray, pontos: List[PontoDTO]) -> Tuple[List[PontoDTO], float]:
        num_cidades = len(pontos)
        # 1. Gera uma solução inicial aleatória (garantindo que o ponto 0 seja o início)
        solucao_atual = list(range(num_cidades))
        random.shuffle(solucao_atual)
        
        # Força o início no ponto 0
        ponto_zero_idx = solucao_atual.index(0)
        solucao_atual[0], solucao_atual[ponto_zero_idx] = solucao_atual[ponto_zero_idx], solucao_atual[0]

        melhor_solucao = solucao_atual
        
        temperatura = self.temp_inicial

        while temperatura > 1:
            for _ in range(self.iteracoes_por_temp):
                # 2. Gera uma solução vizinha trocando duas cidades (exceto a primeira)
                nova_solucao = solucao_atual[:]
                
                # Seleciona dois índices para trocar, garantindo que não seja o ponto de partida (índice 0)
                i, j = random.sample(range(1, num_cidades), 2)
                nova_solucao[i], nova_solucao[j] = nova_solucao[j], nova_solucao[i]

                # 3. Calcula a diferença de custo (energia)
                custo_atual = self.calcular_distancia_total(solucao_atual, dist_matrix)
                custo_novo = self.calcular_distancia_total(nova_solucao, dist_matrix)
                
                delta_custo = custo_novo - custo_atual

                # 4. Decide se aceita a nova solução
                if delta_custo < 0 or random.uniform(0, 1) < math.exp(-delta_custo / temperatura):
                    solucao_atual = nova_solucao
                
                # Atualiza a melhor solução encontrada até agora
                if self.calcular_distancia_total(solucao_atual, dist_matrix) < self.calcular_distancia_total(melhor_solucao, dist_matrix):
                    melhor_solucao = solucao_atual
            
            # 5. Resfria a temperatura
            temperatura *= self.taxa_resfriamento

        melhor_distancia = self.calcular_distancia_total(melhor_solucao, dist_matrix)
        
        # Formata o resultado para o DTO
        best_path_dto: List[PontoDTO] = []
        for idx in melhor_solucao + [melhor_solucao[0]]: # Adiciona o ponto inicial no final para fechar o ciclo
            best_path_dto.append(pontos[idx])

        return best_path_dto, melhor_distancia

    def calcular_distancia_total(self, rota: List[int], dist_matrix: np.ndarray) -> float:
        """Calcula a distância total de uma rota."""
        distancia = 0
        for i in range(len(rota)):
            cidade_atual = rota[i]
            proxima_cidade = rota[(i + 1) % len(rota)]
            distancia += dist_matrix[cidade_atual][proxima_cidade]
        return distancia

def get_algoritmo_SA() -> AlgoritmoSimulatedAnnealing:
    service = AlgoritmoSimulatedAnnealing()
    service.adicionar_metrica(TempoExecucao())
    service.adicionar_metrica(SequenciaExecucao())
    service.adicionar_metrica(Distancia())
    service.adicionar_metrica(MetricaPreco(tipo_recurso='cpu', provider='aws')) # <--- NOVO
    service.adicionar_metrica(UsoMemoria())
    return service