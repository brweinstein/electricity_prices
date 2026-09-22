# app/models/seasonality.py

import pandas as pd

def hourly_baseline(df: pd.DataFrame) -> pd.Series:
    """Median price by hour-of-day"""
    hours = df["timestamp"].dt.hour
    return df.groupby(hours)["price_toronto"].median()

def dow_hourly_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """Median price by (day_of_week, hour)"""
    dow = df["timestamp"].dt.day_name()
    hour = df["timestamp"].dt.hour
    pivot = df.groupby([dow, hour])["price_toronto"].median().unstack()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return pivot.reindex(day_order)

def weekday_vs_weekend_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """Median price by (is_weekend, hour)"""
    is_weekend = df["timestamp"].dt.dayofweek >= 5
    hour = df["timestamp"].dt.hour
    baseline = df.groupby([is_weekend, hour])["price_toronto"].median().unstack(level=0)
    return baseline.reindex(index=range(24), columns=[False, True])


def monthly_weekday_vs_weekend_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """Median price by (month, hour, weekday/weekend)."""
    month = df["timestamp"].dt.month
    is_weekend = df["timestamp"].dt.dayofweek >= 5
    hour = df["timestamp"].dt.hour
    baseline = df.groupby([month, hour, is_weekend])["price_toronto"].median().unstack(level=2)
    index = pd.MultiIndex.from_product([range(1, 13), range(24)], names=["month", "hour"])
    return baseline.reindex(index=index, columns=[False, True])