from itertools import chain
from py2neo import Node
from fastapi import Depends
from core.dto.algoritmos_dto import AlgoritmosDto
from services.distance_matrix_service import get_distance_matrix, DistanceMatixService # Importe o serviço de matriz
from infra.poi_dao import PoiDAO, get_poi_dao
from typing import List
from services.fabrica_algoritmos_service import FabricaAlgoritmosService
from core.dto.algoritmos_response_dto import AlgoritmosResponseDto
class AlgoritmoService:
    
    def __init__(self, poiDao: PoiDAO, matrixService: DistanceMatixService):
        self.poi_dao = poiDao
        self.matrixService = matrixService 
    
    def run(self, dto: AlgoritmosDto) -> AlgoritmosResponseDto:
        print("Instância de PoiDAO no AlgoritmoService.run:", self.poi_dao)
        
        algoritmo = FabricaAlgoritmosService.build(dto.algoritmo)
        
        print(algoritmo)
        
        pois_salvos: List[Node] = []
        
        all_input_points = [dto.ponto_inicial] + dto.pontos_interesse
        
        for ponto_dto_original in all_input_points:
            try:
                result_ponto = self.poi_dao.insert_poi(
                    lat=ponto_dto_original.latitude,
                    lon=ponto_dto_original.longitude,
                    name=ponto_dto_original.name
                )
                pois_salvos.append(result_ponto)
            except Exception as e:
                print(f"Erro ao processar POI '{ponto_dto_original.name}': {e}")
                raise 

        if len(pois_salvos) < 1:
            raise ValueError("Nenhum ponto válido foi processado. Impossível construir a matriz de distância ou calcular rota.")
        
        dist_matrix_np, streets_matrix_info = self.matrixService.build(
            pois_salvos[0],       
            pois_salvos[1:]       
        )
        
        best_path, min_distance, resultadoDasMetricas = algoritmo.executar(dist_matrix_np, pois_salvos)
        
        print(best_path)
        
        point_index = {p['osmid']: i for i, p in enumerate(pois_salvos)}

        street_ids = []

        for i in range(len(best_path) - 1):
            idx1 = point_index[best_path[i]['osmid']]
            idx2 = point_index[best_path[i + 1]['osmid']]
            street_ids.append(streets_matrix_info[idx1][idx2])

        resultList =  list(chain.from_iterable(street_ids))

        print(resultList, street_ids)
        
        return AlgoritmosResponseDto(
            algoritmo=dto.algoritmo,
            menorCaminho=min_distance,
            metricas=resultadoDasMetricas,
            ruas=resultList
        )

def get_algoritmo_service(
    poi_dao: PoiDAO = Depends(get_poi_dao),
    matrix_service: DistanceMatixService = Depends(get_distance_matrix) # Injeta o DistanceMatixService aqui
) -> AlgoritmoService:
    return AlgoritmoService(poi_dao, matrix_service)