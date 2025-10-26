from core.abstract.algoritmo_base import AlgoritmoBase
from services.forca_bruta_service import get_forca_bruta_service
from services.algoritmo_genetico import get_algoritmo_genetico
from services.algoritmo_qaoa import get_algoritmo_QAOA
from services.algoritmo_qaoa_amazon import get_algoritmo_QAOA_Amazon
from services.simulate_annealing import get_algoritmo_SA
from services.algoritmo_iqaoa_amazon import get_algoritmo_IQAOA_Amazon
from typing import List
from services.algoritmo_iqaoa_amazon_simulador import get_algoritmo_IQAOA_AmazonSim
from services.algoritmo_iqaoa_amazon_upload import get_algoritmo_IQAOA_AmazonSimUpload
class FabricaAlgoritmosService:
    
    @staticmethod
    def algoritmosRegistrados() -> List[AlgoritmoBase]:
        """Retorna uma lista com uma instância de cada algoritmo disponível."""
        return [
            get_algoritmo_IQAOA_AmazonSimUpload(),
            get_forca_bruta_service(),
            get_algoritmo_IQAOA_Amazon(),
            get_algoritmo_genetico(),
            # get_algoritmo_QAOA(),
            get_algoritmo_QAOA_Amazon(),
            get_algoritmo_SA(),
            get_algoritmo_IQAOA_AmazonSim()
        ]

    @staticmethod
    def build(alias: str) -> AlgoritmoBase:
        """
        Constrói e retorna a instância do algoritmo correspondente ao alias fornecido.

        A busca é feita dinamicamente na lista de algoritmos registrados,
        comparando o alias com o atributo 'TIPO_ALGORITMO' de cada um.
        """
        algoritmos_disponiveis = FabricaAlgoritmosService.algoritmosRegistrados()

        for algoritmo in algoritmos_disponiveis:
            if algoritmo.TIPO_ALGORITMO == alias:
                return algoritmo  
        
        raise NotImplementedError(f"O algoritmo com o alias '{alias}' não foi encontrado ou registrado na fábrica.")

def get_fabricaAlgoritmosService() -> FabricaAlgoritmosService:
    return FabricaAlgoritmosService()