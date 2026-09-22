# app/api/recommendation.py

from fastapi import APIRouter, HTTPException, Query
from functools import lru_cache
import pandas as pd
from app.data.cache import load_prices
from app.models.seasonality import monthly_weekday_vs_weekend_baseline
from app.models.forecast import forecast_window, recommend
from app.schemas import ForecastResponse, RecommendationResponse

router = APIRouter()

def normalize_forecast_timestamp(timestamp: pd.Timestamp) -> pd.Timestamp:
    """Convert aware client timestamps to the database's naive Ontario time."""
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_convert("America/Toronto").tz_localize(None)
    return timestamp

@lru_cache(maxsize=1)
def get_forecaster():
    from app.models.gbm_forecast import ResidualGBMForecaster

    return ResidualGBMForecaster.train(load_prices())

@router.get("/recommendation", response_model=RecommendationResponse)
def get_recommendation(current_price: float):
    """Returns a fill-up-now-vs-wait recommendation"""
    df = load_prices()
    baseline = monthly_weekday_vs_weekend_baseline(df)
    result = recommend(current_price, pd.Timestamp.now(), baseline)
    return result

@router.get("/forecast", response_model=ForecastResponse)
def get_forecast(
    target_time: str,
    window_hours: int = Query(default=1, ge=1, le=336),
):
    """Estimate future hourly prices with the residual gradient-boosted model."""
    try:
        timestamp = normalize_forecast_timestamp(pd.Timestamp(target_time))
    except ValueError as error:
        raise HTTPException(status_code=400, detail="target_time must be a valid date and time") from error

    try:
        return get_forecaster().forecast(timestamp, window_hours)
    except (ImportError, OSError, RuntimeError) as error:
        print(f"Residual GBM unavailable; using seasonal fallback: {error}")
        df = load_prices()
        baseline = monthly_weekday_vs_weekend_baseline(df)
        return forecast_window(timestamp, window_hours, baseline)