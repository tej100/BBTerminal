"""
Mortgages Panel Component
Mortgage rates and spreads
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.mortgages import MortgagesFetcher
from data.rates import RatesFetcher
from utils.formatters import format_yield


def render_mortgages_panel():
    """Render the mortgages panel"""
    st.markdown("### Mortgage Rates")

    mortgages = MortgagesFetcher()

    # Tabs for different views
    tab1, tab2 = st.tabs(["Current Rates", "Historical Trend"])

    with tab1:
        _render_current_rates(mortgages)

    with tab2:
        _render_historical_trend(mortgages)


def _render_current_rates(mortgages: MortgagesFetcher):
    """Render current mortgage rates"""
    st.markdown("#### Current Mortgage Rates")

    try:
        rates_data = mortgages.get_all_rates()

        if rates_data.empty:
            st.info("Mortgage rate data not available")
            return

        df = rates_data[['name', 'value', 'change', 'date']].copy()
        df.columns = ['Mortgage Type', 'Rate (%)', 'Change', 'Last Updated']

        # Display rates
        st.dataframe(
            df.style.map(
                lambda x: 'color: green' if isinstance(x, (int, float)) and x < 0
                else ('color: red' if isinstance(x, (int, float)) and x > 0 else ''),
                subset=['Change']
            ),
            width='stretch',
            hide_index=True
        )

        # Show spread to 10Y Treasury
        st.markdown("#### Spreads to 10Y Treasury")

        rates = RatesFetcher()
        ten_year = rates.get_latest_rate("GS10")

        if ten_year:
            col1, col2, col3 = st.columns(3)

            for idx, row in rates_data.iterrows():
                spread = row['value'] - ten_year['value']
                name = row['name'].replace(" Mortgage", "").replace(" Fixed", "")

                with [col1, col2, col3][idx % 3]:
                    st.metric(
                        f"{name}",
                        f"{spread*100:.0f} bps",
                        delta=f"Rate: {row['value']:.2f}%"
                    )

    except Exception as e:
        st.error(f"Error loading mortgage data: {str(e)}")
        st.info("Ensure FRED_API_KEY is set in .env file")


def _render_historical_trend(mortgages: MortgagesFetcher):
    """Render historical mortgage rate trends"""
    st.markdown("#### 30-Day Trend")

    try:
        # Get historical data for 30Y fixed mortgage
        hist_data = mortgages.get_historical_rates("MORTGAGE30US", days=30)

        if hist_data.empty:
            st.info("Historical data not available")
            return

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hist_data['date'],
            y=hist_data['value'],
            mode='lines',
            name='30Y Fixed',
            line=dict(color='#1f77b4', width=2)
        ))

        fig.update_layout(
            title="30Y Fixed Mortgage Rate (30 Days)",
            xaxis_title="Date",
            yaxis_title="Rate (%)",
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, width='stretch')

        # Statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("30D High", f"{hist_data['value'].max():.3f}%")

        with col2:
            st.metric("30D Low", f"{hist_data['value'].min():.3f}%")

        with col3:
            st.metric("Current", f"{hist_data['value'].iloc[-1]:.3f}%")

    except Exception as e:
        st.error(f"Error loading historical data: {str(e)}")