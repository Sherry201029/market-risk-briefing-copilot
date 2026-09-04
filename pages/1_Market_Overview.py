import pandas as pd
import streamlit as st

from src.charts import bar_returns, heatmap, line_chart
from src.config import DEFAULT_TICKERS
from src.data_loader import load_market_data
from src.risk_metrics import daily_returns


st.set_page_config(page_title="Market Overview", page_icon="🌏", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #08111f; color: #e8edf5; }
    [data-testid="stMetric"] { background: rgba(255,255,255,0.055); border: 1px solid rgba(255,255,255,0.12); border-radius: 18px; padding: 18px; }
    .market-card { border-left: 4px solid #58d4ff; padding: 0.7rem 1rem; background: rgba(88,212,255,0.08); border-radius: 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=900)
def cached_market_data(tickers: tuple[str, ...], period: str) -> tuple[pd.DataFrame, str]:
    return load_market_data(tickers, period=period)


st.title("🌏 Cross-Asset Market Overview")
st.caption("Monitor a compact S&T watchlist across equities, rates proxies, FX, commodities, and volatility.")

with st.sidebar:
    st.header("Market Watchlist")
    selected = st.multiselect(
        "Assets",
        options=list(DEFAULT_TICKERS.keys()),
        default=["SPY", "QQQ", "EWH", "TLT", "IEF", "UUP", "GLD", "USO", "^VIX"],
        format_func=lambda ticker: f"{ticker} — {DEFAULT_TICKERS[ticker]}",
    )
    period = st.selectbox("Lookback window", ["3mo", "6mo", "1y", "2y"], index=2)

if not selected:
    st.warning("Select at least one asset from the sidebar.")
    st.stop()

prices, source = cached_market_data(tuple(selected), period)
returns = daily_returns(prices)
latest_returns = returns.iloc[-1].dropna() if not returns.empty else pd.Series(dtype=float)
vol_21d = returns.rolling(21).std().iloc[-1].dropna() * (252 ** 0.5) if len(returns) >= 21 else pd.Series(dtype=float)

st.markdown(
    f"<div class='market-card'><b>Data mode:</b> {source}. Live Yahoo Finance is used when reachable; deterministic sample data is used as a resilient demo fallback.</div>",
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
best_asset = latest_returns.idxmax() if not latest_returns.empty else "N/A"
worst_asset = latest_returns.idxmin() if not latest_returns.empty else "N/A"
avg_move = latest_returns.mean() if not latest_returns.empty else 0.0
highest_vol = vol_21d.idxmax() if not vol_21d.empty else "N/A"

col1.metric("Best latest session", best_asset, f"{latest_returns.get(best_asset, 0):.2%}" if best_asset != "N/A" else "N/A")
col2.metric("Weakest latest session", worst_asset, f"{latest_returns.get(worst_asset, 0):.2%}" if worst_asset != "N/A" else "N/A")
col3.metric("Average asset move", f"{avg_move:.2%}")
col4.metric("Highest 21D ann. vol", highest_vol, f"{vol_21d.get(highest_vol, 0):.2%}" if highest_vol != "N/A" else "N/A")

st.plotly_chart(line_chart(prices, "Indexed Cross-Asset Performance (Start = 100)"), use_container_width=True)

left, right = st.columns([1, 1])
with left:
    st.plotly_chart(bar_returns(latest_returns, "Latest Session Return by Asset"), use_container_width=True)
with right:
    if len(returns) > 2 and len(returns.columns) > 1:
        st.plotly_chart(heatmap(returns.corr(), "Return Correlation Matrix"), use_container_width=True)
    else:
        st.info("Correlation requires at least two assets and enough observations.")

st.subheader("Analyst read-through")
if not latest_returns.empty:
    st.write(
        f"The latest session was led by **{best_asset}** and pressured by **{worst_asset}**. "
        f"For an S&T discussion, connect this dispersion to cross-asset drivers: growth risk, rates sensitivity, USD strength, commodity shocks, or volatility repricing."
    )

with st.expander("Raw market data"):
    st.dataframe(prices.tail(20), use_container_width=True)
