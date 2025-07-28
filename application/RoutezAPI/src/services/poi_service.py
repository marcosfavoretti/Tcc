from py2neo import Graph
from infra.poi_dao import PoiDAO
from fastapi import Depends
from infra.poi_dao import get_poi_dao
from core.dto.menor_caminho_resultado import MenorCaminhoResultado

class POIService:
    def __init__(self, dao: PoiDAO = Depends(get_poi_dao)):
        self.DAO = dao
    
    def menorCaminhoEntre(self, poiId1: str, poiId2: str)-> MenorCaminhoResultado:
        result = self.DAO.shortPathByPOI(poiId1, poiId2)
        return result            
        
        
def get_poi_service(dao: PoiDAO = Depends(get_poi_dao)) -> POIService:
    return POIService(dao)