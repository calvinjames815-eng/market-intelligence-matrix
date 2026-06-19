import requests
import pandas as pd
import numpy as np

# Configuration
MASTER_FILE = "macro_scorecard.csv"
COUNTRIES = ["USA", "JPN", "CHN", "IND", "CHE", "KOR", "NLD", "TWN", "SAU", "ARE", "SGP", "DEU"]

def fetch_indicator(country_code, indicator_id):
    """Fetches indicator data and prints debug info if data is missing."""
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_id}?format=json&per_page=1"
    try:
        response = requests.get(url, timeout=10).json()
        if len(response) > 1 and response[1] and response[1][0]['value'] is not None:
            return float(response[1][0]['value'])
        else:
            print(f"DEBUG: No data for {country_code} on {indicator_id}")
            return 0.0
    except Exception as e:
        print(f"DEBUG: Error fetching {country_code}: {e}")
        return 0.0

def get_real_macro_data():
    data_list = []
    for code in COUNTRIES:
        # NY.GDP.MKTP.KD.ZG = GDP Growth
        # FP.CPI.TOTL.ZG = Inflation
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
    # Scoring: (GDP * 0.5) - (Inflation * 0.3) + (Infrastructure * 0.2)
    return (weights[0] * row['gdp_growth']) - (weights[1] * row['inflation']) + (weights[2] * row['infrastructure'])

if __name__ == "__main__":
    data = get_real_macro_data()
    
    # Validation: Print the data structure to ensure it's not all zeros
    print("--- DATA LOADED ---")
    print(data)
    
    data['SCORE'] = data.apply(calculate_attractiveness, axis=1)
    results = data.sort_values(by='SCORE', ascending=False)
    
    print(f"\n{'='*40}\nFINAL MARKET ATTRACTIVENESS RANKING\n{'='*40}")
    print(results[['SCORE']])
    results.to_csv(MASTER_FILE)
