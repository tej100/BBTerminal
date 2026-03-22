"""
Economic Data Panel Component
Key economic indicators
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.economic import EconomicFetcher
from utils.formatters import format_number


def render_economic_panel():
    """Render the economic indicators panel"""
    st.markdown("### Economic Indicators")

    economic = EconomicFetcher()

    # Tabs for different views
    tab1, tab2 = st.tabs(["Key Indicators", "Historical"])

    with tab1:
        _render_key_indicators(economic)

    with tab2:
        _render_historical_view(economic)


def _render_key_indicators(economic: EconomicFetcher):
    """Render key economic indicators"""
    st.markdown("#### Current Economic Data")

    try:
        indicators = economic.get_all_indicators()

        if indicators.empty:
            st.info("Economic data not available")
            return

        # Create cards for each indicator
        cols = st.columns(2)

        for idx, row in indicators.iterrows():
            col_idx = idx % 2

            with cols[col_idx]:
                st.markdown(f"**{row['name']}**")
                st.markdown(f"Latest: **{row['value']:,.2f}**")
                st.caption(f"Updated: {row['date']}")

                if row['yoy_change'] is not None:
                    yoy_color = "green" if row['yoy_change'] > 0 else "red"
                    st.markdown(f"YoY: <span style='color:{yoy_color}'>{row['yoy_change']:+.2f}%</span>",
                               unsafe_allow_html=True)

                if row['mom_change'] is not None:
                    mom_color = "green" if row['mom_change'] > 0 else "red"
                    st.markdown(f"MoM: <span style='color:{mom_color}'>{row['mom_change']:+.2f}%</span>",
                               unsafe_allow_html=True)

                st.markdown("---")

    except Exception as e:
        st.error(f"Error loading economic data: {str(e)}")
        st.info("Ensure FRED_API_KEY is set in .env file")


def _render_historical_view(economic: EconomicFetcher):
    """Render historical economic data view"""
    st.markdown("#### Historical Trends")

    # Select indicator
    indicator_options = {
        "CPI": "CPIAUCSL",
        "Unemployment Rate": "UNRATE",
        "GDP": "GDP",
        "Non-Farm Payrolls": "PAYEMS",
    }

    selected = st.selectbox("Select Indicator", list(indicator_options.keys()))
    series_id = indicator_options[selected]

    try:
        hist_data = economic.get_historical(series_id, months=12)

        if hist_data.empty:
            st.info("Historical data not available")
            return

        # Create chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hist_data['date'],
            y=hist_data['value'],
            mode='lines+markers',
            name=selected,
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        ))

        fig.update_layout(
            title=f"{selected} - 12 Month Trend",
            xaxis_title="Date",
            yaxis_title=selected,
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, width='stretch')

        # Recent changes
        st.markdown("#### Recent Values")

        recent = hist_data.tail(6).iloc[::-1]  # Last 6 values, reversed

        for _, row in recent.iterrows():
            date = row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date'])
            value = row['value']

            st.write(f"**{date}**: {value:,.2f}")

    except Exception as e:
        st.error(f"Error loading historical data: {str(e)}")