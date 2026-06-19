import requests
import pandas as pd
import numpy as np

MASTER_FILE = "macro_scorecard.csv"
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
    # ISO3166-1 is the standard for country codes in OSM
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
        # Extract the count from the OSM response structure
        count = response.get('elements', [{}])[0].get('tags', {}).get('total', 0)
        return min(float(count) / 500, 1.0) 
    except Exception:
        return 0.1 # Fallback to low-neutral if API is unreachable

def get_real_macro_data():
    data_list = []
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

def calculate_attractiveness(row, weights=(0.5, 0.3, 0.2)):
    return (weights[0] * row['gdp_growth']) - (weights[1] * row['inflation']) + (weights[2] * row['infrastructure'])

if __name__ == "__main__":
    data = get_real_macro_data()
    print("--- DATA LOADED (INCLUDING OSM INFRASTRUCTURE) ---")
    print(data)
    
    data['SCORE'] = data.apply(calculate_attractiveness, axis=1)
    results = data.sort_values(by='SCORE', ascending=False)
    
    print(f"\n{'='*40}\nFINAL MARKET ATTRACTIVENESS RANKING\n{'='*40}")
    print(results[['SCORE']])
    results.to_csv(MASTER_FILE)
