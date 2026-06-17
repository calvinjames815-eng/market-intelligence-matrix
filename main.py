import os
import datetime
import logging
import warnings
import numpy as np
import pandas as pd
import yfinance as yf

# --- SETUP ---
warnings.filterwarnings("ignore", category=FutureWarning)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
os.makedirs("market_engine_cache", exist_ok=True)

# [KEEP YOUR EXISTING DICTIONARIES HERE: COUNTRIES, TARGET_COMPANIES, MACRO_CACHE, ETC]
# (Note: I have abbreviated them for brevity, keep your full version)
# TARGET_COMPANIES = {...} 

def run_integrated_engine():
    tickers = list(TARGET_COMPANIES.keys())
    
    # --- PHASE 1: DATA INGESTION ---
    logging.info("⚡ Executing unified sub-second market tape request...")
    df = yf.download(tickers, period="1y", progress=False, auto_adjust=True)['Close']
    
    # --- PHASE 2: STOCHASTIC RISK ENGINE ---
    # Calculating systemic risk using Covariance Matrix and Monte Carlo
    returns = df.pct_change(fill_method=None).dropna()
    cov_matrix = returns.cov().fillna(0) + np.eye(len(tickers)) * 1e-6
    
    # Simulate 10,000 iterations
    simulations = np.random.multivariate_normal(returns.mean().values, cov_matrix, (10000, 5))
    var_95 = np.percentile(simulations.sum(axis=2).mean(axis=1), 5)
    
    # --- PHASE 3: AGGREGATION & REPORTING ---
    master_records = []
    for ticker, (name, home_country, def_pe, def_ev, def_margin) in TARGET_COMPANIES.items():
        closes = df[ticker].dropna()
        mom = ((closes.iloc[-1] - closes.iloc[-90]) / closes.iloc[-90]) * 100 if len(closes) >= 90 else 0.0
        
        # Risk Logic: Flag if company performance < Systemic VaR floor
        risk_status = "URGENT REVIEW" if mom < (var_95 * 100) else "STABLE"
        
        master_records.append({
            "Enterprise": name,
            "90D Momentum": f"{mom:+.2f}%",
            "Stability Rating": risk_status,
            "VaR_Threshold": f"{var_95:.4f}"
        })

    # OUTPUT
    df_final = pd.DataFrame(master_records)
    print(f"\n--- MANAGEMENT MATRIX | {datetime.date.today()} ---")
    print(df_final.to_string(index=False))

if __name__ == "__main__":
    run_integrated_engine()
