import matplotlib
matplotlib.use('Agg') # Mantém o backend não interativo
import matplotlib.pyplot as plt
import io
import base64
from core.abstract.metricas_base import MetricasBase
from core.dto.algoritmos_response_dto import MetricaDto

class CircuitoQuanticoImagem(MetricasBase):
    
    def __init__(self):
        # Apenas inicializa o atributo que guardará o circuito
        self.circuito_a_desenhar = None
    
    def get_description(self):
        return "Imagem ilustrativa do circuito quântico responsável por rodar o algoritmo"

    def on_inicio_execucao(self, algoritmo) -> None:
        pass

    def on_fim_execucao(self, algoritmo, melhorCaminho, distancia):
        """
        Este método agora só tem a responsabilidade de capturar e armazenar
        o circuito ao final da execução principal do algoritmo.
        """
        if hasattr(algoritmo, 'circuito_transpilado'):
            self.circuito_a_desenhar = algoritmo.circuito_transpilado

    def resultadoFinal(self) -> MetricaDto:
        """
        A lógica de geração da imagem agora está aqui. 
        Este método será chamado em uma thread pelo AlgoritmoService.
        """
        if self.circuito_a_desenhar is None:
            return MetricaDto(name="Circuito Quântico usado", description=self.get_description(), result=None)

        try:
            # Lógica de geração de imagem que antes estava na thread
            fig = self.circuito_a_desenhar.draw('mpl', scale=1.4)
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig) # Importante para liberar memória
            buf.seek(0)
            
            image_bytes = buf.getvalue()
            base64_bytes = base64.b64encode(image_bytes)
            base64_string = base64_bytes.decode('utf-8')
            
            value = f"data:image/png;base64,{base64_string}"

        except Exception as e:
            print(f"Erro ao gerar a imagem Base64 do circuito: {e}")
            value = "Erro ao gerar imagem."
        
        return MetricaDto(name="Circuito Quântico usado", description=self.get_description(), result=value)