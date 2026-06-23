import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="Market Entry Simulator", layout="wide")
st.title("Global Market Attractiveness Scorecard")

# 2. Data Loading
@st.cache_data(ttl=3600) # Refreshes cache every hour
def load_data():
    return pd.read_csv("market_engine_cache.csv")

df = load_data()

# 3. Categorize for the Nine-Box Matrix
# Assuming 0-0.33 (Low), 0.33-0.66 (Med), 0.66-1.0 (High)
def get_zone(row):
    if row['Attractiveness_Score'] > 0.66 and row['Competitive_Strength'] > 0.66:
        return "Invest / Grow"
    elif row['Attractiveness_Score'] < 0.33 and row['Competitive_Strength'] < 0.33:
        return "Harvest / Divest"
    else:
        return "Selectivity / Earnings"

df['Zone'] = df.apply(get_zone, axis=1)

# 4. Enhanced Visualization
fig = px.scatter(
    df, 
    x="Competitive_Strength", 
    y="Attractiveness_Score", 
    text="Market_Name",
    color="Zone", # Automatically colors the bubbles by strategy
    size_max=60,
    range_x=[0, 1],
    range_y=[0, 1],
    title="GE-McKinsey Strategic Positioning"
)

# Adding the grid lines for the 3x3 effect
fig.add_hline(y=0.33, line_dash="dot", line_color="gray")
fig.add_hline(y=0.66, line_dash="dash", line_color="black")
fig.add_vline(x=0.33, line_dash="dot", line_color="gray")
fig.add_vline(x=0.66, line_dash="dash", line_color="black")

fig.update_traces(textposition='top center')
st.plotly_chart(fig, use_container_width=True)

# 5. Data Table
with st.expander("View Raw Metric Data"):
    st.dataframe(df)
