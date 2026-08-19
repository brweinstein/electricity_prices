# app/api/recommendation.py

from fastapi import APIRouter
import pandas as pd
from app.data.cache import load_prices
from app.models.seasonality import weekday_vs_weekend_baseline
from app.models.forecast import recommend
from app.schemas import RecommendationResponse

router = APIRouter()

@router.get("/recommendation", response_model=RecommendationResponse)
def get_recommendation(current_price: float):
    """Returns a fill-up-now-vs-wait recommendation"""
    df = load_prices()
    baseline = weekday_vs_weekend_baseline(df)
    result = recommend(current_price, pd.Timestamp.now(), baseline)
    return result