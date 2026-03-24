"""
Economic data fetcher using FRED API
"""
import pandas as pd
import streamlit as st
from typing import Optional
from fredapi import Fred
from .fetcher import DataFetcher
from config.settings import ECONOMIC_DATA, FRED_API_KEY


# Streamlit-cached FRED client - persists across reruns
@st.cache_resource
def _get_fred_client(api_key: str) -> Fred:
    """Get cached FRED client instance."""
    return Fred(api_key=api_key)


# Streamlit-cached function for series data - prevents repeated API calls
# FRED data updates daily/monthly, so cache for 6 hours
@st.cache_data(ttl=21600)
def _fetch_fred_series(series_id: str, _fred: Fred) -> pd.Series:
    """
    Fetch a FRED series.
    Cached by Streamlit to prevent repeated API calls on widget interactions.
    """
    return _fred.get_series(series_id)


class EconomicFetcher(DataFetcher):
    """Fetch economic indicator data from FRED"""

    def __init__(self, cache_duration: int = 300, api_key: str = None):
        super().__init__(cache_duration)
        self.api_key = api_key or FRED_API_KEY
        self._fred = None
        self.series = ECONOMIC_DATA

    @property
    def fred(self) -> Fred:
        """Get FRED client (cached by Streamlit)"""
        if self._fred is None:
            if not self.api_key:
                raise ValueError("FRED API key required. Set FRED_API_KEY in .env file")
            self._fred = _get_fred_client(self.api_key)
        return self._fred

    def get_latest_value(self, series_id: str) -> Optional[dict]:
        """
        Get the latest value for an economic series

        Args:
            series_id: FRED series ID

        Returns:
            Dict with latest value and metadata
        """
        try:
            series = _fetch_fred_series(series_id, self.fred)
            if series is not None and len(series) > 0:
                latest = series.iloc[-1]
                latest_date = series.index[-1]

                # Calculate YoY and MoM changes
                yoy_change = None
                mom_change = None

                if len(series) >= 13:  # At least 12 months for YoY
                    yoy_value = series.iloc[-13]
                    if yoy_value != 0:
                        yoy_change = ((latest - yoy_value) / abs(yoy_value)) * 100

                if len(series) >= 2:
                    prev = series.iloc[-2]
                    if prev != 0:
                        mom_change = ((latest - prev) / abs(prev)) * 100

                return {
                    'series_id': series_id,
                    'name': self.series.get(series_id, series_id),
                    'value': round(latest, 2),
                    'date': latest_date.strftime('%Y-%m-%d'),
                    'yoy_change': round(yoy_change, 2) if yoy_change is not None else None,
                    'mom_change': round(mom_change, 2) if mom_change is not None else None
                }

        except Exception:
            pass

        return None

    def get_all_indicators(self) -> pd.DataFrame:
        """Get latest values for all configured economic series"""
        results = []
        for series_id in self.series.keys():
            data = self.get_latest_value(series_id)
            if data:
                results.append(data)

        return pd.DataFrame(results)

    def get_historical(self, series_id: str, months: int = 12) -> pd.DataFrame:
        """
        Get historical values for an economic series

        Args:
            series_id: FRED series ID
            months: Number of months of history

        Returns:
            DataFrame with date and value columns
        """
        try:
            series = _fetch_fred_series(series_id, self.fred)

            if series is not None:
                # Get last N months
                recent = series.iloc[-months*2:]  # Get more to handle varying frequency

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

    def get_series_info(self, series_id: str) -> dict:
        """Get metadata for a FRED series"""
        try:
            info = self.fred.get_series_info(series_id)
            return info
        except Exception:
            return {}