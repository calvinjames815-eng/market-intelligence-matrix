import requests
import pandas as pd
import numpy as np
import datetime
import time

# --- CONFIGURATION ---
CACHE_FILE = "market_engine_cache.csv"
COUNTRIES = ["USA", "JPN", "CHN", "IND", "CHE", "KOR", "NLD", "SAU", "ARE", "SGP", "DEU", "PHL", "MYS", "QAT", "BHR", "CAN", "FRA", "GBR"]
EODB_SCORES = {"USA": 0.9, "JPN": 0.85, "CHN": 0.7, "IND": 0.6, "CHE": 0.95, "KOR": 0.8, "NLD": 0.9, 
               "SAU": 0.65, "ARE": 0.85, "SGP": 0.99, "DEU": 0.8, "PHL": 0.5, "MYS": 0.75, 
               "QAT": 0.7, "BHR": 0.7, "CAN": 0.9, "FRA": 0.8, "GBR": 0.9}

def get_wb_data(country, indicator):
    """Fetches World Bank data (Macro) with rate-limiting"""
    time.sleep(1.2)
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&date=2015:2025&per_page=15"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()[1]
        vals = [float(x['value']) for x in data if x['value'] is not None and float(x['value']) != 0]
        return vals if len(vals) > 1 else [0.02, 0.02]
    except:
        return [0.02, 0.02]

def get_ilo_labor(country_code):
    """Fetches Labor Participation rate from ILOSTAT (Open Data)"""
    time.sleep(1.2)
    url = f"https://www.ilo.org/sdmxws/rest/data/ILO,DF_EAP_DWAP_SEX_AGE_RT_A/{country_code}...?format=csv"
    try:
        df = pd.read_csv(url)
        return float(df['OBS_VALUE'].iloc[-1]) / 100
    except:
        return 0.70 # Fallback

def build_engine():
    print("--- GENERATING CENTRALIZED CACHE ---")
    data_list = []
    
    for code in COUNTRIES:
        # 1. Fetching Data
        gdp_s = get_wb_data(code, "NY.GDP.MKTP.KD.ZG")
        inf_s = get_wb_data(code, "FP.CPI.TOTL.ZG")
        labor = get_ilo_labor(code)
        
        # 2. Advanced Mathematical Logic (Your Original Simulation Engine)
        velocity = float(np.real((gdp_s[-1] / gdp_s[0])**(1/len(gdp_s)) - 1))
        velocity = max(min(velocity, 0.07), -0.02)
        
        shock = np.random.normal(0, 0.005) 
        stoch_vel = max(min(velocity + shock, 0.07), -0.02)
        
        inf_avg = float(np.real(np.mean(inf_s))) / 100
        infra = EODB_SCORES.get(code, 0.5)
        
        # Weighted Scoring (Now incorporating Labor as a core metric)
        score = (velocity * 0.4) + (labor * 0.3) + (infra * 0.2) - (inf_avg * 0.1)
        
        row = {
            "country": code,
            "RISK_ADJ_SCORE": round(score, 4),
            "GDP_Growth": round(velocity, 4),
            "Labor_Participation": round(labor, 4),
            "Infrastructure": infra
        }
        
        # Projection Logic
        proj_val, decay = 100.0, 0.95 
        for year in [2035, 2040, 2045, 2050]:
            proj_val *= (((1 + stoch_vel) ** 5) * decay)
            row[f'Proj_{year}'] = round(proj_val, 2)
        
        data_list.append(row)
    
    # 3. Load & Finalize
    df = pd.DataFrame(data_list)
    df['Recommendation'] = pd.qcut(df['RISK_ADJ_SCORE'], q=3, labels=['Avoid', 'Watch', 'Target'])
    df['Last_Updated'] = datetime.datetime.now().strftime("%Y-%m-%d")
    
    df.to_csv(CACHE_FILE, index=False)
    print("Pipeline Complete.")

if __name__ == "__main__":
    build_engine()
