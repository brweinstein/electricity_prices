# app/data/fetch.py

import pandas as pd
import time
from app.config import PRICE_NODAL_BASE_URL, TORONTO_COLUMN

def fetch_year(year: int) -> pd.DataFrame:
    """Returns columns: timestamp, price (Toronto zone only)"""
    url = PRICE_NODAL_BASE_URL.format(year=year)
    df = pd.read_csv(url, skiprows=4)
    df["timestamp"] = pd.to_datetime(df["Date"]) + pd.to_timedelta(df["Hour"] - 1, unit="h")
    toronto = df[["timestamp", "Darlington"]].rename(columns={"Darlington": "price_toronto"})
    return toronto

def fetch_all_years(start: int, end: int) -> pd.DataFrame:
    """Concatenates fetch_year across the range"""
    frames = []
    for year in range(start, end + 1):
        try:
            frames.append(fetch_year(year))
        except Exception as e:
            print(f"Skipping {year}: {e}")
        time.sleep(0.5)
    return pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)


