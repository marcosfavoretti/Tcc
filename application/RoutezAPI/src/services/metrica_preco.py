from core.abstract.metricas_base import MetricasBase
from core.dto.algoritmos_response_dto import MetricaDto
import time

# Dicionário de FALLBACK (sem alterações)
PRECOS_FALLBACK = {
    "qpu": {
        "rigetti": {"por_tarefa": 0.30, "por_shot": 0.00035},
        "ionq":    {"por_tarefa": 0.30, "por_shot": 0.03},
        "iqm":     {"por_tarefa": 0.30, "por_shot": 0.00160},
        'anka':    {"por_tarefa": 0.3, 'por_shot': 0.0009}
    },
    "simulator": {
        "sv1": {"por_minuto": 0.075},
        "tn1": {"por_minuto": 0.275},
        "dm1": {"por_minuto": 0.075},
    },
    "cpu": {
        'aws': {"por_minuto": 0.075}
    }
}

class MetricaPreco(MetricasBase):
    _inicio = None
    _fim = None
    
    def __init__(self, tipo_recurso: str, provider: str):
        if tipo_recurso not in ['qpu', 'simulator', 'cpu']:
            raise ValueError("O tipo de recurso deve ser 'qpu', 'simulator' ou 'cpu'")
            
        if tipo_recurso in PRECOS_FALLBACK and provider not in PRECOS_FALLBACK[tipo_recurso]:
            raise ValueError(f"Provider '{provider}' não encontrado para o tipo de recurso '{tipo_recurso}'.")

        self.tipo_recurso = tipo_recurso
        self.provider = provider # Ex: 'rigetti', 'sv1', 'aws'

    def get_description(self) -> str:
        return f"Estima o custo de execução em [{self.tipo_recurso.upper()}/{self.provider.upper()}] usando a base de preços da AWS."

    def on_inicio_execucao(self, algoritmo):
        self._inicio = time.perf_counter()
 
    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        self._fim = time.perf_counter()
        duracao_segundos = self._fim - self._inicio
        self.value = 0.0

        if self.tipo_recurso == 'qpu':
            # Acessa o dicionário 'qpu' com o provider correto (ex: 'rigetti')
            priceObj = PRECOS_FALLBACK['qpu'][self.provider]
            
            # Custo de 1 tarefa + custo dos shots dessa tarefa
            custo_tarefa =  (algoritmo._OPTIMIZER_MAX_ITER + 1) * priceObj['por_tarefa']
            custo_shots = algoritmo._TOTAL_SHOTS_FINAL * priceObj['por_shot']
            self.value = custo_tarefa + custo_shots

        # --- Custo para Simulador AWS ---
        # O custo é baseado no tempo de execução total.
        elif self.tipo_recurso == 'simulator':
            priceObj = PRECOS_FALLBACK['simulator'][self.provider]
            duracao_minutos = duracao_segundos / 60.0
            self.value = duracao_minutos * priceObj['por_minuto']
            
        # --- Custo para CPU (ou qualquer lógica baseada em tempo) ---
        elif self.tipo_recurso == 'cpu':
            priceObj = PRECOS_FALLBACK['cpu'][self.provider]
            
            # Converte a duração de segundos para minutos
            duracao_minutos = duracao_segundos / 60.0
            self.value = duracao_minutos * priceObj['por_minuto']
            
    def resultadoFinal(self) -> MetricaDto:
        # Formata o resultado para ter uma aparência de dólar
        resultado_formatado = f"US$ {self.value:.4f}"

        return MetricaDto(
            name="Preço da solução",
            description=self.get_description(),
            result=resultado_formatado
        )