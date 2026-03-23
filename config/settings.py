"""
BBTerminal Configuration Settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
FRED_API_KEY = os.getenv("FRED_API_KEY", "")

# Refresh interval in seconds (5-15 minutes)
REFRESH_INTERVAL = 300  # 5 minutes

# Outlier detection thresholds
ZSCORE_THRESHOLD = 2.0  # Flag moves > 2 standard deviations
VOLATILITY_WINDOW = 20  # 20-day rolling volatility

# Equities Configuration
EQUITY_INDICES = {
    "SPY": "S&P 500",
    "QQQ": "Nasdaq 100",
    "IWM": "Russell 2000",
    "^VIX": "Volatility Index",
}

SECTOR_ETFS = {
    "XLE": "Energy",
    "XLF": "Financials",
    "XLK": "Technology",
    "XLV": "Healthcare",
    "XLI": "Industrials",
    "XLP": "Consumer Staples",
    "XLY": "Consumer Discretionary",
    "XLU": "Utilities",
    "XLRE": "Real Estate",
    "XLC": "Communication Services",
}

# Interest Rates (FRED Series IDs)
INTEREST_RATES = {
    "FEDFUNDS": "Fed Funds Rate",
    "GS2": "2Y Treasury",
    "GS5": "5Y Treasury",
    "GS10": "10Y Treasury",
    "GS30": "30Y Treasury",
    "DGS3MO": "3M Treasury",
    "DGS6MO": "6M Treasury",
    "DGS1": "1Y Treasury",
}

# Mortgage Rates (FRED Series IDs)
MORTGAGE_RATES = {
    "MORTGAGE30US": "30Y Fixed Mortgage",
    "MORTGAGE15US": "15Y Fixed Mortgage",
    "MORTGAGE5US": "5/1 ARM",
}

# Commodities (Yahoo Finance Tickers)
COMMODITIES = {
    "CL=F": "Crude Oil",
    "NG=F": "Natural Gas",
    "GC=F": "Gold",
    "SI=F": "Silver",
    "HG=F": "Copper",
    "ZC=F": "Corn",
    "ZW=F": "Wheat",
}

# Economic Data (FRED Series IDs)
ECONOMIC_DATA = {
    "CPIAUCSL": "CPI",
    "UNRATE": "Unemployment Rate",
    "GDP": "GDP",
    "PAYEMS": "Non-Farm Payrolls",
    "PCEPI": "PCE Price Index",
    "RSAFS": "Retail Sales",
}

# Exchange Calendars for Holiday Detection
EXCHANGE_CALENDARS = {
    "US": "XNYS",  # NYSE
    "UK": "XLON",  # London
    "JP": "XTKS",  # Tokyo
    "DE": "XETR",  # Frankfurt
    "HK": "XHKG",  # Hong Kong
    "CN": "XSHG",  # Shanghai
}

