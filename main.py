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
    """Fetches real data from World Bank."""
    # Fetch data
    df = wbdata.get_dataframe(INDICATORS, country=COUNTRIES, convert_date=True)
    # Get the most recent non-null year for each country
    df = df.groupby('country').last()
    
    # Normalize/Clean data (Fill NaN with neutral values to prevent crashes)
    df['gdp_growth'] = df['gdp_growth'].fillna(0) / 100 # Convert % to decimal
    df['inflation'] = df['inflation'].fillna(0) / 100
    
    # Placeholder for infrastructure density (OSM API would go here)
    df['infrastructure'] = 0.5 
    return df

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
