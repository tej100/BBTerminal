"""
Generic Yahoo Finance data fetcher
"""
import yfinance as yf
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional
from .fetcher import DataFetcher


# Streamlit-cached functions for API calls - persist across page reruns
@st.cache_data(ttl=300)
def _fetch_yfinance_data(tickers: tuple) -> pd.DataFrame:
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
def _fetch_yfinance_historical(ticker: str, period: str) -> pd.DataFrame:
    """
    Fetch historical data for a single ticker.
    Cached by Streamlit.
    """
    try:
        asset = yf.Ticker(ticker)
        return asset.history(period=period, auto_adjust=True)
    except Exception:
        return pd.DataFrame()


class YahooFinanceFetcher(DataFetcher):
    """
    Generic fetcher for Yahoo Finance data (equities, commodities, etc.)

    Args:
        tickers_config: Dictionary mapping ticker symbols to display names
        cache_duration: Cache duration in seconds (default 5 minutes)
    """

    def __init__(self, tickers_config: Dict[str, str], cache_duration: int = 300):
        super().__init__(cache_duration)
        self.tickers_config = tickers_config
        self.tickers = list(tickers_config.keys())

    def get_current_prices(self) -> pd.DataFrame:
        """
        Get current prices with daily, weekly, monthly changes for given tickers

        Args:
            tickers: List of ticker symbols (default: all configured tickers)

        Returns:
            DataFrame with price, change_pct (daily), weekly_pct, monthly_pct columns
        """

        try:
            # Use Streamlit-cached function for API call
            data = _fetch_yfinance_data(tuple(sorted(self.tickers)))

            if data.empty:
                return pd.DataFrame()

            results = []
            for ticker in self.tickers:
                try:
                    # Handle MultiIndex columns from yfinance
                    if len(self.tickers) == 1:
                        close_prices = data.xs('Close', level='Price', axis=1).iloc[:, 0]
                    else:
                        close_prices = data[ticker]['Close']

                    if len(close_prices) < 2:
                        continue

                    last_close = close_prices.iloc[-1]
                    latest_date = close_prices.index[-1]

                    # Daily change (vs previous available data point)
                    daily_pct = 0
                    if len(close_prices) >= 2:
                        prev_close = close_prices.iloc[-2]
                        daily_pct = ((last_close - prev_close) / prev_close) * 100

                    # Weekly change: value as of ~7 days before latest, using latest available before that date
                    weekly_pct = None
                    weekly_target_date = latest_date - pd.DateOffset(weeks=1)
                    weekly_candidates = close_prices[close_prices.index <= weekly_target_date]
                    if not weekly_candidates.empty:
                        week_ago = weekly_candidates.iloc[-1]
                        weekly_pct = ((last_close - week_ago) / week_ago) * 100

                    # Monthly change: value as of ~1 month before latest, using latest available before that date
                    monthly_pct = None
                    monthly_target_date = latest_date - pd.DateOffset(months=1)
                    monthly_candidates = close_prices[close_prices.index <= monthly_target_date]
                    if not monthly_candidates.empty:
                        month_ago = monthly_candidates.iloc[-1]
                        monthly_pct = ((last_close - month_ago) / month_ago) * 100

                    results.append({
                        'ticker': ticker,
                        'name': self.tickers_config.get(ticker, ticker),
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
        return _fetch_yfinance_historical(ticker, period)

    def get_info(self, ticker: str) -> Dict:
        """Get basic asset info"""
        try:
            asset = yf.Ticker(ticker)
            return asset.info
        except Exception:
            return {}