from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CACHED_MARKET_DATA_PATH = DATA_DIR / "market_prices.csv"


def generate_sample_prices(tickers: Iterable[str], periods: int = 252, seed: int = 42) -> pd.DataFrame:
    """Generate deterministic sample prices for offline demos."""
    rng = np.random.default_rng(seed)
    tickers = list(tickers)
    end = datetime.today().date()
    dates = pd.bdate_range(end=end, periods=periods)

    base_returns = rng.normal(0.00035, 0.009, size=(periods, 1))
    data = {}
    for idx, ticker in enumerate(tickers):
        beta = 0.5 + (idx % 4) * 0.18
        vol = 0.006 + (idx % 5) * 0.0025
        noise = rng.normal(0, vol, size=periods)
        returns = beta * base_returns[:, 0] + noise
        prices = 100 * np.cumprod(1 + returns)
        data[ticker] = prices
    return pd.DataFrame(data, index=dates)


def load_market_data(tickers: Iterable[str], period: str = "1y") -> tuple[pd.DataFrame, str]:
    """Load adjusted close data from yfinance, then cached GitHub data, then sample data."""
    tickers = [ticker.strip() for ticker in tickers if ticker.strip()]
    if not tickers:
        raise ValueError("At least one ticker is required")

    try:
        import yfinance as yf

        raw = yf.download(tickers, period=period, auto_adjust=True, progress=False, threads=True)
        if raw.empty:
            raise ValueError("empty yfinance response")
        if isinstance(raw.columns, pd.MultiIndex):
            prices = raw.get("Close")
            if prices is None:
                prices = raw.xs("Close", axis=1, level=0)
        else:
            prices = raw[["Close"]].rename(columns={"Close": tickers[0]})
        prices = prices.dropna(how="all").ffill().dropna(axis=1, how="all")
        missing = [ticker for ticker in tickers if ticker not in prices.columns]
        if missing:
            fallback = generate_sample_prices(missing, periods=len(prices))
            fallback.index = prices.index
            prices = pd.concat([prices, fallback], axis=1)
        return prices[tickers], "live_yfinance"
    except Exception:
        cached_prices = load_cached_market_data(tickers, period=period)
        if not cached_prices.empty:
            return cached_prices, "cached_github_data"
        return generate_sample_prices(tickers), "sample_offline"


def load_cached_market_data(tickers: Iterable[str], period: str = "1y") -> pd.DataFrame:
    """Load market prices committed under data/ and trim them to the requested lookback."""
    if not CACHED_MARKET_DATA_PATH.exists():
        return pd.DataFrame()

    tickers = [ticker.strip() for ticker in tickers if ticker.strip()]
    prices = pd.read_csv(CACHED_MARKET_DATA_PATH, parse_dates=["date"]).set_index("date")
    available = [ticker for ticker in tickers if ticker in prices.columns]
    if not available:
        return pd.DataFrame()

    prices = prices[available].dropna(how="all").ffill()
    if prices.empty:
        return pd.DataFrame()

    lookback_days = {"3mo": 92, "6mo": 183, "1y": 366, "2y": 732}.get(period)
    if lookback_days:
        cutoff = prices.index.max() - pd.Timedelta(days=lookback_days)
        prices = prices.loc[prices.index >= cutoff]

    missing = [ticker for ticker in tickers if ticker not in prices.columns]
    if missing:
        fallback = generate_sample_prices(missing, periods=len(prices))
        fallback.index = prices.index
        prices = pd.concat([prices, fallback], axis=1)

    return prices[tickers]


def load_sample_news() -> pd.DataFrame:
    path = DATA_DIR / "sample_news.csv"
    return pd.read_csv(path, parse_dates=["date"])
