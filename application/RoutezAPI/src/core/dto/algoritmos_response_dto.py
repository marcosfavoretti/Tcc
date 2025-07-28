from pydantic import BaseModel, Field
from typing import List, Dict, Any
from core.enum.tipos_algoritmos import TipoAlgoritmo

class AlgoritmosResponseDto(BaseModel):
    algoritmo: TipoAlgoritmo = Field(
        ...,
        description='Alias do algoritmo que sera utilizado',
        examples=['FORCA_BRUTA']
    )
    metricas: Dict[str, str] = Field(
        description='Objeto com as metricas dos algoritmos'
    )
    menorCaminho: float = Field(
        description='menor caminho em (m)'
    )
    ruas: List[Any] = Field(
        description='Ruas selecionadas pelo agoritmo',
    )
    # melhorSequencia: 
    