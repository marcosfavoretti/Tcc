from core.abstract.metricas_base import MetricasBase
import tracemalloc
from core.dto.algoritmos_response_dto import MetricaDto

class UsoMemoria(MetricasBase):

    def __init__(self):
        self.pico_memoria_bytes = 0
        self.estava_ativo = False

    def get_description(self):
        return "faz a medição de quantas MB de memoria foram utilizados pelo algoritmo"

    def on_inicio_execucao(self, algoritmo):
        # Verifica se o tracemalloc já estava a ser executado por algum motivo
        if tracemalloc.is_tracing():
            print(f"AVISO: tracemalloc já estava ativo antes do início de {algoritmo.TIPO_ALGORITMO}.")
            self.estava_ativo = True
            # Não iniciamos um novo, apenas continuamos a monitorizar
            return

        print(f"Iniciando tracemalloc para {algoritmo.TIPO_ALGORITMO}...")
        tracemalloc.start()

    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        # Se o tracemalloc não estava a ser executado, não há nada a fazer
        if not tracemalloc.is_tracing():
            print(f"ERRO: tracemalloc não estava ativo no fim de {algoritmo.TIPO_ALGORITMO}.")
            return

        current, peak = tracemalloc.get_traced_memory()
        self.pico_memoria_bytes = peak
        
        print(f"Pico de memória capturado para {algoritmo.TIPO_ALGORITMO}: {peak / 1024 / 1024:.4f} MB")
        
        # Só paramos o tracemalloc se a nossa própria instância o iniciou
        if not self.estava_ativo:
            print(f"Parando tracemalloc para {algoritmo.TIPO_ALGORITMO}.")
            tracemalloc.stop()
            # Limpa os vestígios para a próxima execução não ser contaminada
            tracemalloc.clear_traces()
        else:
            print(f"AVISO: Não parando tracemalloc, pois já estava ativo externamente.")


    def resultadoFinal(self) -> MetricaDto:
        value = ''
        if self.pico_memoria_bytes == 0:
            value = "0.0000 MB (Medição pode ser imprecisa devido a código C/Fortran)"
        
        pico_memoria_mb = self.pico_memoria_bytes / 1024 / 1024
        value =  f"{pico_memoria_mb:.4f} MB"
        
        return MetricaDto(name=self.__class__.__name__,description=self.get_description(), result=value)