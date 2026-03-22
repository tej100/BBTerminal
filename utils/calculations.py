"""
Financial calculations for time series analysis
"""
import pandas as pd
import numpy as np
from typing import Optional


def calculate_returns(series: pd.Series, period: int = 1) -> pd.Series:
    """
    Calculate percentage returns

    Args:
        series: Price series
        period: Return period (default 1 for daily returns)

    Returns:
        Series of percentage returns
    """
    return series.pct_change(period) * 100


def calculate_log_returns(series: pd.Series, period: int = 1) -> pd.Series:
    """
    Calculate log returns

    Args:
        series: Price series
        period: Return period

    Returns:
        Series of log returns
    """
    return np.log(series / series.shift(period)) * 100


def calculate_volatility(series: pd.Series, window: int = 20,
                         annualize: bool = True) -> pd.Series:
    """
    Calculate rolling volatility (standard deviation of returns)

    Args:
        series: Price series
        window: Rolling window (default 20 for ~1 month of trading days)
        annualize: Whether to annualize (multiply by sqrt(252))

    Returns:
        Series of rolling volatility
    """
    returns = series.pct_change()
    vol = returns.rolling(window=window).std()

    if annualize:
        vol = vol * np.sqrt(252)

    return vol * 100  # Convert to percentage


def calculate_zscore(series: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate rolling z-score

    Args:
        series: Data series
        window: Rolling window

    Returns:
        Series of z-scores
    """
    mean = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    return (series - mean) / std


def calculate_moving_average(series: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate simple moving average

    Args:
        series: Price series
        window: Moving average window

    Returns:
        Series of moving averages
    """
    return series.rolling(window=window).mean()


def calculate_ema(series: pd.Series, span: int = 20) -> pd.Series:
    """
    Calculate exponential moving average

    Args:
        series: Price series
        span: EMA span

    Returns:
        Series of EMA values
    """
    return series.ewm(span=span, adjust=False).mean()


def calculate_bollinger_bands(series: pd.Series, window: int = 20,
                               num_std: float = 2) -> dict:
    """
    Calculate Bollinger Bands

    Args:
        series: Price series
        window: Window for moving average
        num_std: Number of standard deviations for bands

    Returns:
        Dict with 'upper', 'middle', 'lower' bands
    """
    middle = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()

    return {
        'upper': middle + (std * num_std),
        'middle': middle,
        'lower': middle - (std * num_std)
    }


def calculate_drawdown(series: pd.Series) -> pd.Series:
    """
    Calculate drawdown from peak

    Args:
        series: Price series

    Returns:
        Series of drawdown percentages
    """
    peak = series.cummax()
    drawdown = (series - peak) / peak * 100
    return drawdown


def calculate_max_drawdown(series: pd.Series) -> float:
    """
    Calculate maximum drawdown

    Args:
        series: Price series

    Returns:
        Maximum drawdown as percentage
    """
    drawdown = calculate_drawdown(series)
    return drawdown.min()


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.04) -> float:
    """
    Calculate Sharpe ratio

    Args:
        returns: Daily return series
        risk_free_rate: Annual risk-free rate (default 4%)

    Returns:
        Sharpe ratio
    """
    excess_returns = returns - risk_free_rate / 252
    if excess_returns.std() == 0:
        return 0
    return (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)


def calculate_correlation_matrix(price_dict: dict) -> pd.DataFrame:
    """
    Calculate correlation matrix for multiple price series

    Args:
        price_dict: Dictionary of name -> price series

    Returns:
        Correlation matrix DataFrame
    """
    df = pd.DataFrame(price_dict)
    returns = df.pct_change()
    return returns.corr()


def calculate_yield_curve_slope(short_rate: float, long_rate: float) -> float:
    """
    Calculate yield curve slope (spread between long and short rates)

    Args:
        short_rate: Short-term rate (e.g., 2Y)
        long_rate: Long-term rate (e.g., 10Y)

    Returns:
        Spread in basis points
    """
    return (long_rate - short_rate) * 100  # Convert to basis points


def calculate_spread(base_rate: float, reference_rate: float) -> float:
    """
    Calculate spread between two rates

    Args:
        base_rate: Base rate
        reference_rate: Reference rate

    Returns:
        Spread in basis points
    """
    return (base_rate - reference_rate) * 100