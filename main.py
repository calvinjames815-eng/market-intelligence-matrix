import requests
import pandas as pd
import numpy as np
import os
import datetime 

CACHE_FILE = "market_engine_cache.csv"
COUNTRIES = ["USA", "JPN", "CHN", "IND", "CHE", "KOR", "NLD", "SAU", "ARE", "SGP", "DEU", "PHL", "MYS", "QAT", "BHR", "CAN", "FRA", "GBR"]

def get_series(country, indicator):
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&date=2010:2025&per_page=20"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()[1]
        vals = [float(x['value']) for x in data if x['value'] is not None and float(x['value']) != 0]
        return vals if len(vals) > 1 else [0.02, 0.02]
    except Exception:
        return [0.02, 0.02]

def build_engine():
    print(f"--- GENERATING CENTRALIZED CACHE: {CACHE_FILE} ---")
    data_list = []
    eodb = {"USA": 0.9, "JPN": 0.85, "CHN": 0.7, "IND": 0.6, "CHE": 0.95, "KOR": 0.8, "NLD": 0.9, 
            "SAU": 0.65, "ARE": 0.85, "SGP": 0.99, "DEU": 0.8, "PHL": 0.5, "MYS": 0.75, 
            "QAT": 0.7, "BHR": 0.7, "CAN": 0.9, "FRA": 0.8, "GBR": 0.9}

    for code in COUNTRIES:
        gdp_s = get_series(code, "NY.GDP.MKTP.KD.ZG")
        inf_s = get_series(code, "FP.CPI.TOTL.ZG")
        
        # Velocity and bounds
        velocity = float(np.real((gdp_s[-1] / gdp_s[0])**(1/len(gdp_s)) - 1))
        velocity = max(min(velocity, 0.07), -0.02)
        inf_avg = float(np.real(np.mean(inf_s))) / 100
        
        # Risk-Adjusted ROI
        risk_roi = velocity - (np.std(inf_s)/100)
        
        row = {
            "country": code,
            "GDP_Growth": round(velocity, 4),
            "Inflation": round(inf_avg, 4),
            "Infrastructure": eodb.get(code, 0.5),
            "Risk_Adjusted_ROI": round(risk_roi, 4),
            "RISK_ADJ_SCORE": round((velocity * 0.6) - (inf_avg * 0.2) + (eodb.get(code, 0.5) * 0.2), 4)
        }
        
        # Maturity Decay projections
        proj_val, decay = 100.0, 0.95 
        for year in [2035, 2040, 2045, 2050]:
            proj_val *= (((1 + velocity) ** 5) * decay)
            row[f'Proj_{year}'] = round(proj_val, 2)
        
        data_list.append(row)
    
    df = pd.DataFrame(data_list).set_index('country')
    
    df['Last_Updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    df.to_csv(CACHE_FILE)
    return df

if __name__ == "__main__":
    df = build_engine()
    print(df.to_string())
