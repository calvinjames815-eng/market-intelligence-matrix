import sys
import datetime
import logging
import time
import numpy as np
import pandas as pd
import yfinance as yf
import requests_cache

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# 1. DEFINE YOUR DATA FETCHING FUNCTION FIRST
def get_market_data(tickers):
    session = requests_cache.CachedSession('yfinance.cache')
    session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
    
    for attempt in range(3):
        try:
            logging.info(f"Attempt {attempt+1}: Fetching data...")
            data = yf.download(tickers, period="1y", session=session, progress=False, auto_adjust=True)
            if not data.empty:
                return data['Close']
        except Exception as e:
            logging.warning(f"Error fetching data: {e}")
        time.sleep(30) 
    return pd.DataFrame()

# 2. YOUR TARGET COMPANIES DICTIONARY
TARGET_COMPANIES = {
    "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet",
    "AMZN": "Amazon", "TSM": "TSMC", "AVGO": "Broadcom", "2222.SR": "Saudi Aramco",
    "TSLA": "Tesla", "META": "Meta Platforms", "005930.KS": "Samsung", "MU": "Micron",
    "000660.KS": "SK Hynix", "BRK-B": "Berkshire", "LLY": "Eli Lilly",
    "WMT": "Walmart", "AMD": "AMD", "JPM": "JPMorgan", "ASML": "ASML", "TCEHY": "Tencent"
}

# 3. YOUR MAIN ENGINE
def run_business_insight_engine():
    try:
        tickers = sorted(list(TARGET_COMPANIES.keys()))
        
        # --- CALL THE NEW FUNCTION HERE ---
        df = get_market_data(tickers)
        
        if df.empty:
            raise ValueError("Connection Timeout: No data returned from market tape.")

        # --- STOCHASTIC RISK MODEL ---
        returns = df.pct_change(fill_method=None).dropna()
        cov_matrix = returns.cov().fillna(0) + np.eye(len(tickers)) * 1e-6
        sims = np.random.multivariate_normal(returns.mean().values, cov_matrix, (10000, 5))
        var_95 = np.percentile(sims.sum(axis=2).mean(axis=1), 5)

        # --- INSIGHTS ---
        insight_data = []
        for ticker in tickers:
            series = df[ticker].dropna()
            mom = ((series.iloc[-1] - series.iloc[-90]) / series.iloc[-90]) * 100 if len(series) >= 90 else 0.0
            status = "REVIEW REQUIRED" if (mom/100) < var_95 else "STABLE"
            insight_data.append({"Enterprise": TARGET_COMPANIES[ticker], "90D Momentum": f"{mom:+.2f}%", "Status": status})

        print(f"\n--- MARKET INTELLIGENCE REPORT | {datetime.date.today()} ---")
        print(pd.DataFrame(insight_data).to_string(index=False))

    except Exception as e:
        logging.error(f"ENGINE CRITICAL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_business_insight_engine()
