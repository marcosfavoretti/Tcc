from core.abstract.algoritmo_base import AlgoritmoBase
from core.enum.tipos_algoritmos import TipoAlgoritmo
from services.forca_bruta_service import get_forca_bruta_service
class FabricaAlgoritmosService:

    @staticmethod
    def build(alias: TipoAlgoritmo)-> AlgoritmoBase:
        if alias == TipoAlgoritmo.FORCA_BRUTA:
            return get_forca_bruta_service()
        else:
            raise Exception('Nao foi implementado esse algoritmo')

def get_fabricaAlgoritmosService()-> FabricaAlgoritmosService:
    return FabricaAlgoritmosService()