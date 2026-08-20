# backned/scripts/backfill_historical_data.py

import sqlite3
from datetime import date
from app.config import DB_PATH
from app.data.fetch import fetch_all_years, fetch_zonal_range

def backfill(start: int, end: int):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = fetch_all_years(start, end)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("prices", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON prices(timestamp)")
    conn.commit()
    conn.close()
    print(f"Backfilled {len(df)} rows into {DB_PATH}")

def backfill_recent(start: date, end: date):
    """Fills the post-regime gap. Run this AFTER backfill(), since it appends."""
    df = fetch_zonal_range(start, end)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("prices", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
    print(f"Appended {len(df)} recent rows into {DB_PATH}")

if __name__ == "__main__":
    backfill(2018, 2024)
    backfill_recent(date(2025, 5, 3), date.today())