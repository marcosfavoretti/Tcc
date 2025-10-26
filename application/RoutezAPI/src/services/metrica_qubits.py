from core.abstract.metricas_base import MetricasBase
from core.dto.algoritmos_response_dto import MetricaDto

class MetricaQubits(MetricasBase):

    def __init__(self, tipo: str):
        super().__init__()
        self.tipo = tipo

    def get_description(self):
        if self.tipo == 'QAOA':
            return "Quantidade de qubits para o circuito funcionar (codificação n^2).\n qubits = pontos^2"
        elif self.tipo == 'IQAOA':
            return "Quantidade de qubits para o circuito funcionar (codificação n).\n qubits = pontos"
        return "Quantidade de qubits para o circuito funcionar."

    def on_inicio_execucao(self, _algoritmo):
        pass
    
    def on_fim_execucao(self, _algoritmo, melhorCaminho, _distancia):
        if not melhorCaminho:
            self.value = 0
            return

        # -1 porque a rota é um ciclo, retornando ao ponto inicial
        pontos = len(melhorCaminho) - 1
        
        if self.tipo == 'QAOA':
            self.value = pontos * pontos
        elif self.tipo == 'IQAOA':
            self.value = pontos
        else:
            self.value = 0

    def resultadoFinal(self) -> MetricaDto:
        return MetricaDto(name="Qtd. de qubits no circuito", description=self.get_description(), result=str(self.value))
