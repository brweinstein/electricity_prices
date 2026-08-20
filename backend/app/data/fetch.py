# app/data/fetch.py

import pandas as pd
import requests
import xml.etree.ElementTree as ET
import time
from datetime import date, timedelta
from app.config import PRICE_NODAL_BASE_URL, TORONTO_COLUMN, DA_ZONAL_BASE_URL

NS = {"ieso": "http://www.ieso.ca/schema"}

def fetch_year(year: int) -> pd.DataFrame:
    """Returns columns: timestamp, price_toronto"""
    url = PRICE_NODAL_BASE_URL.format(year=year)
    df = pd.read_csv(url, skiprows=4)
    df["timestamp"] = pd.to_datetime(df["Date"]) + pd.to_timedelta(df["Hour"] - 1, unit="h")
    toronto = df[["timestamp", TORONTO_COLUMN]].rename(columns={TORONTO_COLUMN: "price_toronto"})
    return toronto


def fetch_all_years(start: int, end: int) -> pd.DataFrame:
    """Concatenates fetch_year across the range [start, end], inclusive"""
    frames = []
    failed = []
    for year in range(start, end + 1):
        try:
            frames.append(fetch_year(year))
        except Exception:
            failed.append(year)
        time.sleep(0.5)
    if failed:
        print(f"Failed to fetch {len(failed)} year(s): {failed}")
    if not frames:
        return pd.DataFrame(columns=["timestamp", "price_toronto"])
    return pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)


def fetch_zonal_day(day: date) -> pd.DataFrame:
    """Fetch one day's post-May-2025 Ontario zonal price (used Toronto)"""
    url = DA_ZONAL_BASE_URL.format(date=day.strftime("%Y%m%d"))
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    rows = []
    for component in root.iter(f"{{{NS['ieso']}}}HourlyPriceComponents"):
        hour_el = component.find("ieso:PricingHour", NS)
        price_el = component.find("ieso:ZonalPrice", NS)

        hour_text = hour_el.text if hour_el is not None else None
        price_text = price_el.text if price_el is not None else None

        if hour_text is None or price_text is None:
            continue  # skip malformed hour rather than crashing the whole day

        hour = int(hour_text)
        price = float(price_text)
        timestamp = pd.Timestamp(day) + pd.Timedelta(hours=hour - 1)
        rows.append({"timestamp": timestamp, "price_toronto": price})

    return pd.DataFrame(rows)


def fetch_zonal_range(start: date, end: date) -> pd.DataFrame:
    """Concatenate fetch_zonal_day across [start, end], inclusive."""
    frames = []
    failed = []
    current = start
    while current <= end:
        try:
            frames.append(fetch_zonal_day(current))
        except Exception:
            failed.append(current)
        time.sleep(0.3)
        current += timedelta(days=1)
    if failed:
        print(f"Failed to fetch {len(failed)} day(s): {failed[:5]}{'...' if len(failed) > 5 else ''}")
    if not frames:
        return pd.DataFrame(columns=["timestamp", "price_toronto"])
    return pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)
