# Global Market Entry Simulation Engine

![Market Matrix](matrix.png)

I decided to built this tool to automate how I evaluate new global market trends. I didn't want to enter the market by rely on Intuition and relying at outdated reports, so I created a pipeline that pulls live economic data from the World Bank and it runs through a weighted scoring model based on the GE-McKinsey Nine-Box Matrix.

[View Live Dashboard](https://market-entry-simulator.streamlit.app/) | [Download Market Entry Simulation Case Study (PDF)](case-study.pdf)

---

## How it works
I calculated the `RISK_ADJ_SCORE` for each market it's based on four factors:

  - GDP growth (40%)
  - Labor capacity (30%)
  - Infrastructure (20%)
  - Inflation volatility (10%).

  I added a small Gaussian noise term (σ = 0.005) to the growth input. Real economies are messy and unpredictable, and I didn't want the model's decision to be highly optimistic about the results.
 
---

## Architecture

- **ETL pipeline:** A Python script runs weekly in GitHub Actions to gather latest data from the World Bank API and update `market_engine_cache.csv` automatically.
- **Dashboard:** I used Streamlit and Plotly for the UI. It reads directly from the cache to keep loadtime faster and avoid dependency on live API calls.
- **Result:** The dashboard categorizes the market into "Target," "Watch," or "Avoid." I like this better than a ranked list and it helps me figure out what to do next.
  
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

## How to set it upLocally

```bash
git clone [your-repo-url]
pip install -r requirements.txt
python main.py        # updates the cache
streamlit run app.py  # launch the dashboard
```

---
