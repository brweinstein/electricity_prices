# app/api/prices.py

from fastapi import APIRouter
from app.data.cache import load_prices

router = APIRouter()

@router.get("/prices/history")
def get_price_history(start: str | None = None, end: str | None = None):
    """Returns cached historical prices"""
    df = load_prices(start, end)
    return df.to_dict(orient="records")