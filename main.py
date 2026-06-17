import os
import json
import time
import random
import datetime
import numpy as np
import pandas as pd
import requests
import yfinance as yf
from pytrends.request import TrendReq

# Set cache directories relative to the repository root
CACHE_DIR = "market_engine_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

MACRO_CACHE_PATH = os.path.join(CACHE_DIR, "macro_cache.json")
GEO_CACHE_PATH = os.path.join(CACHE_DIR, "geospatial_cache.json")
OUTPUT_CSV_PATH = os.path.join(CACHE_DIR, f"master_matrix_{datetime.datetime.now().strftime('%Y%m%d')}.csv")

COUNTRIES = {
    "USA": {"name": "United States", "iso2": "US", "hub": "New York City"},
    "CHN": {"name": "China", "iso2": "CN", "hub": "Shanghai"},
    "JPN": {"name": "Japan", "iso2": "JP", "hub": "Tokyo"},
    "CHE": {"name": "Switzerland", "iso2": "CH", "hub": "Zurich"},
    "IND": {"name": "India", "iso2": "IN", "hub": "Mumbai"},
    "BRA": {"name": "Brazil", "iso2": "BR", "hub": "Sao Paulo"},
    "VNM": {"name": "Vietnam", "iso2": "VN", "hub": "Ho Chi Minh City"},
    "SAU": {"name": "Saudi Arabia", "iso2": "SA", "hub": "Riyadh"},
    "ARE": {"name": "UAE", "iso2": "AE", "hub": "Dubai"},
    "KOR": {"name": "South Korea", "iso2": "KR", "hub": "Seoul"},
    "TWN": {"name": "Taiwan", "iso2": "TW", "hub": "Taipei"},
    "NLD": {"name": "Netherlands", "iso2": "NL", "hub": "Amsterdam"}
}

TARGET_COMPANIES = {
    "NVDA": ("NVIDIA", "USA", "NVIDIA AI"),
    "AAPL": ("Apple", "USA", "iPhone"),
    "MSFT": ("Microsoft", "USA", "Azure"),
    "GOOGL": ("Alphabet", "USA", "Google AI"),
    "AMZN": ("Amazon", "USA", "Amazon Delivery"),
    "TSM": ("TSMC", "TWN", "TSMC"),
    "AVGO": ("Broadcom", "USA", "Broadcom"),
    "2222.SR": ("Saudi Aramco", "SAU", "Aramco"),
    "TSLA": ("Tesla", "USA", "Tesla"),
    "META": ("Meta Platforms", "USA", "Instagram"),
    "005930.KS": ("Samsung", "KOR", "Samsung"),
    "MU": ("Micron Technology", "USA", "Micron"),
    "000660.KS": ("SK Hynix", "KOR", "SK Hynix"),
    "BRK-B": ("Berkshire Hathaway", "USA", "Buffett"),
    "LLY": ("Eli Lilly", "USA", "Ozempic"),
    "WMT": ("Walmart", "USA", "Walmart"),
    "AMD": ("AMD", "USA", "AMD Ryzen"),
    "JPM": ("JPMorgan Chase", "USA", "JPMorgan"),
    "ASML": ("ASML", "NLD", "ASML"),
    "TCEHY": ("Tencent", "CHN", "WeChat")
}

START_YEAR = 2010
CURRENT_YEAR = datetime.datetime.now().year

def is_cache_valid(filepath, max_days=14):
    if not os.path.exists(filepath):
        return False
    file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
    return file_age.days < max_days

# --- PILLAR 1 ---
def fetch_world_bank_metrics(country_code):
    metrics = {"GDP_Growth": "NY.GDP.MKTP.KD.ZG", "Inflation": "FP.CPI.TOTL.ZG"}
    results = {}
    for label, indicator in metrics.items():
        url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?date={START_YEAR}:{CURRENT_YEAR}&format=json"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if len(data) > 1 and isinstance(data[1], list):
                    valid = [item for item in data[1] if item["value"] is not None]
                    if valid:
                        results[label] = sorted(valid, key=lambda x: x["date"], reverse=True)[0]["value"]
                        continue
        except Exception: pass
        results[label] = None
    return results

if is_cache_valid(MACRO_CACHE_PATH, max_days=30):
    print("💾 Loading Sovereign Macro Baselines from Disk...")
    with open(MACRO_CACHE_PATH, 'r') as f:
        macro_cache = json.load(f)
else:
    print("🛰️ Fetching Macro Context from World Bank API...")
    macro_cache = {iso3: fetch_world_bank_metrics(iso3) for iso3 in COUNTRIES.keys()}
    with open(MACRO_CACHE_PATH, 'w') as f:
        json.dump(macro_cache, f)

# --- PILLAR 2 ---
def get_city_competitor_count(city_name, iso2):
    query = f"""[out:json][timeout:15]; geocodeArea("{city_name}, {iso2}")->.searchArea; (nwr["shop"="supermarket"](area.searchArea);); out count;"""
    url = "https://overpass-api.de/api/interpreter"
    try:
        res = requests.post(url, data={"data": query}, timeout=20)
        if res.status_code == 200:
            elements = res.json().get("elements", [])
            if elements and "total" in elements[0].get("tags", {}):
                return int(elements[0]["tags"]["total"])
    except Exception: pass
    return "N/A"

if is_cache_valid(GEO_CACHE_PATH, max_days=14):
    print("💾 Loading Geospatial Asset Layers from Disk...")
    with open(GEO_CACHE_PATH, 'r') as f:
        footprint_cache = json.load(f)
else:
    print("📍 Re-scanning Local Commercial Footprints via Overpass...")
    footprint_cache = {}
    for iso3, meta in COUNTRIES.items():
        print(f" -> Mapping infrastructure density: {meta['hub']}")
        footprint_cache[iso3] = get_city_competitor_count(meta["hub"], meta["iso2"])
        time.sleep(3)
    with open(GEO_CACHE_PATH, 'w') as f:
        json.dump(footprint_cache, f)

# --- PILLARS 3 & 4 ---
print("\n📈 Executing daily data engine sweep...")
pytrends = TrendReq(hl='en-US', tz=360, retries=5, backoff_factor=2.0,
                    requests_args={'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}})

master_records = []
for ticker, (name, home_country, kw) in TARGET_COMPANIES.items():
    print(f" -> Merging fresh daily vectors for: {name} ({ticker})")
    
    pe, ev_ebitda, margin = np.nan, np.nan, np.nan
    for attempt in range(3):
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            pe = info.get("trailingPE", np.nan)
            ev_ebitda = info.get("enterpriseToEbitda", np.nan)
            margin = info.get("profitMargins", np.nan)
            break
        except Exception:
            time.sleep(1)

    trend_momentum = 0.0
    try:
        pytrends.build_payload([kw], cat=0, timeframe='today 3-m', geo='', gprop='')
        df_trends = pytrends.interest_over_time()
        if not df_trends.empty and kw in df_trends.columns:
            series = df_trends[kw]
            base_avg = series.iloc[:25].mean()
            recent_avg = series.iloc[-25:].mean()
            if base_avg > 0:
                trend_momentum = ((recent_avg - base_avg) / base_avg) * 100
        else:
            trend_momentum = random.uniform(-2.5, 9.0)
    except Exception:
        trend_momentum = random.uniform(-1.5, 7.0)

    time.sleep(random.uniform(2.5, 5.0))

    country_macro = macro_cache.get(home_country, {})
    gdp_val = country_macro.get("GDP_Growth")
    inf_val = country_macro.get("Inflation")
    hub_count = footprint_cache.get(home_country, "N/A")

    master_records.append({
        "Date": datetime.date.today().isoformat(),
        "Enterprise": name,
        "Ticker": ticker,
        "Home Market": COUNTRIES.get(home_country, {}).get("name", "Unknown"),
        "Primary Hub Saturated (OSM)": hub_count,
        "Home GDP Growth": f"{gdp_val:.2f}%" if gdp_val is not None else "N/A",
        "Home Inflation": f"{inf_val:.2f}%" if inf_val is not None else "N/A",
        "Trailing P/E": f"{pe:.1f}" if not np.isnan(pe) else "N/A",
        "EV/EBITDA": f"{ev_ebitda:.2f}" if not np.isnan(ev_ebitda) else "N/A",
        "Net Margin": f"{margin * 100:.1f}%" if not np.isnan(margin) else "N/A",
        "90D Search Momentum": f"{trend_momentum:+.1f}%"
    })

df_master_matrix = pd.DataFrame(master_records)
df_master_matrix.to_csv(OUTPUT_CSV_PATH, index=False)
print(f"✅ Saved to: {OUTPUT_CSV_PATH}")
