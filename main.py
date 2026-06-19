import requests
import pandas as pd
import numpy as np

# Configuration
MASTER_FILE = "macro_scorecard.csv"
# Using a list of codes that the World Bank API strictly recognizes
COUNTRIES = ["USA", "JPN", "CHN", "IND", "CHE", "KOR", "NLD", "TWN", "SAU", "ARE", "SGP", "DEU"]

def fetch_indicator(country_code, indicator_id):
    """Fetches indicator data by forcing a date range search."""
    # Added &date=2020:2026 to find recent valid data
    # Added per_page=10 to ensure we get a few years if the latest is empty
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_id}?format=json&date=2020:2026&per_page=10"
    
    try:
        response = requests.get(url, timeout=15).json()
        
        # Parse through the response to find the first non-null value
        if len(response) > 1 and response[1]:
            for entry in response[1]:
                if entry['value'] is not None:
                    return float(entry['value'])
        
        print(f"DEBUG: No data found for {country_code} on {indicator_id}")
        return 0.0
    except Exception as e:
        print(f"DEBUG: Error fetching {country_code}: {e}")
        return 0.0

def get_real_macro_data():
    data_list = []
    for code in COUNTRIES:
        gdp = fetch_indicator(code, "NY.GDP.MKTP.KD.ZG")
        inf = fetch_indicator(code, "FP.CPI.TOTL.ZG")
        
        data_list.append({
            "country": code,
            "gdp_growth": gdp / 100,
            "inflation": inf / 100,
            "infrastructure": 0.5 
        })
    return pd.DataFrame(data_list).set_index('country')

def calculate_attractiveness(row, weights=(0.5, 0.3, 0.2)):
    return (weights[0] * row['gdp_growth']) - (weights[1] * row['inflation']) + (weights[2] * row['infrastructure'])

if __name__ == "__main__":
    data = get_real_macro_data()
    
    print("--- DATA LOADED ---")
    print(data)
    
    data['SCORE'] = data.apply(calculate_attractiveness, axis=1)
    results = data.sort_values(by='SCORE', ascending=False)
    
    print(f"\n{'='*40}\nFINAL MARKET ATTRACTIVENESS RANKING\n{'='*40}")
    print(results[['SCORE']])
    results.to_csv(MASTER_FILE)
