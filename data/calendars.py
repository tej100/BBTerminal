"""
Holiday calendar and corporate actions fetcher
"""
import pandas as pd
from datetime import date, timedelta
from typing import Dict, List, Optional
import pandas_market_calendars as mcal
from .fetcher import DataFetcher
from config.settings import EXCHANGE_CALENDARS
import yfinance as yf


class CalendarFetcher(DataFetcher):
    """Fetch holiday calendars and corporate actions"""

    def __init__(self, cache_duration: int = 3600):  # 1 hour cache for calendars
        super().__init__(cache_duration)
        self.calendars = EXCHANGE_CALENDARS

    def get_todays_holidays(self) -> pd.DataFrame:
        """
        Get all holidays occurring today across tracked exchanges

        Returns:
            DataFrame with exchange, region, and holiday name
        """
        today = date.today()
        cache_key = "holidays_today"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        results = []
        for region, exchange_code in self.calendars.items():
            try:
                cal = mcal.get_calendar(exchange_code)
                # Get holidays for today's year
                start = today.replace(month=1, day=1)
                end = today.replace(month=12, day=31)

                schedule = cal.schedule(start_date=start, end_date=end)
                holidays = cal.holidays()

                # Check if today is a holiday
                if hasattr(holidays, 'holidays'):
                    holiday_dates = holidays.holidays
                    for h in holiday_dates:
                        if hasattr(h, 'date'):
                            h_date = h.date()
                        else:
                            h_date = pd.to_datetime(h).date()

                        if h_date == today:
                            results.append({
                                'region': region,
                                'exchange': exchange_code,
                                'holiday': str(h),
                                'date': today
                            })

            except Exception:
                continue

        result_df = pd.DataFrame(results)
        self._set_cache(cache_key, result_df)
        return result_df

    def get_upcoming_holidays(self, days: int = 30) -> pd.DataFrame:
        """
        Get upcoming holidays for all tracked exchanges

        Args:
            days: Number of days to look ahead

        Returns:
            DataFrame with upcoming holidays
        """
        cache_key = f"holidays_upcoming_{days}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        today = date.today()
        end_date = today + timedelta(days=days)
        results = []

        for region, exchange_code in self.calendars.items():
            try:
                cal = mcal.get_calendar(exchange_code)

                # Get schedule for the period
                start = today - timedelta(days=7)  # Start slightly before
                schedule = cal.schedule(start_date=start, end_date=end_date)

                # Get holidays
                holidays = cal.holidays()
                if hasattr(holidays, 'holidays'):
                    for h in holidays.holidays:
                        if hasattr(h, 'date'):
                            h_date = h.date()
                        else:
                            h_date = pd.to_datetime(h).date()

                        if today <= h_date <= end_date:
                            results.append({
                                'region': region,
                                'exchange': exchange_code,
                                'holiday': str(h),
                                'date': h_date
                            })

            except Exception:
                continue

        result_df = pd.DataFrame(results)
        if not result_df.empty:
            result_df = result_df.sort_values('date')
        self._set_cache(cache_key, result_df)
        return result_df

    def get_exchange_holidays(self, exchange_code: str, year: int = None) -> List[date]:
        """
        Get all holidays for a specific exchange

        Args:
            exchange_code: Exchange code (e.g., 'XNYS' for NYSE)
            year: Year to get holidays for (default: current year)

        Returns:
            List of holiday dates
        """
        if year is None:
            year = date.today().year

        cache_key = f"holidays_{exchange_code}_{year}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            cal = mcal.get_calendar(exchange_code)
            start = date(year, 1, 1)
            end = date(year, 12, 31)

            holidays = cal.holidays()
            holiday_dates = []

            if hasattr(holidays, 'holidays'):
                for h in holidays.holidays:
                    if hasattr(h, 'date'):
                        h_date = h.date()
                    else:
                        h_date = pd.to_datetime(h).date()

                    if start <= h_date <= end:
                        holiday_dates.append(h_date)

            self._set_cache(cache_key, holiday_dates)
            return holiday_dates

        except Exception:
            return []

    def get_corporate_actions(self, ticker: str, days: int = 30) -> pd.DataFrame:
        """
        Get corporate actions for a stock

        Args:
            ticker: Stock ticker
            days: Number of days to look back

        Returns:
            DataFrame with corporate actions
        """
        cache_key = f"corp_actions_{ticker}_{days}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            stock = yf.Ticker(ticker)
            actions = stock.actions

            if actions is not None and len(actions) > 0:
                # Filter to recent days
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
                recent = actions[actions.index >= cutoff]

                if not recent.empty:
                    recent = recent.reset_index()
                    recent['ticker'] = ticker
                    recent.columns = ['date'] + list(recent.columns[1:])

                    self._set_cache(cache_key, recent)
                    return recent

            return pd.DataFrame()

        except Exception:
            return pd.DataFrame()

    def get_recent_corporate_actions(self, tickers: List[str], days: int = 30) -> pd.DataFrame:
        """
        Get corporate actions for multiple stocks

        Args:
            tickers: List of ticker symbols
            days: Number of days to look back

        Returns:
            DataFrame with all recent corporate actions
        """
        results = []
        for ticker in tickers:
            actions = self.get_corporate_actions(ticker, days)
            if not actions.empty:
                results.append(actions)

        if results:
            return pd.concat(results, ignore_index=True)
        return pd.DataFrame()

    def is_market_open(self, exchange_code: str) -> bool:
        """
        Check if a market is currently open

        Args:
            exchange_code: Exchange code

        Returns:
            True if market is open
        """
        try:
            cal = mcal.get_calendar(exchange_code)
            now = pd.Timestamp.now()
            schedule = cal.schedule(start_date=now.date(), end_date=now.date())

            if schedule.empty:
                return False

            market_open = schedule.iloc[0]['market_open']
            market_close = schedule.iloc[0]['market_close']

            return market_open <= now <= market_close

        except Exception:
            return False