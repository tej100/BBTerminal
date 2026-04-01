"""
Alerts Panel Component
Key Risk Indicators (KRI) monitoring
"""
import streamlit as st
import pandas as pd
from data.kri_checker import KRIChecker
from data.calendars import CalendarFetcher
from config.kri_config import KRI_CONFIG


def render_alerts_panel():
    """Render KRI panel"""
    st.markdown("### KRIs")

    kri_checker = KRIChecker()
    tab1, tab2 = st.tabs(["Active", "All KRIs"])

    with st.spinner("Checking..."):
        alerts = kri_checker.check_all()

    with tab1:
        _render_active(alerts)

    with tab2:
        _render_all_kris()


def _render_active(alerts: list):
    """Render triggered KRIs"""
    if not alerts:
        st.success("✓ No KRI alerts")
        return

    st.markdown(f"**{len(alerts)} triggered**")

    high_alerts = [a for a in alerts if a.severity == 'high']
    low_alerts = [a for a in alerts if a.severity == 'low']

    if high_alerts:
        st.markdown("**🔴 High Priority:**")
        for a in high_alerts:
            desc = f" — *{a.description}*" if a.description else ""
            st.markdown(f"<span style='color:#f85149'>**{a.ticker}**</span> — {a.message}{desc}",
                       unsafe_allow_html=True)

    if low_alerts:
        st.markdown("**🟡 Low Priority:**")
        for a in low_alerts:
            desc = f" — *{a.description}*" if a.description else ""
            st.markdown(f"<span style='color:#d4941e'>**{a.ticker}**</span> — {a.message}{desc}",
                       unsafe_allow_html=True)


def _render_all_kris():
    """Render all KRIs status"""
    st.markdown("**Tier 1 KRIs**")

    rows = []
    for name, config in KRI_CONFIG.items():
        ticker_str = config.get("ticker", config.get("tickers", "?"))
        low = config.get("low_threshold", "-")
        high = config.get("high_threshold", "-")
        lookback = config.get("lookback", 30)

        rows.append({
            "KRI": name.replace("_", " ").title(),
            "Watch": ticker_str,
            "Low": low,
            "High": high,
            "Metric": config["metric"],
            "Lookback": f"{lookback}d" if config["metric"] in ("z_score", "z_score_abs") else "-",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    st.caption("Add new KRIs in config/kri_config.py")


def render_market_status():
    """Render market status"""
    calendars = CalendarFetcher()
    st.markdown("### Market Status")

    try:
        is_us_open = calendars.is_market_open("XNYS")
        status = "✓ OPEN" if is_us_open else "✗ CLOSED"
        st.markdown(f"**US Markets: {status}**")
    except Exception:
        st.markdown("**? US Markets: ?**")

    try:
        holidays = calendars.get_todays_holidays()
        if not holidays.empty:
            st.markdown("**Today's Holidays:**")
            for _, row in holidays.iterrows():
                st.markdown(f"• {row['region']}: {row['holiday']}")
    except Exception:
        pass