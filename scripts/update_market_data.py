from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import DEFAULT_TICKERS
from src.data_loader import generate_sample_prices


DATA_DIR = ROOT / "data"
PRICES_PATH = DATA_DIR / "market_prices.csv"
METADATA_PATH = DATA_DIR / "market_metadata.json"


def download_prices(tickers: list[str], period: str = "2y") -> tuple[pd.DataFrame, str]:
    """Download adjusted close prices and fall back to deterministic demo data if needed."""
    try:
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
    except Exception as exc:  # pragma: no cover - intended network fallback
        prices = generate_sample_prices(tickers, periods=504)
        return prices, f"sample_offline: {exc}"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tickers = list(DEFAULT_TICKERS.keys())
    prices, source = download_prices(tickers)
    prices = prices.reset_index().rename(columns={"index": "date", "Date": "date"})
    prices["date"] = pd.to_datetime(prices["date"]).dt.strftime("%Y-%m-%d")
    prices.to_csv(PRICES_PATH, index=False)

    metadata = {
        "updated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": source,
        "tickers": tickers,
        "rows": int(len(prices)),
        "start_date": str(prices["date"].min()),
        "end_date": str(prices["date"].max()),
        "purpose": "Daily cached market data for the AI Market Pulse & Risk Briefing Dashboard.",
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Updated {PRICES_PATH} with {len(prices)} rows from {source}.")


if __name__ == "__main__":
    main()
