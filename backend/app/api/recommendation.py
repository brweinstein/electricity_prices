# app/api/recommendation.py

from fastapi import APIRouter, HTTPException, Query
import pandas as pd
from app.data.cache import load_prices
from app.models.seasonality import weekday_vs_weekend_baseline
from app.models.forecast import forecast_window, recommend
from app.schemas import ForecastResponse, RecommendationResponse

router = APIRouter()

@router.get("/recommendation", response_model=RecommendationResponse)
def get_recommendation(current_price: float):
    """Returns a fill-up-now-vs-wait recommendation"""
    df = load_prices()
    baseline = weekday_vs_weekend_baseline(df)
    result = recommend(current_price, pd.Timestamp.now(), baseline)
    return result

@router.get("/forecast", response_model=ForecastResponse)
def get_forecast(
    target_time: str,
    window_hours: int = Query(default=1),
):
    """Estimate future hourly prices using the historical seasonal baseline."""
    if window_hours not in (4, 12, 24, 168):
        raise HTTPException(status_code=400, detail="window_hours must be 4, 12, 24, or 168")

    try:
        timestamp = pd.Timestamp(target_time)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="target_time must be a valid date and time") from error

    df = load_prices()
    baseline = weekday_vs_weekend_baseline(df)
    return forecast_window(timestamp, window_hours, baseline)