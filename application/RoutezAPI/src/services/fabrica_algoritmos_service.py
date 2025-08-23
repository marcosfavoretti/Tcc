from core.abstract.algoritmo_base import AlgoritmoBase
from core.enum.tipos_algoritmos import TipoAlgoritmo
from services.forca_bruta_service import get_forca_bruta_service
from services.algoritmo_genetico import get_algoritmo_genetico
from services.algoritmo_qaoa import get_algoritmo_QAOA

class FabricaAlgoritmosService:

    @staticmethod
    def build(alias: TipoAlgoritmo)-> AlgoritmoBase:
        if alias == TipoAlgoritmo.FORCA_BRUTA:
            return get_forca_bruta_service()
        
        elif alias == TipoAlgoritmo.GENETICO:
            return get_algoritmo_genetico()
        
        elif alias == TipoAlgoritmo.QAOA:
            return get_algoritmo_QAOA()
        else:
            raise Exception('Nao foi implementado esse algoritmo')

def get_fabricaAlgoritmosService()-> FabricaAlgoritmosService:
    return FabricaAlgoritmosService()