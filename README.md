# AI Market Pulse & Risk Briefing Dashboard

An AI-powered cross-asset market monitoring and risk briefing dashboard designed for Sales & Trading use cases.

The project combines market data, portfolio risk analytics, financial news sentiment, and AI-generated market commentary to support risk-aware client conversations.

## Why I Built This

I built this project to better understand how Sales & Trading teams connect market movements, portfolio risk exposure, and client communication. My background is in AI product management and data-driven evaluation systems, and this project explores how similar analytical workflows can be applied to financial markets.

## What It Does

- **Market Overview**: Track equities, rates proxy, FX proxy, commodities, and volatility across a configurable watchlist.
- **Portfolio Risk**: Calculate portfolio return, volatility, maximum drawdown, historical VaR, Expected Shortfall, rolling correlations, and stress-test losses.
- **News Sentiment**: Score financial news headlines and map them to market themes such as inflation, rates, AI, earnings, geopolitics, and risk-off sentiment.
- **AI Morning Brief**: Convert market data and news sentiment into a structured Sales & Trading-style briefing with market overview, risk alerts, and client talking points.

## Demo Use Case

The default portfolio is designed as a cross-asset watchlist:

- Equities: SPY, QQQ, DIA, HSI proxy
- Rates proxy: TLT, IEF
- FX proxy: UUP
- Commodities: GLD, USO
- Volatility: VIX

It answers questions such as:

- What changed across equities, rates, FX, commodities, and volatility?
- Where is the portfolio most exposed to downside risk?
- How do recent headlines map to market sentiment?
- What would a concise client-facing morning brief look like?

## Screens / Pages

1. **Market Overview** – cross-asset performance, volatility, and correlation.
2. **Portfolio Risk** – VaR, Expected Shortfall, drawdown, contribution to risk, and scenario stress testing.
3. **News Sentiment** – headline-level scoring and market theme tagging.
4. **AI Morning Brief** – S&T-style summary generated from market and sentiment signals.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app can run with live Yahoo Finance data through `yfinance`. If live data is unavailable, it falls back to deterministic sample market data so the demo remains reviewable.

## Tech Stack

- Python
- Streamlit
- pandas / numpy
- Plotly
- yfinance
- optional OpenAI-compatible LLM integration via `OPENAI_API_KEY`

## Resume Bullet

```text
Market Risk Briefing Copilot | Personal Project
• Built a Streamlit-based cross-asset market dashboard integrating equity, rates, FX proxy and commodity data to monitor market movements, rolling volatility and asset correlations.
• Developed a portfolio risk module calculating historical VaR, Expected Shortfall, max drawdown and scenario-based stress losses to support risk-aware decision-making.
• Designed an AI briefing module that converts market data and financial news sentiment into structured morning briefs, including market overview, risk alerts and client talking points.
• Added a scheduled GitHub Actions data pipeline to refresh cached market data daily and maintain demo reliability  
when live market APIs are unavailable. 
```

## Disclaimer

This project is for educational and career portfolio purposes only. It is not investment advice and should not be used for live trading decisions.
