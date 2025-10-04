from core.abstract.metricas_base import MetricasBase
from core.dto.algoritmos_response_dto import MetricaDto

class MetricaQubits(MetricasBase):

    def get_description(self):
        return "quantidades de qubits para o circuito funcionar\n qubits = pontos^2"

    def on_inicio_execucao(self, algoritmo):
        pass
    
    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        pontos = len(melhorCaminho)-1 # -1 pq aqui estou retornando o ciclo inteiro, incluindo o primeiro ponto ida e volta
        self.value = pontos*pontos #no algoritmo o valor 1 signifca a medicao final do sistema


    def resultadoFinal(self) -> MetricaDto:
        return MetricaDto(name="Qtd. de qubits no circuito",description=self.get_description(), result=str(self.value))