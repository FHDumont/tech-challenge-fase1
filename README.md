# Tech Challenge Fase 1: API Pública para Consulta de Livros

## Descrição do Projeto

Este projeto é parte do Tech Challenge da Fase 1 da pós-graduação em Machine Learning Engineering. O objetivo é criar uma infraestrutura para extração de dados de livros via web scraping do site https://books.toscrape.com/, armazená-los em um arquivo CSV e e disponibilizá-los por meio de uma API RESTful usando FastAPI. O pipeline é projetado para escalabilidade e integração futura com modelos de machine learning, como sistemas de recomendação.

O projeto inclui:

- Web scraping robusto para capturar título, preço, rating, disponibilidade, categoria e URL da imagem de todos os livros.
- Armazenamento em arquivo CSV para persistência.
- API com endpoints obrigatórios e opcionais, documentada via Swagger.
- Containerização com Docker e orquestração via Docker Compose para facilitar o deploy e a reprodução.
- Pensado para ML: Dados formatados para features e treinamento.

## Arquitetura

```mermaid
graph TD
    A[Docker Compose: api + scraper] --> B[API FastAPI]
    B --> C[Endpoints abertos]
    B --> D[Autenticação]
    D --> E[Endpoints Fechados]
    E --> F[Scrap Web & Salvar CSV]
    E --> G[Outros endpoints]
    C --> L
    G --> L
    F --> L
    L[Queries no CSV via Panda] --> X[Resultados das APIs]
```

**Descrição da Arquitetura:**

- **Pipeline:** Ingestão (scraping) → Processamento (parse e salvar em CSV) → API (serviço RESTful) → Consumo (por apps ou ML pipelines).
- **Cenário de Uso para Cientistas de Dados/ML:** A API serve dados crus ou agregados para treinamento de modelos (ex: embeddings de títulos para recomendação via cosine similarity).
- **Plano de Integração com Modelos de ML:** Futuros endpoints como /ml/features podem retornar dados vetorizados; integre com tools como MLflow para tracking.

## Instruções de Instalação e Configuração

1. Clone o repositório: `git clone https://github.com/fhdumont/tech-challenge-fase1`
2. Entre na pasta: `cd tech-challenge-fase1`
3. Instale Python 3.13+ (baixe em https://www.python.org/downloads/).
4. Crie e ative um ambiente virtual: `python3.13 -m venv env && source env/bin/activate` (ou `env\Scripts\activate` no Windows).
5. Instale as dependências: `pip install -r requirements.txt`

## Instruções para Execução

Para rodar com Docker (local):

- Instale Docker e execute o arquivo build.sh para fazer build das imagens localmente
- Se desejar fazer push para o repositório do docker (hub.docker.com), execute o arquivo push.sh.
- Serão geradas as imagens para a plataforma amd64 como arm64.
- Execute `docker-compose up -d`

Para rodar sem Docker (local):

- Execute o arquivo run-app.sh
- Em outro terminal, execute o arquivo dashboard.sh

Para acessar as APIs

Independentemente se foi executado com Docker ou não, o acesso local se dá pelo mesmo endereço:

- Acesse: http://localhost:8000/docs para a documentação das API's
- Acesse: http://localhost:8000/api/v1/<nome_api>, conforme documentação
- Acesse: http://localhost:8501/ para o dashboard

## Documentação das Rotas da API

A API usa FastAPI, com documentação automática em `/docs` (Swagger UI).

### Endpoints abertos

- **GET /api/v1/books**: Lista todos os livros disponíveis.
- **GET /api/v1/books/search?title={title}&category={category}**: Busca livros por título e/ou categoria (case-insensitive).
- **GET /api/v1/categories**: Lista todas as categorias únicas.
- **GET /api/v1/health**: Verifica status da API e contagem de livros.
- **GET /api/v1/stats/overview**: Lista estatísticas dos livros (total de livros, média de preço e total de livros por rating)
- **GET /api/v1/stats/categories**: Lista estatísticas das categorias (nome da categoria, total de livros, média de preço, preço mínimo e preço máximo)
- **GET /api/v1/top-rated**: Lista os livros com a melhor avaliação (rating 5).
- **GET /api/v1/price-range**: Filtra livros dentro de uma faixa de preço específica, informando o preço mínimo e máximo.
- **GET /api/v1/books/{id}**: Retorna detalhes de um livro específico pelo ID.

### Endpoints com autenticação

- **POST /api/v1/login**: Endpoint para autenticação e obtenção de token JWT. Necessário informar username e password. Para efeitos de testes, utilizar username=admin e password=admin123. O token retornado tem duração de 30 minutos.
- **POST /api/v1/refresh**: Se a API for chamada antes do token expirar, ele será novado por mais 30 minutos. O token anterior será revogado.
- **POST /api/v1/scraping/trigger**: Necessário passar o token recebido no login no Header como "Baerer Token" para autenticar. Será realizada o scraping dos livros do site https://books.toscrape.com e salvos no CSV.

## Deploy

A API está em execução no endereço https://fiap.fernando.com.br, exemplos de endpoints:

- **https://fiap.fernando.com.br/docs**
- **https://fiap.fernando.com.br/api/v1/books**
- **https://fiap.fernando.com.br/api/v1/categories**
- **https://fiap.fernando.com.br/api/v1/books/top-rated**

## Vídeo de Apresentação

Link do vídeo: https://youtu.be/XXX.
