import requests
import pandas as pd
import numpy as np
import os

CACHE_FILE = "market_engine_cache.csv"
COUNTRIES = ["USA", "JPN", "CHN", "IND", "CHE", "KOR", "NLD", "SAU", "ARE", "SGP", "DEU", "PHL", "MYS", "QAT", "BHR", "CAN", "FRA", "GBR"]

def get_data_series(country_code, indicator_id):
    # Fetching from 2010 to latest available
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_id}?format=json&date=2010:2025&per_page=20"
    try:
        data = requests.get(url, timeout=10).json()[1]
        values = [float(x['value']) for x in data if x['value'] is not None and float(x['value']) > 0]
        return values if len(values) > 1 else [1.0, 1.0]
    except:
        return [1.0, 1.0]

def calculate_projections(start_val, velocity, years_out):
    # Projects value based on Annualized Economic Velocity
    return start_val * ((1 + velocity) ** years_out)

def build_engine():
    if os.path.exists(CACHE_FILE):
        return pd.read_csv(CACHE_FILE, index_col='country')

    data_list = []
    eodb = {"USA": 0.9, "JPN": 0.85, "CHN": 0.7, "IND": 0.6, "CHE": 0.95, "KOR": 0.8, "NLD": 0.9, 
            "SAU": 0.65, "ARE": 0.85, "SGP": 0.99, "DEU": 0.8, "PHL": 0.5, "MYS": 0.75, 
            "QAT": 0.7, "BHR": 0.7, "CAN": 0.9, "FRA": 0.8, "GBR": 0.9}

    for code in COUNTRIES:
        gdp_s = get_data_series(code, "NY.GDP.MKTP.KD.ZG")
        # Annualized Economic Velocity calculation
        velocity = (gdp_s[-1] / gdp_s[0])**(1/len(gdp_s)) - 1
        
        # Projecting GDP Growth for future years
        row = {"country": code, "Velocity": velocity, "infrastructure": eodb.get(code, 0.5)}
        for year in [2030, 2035, 2040, 2045, 2050]:
            row[f'Proj_{year}'] = calculate_projections(gdp_s[-1], velocity, (year - 2025))
        
        data_list.append(row)
    
    df = pd.DataFrame(data_list).set_index('country')
    df.to_csv(CACHE_FILE)
    return df

if __name__ == "__main__":
    df = build_engine()
    # Scoring based on Velocity + Infrastructure
    df['RISK_ADJ_SCORE'] = (df['Velocity'] * 0.7) + (df['infrastructure'] * 0.3)
    results = df.sort_values(by='RISK_ADJ_SCORE', ascending=False)
    
    print(results[['Velocity', 'Proj_2050', 'RISK_ADJ_SCORE']])
