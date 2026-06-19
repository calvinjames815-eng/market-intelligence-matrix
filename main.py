import os
import time
import datetime
import pandas as pd
import numpy as np
import yfinance as yf

# CONFIGURATION
PROJECT_ROOT = os.getcwd()
CACHE_DIR = os.path.join(PROJECT_ROOT, "market_engine_cache")
os.makedirs(CACHE_DIR, exist_ok=True)
MASTER_FILE = os.path.join(CACHE_DIR, "telemetry.csv")

COUNTRY_METRICS = {
    "USA": {"GDP": "2.79%", "RISK": "LOW", "VIABILITY": "STABLE", "HUB": "284", "INFL": "2.95%"},
    "CHN": {"GDP": "4.97%", "RISK": "MODERATE", "VIABILITY": "GROWTH", "HUB": "312", "INFL": "0.22%"},
    "TWN": {"GDP": "2.30%", "RISK": "MODERATE", "VIABILITY": "STABLE", "HUB": "115", "INFL": "1.90%"},
    "SAU": {"GDP": "1.99%", "RISK": "LOW", "VIABILITY": "STABLE", "HUB": "110", "INFL": "1.68%"},
    "KOR": {"GDP": "2.00%", "RISK": "LOW", "VIABILITY": "STABLE", "HUB": "142", "INFL": "2.32%"},
    "NLD": {"GDP": "1.08%", "RISK": "LOW", "VIABILITY": "STABLE", "HUB": "85", "INFL": "2.10%"}
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

def run_engine():
    tickers = sorted(list(TARGET_COMPANIES.keys()))
    df = yf.download(tickers, period="1y", progress=False)['Close']
    df = df.ffill().bfill()
    returns = df.pct_change().dropna()
    
    market_mean = returns.mean(axis=1)
    stress_impact = returns.apply(lambda x: x.corr(market_mean))
    
    cov_matrix = returns.cov().fillna(0) + np.eye(len(tickers)) * 1e-6
    sims = np.random.multivariate_normal(returns.mean().values, cov_matrix, (10000, 5))
    var_95 = np.percentile(sims.sum(axis=2).mean(axis=1), 5)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ent_data = []
    
    for t in tickers:
        try:
            name, code, pe, margin = TARGET_COMPANIES[t]
            m = COUNTRY_METRICS.get(code, {"GDP": "0%", "RISK": "N/A", "VIABILITY": "N/A", "HUB": "0", "INFL": "0%"})
            
            mom = ((df[t].iloc[-1] - df[t].iloc[-90]) / df[t].iloc[-90]) * 100
            impact = stress_impact[t] if t in stress_impact else 0
            status = "REVIEW" if (impact < -0.15 or (mom/100) < var_95) else "STABLE"
            
            ent_data.append({
                "TIMESTAMP": timestamp, "COUNTRY": code, "ENTERPRISE": name,
                "MOMENTUM": f"{mom:+.2f}%", "STATUS": status, "P/E": f"{pe:.1f}x", 
                "MARGIN": f"{margin*100:.0f}%", "GDP": m["GDP"], "RISK": m["RISK"],
                "VIABILITY": m["VIABILITY"], "HUB_OSM": m["HUB"], "INFL": m["INFL"]
            })
            time.sleep(0.5) # Prevents database locking
        except Exception as e:
            print(f"Skipping {t}: {e}")
            continue
    
    # Save to telemetry
    pd.DataFrame(ent_data).to_csv(MASTER_FILE, mode='a', index=False, header=not os.path.exists(MASTER_FILE))
    return ent_data, var_95

if __name__ == "__main__":
    ent_data, var_95 = run_engine()
    
    print(f"\n{'='*60}\nENTERPRISE PERFORMANCE MATRIX\nSystemic Risk Threshold (VaR 95%): {var_95:.4f}\n{'='*60}")
    print(f"{'ENTERPRISE':<16} {'MOMENTUM':<12} {'STATUS':<10} {'P/E':<6} {'MARGIN'}")
    for row in sorted(ent_data, key=lambda x: x['STATUS'], reverse=True):
        print(f"{row['ENTERPRISE']:<16} {row['MOMENTUM']:<12} {row['STATUS']:<10} {row['P/E']:<6} {row['MARGIN']}")
