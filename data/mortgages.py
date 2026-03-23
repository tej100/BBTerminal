"""
Mortgage rates data fetcher using FRED API
"""
import pandas as pd
import streamlit as st
from typing import Optional
from fredapi import Fred
from .fetcher import DataFetcher
from config.settings import MORTGAGE_RATES, FRED_API_KEY


# Streamlit-cached FRED client - persists across reruns
@st.cache_resource
def _get_fred_client(api_key: str) -> Fred:
    """Get cached FRED client instance."""
    return Fred(api_key=api_key)


# Streamlit-cached function for series data - prevents repeated API calls
# FRED data updates daily, so cache for 6 hours
@st.cache_data(ttl=21600)
def _fetch_fred_series(series_id: str, _fred: Fred) -> pd.Series:
    """
    Fetch a FRED series.
    Cached by Streamlit to prevent repeated API calls on widget interactions.
    """
    return _fred.get_series(series_id)


class MortgagesFetcher(DataFetcher):
    """Fetch mortgage rate data from FRED"""

    def __init__(self, cache_duration: int = 300, api_key: str = None):
        super().__init__(cache_duration)
        self.api_key = api_key or FRED_API_KEY
        self._fred = None
        self.series = MORTGAGE_RATES

    @property
    def fred(self) -> Fred:
        """Get FRED client (cached by Streamlit)"""
        if self._fred is None:
            if not self.api_key:
                raise ValueError("FRED API key required. Set FRED_API_KEY in .env file")
            self._fred = _get_fred_client(self.api_key)
        return self._fred

    def get_latest_rate(self, series_id: str) -> Optional[dict]:
        """
        Get the latest mortgage rate for a series

        Args:
            series_id: FRED series ID

        Returns:
            Dict with latest rate and metadata
        """
        try:
            series = _fetch_fred_series(series_id, self.fred)
            if series is not None and len(series) > 0:
                latest = series.iloc[-1]
                latest_date = series.index[-1]

                if len(series) >= 2:
                    prev = series.iloc[-2]
                    change = latest - prev
                else:
                    change = 0

                return {
                    'series_id': series_id,
                    'name': self.series.get(series_id, series_id),
                    'value': round(latest, 3),
                    'date': latest_date.strftime('%Y-%m-%d'),
                    'change': round(change, 3) if change else 0
                }

        except Exception:
            pass

        return None

    def get_all_rates(self) -> pd.DataFrame:
        """Get latest mortgage rates for all configured series"""
        results = []
        for series_id in self.series.keys():
            rate_data = self.get_latest_rate(series_id)
            if rate_data:
                results.append(rate_data)

        return pd.DataFrame(results)

    def get_historical_rates(self, series_id: str, days: int = 30) -> pd.DataFrame:
        """
        Get historical mortgage rates for a series

        Args:
            series_id: FRED series ID
            days: Number of days of history

        Returns:
            DataFrame with date and value columns
        """
        try:
            series = _fetch_fred_series(series_id, self.fred)

            if series is not None:
                cutoff = series.index[-1] - pd.Timedelta(days=days)
                recent = series[series.index >= cutoff]

                df = pd.DataFrame({
                    'date': recent.index,
                    'value': recent.values
                })
                df['series_id'] = series_id
                df['name'] = self.series.get(series_id, series_id)

                return df

        except Exception:
            pass

        return pd.DataFrame()

    def get_spread_to_10y(self) -> pd.DataFrame:
        """
        Calculate mortgage spread to 10Y Treasury

        Returns:
            DataFrame with mortgage spreads
        """
        from .rates import RatesFetcher

        rates_fetcher = RatesFetcher()
        ten_year = rates_fetcher.get_latest_rate("GS10")

        if not ten_year:
            return pd.DataFrame()

        mortgage_rates = self.get_all_rates()
        if mortgage_rates.empty:
            return pd.DataFrame()

        mortgage_rates['spread'] = mortgage_rates['value'] - ten_year['value']
        return mortgage_rates