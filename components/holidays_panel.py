"""
Holidays Panel Component
Global holiday calendar sidebar
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from data.calendars import CalendarFetcher
from config.settings import EXCHANGE_CALENDARS


def render_holidays_panel():
    """Render the holidays sidebar panel"""
    st.markdown("### Global Holidays")

    calendars = CalendarFetcher()

    # Today's holidays
    st.markdown("#### Today's Holidays")
    try:
        todays_holidays = calendars.get_todays_holidays()

        if todays_holidays.empty:
            st.success("No market holidays today")
        else:
            for _, row in todays_holidays.iterrows():
                st.markdown(f"🚫 **{row['region']}**: {row['holiday']}")

    except Exception as e:
        st.warning(f"Unable to fetch today's holidays: {str(e)}")

    st.markdown("---")

    # Upcoming holidays
    st.markdown("#### Upcoming Holidays (Next 30 Days)")
    try:
        upcoming = calendars.get_upcoming_holidays(days=30)

        if upcoming.empty:
            st.info("No upcoming holidays in the next 30 days")
        else:
            # Group by region
            for region in EXCHANGE_CALENDARS.keys():
                region_holidays = upcoming[upcoming['region'] == region]

                if not region_holidays.empty:
                    st.markdown(f"**{region}**")

                    for _, row in region_holidays.head(5).iterrows():
                        date_str = row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date'])
                        st.caption(f"• {date_str}: {row['holiday']}")

    except Exception as e:
        st.warning(f"Unable to fetch upcoming holidays: {str(e)}")

    st.markdown("---")

    # Market status
    st.markdown("#### Market Status Today")

    for region, exchange_code in EXCHANGE_CALENDARS.items():
        try:
            is_open = calendars.is_market_open(exchange_code)

            if is_open:
                st.markdown(f"🟢 {region}: Open")
            else:
                st.markdown(f"🔴 {region}: Closed")

        except Exception:
            st.markdown(f"⚪ {region}: Unknown")


def render_compact_holidays():
    """Render a compact version of holidays for sidebar"""
    calendars = CalendarFetcher()

    # Today's holidays in compact format
    try:
        todays_holidays = calendars.get_todays_holidays()

        if not todays_holidays.empty:
            st.markdown("**🔴 Today's Holidays:**")
            for _, row in todays_holidays.iterrows():
                st.caption(f"{row['region']}: {row['holiday']}")
        else:
            st.markdown("**✅ No holidays today**")

    except Exception:
        st.markdown("**⚪ Holiday data unavailable**")

    # Quick check for upcoming
    try:
        upcoming = calendars.get_upcoming_holidays(days=7)

        if not upcoming.empty:
            st.markdown("**📅 This Week:**")
            for _, row in upcoming.head(3).iterrows():
                date_str = row['date'].strftime('%m/%d') if hasattr(row['date'], 'strftime') else str(row['date'])
                st.caption(f"{date_str}: {row['region']}")

    except Exception:
        pass