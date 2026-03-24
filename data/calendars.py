"""
Holiday calendar and corporate actions fetcher
"""
import pandas as pd
import streamlit as st
from datetime import date, timedelta
from typing import List, Optional
import pandas_market_calendars as mcal
from .fetcher import DataFetcher
from config.settings import EXCHANGE_CALENDARS
import yfinance as yf


# Streamlit-cached function for corporate actions - prevents repeated API calls
@st.cache_data(ttl=300)
def _fetch_yfinance_actions(ticker: str) -> pd.DataFrame:
    """
    Fetch corporate actions from yfinance.
    Cached by Streamlit to prevent repeated API calls on widget interactions.
    """
    try:
        stock = yf.Ticker(ticker)
        return stock.actions
    except Exception:
        return pd.DataFrame()


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
        start_ts = pd.Timestamp(today)
        end_ts = pd.Timestamp(today)

        results = []
        for region, exchange_code in self.calendars.items():
            try:
                cal = mcal.get_calendar(exchange_code)
                rh = cal.regular_holidays

                if rh:
                    for rule in rh.rules:
                        try:
                            result = rule.dates(start_ts, end_ts, return_name=True)
                            for ts, name in result.items():
                                results.append({
                                    'region': region,
                                    'exchange': exchange_code,
                                    'holiday': name,
                                    'date': ts.date()
                                })
                        except Exception:
                            continue

            except Exception:
                continue

        return pd.DataFrame(results)

    def get_upcoming_holidays(self, days: int = 30) -> pd.DataFrame:
        """
        Get upcoming holidays for all tracked exchanges

        Args:
            days: Number of days to look ahead

        Returns:
            DataFrame with upcoming holidays with holiday names
        """
        today = date.today()
        end_date = today + timedelta(days=days)
        start_ts = pd.Timestamp(today)
        end_ts = pd.Timestamp(end_date)

        results = []

        for region, exchange_code in self.calendars.items():
            try:
                cal = mcal.get_calendar(exchange_code)
                rh = cal.regular_holidays

                if rh:
                    for rule in rh.rules:
                        try:
                            result = rule.dates(start_ts, end_ts, return_name=True)
                            for ts, name in result.items():
                                h_date = ts.date()
                                # Filter to only dates in our range
                                if today <= h_date <= end_date:
                                    results.append({
                                        'region': region,
                                        'exchange': exchange_code,
                                        'holiday': name,
                                        'date': h_date
                                    })
                        except Exception:
                            continue

            except Exception:
                continue

        result_df = pd.DataFrame(results)
        if not result_df.empty:
            result_df = result_df.sort_values('date')
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
        try:
            actions = _fetch_yfinance_actions(ticker)

            if actions is not None and len(actions) > 0:
                # Filter to recent days
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
                recent = actions[actions.index >= cutoff]

                if not recent.empty:
                    recent = recent.reset_index()
                    recent['ticker'] = ticker
                    recent.columns = ['date'] + list(recent.columns[1:])
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