from __future__ import annotations

import re

import pandas as pd


POSITIVE_TERMS = {
    "beat", "beats", "rally", "gain", "gains", "strong", "growth", "cooling", "cut", "cuts",
    "optimism", "resilient", "upgrade", "surge", "rebound", "easing", "soft landing",
}
NEGATIVE_TERMS = {
    "miss", "falls", "fall", "drop", "drops", "selloff", "sell-off", "risk", "inflation", "hotter",
    "hike", "recession", "default", "war", "conflict", "downgrade", "weak", "volatility", "hawkish",
}

THEME_KEYWORDS = {
    "Rates": ["fed", "rate", "yield", "treasury", "inflation", "cpi", "central bank"],
    "Equities": ["equity", "stock", "earnings", "nasdaq", "s&p", "ai stocks", "tech"],
    "FX": ["dollar", "usd", "currency", "fx"],
    "Commodities": ["oil", "gold", "commodity", "energy"],
    "Credit/Risk": ["credit", "spread", "default", "risk", "volatility", "vix"],
    "AI/Technology": ["ai", "semiconductor", "chips", "cloud", "data center"],
}


def score_headline(text: str) -> float:
    lower = text.lower()
    score = 0
    for term in POSITIVE_TERMS:
        if term in lower:
            score += 1
    for term in NEGATIVE_TERMS:
        if term in lower:
            score -= 1
    return max(min(score / 3, 1.0), -1.0)


def sentiment_label(score: float) -> str:
    if score > 0.15:
        return "Positive"
    if score < -0.15:
        return "Negative"
    return "Neutral"


def tag_themes(text: str) -> str:
    lower = text.lower()
    tags = [theme for theme, words in THEME_KEYWORDS.items() if any(re.search(rf"\b{re.escape(word)}\b", lower) for word in words)]
    return ", ".join(tags) if tags else "General Market"


def enrich_news(news: pd.DataFrame) -> pd.DataFrame:
    result = news.copy()
    result["sentiment_score"] = result["headline"].map(score_headline)
    result["sentiment"] = result["sentiment_score"].map(sentiment_label)
    result["themes"] = result["headline"].map(tag_themes)
    return result


def sentiment_summary(news: pd.DataFrame) -> dict[str, object]:
    enriched = enrich_news(news)
    avg = float(enriched["sentiment_score"].mean()) if not enriched.empty else 0.0
    counts = enriched["sentiment"].value_counts().to_dict()
    top_negative = enriched.sort_values("sentiment_score").head(3)["headline"].tolist()
    top_positive = enriched.sort_values("sentiment_score", ascending=False).head(3)["headline"].tolist()
    return {
        "average_sentiment": avg,
        "label_counts": counts,
        "top_negative": top_negative,
        "top_positive": top_positive,
    }
