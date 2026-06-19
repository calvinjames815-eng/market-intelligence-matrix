import numpy as np
import pandas as pd

def get_risk_adjusted_score(row, simulations=1000):
    """
    Monte Carlo: Samples GDP/Inflation from a normal distribution 
    to see the probability of success.
    """
    # Define volatility (std_dev) as 10% of the mean if no history
    gdp_std = abs(row['gdp_growth'] * 0.1)
    infl_std = abs(row['inflation'] * 0.1)
    
    # Run simulations
    sim_gdp = np.random.normal(row['gdp_growth'], gdp_std, simulations)
    sim_infl = np.random.normal(row['inflation'], infl_std, simulations)
    
    # Calculate scores for all simulations
    scores = (0.5 * sim_gdp) - (0.3 * sim_infl) + (0.2 * row['infrastructure'])
    
    return scores.mean() # Return the expected (average) risk-adjusted score

# --- In your main execution block ---
if __name__ == "__main__":
    data = get_data_with_cache()
    
    # 1. Apply Monte Carlo Engine
    data['RISK_ADJ_SCORE'] = data.apply(get_risk_adjusted_score, axis=1)
    
    # 2. Sort by the risk-adjusted result
    results = data.sort_values(by='RISK_ADJ_SCORE', ascending=False)
    
    print(f"\n{'='*60}\nMONTE CARLO RISK-ADJUSTED RANKING\n{'='*60}")
    print(results[['gdp_growth', 'inflation', 'RISK_ADJ_SCORE']])
