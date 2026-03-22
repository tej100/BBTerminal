"""
Equities Panel Component
Sector heatmap and top movers
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.equities import EquitiesFetcher
from data.calendars import CalendarFetcher
from utils.calculations import calculate_volatility, calculate_zscore
from utils.formatters import format_price, format_percent
from config.settings import EQUITY_INDICES, SECTOR_ETFS, KEY_STOCKS


def render_equities_panel():
    """Render the equities panel with sector performance"""
    st.markdown("### Equities")

    equities = EquitiesFetcher()
    calendars = CalendarFetcher()

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Sectors", "Key Stocks", "Corporate Actions"])

    with tab1:
        _render_sector_heatmap(equities)

    with tab2:
        _render_key_stocks(equities)

    with tab3:
        _render_corporate_actions(calendars)


def _render_sector_heatmap(equities: EquitiesFetcher):
    """Render sector performance as a heatmap-style table"""
    st.markdown("#### Sector Performance")

    try:
        sector_data = equities.get_sector_performance()

        if sector_data.empty:
            st.info("Sector data not available")
            return

        # Create styled dataframe
        df = sector_data[['name', 'price', 'change', 'change_pct']].copy()
        df.columns = ['Sector', 'Price', 'Change ($)', 'Change (%)']

        # Style based on performance
        def color_change(val):
            if val > 0:
                return 'color: green'
            elif val < 0:
                return 'color: red'
            return ''

        # Display with conditional formatting
        st.dataframe(
            df.style.map(
                lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0
                else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''),
                subset=['Change ($)', 'Change (%)']
            ),
            width='stretch',
            hide_index=True
        )

        # Create a simple bar chart of sector performance
        fig = go.Figure(data=[
            go.Bar(
                x=df['Sector'],
                y=df['Change (%)'],
                marker_color=['green' if x > 0 else 'red' for x in df['Change (%)']],
                text=[f"{x:+.2f}%" for x in df['Change (%)']],
                textposition='outside'
            )
        ])

        fig.update_layout(
            title="Sector Performance (%)",
            xaxis_title="",
            yaxis_title="Change (%)",
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, width='stretch')

    except Exception as e:
        st.error(f"Error loading sector data: {str(e)}")


def _render_key_stocks(equities: EquitiesFetcher):
    """Render key stocks performance"""
    st.markdown("#### Key Stocks")

    try:
        stocks_data = equities.get_current_prices(KEY_STOCKS)

        if stocks_data.empty:
            st.info("Stock data not available")
            return

        df = stocks_data[['ticker', 'name', 'price', 'change', 'change_pct']].copy()
        df.columns = ['Ticker', 'Name', 'Price', 'Change ($)', 'Change (%)']

        st.dataframe(
            df.style.map(
                lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0
                else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''),
                subset=['Change ($)', 'Change (%)']
            ),
            width='stretch',
            hide_index=True
        )

    except Exception as e:
        st.error(f"Error loading stock data: {str(e)}")


def _render_corporate_actions(calendars: CalendarFetcher):
    """Render recent corporate actions for tracked stocks"""
    st.markdown("#### Recent Corporate Actions")

    all_tickers = list(SECTOR_ETFS.keys()) + KEY_STOCKS

    try:
        actions = calendars.get_recent_corporate_actions(all_tickers, days=30)

        if actions.empty:
            st.info("No recent corporate actions found")
            return

        # Display actions
        for _, row in actions.iterrows():
            date = row.get('date', '')
            ticker = row.get('ticker', '')
            dividends = row.get('Dividends', 0)
            splits = row.get('Stock Splits', 0)

            if dividends > 0:
                st.write(f"📅 {date} - **{ticker}** Dividend: ${dividends:.2f}")

            if splits != 0 and splits != 1:
                st.write(f"📅 {date} - **{ticker}** Stock Split: {splits}")

    except Exception as e:
        st.error(f"Error loading corporate actions: {str(e)}")