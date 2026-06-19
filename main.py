import requests
import pandas as pd
import numpy as np

# Configuration
MASTER_FILE = "macro_scorecard.csv"
COUNTRIES = ["USA", "JPN", "CHN", "IND", "CHE", "KOR", "NLD", "TWN", "SAU", "ARE", "SGP", "DEU"]

def fetch_indicator(country_code, indicator_id):
    """Direct API call to World Bank to avoid library-specific errors."""
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_id}?format=json&per_page=1"
    response = requests.get(url).json()
    
    # World Bank API returns a list where [0] is metadata, [1] is the data
    if len(response) > 1 and response[1]:
        value = response[1][0]['value']
        return float(value) if value is not None else 0.0
    return 0.0

def get_real_macro_data():
    """Builds the dataframe by calling the API directly for each country."""
    data_list = []
    
    for code in COUNTRIES:
        gdp = fetch_indicator(code, "NY.GDP.MKTP.KD.ZG")
        inf = fetch_indicator(code, "FP.CPI.TOTL.ZG")
        
        data_list.append({
            "country": code,
            "gdp_growth": gdp / 100,
            "inflation": inf / 100,
            "infrastructure": 0.5 # Placeholder for OSM logic
        })
    
    return pd.DataFrame(data_list).set_index('country')

def calculate_attractiveness(row, weights=(0.5, 0.3, 0.2)):
    return (weights[0] * row['gdp_growth']) - (weights[1] * row['inflation']) + (weights[2] * row['infrastructure'])

if __name__ == "__main__":
    data = get_real_macro_data()
    data['SCORE'] = data.apply(calculate_attractiveness, axis=1)
    results = data.sort_values(by='SCORE', ascending=False)
    
    print(f"{'='*40}\nCOUNTRY ATTRACTIVENESS RANKING\n{'='*40}")
    print(results[['SCORE']])
    results.to_csv(MASTER_FILE)
