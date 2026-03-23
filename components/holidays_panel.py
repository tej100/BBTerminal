"""
Holidays Panel Component
Global holiday calendar sidebar - Compact version
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from data.calendars import CalendarFetcher
from config.settings import EXCHANGE_CALENDARS


def render_holidays_panel():
    """Render the holidays sidebar panel"""
    st.markdown("### Holidays")

    calendars = CalendarFetcher()

    # Upcoming holidays
    st.markdown("#### Upcoming (30d)")
    try:
        upcoming = calendars.get_upcoming_holidays(days=30)

        if upcoming.empty:
            st.info("No upcoming holidays")
        else:
            # Compact list
            for _, row in upcoming.head(10).iterrows():
                date_str = row['date'].strftime('%m/%d') if hasattr(row['date'], 'strftime') else str(row['date'])
                st.caption(f"{date_str} - {row['region']}: {row['holiday']}")

    except Exception as e:
        st.warning(f"Unable to fetch holidays")


def render_compact_holidays():
    """Render a compact version of holidays for sidebar"""
    calendars = CalendarFetcher()

    # Today's holidays
    try:
        todays_holidays = calendars.get_todays_holidays()

        if not todays_holidays.empty:
            st.markdown("**Holidays Today:**")
            for _, row in todays_holidays.iterrows():
                st.caption(f"{row['region']}: {row['holiday']}")
        else:
            st.markdown("**No holidays today**")

    except Exception:
        st.markdown("**Holiday data unavailable**")

    # Upcoming
    try:
        upcoming = calendars.get_upcoming_holidays(days=7)

        if not upcoming.empty:
            st.markdown("**This Week:**")
            for _, row in upcoming.head(3).iterrows():
                date_str = row['date'].strftime('%m/%d') if hasattr(row['date'], 'strftime') else str(row['date'])
                st.caption(f"{date_str}: {row['region']}")

    except Exception:
        pass