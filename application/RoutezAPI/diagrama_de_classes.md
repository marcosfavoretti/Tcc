
```mermaid
classDiagram
    direction LR

    class AlgoritmoBase {
        <<Abstract>>
        +TIPO_ALGORITMO: str
        +adicionar_metrica(metrica: MetricasBase)
        +executar(dist_matrix, pontos)
        +_executar_logica_algoritmo(dist_matrix, pontos)*
        +_notificar_inicio_execucao()
        +_notificar_fim_execucao(melhorCaminho, distancia)
    }

    class MetricasBase {
        <<Abstract>>
        +on_inicio_execucao(algoritmo)*
        +on_fim_execucao(algoritmo, resultado)*
        +resultadoFinal()* MetricaDto
        +get_description() str
    }

    package "Algoritmos Concretos" {
        class ForcaBrutaService
        class AlgoritmoGenetico
        class AlgoritmoSimulatedAnnealing
        class AlgoritmoQAOA
        class AlgoritmoQAOAAmazon
        class AlgoritmoIQAOAAmazon
        class AlgoritmoIQAOAAmazonSimulador
    }

    package "Métricas Concretas" {
        class TempoExecucao
        class Distancia
        class SequenciaExecucao
        class UsoMemoria
        class MetricaPreco
        class MetricaQubits
        class MetricasQuanticas
        class CircuitoQuanticoImagem
        class MetricaQuantidadeShotsQuanticas
        class MetricaQuantidadeTaskQuanticas
    }

    package "Delivery (API Endpoints)" {
        class algoritmos_rotas {
            +GET /
            +POST /
        }
        class poi_rotas {
            +GET /pois
        }
    }

    package "Services" {
        class AlgoritmoService {
            +run(dto: AlgoritmosDto) AlgoritmosResponseDto
        }
        class POIService {
            +get_all_pois()
            +menorCaminhoEntre(poiId1, poiId2)
        }
        class DistanceMatixService {
            +build(ponto_inicial, POIs)
        }
        class FabricaAlgoritmosService {
            +build(alias: str) AlgoritmoBase
            +algoritmosRegistrados() List~AlgoritmoBase~
        }
        class WorkerService {
            +execute_algorithm_in_worker(algoritmo, ...)
        }
    }

    package "Infra" {
        class PoiDAO {
            +getRoads()
            +findPoiByLatAndLog(lat, lon)
            +shortPathByPOI(poiId1, poiId2)
            +insert_poi(lat, lon, name)
            +get_all_pois()
        }
        class Neo4jSingleton {
            +get_driver() Graph
        }
    }

    package "Core (DTOs)" {
        class AlgoritmosDto
        class PontoDTO
        class AlgoritmosResponseDto
        class MetricaDto
    }

    ' Relações de Herança
    AlgoritmoBase <|-- ForcaBrutaService
    AlgoritmoBase <|-- AlgoritmoGenetico
    AlgoritmoBase <|-- AlgoritmoSimulatedAnnealing
    AlgoritmoBase <|-- AlgoritmoQAOA
    AlgoritmoBase <|-- AlgoritmoQAOAAmazon
    AlgoritmoBase <|-- AlgoritmoIQAOAAmazon
    AlgoritmoBase <|-- AlgoritmoIQAOAAmazonSimulador

    MetricasBase <|-- TempoExecucao
    MetricasBase <|-- Distancia
    MetricasBase <|-- SequenciaExecucao
    MetricasBase <|-- UsoMemoria
    MetricasBase <|-- MetricaPreco
    MetricasBase <|-- MetricaQubits
    MetricasBase <|-- MetricasQuanticas
    MetricasBase <|-- CircuitoQuanticoImagem
    MetricasBase <|-- MetricaQuantidadeShotsQuanticas
    MetricasBase <|-- MetricaQuantidadeTaskQuanticas

    ' Relações de Dependência e Composição
    algoritmos_rotas --> AlgoritmoService : "depends on"
    algoritmos_rotas --> FabricaAlgoritmosService : "uses"
    poi_rotas --> POIService : "depends on"

    AlgoritmoService --> FabricaAlgoritmosService : "uses"
    AlgoritmoService --> DistanceMatixService : "uses"
    AlgoritmoService --> PoiDAO : "uses"
    AlgoritmoService --> WorkerService : "uses"
    
    WorkerService --> AlgoritmoBase : "executes"

    POIService --> PoiDAO : "uses"
    DistanceMatixService --> PoiDAO : "uses"
    PoiDAO --> Neo4jSingleton : "uses"

    AlgoritmoBase o-- "many" MetricasBase : "has"
    
    FabricaAlgoritmosService ..> ForcaBrutaService : "creates"
    FabricaAlgoritmosService ..> AlgoritmoGenetico : "creates"
    FabricaAlgoritmosService ..> AlgoritmoSimulatedAnnealing : "creates"
    FabricaAlgoritmosService ..> AlgoritmoQAOAAmazon : "creates"
    FabricaAlgoritmosService ..> AlgoritmoIQAOAAmazon : "creates"
    FabricaAlgoritmosService ..> AlgoritmoIQAOAAmazonSimulador : "creates"

    ' Relações com DTOs
    algoritmos_rotas ..> AlgoritmosDto : "receives"
    algoritmos_rotas ..> AlgoritmosResponseDto : "returns"
    AlgoritmoService ..> AlgoritmosDto : "receives"
    AlgoritmoService ..> AlgoritmosResponseDto : "returns"
    AlgoritmoBase ..> MetricaDto : "returns"
    MetricasBase ..> MetricaDto : "returns"

```
