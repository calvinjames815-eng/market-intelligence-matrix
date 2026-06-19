import requests
import pandas as pd
import numpy as np
import os

MASTER_FILE = "macro_scorecard.csv"
CACHE_FILE = "market_engine_cache.csv"
COUNTRIES = ["USA", "JPN", "CHN", "IND", "CHE", "KOR", "NLD", "SAU", "ARE", "SGP", "DEU", "PHL", "MYS", "QAT", "BHR", "CAN", "FRA", "GBR"]

def fetch_indicator(country_code, indicator_id):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_id}?format=json&date=2020:2026&per_page=10"
    try:
        response = requests.get(url, timeout=15).json()
        if len(response) > 1 and response[1]:
            for entry in response[1]:
                if entry['value'] is not None:
                    return float(entry['value'])
        return 0.0
    except Exception:
        return 0.0

def get_infrastructure_score(country_code):
    """Queries OpenStreetMap (Overpass API) for economic infrastructure nodes."""
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:25];
    area["ISO3166-1"="{country_code}"][admin_level=2]->.searchArea;
    (
      node["amenity"="bank"](area.searchArea);
      way["aeroway"="aerodrome"](area.searchArea);
    );
    out count;
    """
    try:
        response = requests.post(overpass_url, data=query, timeout=25).json()
        # The structure of the count response is {'elements': [{'tags': {'total': 'X'}}]}
        count = int(response.get('elements', [{}])[0].get('tags', {}).get('total', 0))
        return min(float(count) / 500, 1.0) 
    except Exception:
        return 0.1

def get_real_macro_data():
    data_list = []
    print(f"--- FETCHING FRESH DATA FOR {len(COUNTRIES)} COUNTRIES ---")
    for code in COUNTRIES:
        gdp = fetch_indicator(code, "NY.GDP.MKTP.KD.ZG")
        inf = fetch_indicator(code, "FP.CPI.TOTL.ZG")
        infra = get_infrastructure_score(code)
        
        data_list.append({
            "country": code,
            "gdp_growth": gdp / 100,
            "inflation": inf / 100,
            "infrastructure": infra
        })
    return pd.DataFrame(data_list).set_index('country')

def get_data_with_cache():
    if os.path.exists(CACHE_FILE):
        print(f"--- LOADING FROM CACHE: {CACHE_FILE} ---")
        return pd.read_csv(CACHE_FILE, index_col='country')
    
    data = get_real_macro_data()
    data.to_csv(CACHE_FILE)
    return data

def calculate_attractiveness(row, weights=(0.5, 0.3, 0.2)):
    return (weights[0] * row['gdp_growth']) - (weights[1] * row['inflation']) + (weights[2] * row['infrastructure'])

if __name__ == "__main__":
    # Logic: Load from cache if possible, else fetch and save
    data = get_data_with_cache()
    
    data['SCORE'] = data.apply(calculate_attractiveness, axis=1)
    results = data.sort_values(by='SCORE', ascending=False)
    
    print(f"\n{'='*40}\nFINAL MARKET ATTRACTIVENESS RANKING\n{'='*40}")
    print(results[['SCORE']])
    results.to_csv(MASTER_FILE)
