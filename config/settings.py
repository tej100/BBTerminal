"""
BBTerminal Configuration Settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
FRED_API_KEY = os.getenv("FRED_API_KEY", "")

# Outlier detection thresholds
ZSCORE_THRESHOLD = 1.0  # Flag moves > 1 standard deviations
VOLATILITY_WINDOW = 30  # 30-day rolling volatility

# Equities Configuration
MARKET_SUMMARY_TICKERS = {
    "SPY": "S&P 500",
    "QQQ": "Nasdaq 100",
    "IWM": "Russell 2000",
    "^VIX": "Volatility Index",
    "MBB": "iShares MBS ETF",
    "^N225": "Nikkei 225",
    # Interest Rate Tickers (must end in space " ") for regex matching in market summary rendering
    "^IRX": "13W T-Bill ",
    "^FVX": "5Y Treasury ",
    "^TNX": "10Y Treasury ",
    "^TYX": "30Y Treasury "
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
    "XLB": "Materials",
}

# Mortgage Rates (FRED Series IDs)
MORTGAGE_RATES = {
    "OBMMIC30YF": "30Y Fixed Mortgage",
    "OBMMIC15YF": "15Y Fixed Mortgage",
    "OBMMIJUMBO30YF": "30Y Jumbo Mortgage",
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
    "ZS=F": "Soybeans",
    "OJ=F": "Orange Juice",
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

# Treasury Tenors for Correlation Analysis (Treasury.gov column names)
TREASURY_TENORS = {
    "BC_1MONTH": "1M",
    "BC_2MONTH": "2M",
    "BC_3MONTH": "3M",
    "BC_4MONTH": "4M",
    "BC_6MONTH": "6M",
    "BC_1YEAR": "1Y",
    "BC_2YEAR": "2Y",
    "BC_3YEAR": "3Y",
    "BC_5YEAR": "5Y",
    "BC_7YEAR": "7Y",
    "BC_10YEAR": "10Y",
    "BC_20YEAR": "20Y",
    "BC_30YEAR": "30Y",
}

# KRI Ticker Groups (extensible references for Yahoo Finance tickers)
KRI_TICKER_GROUPS = {
    "MARKET_SUMMARY_TICKERS": MARKET_SUMMARY_TICKERS,
    "SECTOR_ETFS": SECTOR_ETFS,
    "COMMODITIES": COMMODITIES,
}

# KRI Default Parameters
KRI_DEFAULT_LOOKBACK = 30

