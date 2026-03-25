"""
Alerts Panel Component
DQ alerts and outlier detection - Compact version
"""
import streamlit as st
import pandas as pd
from data.yfinance_fetcher import YahooFinanceFetcher
from data.calendars import CalendarFetcher
from utils.dq_checks import DQChecker, OutlierType
from config.settings import MARKET_SUMMARY_TICKERS, SECTOR_ETFS, COMMODITIES
from typing import Dict, List


def render_alerts_panel():
    """Render the DQ alerts panel"""
    st.markdown("### DQ Alerts")

    dq_checker = DQChecker()

    # Tabs for different alert types
    tab1, tab2 = st.tabs(["All", "Outliers"])

    # Collect alerts from all data sources
    with st.spinner("Checking..."):
        all_alerts = _collect_all_alerts(dq_checker)

    with tab1:
        _render_all_alerts(all_alerts)

    with tab2:
        _render_outlier_alerts(all_alerts)


def _collect_all_alerts(dq_checker: DQChecker) -> list:
    """Collect all DQ alerts from various data sources"""
    # Combine all ticker configurations into one comprehensive set
    all_tickers = {**MARKET_SUMMARY_TICKERS, **SECTOR_ETFS, **COMMODITIES}

    return _check_ticker_category(dq_checker, "All Tickers", all_tickers)


def _check_ticker_category(dq_checker: DQChecker, category_name: str, ticker_config: Dict[str, str]) -> list:
    """Check a specific ticker category for DQ alerts"""
    alerts = []

    try:
        fetcher = YahooFinanceFetcher(ticker_config)
        prices_data = fetcher.get_current_prices()

        for _, row in prices_data.iterrows():
            ticker = row['ticker']
            hist = fetcher.get_historical(ticker, period="1mo")

            if not hist.empty and 'Close' in hist.columns:
                series = hist['Close']
                series.name = ticker
                ticker_alerts = dq_checker.check_outliers(series, f"{ticker} ({row.get('name', ticker)})")
                alerts.extend(ticker_alerts)

    except Exception:
        pass

    return alerts


def _render_all_alerts(alerts: list):
    """Render all alerts in compact format"""
    if not alerts:
        st.success("No alerts")
        return

    st.markdown(f"**{len(alerts)} alerts**")

    # Group by severity
    high_alerts = [a for a in alerts if a.severity == 'high']
    medium_alerts = [a for a in alerts if a.severity == 'medium']
    low_alerts = [a for a in alerts if a.severity == 'low']

    if high_alerts:
        st.markdown("**High:**")
        for alert in high_alerts:
            st.markdown(f"<span style='color:#f85149'>[{alert.series_name}]</span> {alert.message}",
                       unsafe_allow_html=True)

    if medium_alerts:
        st.markdown("**Medium:**")
        for alert in medium_alerts:
            st.markdown(f"<span style='color:#d29922'>[{alert.series_name}]</span> {alert.message}",
                       unsafe_allow_html=True)

    if low_alerts:
        st.markdown("**Low:**")
        for alert in low_alerts:
            st.markdown(f"<span style='color:#58a6ff'>[{alert.series_name}]</span> {alert.message}",
                       unsafe_allow_html=True)


def _render_outlier_alerts(alerts: list):
    """Render outlier/volatility alerts"""
    outlier_types = [OutlierType.VOLATILITY_SPIKE, OutlierType.PRICE_JUMP]
    outlier_alerts = [a for a in alerts if a.alert_type in outlier_types]

    if not outlier_alerts:
        st.success("No outliers detected")
        return

    st.markdown(f"**{len(outlier_alerts)} outliers**")

    for alert in outlier_alerts:
        severity_color = "#f85149" if alert.severity == 'high' else "#d29922"
        st.markdown(f"<span style='color:{severity_color}'>[{alert.series_name}]</span> {alert.message}",
                   unsafe_allow_html=True)


def render_market_status():
    """Render market status indicator in sidebar"""
    calendars = CalendarFetcher()
    st.markdown("### Market Status")

    try:
        is_us_open = calendars.is_market_open("XNYS")

        if is_us_open:
            st.markdown("**US Markets: OPEN**")
        else:
            st.markdown("**US Markets: CLOSED**")

    except Exception:
        st.markdown("**US Markets: ?**")

    # Check holidays
    try:
        todays_holidays = calendars.get_todays_holidays()

        if not todays_holidays.empty:
            st.markdown("**Today's Holidays:**")
            for _, row in todays_holidays.iterrows():
                st.markdown(f"{row['region']}: {row['holiday']}")

    except Exception:
        pass