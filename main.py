import sys
import os
import datetime
import pandas as pd
import numpy as np
import yfinance as yf

# CONFIGURATION
CACHE_DIR = "market_engine_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

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

MACRO_DATA = {
    "USA": (284, 2.79, 2.95), "CHN": (312, 4.97, 0.22), "TWN": (115, 2.30, 1.90),
    "SAU": (110, 1.99, 1.68), "KOR": (142, 2.00, 2.32), "NLD": (85, 1.08, 2.10)
}

def run_engine():
    tickers = sorted(list(TARGET_COMPANIES.keys()))
    df = yf.download(tickers, period="1y", progress=False, auto_adjust=True)['Close']
    
    # Calculate Risk Floor
    returns = df.pct_change(fill_method=None).dropna()
    cov_matrix = returns.cov().fillna(0) + np.eye(len(tickers)) * 1e-6
    sims = np.random.multivariate_normal(returns.mean().values, cov_matrix, (10000, 5))
    var_95 = np.percentile(sims.sum(axis=2).mean(axis=1), 5)

    ent_data, cntry_data = [], []
    for t in tickers:
        name, code, pe, margin = TARGET_COMPANIES[t]
        osm, gdp, infl = MACRO_DATA.get(code, (0, 0.0, 0.0))
        series = df[t].dropna()
        mom = ((series.iloc[-1] - series.iloc[-90]) / series.iloc[-90]) * 100
        
        status = "REVIEW" if (mom/100) < var_95 else "STABLE"
        ent_data.append({"ENTERPRISE": name, "MOMENTUM": f"{mom:+.2f}%", "STATUS": status, "P/E": f"{pe:.1f}x", "MARGIN": f"{margin*100:.0f}%"})
        
        if not any(c['COUNTRY'] == code for c in cntry_data):
            cntry_data.append({"COUNTRY": code, "HUB OSM": osm, "GDP %": gdp, "INFL %": infl})

    # Display and Cache
    report_date = datetime.date.today()
    ent_df = pd.DataFrame(ent_data)
    cntry_df = pd.DataFrame(cntry_data)
    
    ent_df.to_csv(os.path.join(CACHE_DIR, f"enterprise_{report_date}.csv"), index=False)

    print(f"{'='*60}\nREGIONAL MACRO-ENVIRONMENT\n{'='*60}")
    print(cntry_df.to_string(index=False))
    print(f"\n{'='*60}\nENTERPRISE PERFORMANCE MATRIX\nSystemic Risk Threshold (VaR 95%): {var_95:.4f}\n{'='*60}")
    print(ent_df.to_string(index=False))

if __name__ == "__main__":
    run_engine()
