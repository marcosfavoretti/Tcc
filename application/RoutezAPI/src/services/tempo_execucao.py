from core.abstract.metricas_base import MetricasBase
import time

class TempoExecucao(MetricasBase):
    
    def __init__(self):
        self._inicio = None
        self._fim = None

    def on_inicio_execucao(self, algoritmo):
        self._inicio = time.perf_counter()

    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        self._fim = time.perf_counter()

    def resultadoFinal(self) -> str:
        if self._inicio is None or self._fim is None:
            raise Exception('metrica de tempo mal executada')

        tempo_decorrido = self._fim - self._inicio
        
        # Formata o resultado para ter 4 casas decimais e adiciona " s" no final
        return f"{tempo_decorrido:.4f} s"