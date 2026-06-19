import wbdata
import pandas as pd
import numpy as np
import os

# Configuration
MASTER_FILE = "macro_scorecard.csv"
COUNTRIES = ["USA", "JPN", "CHN", "IND", "CHE", "KOR", "NLD", "TWN", "SAU", "ARE", "SGP", "DEU"]

# World Bank Indicator IDs
INDICATORS = {
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "inflation": "FP.CPI.TOTL.ZG"
}

def get_real_macro_data():
    """Fetches data one by one to ensure pipeline stability."""
    target_codes = ["USA", "JPN", "CHN", "IND", "CHE", "KOR", "NLD", "TWN", "SAU", "ARE", "SGP", "DEU"]
    all_data = []

    for code in target_codes:
        try:
            # Fetch one country at a time
            df = wbdata.get_dataframe(INDICATORS, country=code)
            # Take only the most recent year
            latest = df.tail(1)
            latest['country'] = code
            all_data.append(latest)
        except Exception as e:
            print(f"Skipping {code} due to API error: {e}")
    
    # Concatenate all successfully fetched data
    full_df = pd.concat(all_data)
    
    # Data Cleaning
    full_df['gdp_growth'] = full_df['gdp_growth'].fillna(0) / 100
    full_df['inflation'] = full_df['inflation'].fillna(0) / 100
    full_df['infrastructure'] = 0.5 
    
    return full_df

def calculate_attractiveness(row, weights=(0.5, 0.3, 0.2)):
    w_gdp, w_infl, w_infra = weights
    return (w_gdp * row['gdp_growth']) - (w_infl * row['inflation']) + (w_infra * row['infrastructure'])

if __name__ == "__main__":
    # 1. Fetch
    data = get_real_macro_data()
    
    # 2. Score
    data['SCORE'] = data.apply(calculate_attractiveness, axis=1)
    
    # 3. Sort and Display
    results = data.sort_values(by='SCORE', ascending=False)
    print(f"{'='*40}\nCOUNTRY ATTRACTIVENESS RANKING\n{'='*40}")
    print(results[['SCORE']])
    
    # 4. Save
    results.to_csv(MASTER_FILE)
