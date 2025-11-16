# Routez - Estudo Comparativo de Algoritmos para o Problema do Caixeiro Viajante

Este projeto implementa e compara algoritmos para o Problema do Caixeiro Viajante (PCV) através de uma aplicação web completa. Ele utiliza um banco de dados de grafos (Neo4j) para gerenciar e visualizar dados de grafos, um backend Python com FastAPI para a lógica de negócios e execução de algoritmos, e um frontend Angular para a interação do usuário. O foco principal é a análise combinatória de diferentes algoritmos para o PCV.

## Funcionalidades

*   **Interface Web Interativa:** Frontend desenvolvido com Angular para uma experiência de usuário dinâmica.
*   **API Backend Robusta:** Backend construído com Python FastAPI, responsável pela lógica de negócios e pela execução dos algoritmos do PCV.
*   **Banco de Dados de Grafos:** Neo4j para armazenamento e consulta eficientes de dados relacionados a grafos.
*   **Algoritmos do Problema do Caixeiro Viajante (PCV):** Implementação e estudo comparativo de vários algoritmos para resolver o PCV.
*   **Ambiente Dockerizado:** Configuração e implantação facilitadas usando Docker e Docker Compose.

## Tecnologias Utilizadas

*   **Frontend:** Angular, HTML, CSS, TypeScript
*   **Backend:** Python, FastAPI
*   **Banco de Dados:** Neo4j (Banco de Dados de Grafos)
*   **Containerização:** Docker, Docker Compose

## Como Executar

### Pré-requisitos

*   Docker Desktop instalado e em execução.

### Clonar o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd TCC
```
*Substitua `<URL_DO_SEU_REPOSITORIO>` pela URL real do seu repositório.*

### Iniciar a Aplicação

Navegue até o diretório `dev` e execute o Docker Compose:

```bash
cd dev
docker-compose up --build
```

Este comando irá:
*   Construir as imagens Docker para os serviços de frontend e backend.
*   Iniciar o contêiner do banco de dados Neo4j.
*   Iniciar a API backend, conectada ao Neo4j.
*   Iniciar a aplicação frontend, conectada ao backend.

### Acessar a Aplicação

*   **Frontend:** Abra seu navegador web e acesse `http://localhost:80`.
*   **API Backend (Documentação):** Acesse a documentação interativa do FastAPI em `http://localhost:8000/docs`.
*   **Neo4j Browser:** Acesse o navegador Neo4j em `http://localhost:7474` (login com `neo4j` / `test`).

## Estrutura do Projeto

*   `dev/`: Contém a configuração do Docker Compose para configurar o ambiente de desenvolvimento.
*   `application/Routez/`: Aplicação frontend Angular.
*   `application/RoutezAPI/`: Aplicação backend Python FastAPI.
*   `env-python/`: Ambiente Python com notebooks Jupyter, contendo implementações de algoritmos e scripts para a exportação o mapa como grafo para o neo4j.
*   `monografia/`: Contém o estudo acadêmico relacionado ao projeto, incluindo o documento PDF "ESTUDO COMPARATIVO DE ALGORITMOS PARA O PROBLEMA DO CAIXEIRO VIAJANTE SOB A ÓTICA DA ANÁLISE COMBINATÓRIA.pdf".
