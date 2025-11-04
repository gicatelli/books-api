# 📚 Books API — FastAPI + Scraping + ML Pipeline

Projeto desenvolvido como parte do **Tech Challenge — Pós Tech Machine Learning Engineering (FIAP)**.

O sistema implementa **um pipeline completo de coleta, processamento e exposição de dados de livros** a partir do site *Books to Scrape*, com **autenticação JWT**, endpoints RESTful e **módulos preparados para integração com Machine Learning**.

---

## 🧠 Visão Geral e Arquitetura

### 🏗️ Descrição do Pipeline

O projeto segue um fluxo estruturado de ponta a ponta:

```
[BooksToScrape.com]
        │
        ▼
 (1) Web Scraper (Python + BeautifulSoup)
        │
        ▼
 (2) Data Processing (Pandas → CSV)
        │
        ▼
 (3) API Layer (FastAPI + JWT)
        │
        ▼
 (4) ML-ready Endpoints
        │
        ▼
 (5) Consumers (Dashboards, Cientistas de Dados, Modelos ML)
```

Cada camada é modular, permitindo **manutenção e escalabilidade** independentes:

* **Ingestão:** coleta os dados brutos diretamente do site.
* **Processamento:** normaliza e salva em `data/books.csv`.
* **API:** fornece endpoints públicos e protegidos com JWT.
* **ML Layer:** expõe dados pré-processados e simula predições.
* **Consumo:** cientistas de dados e sistemas externos podem consumir dados e modelos.

---

## ☁️ Arquitetura para Escalabilidade Futura

A arquitetura foi projetada para suportar expansão e integração com novas camadas:

```
┌─────────────────────────────┐
│        Frontend UI          │
│   (Dashboards ou Streamlit) │
└───────────────┬─────────────┘
                │
┌───────────────┴────────────────┐
│          FastAPI Layer         │
│  - /books, /ml, /auth, /stats  │
│  - Autenticação JWT            │
└───────────────┬────────────────┘
                │
┌───────────────┴────────────────┐
│       Data Processing Layer    │
│  - Pandas                      │
│  - Limpeza, Feature Engineering│
└───────────────┬────────────────┘
                │
┌───────────────┴────────────────┐
│        Data Storage (S3/DB)    │
│  - CSV → Banco SQL futuro      │
└───────────────┬────────────────┘
                │
┌───────────────┴────────────────┐
│     Machine Learning Layer     │
│  - Modelos scikit-learn/PyTorch│
│  - Endpoint `/ml/predictions`  │
└────────────────────────────────┘
```

> **Futuro:** o `books.csv` será substituído por um banco de dados SQL, e os modelos de Machine Learning serão servidos via FastAPI (endpoint `/predict` real).

---

## 🔬 Cenário de Uso para Cientistas de Dados / ML

Os cientistas de dados podem:

1. **Consumir `/ml/training-data`** para obter dataset completo para treino.
2. Realizar **feature engineering e modelagem offline**.
3. Enviar modelos treinados para o time de engenharia, que os **deploya via `/ml/predictions`**.
4. Monitorar métricas de desempenho via logs da API e dados históricos.

---

## 🤖 Plano de Integração com Modelos de ML

| Etapa | Descrição                                | Resultado Esperado                           |
| :---- | :--------------------------------------- | :------------------------------------------- |
| 1     | Consumir dataset via `/ml/training-data` | Dados limpos e balanceados                   |
| 2     | Treinar modelo (ex: regressão linear)    | Modelo `.pkl` salvo em `/models`             |
| 3     | Carregar modelo no backend FastAPI       | Endpoint `/api/v1/ml/predictions` atualizado |
| 4     | Retornar predições reais                 | Resposta JSON com preço estimado             |

---

## 🧩 Estrutura do Projeto

```
BooksApi/
│
├── api/
│   ├── __init__.py
│   ├── auth.py                  # Autenticação JWT
│   ├── config.py                # Configurações (lidas do .env)
│   ├── main.py                  # Aplicação principal (FastAPI)
│   ├── ml.py                    # Endpoints ML-ready
│   ├── schemas.py               # Modelos Pydantic
│   └── utils.py                 # Funções auxiliares
│
├── data/
│   └── books.csv                # Base de dados gerada pelo scraper
|
├── docs/
│   └── architecture.drawio.png  # Diagrama de arquitetura
|
├── scripts/
│   ├── __init__.py
│   └── scrape_books.py          # Web scraping de livros
│
├── tests/
│   └── test_api.py              # Testes automatizados
│
├── .env.example                 # Exemplo de variáveis de ambiente
├── README.md                    # Este arquivo
└── requirements.txt             # Dependências do projeto
```

---

## ⚙️ Instalação e Configuração

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/gicatelli/books-api.git
cd BooksApi
```

### 2️⃣ Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
```

### 3️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Configure suas credenciais no `.env`:

```ini
ADMIN_USER=admin
ADMIN_PASSWORD=admin123
JWT_SECRET=seu_jwt_secret_aqui
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_MINUTES=1440
DATA_PATH=data/books.csv
SCRAPER_BASE_URL=https://books.toscrape.com/
```

---

## 🧹 Rodar o Scraper

```bash
python -m scripts.scrape_books
```

Isso gera ou atualiza `data/books.csv` com os livros coletados.

---

## 🚀 Executar a API

```bash
uvicorn api.main:app --reload
```

Acesse:
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔑 Autenticação (JWT)

### Login

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
-H "Content-Type: application/json" \
-d '{"username": "admin", "password": "admin123"}'
```

**Resposta:**

```json
{
  "access_token": "<ACCESS_TOKEN>",
  "refresh_token": "<REFRESH_TOKEN>",
  "expires_in": 3600
}
```

### Renovar Token

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/refresh" \
-H "Content-Type: application/json" \
-d '{"refresh_token": "<REFRESH_TOKEN>"}'
```

### Usar Token

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/scraping/trigger" \
-H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

## 📡 Documentação dos Endpoints

| Método | Endpoint                      | Descrição                       |
| ------ | ----------------------------- | ------------------------------- |
| GET    | `/api/v1/health`              | Verifica status da API          |
| GET    | `/api/v1/books`               | Retorna todos os livros         |
| GET    | `/api/v1/books/{id}`          | Retorna detalhes de um livro    |
| GET    | `/api/v1/books/search?title=` | Busca por título                |
| GET    | `/api/v1/categories`          | Lista categorias                |
| GET    | `/api/v1/stats/overview`      | Estatísticas gerais             |
| GET    | `/api/v1/books/top-rated`     | Top livros                      |
| POST   | `/api/v1/scraping/trigger`    | **Protegido**: dispara scraping |
| GET    | `/api/v1/ml/features`         | Features processadas            |
| GET    | `/api/v1/ml/training-data`    | Dataset completo                |
| POST   | `/api/v1/ml/predictions`      | Predição simulada (heurística)  |

---

## 🧠 Exemplo `/ml/predictions`

### Request

```json
[
  {"category": "Poetry", "rating": 4},
  {"category": "Travel", "rating": 2}
]
```

### Response

```json
[
  {"predicted_price": 15.45, "details": {"base": 14.99, "rating": 4, "category": "Poetry"}},
  {"predicted_price": 7.88, "details": {"base": 8.12, "rating": 2, "category": "Travel"}}
]
```

---

## 🧱 Pipeline ML (Diagrama Conceitual)

```
        ┌──────────────────────────────┐
        │     BooksToScrape.com        │
        └──────────────┬───────────────┘
                       │
        ┌──────────────┴───────────────┐
        │  Scraper (BeautifulSoup4)    │
        └──────────────┬───────────────┘
                       │
        ┌──────────────┴───────────────┐
        │   Data Cleaning (Pandas)     │
        │   → data/books.csv           │
        └──────────────┬───────────────┘
                       │
        ┌──────────────┴───────────────┐
        │   FastAPI (Books API)        │
        │   /books, /ml, /auth         │
        └──────────────┬───────────────┘
                       │
        ┌──────────────┴───────────────┐
        │ Cientistas de Dados / ML     │
        │  (treino e predição)         │
        └──────────────────────────────┘
```

---

## 🧾 Créditos

**Autores:**
👩‍💻 Giovanna Catelli
👨‍💻 Pedro Cordeiro Franco

📘 Projeto acadêmico da Pós-Tech FIAP — *Machine Learning Engineering*
**Versão:** 1.2 (2025)