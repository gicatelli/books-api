# 📚 Books API — FastAPI + Scraping + ML Pipeline

Projeto desenvolvido como parte do **Tech Challenge - Pós Tech Machine Learning Engineering (FIAP)**.
O objetivo é criar uma **API completa** que realiza *web scraping*, expõe os dados em endpoints RESTful, possui *autenticação JWT* e disponibiliza *endpoints preparados para Machine Learning*.

---

## 🚀 Tecnologias Utilizadas

* **Python 3.11+**
* **FastAPI** — Framework principal da API
* **Uvicorn** — Servidor ASGI
* **Pandas** — Manipulação e análise de dados
* **Python-JOSE** — Geração e validação de tokens JWT
* **Passlib** — Utilitários de autenticação (hash de senhas)
* **Requests / BeautifulSoup4** — Scraping de dados

---

## 📂 Estrutura do Projeto

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

## ⚙️ Configuração do Ambiente

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/gicatelli/books-api.git
cd BooksApi
```

### 2️⃣ Criar ambiente virtual (Windows)

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3️⃣ Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Configurar variáveis de ambiente

Copie o arquivo de exemplo:

```bash
Copy-Item -Path .env.example -Destination .env
```

Edite o `.env` conforme necessário:

```ini
DATA_PATH=data/books.csv
SCRAPER_BASE_URL=https://books.toscrape.com/
ADMIN_USER=admin
ADMIN_PASSWORD=admin123
JWT_SECRET=JWT_SECRET=sbkefjscleirfnliekjrfnlieakfjn
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_MINUTES=1440
```

---

## 🧹 Scraping (Coleta de Dados)

Para gerar ou atualizar o dataset (`data/books.csv`):

```bash
python -m scripts.scrape_books
```

Os dados coletados incluem:

* Título
* Preço
* Avaliação
* Categoria
* Disponibilidade
* URL da imagem

---

## 🧩 Execução da API

Inicie o servidor localmente:

```bash
uvicorn api.main:app --reload --port 8000
```

Acesse a documentação interativa (Swagger):
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔑 Autenticação (JWT)

Algumas rotas administrativas estão protegidas com **JWT**.

### 🔹 Obter Token (Login)

```
POST /api/v1/auth/login
```

Body (form-data):

```
username=admin
password=admin123
```

Exemplo CURL:

```bash
curl --location 'http://127.0.0.1:8000/api/v1/auth/login' \
--header 'Content-Type: application/json' \
--data '{
  "username": "admin",
  "password": "admin123"
}'
```

Resposta:

```json
{
  "access_token": "<ACCESS_TOKEN>",
  "refresh_token": "<REFRESH_TOKEN>",
  "expires_in": 3600
}
```

### 🔹 Renovar Token

```
POST /api/v1/auth/refresh
```

Exemplo CURL:

```bash
curl --location 'http://127.0.0.1:8000/api/v1/auth/refresh' \
--header 'Content-Type: application/json' \
--data '{"refresh_token":"<REFRESH_TOKEN>"}'
```

### 🔹 Usar Token em Rotas Protegidas

Adicione o cabeçalho:

```
Authorization: Bearer <ACCESS_TOKEN>
```

Exemplo:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/scraping/trigger" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

## 🧰 Endpoints Principais

| Método | Endpoint                      | Descrição                                           |
| :----: | :---------------------------- | :-------------------------------------------------- |
|   GET  | `/api/v1/health`              | Verifica se a API está saudável                     |
|   GET  | `/api/v1/books`               | Lista todos os livros                               |
|   GET  | `/api/v1/books/{id}`          | Detalhes de um livro específico                     |
|   GET  | `/api/v1/books/search?title=` | Pesquisa por título                                 |
|   GET  | `/api/v1/categories`          | Lista categorias disponíveis                        |
|   GET  | `/api/v1/stats/overview`      | Retorna estatísticas gerais                         |
|   GET  | `/api/v1/books/top-rated`     | Lista livros mais bem avaliados                     |
|  POST  | `/api/v1/scraping/trigger`    | **(Protegido)** Executa novo scraping em background |

---

## 🤖 Endpoints ML-Ready

### `GET /api/v1/ml/features`

Retorna features processadas para uso em modelos ML.

Exemplo:

```json
[
  {
    "id": 1,
    "title": "Book Example",
    "price_num": 15.99,
    "rating": 4,
    "category": "Poetry",
    "in_stock": 1
  }
]
```

---

### `GET /api/v1/ml/training-data`

Retorna o dataset completo formatado para treino de modelos.

```json
{
  "columns": ["price_num","rating","category","in_stock"],
  "records": [
    {"price_num": 12.99,"rating":4,"category":"Poetry","in_stock":1},
    {"price_num": 8.99,"rating":2,"category":"Travel","in_stock":1}
  ]
}
```

---

### `POST /api/v1/ml/predictions`

Recebe features e retorna predições simuladas (heurística baseada na média de preço por categoria e nota).

Request:

```json
[
  {"category": "Poetry", "rating": 4},
  {"category": "Travel", "rating": 2}
]
```

Response:

```json
[
  {"predicted_price": 15.45, "details": {"base": 14.99, "rating": 4, "category": "Poetry"}},
  {"predicted_price": 7.88, "details": {"base": 8.12, "rating": 2, "category": "Travel"}}
]
```

---

## 🔐 Endpoint Protegido: Scraping Manual

Executa novamente o scraping (requisição protegida por JWT):

```
POST /api/v1/scraping/trigger
```

Cabeçalho obrigatório:

```
Authorization: Bearer <ACCESS_TOKEN>
```

Resposta:

```json
{"status":"accepted","detail":"Scraping em background iniciado"}
```

---

## 🧱 Deploy (Render.com)

1. Crie conta em [https://render.com](https://render.com)
2. Conecte sua conta GitHub.
3. Novo “Web Service” → selecione seu repositório.
4. Configure:

   * Build command: `pip install -r requirements.txt`
   * Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Deploy automático a cada push.

---

## 🧠 Pipeline ML (resumo conceitual)

```
[SITE - BooksToScrape]
        │
        ▼
 [Scraper Python]
 (scripts/scrape_books.py)
        │
        ▼
  [Dataset CSV local]
        │
        ▼
   [FastAPI Server]
   ├─ /books (dados brutos)
   ├─ /ml/features (pré-processados)
   └─ /ml/training-data (para treino)
```

Futuramente, um modelo pode ser treinado com esses dados e disponibilizado
via `/api/v1/ml/predictions` com predições reais.

---

## 🛡️ Segurança e Boas Práticas

* Tokens JWT com expiração configurável.
* Variáveis sensíveis isoladas no `.env`.
* Rotas administrativas protegidas.
* Recomenda-se HTTPS em produção.
* Armazenar senhas com hash (bcrypt).
* Utilizar `JWT_SECRET` forte e único.

---

## 🧾 Créditos e Autoria

Desenvolvido por **Giovanna Catelli** e **Pedro Cordeiro Franco**
📘 Projeto acadêmico da Pós Tech FIAP - Machine Learning Engineering
Versão: `1.1`
Ano: `2025`