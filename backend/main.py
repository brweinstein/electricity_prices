# main.py

import pandas as pd
from app.data.fetch import fetch_all_years
from app.data.cache import load_prices
from app.models.seasonality import hourly_baseline, dow_hourly_baseline, weekday_vs_weekend_baseline

def main():
    df = load_prices()
    print(df.describe())

    print(hourly_baseline(df))
    print(weekday_vs_weekend_baseline(df))

if __name__ == '__main__':
    main()