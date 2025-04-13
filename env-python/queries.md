
```WITH -23.2848682 AS targetLat, -47.6720885 AS targetLon  // Substitua com suas coordenadas

MATCH (a)-[r:ROAD_TO]->(b)
WHERE a.latitude IS NOT NULL AND a.longitude IS NOT NULL
  AND b.latitude IS NOT NULL AND b.longitude IS NOT NULL

WITH r, a, b,
     point({y: a.latitude, x: a.longitude}) AS pointA,
     point({y: b.latitude, x: b.longitude}) AS pointB,
     point({y: targetLat, x: targetLon}) AS targetPoint

WITH r, a, b,
     point.distance(pointA, targetPoint) AS distA,
     point.distance(pointB, targetPoint) AS distB

WITH r, a, b,
     CASE WHEN distA < distB THEN distA ELSE distB END AS minDist

ORDER BY minDist ASC
LIMIT 1

RETURN r, a, b, minDist
```

``` 
MATCH p=()-[r:ROAD_TO]->()
WHERE r.name IS NOT NULL AND toLower(r.name) CONTAINS toLower('coronel arruda') or toLower(r.name) CONTAINS toLower('são roque')
RETURN r, p
LIMIT 25
```