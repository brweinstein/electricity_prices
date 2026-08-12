# app/config.py

from pathlib import Path

PRICE_NODAL_BASE_URL = "https://reports-public.ieso.ca/public/PriceNodal/PUB_PriceNodal_{year}.csv"
TORONTO_COLUMN = "Darlington"
DB_PATH = Path(__file__).parent / "data" / "prices.db"