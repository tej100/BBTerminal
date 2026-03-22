"""
Equities data fetcher using yfinance
"""
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from .fetcher import DataFetcher
from config.settings import EQUITY_INDICES, SECTOR_ETFS, KEY_STOCKS


class EquitiesFetcher(DataFetcher):
    """Fetch equity market data from Yahoo Finance"""

    def __init__(self, cache_duration: int = 300):
        super().__init__(cache_duration)
        self.indices = EQUITY_INDICES
        self.sectors = SECTOR_ETFS
        self.key_stocks = KEY_STOCKS

    def get_all_tickers(self) -> List[str]:
        """Get all equity tickers"""
        return list(self.indices.keys()) + list(self.sectors.keys()) + self.key_stocks

    def get_current_prices(self, tickers: List[str]) -> pd.DataFrame:
        """
        Get current prices and daily changes for given tickers

        Args:
            tickers: List of ticker symbols

        Returns:
            DataFrame with price, change, change_pct columns
        """
        cache_key = f"equities_current_{'_'.join(sorted(tickers[:5]))}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            data = yf.download(
                tickers,
                period="2d",
                progress=False,
                group_by="ticker",
                auto_adjust=True
            )

            results = []
            for ticker in tickers:
                try:
                    # Handle MultiIndex columns from yfinance
                    if len(tickers) == 1:
                        # Single ticker: columns are MultiIndex with ticker as first level
                        close_prices = data.xs('Close', level='Price', axis=1).iloc[:, 0]
                    else:
                        # Multiple tickers: access by ticker then Close
                        close_prices = data[ticker]['Close']

                    if len(close_prices) >= 2:
                        last_close = close_prices.iloc[-1]
                        prev_close = close_prices.iloc[-2]
                        change = last_close - prev_close
                        change_pct = (change / prev_close) * 100

                        results.append({
                            'ticker': ticker,
                            'price': round(last_close, 2),
                            'change': round(change, 2),
                            'change_pct': round(change_pct, 2),
                            'name': self._get_name(ticker)
                        })
                except Exception:
                    continue

            result_df = pd.DataFrame(results)
            self._set_cache(cache_key, result_df)
            return result_df

        except Exception as e:
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
        cache_key = f"equities_hist_{ticker}_{period}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, auto_adjust=True)
            self._set_cache(cache_key, hist)
            return hist
        except Exception:
            return pd.DataFrame()

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