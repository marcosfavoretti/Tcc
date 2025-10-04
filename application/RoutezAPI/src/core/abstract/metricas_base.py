from abc import ABC, abstractmethod
from core.dto.algoritmos_response_dto import MetricaDto
class MetricasBase(ABC):
    
    @abstractmethod
    def on_inicio_execucao(self, algoritmo) -> None:
        pass

    def on_iteracao(self, algoritmo) -> None:
        """
        metodo opcional que pode ou nao ser reescrito
        """
        pass


    def get_description(self)->str:
        """
        define o que vai ser escrito no tooltip
        """
        return "sem descrição"

    @abstractmethod
    def on_fim_execucao(self, algoritmo, resultado) -> None:
        pass
    
    @abstractmethod
    def resultadoFinal(self) -> MetricaDto:
        pass