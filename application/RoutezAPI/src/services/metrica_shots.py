from core.abstract.metricas_base import MetricasBase
from core.dto.algoritmos_response_dto import MetricaDto

class MetricaQuantidadeShotsQuanticas(MetricasBase):

    def get_description(self):
        return "quantidades de vezes que o algoritmo requere um shot quântico"

    def on_inicio_execucao(self, algoritmo):
        pass
    
    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        self.value = (algoritmo._OPTIMIZER_MAX_ITER * algoritmo._TOTAL_SHOTS_FINAL) + algoritmo._TOTAL_SHOTS_FINAL #no algoritmo o valor 1 signifca a medicao final do sistema


    def resultadoFinal(self) -> MetricaDto:
        return MetricaDto(name="Qtd. shots quânticos",description=self.get_description(), result=str(self.value))