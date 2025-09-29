from core.abstract.metricas_base import MetricasBase
import matplotlib
# matplotlib.use('Agg') # <-- 1. ADICIONE ESTA LINHA ANTES DE IMPORTAR O PYPLOT
import matplotlib.pyplot as plt
import io
import base64
import threading

class CircuitoQuanticoImagem(MetricasBase):
    
    def __init__(self):
        self.base64_image = None
        self._thread = None

    def on_inicio_execucao(self, algoritmo) -> None:
        pass

    def _gerar_imagem_em_background(self, circuito):
        try:
            fig = circuito.draw('mpl')
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            
            image_bytes = buf.getvalue()
            base64_bytes = base64.b64encode(image_bytes)
            base64_string = base64_bytes.decode('utf-8')
            
            self.base64_image = f"data:image/png;base64,{base64_string}"

        except Exception as e:
            print(f"Erro na thread ao gerar a imagem Base64 do circuito: {e}")
            self.base64_image = "Erro ao gerar imagem."

    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        if hasattr(algoritmo, 'circuito_transpilado') and algoritmo.circuito_transpilado is not None:
            # A lógica da thread continua a mesma
            self._thread = threading.Thread(
                target=self._gerar_imagem_em_background, 
                args=(algoritmo.circuito_transpilado,)
            )
            self._thread.start()
            self.base64_image = "Processando imagem..."

    def resultadoFinal(self) -> str:
        if self._thread is not None:
            self._thread.join()

        if self.base64_image and self.base64_image != "Processando imagem...":
            return self.base64_image
            
        return "Nenhum circuito para exibir ou falha na geração."