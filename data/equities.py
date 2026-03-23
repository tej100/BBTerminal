"""
Equities data fetcher using yfinance
"""
import yfinance as yf
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional
from .fetcher import DataFetcher
from config.settings import EQUITY_INDICES, SECTOR_ETFS


# Streamlit-cached functions for API calls - persist across page reruns
@st.cache_data(ttl=300)
def _fetch_prices_data(tickers: tuple) -> pd.DataFrame:
    """
    Fetch price data from yfinance.
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
def _fetch_historical(ticker: str, period: str) -> pd.DataFrame:
    """
    Fetch historical data for a single ticker.
    Cached by Streamlit.
    """
    try:
        stock = yf.Ticker(ticker)
        return stock.history(period=period, auto_adjust=True)
    except Exception:
        return pd.DataFrame()


class EquitiesFetcher(DataFetcher):
    """Fetch equity market data from Yahoo Finance"""

    def __init__(self, cache_duration: int = 300):
        super().__init__(cache_duration)
        self.indices = EQUITY_INDICES
        self.sectors = SECTOR_ETFS

    def get_all_tickers(self) -> List[str]:
        """Get all equity tickers"""
        return list(self.indices.keys()) + list(self.sectors.keys())

    def get_current_prices(self, tickers: List[str]) -> pd.DataFrame:
        """
        Get current prices with daily, weekly, monthly changes for given tickers

        Args:
            tickers: List of ticker symbols

        Returns:
            DataFrame with price, change_pct (daily), weekly_pct, monthly_pct columns
        """
        try:
            # Use Streamlit-cached function for API call
            data = _fetch_prices_data(tuple(sorted(tickers)))

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
                        'name': self._get_name(ticker),
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
        Get historical data for a single ticker

        Args:
            ticker: Ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y)

        Returns:
            DataFrame with OHLCV data
        """
        return _fetch_historical(ticker, period)

    def get_corporate_actions(self, ticker: str, days: int = 30) -> pd.DataFrame:
        """
        Get recent corporate actions (dividends, splits)

        Args:
            ticker: Ticker symbol
            days: Number of days to look back

        Returns:
            DataFrame with corporate actions
        """
        try:
            stock = yf.Ticker(ticker)
            actions = stock.actions

            if actions is not None and len(actions) > 0:
                # Filter to recent days
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
                recent = actions[actions.index >= cutoff]
                return recent

            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def get_info(self, ticker: str) -> Dict:
        """Get basic company info"""
        try:
            stock = yf.Ticker(ticker)
            return stock.info
        except Exception:
            return {}

    def _get_name(self, ticker: str) -> str:
        """Get display name for ticker"""
        if ticker in self.indices:
            return self.indices[ticker]
        if ticker in self.sectors:
            return self.sectors[ticker]
        return ticker

    def get_sector_performance(self) -> pd.DataFrame:
        """Get performance data for all sector ETFs"""
        tickers = list(self.sectors.keys())
        return self.get_current_prices(tickers)

    def get_indices_performance(self) -> pd.DataFrame:
        """Get performance data for major indices"""
        tickers = list(self.indices.keys())
        return self.get_current_prices(tickers)