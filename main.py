import sys
import datetime
import logging
import time
import numpy as np
import pandas as pd
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# 1. DEFINE TARGETS
TARGET_COMPANIES = {
    "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet",
    "AMZN": "Amazon", "TSM": "TSMC", "AVGO": "Broadcom", "2222.SR": "Saudi Aramco",
    "TSLA": "Tesla", "META": "Meta Platforms", "005930.KS": "Samsung", "MU": "Micron",
    "000660.KS": "SK Hynix", "BRK-B": "Berkshire", "LLY": "Eli Lilly",
    "WMT": "Walmart", "AMD": "AMD", "JPM": "JPMorgan", "ASML": "ASML", "TCEHY": "Tencent"
}

def get_market_data(tickers):
    """Fetches market data using native yfinance with retry logic."""
    for attempt in range(3):
        try:
            logging.info(f"Attempt {attempt+1}: Fetching data...")
            # Native download call - yfinance handles headers internally now
            data = yf.download(
                tickers, 
                period="1y", 
                progress=False, 
                auto_adjust=True
            )
            
            if not data.empty:
                # Handle MultiIndex structure: Extract 'Close' prices
                if isinstance(data.columns, pd.MultiIndex):
                    return data['Close']
                return data['Close']
        
        except Exception as e:
            logging.warning(f"Attempt {attempt+1} failed: {e}")
        
        time.sleep(30) # Mandatory cool-down before retry
    return pd.DataFrame()

def run_integrated_engine():
    try:
        tickers = sorted(list(TARGET_COMPANIES.keys()))
        df = get_market_data(tickers)
        
        if df.empty:
            raise ValueError("No data returned from Yahoo Finance.")

        # Stochastic Simulation (Phase 2)
        returns = df.pct_change(fill_method=None).dropna()
        cov_matrix = returns.cov().fillna(0) + np.eye(len(tickers)) * 1e-6
        sims = np.random.multivariate_normal(returns.mean().values, cov_matrix, (10000, 5))
        var_95 = np.percentile(sims.sum(axis=2).mean(axis=1), 5)

        # Insight Logic (Phase 1)
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
    run_integrated_engine()
