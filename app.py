import streamlit as st


st.set_page_config(
    page_title="AI Market Pulse & Risk Briefing",
    page_icon="📈",
    layout="wide",
)

st.title("📈 AI Market Pulse & Risk Briefing Dashboard")
st.caption("A Sales & Trading-style dashboard for cross-asset monitoring, portfolio risk, news sentiment, and AI briefing.")

st.markdown(
    """
## Project Purpose

This dashboard simulates a lightweight **Sales & Trading analyst workflow**: monitor market moves, identify risk signals,
interpret financial headlines, and generate a concise client-facing morning brief.

### Key Modules

1. **Market Overview** – cross-asset returns, rolling volatility, and correlation.
2. **Portfolio Risk** – VaR, Expected Shortfall, drawdown, and stress scenarios.
3. **News Sentiment** – financial headline scoring and market theme tagging.
4. **AI Morning Brief** – structured market commentary for client conversations.

### Why It Matters for Sales & Trading

Sales & Trading sits at the intersection of markets, clients, and risk-aware decision-making. This project demonstrates
how AI and data workflows can help analysts translate market noise into structured views and actionable talking points.
"""
)

st.info("Use the sidebar pages to explore the dashboard modules. The app uses live data when available and falls back to built-in sample data for reliable demos.")
