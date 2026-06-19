import sys
import os
import datetime
import pandas as pd
import numpy as np
import yfinance as yf
import requests

# Set absolute path for CI/CD consistency
PROJECT_ROOT = os.getcwd()
CACHE_DIR = os.path.join(PROJECT_ROOT, "market_engine_cache")
os.makedirs(CACHE_DIR, exist_ok=True)
MASTER_FILE = os.path.join(CACHE_DIR, "telemetry.csv")

COUNTRY_ISO_MAP = {
    "USA": "US", "CHN": "CN", "TWN": "TW", 
    "SAU": "SA", "KOR": "KR", "NLD": "NL"
}

TARGET_COMPANIES = {
    "NVDA": ("NVIDIA", "USA", 32.4, 0.55), "AAPL": ("Apple", "USA", 28.1, 0.26),
    "MSFT": ("Microsoft", "USA", 31.5, 0.35), "GOOGL": ("Alphabet", "USA", 24.2, 0.27),
    "AMZN": ("Amazon", "USA", 38.0, 0.10), "TSM": ("TSMC", "TWN", 22.1, 0.38),
    "AVGO": ("Broadcom", "USA", 26.4, 0.22), "2222.SR": ("Saudi Aramco", "SAU", 16.5, 0.42),
    "TSLA": ("Tesla", "USA", 45.2, 0.12), "META": ("Meta Platforms", "USA", 23.9, 0.32),
    "005930.KS": ("Samsung", "KOR", 14.1, 0.08), "MU": ("Micron", "USA", 20.2, 0.14),
    "000660.KS": ("SK Hynix", "KOR", 15.4, 0.11), "BRK-B": ("Berkshire", "USA", 19.8, 0.15),
    "LLY": ("Eli Lilly", "USA", 55.4, 0.21), "WMT": ("Walmart", "USA", 25.1, 0.03),
    "AMD": ("AMD", "USA", 34.1, 0.11), "JPM": ("JPMorgan", "USA", 12.2, 0.33),
    "ASML": ("ASML", "NLD", 36.5, 0.28), "TCEHY": ("Tencent", "CHN", 18.2, 0.29)
}

def get_market_health(country_iso):
    """Fetches macro data directly from World Bank API using requests."""
    try:
        url = f"https://api.worldbank.org/v2/country/{country_iso}/indicator/NY.GDP.MKTP.KD.ZG?format=json&date=2020:2025"
        response = requests.get(url, timeout=10)
        data = response.json()[1]
        values = [item['value'] for item in data if item['value'] is not None]
        avg_growth = sum(values) / len(values) if values else 0
        
        rating = "LOW" if avg_growth > 2.0 else "MODERATE"
        viability = "STABLE" if avg_growth > 2.0 else "WATCH"
        return avg_growth, rating, viability
    except Exception:
        return 0.0, "N/A", "N/A"

def run_engine():
    tickers = sorted(list(TARGET_COMPANIES.keys()))
    df = yf.download(tickers, period="1y", progress=False, auto_adjust=True)['Close']
    
    returns = df.pct_change(fill_method=None).dropna()
    cov_matrix = returns.cov().fillna(0) + np.eye(len(tickers)) * 1e-6
    sims = np.random.multivariate_normal(returns.mean().values, cov_matrix, (10000, 5))
    var_95 = np.percentile(sims.sum(axis=2).mean(axis=1), 5)

    ent_data = []
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for t in tickers:
        name, code, pe, margin = TARGET_COMPANIES[t]
        series = df[t].dropna()
        mom = ((series.iloc[-1] - series.iloc[-90]) / series.iloc[-90]) * 100
        status = "REVIEW" if (mom/100) < var_95 else "STABLE"
        ent_data.append({
            "TIMESTAMP": timestamp, "COUNTRY": code, "ENTERPRISE": name,
            "MOMENTUM": f"{mom:+.2f}%", "STATUS": status, "P/E": f"{pe:.1f}x", 
            "MARGIN": f"{margin*100:.0f}%"
        })

    # Save to the specific path defined by the YAML
    pd.DataFrame(ent_data).to_csv(MASTER_FILE, mode='a', index=False, header=not os.path.exists(MASTER_FILE))
    print(f"Successfully wrote to {MASTER_FILE}")

if __name__ == "__main__":
   print(f"\n{'='*60}")
    print(f"REGIONAL MACRO-ENVIRONMENT")
    print(f"{'='*60}")
    print(f"{'COUNTRY':<8} {'GDP %':<8} {'INFL %':<8}")
    # Assuming you have logic for inflation; if not, you can hardcode or placeholder it
    for m in macro_summary:
        print(f"{m['COUNTRY']:<8} {m['GDP']:<8.2f} {'N/A':<8}")
    
    print(f"\n{'='*60}")
    print(f"ENTERPRISE PERFORMANCE MATRIX")
    print(f"Systemic Risk Threshold (VaR 95%): {var_95:.4f}")
    print(f"{'='*60}")
    print(f"{'ENTERPRISE':<16} {'MOMENTUM':<12} {'STATUS':<10} {'P/E':<6} {'MARGIN'}")
    
    # Sort and print without emojis
    for row in sorted(ent_data, key=lambda x: x['STATUS'], reverse=True):
        status_text = "REVIEW" if row['STATUS'] == "REVIEW" else "STABLE"
        print(f"{row['ENTERPRISE']:<16} {row['MOMENTUM']:<12} {status_text:<10} {row['P/E']:<6} {row['MARGIN']}")
