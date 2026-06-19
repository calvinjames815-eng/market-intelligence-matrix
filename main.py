import os
import datetime
import pandas as pd
import numpy as np
import yfinance as yf
from pandas_datareader import wb # New dependency

# CONFIGURATION
CACHE_DIR = "market_engine_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
MASTER_FILE = os.path.join(CACHE_DIR, "telemetry.csv")

def get_worldbank_data(country_iso):
    """Fetches GDP and Inflation from World Bank."""
    try:
        # GDP Growth: NY.GDP.MKTP.KD.ZG, Inflation: FP.CPI.TOTL.ZG
        data = wb.download(indicator=['NY.GDP.MKTP.KD.ZG', 'FP.CPI.TOTL.ZG'], 
                           country=[country_iso], start=2020, end=2025)
        gdp = data['NY.GDP.MKTP.KD.ZG'].mean()
        inf = data['FP.CPI.TOTL.ZG'].mean()
        return gdp, inf
    except:
        return 0.0, 0.0

def run_engine():
    # Mapping ISO codes for World Bank
    country_map = {"USA": "US", "CHN": "CN", "TWN": "TW", "SAU": "SA", "KOR": "KR", "NLD": "NL"}
    
    # ... [Keep your existing TARGET_COMPANIES and Risk Floor logic here] ...
    
    # NEW: Fetch Macro Health
    macro_records = []
    for iso, wb_code in country_map.items():
        gdp, inf = get_worldbank_data(wb_code)
        # Determine viability/risk rating
        rating = "STABLE" if gdp > 2.0 else "MODERATE"
        macro_records.append({"COUNTRY": iso, "GDP_GROWTH": gdp, "INFLATION": inf, "RATING": rating})

    # Integrate into report printing
    print(f"\n{'='*60}\nREGIONAL MACRO-ENVIRONMENT (LIVE DATA)\n{'='*60}")
    print(f"{'COUNTRY':<8} {'GDP_GROWTH':<12} {'INFLATION':<10} {'RATING'}")
    for m in macro_records:
        print(f"{m['COUNTRY']:<8} {m['GDP_GROWTH']:<12.2f} {m['INFLATION']:<10.2f} {m['RATING']}")
    
    # ... [Proceed with existing Performance Matrix printing] ...
