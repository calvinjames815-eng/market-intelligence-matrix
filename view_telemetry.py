import pandas as pd

# Load your history
df = pd.read_csv("market_engine_cache/telemetry.csv")

# Print it using the same formatting logic
print(f"{'ENTERPRISE':<16} {'MOMENTUM':<12} {'STATUS':<10} {'P/E':<6} {'MARGIN'}")
for _, row in df.tail(20).iterrows(): # Shows the latest 20 entries
    print(f"{row['ENTERPRISE']:<16} {row['MOMENTUM']:<12} {row['STATUS']:<10} {row['P/E']:<6} {row['MARGIN']}")
