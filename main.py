import sys
import os
import datetime
import logging
import time
import numpy as np
import pandas as pd
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Ensure cache directory exists for GitHub Artifacts
CACHE_DIR = "market_engine_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

TARGET_COMPANIES = {
    "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet",
    "AMZN": "Amazon", "TSM": "TSMC", "AVGO": "Broadcom", "2222.SR": "Saudi Aramco",
    "TSLA": "Tesla", "META": "Meta Platforms", "005930.KS": "Samsung", "MU": "Micron",
    "000660.KS": "SK Hynix", "BRK-B": "Berkshire", "LLY": "Eli Lilly",
    "WMT": "Walmart", "AMD": "AMD", "JPM": "JPMorgan", "ASML": "ASML", "TCEHY": "Tencent"
}

def run_integrated_engine():
    try:
        tickers = sorted(list(TARGET_COMPANIES.keys()))
        logging.info(f"Initiating Engine at {datetime.datetime.now()}")
        
        # 1. Fetching Data
        df = yf.download(tickers, period="1y", progress=False, auto_adjust=True)['Close']
        
        # 2. Risk Calculation (Monte Carlo VaR95)
        returns = df.pct_change(fill_method=None).dropna()
        cov_matrix = returns.cov().fillna(0) + np.eye(len(tickers)) * 1e-6
        sims = np.random.multivariate_normal(returns.mean().values, cov_matrix, (10000, 5))
        var_95 = np.percentile(sims.sum(axis=2).mean(axis=1), 5)

        # 3. Insight Logic
        insight_data = []
        for ticker in tickers:
            series = df[ticker].dropna()
            mom = ((series.iloc[-1] - series.iloc[-90]) / series.iloc[-90]) * 100 if len(series) >= 90 else 0.0
            status = "⚠️ REVIEW" if (mom/100) < var_95 else "✅ STABLE"
            insight_data.append({
                "Ticker": ticker, 
                "Enterprise": TARGET_COMPANIES[ticker], 
                "90D Momentum": f"{mom:+.2f}%", 
                "Status": status
            })

        # 4. Generate Output Artifacts
        report_df = pd.DataFrame(insight_data)
        file_path = os.path.join(CACHE_DIR, f"market_report_{datetime.date.today()}.csv")
        report_df.to_csv(file_path, index=False)
        
        print(f"\n--- SYSTEMIC RISK THRESHOLD: {var_95:.4f} ---")
        print(report_df.to_string(index=False))
        logging.info(f"Artifact saved: {file_path}")

    except Exception as e:
        logging.error(f"ENGINE CRITICAL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_integrated_engine()
