import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="Market Entry Simulator", layout="wide")

st.title("📊 Global Market Attractiveness Scorecard")
st.markdown("Dynamic GE-McKinsey Nine-Box Matrix for real-time market entry analysis.")

# 2. Data Loading with Column Cleaning
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv("market_engine_cache.csv")
    df.columns = df.columns.str.strip() # Remove hidden spaces
    return df

df = load_data()

# 3. Corrected Zone Logic (Matching your CSV columns)
def get_zone(row):
    # Using your actual CSV columns
    attr = float(row['Infrastructure']) 
    comp = float(row['RISK_ADJ_SCORE'])
    
    if attr >= 0.70 and comp >= 0.20:
        return "1. Invest / Grow"
    elif attr <= 0.50 and comp <= 0.12:
        return "3. Harvest / Divest"
    else:
        return "2. Selectivity / Earnings"

df['Zone'] = df.apply(get_zone, axis=1)

# 4. Professional Visualization (Using your actual column names)
fig = px.scatter(
    df, 
    x="RISK_ADJ_SCORE", 
    y="Infrastructure", 
    text="country",
    color="Zone",
    size_max=60,
    range_x=[0.1, 0.25], # Adjusted range to fit your specific data
    range_y=[0.4, 1.0],  # Adjusted range to fit your specific data
    title="GE-McKinsey Strategic Positioning Matrix",
    template="plotly_white"
)

# 3x3 Grid
for val_x in [0.15, 0.20]:
    fig.add_vline(x=val_x, line_dash="dash", line_color="gray", opacity=0.5)
for val_y in [0.60, 0.80]:
    fig.add_hline(y=val_y, line_dash="dash", line_color="gray", opacity=0.5)

fig.update_traces(textposition='top center', marker=dict(size=14))
st.plotly_chart(fig, use_container_width=True)

# 5. Consultant Metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Markets Analyzed", len(df))
with col2:
    top_market = df.loc[df['Infrastructure'].idxmax()]['country']
    st.metric("Top Infrastructure Market", top_market)

with st.expander("View Raw Metric Data"):
    st.dataframe(df, use_container_width=True)

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
