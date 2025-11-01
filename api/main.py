# api/main.py
"""
FastAPI principal. Registra routers:
- auth (login/refresh)
- ml (features/training/predict)
- endpoints core (books, categories, stats)
"""

from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
import logging
from api.config import settings
from api.schemas import Book, Health
from api.utils import load_data
from api.auth import get_current_user  # dependência para proteger rotas
from api import auth  # importa módulo para registrar router
from api import ml as ml_router  # importa router de ML

# registrar logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

app = FastAPI(title="Books API", version="1.1")

# registrar routers
app.include_router(auth.router)
app.include_router(ml_router.router)

# variável global com o dataframe
BOOKS_DF = None

@app.on_event("startup")
def startup_event():
    global BOOKS_DF
    try:
        BOOKS_DF = load_data(settings.DATA_PATH)
        logger.info("Dados carregados: %d registros", BOOKS_DF.shape[0])
    except Exception as e:
        logger.error("Erro ao carregar dados: %s", str(e))
        BOOKS_DF = None

# endpoint de health-check
@app.get("/api/v1/health", response_model=Health)
def health():
    if BOOKS_DF is None:
        raise HTTPException(status_code=500, detail="Dados não carregados")
    return {"status": "ok", "items": int(BOOKS_DF.shape[0])}

# listar livros (paginação simples via skip/limit)
@app.get("/api/v1/books", response_model=List[Book])
def list_books(skip: int = 0, limit: int = 100):
    if BOOKS_DF is None:
        raise HTTPException(status_code=500, detail="Dados não carregados")
    df = BOOKS_DF.iloc[skip: skip + limit]
    return df.to_dict(orient="records")

# obter livro por id
@app.get("/api/v1/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    if BOOKS_DF is None:
        raise HTTPException(status_code=500, detail="Dados não carregados")
    df = BOOKS_DF[BOOKS_DF["id"] == book_id]
    if df.empty:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return df.iloc[0].to_dict()

# busca por título e/ou categoria e opção de faixa de preço
@app.get("/api/v1/books/search", response_model=List[Book])
def search_books(
    title: Optional[str] = Query(None, description="Parte do título para buscar (case-insensitive)"),
    category: Optional[str] = Query(None, description="Categoria para filtrar (case-insensitive)"),
    min_price: Optional[float] = Query(None, description="Preço mínimo em £"),
    max_price: Optional[float] = Query(None, description="Preço máximo em £"),
    limit: int = 100
):
    if BOOKS_DF is None:
        raise HTTPException(status_code=500, detail="Dados não carregados")
    df = BOOKS_DF.copy()
    if title:
        df = df[df["title"].str.contains(title, case=False, na=False)]
    if category:
        df = df[df["category"].str.contains(category, case=False, na=False)]
    if min_price is not None:
        df = df[df["price_num"] >= min_price]
    if max_price is not None:
        df = df[df["price_num"] <= max_price]
    return df.head(limit).to_dict(orient="records")

# listar todas as categorias disponíveis
@app.get("/api/v1/categories")
def list_categories():
    if BOOKS_DF is None:
        raise HTTPException(status_code=500, detail="Dados não carregados")
    cats = BOOKS_DF["category"].dropna().unique().tolist()
    return {"categories": sorted(cats)}

# --- Endpoints opcionais de estatísticas (insights) ---

@app.get("/api/v1/stats/overview")
def stats_overview():
    if BOOKS_DF is None:
        raise HTTPException(status_code=500, detail="Dados não carregados")
    total = int(BOOKS_DF.shape[0])
    avg_price = float(BOOKS_DF["price_num"].dropna().mean())
    rating_dist = BOOKS_DF["rating"].value_counts().to_dict()
    return {"total_books": total, "avg_price": avg_price, "rating_distribution": rating_dist}

@app.get("/api/v1/books/top-rated", response_model=List[Book])
def top_rated(limit: int = 10):
    if BOOKS_DF is None:
        raise HTTPException(status_code=500, detail="Dados não carregados")
    df = BOOKS_DF.sort_values(by="rating", ascending=False)
    return df.head(limit).to_dict(orient="records")

from scripts.scrape_books import scrape_all_books

# Endpoint protegido: dispara scraping (executa em background)
@app.post("/api/v1/scraping/trigger")
def trigger_scraping(background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    """
    Endpoint protegido que dispara o scraping em background.
    Requer token Bearer válido (admin).
    """
    # adiciona a tarefa de scraping em background (não bloqueia a API)
    background_tasks.add_task(scrape_all_books)
    return {"status": "accepted", "detail": "Scraping em background iniciado"}