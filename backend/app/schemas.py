# app/schemas.py

from pydantic import BaseModel

class RecommendationResponse(BaseModel):
    """Response shape for GET /recommendation"""
    action: str
    deviation_pct: float
    current_price: float
    typical_price: float
    is_weekend: float
    hour: int

class PriceHistoryPoint(BaseModel):
    """A single timestamped price observation"""
    timestamp: str
    price_toronto: float