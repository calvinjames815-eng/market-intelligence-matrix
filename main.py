import sys
import datetime
import logging
import numpy as np
import pandas as pd
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Define companies at the top level so they are always visible
TARGET_COMPANIES = {
    "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet",
    "AMZN": "Amazon", "TSM": "TSMC", "AVGO": "Broadcom", "2222.SR": "Saudi Aramco",
    "TSLA": "Tesla", "META": "Meta Platforms", "005930.KS": "Samsung", "MU": "Micron",
    "000660.KS": "SK Hynix", "BRK-B": "Berkshire", "LLY": "Eli Lilly",
    "WMT": "Walmart", "AMD": "AMD", "JPM": "JPMorgan", "ASML": "ASML", "TCEHY": "Tencent"
}

def run_business_insight_engine():
    try:
        # Use the global variable defined above
        tickers = sorted(list(TARGET_COMPANIES.keys()))
        
        # 1. LIVE DATA FETCH
        df = yf.download(tickers, period="1y", progress=False, auto_adjust=True)['Close']
        if df.empty:
            raise ValueError("Connection Timeout: No data returned from market tape.")

        # 2. STOCHASTIC SIMULATION
        # Ensure we drop NaNs specifically for the return calculation
        returns = df.pct_change(fill_method=None).dropna()
        cov_matrix = returns.cov().fillna(0) + np.eye(len(tickers)) * 1e-6
        
        # 10,000 iterations to determine the 95% Risk Floor
        simulations = np.random.multivariate_normal(returns.mean().values, cov_matrix, (10000, 5))
        var_95 = np.percentile(simulations.sum(axis=2).mean(axis=1), 5)
        
        # 3. BUSINESS INSIGHT LOGIC
        insight_data = []
        for ticker in tickers:
            name = TARGET_COMPANIES[ticker]
            series = df[ticker].dropna()
            
            mom = ((series.iloc[-1] - series.iloc[-90]) / series.iloc[-90]) * 100 if len(series) >= 90 else 0.0
            status = "REVIEW REQUIRED" if mom < (var_95 * 100) else "STABLE"
            
            insight_data.append({
                "Enterprise": name,
                "90D Momentum": f"{mom:+.2f}%",
                "Status": status
            })

        # 4. OUTPUT
        df_final = pd.DataFrame(insight_data)
        print(f"\n--- MARKET INTELLIGENCE REPORT | {datetime.date.today()} ---")
        print(f"Systemic Risk Threshold (VaR 95%): {var_95:.4f}")
        print("-" * 60)
        print(df_final.to_string(index=False))
        print("-" * 60)

    except Exception as e:
        logging.error(f"ENGINE CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_business_insight_engine()
