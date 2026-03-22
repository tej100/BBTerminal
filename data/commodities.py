"""
Commodities data fetcher using yfinance
"""
import yfinance as yf
import pandas as pd
from typing import List, Optional
from .fetcher import DataFetcher
from config.settings import COMMODITIES


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
        Get current prices and daily changes for commodities

        Args:
            tickers: List of ticker symbols (default: all commodities)

        Returns:
            DataFrame with price, change, change_pct columns
        """
        if tickers is None:
            tickers = self.get_all_tickers()

        cache_key = f"commodities_current_{'_'.join(sorted(tickers[:5]))}"
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
                            'name': self.commodities.get(ticker, ticker),
                            'price': round(last_close, 2),
                            'change': round(change, 2),
                            'change_pct': round(change_pct, 2)
                        })
                except Exception:
                    continue

            result_df = pd.DataFrame(results)
            self._set_cache(cache_key, result_df)
            return result_df

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
        cache_key = f"commodity_hist_{ticker}_{period}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            commodity = yf.Ticker(ticker)
            hist = commodity.history(period=period, auto_adjust=True)
            self._set_cache(cache_key, hist)
            return hist
        except Exception:
            return pd.DataFrame()

    def get_contract_info(self, ticker: str) -> dict:
        """Get contract info for a commodity"""
        try:
            commodity = yf.Ticker(ticker)
            return commodity.info
        except Exception:
            return {}