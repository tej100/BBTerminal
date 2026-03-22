"""
Formatting utilities for display
"""
from typing import Optional


def format_price(value: float, currency: str = "$") -> str:
    """
    Format price with currency symbol

    Args:
        value: Price value
        currency: Currency symbol

    Returns:
        Formatted price string
    """
    if value >= 1000:
        return f"{currency}{value:,.2f}"
    elif value >= 1:
        return f"{currency}{value:.2f}"
    else:
        return f"{currency}{value:.4f}"


def format_change(value: float, include_sign: bool = True) -> str:
    """
    Format price change with sign and color indicators

    Args:
        value: Change value
        include_sign: Whether to include +/- sign

    Returns:
        Formatted change string
    """
    if include_sign:
        if value >= 0:
            return f"+{value:.2f}"
        else:
            return f"{value:.2f}"
    else:
        return f"{value:.2f}"


def format_percent(value: float, include_sign: bool = True) -> str:
    """
    Format percentage change

    Args:
        value: Percentage value
        include_sign: Whether to include +/- sign

    Returns:
        Formatted percentage string
    """
    if include_sign:
        if value >= 0:
            return f"+{value:.2f}%"
        else:
            return f"{value:.2f}%"
    else:
        return f"{value:.2f}%"


def format_number(value: float, decimals: int = 2) -> str:
    """
    Format large numbers with K, M, B suffixes

    Args:
        value: Number value
        decimals: Number of decimal places

    Returns:
        Formatted number string
    """
    abs_value = abs(value)
    sign = "-" if value < 0 else ""

    if abs_value >= 1e9:
        return f"{sign}{abs_value / 1e9:.{decimals}f}B"
    elif abs_value >= 1e6:
        return f"{sign}{abs_value / 1e6:.{decimals}f}M"
    elif abs_value >= 1e3:
        return f"{sign}{abs_value / 1e3:.{decimals}f}K"
    else:
        return f"{sign}{abs_value:.{decimals}f}"


def format_basis_points(value: float) -> str:
    """
    Format value as basis points

    Args:
        value: Rate value (e.g., 0.05 for 5%)

    Returns:
        Formatted basis points string
    """
    bps = value * 100  # Convert to basis points (1% = 100 bps)
    return f"{bps:.1f} bps"


def format_yield(value: float) -> str:
    """
    Format yield/rate as percentage

    Args:
        value: Yield value

    Returns:
        Formatted yield string
    """
    return f"{value:.3f}%"


def get_change_color(value: float) -> str:
    """
    Get color for change value (for Streamlit)

    Args:
        value: Change value

    Returns:
        Color string ('green', 'red', 'gray')
    """
    if value > 0:
        return "green"
    elif value < 0:
        return "red"
    else:
        return "gray"


def get_severity_color(severity: str) -> str:
    """
    Get color for DQ alert severity

    Args:
        severity: Severity level ('high', 'medium', 'low')

    Returns:
        Color string
    """
    colors = {
        'high': 'red',
        'medium': 'orange',
        'low': 'yellow'
    }
    return colors.get(severity, 'gray')


def format_timestamp(ts) -> str:
    """
    Format timestamp for display

    Args:
        ts: Timestamp object

    Returns:
        Formatted date string
    """
    if hasattr(ts, 'strftime'):
        return ts.strftime('%Y-%m-%d %H:%M')
    return str(ts)


def format_date(ts) -> str:
    """
    Format date for display

    Args:
        ts: Date/timestamp object

    Returns:
        Formatted date string
    """
    if hasattr(ts, 'strftime'):
        return ts.strftime('%Y-%m-%d')
    return str(ts)