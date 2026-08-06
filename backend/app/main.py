# main.py

import pandas as pd
from app.data.fetch import fetch_all_years

def main():
    df = fetch_all_years(2018, 2024)
    print(df.describe())

if __name__ == '__main__':
    main()