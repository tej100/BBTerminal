"""
Generic FRED API data fetcher with configurable series list and cache duration
"""
import pandas as pd
import streamlit as st
from typing import Optional, Dict
from fredapi import Fred
from .fetcher import DataFetcher
from config.settings import FRED_API_KEY


# Streamlit-cached FRED client - persists across reruns
@st.cache_resource
def _get_fred_client(api_key: str) -> Fred:
    """Get cached FRED client instance."""
    return Fred(api_key=api_key)


# Streamlit-cached function for series data - prevents repeated API calls
# FRED data updates daily, so cache for 24 hours
@st.cache_data(ttl=86400)
def _fetch_fred_series(series_id: str, _fred: Fred) -> pd.Series:
    """
    Fetch a FRED series.
    Cached by Streamlit to prevent repeated API calls on widget interactions.
    FRED data updates daily, so cache is set to 24 hours.
    """
    return _fred.get_series(series_id)


class FredFetcher(DataFetcher):
    """Generic FRED data fetcher with configurable series list"""

    def __init__(self, series_dict: Dict[str, str], cache_duration: int = 86400):
        """
        Initialize FredFetcher with a series dictionary.

        Args:
            series_dict: Dictionary mapping series_id -> display_name
                        (e.g., {"MORTGAGE30US": "30Y Fixed Mortgage"})
            cache_duration: Cache duration in seconds (default 86400 = 24 hours)
            api_key: FRED API key (uses FRED_API_KEY from settings if not provided)
        """
        super().__init__(cache_duration)
        self.api_key = FRED_API_KEY
        self._fred = None
        self.series = series_dict

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
        Get the latest rate for a series with daily, weekly, and monthly changes.

        Args:
            series_id: FRED series ID

        Returns:
            Dict with latest rate and metadata, or None if unavailable
        """
        try:
            series = _fetch_fred_series(series_id, self.fred)
            if series is not None and len(series) > 0:
                latest = series.iloc[-1]
                latest_date = series.index[-1]

                # Daily change: previous available data point
                daily_change = 0
                if len(series) >= 2:
                    daily_change = latest - series.iloc[-2]

                # Weekly change: value as of ~7 days before latest, using latest available before that date
                weekly_change = 0
                weekly_target_date = latest_date - pd.DateOffset(weeks=1)
                weekly_candidates = series[series.index <= weekly_target_date]
                if not weekly_candidates.empty:
                    weekly_value = weekly_candidates.iloc[-1]
                    weekly_change = latest - weekly_value

                # Monthly change: value as of ~1 month before latest, using latest available before that date
                monthly_change = 0
                monthly_target_date = latest_date - pd.DateOffset(months=1)
                monthly_candidates = series[series.index <= monthly_target_date]
                if not monthly_candidates.empty:
                    monthly_value = monthly_candidates.iloc[-1]
                    monthly_change = latest - monthly_value

                return {
                    'series_id': series_id,
                    'name': self.series.get(series_id, series_id),
                    'value': round(latest, 3),
                    'date': latest_date.strftime('%Y-%m-%d'),
                    'daily': round(daily_change, 3) if daily_change else pd.NA,
                    'weekly': round(weekly_change, 3) if weekly_change else pd.NA,
                    'monthly': round(monthly_change, 3) if monthly_change else pd.NA
                }

        except Exception:
            pass

        return None

    def get_all_rates(self) -> pd.DataFrame:
        """Get latest rates for all configured series"""
        results = []
        for series_id in self.series.keys():
            rate_data = self.get_latest_rate(series_id)
            if rate_data:
                results.append(rate_data)

        return pd.DataFrame(results)

    def get_historical_rates(self, series_id: str, days: int = 30) -> pd.DataFrame:
        """
        Get historical rates for a series.

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
