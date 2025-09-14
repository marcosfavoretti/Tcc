from core.abstract.metricas_base import MetricasBase
import time

class SequenciaExecucao(MetricasBase):
    
    def __init__(self):
        self.sequencia = None

    def on_inicio_execucao(self, algoritmo):
        pass
    
    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        print(melhorCaminho)
        melhorCaminho = list(map(lambda x: x['name'], melhorCaminho))
        print(melhorCaminho)
        self.sequencia = melhorCaminho

    def resultadoFinal(self) -> str:
        if self.sequencia is None:
            raise Exception('metrica de tempo mal executada')  # Ou lançar uma exceção se preferir
        return ', '.join(self.sequencia)