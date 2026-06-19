import sys
import os
import datetime
import pandas as pd
import numpy as np
import yfinance as yf

if not hasattr(pd, 'deprecate_kwarg'):
    from pandas.util._exceptions import find_stack_level
    import warnings
    def deprecate_kwarg(old_arg_name, new_arg_name, mapping=None, stacklevel=2):
        def _deprecate(func):
            return func
        return _deprecate
    pd.deprecate_kwarg = deprecate_kwarg

from pandas_datareader import wb

# CONFIGURATION
CACHE_DIR = "market_engine_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
MASTER_FILE = os.path.join(CACHE_DIR, "telemetry.csv")

# Map codes to World Bank ISOs
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
    """Fetches live 5-year average macro health from World Bank."""
    try:
        data = wb.download(indicator=['NY.GDP.MKTP.KD.ZG', 'FP.CPI.TOTL.ZG'], 
                           country=[country_iso], start=2020, end=2025)
        avg_growth = data['NY.GDP.MKTP.KD.ZG'].tail(5).mean()
        avg_infl = data['FP.CPI.TOTL.ZG'].tail(5).mean()
        rating = "LOW" if avg_growth > 2.0 else "MODERATE"
        viability = "STABLE" if avg_growth > 2.0 else "WATCH"
        return avg_growth, avg_infl, rating, viability
    except:
        return 0.0, 0.0, "N/A", "N/A"

def run_engine():
    tickers = sorted(list(TARGET_COMPANIES.keys()))
    df = yf.download(tickers, period="1y", progress=False, auto_adjust=True)['Close']
    
    # Risk Floor Calculation
    returns = df.pct_change(fill_method=None).dropna()
    cov_matrix = returns.cov().fillna(0) + np.eye(len(tickers)) * 1e-6
    sims = np.random.multivariate_normal(returns.mean().values, cov_matrix, (10000, 5))
    var_95 = np.percentile(sims.sum(axis=2).mean(axis=1), 5)

    ent_data, macro_summary = [], []
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Fetch Macro
    for iso, wb_code in COUNTRY_ISO_MAP.items():
        gdp, inf, risk, viab = get_market_health(wb_code)
        macro_summary.append({"COUNTRY": iso, "GDP": gdp, "RISK": risk, "VIABILITY": viab})

    # Fetch Performance
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

    # Write to CSV
    pd.DataFrame(ent_data).to_csv(MASTER_FILE, mode='a', index=False, header=not os.path.exists(MASTER_FILE))

    # Clean Output
    print(f"\n{'='*60}\nREGIONAL MACRO-ENVIRONMENT (LIVE DATA)\n{'='*60}")
    print(f"{'COUNTRY':<10} {'5YR GDP':<12} {'RISK':<12} {'VIABILITY'}")
    for m in macro_summary:
        print(f"{m['COUNTRY']:<10} {m['GDP']:+<12.2f} {m['RISK']:<12} {m['VIABILITY']}")
    
    print(f"\n{'='*60}\nENTERPRISE PERFORMANCE MATRIX\nSystemic Risk Threshold: {var_95:.4f}\n{'='*60}")
    print(f"{'ENTERPRISE':<16} {'MOMENTUM':<12} {'STATUS':<10} {'P/E':<6} {'MARGIN'}")
    for row in sorted(ent_data, key=lambda x: x['STATUS'], reverse=True):
        print(f"{row['ENTERPRISE']:<16} {row['MOMENTUM']:<12} {row['STATUS']:<10} {row['P/E']:<6} {row['MARGIN']}")

if __name__ == "__main__":
    try:
        run_engine()
    except Exception as e:
        print(f"Pipeline failed: {e}")
        sys.exit(1)
