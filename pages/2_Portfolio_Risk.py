import pandas as pd
import streamlit as st

from src.charts import drawdown_chart
from src.config import DEFAULT_TICKERS, DEFAULT_WEIGHTS, STRESS_SCENARIOS
from src.data_loader import load_market_data
from src.risk_metrics import (
    contribution_to_risk,
    daily_returns,
    normalize_weights,
    portfolio_returns,
    risk_summary,
    stress_test,
)

st.set_page_config(page_title="Portfolio Risk", page_icon="🛡️", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(135deg, #07111f 0%, #121826 55%, #21160d 100%); }
    [data-testid="stMetric"] { border: 1px solid rgba(255,204,112,0.22); border-radius: 18px; padding: 18px; background: rgba(255,204,112,0.06); }
    .risk-note { padding: 1rem; border-radius: 16px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=900)
def cached_market_data(tickers: tuple[str, ...], period: str) -> tuple[pd.DataFrame, str]:
    return load_market_data(tickers, period=period)


st.title("🛡️ Portfolio Risk Console")
st.caption("Translate a cross-asset portfolio into VaR, Expected Shortfall, drawdown, contribution-to-risk, and scenario losses.")

with st.sidebar:
    st.header("Portfolio Setup")
    selected = st.multiselect(
        "Portfolio assets",
        options=[ticker for ticker in DEFAULT_TICKERS if ticker != "^VIX"],
        default=list(DEFAULT_WEIGHTS.keys()),
        format_func=lambda ticker: f"{ticker} — {DEFAULT_TICKERS[ticker]}",
    )
    period = st.selectbox("Risk lookback", ["6mo", "1y", "2y"], index=1)
    st.divider()
    st.caption("Initial weights are normalized automatically.")
    raw_weights = {}
    for ticker in selected:
        raw_weights[ticker] = st.slider(
            ticker,
            min_value=0.0,
            max_value=1.0,
            value=float(DEFAULT_WEIGHTS.get(ticker, 0.05)),
            step=0.01,
        )

if not selected:
    st.warning("Select at least one portfolio asset from the sidebar.")
    st.stop()

prices, source = cached_market_data(tuple(selected), period)
returns = daily_returns(prices)
weights = normalize_weights(raw_weights, list(returns.columns))
port_ret = portfolio_returns(returns, weights)
summary = risk_summary(port_ret)
stress = stress_test(weights, STRESS_SCENARIOS)
ctr = contribution_to_risk(returns, weights)

st.markdown(
    f"<div class='risk-note'><b>Data mode:</b> {source}. Weight sliders are normalized to 100%, so the current portfolio weights sum to {weights.sum():.0%}.</div>",
    unsafe_allow_html=True,
)

cols = st.columns(5)
for col, (metric, value) in zip(cols, summary.items()):
    col.metric(metric, f"{value:.2%}")

left, right = st.columns([1.2, 0.8])
with left:
    st.plotly_chart(drawdown_chart(port_ret), use_container_width=True)
with right:
    st.subheader("Normalized weights")
    st.dataframe(weights.rename("Weight").map(lambda x: f"{x:.1%}"), use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Contribution to risk")
    display_ctr = ctr.sort_values("Contribution", ascending=False).copy()
    display_ctr["Contribution"] = display_ctr["Contribution"].map(lambda x: f"{x:.1%}")
    st.dataframe(display_ctr, use_container_width=True, hide_index=True)
with right:
    st.subheader("Scenario stress tests")
    display_stress = stress.copy()
    display_stress["Portfolio Shock"] = display_stress["Portfolio Shock"].map(lambda x: f"{x:.2%}")
    st.dataframe(display_stress, use_container_width=True, hide_index=True)

worst = stress.sort_values("Portfolio Shock").iloc[0]
st.subheader("Risk read-through")
st.write(
    f"The main downside scenario is **{worst['Scenario']}**, with an estimated portfolio shock of **{worst['Portfolio Shock']:.2%}**. "
    "For an interview discussion, emphasize that the dashboard does not predict markets; it organizes risk signals so an analyst can explain exposure, downside, and client-relevant trade-offs quickly."
)
