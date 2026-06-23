# Global Market Entry Simulation Engine

![Market Matrix](matrix.png)

## Executive Summary

This project is a consultant-grade strategic decision-support tool designed to rank global markets for corporate expansion. By automating data ingestion from the World Bank API and applying a custom Risk-Adjusted ROI framework, the engine enables stakeholders to move beyond intuition and rely on quantitative market modeling.

[View Live Dashboard](https://market-entry-simulator.streamlit.app/)

---

## Project Documentation

To understand the rationale behind the engine's design, mathematical modeling, and strategic framework, please refer to the detailed project case study:

[📄 Download Market Entry Simulation Case Study (PDF)](link-to-your-pdf-file)

---

## Strategic Methodology

The engine evaluates market attractiveness through the lens of the **GE-McKinsey Nine-Box Matrix**. Key inputs are synthesized into a `RISK_ADJ_SCORE` using a weighted framework:

- **Velocity (60%):** GDP growth rate smoothed over a 15-year horizon, incorporating maturity decay factors to model long-term terminal value.
- **Inflation Penalty (20%):** Standard deviation of CPI used as a volatility coefficient to deflate nominal ROI.
- **Market Maturity (20%):** Qualitative infrastructure and Ease of Doing Business (EODB) indexing.

**Stochastic Modeling:** To prevent deterministic bias, the engine injects Gaussian noise (σ = 0.005) into growth projections, simulating real-world macroeconomic uncertainty.

---

## Technical Architecture

The system is designed for low-maintenance, high-availability production:

- **ETL Pipeline:** A fully automated Python-based pipeline hosted on GitHub Actions. It executes weekly to pull fresh data, process metrics, and update the `market_engine_cache.csv`.
- **Frontend:** A responsive web application built with Streamlit, featuring interactive `Plotly` visualizations for executive-level decisioning.
- **Data Persistence:** A centralized cache-based architecture ensures the frontend remains lightweight and performs with sub-second latency.

---

## Project Structure

```
├── .github/workflows/      # CI/CD pipeline for automated data updates
├── app.py                  # Streamlit dashboard implementation
├── main.py                 # Core simulation and ETL engine
├── market_engine_cache.csv # Processed market data
└── requirements.txt        # Dependency management
```

---

## Deployment & Usage

The dashboard is deployed on Streamlit Cloud and keeps itself updated via GitHub Actions.

**To run locally:**

1. Clone the repository:
   ```bash
   git clone [your-repo-url]
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate data:
   ```bash
   python main.py
   ```
4. Launch the dashboard:
   ```bash
   streamlit run app.py
   ```

---
