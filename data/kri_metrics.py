"""
KRI Metric Handlers - Pluggable metric calculation system
"""
import pandas as pd
from typing import Dict, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class MetricContext:
    """Context passed to metric handlers"""
    lookback: int = 30


class MetricHandler(ABC):
    """Abstract base class for metric handlers"""

    @abstractmethod
    def calculate(self, data: pd.DataFrame, context: MetricContext) -> Optional[float]:
        """Calculate the metric value"""
        pass

    @abstractmethod
    def requires_historical(self) -> bool:
        """Whether this metric requires historical data"""
        pass


class LastPriceHandler(MetricHandler):
    """Handle last_price metric"""

    def calculate(self, data: pd.DataFrame, context: MetricContext) -> Optional[float]:
        if data.empty:
            return None
        return data.iloc[-1].get("price")

    def requires_historical(self) -> bool:
        return False


class DailyPctChangeHandler(MetricHandler):
    """Handle daily_pct_change metric"""

    def calculate(self, data: pd.DataFrame, context: MetricContext) -> Optional[float]:
        if len(data) < 2:
            return None

        # Check if we have Close column (historical data)
        if "Close" in data.columns:
            close_today = data["Close"].iloc[-1]
            close_yesterday = data["Close"].iloc[-2]
        else:
            # Current prices data
            close_today = data.iloc[-1].get("price")
            close_yesterday = data.iloc[-1].get("change") + close_today if close_today else None

        if close_yesterday is None or close_yesterday == 0:
            return None

        return ((close_today - close_yesterday) / close_yesterday) * 100

    def requires_historical(self) -> bool:
        return True


class ZScoreHandler(MetricHandler):
    """Handle z_score metric (value relative to rolling mean)"""

    def calculate(self, data: pd.DataFrame, context: MetricContext) -> Optional[float]:
        if data.empty or len(data) < context.lookback:
            return None

        if "Close" not in data.columns:
            return None

        series = data["Close"]
        returns = series.pct_change(fill_method=None).dropna()

        if len(returns) < context.lookback:
            return None

        rolling_mean = returns.rolling(window=context.lookback).mean().iloc[-1]
        rolling_std = returns.rolling(window=context.lookback).std().iloc[-1]

        if pd.isna(rolling_std) or rolling_std == 0:
            return None

        last_return = returns.iloc[-1]
        return (last_return - rolling_mean) / rolling_std

    def requires_historical(self) -> bool:
        return True


class ZScoreAbsHandler(ZScoreHandler):
    """Handle z_score_abs metric (absolute z-score)"""

    def calculate(self, data: pd.DataFrame, context: MetricContext) -> Optional[float]:
        z_score = super().calculate(data, context)
        return abs(z_score) if z_score is not None else None



# Metric handler registry
METRIC_HANDLERS: Dict[str, MetricHandler] = {
    "last_price": LastPriceHandler(),
    "daily_pct_change": DailyPctChangeHandler(),
    "z_score": ZScoreHandler(),
    "z_score_abs": ZScoreAbsHandler()
}


def get_handler(metric: str) -> Optional[MetricHandler]:
    """Get metric handler by name"""
    return METRIC_HANDLERS.get(metric)


def requires_historical(metric: str) -> bool:
    """Check if metric requires historical data"""
    handler = get_handler(metric)
    return handler.requires_historical() if handler else False