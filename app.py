import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="Market Entry Simulator", layout="wide")

st.title("📊 Global Market Attractiveness Scorecard")
st.markdown("Dynamic GE-McKinsey Nine-Box Matrix for real-time market entry analysis.")

# 2. Data Loading
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv("market_engine_cache.csv")
    df.columns = df.columns.str.strip() 
    return df

try:
    df = load_data()

    # 3. Dynamic Zone Logic
    def get_zone(row):
        # We use dynamic thresholds based on the actual data to avoid empty zones
        attr = float(row['Infrastructure']) 
        comp = float(row['RISK_ADJ_SCORE'])
        
        if attr >= df['Infrastructure'].median() and comp >= df['RISK_ADJ_SCORE'].median():
            return "1. Invest / Grow"
        elif attr <= df['Infrastructure'].median() and comp <= df['RISK_ADJ_SCORE'].median():
            return "3. Harvest / Divest"
        else:
            return "2. Selectivity / Earnings"

    df['Zone'] = df.apply(get_zone, axis=1)

    # 4. Professional Visualization (DYNAMIC RANGES)
    # Using 'auto' for ranges ensures no points are cut off
    fig = px.scatter(
        df, 
        x="RISK_ADJ_SCORE", 
        y="Infrastructure", 
        text="country",
        color="Zone",
        size_max=14,
        title="GE-McKinsey Strategic Positioning Matrix",
        template="plotly_white"
    )

    # Dynamic Gridlines based on medians
    fig.add_vline(x=df['RISK_ADJ_SCORE'].median(), line_dash="dash", line_color="gray")
    fig.add_hline(y=df['Infrastructure'].median(), line_dash="dash", line_color="gray")

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

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    st.info("Ensure main.py has run at least once to generate 'market_engine_cache.csv'.")

# Hide Streamlit branding
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
