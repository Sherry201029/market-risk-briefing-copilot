from __future__ import annotations

import pandas as pd


def _pct(value: float) -> str:
    return f"{value:.2%}"


def generate_rule_based_brief(
    prices: pd.DataFrame,
    risk_summary: dict[str, float],
    sentiment_summary: dict[str, object],
    stress_results: pd.DataFrame,
) -> str:
    returns = prices.pct_change().dropna()
    latest = returns.iloc[-1].sort_values() if not returns.empty else pd.Series(dtype=float)
    weakest = latest.head(2)
    strongest = latest.tail(2).sort_values(ascending=False)
    worst_stress = stress_results.sort_values("Portfolio Shock").head(1).iloc[0]

    sentiment_score = float(sentiment_summary.get("average_sentiment", 0.0))
    if sentiment_score > 0.15:
        tone = "constructive"
    elif sentiment_score < -0.15:
        tone = "cautious"
    else:
        tone = "balanced"

    return f"""
### Morning Market Brief

**Market tone:** The cross-asset setup looks **{tone}** based on recent price action and headline sentiment.

**Cross-asset moves:** The strongest assets in the latest session were {', '.join([f'{k} ({_pct(v)})' for k, v in strongest.items()]) or 'N/A'}, while the weakest were {', '.join([f'{k} ({_pct(v)})' for k, v in weakest.items()]) or 'N/A'}.

**Risk signals:** The portfolio's annualized volatility is {_pct(risk_summary['Annualized Volatility'])}, with 95% historical VaR of {_pct(risk_summary['Historical VaR 95%'])} and Expected Shortfall of {_pct(risk_summary['Expected Shortfall 95%'])}. Maximum drawdown over the lookback window is {_pct(risk_summary['Max Drawdown'])}.

**Stress scenario:** The most severe predefined scenario is **{worst_stress['Scenario']}**, implying an estimated portfolio shock of {_pct(worst_stress['Portfolio Shock'])}.

**Client talking points:**
1. Explain whether equity weakness is broad-based or concentrated in growth/technology exposure.
2. Watch rates-sensitive assets because a yield shock can pressure long-duration equities and fixed-income proxies at the same time.
3. Connect headline sentiment with observed market moves before turning it into a client view.
4. Frame any opportunity together with risk controls: VaR, drawdown, correlation, and scenario loss.
""".strip()
