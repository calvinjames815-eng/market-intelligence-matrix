import requests
import pandas as pd
import numpy as np
import os

# Files will be generated in the same directory as this script
CACHE_FILE = "market_engine_cache.csv"
MASTER_FILE = "macro_scorecard.csv"
COUNTRIES = ["USA", "JPN", "CHN", "IND", "CHE", "KOR", "NLD", "SAU", "ARE", "SGP", "DEU", "PHL", "MYS", "QAT", "BHR", "CAN", "FRA", "GBR"]

def build_engine():
    print(f"--- GENERATING CACHE FILE: {CACHE_FILE} ---")
    data_list = []
    eodb = {"USA": 0.9, "JPN": 0.85, "CHN": 0.7, "IND": 0.6, "CHE": 0.95, "KOR": 0.8, "NLD": 0.9, 
            "SAU": 0.65, "ARE": 0.85, "SGP": 0.99, "DEU": 0.8, "PHL": 0.5, "MYS": 0.75, 
            "QAT": 0.7, "BHR": 0.7, "CAN": 0.9, "FRA": 0.8, "GBR": 0.9}

    for code in COUNTRIES:
        gdp_s = get_series(code, "NY.GDP.MKTP.KD.ZG")
        inf_s = get_series(code, "FP.CPI.TOTL.ZG")
        
        # 1. Force real-number math for velocity (CAGR)
        # We use np.abs() and np.real() to strip away any 'j' components
        raw_velocity = (gdp_s[-1] / gdp_s[0])**(1/len(gdp_s)) - 1
        velocity = float(np.real(raw_velocity))
        
        # 2. Ensure volatility is also a simple float
        gdp_vol = float(np.real(np.std(gdp_s))) / 100
        inf_avg = float(np.real(np.mean(inf_s))) / 100
        
        # 3. Safe Monte Carlo: Use the real-number velocity and volatility
        sims = np.random.normal(velocity, gdp_vol, 10000)
        risk_roi = np.percentile(sims, 5)
        
        row = {
            "country": code,
            "GDP_Growth": round(velocity, 4),
            "Inflation": round(inf_avg, 4),
            "Infrastructure": eodb.get(code, 0.5),
            "Risk_Adjusted_ROI": round(risk_roi, 4),
            "RISK_ADJ_SCORE": round((velocity * 0.6) - (inf_avg * 0.2) + (eodb.get(code, 0.5) * 0.2), 4)
        }
        
        for year in [2035, 2040, 2045, 2050]:
            # Use abs() to ensure projection math stays in the real domain
            row[f'Proj_{year}'] = round(100 * ((1 + abs(velocity)) ** (year - 2025)), 2)
        
        data_list.append(row)
    
    df = pd.DataFrame(data_list).set_index('country')
    df.to_csv(CACHE_FILE)
    df.to_csv(MASTER_FILE)
    return df

if __name__ == "__main__":
    df = build_engine()
    print(df.to_string())
