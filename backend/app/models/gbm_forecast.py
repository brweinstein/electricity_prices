"""Residual gradient-boosted forecast model with leakage-safe lag features."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor

from app.models.forecast import _get_typical, recommend
from app.models.seasonality import monthly_weekday_vs_weekend_baseline

FEATURE_COLUMNS = [
    "hour",
    "day_of_week",
    "month",
    "is_weekend",
    "is_holiday",
    "hour_sin",
    "hour_cos",
    "day_of_year_sin",
    "day_of_year_cos",
    "baseline_price",
    "lag_1",
    "lag_24",
    "lag_168",
    "rolling_mean_24",
    "rolling_std_24",
    "rolling_mean_168",
    "rolling_std_168",
    "rolling_range_24",
]


def _easter_sunday(year: int) -> pd.Timestamp:
    """Return Easter Sunday using the Gregorian computus."""
    century = year // 100
    year_remainder = year % 100
    correction = century - century // 4 - (8 * century + 13) // 25
    shifted = (19 * (year % 19) + century - century // 4 - correction + 15) % 30
    weekday = (32 + 2 * (century % 4) + 2 * (year_remainder // 4) - shifted - year_remainder % 4) % 7
    month = (shifted + weekday + 114) // 31
    day = (shifted + weekday + 114) % 31 + 1
    return pd.Timestamp(year=year, month=month, day=day)


def _ontario_holidays(year: int) -> set[pd.Timestamp]:
    dates = {
        pd.Timestamp(year=year, month=1, day=1),
        pd.Timestamp(year=year, month=7, day=1),
        pd.Timestamp(year=year, month=9, day=1),
        pd.Timestamp(year=year, month=11, day=11),
        pd.Timestamp(year=year, month=12, day=25),
        pd.Timestamp(year=year, month=12, day=26),
    }
    dates.add(_nth_weekday(year, 2, 0, 3))
    dates.add(_last_weekday_before(year, 5, 25, 0))
    dates.add(_nth_weekday(year, 10, 0, 2))
    dates.add(_nth_weekday(year, 8, 0, 1))
    dates.add(_nth_weekday(year, 9, 0, 1))
    dates.add(_easter_sunday(year) - pd.Timedelta(days=2))
    return dates


def _nth_weekday(year: int, month: int, weekday: int, occurrence: int) -> pd.Timestamp:
    first = pd.Timestamp(year=year, month=month, day=1)
    return first + pd.Timedelta(days=(weekday - first.weekday()) % 7 + 7 * (occurrence - 1))


def _last_weekday_before(year: int, month: int, day: int, weekday: int) -> pd.Timestamp:
    current = pd.Timestamp(year=year, month=month, day=day)
    return current - pd.Timedelta(days=(current.weekday() - weekday) % 7 or 7)


def _holiday_flags(timestamps: pd.Series) -> pd.Series:
    holidays = set().union(*(_ontario_holidays(year) for year in timestamps.dt.year.unique()))
    return timestamps.dt.normalize().isin(holidays).astype(int)


def build_feature_frame(data: pd.DataFrame, baseline: pd.DataFrame) -> pd.DataFrame:
    """Build features using current and prior observations only."""
    frame = data.sort_values("timestamp").reset_index(drop=True).copy()
    timestamps = frame["timestamp"]
    prices = frame["price_toronto"].astype(float)
    is_weekend = timestamps.dt.dayofweek >= 5
    frame["hour"] = timestamps.dt.hour
    frame["day_of_week"] = timestamps.dt.dayofweek
    frame["month"] = timestamps.dt.month
    frame["is_weekend"] = is_weekend.astype(int)
    frame["is_holiday"] = _holiday_flags(timestamps)
    frame["hour_sin"] = np.sin(2 * np.pi * timestamps.dt.hour / 24)
    frame["hour_cos"] = np.cos(2 * np.pi * timestamps.dt.hour / 24)
    frame["day_of_year_sin"] = np.sin(2 * np.pi * timestamps.dt.dayofyear / 365.25)
    frame["day_of_year_cos"] = np.cos(2 * np.pi * timestamps.dt.dayofyear / 365.25)
    frame["baseline_price"] = [
        _get_typical(baseline, timestamp.hour, bool(weekend), timestamp.month)
        for timestamp, weekend in zip(timestamps, is_weekend)
    ]
    prior = prices.shift(1)
    frame["lag_1"] = prices.shift(1)
    frame["lag_24"] = prices.shift(24)
    frame["lag_168"] = prices.shift(168)
    frame["rolling_mean_24"] = prior.rolling(24, min_periods=24).mean()
    frame["rolling_std_24"] = prior.rolling(24, min_periods=24).std()
    frame["rolling_mean_168"] = prior.rolling(168, min_periods=168).mean()
    frame["rolling_std_168"] = prior.rolling(168, min_periods=168).std()
    frame["rolling_range_24"] = prior.rolling(24, min_periods=24).max() - prior.rolling(24, min_periods=24).min()
    frame["residual"] = prices - frame["baseline_price"]
    return frame


@dataclass
class ResidualGBMForecaster:
    history: pd.DataFrame
    baseline: pd.DataFrame
    model: LGBMRegressor

    @classmethod
    def train(cls, history: pd.DataFrame) -> "ResidualGBMForecaster":
        history = history.sort_values("timestamp").reset_index(drop=True)
        baseline = monthly_weekday_vs_weekend_baseline(history)
        features = build_feature_frame(history, baseline).dropna(subset=FEATURE_COLUMNS + ["residual"])
        model = LGBMRegressor(
            objective="huber",
            alpha=0.9,
            n_estimators=400,
            learning_rate=0.04,
            num_leaves=31,
            max_depth=-1,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            verbosity=-1,
        )
        model.fit(features[FEATURE_COLUMNS], features["residual"])
        return cls(history=history, baseline=baseline, model=model)

    def predict_rows(self, data: pd.DataFrame) -> pd.DataFrame:
        features = build_feature_frame(data, self.baseline)
        valid = features.dropna(subset=FEATURE_COLUMNS).copy()
        valid["predicted_residual"] = self.model.predict(valid[FEATURE_COLUMNS])
        valid["prediction"] = valid["baseline_price"] + valid["predicted_residual"]
        return valid

    def forecast(self, start: pd.Timestamp, window_hours: int) -> dict:
        working = self.history.tail(168).copy()
        estimates = []
        for offset in range(window_hours):
            timestamp = start + pd.Timedelta(hours=offset)
            candidate = pd.DataFrame({"timestamp": [timestamp], "price_toronto": [np.nan]})
            features = build_feature_frame(pd.concat([working, candidate], ignore_index=True), self.baseline).iloc[[-1]]
            predicted_residual = float(self.model.predict(features[FEATURE_COLUMNS])[0])
            price = float(features["baseline_price"].iloc[0] + predicted_residual)
            estimates.append({"timestamp": timestamp.isoformat(), "price": round(price, 2)})
            working = pd.concat(
                [working, pd.DataFrame({"timestamp": [timestamp], "price_toronto": [price]})],
                ignore_index=True,
            ).tail(168)

        prices = [item["price"] for item in estimates]
        ranked_hours = sorted(estimates, key=lambda item: (item["price"], item["timestamp"]))[:3]
        average = sum(prices) / len(prices)
        recommendation = recommend(average, start, self.baseline)
        return {
            "start_time": start.isoformat(),
            "end_time": estimates[-1]["timestamp"],
            "window_hours": window_hours,
            "estimates": estimates,
            "best_hours": ranked_hours,
            "average_price": round(average, 2),
            "lowest_price": min(prices),
            "highest_price": max(prices),
            "action": recommendation["action"],
            "deviation_pct": recommendation["deviation_pct"],
            "typical_price": recommendation["typical_price"],
            "model": "Huber gradient-boosted residual model",
        }
