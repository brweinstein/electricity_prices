# app/data/cache.py
import sqlite3
import pandas as pd
from app.config import DB_PATH

def load_prices(start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """Load cached historical prices, optionally filtered by date range"""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM prices"
    params = []
    filters = []
    if start:
        filters.append("timestamp >= ?")
        params.append(start)
    if end:
        filters.append("timestamp <= ?")
        params.append(end)
    if filters:
        query += " WHERE " + " AND ".join(filters)
    df = pd.read_sql(query, conn, params=params, parse_dates=["timestamp"])
    conn.close()
    return df.sort_values("timestamp").reset_index(drop=True)