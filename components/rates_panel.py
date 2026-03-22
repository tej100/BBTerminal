"""
Interest Rates Panel Component
Yield curve and key rates display
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.rates import RatesFetcher
from utils.formatters import format_yield, format_basis_points
from utils.calculations import calculate_yield_curve_slope


def render_rates_panel():
    """Render the interest rates panel"""
    st.markdown("### Interest Rates")

    rates = RatesFetcher()

    # Tabs for different views
    tab1, tab2 = st.tabs(["Yield Curve", "Key Rates"])

    with tab1:
        _render_yield_curve(rates)

    with tab2:
        _render_key_rates(rates)


def _render_yield_curve(rates: RatesFetcher):
    """Render yield curve visualization"""
    st.markdown("#### US Treasury Yield Curve")

    try:
        yield_curve = rates.get_yield_curve()

        if yield_curve.empty:
            st.info("Yield curve data not available")
            return

        # Create yield curve plot
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=yield_curve['maturity'],
            y=yield_curve['rate'],
            mode='lines+markers',
            name='Current',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title="US Treasury Yield Curve",
            xaxis_title="Maturity",
            yaxis_title="Yield (%)",
            height=400,
            showlegend=False,
            xaxis=dict(
                categoryorder='array',
                categoryarray=['3M', '6M', '1Y', '2Y', '5Y', '10Y', '30Y']
            )
        )

        st.plotly_chart(fig, width='stretch')

        # Add key spreads
        col1, col2, col3 = st.columns(3)

        rates_data = yield_curve.to_dict('records')
        rates_dict = {r['maturity']: r['rate'] for r in rates_data}

        with col1:
            if '2Y' in rates_dict and '10Y' in rates_dict:
                spread = rates_dict['10Y'] - rates_dict['2Y']
                st.metric("2Y-10Y Spread", f"{spread*100:.0f} bps")
                if spread < 0:
                    st.caption("⚠️ Inverted yield curve")

        with col2:
            if '3M' in rates_dict and '10Y' in rates_dict:
                spread = rates_dict['10Y'] - rates_dict['3M']
                st.metric("3M-10Y Spread", f"{spread*100:.0f} bps")

        with col3:
            if '2Y' in rates_dict and '30Y' in rates_dict:
                spread = rates_dict['30Y'] - rates_dict['2Y']
                st.metric("2Y-30Y Spread", f"{spread*100:.0f} bps")

    except Exception as e:
        st.error(f"Error loading yield curve: {str(e)}")
        st.info("Ensure FRED_API_KEY is set in .env file")


def _render_key_rates(rates: RatesFetcher):
    """Render key interest rates table"""
    st.markdown("#### Key Interest Rates")

    try:
        rates_data = rates.get_all_rates()

        if rates_data.empty:
            st.info("Rate data not available")
            return

        df = rates_data[['name', 'value', 'change', 'date']].copy()
        df.columns = ['Rate', 'Value (%)', 'Change', 'Last Updated']

        # Color the change column
        def style_change(val):
            if val > 0:
                return 'color: green'
            elif val < 0:
                return 'color: red'
            return ''

        st.dataframe(
            df.style.map(
                lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0
                else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''),
                subset=['Change']
            ),
            width='stretch',
            hide_index=True
        )

    except Exception as e:
        st.error(f"Error loading rate data: {str(e)}")
        st.info("Ensure FRED_API_KEY is set in .env file")