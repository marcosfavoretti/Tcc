from core.abstract.metricas_base import MetricasBase
import json

class MetricasQuanticas(MetricasBase):
    
    def __init__(self):
        self.dados_circuito = {}

    def on_inicio_execucao(self, algoritmo):
        self.dados_circuito = {}

    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        # O algoritmo QAOA deve expor o circuito transpilado
        # Ex: algoritmo.circuito_transpilado
        if hasattr(algoritmo, 'circuito_transpilado'):
            circuito = algoritmo.circuito_transpilado
            self.dados_circuito['profundidade'] = circuito.depth()
            self.dados_circuito['tamanho'] = circuito.size()
            self.dados_circuito['qubits'] = circuito.num_qubits
            self.dados_circuito['parametros'] = circuito.num_parameters
        else:
            self.dados_circuito['erro'] = "Circuito não encontrado no algoritmo."

    def resultadoFinal(self) -> str:
        if not self.dados_circuito:
            return "Nenhuma métrica quântica coletada."
        
        return json.dumps(self.dados_circuito)