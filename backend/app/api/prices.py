# app/api/prices.py

from fastapi import APIRouter
from app.data.cache import load_prices
from app.schemas import PriceHistoryPoint

router = APIRouter()

@router.get("/prices/history", response_model=list[PriceHistoryPoint])
def get_price_history(start: str | None = None, end: str | None = None):
    """Returns cached historical prices"""
    df = load_prices(start, end)
    return [
        {
            "timestamp": timestamp.isoformat(),
            "price_toronto": float(price),
        }
        for timestamp, price in zip(df["timestamp"], df["price_toronto"])
    ]