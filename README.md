# Global Market Entry Simulation Engine

![Market Matrix](matrix.png)

A decision-support tool that automates the evaluation of global market trends using live World Bank economic data and a weighted scoring algorithm based on the GE-McKinsey Nine-Box Matrix.

[View Live Dashboard](https://market-entry-simulator.streamlit.app/) | [Download Market Entry Simulation Case Study (PDF)](case-study.pdf)

---

## How it works
The `RISK_ADJ_SCORE` for each market is derived from four weighted factors:

  - GDP growth (40%) Adjusted with a Gaussian noise term (σ = 0.005) to account for macroeconomic stochasticity and prevent over-optimistic projections.
  - Labor capacity (30%)
  - Infrastructure (20%)
  - Inflation volatility (10%).
 
---

## Architecture

- **ETL pipeline:** Python-based automation running via GitHub Actions to fetch live World Bank data and persist the results to  `market_engine_cache.csv`.
- **Dashboard:** Streamlit/Plotly interface that visualizes data from the cached CSV, ensuring low-latency performance and decoupling the UI from external API constraints.
- **Result:** Markets are separated into "Target," "Watch," or "Avoid" categories, providing clear actionable business insights.
  
---

## Project Structure

```
├── .github/workflows/      # CI/CD pipeline for automated data updates
├── app.py                  # Streamlit dashboard
├── main.py                 # ETL engine and scoring logic
├── market_engine_cache.csv # Processed market data (auto-updated)
└── requirements.txt        # Dependencies
```

---

## How to set it up locally

```bash
git clone [your-repo-url]
pip install -r requirements.txt
python main.py        # updates the cache
streamlit run app.py  # launch the dashboard
```

---
