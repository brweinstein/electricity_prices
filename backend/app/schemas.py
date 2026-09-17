# app/schemas.py

from pydantic import BaseModel

class RecommendationResponse(BaseModel):
    """Response shape for GET /recommendation"""
    action: str
    deviation_pct: float
    current_price: float
    typical_price: float
    is_weekend: bool
    hour: int

class ForecastPoint(BaseModel):
    timestamp: str
    price: float

class ForecastResponse(BaseModel):
    start_time: str
    end_time: str
    window_hours: int
    estimates: list[ForecastPoint]
    average_price: float
    lowest_price: float
    highest_price: float
    action: str
    deviation_pct: float
    typical_price: float

class PriceHistoryPoint(BaseModel):
    """A single timestamped price observation"""
    timestamp: str
    price_toronto: float