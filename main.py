import requests
import pandas as pd
import numpy as np
import os

MASTER_FILE = "macro_scorecard.csv"
CACHE_FILE = "market_engine_cache.csv"
COUNTRIES = ["USA", "JPN", "CHN", "IND", "CHE", "KOR", "NLD", "SAU", "ARE", "SGP", "DEU", "PHL", "MYS", "QAT", "BHR", "CAN", "FRA", "GBR"]

def get_5year_series(country_code, indicator_id):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_id}?format=json&date=2021:2025&per_page=10"
    try:
        data = requests.get(url, timeout=10).json()[1]
        values = [float(x['value']) for x in data if x['value'] is not None]
        return values if len(values) > 0 else [0.0]
    except:
        return [0.0]

def get_market_data():
    """Fetches real historical data and saves to cache."""
    print("--- FETCHING REAL-TIME HISTORICAL DATA ---")
    data_list = []
    # Ease of Doing Business Proxy (Static for consistency)
    eodb = {"USA": 0.9, "JPN": 0.85, "CHN": 0.7, "IND": 0.6, "CHE": 0.95, "KOR": 0.8, "NLD": 0.9, 
            "SAU": 0.65, "ARE": 0.85, "SGP": 0.99, "DEU": 0.8, "PHL": 0.5, "MYS": 0.75, 
            "QAT": 0.7, "BHR": 0.7, "CAN": 0.9, "FRA": 0.8, "GBR": 0.9}

    for code in COUNTRIES:
        gdp_s = get_5year_series(code, "NY.GDP.MKTP.KD.ZG")
        inf_s = get_5year_series(code, "FP.CPI.TOTL.ZG")
        
        cagr = (gdp_s[-1] / gdp_s[0])**0.25 - 1 if gdp_s[0] != 0 else 0
        data_list.append({
            "country": code,
            "cagr": cagr,
            "gdp_vol": np.std(gdp_s) / 100,
            "inf_avg": np.mean(inf_s) / 100,
            "inf_vol": np.std(inf_s) / 100,
            "infrastructure": eodb.get(code, 0.5)
        })
    return pd.DataFrame(data_list).set_index('country')

def run_monte_carlo(df, iterations=10000):
    """Runs 10,000 simulations based on historical volatility."""
    results = []
    for country, row in df.iterrows():
        sim_gdp = np.random.normal(row['cagr'], row['gdp_vol'], iterations)
        sim_inf = np.random.normal(row['inf_avg'], row['inf_vol'], iterations)
        
        # Scoring: 60% Growth, -40% Inflation, +20% Infra Proxy
        scores = (0.6 * sim_gdp) - (0.4 * sim_inf) + (0.2 * row['infrastructure'])
        results.append(scores.mean())
    return results

if __name__ == "__main__":
    if not os.path.exists(CACHE_FILE):
        df = get_market_data()
        df.to_csv(CACHE_FILE)
    else:
        df = pd.read_csv(CACHE_FILE, index_col='country')
        
    df['RISK_ADJ_SCORE'] = run_monte_carlo(df)
    df = df.sort_values(by='RISK_ADJ_SCORE', ascending=False)
    
    print(df[['cagr', 'infrastructure', 'RISK_ADJ_SCORE']])
    df.to_csv(MASTER_FILE)
