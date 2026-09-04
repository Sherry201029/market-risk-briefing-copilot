import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import load_sample_news
from src.sentiment import enrich_news, score_headline, sentiment_label, sentiment_summary, tag_themes


st.set_page_config(page_title="News Sentiment", page_icon="🧭", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: radial-gradient(circle at top left, rgba(37,99,235,0.30), transparent 28%), #08111f; }
    [data-testid="stMetric"] { border: 1px solid rgba(125,211,252,0.18); border-radius: 18px; padding: 18px; background: rgba(15,23,42,0.72); }
    .headline-box { padding: 0.9rem 1rem; border-radius: 16px; border: 1px solid rgba(125,211,252,0.22); background: rgba(125,211,252,0.07); }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("🧭 Financial News Sentiment Radar")
st.caption("Score headlines, tag market themes, and convert unstructured news flow into an analyst-friendly signal layer.")

sample_news = load_sample_news()

with st.sidebar:
    st.header("Headline Input")
    mode = st.radio("News source", ["Built-in sample headlines", "Paste custom headlines"])
    custom_text = ""
    if mode == "Paste custom headlines":
        custom_text = st.text_area(
            "One headline per line",
            height=220,
            placeholder="Treasury yields rise as inflation data surprises to the upside\nAI chipmakers rally after stronger cloud capex guidance",
        )

if mode == "Paste custom headlines" and custom_text.strip():
    rows = [line.strip() for line in custom_text.splitlines() if line.strip()]
    news = pd.DataFrame({"date": pd.Timestamp.today().normalize(), "headline": rows, "source": "Custom Input"})
else:
    news = sample_news

enriched = enrich_news(news)
summary = sentiment_summary(news)

positive_count = summary["label_counts"].get("Positive", 0)
neutral_count = summary["label_counts"].get("Neutral", 0)
negative_count = summary["label_counts"].get("Negative", 0)
avg_score = float(summary["average_sentiment"])

cols = st.columns(4)
cols[0].metric("Average sentiment", f"{avg_score:+.2f}")
cols[1].metric("Positive headlines", positive_count)
cols[2].metric("Neutral headlines", neutral_count)
cols[3].metric("Negative headlines", negative_count)

left, right = st.columns([1, 1])
with left:
    count_df = enriched["sentiment"].value_counts().rename_axis("Sentiment").reset_index(name="Count")
    fig = px.bar(count_df, x="Sentiment", y="Count", color="Sentiment", title="Headline Sentiment Distribution")
    st.plotly_chart(fig, use_container_width=True)
with right:
    theme_df = enriched.assign(themes=enriched["themes"].str.split(", ")).explode("themes")
    theme_counts = theme_df["themes"].value_counts().rename_axis("Theme").reset_index(name="Count")
    fig = px.bar(theme_counts, x="Count", y="Theme", orientation="h", title="Market Themes Mentioned")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Headline-level signal table")
display = enriched.copy()
display["sentiment_score"] = display["sentiment_score"].map(lambda x: f"{x:+.2f}")
st.dataframe(display, use_container_width=True, hide_index=True)

st.subheader("Try a single headline")
headline = st.text_input("Headline", "Dollar strengthens while gold rallies in risk-off trading session")
if headline:
    score = score_headline(headline)
    st.markdown(
        f"<div class='headline-box'><b>Score:</b> {score:+.2f} · <b>Label:</b> {sentiment_label(score)} · <b>Themes:</b> {tag_themes(headline)}</div>",
        unsafe_allow_html=True,
    )

st.info("The first version intentionally uses transparent rule-based scoring so interviewers can inspect the logic. It can later be swapped for FinBERT or an LLM classifier without changing the dashboard workflow.")
