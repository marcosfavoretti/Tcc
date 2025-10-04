from pydantic import BaseModel, Field
from typing import List, Dict, Any

class MetricaDto(BaseModel):
    name: str = Field(..., description="Nome da métrica")
    description: str = Field(..., description="Descrição da métrica")
    result: str = Field(..., description="Resultado da métrica")


class AlgoritmosResponseDto(BaseModel):
    algoritmo: str = Field(
        ...,
        description='Alias do algoritmo que sera utilizado',
        examples=['FORCA_BRUTA']
    )
    caminho: List[tuple[int, int]] = Field(
        ...,
        description='Ruas para traçar',
    )
    metricas: List[MetricaDto] = Field(
        description='Objeto com as metricas dos algoritmos'
    )
    menorCaminho: float = Field(
        description='menor caminho em (m)'
    )
    ruas: List[Any] = Field(
        description='Ruas selecionadas pelo agoritmo',
    )
    # melhorSequencia: 
    