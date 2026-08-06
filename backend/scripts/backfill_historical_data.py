import sqlite3
from app.data.fetch import fetch_all_years
from app.config import DB_PATH

def backfill(start: int, end: int):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = fetch_all_years(start, end)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("prices", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON prices(timestamp)")
    conn.commit()
    conn.close()
    print(f"Backfilled {len(df)} rows into {DB_PATH}")

if __name__ == '__main__':
    backfill(2018, 2024)