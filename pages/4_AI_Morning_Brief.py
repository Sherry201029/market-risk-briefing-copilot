import pandas as pd
import streamlit as st

from src.briefing_generator import generate_rule_based_brief
from src.config import DEFAULT_TICKERS, DEFAULT_WEIGHTS, STRESS_SCENARIOS
from src.data_loader import load_market_data, load_sample_news
from src.risk_metrics import daily_returns, normalize_weights, portfolio_returns, risk_summary, stress_test
from src.sentiment import sentiment_summary


st.set_page_config(page_title="AI Morning Brief", page_icon="🗞️", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(160deg, #07111f 0%, #0e1726 48%, #13251e 100%); }
    .brief-shell { border: 1px solid rgba(167,243,208,0.18); border-radius: 24px; padding: 1.2rem 1.4rem; background: rgba(6,95,70,0.11); }
    [data-testid="stMetric"] { border-radius: 18px; border: 1px solid rgba(167,243,208,0.18); background: rgba(255,255,255,0.055); padding: 18px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=900)
def cached_market_data(tickers: tuple[str, ...], period: str) -> tuple[pd.DataFrame, str]:
    return load_market_data(tickers, period=period)


st.title("🗞️ AI Morning Brief Generator")
st.caption("Combine market moves, portfolio risk, stress scenarios, and news sentiment into a concise client-facing S&T brief.")

with st.sidebar:
    st.header("Brief Controls")
    period = st.selectbox("Market lookback", ["6mo", "1y", "2y"], index=1)
    tickers = st.multiselect(
        "Assets in brief",
        options=[ticker for ticker in DEFAULT_TICKERS if ticker != "^VIX"],
        default=list(DEFAULT_WEIGHTS.keys()),
        format_func=lambda ticker: f"{ticker} — {DEFAULT_TICKERS[ticker]}",
    )
    tone_override = st.selectbox("Audience framing", ["Client-ready", "Internal risk huddle", "Interview walkthrough"], index=0)

if not tickers:
    st.warning("Select at least one asset to generate the brief.")
    st.stop()

prices, source = cached_market_data(tuple(tickers), period)
returns = daily_returns(prices)
weights = normalize_weights(DEFAULT_WEIGHTS, list(returns.columns))
port_ret = portfolio_returns(returns, weights)
risk = risk_summary(port_ret)
stress = stress_test(weights, STRESS_SCENARIOS)
news_summary = sentiment_summary(load_sample_news())
brief = generate_rule_based_brief(prices, risk, news_summary, stress)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Data mode", source)
col2.metric("Portfolio VaR 95%", f"{risk['Historical VaR 95%']:.2%}")
col3.metric("Expected Shortfall", f"{risk['Expected Shortfall 95%']:.2%}")
col4.metric("Headline sentiment", f"{float(news_summary['average_sentiment']):+.2f}")

st.subheader("Generated brief")
st.markdown("<div class='brief-shell'>", unsafe_allow_html=True)
st.markdown(brief)
st.markdown("</div>", unsafe_allow_html=True)

st.subheader("How to explain this project in a Goldman Sachs S&T interview")
if tone_override == "Client-ready":
    st.write(
        "I designed the output to sound like a junior analyst preparing a morning note: concise market tone, key cross-asset moves, risk metrics, stress loss, and practical client talking points."
    )
elif tone_override == "Internal risk huddle":
    st.write(
        "I would use the dashboard internally to separate signal from noise: what moved, where the portfolio is exposed, and which stress scenario deserves attention before speaking with clients."
    )
else:
    st.write(
        "The project connects my AI/data product background to markets: I structured messy data into an evaluation workflow, made the logic inspectable, and turned outputs into communication-ready insight."
    )

with st.expander("Underlying risk inputs"):
    st.json({k: f"{v:.2%}" for k, v in risk.items()})
    st.dataframe(stress, use_container_width=True, hide_index=True)
