from core.abstract.metricas_base import MetricasBase

class Distancia(MetricasBase):
    
    def __init__(self):
        self.distancia = None 
        
    def on_inicio_execucao(self, algoritmo):
        pass

    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        self.distancia = distancia

    def resultadoFinal(self) -> str:
        if self.distancia is None:
            raise Exception('metrica de tempo mal executada')  # Ou lançar uma exceção se preferir
        return str(self.distancia)+'m'