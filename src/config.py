DEFAULT_TICKERS = {
    "SPY": "US Equities - S&P 500 ETF",
    "QQQ": "US Growth Equities - Nasdaq 100 ETF",
    "DIA": "US Blue Chips - Dow ETF",
    "EWH": "Hong Kong Equities ETF",
    "TLT": "Long-duration US Treasury ETF",
    "IEF": "Intermediate US Treasury ETF",
    "UUP": "US Dollar Index Proxy ETF",
    "GLD": "Gold ETF",
    "USO": "Oil ETF",
    "^VIX": "CBOE Volatility Index",
}

DEFAULT_WEIGHTS = {
    "SPY": 0.20,
    "QQQ": 0.20,
    "EWH": 0.10,
    "TLT": 0.15,
    "IEF": 0.10,
    "UUP": 0.10,
    "GLD": 0.10,
    "USO": 0.05,
}

STRESS_SCENARIOS = {
    "Equity sell-off": {
        "SPY": -0.05,
        "QQQ": -0.07,
        "DIA": -0.04,
        "EWH": -0.06,
        "TLT": 0.02,
        "IEF": 0.01,
        "UUP": 0.015,
        "GLD": 0.02,
        "USO": -0.03,
    },
    "Rates shock": {
        "SPY": -0.025,
        "QQQ": -0.045,
        "DIA": -0.015,
        "EWH": -0.025,
        "TLT": -0.06,
        "IEF": -0.025,
        "UUP": 0.02,
        "GLD": -0.015,
        "USO": 0.005,
    },
    "Risk-off / geopolitical shock": {
        "SPY": -0.04,
        "QQQ": -0.05,
        "DIA": -0.035,
        "EWH": -0.045,
        "TLT": 0.03,
        "IEF": 0.015,
        "UUP": 0.02,
        "GLD": 0.04,
        "USO": 0.05,
    },
}
