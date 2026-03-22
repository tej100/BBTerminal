"""
Commodities Panel Component
Commodity prices and performance
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.commodities import CommoditiesFetcher
from utils.formatters import format_price, format_percent


def render_commodities_panel():
    """Render the commodities panel"""
    st.markdown("### Commodities")

    commodities = CommoditiesFetcher()

    # Tabs for different views
    tab1, tab2 = st.tabs(["Overview", "Details"])

    with tab1:
        _render_commodities_overview(commodities)

    with tab2:
        _render_commodities_details(commodities)


def _render_commodities_overview(commodities: CommoditiesFetcher):
    """Render commodities overview grid"""
    st.markdown("#### Commodity Prices")

    try:
        prices_data = commodities.get_current_prices()

        if prices_data.empty:
            st.info("Commodity data not available")
            return

        # Create a grid layout
        cols = st.columns(3)

        for idx, row in prices_data.iterrows():
            col_idx = idx % 3

            with cols[col_idx]:
                price = row['price']
                change_pct = row['change_pct']
                name = row['name']
                ticker = row['ticker']

                # Color based on change
                delta_color = "normal"
                if change_pct > 0:
                    delta_color = "normal"
                elif change_pct < 0:
                    delta_color = "normal"

                st.metric(
                    name,
                    f"${price:,.2f}",
                    delta=f"{change_pct:+.2f}%",
                    delta_color="normal"
                )

    except Exception as e:
        st.error(f"Error loading commodity data: {str(e)}")


def _render_commodities_details(commodities: CommoditiesFetcher):
    """Render detailed commodity view with historical chart"""
    st.markdown("#### Commodity Details")

    # Select commodity
    commodity_options = {
        "Crude Oil (CL=F)": "CL=F",
        "Natural Gas (NG=F)": "NG=F",
        "Gold (GC=F)": "GC=F",
        "Silver (SI=F)": "SI=F",
        "Copper (HG=F)": "HG=F",
    }

    selected = st.selectbox("Select Commodity", list(commodity_options.keys()))
    ticker = commodity_options[selected]

    try:
        # Get historical data
        hist_data = commodities.get_historical(ticker, period="1mo")

        if hist_data.empty:
            st.info("Historical data not available")
            return

        # Create price chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hist_data.index,
            y=hist_data['Close'],
            mode='lines',
            name='Price',
            line=dict(color='#1f77b4', width=2)
        ))

        fig.update_layout(
            title=f"{selected} - 1 Month",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, width='stretch')

        # Statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            current = hist_data['Close'].iloc[-1]
            st.metric("Current", f"${current:,.2f}")

        with col2:
            high_30d = hist_data['Close'].max()
            st.metric("30D High", f"${high_30d:,.2f}")

        with col3:
            low_30d = hist_data['Close'].min()
            st.metric("30D Low", f"${low_30d:,.2f}")

        with col4:
            change = hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[0]
            change_pct = (change / hist_data['Close'].iloc[0]) * 100
            st.metric("30D Change", f"{change_pct:+.2f}%")

    except Exception as e:
        st.error(f"Error loading commodity details: {str(e)}")