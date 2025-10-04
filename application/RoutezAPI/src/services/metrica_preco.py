from core.abstract.metricas_base import MetricasBase
from core.dto.algoritmos_response_dto import MetricaDto
import time

# --- PONTO CENTRAL DE CONFIGURAÇÃO ---

# Taxa de câmbio para converter USD para BRL. 
# Recomenda-se atualizar periodicamente ou obter de uma API.
# Valor consultado em 03/10/2025.
TAXA_CAMBIO_USD_BRL = 5.34

# Dicionário com os preços base em DÓLARES (USD)
PRECOS_BASE_USD = {
    "qpu": {
        "rigetti": {"por_tarefa": 0.30, "por_shot": 0.00035},
        "ionq":    {"por_tarefa": 0.30, "por_shot": 0.03},
        "iqm":     {"por_tarefa": 0.30, "por_shot": 0.00160},
        'anka':    {"por_tarefa": 0.30, "por_shot": 0.0009}
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
    
    def __init__(self, tipo_recurso: str, provider: str):
        # Validação de entradas
        if tipo_recurso not in PRECOS_BASE_USD:
            raise ValueError(f"Tipo de recurso '{tipo_recurso}' inválido. Válidos: {list(PRECOS_BASE_USD.keys())}")
            
        if provider not in PRECOS_BASE_USD[tipo_recurso]:
            raise ValueError(f"Provider '{provider}' não encontrado para o recurso '{tipo_recurso}'. Válidos: {list(PRECOS_BASE_USD[tipo_recurso].keys())}")

        self.tipo_recurso = tipo_recurso
        self.provider = provider
        
        # Atributos para cálculo
        self._inicio_tempo = None
        self._custo_em_usd = 0.0

    def get_description(self) -> str:
        return f"Estima o custo de execução em [{self.tipo_recurso.upper()}/{self.provider.upper()}] e converte para BRL."

    def on_inicio_execucao(self, algoritmo):
        self._inicio_tempo = time.perf_counter()

    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        if self._inicio_tempo is None:
            raise Exception("O método 'on_inicio_execucao' não foi chamado antes de 'on_fim_execucao'.")
            
        duracao_segundos = time.perf_counter() - self._inicio_tempo
        
        # --- LÓGICA DE CÁLCULO DO CUSTO EM USD ---
        
        if self.tipo_recurso == 'qpu':
            price_obj = PRECOS_BASE_USD['qpu'][self.provider]
            
            # Tenta obter os parâmetros do objeto algoritmo de forma segura
            max_iter = getattr(algoritmo, '_OPTIMIZER_MAX_ITER', 0)
            total_shots = getattr(algoritmo, '_TOTAL_SHOTS_FINAL', 0)
            
            # A lógica assume que cada iteração do otimizador + a execução final geram uma "tarefa"
            custo_tarefa = (max_iter + 1) * price_obj['por_tarefa']
            custo_shots = total_shots * price_obj['por_shot']
            self._custo_em_usd = custo_tarefa + custo_shots

        elif self.tipo_recurso in ['simulator', 'cpu']:
            price_obj = PRECOS_BASE_USD[self.tipo_recurso][self.provider]
            duracao_minutos = duracao_segundos / 60.0
            self._custo_em_usd = duracao_minutos * price_obj['por_minuto']
            
    def resultadoFinal(self) -> MetricaDto:
        # --- CONVERSÃO E FORMATAÇÃO FINAL ---
        
        custo_em_brl = self._custo_em_usd * TAXA_CAMBIO_USD_BRL
        
        # Formata o resultado final em Reais (BRL)
        resultado_formatado = f"R$ {custo_em_brl:.9f}"

        return MetricaDto(
            name="Preço da solução",
            description=self.get_description(),
            result=resultado_formatado
        )