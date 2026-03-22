"""
Data Quality checks for time series analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from config.settings import ZSCORE_THRESHOLD, VOLATILITY_WINDOW


class OutlierType(Enum):
    """Types of outliers detected"""
    VOLATILITY_SPIKE = "volatility_spike"
    PRICE_JUMP = "price_jump"
    MISSING_DATA = "missing_data"
    STALE_DATA = "stale_data"
    CORPORATE_ACTION = "corporate_action"


@dataclass
class DQAlert:
    """Data Quality Alert"""
    series_id: str
    series_name: str
    alert_type: OutlierType
    severity: str  # 'low', 'medium', 'high'
    message: str
    value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: Optional[pd.Timestamp] = None


class DQChecker:
    """Data Quality checker for time series data"""

    def __init__(self, zscore_threshold: float = ZSCORE_THRESHOLD,
                 volatility_window: int = VOLATILITY_WINDOW):
        self.zscore_threshold = zscore_threshold
        self.volatility_window = volatility_window

    def check_outliers(self, series: pd.Series, name: str = "series") -> List[DQAlert]:
        """
        Check for various types of outliers in a time series

        Args:
            series: Pandas series with time index
            name: Name of the series for reporting

        Returns:
            List of DQAlert objects
        """
        alerts = []

        # Check for stale data
        stale_alert = self._check_stale_data(series, name)
        if stale_alert:
            alerts.append(stale_alert)

        # Check for missing data
        missing_alerts = self._check_missing_data(series, name)
        alerts.extend(missing_alerts)

        # Check for volatility-based outliers
        volatility_alerts = self._check_volatility_outliers(series, name)
        alerts.extend(volatility_alerts)

        return alerts

    def _check_stale_data(self, series: pd.Series, name: str) -> Optional[DQAlert]:
        """Check if data hasn't been updated recently"""
        if series.empty:
            return None

        last_date = series.index[-1]
        now = pd.Timestamp.now()

        # For daily data, expect update at least within 2 business days
        days_diff = (now - last_date).days

        if days_diff > 7:
            return DQAlert(
                series_id=name,
                series_name=name,
                alert_type=OutlierType.STALE_DATA,
                severity='high',
                message=f"Data is {days_diff} days old (last update: {last_date.strftime('%Y-%m-%d')})",
                timestamp=last_date
            )
        elif days_diff > 3:
            return DQAlert(
                series_id=name,
                series_name=name,
                alert_type=OutlierType.STALE_DATA,
                severity='medium',
                message=f"Data is {days_diff} days old (last update: {last_date.strftime('%Y-%m-%d')})",
                timestamp=last_date
            )

        return None

    def _check_missing_data(self, series: pd.Series, name: str) -> List[DQAlert]:
        """Check for gaps in expected data"""
        alerts = []

        if len(series) < 2:
            return alerts

        # Calculate expected frequency
        freq = pd.infer_freq(series.index)
        if freq is None:
            return alerts

        # Create expected date range
        try:
            expected_range = pd.date_range(start=series.index[0], end=series.index[-1], freq=freq)
            missing_dates = expected_range.difference(series.index)

            if len(missing_dates) > 0:
                severity = 'high' if len(missing_dates) > 5 else 'medium'
                alerts.append(DQAlert(
                    series_id=name,
                    series_name=name,
                    alert_type=OutlierType.MISSING_DATA,
                    severity=severity,
                    message=f"Found {len(missing_dates)} missing data points",
                    value=len(missing_dates),
                    threshold=0
                ))
        except Exception:
            pass

        return alerts

    def _check_volatility_outliers(self, series: pd.Series, name: str) -> List[DQAlert]:
        """Check for volatility-based outliers using z-scores"""
        alerts = []

        if len(series) < self.volatility_window:
            return alerts

        # Calculate returns
        returns = series.pct_change().dropna()

        if len(returns) < self.volatility_window:
            return alerts

        # Calculate rolling volatility and z-scores
        rolling_std = returns.rolling(window=self.volatility_window).std()
        z_scores = (returns - returns.rolling(window=self.volatility_window).mean()) / rolling_std

        # Check last value for outlier
        last_z = z_scores.iloc[-1]

        if abs(last_z) > self.zscore_threshold:
            severity = 'high' if abs(last_z) > 3 else 'medium'
            alerts.append(DQAlert(
                series_id=name,
                series_name=name,
                alert_type=OutlierType.VOLATILITY_SPIKE,
                severity=severity,
                message=f"Unusual move detected: {returns.iloc[-1]*100:.2f}% (z-score: {last_z:.2f})",
                value=returns.iloc[-1] * 100,
                threshold=self.zscore_threshold,
                timestamp=series.index[-1]
            ))

        return alerts

    def check_price_jump(self, series: pd.Series, name: str,
                         threshold: float = 0.1) -> Optional[DQAlert]:
        """
        Check for large price jumps that might indicate corporate actions or errors

        Args:
            series: Price series
            name: Series name
            threshold: Jump threshold (default 10%)

        Returns:
            DQAlert if price jump detected
        """
        if len(series) < 2:
            return None

        change = abs((series.iloc[-1] - series.iloc[-2]) / series.iloc[-2])

        if change > threshold:
            return DQAlert(
                series_id=name,
                series_name=name,
                alert_type=OutlierType.PRICE_JUMP,
                severity='high',
                message=f"Large price jump detected: {change*100:.2f}%",
                value=change * 100,
                threshold=threshold * 100,
                timestamp=series.index[-1]
            )

        return None

    def batch_check(self, data_dict: Dict[str, pd.Series]) -> List[DQAlert]:
        """
        Run DQ checks on multiple series

        Args:
            data_dict: Dictionary of series name -> pandas series

        Returns:
            List of all DQAlerts found
        """
        all_alerts = []

        for name, series in data_dict.items():
            alerts = self.check_outliers(series, name)
            all_alerts.extend(alerts)

        # Sort by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        all_alerts.sort(key=lambda x: severity_order.get(x.severity, 1))

        return all_alerts