"""
Market Summary Row Component
Bloomberg Launchpad style top row with key indices - Compact version
"""
import streamlit as st
import yfinance as yf
from config.settings import MARKET_SUMMARY_TICKERS


def _fetch_market_summary_data():
    """Fetch all tickers configured in MARKET_SUMMARY_TICKERS from yfinance"""
    tickers = list(MARKET_SUMMARY_TICKERS.keys())
    if not tickers:
        return {}

    try:
        data = yf.download(tickers, period="2d", progress=False, auto_adjust=False)
        if data.empty:
            return {}

        results = {}
        close_data = data['Close'] if 'Close' in data else None

        for ticker in tickers:
            try:
                if close_data is None:
                    continue

                if len(tickers) == 1:
                    closes = close_data
                else:
                    closes = close_data[ticker]

                closes = closes.dropna()
                if len(closes) < 2:
                    continue      

                results[ticker] = {
                    'latest': float(closes.iloc[-1]),
                    'previous': float(closes.iloc[-2]),
                }
            except Exception:
                continue

        return results
    except Exception:
        return {}


def _render_market_card(name: str, data: dict):
    """Render a single metric card for market summary tickers"""
    if not data:
        st.metric(name, "N/A")
        return

    latest = data.get('latest', 0)
    previous = data.get('previous', 0)

    # Interest Rate series should be in bps and inverted color scheme
    if name.endswith(" "):
        st.metric(
            name,
            f"{latest:.2f}%",
            delta=f"{latest-previous:+.2f}",
            delta_color="inverse"
        )
    else:
        st.metric(
            name,
            f"{latest:,.2f}",
            delta=f"{(latest / previous - 1) * 100 if previous != 0 else 0.0:+.2f}%",
            delta_color="normal"
    )


def render_market_summary():
    """Render the market summary row at the top of the dashboard"""
    tickers = list(MARKET_SUMMARY_TICKERS.keys())
    if not tickers:
        st.warning("No market summary tickers configured")
        return

    market_data = _fetch_market_summary_data()
    cols = st.columns(len(tickers), gap="small")

    for idx, ticker in enumerate(tickers):
        label = MARKET_SUMMARY_TICKERS.get(ticker, ticker)
        with cols[idx]:
            _render_market_card(label, market_data.get(ticker))