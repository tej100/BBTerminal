"""
Interest rates data fetcher using FRED API
"""
import pandas as pd
from typing import Optional
from fredapi import Fred
from .fetcher import DataFetcher
from config.settings import INTEREST_RATES, FRED_API_KEY


class RatesFetcher(DataFetcher):
    """Fetch interest rate data from FRED"""

    def __init__(self, cache_duration: int = 300, api_key: str = None):
        super().__init__(cache_duration)
        self.api_key = api_key or FRED_API_KEY
        self._fred = None
        self.series = INTEREST_RATES

    @property
    def fred(self) -> Fred:
        """Lazy load FRED client"""
        if self._fred is None:
            if not self.api_key:
                raise ValueError("FRED API key required. Set FRED_API_KEY in .env file")
            self._fred = Fred(api_key=self.api_key)
        return self._fred

    def get_latest_rate(self, series_id: str) -> Optional[dict]:
        """
        Get the latest rate for a series

        Args:
            series_id: FRED series ID

        Returns:
            Dict with latest rate and metadata
        """
        cache_key = f"rate_latest_{series_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached.to_dict('records')[0] if len(cached) > 0 else None

        try:
            series = self.fred.get_series(series_id)
            if series is not None and len(series) > 0:
                latest = series.iloc[-1]
                latest_date = series.index[-1]

                # Get previous value for change calculation
                if len(series) >= 2:
                    prev = series.iloc[-2]
                    change = latest - prev
                else:
                    change = 0

                result = pd.DataFrame([{
                    'series_id': series_id,
                    'name': self.series.get(series_id, series_id),
                    'value': round(latest, 3),
                    'date': latest_date.strftime('%Y-%m-%d'),
                    'change': round(change, 3) if change else 0
                }])

                self._set_cache(cache_key, result)
                return result.to_dict('records')[0]

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
        Get historical rates for a series

        Args:
            series_id: FRED series ID
            days: Number of days of history

        Returns:
            DataFrame with date and value columns
        """
        cache_key = f"rate_hist_{series_id}_{days}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            series = self.fred.get_series(series_id)

            if series is not None:
                cutoff = series.index[-1] - pd.Timedelta(days=days)
                recent = series[series.index >= cutoff]

                df = pd.DataFrame({
                    'date': recent.index,
                    'value': recent.values
                })
                df['series_id'] = series_id
                df['name'] = self.series.get(series_id, series_id)

                self._set_cache(cache_key, df)
                return df

        except Exception:
            pass

        return pd.DataFrame()

    def get_yield_curve(self) -> pd.DataFrame:
        """
        Get current yield curve data

        Returns:
            DataFrame with maturity and rate columns
        """
        # Treasury yield series ordered by maturity
        yield_series = {
            "DGS3MO": "3M",
            "DGS6MO": "6M",
            "DGS1": "1Y",
            "GS2": "2Y",
            "GS5": "5Y",
            "GS10": "10Y",
            "GS30": "30Y",
        }

        results = []
        for series_id, maturity in yield_series.items():
            rate_data = self.get_latest_rate(series_id)
            if rate_data:
                results.append({
                    'maturity': maturity,
                    'rate': rate_data['value'],
                    'series_id': series_id
                })

        return pd.DataFrame(results)