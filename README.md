# Global Market Entry Simulation Engine

![Market Matrix](matrix.png)

## What This Is

Most market entry decisions get made with a mix of gut feel and outdated reports. This tool tries to fix that — it pulls live economic data from the World Bank, runs it through a weighted scoring model, and surfaces which markets are actually worth pursuing.

The output is a ranked dashboard that tells you: **go here, watch this one, avoid that.**

[🚀 View Live Dashboard](https://market-entry-simulator.streamlit.app/)

---

## Project Documentation

Want to see the full reasoning behind the model — the math, the framework choices, the tradeoffs? I wrote it up here:

[📄 Download Market Entry Simulation Case Study (PDF)](case-study.pdf)

---

## How the Scoring Works

Each market gets a `RISK_ADJ_SCORE` built from three factors, weighted by how much they actually move the needle:

- **Velocity (60%):** GDP growth averaged over 15 years, with a decay factor so a market that peaked a decade ago doesn't look artificially attractive.
- **Inflation Penalty (20%):** Uses CPI volatility — not just the headline number — to penalize markets where economic instability would eat into returns.
- **Market Maturity (20%):** Blends infrastructure quality with Ease of Doing Business scores to capture the practical cost of operating in a market.

To avoid the model being overconfident, I added a small Gaussian noise term (σ = 0.005) to growth inputs. Real economies aren't deterministic, and the model shouldn't pretend otherwise.

The whole thing maps onto the **GE-McKinsey Nine-Box Matrix** — a framework used by strategy consultants to plot industry attractiveness against competitive position.

---

## Under the Hood

- **Data pipeline:** Python script running on GitHub Actions, scheduled weekly. It hits the World Bank API, processes the metrics, and overwrites `market_engine_cache.csv` automatically — no manual updates needed.
- **Dashboard:** Built with Streamlit and Plotly. Kept deliberately simple so decision-makers can use it without a technical background.
- **Architecture:** The frontend reads from the cached CSV, which keeps load times fast and the app free of direct API dependencies.

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

## Run It Locally

```bash
git clone [your-repo-url]
pip install -r requirements.txt
python main.py        # builds the cache
streamlit run app.py  # launches the dashboard
```

---

## Why I Built It This Way

- **Framework first:** Anchoring the model to GE-McKinsey means the output maps to something analysts and executives already use — easier to trust and present.
- **Automated freshness:** A dashboard is only useful if the data isn't stale. The GitHub Actions pipeline solves that without any ongoing maintenance.
- **Actionable output:** The three-tier classification (Target / Watch / Avoid) was a deliberate choice. Rankings are hard to act on; clear categories aren't.
