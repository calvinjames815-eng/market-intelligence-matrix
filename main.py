import os
import pandas as pd
import numpy as np

# CONFIGURATION
PROJECT_ROOT = os.getcwd()
CACHE_DIR = os.path.join(PROJECT_ROOT, "market_engine_cache")
os.makedirs(CACHE_DIR, exist_ok=True)
MASTER_FILE = os.path.join(CACHE_DIR, "macro_scorecard.csv")

# Defining the target universe
COUNTRIES = [
    "USA", "JPN", "CHN", "IND", "CHE", "KOR", 
    "NLD", "TWN", "SAU", "ARE", "SGP", "DEU"
]

def get_macro_data(country_code):
    """
    STUB: Replace this with calls to wbdata or requests for OSM.
    Returns normalized values (0 to 1 scale) for the scoring function.
    """
    # Placeholder data for logic testing
    return {
        "gdp_growth": np.random.uniform(0.01, 0.06),
        "inflation": np.random.uniform(0.01, 0.05),
        "infrastructure": np.random.uniform(0.5, 0.9)
    }

def calculate_attractiveness(data, weights=(0.5, 0.3, 0.2)):
    """
    Scoring Function: (w1 * GDP) - (w2 * Inflation) + (w3 * Infrastructure)
    """
    w_gdp, w_infl, w_infra = weights
    score = (w_gdp * data["gdp_growth"]) - (w_infl * data["inflation"]) + (w_infra * data["infrastructure"])
    return round(score, 4)

def run_simulation(n_iterations=1000):
    """
    Runs a Monte Carlo simulation on the scores to determine Risk-Adjusted Attractiveness.
    """
    results = []
    for country in COUNTRIES:
        # Simulate volatility in macro-factors
        scores = []
        for _ in range(n_iterations):
            data = get_macro_data(country)
            scores.append(calculate_attractiveness(data))
        
        results.append({
            "COUNTRY": country,
            "MEAN_SCORE": np.mean(scores),
            "STDEV": np.std(scores),
            "RISK_ADJUSTED": np.mean(scores) - (2 * np.std(scores)) # Conservative estimate
        })
    return pd.DataFrame(results)

if __name__ == "__main__":
    df_results = run_simulation()
    df_results = df_results.sort_values(by="RISK_ADJUSTED", ascending=False)
    
    print(f"{'='*50}\nSTRATEGIC MARKET ENTRY SCORECARD\n{'='*50}")
    print(df_results.to_string(index=False))
    
    # Secure storage: Only append if file doesn't exist to prevent overwrite hacks
    if not os.path.exists(MASTER_FILE):
        df_results.to_csv(MASTER_FILE, index=False)
