import pandas as pd

def display_dashboard():
    try:
        df = pd.read_csv("macro_scorecard.csv")
        print("--- Strategic Market Attractiveness Rankings ---")
        print(df[['SCORE']])
    except FileNotFoundError:
        print("No telemetry data found. Run main.py first.")

if __name__ == "__main__":
    display_dashboard()
