from core.abstract.metricas_base import MetricasBase
import time
from core.dto.algoritmos_response_dto import MetricaDto

class SequenciaExecucao(MetricasBase):
    
    def __init__(self):
        self.sequencia = None

    def on_inicio_execucao(self, algoritmo):
        pass
    
    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        melhorCaminho = list(map(lambda x: x['name'], melhorCaminho))
        print(melhorCaminho)
        self.sequencia = melhorCaminho

    def resultadoFinal(self) -> str:
        if self.sequencia is None:
            raise Exception('metrica de tempo mal executada')  # Ou lançar uma exceção se preferir
        value = '→ '.join(self.sequencia)
        return MetricaDto(name="Sequência de execução", description=self.get_description(), result=value)