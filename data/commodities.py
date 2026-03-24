"""
Commodities data fetcher using yfinance
"""
import yfinance as yf
import pandas as pd
import streamlit as st
from typing import List
from .fetcher import DataFetcher
from config.settings import COMMODITIES


# Streamlit-cached functions for API calls - persist across page reruns
@st.cache_data(ttl=300)
def _fetch_commodities_data(tickers: tuple) -> pd.DataFrame:
    """
    Fetch commodity price data from yfinance.
    Cached by Streamlit to prevent repeated API calls on widget interactions.
    tickers must be a tuple (hashable) for caching.
    """
    try:
        data = yf.download(
            list(tickers),
            period="1mo",
            progress=False,
            group_by="ticker",
            auto_adjust=True
        )
        return data
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def _fetch_commodity_historical(ticker: str, period: str) -> pd.DataFrame:
    """
    Fetch historical data for a commodity.
    Cached by Streamlit.
    """
    try:
        commodity = yf.Ticker(ticker)
        return commodity.history(period=period, auto_adjust=True)
    except Exception:
        return pd.DataFrame()


class CommoditiesFetcher(DataFetcher):
    """Fetch commodity futures data from Yahoo Finance"""

    def __init__(self, cache_duration: int = 300):
        super().__init__(cache_duration)
        self.commodities = COMMODITIES

    def get_all_tickers(self) -> List[str]:
        """Get all commodity ticker symbols"""
        return list(self.commodities.keys())

    def get_current_prices(self, tickers: List[str] = None) -> pd.DataFrame:
        """
        Get current prices with daily, weekly, monthly changes for commodities

        Args:
            tickers: List of ticker symbols (default: all commodities)

        Returns:
            DataFrame with price, change_pct (daily), weekly_pct, monthly_pct columns
        """
        if tickers is None:
            tickers = self.get_all_tickers()

        try:
            # Use Streamlit-cached function for API call
            data = _fetch_commodities_data(tuple(sorted(tickers)))

            if data.empty:
                return pd.DataFrame()

            results = []
            for ticker in tickers:
                try:
                    # Handle MultiIndex columns from yfinance
                    if len(tickers) == 1:
                        close_prices = data.xs('Close', level='Price', axis=1).iloc[:, 0]
                    else:
                        close_prices = data[ticker]['Close']

                    if len(close_prices) < 2:
                        continue

                    last_close = close_prices.iloc[-1]

                    # Daily change (vs previous close)
                    prev_close = close_prices.iloc[-2]
                    daily_pct = ((last_close - prev_close) / prev_close) * 100

                    # Weekly change (vs 5 trading days ago)
                    if len(close_prices) >= 5:
                        week_ago = close_prices.iloc[-5]
                        weekly_pct = ((last_close - week_ago) / week_ago) * 100
                    else:
                        weekly_pct = None

                    # Monthly change (vs 20 trading days ago or earliest available)
                    if len(close_prices) >= 20:
                        month_ago = close_prices.iloc[-20]
                        monthly_pct = ((last_close - month_ago) / month_ago) * 100
                    else:
                        # Use earliest available
                        month_ago = close_prices.iloc[0]
                        monthly_pct = ((last_close - month_ago) / month_ago) * 100

                    results.append({
                        'ticker': ticker,
                        'name': self.commodities.get(ticker, ticker),
                        'price': round(last_close, 2),
                        'change': round(last_close - prev_close, 2),
                        'change_pct': round(daily_pct, 2),
                        'weekly_pct': round(weekly_pct, 2) if weekly_pct is not None else None,
                        'monthly_pct': round(monthly_pct, 2) if monthly_pct is not None else None
                    })
                except Exception:
                    continue

            return pd.DataFrame(results)

        except Exception:
            return pd.DataFrame()

    def get_historical(self, ticker: str, period: str = "1mo") -> pd.DataFrame:
        """
        Get historical data for a commodity

        Args:
            ticker: Commodity ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y)

        Returns:
            DataFrame with OHLCV data
        """
        return _fetch_commodity_historical(ticker, period)

    def get_contract_info(self, ticker: str) -> dict:
        """Get contract info for a commodity"""
        try:
            commodity = yf.Ticker(ticker)
            return commodity.info
        except Exception:
            return {}