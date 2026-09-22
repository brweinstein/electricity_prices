"""Compare the seasonal baseline with the residual GBM on the same holdout."""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.cache import load_prices
from app.models.forecast import _get_typical
from app.models.gbm_forecast import ResidualGBMForecaster
from app.models.seasonality import monthly_weekday_vs_weekend_baseline


def metrics(actual: pd.Series, predictions: pd.Series) -> dict[str, float | int]:
    errors = predictions - actual
    absolute_errors = errors.abs()
    positive_actual = actual > 0
    denominator = (actual.abs() + predictions.abs()).replace(0, pd.NA)
    return {
        "mae_stored_units": round(float(absolute_errors.mean()), 4),
        "median_absolute_error_stored_units": round(float(absolute_errors.median()), 4),
        "smape_percent": round(float((2 * absolute_errors / denominator).dropna().mean() * 100), 2),
        "mape_positive_actuals_percent": round(
            float((absolute_errors[positive_actual] / actual[positive_actual]).mean() * 100), 2
        ),
        "mape_observations_excluded_non_positive_actual": int((~positive_actual).sum()),
    }


def evaluate(train_end: str, test_start: str, test_end: str) -> dict:
    data = load_prices()
    train = data[data["timestamp"] < pd.Timestamp(train_end)].copy()
    test = data[
        (data["timestamp"] >= pd.Timestamp(test_start))
        & (data["timestamp"] < pd.Timestamp(test_end))
    ].copy()
    if train.empty or test.empty:
        raise RuntimeError("Training or test period has no observations")

    baseline = monthly_weekday_vs_weekend_baseline(train)
    test["baseline_prediction"] = [
        _get_typical(baseline, timestamp.hour, timestamp.dayofweek >= 5, timestamp.month)
        for timestamp in test["timestamp"]
    ]
    forecaster = ResidualGBMForecaster.train(train)
    combined = pd.concat([train, test], ignore_index=True)
    predictions = forecaster.predict_rows(combined)
    test_predictions = predictions[predictions["timestamp"] >= pd.Timestamp(test_start)].copy()
    test = test.merge(test_predictions[["timestamp", "prediction"]], on="timestamp", how="inner")

    actual = test["price_toronto"].astype(float)
    baseline_metrics = metrics(actual, test["baseline_prediction"])
    model_metrics = metrics(actual, test["prediction"])
    return {
        "train_end_exclusive": train_end,
        "test_start_inclusive": test_start,
        "test_end_exclusive": test_end,
        "evaluation_mode": "one-step walk-forward using realized prior prices",
        "production_forecast_mode": "recursive multi-step predictions",
        "training_rows": int(len(train)),
        "test_rows": int(len(test)),
        "baseline": baseline_metrics,
        "residual_gbm": model_metrics,
        "mae_improvement_percent": round(
            (1 - model_metrics["mae_stored_units"] / baseline_metrics["mae_stored_units"]) * 100,
            2,
        ),
        "feature_importance": {
            name: int(value)
            for name, value in sorted(
                zip(forecaster.model.feature_name_, forecaster.model.feature_importances_),
                key=lambda item: item[1],
                reverse=True,
            )
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-end", default="2024-01-01")
    parser.add_argument("--test-start", default="2024-01-01")
    parser.add_argument("--test-end", default="2025-01-01")
    parser.add_argument("--output", type=Path, default=Path("model_comparison_metrics.json"))
    args = parser.parse_args()

    result = evaluate(args.train_end, args.test_start, args.test_end)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
