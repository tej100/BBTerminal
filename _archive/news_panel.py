"""
News Panel Component
Displays corporate news from TickerTick API
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from typing import List, Optional
from data.news import NewsFetcher


def render_news_panel(tickers: Optional[List[str]] = None, show_category_filter: bool = True):
    """
    Render the corporate news panel

    Args:
        tickers: Optional list of tickers to filter news by
        show_category_filter: Whether to show category filter dropdown
    """
    st.markdown("### Corporate News")

    fetcher = NewsFetcher()

    # Category filter
    categories = ["All", "Leadership", "Acquisition", "Bankruptcy", "Buyback", "SEC Filings"]
    selected_category = "All"

    if show_category_filter:
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_category = st.selectbox(
                "Category",
                categories,
                key="news_category_filter",
                label_visibility="collapsed"
            )

    # Fetch news based on category
    with st.spinner("Loading news..."):
        if selected_category == "SEC Filings":
            df = fetcher.get_sec_filings(tickers, limit=30)
        elif selected_category == "All":
            df = fetcher.get_corporate_news(tickers, limit=50)
        else:
            df = fetcher.get_corporate_news(tickers, limit=50)
            if not df.empty:
                # Filter by selected category
                df = fetcher.categorize_news(df)
                df = df[df['category'] == selected_category]

    if df.empty:
        st.info("No corporate news found")
        return

    # Add category labels if showing all
    if selected_category == "All":
        df = fetcher.categorize_news(df)

    # Render news items
    _render_news_list(df, limit=15)


def render_compact_news(tickers: Optional[List[str]] = None, limit: int = 10):
    """
    Render a compact news view for sidebar or small panels

    Args:
        tickers: Optional list of tickers to filter by
        limit: Maximum number of items to show
    """
    st.markdown("#### Recent News")

    fetcher = NewsFetcher()

    with st.spinner("Loading..."):
        df = fetcher.get_corporate_news(tickers, limit=limit)

    if df.empty:
        st.caption("No recent news")
        return

    # Add categories
    df = fetcher.categorize_news(df)

    for _, row in df.head(limit).iterrows():
        _render_news_item_compact(row)


def render_ticker_news(ticker: str, limit: int = 10):
    """
    Render news for a specific ticker (detailed view)

    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of items to show
    """
    st.markdown(f"### News for {ticker.upper()}")

    fetcher = NewsFetcher()

    tab1, tab2, tab3 = st.tabs(["All News", "SEC Filings", "Corporate Events"])

    with tab1:
        with st.spinner("Loading..."):
            df = fetcher.get_ticker_news(ticker, limit=limit)
        _render_news_list(df, limit=limit)

    with tab2:
        with st.spinner("Loading..."):
            df = fetcher.get_sec_filings(tickers=[ticker], limit=limit)
        _render_news_list(df, limit=limit, show_tickers=False)

    with tab3:
        with st.spinner("Loading..."):
            df = fetcher.get_corporate_news(tickers=[ticker], limit=limit)
        if not df.empty:
            df = fetcher.categorize_news(df)
        _render_news_list(df, limit=limit, show_tickers=False, show_category=True)


def _render_news_list(df: pd.DataFrame, limit: int = 15, show_tickers: bool = True, show_category: bool = False):
    """Render a list of news items"""
    if df.empty:
        st.info("No news available")
        return

    for i, row in df.head(limit).iterrows():
        _render_news_item(row, show_tickers=show_tickers, show_category=show_category)


def _render_news_item(row: pd.Series, show_tickers: bool = True, show_category: bool = False):
    """Render a single news item"""
    title = row.get('title', 'No title')
    publisher = row.get('publisher', 'Unknown')
    link = row.get('link', '')
    published = row.get('published')
    tickers = row.get('tickers', [])
    category = row.get('category', '')

    # Format time
    time_str = ""
    if published:
        try:
            if isinstance(published, datetime):
                diff = datetime.now(timezone.utc) - published
                if diff.days > 0:
                    time_str = f"{diff.days}d ago"
                elif diff.seconds >= 3600:
                    time_str = f"{diff.seconds // 3600}h ago"
                else:
                    time_str = f"{diff.seconds // 60}m ago"
        except Exception:
            pass

    # Build display line
    meta_parts = []
    if time_str:
        meta_parts.append(f"<span style='color:#8b949e'>{time_str}</span>")
    if publisher:
        meta_parts.append(f"<span style='color:#58a6ff'>{publisher}</span>")
    if show_tickers and tickers:
        ticker_str = ", ".join(tickers[:3])
        meta_parts.append(f"<span style='color:#7ee787'>{ticker_str}</span>")
    if show_category and category:
        category_colors = {
            "Leadership": "#f0883e",
            "Acquisition": "#a371f7",
            "Bankruptcy": "#f85149",
            "Buyback": "#3fb950",
            "SEC Filing": "#79c0ff",
        }
        color = category_colors.get(category, "#8b949e")
        meta_parts.append(f"<span style='color:{color}'>[{category}]</span>")

    meta_html = " • ".join(meta_parts)

    # Render
    if link:
        st.markdown(
            f"**[{title}]({link})**",
            unsafe_allow_html=True
        )
    else:
        st.markdown(f"**{title}**")

    if meta_html:
        st.markdown(f"<div style='font-size:0.75rem;margin-top:-0.25rem'>{meta_html}</div>", unsafe_allow_html=True)


def _render_news_item_compact(row: pd.Series):
    """Render a compact news item for sidebar"""
    title = row.get('title', 'No title')
    link = row.get('link', '')
    category = row.get('category', '')
    published = row.get('published')

    # Truncate title
    if len(title) > 60:
        title = title[:57] + "..."

    # Format time
    time_str = ""
    if published:
        try:
            if isinstance(published, datetime):
                diff = datetime.now(timezone.utc) - published
                if diff.days > 0:
                    time_str = f"{diff.days}d"
                elif diff.seconds >= 3600:
                    time_str = f"{diff.seconds // 3600}h"
                else:
                    time_str = f"{diff.seconds // 60}m"
        except Exception:
            pass

    # Category indicator
    category_indicator = ""
    if category:
        category_colors = {
            "Leadership": "🟠",
            "Acquisition": "🟣",
            "Bankruptcy": "🔴",
            "Buyback": "🟢",
            "SEC Filing": "🔵",
        }
        category_indicator = category_colors.get(category, "⚪")

    # Render as compact line
    if link:
        st.markdown(
            f"<div style='font-size:0.75rem'>{category_indicator} [{title}]({link}) <span style='color:#8b949e'>({time_str})</span></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='font-size:0.75rem'>{category_indicator} {title} <span style='color:#8b949e'>({time_str})</span></div>",
            unsafe_allow_html=True
        )