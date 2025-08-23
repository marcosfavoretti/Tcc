from typing import Optional, Union, Tuple, List, Dict
from core.dto.menor_caminho_resultado import MenorCaminhoResultado
from config.neo4j_driver_config import Neo4jSingleton
from shapely.geometry import Point, LineString
import uuid  
from geopy.distance import geodesic
from py2neo import Graph, Node, Relationship

class PoiDAO: 
    
    def __init__(self):
        self.driver = Neo4jSingleton.get_driver()

    
    def getRoads(self) -> Optional[List[Dict[str, Union[int, float, str]]]]:
        query = '''
        MATCH (a)-[r:ROAD_TO]->(b)
        WHERE a.latitude IS NOT NULL AND a.longitude IS NOT NULL
        AND b.latitude IS NOT NULL AND b.longitude IS NOT NULL
        RETURN id(a) AS from_id, id(b) AS to_id,
            a.latitude AS from_lat, a.longitude AS from_lon,
            b.latitude AS to_lat, b.longitude AS to_lon,
            r.length AS length, id(r) AS rel_id,
            r.highway AS highway, r.name AS name, r.oneway AS oneway
        '''

        try:
            result = self.driver.run(query).data()

            if not result:
                print("No roads found. The query returned no data.")
                return []

            roads = []
            for record in result:
                road = {}

                if 'from_id' in record and 'to_id' in record:
                    road['from_id'] = record['from_id']
                    road['to_id'] = record['to_id']
                else:
                    print(f"Missing ids for road: {record}")
                    continue

                road['from_lat'] = record.get('from_lat', None)
                road['from_lon'] = record.get('from_lon', None)
                road['to_lat'] = record.get('to_lat', None)
                road['to_lon'] = record.get('to_lon', None)

                road['length'] = record.get('length', 0.0) 
                road['rel_id'] = record.get('rel_id', None)

                road['highway'] = record.get('highway', None)
                road['name'] = record.get('name', None)
                road['oneway'] = record.get('oneway', None)

                roads.append(road)

            return roads

        except Exception as e:
            print(f"An error occurred while fetching roads: {str(e)}")
            return []
        
    
    def findPoiByLatAndLog(self,lat: float, lon: float) -> Optional[Dict[str, Union[str, float]]]:
        if not isinstance(lat, (float, int)) or not isinstance(lon, (float, int)):
            print(f"Erro: latitude ou longitude fornecida não são válidas. Latitude: {lat}, Longitude: {lon}")
            return None
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            print(f"Erro: valores de latitude ou longitude fora do intervalo válido. Latitude: {lat}, Longitude: {lon}")
            return None
        query = '''
        MATCH (poi:POI)
        WHERE poi.latitude = $lat AND poi.longitude = $lon
        RETURN poi.osmid AS osmid, poi.name AS name, poi.latitude AS latitude, poi.longitude AS longitude
        '''
        try:
            result = self.driver.run(query, lat=lat, lon=lon).data()
            if not result:
                print(f"Aviso: Nenhum POI encontrado para Latitude: {lat}, Longitude: {lon}")
                return None
            data = result[0]
            if 'osmid' not in data or 'name' not in data or 'latitude' not in data or 'longitude' not in data:
                print(f"Erro: Estrutura de dados inesperada retornada. Dados: {data}")
                return None
            return {
                "osmid": data['osmid'],
                "name": data['name'],
                "latitude": data['latitude'],
                "longitude": data['longitude']
            }

        except Exception as e:
            print(f"Erro ao executar a consulta: {str(e)}")
            return None
    
    def shortPathByPOI(
    self,
    poiId1: str,
    poiId2: str
) -> Optional[Dict[str, Union[float, List]]]:

        if not poiId1 or not isinstance(poiId1, str):
            print(f"Invalid poiId1: {poiId1}")
            return None
        if not poiId2 or not isinstance(poiId2, str):
            print(f"Invalid poiId2: {poiId2}")
            return None

        query = '''
        MATCH (poi1:POI {osmid: $poiId1})-[:CONNECTED_TO]->(start:Node),
            (poi2:POI {osmid: $poiId2})-[:CONNECTED_TO]->(end:Node)
        CALL apoc.algo.dijkstra(start, end, 'ROAD_TO>', 'length') 
        YIELD path, weight

        UNWIND relationships(path) AS rel
        WITH weight, rel,
            startNode(rel) AS fromNode,
            endNode(rel) AS toNode
        RETURN 
            weight AS totalLength,
            COLLECT([
                fromNode.latitude, fromNode.longitude,
                toNode.latitude, toNode.longitude
            ]) AS pathCoordinates,
            COLLECT(rel.osmid) AS streetsIds
        '''

        try:
            result = self.driver.run(query, poiId1=poiId1, poiId2=poiId2).data()

            if not result:
                print(f"No path found between POIs {poiId1} and {poiId2}")
                return None

            data = result[0]

            if 'totalLength' not in data or 'pathCoordinates' not in data:
                print(f"Unexpected result structure: {data}")
                return None

            # Formatar como lista de pares de coordenadas para o frontend (Leaflet)
            route_lines = [
                [[lat1, lon1], [lat2, lon2]]
                for lat1, lon1, lat2, lon2 in data["pathCoordinates"]
            ]

            return {
                "totalLength": round(data['totalLength'], 2),
                "streetsIds": data['streetsIds'],
                "routeLines": route_lines
            }

        except Exception as e:
            print(f"An error occurred while querying the database: {str(e)}")
            return None

    def insert_poi(self, lat: float, lon: float, name:str, label='POI') -> Node:
        node = self.findPoiByLatAndLog(lat, lon)
        if(node):
            return node
        roads = self.getRoads()
        poi_point = Point(lon, lat)
        closest = None
        min_dist = float('inf')
        # Encontrar a aresta mais próxima ao ponto informado
        for road in roads:
            a = Point(road['from_lon'], road['from_lat'])
            b = Point(road['to_lon'], road['to_lat'])
            line = LineString([a, b])
            proj = line.interpolate(line.project(poi_point))
            dist = geodesic((lat, lon), (proj.y, proj.x)).meters

            if dist < min_dist:
                min_dist = dist
                closest = {**road, 'proj_point': proj}

        if not closest:
            print("Nenhuma aresta próxima encontrada.")
            return

        proj = closest['proj_point']

        mid_node = Node("Node",
                        latitude=proj.y,
                        longitude=proj.x,
                        osmid=str(uuid.uuid4()))
        
        self.driver.create(mid_node)
        
        poi_node = Node(label,
                        name=name,
                        latitude=lat,
                        longitude=lon,
                        osmid=str(uuid.uuid4())
                        )
        self.driver.create(poi_node)

        self.driver.create(Relationship(poi_node, "CONNECTED_TO", mid_node,
                                    distance=min_dist))

        # Remover aresta original
        self.driver.run("MATCH ()-[r]->() WHERE id(r) = $id DELETE r", id=closest['rel_id'])

        # Criar novas arestas dividindo a original
        from_id = closest['from_id']
        to_id = closest['to_id']
        mid_id = mid_node.identity

        len1 = geodesic((closest['from_lat'], closest['from_lon']), (proj.y, proj.x)).meters
        len2 = geodesic((closest['to_lat'], closest['to_lon']), (proj.y, proj.x)).meters

        self.driver.run('''
            MATCH (a), (b), (c)
            WHERE id(a) = $from_id AND id(b) = $to_id AND id(c) = $mid_id
            CREATE (a)-[:ROAD_TO {
                length: $len1,
                highway: $highway,
                name: $name,
                oneway: $oneway
            }]->(c),
            (c)-[:ROAD_TO {
                length: $len2,
                highway: $highway,
                name: $name,
                oneway: $oneway
            }]->(b)
        ''', parameters={
            "from_id": from_id,
            "to_id": to_id,
            "mid_id": mid_id,
            "len1": len1,
            "len2": len2,
            "highway": closest['highway'],
            "name": closest['name'],
            "oneway": closest['oneway'],
        })
        
        print(f"POI criado e conectado no ponto mais próximo da rua: {closest['name'] or 'desconhecida'}")
        return poi_node
        
def get_poi_dao() -> PoiDAO:
    return PoiDAO()