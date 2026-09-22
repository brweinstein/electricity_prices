# app/models/forecast.py

from typing import cast

import numpy as np
import pandas as pd

def _get_typical(
    baseline: pd.DataFrame,
    hour: int,
    is_weekend: bool,
    month: int | None = None,
) -> float:
    """Look up the typical price for a given hour and day-type"""
    key = (month, hour) if isinstance(baseline.index, pd.MultiIndex) else hour
    value = baseline.loc[key, is_weekend]
    if pd.isna(value):
        value = baseline.loc[key].dropna().median()
    if not isinstance(value, (int, float, np.number)) or pd.isna(value):
        raise TypeError(f"Expected numeric baseline value, got {type(value)}: {value}")
    return float(cast(float, value))

def current_deviation(current_price: float,
                      timestamp: pd.Timestamp,
                      baseline: pd.DataFrame) -> float:
    """% deviation from the typical price for this hour/day-type"""
    is_weekend = timestamp.dayofweek >= 5
    hour = timestamp.hour
    typical = _get_typical(baseline, hour, is_weekend, timestamp.month)
    return (current_price - typical) / typical * 100

def recommend(current_price: float,
              timestamp: pd.Timestamp,
              baseline: pd.DataFrame,
              threshold: float = 15.0) -> dict:
    """Return a recommendation based on how current price deviates from the seasonal baseline."""
    is_weekend = timestamp.dayofweek >= 5
    hour = timestamp.hour
    typical = _get_typical(baseline, hour, is_weekend, timestamp.month)
    deviation = (current_price - typical) / typical * 100

    if deviation <= -threshold:
        action = "good time to use electricity"
    elif deviation >= threshold:
        action = "wait if you can"
    else:
        action = "about average right now"

    return {
        "action": action,
        "deviation_pct": round(deviation, 1),
        "current_price": current_price,
        "typical_price": round(typical, 2),
        "is_weekend": bool(is_weekend),
        "hour": hour,
    }

def forecast_window(start: pd.Timestamp,
                    window_hours: int,
                    baseline: pd.DataFrame) -> dict:
    """Estimate each hour in a future window from the seasonal baseline."""
    timestamps = [start + pd.Timedelta(hours=offset) for offset in range(window_hours)]
    estimates = [
        round(_get_typical(baseline, timestamp.hour, timestamp.dayofweek >= 5, timestamp.month), 2)
        for timestamp in timestamps
    ]
    ranked_hours = sorted(
        zip(timestamps, estimates),
        key=lambda item: (item[1], item[0]),
    )[:3]
    average = sum(estimates) / len(estimates)
    recommendation = recommend(average, start, baseline)

    return {
        "start_time": start.isoformat(),
        "end_time": timestamps[-1].isoformat(),
        "window_hours": window_hours,
        "estimates": [
            {"timestamp": timestamp.isoformat(), "price": price}
            for timestamp, price in zip(timestamps, estimates)
        ],
        "best_hours": [
            {"timestamp": timestamp.isoformat(), "price": price}
            for timestamp, price in ranked_hours
        ],
        "average_price": round(average, 2),
        "lowest_price": min(estimates),
        "highest_price": max(estimates),
        "action": recommendation["action"],
        "deviation_pct": recommendation["deviation_pct"],
        "typical_price": recommendation["typical_price"],
    }