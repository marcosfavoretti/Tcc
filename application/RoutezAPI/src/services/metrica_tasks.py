from core.abstract.metricas_base import MetricasBase
from core.dto.algoritmos_response_dto import MetricaDto

class MetricaQuantidadeTaskQuanticas(MetricasBase):

    def get_description(self):
        return "quantidades de tasks criadas para resolver o algoritmo"

    def on_inicio_execucao(self, algoritmo):
        pass
    
    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        self.value = algoritmo._OPTIMIZER_MAX_ITER + 1 #no algoritmo o valor 1 signifca a medicao final do sistema


    def resultadoFinal(self) -> MetricaDto:
        return MetricaDto(name="Qtd. tasks quânticas",description=self.get_description(), result=str(self.value))