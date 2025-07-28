from pydantic import BaseModel, Field
from typing import List, Dict
from core.enum.tipos_algoritmos import TipoAlgoritmo
class PontoDTO(BaseModel):
    latitude: float = Field(..., description="Latitude do ponto")
    longitude: float = Field(..., description="Longitude do ponto")
    name: str = Field(..., description="Nome do ponto")

class AlgoritmosDto(BaseModel):
    algoritmo: TipoAlgoritmo = Field(
        ...,
        description='Alias do algoritmo que sera utilizado',
        examples=['FORCA_BRUTA']
    )
    ponto_inicial: PontoDTO = Field(
        ...,
        description="Ponto de partida",
        example={
            "latitude": -23.2848682,
            "longitude": -47.6720885,
            "name": "Ponto Inicial"
        }
    )
    pontos_interesse: List[PontoDTO] = Field(
        ...,
        description="Lista de pontos de interesse",
        example=[
            {
                "latitude": -23.2999866,
                "longitude":-47.6650897,
                "name": "Ponto 1"
            },
            {
                "latitude":-23.2829741,
                "longitude":-47.6745936,
                "name": "Ponto 2"
            },
             {
                "latitude": -23.27608779608440,
                "longitude":-47.67514362249426,
                "name": "Ponto 3"
            },
        ]
    )
