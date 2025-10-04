from core.dto.algoritmos_response_dto import AlgoritmosResponseDto 
from typing import List
from fastapi import APIRouter, Depends, Body,HTTPException
from services.poi_service import POIService
from py2neo import Graph
from config.neo4j_driver_config import Neo4jSingleton
from core.dto.algoritmos_dto import AlgoritmosDto
from services.algoritmo_service import AlgoritmoService, get_algoritmo_service
from services.forca_bruta_service import ForcaBrutaService, get_forca_bruta_service
import traceback
from services.fabrica_algoritmos_service import FabricaAlgoritmosService

router = APIRouter(
    prefix='/algoritmos'
)

def get_poi_service() -> POIService:
    driver: Graph = Neo4jSingleton.get_driver()
    return POIService(driver)

@router.get("/")
def algoritmos_disponiveis() -> List[str]:
    return [algoritmo.TIPO_ALGORITMO for algoritmo in FabricaAlgoritmosService.algoritmosRegistrados()]

@router.post("/")
def calcular_rota(
    dto: AlgoritmosDto = Body(...),  
    service: AlgoritmoService = Depends(get_algoritmo_service)
)-> AlgoritmosResponseDto:
    try:
        return service.run(dto) 
    except Exception as e:
        print(f"Ocorreu uma exceção: {type(e).__name__} - {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao calcular rota: {str(e)}")