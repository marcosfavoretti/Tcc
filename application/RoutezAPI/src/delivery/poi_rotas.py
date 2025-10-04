from fastapi import APIRouter, Depends
from services.poi_service import POIService, get_poi_service

router = APIRouter()

@router.get('/pois')
def get_all_pois(service: POIService = Depends(get_poi_service)):
    return service.get_all_pois()
