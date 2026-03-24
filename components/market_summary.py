"""
Market Summary Row Component
Bloomberg Launchpad style top row with key indices - Compact version
"""
import streamlit as st
import pandas as pd
import yfinance as yf
from typing import Dict, Union
from data.equities import EquitiesFetcher
from data.commodities import CommoditiesFetcher


# Treasury yield tickers from yfinance (real-time)
TREASURY_YIELD_TICKERS = {
    "^TNX": ("10Y Treasury", "10Y"),
    "^FVX": ("5Y Treasury", "5Y"),
    "^TYX": ("30Y Treasury", "30Y"),
    "^IRX": ("3M Treasury", "3M"),
}


def _fetch_treasury_yields():
    """Fetch live treasury yields from yfinance"""
    try:
        tickers = list(TREASURY_YIELD_TICKERS.keys())
        data = yf.download(tickers, period="2d", progress=False, auto_adjust=False)

        if data.empty:
            return {}

        results = {}
        for ticker, (name, maturity) in TREASURY_YIELD_TICKERS.items():
            try:
                # Get close prices
                if len(tickers) == 1:
                    closes = data['Close']
                else:
                    closes = data['Close'][ticker]

                if len(closes) >= 2:
                    latest = closes.iloc[-1]
                    previous = closes.iloc[-2]
                    change = latest - previous

                    results[maturity] = {
                        'name': name,
                        'value': round(latest, 3),
                        'change': round(change, 3)
                    }
            except Exception:
                continue

        return results
    except Exception:
        return {}


def render_market_summary():
    """Render the market summary row at the top of the dashboard"""
    # Create columns for major indices - 6 columns
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # Initialize fetchers
    equities = EquitiesFetcher()
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

        # VIX
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


def _render_index_card(data: Union[Dict, pd.Series], name: str, is_vix: bool = False):
    """Render a single index card using compact metric"""
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
        st.metric(
            name,
            f"{price:.1f}",
            delta=f"{change_pct:+.1f}%",
            delta_color="normal"
        )
    else:
        st.metric(
            name,
            f"{price:,.2f}",
            delta=f"{change_pct:+.2f}%",
            delta_color="normal"
        )


def _render_commodity_card(data: pd.Series, name: str):
    """Render a single commodity card"""
    price = data.get('price', 0)
    change_pct = data.get('change_pct', 0)

    st.metric(
        name,
        f"${price:,.2f}",
        delta=f"{change_pct:+.2f}%",
        delta_color="normal"
    )


def render_quick_stats():
    """Render quick stats row with live treasury yields from yfinance"""
    col1, col2, col3, col4 = st.columns(4)

    yields = _fetch_treasury_yields()

    try:
        # 3M Treasury
        with col1:
            if '3M' in yields:
                data = yields['3M']
                st.metric(
                    "3M Treasury",
                    f"{data['value']:.2f}%",
                    delta=f"{data['change']:+.2f}",
                    delta_color="inverse"
                )
            else:
                st.metric("3M Treasury", "N/A")

        # 5Y Treasury
        with col2:
            if '5Y' in yields:
                data = yields['5Y']
                st.metric(
                    "5Y Treasury",
                    f"{data['value']:.2f}%",
                    delta=f"{data['change']:+.2f}",
                    delta_color="inverse"
                )
            else:
                st.metric("5Y Treasury", "N/A")

        # 10Y Treasury
        with col3:
            if '10Y' in yields:
                data = yields['10Y']
                st.metric(
                    "10Y Treasury",
                    f"{data['value']:.2f}%",
                    delta=f"{data['change']:+.2f}",
                    delta_color="inverse"
                )
            else:
                st.metric("10Y Treasury", "N/A")

        # 30Y Treasury
        with col4:
            if '30Y' in yields:
                data = yields['30Y']
                st.metric(
                    "30Y Treasury",
                    f"{data['value']:.2f}%",
                    delta=f"{data['change']:+.2f}",
                    delta_color="inverse"
                )
            else:
                st.metric("30Y Treasury", "N/A")

    except Exception as e:
        st.warning("Treasury yield data temporarily unavailable")