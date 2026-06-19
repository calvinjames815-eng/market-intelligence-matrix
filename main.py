import os
import datetime
import logging
import numpy as np
import pandas as pd
import yfinance as yf
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
os.makedirs("market_engine_cache", exist_ok=True)

# --- CONFIGURATION ---
COUNTRIES = {
    "USA": "United States", "CHN": "China", "JPN": "Japan", "CHE": "Switzerland",
    "IND": "India", "BRA": "Brazil", "VNM": "Vietnam", "SAU": "Saudi Arabia",
    "ARE": "UAE", "KOR": "South Korea", "TWN": "Taiwan", "NLD": "Netherlands"
}

# Mapping: (Name, Country, P/E, EV/EBITDA, Margin)
TARGET_COMPANIES = {
    "NVDA": ("NVIDIA", "USA", 32.4, 28.1, 0.55), "AAPL": ("Apple", "USA", 28.1, 18.2, 0.26),
    "MSFT": ("Microsoft", "USA", 31.5, 20.4, 0.35), "GOOGL": ("Alphabet", "USA", 24.2, 14.8, 0.27),
    "AMZN": ("Amazon", "USA", 38.0, 13.1, 0.10), "TSM": ("TSMC", "TWN", 22.1, 11.5, 0.38),
    "AVGO": ("Broadcom", "USA", 26.4, 17.2, 0.22), "2222.SR": ("Saudi Aramco", "SAU", 16.5, 9.8, 0.42),
    "TSLA": ("Tesla", "USA", 45.2, 24.1, 0.12), "META": ("Meta Platforms", "USA", 23.9, 13.5, 0.32),
    "005930.KS": ("Samsung", "KOR", 14.1, 7.2, 0.08), "MU": ("Micron", "USA", 20.2, 11.4, 0.14),
    "000660.KS": ("SK Hynix", "KOR", 15.4, 8.1, 0.11), "BRK-B": ("Berkshire", "USA", 19.8, 12.0, 0.15),
    "LLY": ("Eli Lilly", "USA", 55.4, 34.2, 0.21), "WMT": ("Walmart", "USA", 25.1, 12.8, 0.03),
    "AMD": ("AMD", "USA", 34.1, 22.0, 0.11), "JPM": ("JPMorgan", "USA", 12.2, 10.1, 0.33),
    "ASML": ("ASML", "NLD", 36.5, 24.2, 0.28), "TCEHY": ("Tencent", "CHN", 18.2, 11.1, 0.29)
}

def run_integrated_engine():
    try:
        tickers = sorted(list(TARGET_COMPANIES.keys()))
        logging.info("⚡ Synchronizing with Global Market Tape...")
        
        # 1. FETCH DATA (Single source of truth)
        df = yf.download(tickers, period="1y", progress=False, auto_adjust=True)['Close']
        if df.empty: raise ValueError("Data fetch failed.")

        # 2. STOCHASTIC RISK MODEL (Phase 2)
        returns = df.pct_change(fill_method=None).dropna()
        cov_matrix = returns.cov().fillna(0) + np.eye(len(tickers)) * 1e-6
        sims = np.random.multivariate_normal(returns.mean().values, cov_matrix, (10000, 5))
        var_95 = np.percentile(sims.sum(axis=2).mean(axis=1), 5)

        # 3. GENERATE MATRIX (Phase 1)
        records = []
        for ticker in tickers:
            name, country, pe, ev, margin = TARGET_COMPANIES[ticker]
            closes = df[ticker].dropna()
            
            # Momentum
            mom = ((closes.iloc[-1] - closes.iloc[-90]) / closes.iloc[-90]) * 100 if len(closes) >= 90 else 0.0
            
            # Risk Status (Combined Logic)
            status = "URGENT REVIEW" if (mom/100) < var_95 else "STABLE"
            
            records.append({
                "Enterprise": name,
                "90D Momentum": f"{mom:+.2f}%",
                "Stability": status,
                "P/E": pe,
                "Margin %": margin * 100
            })

        # 4. OUTPUT
        df_final = pd.DataFrame(records)
        print(f"\n--- INTEGRATED BUSINESS INSIGHT ENGINE | {datetime.date.today()} ---")
        print(f"Systemic Risk Threshold (VaR 95%): {var_95:.4f}")
        print(df_final.to_string(index=False))
        
        # Export to CSV for your records
        df_final.to_csv(f"market_engine_cache/final_matrix_{datetime.date.today()}.csv")

    except Exception as e:
        logging.error(f"ENGINE CRITICAL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_integrated_engine()
