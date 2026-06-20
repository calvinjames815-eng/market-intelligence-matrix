import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="Market Entry Simulator", layout="wide")
st.title("Global Market Attractiveness Scorecard")

# 2. Load the Source of Truth
@st.cache_data
def load_data():
    return pd.read_csv("market_engine_cache.csv")

df = load_data()

# 3. GE-McKinsey Matrix Visualization
fig = px.scatter(
    df, 
    x="Competitive_Strength", 
    y="Attractiveness_Score", 
    text="Market_Name",
    title="GE-McKinsey Nine-Box Matrix"
)
fig.update_traces(textposition='top center')
fig.add_hline(y=0.66, line_dash="dash") # Thresholds for High/Med/Low
fig.add_vline(x=0.66, line_dash="dash")

st.plotly_chart(fig, use_container_width=True)

# 4. Data Table
st.subheader("Raw Metric Data")
st.dataframe(df)
