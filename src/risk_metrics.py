from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna(how="all")


def normalize_weights(weights: dict[str, float], columns: list[str]) -> pd.Series:
    selected = pd.Series({ticker: float(weights.get(ticker, 0.0)) for ticker in columns})
    if selected.sum() == 0:
        selected[:] = 1 / len(selected)
    return selected / selected.sum()


def portfolio_returns(returns: pd.DataFrame, weights: pd.Series) -> pd.Series:
    aligned = weights.reindex(returns.columns).fillna(0.0)
    return returns.fillna(0.0).dot(aligned)


def max_drawdown(return_series: pd.Series) -> float:
    cumulative = (1 + return_series).cumprod()
    running_max = cumulative.cummax()
    drawdown = cumulative / running_max - 1
    return float(drawdown.min())


def historical_var(return_series: pd.Series, confidence: float = 0.95) -> float:
    return float(-np.quantile(return_series.dropna(), 1 - confidence))


def expected_shortfall(return_series: pd.Series, confidence: float = 0.95) -> float:
    var_threshold = np.quantile(return_series.dropna(), 1 - confidence)
    tail = return_series[return_series <= var_threshold]
    return float(-tail.mean()) if not tail.empty else float("nan")


def annualized_volatility(return_series: pd.Series) -> float:
    return float(return_series.std() * np.sqrt(TRADING_DAYS))


def annualized_return(return_series: pd.Series) -> float:
    if return_series.empty:
        return 0.0
    cumulative = (1 + return_series).prod()
    years = len(return_series) / TRADING_DAYS
    return float(cumulative ** (1 / years) - 1) if years > 0 else 0.0


def risk_summary(portfolio_ret: pd.Series) -> dict[str, float]:
    return {
        "Annualized Return": annualized_return(portfolio_ret),
        "Annualized Volatility": annualized_volatility(portfolio_ret),
        "Max Drawdown": max_drawdown(portfolio_ret),
        "Historical VaR 95%": historical_var(portfolio_ret, 0.95),
        "Expected Shortfall 95%": expected_shortfall(portfolio_ret, 0.95),
    }


def stress_test(weights: pd.Series, scenarios: dict[str, dict[str, float]]) -> pd.DataFrame:
    rows = []
    for name, shocks in scenarios.items():
        loss = sum(weights.get(ticker, 0.0) * shocks.get(ticker, 0.0) for ticker in weights.index)
        rows.append({"Scenario": name, "Portfolio Shock": loss})
    return pd.DataFrame(rows)


def contribution_to_risk(returns: pd.DataFrame, weights: pd.Series) -> pd.DataFrame:
    cov = returns.cov() * TRADING_DAYS
    aligned = weights.reindex(returns.columns).fillna(0.0)
    port_var = float(aligned.T @ cov @ aligned)
    if port_var <= 0:
        return pd.DataFrame({"Asset": returns.columns, "Contribution": 0.0})
    marginal = cov @ aligned
    contribution = aligned * marginal / port_var
    return contribution.rename("Contribution").reset_index().rename(columns={"index": "Asset"})
