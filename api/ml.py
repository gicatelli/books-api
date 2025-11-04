# api/ml.py
"""
Endpoints pensados para consumo de modelos ML:
- /api/v1/ml/features        -> features prontas (JSON)
- /api/v1/ml/training-data  -> dataset pronto para treinar (CSV/JSON)
- /api/v1/ml/predictions    -> recebe features e retorna predições (simulação)
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import pandas as pd
from api.utils import load_data
from pydantic import BaseModel
from api.auth import get_current_user  # caso queira proteger endpoints ML, pode usar Depends

router = APIRouter(prefix="/api/v1/ml", tags=["ml"])

# Endpoint que retorna as features já processadas (lista)
@router.get("/features")
def get_features():
    df = load_data()
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Dados não disponíveis")
    # Exemplo de processamento básico de features:
    features = df[["id", "title", "price_num", "rating", "category"]].copy()
    # transforma availability em binário (0/1)
    features["in_stock"] = df["availability"].str.contains("In stock", case=False, na=False).astype(int)
    # preencher nulos
    features = features.fillna({"price_num": 0.0, "rating": 0})
    return features.to_dict(orient="records")

# Endpoint que retorna dataset pronto para treino (JSON)
@router.get("/training-data")
def get_training_data():
    df = load_data()
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Dados não disponíveis")
    # Dataset de exemplo: price_num (target), rating, category (string), in_stock
    data = pd.DataFrame({
        "price_num": df["price_num"],
        "rating": df["rating"].fillna(0),
        "category": df["category"].fillna("Unknown"),
        "in_stock": df["availability"].str.contains("In stock", case=False, na=False).astype(int)
    })
    # Retorna JSON com colunas prontas
    return {"columns": list(data.columns), "records": data.to_dict(orient="records")}

# Endpoint de predições - aqui fazemos uma predição simples (heurística)
import math
from api.schemas import PredictionRequestItem, PredictionResponseItem

@router.post("/predictions", response_model=List[PredictionResponseItem])
def predict(items: List[PredictionRequestItem]):
    """
    Faz predição de preço com base na categoria e rating.
    Aplica média de preço da categoria e ajusta conforme a nota.
    Garante que nenhum valor NaN ou inválido é retornado.
    """
    df = load_data()
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Dados não disponíveis")

    # Garantir que a coluna price_num não tenha NaN
    df["price_num"] = df["price_num"].fillna(df["price_num"].mean())
    df = df[df["price_num"].notna()]

    # Heurística simples: média de preços por categoria
    mean_prices = df.groupby("category")["price_num"].mean().fillna(df["price_num"].mean()).to_dict()
    default_mean = float(df["price_num"].mean())

    # Se default_mean for NaN, substitui por 0.0
    if math.isnan(default_mean) or math.isinf(default_mean):
        default_mean = 0.0

    results = []
    for item in items:
        cat = item.category or "Unknown"
        base = mean_prices.get(cat, default_mean)

        # Proteção contra NaN ou infinito
        if base is None or math.isnan(base) or math.isinf(base):
            base = default_mean

        rating = item.rating or 0.0
        predicted = base * (1 + (rating - 3) * 0.03)

        # Limpeza final
        if predicted is None or math.isnan(predicted) or math.isinf(predicted):
            predicted = default_mean

        results.append({
            "predicted_price": round(float(predicted), 2),
            "details": {
                "base": round(float(base), 2),
                "rating": rating,
                "category": cat
            }
        })

    return results