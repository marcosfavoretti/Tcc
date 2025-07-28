from abc import ABC, abstractmethod

class MetricasBase(ABC):
    
    @abstractmethod
    def on_inicio_execucao(self, algoritmo) -> None:
        pass

    def on_iteracao(self, algoritmo) -> None:
        """
        metodo opcional que pode ou nao ser reescrito
        """
        pass

    @abstractmethod
    def on_fim_execucao(self, algoritmo, resultado) -> None:
        pass
    
    @abstractmethod
    def resultadoFinal(self) -> str:
        pass