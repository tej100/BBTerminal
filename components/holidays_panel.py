"""
Holidays Panel Component
Global exchange holiday calendar
"""
import streamlit as st
import pandas as pd
from datetime import date
from data.calendars import CalendarFetcher


def render_holidays_panel():
    """Render the holidays panel with tabular format"""
    st.markdown("### Holidays")

    calendars = CalendarFetcher()

    # Filter by region
    regions = ['All', 'US', 'UK', 'JP', 'DE', 'HK', 'CN']
    selected_region = st.selectbox("Region", regions, label_visibility="collapsed", key="holiday_region")

    try:
        # Get upcoming holidays (60 days)
        df = calendars.get_upcoming_holidays(days=60)

        if df.empty:
            st.info("No holiday data available")
            return

        # Filter by region if selected
        if selected_region != 'All':
            df = df[df['region'] == selected_region]

        if df.empty:
            st.info(f"No upcoming holidays for {selected_region}")
            return

        # Format for display
        df = df.rename(columns={
            'region': 'Region',
            'exchange': 'Market',
            'holiday': 'Holiday'
        })

        # Format date
        df['Date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else str(x))

        # Add "Days Away" column
        today = date.today()
        df['Days'] = df['date'].apply(lambda x: (x - today).days if hasattr(x, '__sub__') else 0)

        # Select and order columns
        display_df = df[['Date', 'Days', 'Region', 'Market', 'Holiday']].copy()
        display_df['Days'] = display_df['Days'].apply(lambda x: f"+{x}" if x > 0 else "Today")

        # Style by region
        def _color_region_column(series):
            region_colors = {
                'US': '#58a6ff',   # Blue
                'UK': '#3fb950',   # Green
                'JP': '#f85149',   # Red
                'DE': '#d29922',   # Yellow/Orange
                'HK': '#a371f7',   # Purple
                'CN': '#ff6b00',   # Orange
            }
            colors = []
            for val in series:
                colors.append(f'color: {region_colors.get(val, "#8b949e")}')
            return colors

        styled_df = display_df.style.apply(_color_region_column, subset=['Region'])

        st.dataframe(
            styled_df,
            width='stretch',
            hide_index=True,
            column_config={
                'Date': st.column_config.TextColumn(width='small'),
                'Days': st.column_config.TextColumn(width='small'),
                'Region': st.column_config.TextColumn(width='small'),
                'Market': st.column_config.TextColumn(width='small'),
                'Holiday': st.column_config.TextColumn(width='large')
            }
        )

    except Exception as e:
        st.error(f"Error loading holidays: {str(e)}")