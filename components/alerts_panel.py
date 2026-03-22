"""
Alerts Panel Component
DQ alerts and outlier detection
"""
import streamlit as st
import pandas as pd
from data.equities import EquitiesFetcher
from data.rates import RatesFetcher
from data.mortgages import MortgagesFetcher
from data.commodities import CommoditiesFetcher
from data.economic import EconomicFetcher
from utils.dq_checks import DQChecker, OutlierType
from utils.formatters import get_severity_color


def render_alerts_panel():
    """Render the DQ alerts panel"""
    st.markdown("### Data Quality Alerts")

    dq_checker = DQChecker()

    all_alerts = []

    # Tabs for different alert types
    tab1, tab2, tab3 = st.tabs(["All Alerts", "Outliers", "Stale/Missing Data"])

    # Collect alerts from all data sources
    with st.spinner("Checking for alerts..."):
        all_alerts = _collect_all_alerts(dq_checker)

    with tab1:
        _render_all_alerts(all_alerts)

    with tab2:
        _render_outlier_alerts(all_alerts)

    with tab3:
        _render_data_quality_alerts(all_alerts)


def _collect_all_alerts(dq_checker: DQChecker) -> list:
    """Collect all DQ alerts from various data sources"""
    all_alerts = []

    # Check equities
    try:
        equities = EquitiesFetcher()
        indices_data = equities.get_indices_performance()

        for _, row in indices_data.iterrows():
            ticker = row['ticker']
            hist = equities.get_historical(ticker, period="1mo")

            if not hist.empty and 'Close' in hist.columns:
                series = hist['Close']
                series.name = ticker
                alerts = dq_checker.check_outliers(series, f"{ticker} ({row.get('name', ticker)})")
                all_alerts.extend(alerts)

    except Exception:
        pass

    # Check commodities
    try:
        commodities = CommoditiesFetcher()
        prices_data = commodities.get_current_prices()

        for _, row in prices_data.iterrows():
            ticker = row['ticker']
            hist = commodities.get_historical(ticker, period="1mo")

            if not hist.empty and 'Close' in hist.columns:
                series = hist['Close']
                series.name = ticker
                alerts = dq_checker.check_outliers(series, f"{ticker} ({row.get('name', ticker)})")
                all_alerts.extend(alerts)

    except Exception:
        pass

    return all_alerts


def _render_all_alerts(alerts: list):
    """Render all alerts"""
    if not alerts:
        st.success("No data quality alerts at this time")
        return

    st.markdown(f"**Total Alerts: {len(alerts)}**")

    # Group by severity
    high_alerts = [a for a in alerts if a.severity == 'high']
    medium_alerts = [a for a in alerts if a.severity == 'medium']
    low_alerts = [a for a in alerts if a.severity == 'low']

    if high_alerts:
        st.markdown("#### High Priority")
        for alert in high_alerts:
            st.error(f"⚠️ **{alert.series_name}**: {alert.message}")

    if medium_alerts:
        st.markdown("#### Medium Priority")
        for alert in medium_alerts:
            st.warning(f"⚡ **{alert.series_name}**: {alert.message}")

    if low_alerts:
        st.markdown("#### Low Priority")
        for alert in low_alerts:
            st.info(f"ℹ️ **{alert.series_name}**: {alert.message}")


def _render_outlier_alerts(alerts: list):
    """Render outlier/volatility alerts"""
    outlier_types = [OutlierType.VOLATILITY_SPIKE, OutlierType.PRICE_JUMP]
    outlier_alerts = [a for a in alerts if a.alert_type in outlier_types]

    if not outlier_alerts:
        st.success("No outlier alerts detected")
        return

    st.markdown(f"**Outlier Alerts: {len(outlier_alerts)}**")

    for alert in outlier_alerts:
        severity_emoji = "🔴" if alert.severity == 'high' else "🟡"
        st.markdown(f"{severity_emoji} **{alert.series_name}**: {alert.message}")

        if alert.value is not None:
            st.caption(f"Value: {alert.value:.2f}%, Threshold: {alert.threshold}")


def _render_data_quality_alerts(alerts: list):
    """Render data quality alerts (stale, missing)"""
    dq_types = [OutlierType.STALE_DATA, OutlierType.MISSING_DATA]
    dq_alerts = [a for a in alerts if a.alert_type in dq_types]

    if not dq_alerts:
        st.success("No data quality issues detected")
        return

    st.markdown(f"**Data Quality Issues: {len(dq_alerts)}**")

    for alert in dq_alerts:
        severity_emoji = "🔴" if alert.severity == 'high' else "🟡"
        alert_type = alert.alert_type.value.replace("_", " ").title()
        st.markdown(f"{severity_emoji} **{alert.series_name}** ({alert_type}): {alert.message}")


def render_market_status():
    """Render market status indicator"""
    from data.calendars import CalendarFetcher
    import pandas_market_calendars as mcal

    calendars = CalendarFetcher()

    st.markdown("#### Market Status")

    col1, col2, col3 = st.columns(3)

    # Check US market status
    try:
        is_us_open = calendars.is_market_open("XNYS")

        with col1:
            if is_us_open:
                st.markdown("🟢 **US Markets**: Open")
            else:
                st.markdown("🔴 **US Markets**: Closed")

    except Exception:
        with col1:
            st.markdown("⚪ **US Markets**: Unknown")

    # Check holidays
    try:
        todays_holidays = calendars.get_todays_holidays()

        with col2:
            if not todays_holidays.empty:
                st.markdown("📅 **Today's Holidays**:")
                for _, row in todays_holidays.iterrows():
                    st.caption(f"- {row['region']}: {row['holiday']}")
            else:
                st.markdown("📅 **No holidays today**")

    except Exception:
        with col2:
            st.markdown("⚪ **Holiday data unavailable**")

    # Upcoming holidays
    try:
        upcoming = calendars.get_upcoming_holidays(days=7)

        with col3:
            if not upcoming.empty:
                st.markdown("🗓️ **Upcoming Holidays (7d)**:")
                for _, row in upcoming.head(3).iterrows():
                    date_str = row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date'])
                    st.caption(f"- {date_str}: {row['region']} ({row['holiday']})")
            else:
                st.markdown("🗓️ **No upcoming holidays**")

    except Exception:
        with col3:
            st.markdown("⚪ **Upcoming holidays unavailable**")