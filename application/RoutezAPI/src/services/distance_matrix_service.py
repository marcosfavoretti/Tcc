from core.dto.algoritmos_dto import PontoDTO
from typing import List, Tuple, Optional
import numpy as np
from infra.poi_dao import PoiDAO, get_poi_dao
from fastapi import Depends
from core.dto.menor_caminho_resultado import MenorCaminhoResultado 

class DistanceMatixService:
    def __init__(self, poiDao: PoiDAO):
        self.poi_dao = poiDao
    
    
    def build(self, ponto_inicial: PontoDTO, POIs: List[PontoDTO]) -> Tuple[np.ndarray, List[List[List[str]]]]:
        all_points = [ponto_inicial] + POIs
        n = len(all_points)

        dist_matrix = np.zeros((n, n))
        streets_matrix: List[List[List[str]]] = [[[] for _ in range(n)] for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    dist_matrix[i][j] = 0
                    streets_matrix[i][j] = []
                else:
                    
                    p1_osmid = all_points[i]['osmid']
                    p2_osmid = all_points[j]['osmid']
                    print(p1_osmid,p2_osmid)
                    
                    if p1_osmid is None or p2_osmid is None:
                        print(f"Erro: OSMID de ponto inválido encontrado. Pulando caminho entre {all_points[i].name} e {all_points[j].name}.")
                        dist_matrix[i][j] = float('inf')
                        streets_matrix[i][j] = []
                        continue 
                        
                    print(f"Buscando caminho entre {p1_osmid} e {p2_osmid}")
                    
                    
                    segment: Optional[MenorCaminhoResultado] = self.poi_dao.shortPathByPOI(p1_osmid, p2_osmid)
                    
                    if segment:
                        length_value = segment.get('totalLength', 0)
                        streets_ids = segment.get('streetsIds', [])
                        dist_matrix[i][j] = float(length_value)
                        streets_matrix[i][j] = streets_ids
                    else:
                        
                        dist_matrix[i][j] = float('inf') 
                        streets_matrix[i][j] = []
                        print(f"Aviso: Nenhum caminho encontrado entre POI {p1_osmid} e {p2_osmid}. Distância setada para infinito.")

        return dist_matrix, streets_matrix
    
def get_distance_matrix(
    poi_dao: PoiDAO = Depends(get_poi_dao), 
) -> DistanceMatixService: 
    return DistanceMatixService(poiDao=poi_dao)