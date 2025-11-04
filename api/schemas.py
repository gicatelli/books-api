# api/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict

# Esquema que representa um livro retornado pela API
class Book(BaseModel):
    id: int
    title: str
    price: str
    rating: Optional[int] = None
    availability: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    book_url: Optional[str] = None

# Esquema simples para health-check
class Health(BaseModel):
    status: str
    items: int

class PredictionRequestItem(BaseModel):
    category: Optional[str] = None
    rating: Optional[float] = None


class PredictionResponseItem(BaseModel):
    predicted_price: float
    details: Dict[str, float | str]