"""Compare 2025 nodal Darlington and Ontario zonal prices over an overlap window."""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.fetch import fetch_year, fetch_zonal_range


def compare(start: date, end: date) -> dict[str, float | int | str]:
    nodal = fetch_year(2025)
    nodal = nodal[(nodal["timestamp"].dt.date >= start) & (nodal["timestamp"].dt.date <= end)]
    nodal = nodal.rename(columns={"price_toronto": "nodal_darlington"})
    zonal = fetch_zonal_range(start, end).rename(columns={"price_toronto": "zonal_ontario"})
    nodal["timestamp"] = pd.to_datetime(nodal["timestamp"])
    zonal["timestamp"] = pd.to_datetime(zonal["timestamp"])
    merged = nodal.merge(zonal, on="timestamp", how="inner").dropna()
    if merged.empty:
        return {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "nodal_rows": int(len(nodal)),
            "zonal_rows": int(len(zonal)),
            "overlap_rows": 0,
            "status": "no overlapping observations; sources remain unvalidated",
        }

    difference = merged["nodal_darlington"] - merged["zonal_ontario"]
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "nodal_rows": int(len(nodal)),
        "zonal_rows": int(len(zonal)),
        "overlap_rows": int(len(merged)),
        "correlation": round(float(merged["nodal_darlington"].corr(merged["zonal_ontario"])), 4),
        "mae_stored_units": round(float(difference.abs().mean()), 4),
        "median_difference_stored_units": round(float(difference.median()), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2025, 5, 3))
    parser.add_argument("--end", type=date.fromisoformat, default=date(2025, 5, 31))
    parser.add_argument("--output", type=Path, default=Path("source_comparison_2025.json"))
    args = parser.parse_args()

    metrics = compare(args.start, args.end)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
