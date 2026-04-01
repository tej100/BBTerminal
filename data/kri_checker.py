"""
Key Risk Indicators (KRI) framework for market monitoring
Supports multiple data sources: Yahoo Finance, Treasury.gov, FRED
"""
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from data.yfinance_fetcher import YahooFinanceFetcher
from data.treasury import TreasuryFetcher
from data.fred_fetcher import FredFetcher
from config.settings import (
    KRI_TICKER_GROUPS, KRI_DEFAULT_LOOKBACK,
    ECONOMIC_DATA, MORTGAGE_RATES
)
from config.kri_config import KRI_CONFIG
from data.kri_metrics import get_handler, MetricContext, requires_historical


@dataclass
class KRIAlert:
    """KRI Alert"""
    kri_name: str
    ticker: str
    value: float
    threshold: float
    severity: str
    message: str
    metric: str
    description: Optional[str] = None
    lookback: Optional[int] = None


class KRIChecker:
    """Check all configured Key Risk Indicators from settings"""

    def __init__(self, historical_period: str = "3mo"):
        """
        Initialize KRI Checker.

        Args:
            historical_period: Default period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y)
        """
        self.historical_period = historical_period
        self._price_cache: Dict[str, pd.DataFrame] = {}
        self._treasury_fetcher: Optional[TreasuryFetcher] = None
        self._fred_fetcher: Optional[FredFetcher] = None

    def _detect_source(self, ticker: str) -> str:
        """
        Auto-detect data source based on ticker pattern.

        Returns: 'treasury', 'fred', or 'yahoo'
        """
        # Treasury.gov: BC_ prefix (e.g., BC_10YEAR, BC_1MONTH)
        if ticker.startswith("BC_"):
            return "treasury"
        # FRED: Check against known FRED series dictionaries
        if ticker in ECONOMIC_DATA or ticker in MORTGAGE_RATES:
            return "fred"
        # Default to Yahoo Finance
        return "yahoo"

    def check_all(self) -> List[KRIAlert]:
        """Check all KRIs and return alerts"""
        alerts = []
        for kri_name, kri_def in KRI_CONFIG.items():
            try:
                kri_alerts = self._check_kri(kri_name, kri_def)
                alerts.extend(kri_alerts)
            except Exception:
                pass
        return alerts

    def _check_kri(self, kri_name: str, kri_def: Dict) -> List[KRIAlert]:
        """Check single KRI (single or multi-ticker)"""
        if "ticker" in kri_def:
            alert = self._check_single_ticker(kri_name, kri_def)
            return [alert] if alert else []
        elif "tickers" in kri_def:
            return self._check_multi_ticker(kri_name, kri_def)
        return []

    def _check_single_ticker(self, kri_name: str, kri_def: Dict) -> Optional[KRIAlert]:
        """Check KRI for single ticker"""
        ticker = kri_def["ticker"]
        metric = kri_def["metric"]
        lookback = kri_def.get("lookback", KRI_DEFAULT_LOOKBACK)

        handler = get_handler(metric)
        if handler is None:
            return None

        try:
            # Fetch data based on metric requirements
            if requires_historical(metric):
                data = self._get_historical_data(ticker)
            else:
                data = self._get_current_prices(ticker)

            if data.empty:
                return None

            context = MetricContext(lookback=lookback)
            value = handler.calculate(data, context)

            if value is None:
                return None

            severity_and_threshold = self._evaluate_severity(value, kri_def)
            if severity_and_threshold:
                severity, threshold = severity_and_threshold
                return KRIAlert(
                    kri_name=kri_name,
                    ticker=ticker,
                    value=value,
                    threshold=threshold,
                    severity=severity,
                    message=self._format_message(ticker, value, threshold, metric),
                    metric=metric,
                    description=kri_def.get("description"),
                    lookback=lookback
                )
        except Exception:
            pass
        return None

    def _check_multi_ticker(self, kri_name: str, kri_def: Dict) -> List[KRIAlert]:
        """Check KRI for multiple tickers"""
        tickers_config = self._resolve_ticker_ref(kri_def["tickers"])
        if not tickers_config:
            return []

        metric = kri_def["metric"]
        lookback = kri_def.get("lookback", KRI_DEFAULT_LOOKBACK)

        handler = get_handler(metric)
        if handler is None:
            return []

        alerts = []

        # For other multi-ticker metrics, check each ticker
        for ticker in tickers_config.keys():
            try:
                if requires_historical(metric):
                    data = self._get_historical_data(ticker)
                else:
                    data = self._get_current_prices(ticker)
                    data = data[data["ticker"] == ticker] if "ticker" in data.columns else data

                if data.empty:
                    continue

                context = MetricContext(lookback=lookback)
                value = handler.calculate(data, context)

                if value is None:
                    continue

                severity_and_threshold = self._evaluate_severity(value, kri_def)
                if severity_and_threshold:
                    severity, threshold = severity_and_threshold
                    display_name = tickers_config.get(ticker, ticker)
                    alerts.append(KRIAlert(
                        kri_name=kri_name,
                        ticker=ticker,
                        value=value,
                        threshold=threshold,
                        severity=severity,
                        message=self._format_message(display_name, value, threshold, metric),
                        metric=metric,
                        description=kri_def.get("description"),
                        lookback=lookback
                    ))
            except Exception:
                continue

        return alerts

    def _get_historical_data(self, ticker: str) -> pd.DataFrame:
        """Get historical data with caching, routing to appropriate fetcher"""
        if ticker in self._price_cache:
            return self._price_cache[ticker]

        source = self._detect_source(ticker)

        if source == "treasury":
            hist = self._get_treasury_historical(ticker)
        elif source == "fred":
            hist = self._get_fred_historical(ticker)
        else:
            hist = self._get_yahoo_historical(ticker)

        self._price_cache[ticker] = hist
        return hist

    def _get_yahoo_historical(self, ticker: str) -> pd.DataFrame:
        """Fetch historical data from Yahoo Finance"""
        fetcher = YahooFinanceFetcher({ticker: ticker})
        return fetcher.get_historical(ticker, period=self.historical_period)

    def _get_treasury_historical(self, ticker: str) -> pd.DataFrame:
        """
        Fetch historical yield data from Treasury.gov.
        Ticker format: BC_1MONTH, BC_10YEAR, etc.
        """
        if self._treasury_fetcher is None:
            self._treasury_fetcher = TreasuryFetcher()

        # Convert period to days (approximate)
        period_days = {
            "1d": 5, "5d": 10, "1mo": 35, "3mo": 100, "6mo": 190, "1y": 380
        }
        days = period_days.get(self.historical_period, 100)

        df = self._treasury_fetcher.get_yield_curve_data(days=days)

        if df.empty or ticker not in df.columns:
            return pd.DataFrame()

        # Extract just this tenor and normalize to Close column
        result = df[["date", ticker]].copy()
        result = result.rename(columns={ticker: "Close"})
        result = result.sort_values("date", ascending=False).reset_index(drop=True)

        return result

    def _get_fred_historical(self, ticker: str) -> pd.DataFrame:
        """
        Fetch historical data from FRED API.
        Ticker is the FRED series ID (e.g., CPIAUCSL, UNRATE).
        """
        if self._fred_fetcher is None:
            self._fred_fetcher = FredFetcher({ticker: ticker})

        # Convert period to days
        period_days = {
            "1d": 5, "5d": 10, "1mo": 35, "3mo": 100, "6mo": 190, "1y": 380
        }
        days = period_days.get(self.historical_period, 100)

        df = self._fred_fetcher.get_historical_rates(ticker, days=days)

        if df.empty:
            return pd.DataFrame()

        # Normalize to Close column
        result = df[["date", "value"]].copy()
        result = result.rename(columns={"value": "Close"})
        result = result.sort_values("date", ascending=False).reset_index(drop=True)

        return result

    def _get_current_prices(self, ticker: str) -> pd.DataFrame:
        """Get current prices, routing to appropriate fetcher"""
        source = self._detect_source(ticker)

        if source == "treasury":
            return self._get_treasury_current(ticker)
        elif source == "fred":
            return self._get_fred_current(ticker)
        else:
            return self._get_yahoo_current(ticker)

    def _get_yahoo_current(self, ticker: str) -> pd.DataFrame:
        """Get current prices from Yahoo Finance"""
        fetcher = YahooFinanceFetcher({ticker: ticker})
        return fetcher.get_current_prices()

    def _get_treasury_current(self, ticker: str) -> pd.DataFrame:
        """Get current yield from Treasury.gov"""
        if self._treasury_fetcher is None:
            self._treasury_fetcher = TreasuryFetcher()

        yields = self._treasury_fetcher.get_latest_yields()

        if yields.empty:
            return pd.DataFrame()

        # Find the maturity matching this ticker
        maturity_map = {v: k for k, v in self._treasury_fetcher.MATURITIES.items()}
        maturity_name = None
        for col, name in self._treasury_fetcher.MATURITIES.items():
            if col == ticker:
                maturity_name = name
                break

        if maturity_name is None:
            return pd.DataFrame()

        row = yields[yields["maturity"] == maturity_name]
        if row.empty:
            return pd.DataFrame()

        # Normalize to price format
        return pd.DataFrame([{
            "ticker": ticker,
            "price": row.iloc[0]["rate"]
        }])

    def _get_fred_current(self, ticker: str) -> pd.DataFrame:
        """Get current value from FRED"""
        if self._fred_fetcher is None:
            self._fred_fetcher = FredFetcher({ticker: ticker})

        rate_data = self._fred_fetcher.get_latest_rate(ticker)

        if rate_data is None:
            return pd.DataFrame()

        # Normalize to price format
        return pd.DataFrame([{
            "ticker": ticker,
            "price": rate_data["value"]
        }])

    def _check_condition(self, value: float, threshold: float, condition: str) -> bool:
        """Evaluate condition"""
        if condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "abs":
            return abs(value) >= threshold
        elif condition == "abs_le":
            return abs(value) <= threshold
        elif condition == "drop":
            # Alert when value drops below threshold
            return value <= threshold
        elif condition == "spike":
            return value >= threshold
        return False

    def _evaluate_severity(self, value: float, kri_def: Dict) -> Optional[Tuple[str, float]]:
        """
        Evaluate which threshold was hit.
        For "drop" condition: low_threshold > high_threshold (e.g., 0.4 > 0.2)
        """
        condition = kri_def["condition"]
        high_threshold = kri_def.get("high_threshold")
        low_threshold = kri_def.get("low_threshold")

        # For "drop" condition: lower value = higher severity
        # low_threshold (0.4) triggers yellow, high_threshold (0.2) triggers red
        if condition == "drop":
            if high_threshold is not None and value <= high_threshold:
                return ("high", high_threshold)
            if low_threshold is not None and value <= low_threshold:
                return ("low", low_threshold)
            return None

        # Standard threshold checking - high threshold first
        if high_threshold is not None:
            if self._check_condition(value, high_threshold, condition):
                return ("high", high_threshold)

        if low_threshold is not None:
            if self._check_condition(value, low_threshold, condition):
                return ("low", low_threshold)

        return None

    def _format_message(self, display_name: str, value: float,
                         threshold: float, metric: str) -> str:
        """Auto-generate readable message based on metric type"""
        if metric in ("z_score", "z_score_abs"):
            return f"{display_name}: z-score={value:.2f} (threshold: {threshold:.2f})"
        elif metric == "daily_pct_change":
            return f"{display_name}: {value:.2f}% (threshold: {threshold:.2f}%)"
        else:
            return f"{display_name}: {value:.2f} (threshold: {threshold:.2f})"

    def _resolve_ticker_ref(self, ref: str) -> Optional[Dict]:
        """Resolve ticker dictionary reference"""
        return KRI_TICKER_GROUPS.get(ref)

    def clear_cache(self):
        """Clear historical data cache and fetcher instances"""
        self._price_cache.clear()
        self._treasury_fetcher = None
        self._fred_fetcher = None