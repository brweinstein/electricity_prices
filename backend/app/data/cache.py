# app/data/cache.py
import sqlite3
import pandas as pd
from app.config import DB_PATH

def load_prices(start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """Load cached historical prices, optionally filtered by date range"""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM prices"
    params = []
    if start and end:
        query += " WHERE timestamp BETWEEN ? AND ?"
        params = [start, end]
    df = pd.read_sql(query, conn, params=params, parse_dates=["timestamp"])
    conn.close()
    return df.sort_values("timestamp").reset_index(drop=True)