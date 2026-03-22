"""
Market Summary Row Component
Bloomberg Launchpad style top row with key indices
"""
import streamlit as st
import pandas as pd
from typing import Dict, Union
from data.equities import EquitiesFetcher
from data.rates import RatesFetcher
from data.commodities import CommoditiesFetcher
from utils.formatters import format_price, format_percent, get_change_color


def render_market_summary():
    """Render the market summary row at the top of the dashboard"""
    st.markdown("### Market Overview")

    # Create columns for major indices
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # Initialize fetchers
    equities = EquitiesFetcher()
    rates = RatesFetcher()
    commodities = CommoditiesFetcher()

    # Fetch data
    try:
        indices_data = equities.get_indices_performance()
        oil_data = commodities.get_current_prices(['CL=F'])
        gold_data = commodities.get_current_prices(['GC=F'])

        # Create index mapping
        indices_map = {row['ticker']: row for _, row in indices_data.iterrows()}

        # SPY
        with col1:
            _render_index_card(indices_map.get('SPY', {}), "S&P 500")

        # QQQ
        with col2:
            _render_index_card(indices_map.get('QQQ', {}), "Nasdaq 100")

        # IWM
        with col3:
            _render_index_card(indices_map.get('IWM', {}), "Russell 2000")

        # VIX (ticker is ^VIX but display name is VIX)
        with col4:
            _render_index_card(indices_map.get('^VIX', {}), "VIX", is_vix=True)

        # Oil
        with col5:
            if not oil_data.empty:
                row = oil_data.iloc[0]
                _render_commodity_card(row, "Crude Oil")
            else:
                st.metric("Crude Oil", "N/A")

        # Gold
        with col6:
            if not gold_data.empty:
                row = gold_data.iloc[0]
                _render_commodity_card(row, "Gold")
            else:
                st.metric("Gold", "N/A")

    except Exception as e:
        st.error(f"Error loading market summary: {str(e)}")
        st.info("Market data may not be available during market closed hours or due to API limits.")


def _render_index_card(data: Union[Dict, pd.Series], name: str, is_vix: bool = False):
    """Render a single index card"""
    # Handle both empty dict and empty Series
    if isinstance(data, pd.Series):
        if data.empty:
            st.metric(name, "N/A")
            return
    elif not data:
        st.metric(name, "N/A")
        return

    price = data.get('price', 0)
    change_pct = data.get('change_pct', 0)

    if is_vix:
        # VIX - just show level
        st.metric(
            name,
            f"{price:.1f}",
            delta=f"{change_pct:+.1f}%"
        )
    else:
        st.metric(
            name,
            f"{price:,.2f}",
            delta=f"{change_pct:+.2f}%"
        )


def _render_commodity_card(data: pd.Series, name: str):
    """Render a single commodity card"""
    price = data.get('price', 0)
    change_pct = data.get('change_pct', 0)

    st.metric(
        name,
        f"${price:,.2f}",
        delta=f"{change_pct:+.2f}%"
    )


def render_quick_stats():
    """Render quick stats row below market summary"""
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    rates = RatesFetcher()

    try:
        # Get key rates
        ten_year = rates.get_latest_rate("GS10")
        two_year = rates.get_latest_rate("GS2")
        fed_funds = rates.get_latest_rate("FEDFUNDS")

        with col1:
            if ten_year:
                st.metric("10Y Treasury", f"{ten_year['value']:.2f}%",
                         delta=f"{ten_year['change']:+.2f}")

        with col2:
            if two_year:
                st.metric("2Y Treasury", f"{two_year['value']:.2f}%",
                         delta=f"{two_year['change']:+.2f}")

        with col3:
            if ten_year and two_year:
                spread = (ten_year['value'] - two_year['value']) * 100
                st.metric("2Y-10Y Spread", f"{spread:.0f} bps")

        with col4:
            if fed_funds:
                st.metric("Fed Funds", f"{fed_funds['value']:.2f}%",
                         delta=f"{fed_funds['change']:+.2f}")

    except Exception as e:
        st.warning("Rate data temporarily unavailable")