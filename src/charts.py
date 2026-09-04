from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def line_chart(prices: pd.DataFrame, title: str):
    normalized = prices / prices.iloc[0] * 100
    fig = px.line(normalized, title=title, labels={"value": "Indexed Price", "index": "Date", "variable": "Asset"})
    fig.update_layout(legend_title_text="Asset")
    return fig


def bar_returns(returns: pd.Series, title: str):
    fig = px.bar(returns.sort_values(), title=title, labels={"value": "Return", "index": "Asset"})
    fig.update_yaxes(tickformat=".2%")
    return fig


def heatmap(corr: pd.DataFrame, title: str):
    fig = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu_r", title=title)
    return fig


def drawdown_chart(portfolio_returns: pd.Series):
    cumulative = (1 + portfolio_returns).cumprod()
    drawdown = cumulative / cumulative.cummax() - 1
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=drawdown.index, y=drawdown, fill="tozeroy", name="Drawdown"))
    fig.update_layout(title="Portfolio Drawdown", yaxis_tickformat=".2%")
    return fig
