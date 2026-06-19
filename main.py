import requests
import pandas as pd
import numpy as np
import os
import time

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
    """Queries OpenStreetMap with rate limiting and robust error handling."""
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    query = f"""
    [out:json][timeout:25];
    area["ISO3166-1"="{country_code}"]["admin_level"="2"]->.searchArea;
    (
      node["amenity"="bank"](area.searchArea);
      way["aeroway"="aerodrome"](area.searchArea);
    );
    out count;
    """
    
    # Rate limit: Wait 2 seconds to avoid being blacklisted by Overpass
    time.sleep(2) 
    
    try:
        response = requests.post(overpass_url, data=query, timeout=30)
        if response.status_code != 200:
            print(f"DEBUG: OSM API returned {response.status_code} for {country_code}")
            return 0.1
            
        data = response.json()
        elements = data.get('elements', [])
        # 'out count' returns an element where the total is in the 'tags' field
        count = int(elements[0].get('tags', {}).get('total', 0)) if elements else 0
        
        print(f"DEBUG: OSM {country_code} success, count={count}")
        return min(float(count) / 500, 1.0) 
    except Exception as e:
        print(f"DEBUG: OSM Connection issue for {country_code}: {e}")
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
    # Check if cache exists and is < 24 hours old (86400 seconds)
    if os.path.exists(CACHE_FILE):
        file_time = os.path.getmtime(CACHE_FILE)
        if (time.time() - file_time) < 86400:
            print(f"--- LOADING FROM CACHE: {CACHE_FILE} ---")
            return pd.read_csv(CACHE_FILE, index_col='country')
        else:
            print("--- CACHE EXPIRED. REFRESHING ---")
    
    data = get_real_macro_data()
    data.to_csv(CACHE_FILE)
    return data

def get_risk_adjusted_score(row, simulations=1000):
    """Monte Carlo engine for risk-adjusted performance."""
    gdp_std = abs(row['gdp_growth'] * 0.1)
    infl_std = abs(row['inflation'] * 0.1)
    sim_gdp = np.random.normal(row['gdp_growth'], gdp_std, simulations)
    sim_infl = np.random.normal(row['inflation'], infl_std, simulations)
    scores = (0.5 * sim_gdp) - (0.3 * sim_infl) + (0.2 * row['infrastructure'])
    return scores.mean()

if __name__ == "__main__":
    data = get_data_with_cache()
    
    # Apply Monte Carlo Engine
    data['RISK_ADJ_SCORE'] = data.apply(get_risk_adjusted_score, axis=1)
    
    # Sort and Print Results
    results = data.sort_values(by='RISK_ADJ_SCORE', ascending=False)
    
    print(f"\n{'='*60}\nMONTE CARLO RISK-ADJUSTED RANKING\n{'='*60}")
    print(results[['gdp_growth', 'inflation', 'infrastructure', 'RISK_ADJ_SCORE']])
    
    results.to_csv(MASTER_FILE)
