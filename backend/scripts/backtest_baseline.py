"""Walk-forward evaluation for the weekday/weekend/hour median baseline."""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import DB_PATH
from app.data.cache import load_prices
from app.models.forecast import _get_typical
from app.models.seasonality import weekday_vs_weekend_baseline


def evaluate(train_end: str, test_start: str, test_end: str) -> dict[str, float | int | str]:
    data = load_prices()
    train = data[data["timestamp"] < pd.Timestamp(train_end)]
    test = data[
        (data["timestamp"] >= pd.Timestamp(test_start))
        & (data["timestamp"] < pd.Timestamp(test_end))
    ]
    if train.empty or test.empty:
        raise RuntimeError("Training or test period has no observations")

    baseline = weekday_vs_weekend_baseline(train)
    predictions = test.apply(
        lambda row: _get_typical(
            baseline,
            row["timestamp"].hour,
            row["timestamp"].dayofweek >= 5,
        ),
        axis=1,
    )
    actual = test["price_toronto"].astype(float)
    errors = predictions - actual
    absolute_errors = errors.abs()
    non_zero_actual = actual != 0
    positive_actual = actual > 0
    smape_denominator = (actual.abs() + predictions.abs()).replace(0, pd.NA)

    return {
        "train_end_exclusive": train_end,
        "test_start_inclusive": test_start,
        "test_end_exclusive": test_end,
        "training_rows": int(len(train)),
        "test_rows": int(len(test)),
        "mae_stored_units": round(float(absolute_errors.mean()), 4),
        "median_absolute_error_stored_units": round(float(absolute_errors.median()), 4),
        "smape_percent": round(float((2 * absolute_errors / smape_denominator).dropna().mean() * 100), 2),
        "mape_positive_actuals_percent": round(
            float((absolute_errors[positive_actual] / actual[positive_actual]).mean() * 100), 2
        ),
        "mape_observations_excluded_zero_actual": int((~non_zero_actual).sum()),
        "mape_observations_excluded_non_positive_actual": int((~positive_actual).sum()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-end", default="2024-01-01")
    parser.add_argument("--test-start", default="2024-01-01")
    parser.add_argument("--test-end", default="2025-01-01")
    parser.add_argument("--output", type=Path, default=Path("backtest_metrics.json"))
    args = parser.parse_args()

    metrics = evaluate(args.train_end, args.test_start, args.test_end)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
