from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Dict
from core.abstract.metricas_base import MetricasBase
import numpy as np
from core.dto.algoritmos_dto import PontoDTO
from core.enum.tipos_algoritmos import TipoAlgoritmo
class AlgoritmoBase(ABC):
    def __init__(self):
        self._metricas: List[MetricasBase]  = [] # Lista para as métricas

    @property
    @abstractmethod
    def TIPO_ALGORITMO(self) -> TipoAlgoritmo: # <-- Adicionar propriedade abstrata
        """Define o tipo de algoritmo que a classe representa."""
        pass

    def adicionar_metrica(self, metrica: MetricasBase):
        self._metricas.append(metrica)

    def executar(self, dist_matrix: np.ndarray, pontos: List[PontoDTO]) ->Tuple[Any, Dict[str, Any]]:
        print(f"Iniciando execução do algoritmo: {self.__class__.__name__}")

        self._notificar_inicio_execucao()

        melhorCaminho, distancia = self._executar_logica_algoritmo(dist_matrix=dist_matrix, pontos=pontos) # Chamada ao método abstrato

        self._notificar_fim_execucao(melhorCaminho, distancia)

        print(f"Finalizando execução do algoritmo: {self.__class__.__name__}")
        
        resultado_das_metricas: Dict[str, Any] = {}
        for metrica in self._metricas:
                resultado_das_metricas[metrica.__class__.__name__] = metrica.resultadoFinal()
                
        print(resultado_das_metricas)
        return melhorCaminho, distancia, resultado_das_metricas

    @abstractmethod
    def _executar_logica_algoritmo(self, dist_matrix: np.ndarray, pontos: List[PontoDTO])-> Tuple[List[PontoDTO], float]:
        """Método abstrato que deve ser implementado pelas subclasses."""
        pass # Não há implementação aqui

    def _notificar_inicio_execucao(self):
        for metrica in self._metricas:
            metrica.on_inicio_execucao(self)

    def _notificar_fim_execucao(self, melhorCaminho, distancia):
        """
        cabe ao desenvolvedor chamar esse metodo na classe filha para avisar uma nova interacao
        """
        for metrica in self._metricas:
            metrica.on_fim_execucao(self, melhorCaminho, distancia)

    def _notificar_iteracao(self, iteracao_atual, dados_iteracao=None):
        for metrica in self._metricas:
            metrica.on_iteracao(self, iteracao_atual, dados_iteracao)
