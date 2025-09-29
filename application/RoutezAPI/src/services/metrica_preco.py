from core.abstract.metricas_base import MetricasBase
import time

# Preços de referência (em USD por segundo). Estes valores podem ser ajustados.
PRECO_CPU_POR_SEGUNDO = 0.000055  # Exemplo baseado em um custo de $0.20/hora para uma VM de computação
PRECO_QPU_POR_SEGUNDO = 1.60      # Exemplo baseado em um custo de $96/minuto para acesso Pay-As-You-Go a QPU

class MetricaPreco(MetricasBase):
    
    def __init__(self, tipo_recurso: str):
        """
        Inicializa a métrica de preço.
        :param tipo_recurso: 'cpu' para algoritmos clássicos, 'qpu' para quânticos.
        """
        if tipo_recurso not in ['cpu', 'qpu']:
            raise ValueError("O tipo de recurso deve ser 'cpu' ou 'qpu'")
        self._inicio = None
        self._fim = None
        self.tipo_recurso = tipo_recurso
        self.preco_por_segundo = PRECO_CPU_POR_SEGUNDO if tipo_recurso == 'cpu' else PRECO_QPU_POR_SEGUNDO

    def on_inicio_execucao(self, algoritmo):
        self._inicio = time.perf_counter()

    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        self._fim = time.perf_counter()

    def resultadoFinal(self) -> str:
        if self._inicio is None or self._fim is None:
            raise Exception('Métrica de preço mal executada')
        
        tempo_total_segundos = self._fim - self._inicio
        custo_total = tempo_total_segundos * self.preco_por_segundo
        
        return f"R${custo_total:.8f}"