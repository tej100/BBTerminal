"""
News data fetcher using TickerTick API
Fetches corporate news: leadership changes, M&A, bankruptcy, buybacks, etc.
"""
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone
from typing import List, Optional
from data.fetcher import DataFetcher


# TickerTick API base URL
TICKERTICK_API = "https://api.tickertick.com/feed"

# Corporate event keywords for filtering
CORPORATE_EVENTS = {
    "leadership": ["ceo", "cfo", "cto", "coo", "president", "board", "director", "executive", "resign", "appoint", "step down"],
    "acquisition": ["acquire", "acquisition", "merger", "buyout", "takeover", "deal", "buy", "sell"],
    "bankruptcy": ["bankruptcy", "chapter 11", "chapter 7", "restructure", "debt", "default", "creditor"],
    "buyback": ["buyback", "buy back", "repurchase", "share repurchase", "dividend"],
}


# Streamlit-cached function for TickerTick news
@st.cache_data(ttl=300)
def _fetch_tickertick_feed(q: str, limit: int = 50) -> list:
    """
    Fetch news from TickerTick API directly via HTTP.
    Cached by Streamlit to prevent repeated API calls.

    Args:
        q: TickerTick query string
        limit: Number of stories to fetch (max 200)

    Returns:
        List of news stories (dicts)
    """
    try:
        params = {'q': q, 'n': limit}
        resp = requests.get(TICKERTICK_API, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get('stories', [])
    except Exception:
        return []


class NewsFetcher(DataFetcher):
    """Fetch corporate news from TickerTick API"""

    def __init__(self, cache_duration: int = 300):
        super().__init__(cache_duration)

    def get_sec_filings(self, tickers: Optional[List[str]] = None, limit: int = 50) -> pd.DataFrame:
        """
        Get SEC filings (8-K, etc.) for corporate events

        Args:
            tickers: Optional list of tickers to filter by
            limit: Maximum number of stories to return

        Returns:
            DataFrame with SEC filing news
        """
        # Build query - SEC filings with optional ticker filter
        if tickers:
            # SEC filings for specific tickers
            ticker_queries = [f"z:{t.lower()}" for t in tickers[:10]]  # Limit to 10 tickers
            if len(ticker_queries) == 1:
                q = f"and({ticker_queries[0]}, T:sec)"
            else:
                ticker_q = f"(or,{','.join(ticker_queries)})"
                q = f"and({ticker_q}, T:sec)"
        else:
            # All SEC filings
            q = "T:sec"

        news = _fetch_tickertick_feed(q, limit=limit)

        if not news:
            return pd.DataFrame()

        return self._parse_stories(news)

    def get_corporate_news(self, tickers: Optional[List[str]] = None, limit: int = 50) -> pd.DataFrame:
        """
        Get corporate news filtered for relevant events

        Args:
            tickers: Optional list of tickers to filter by
            limit: Maximum number of stories to return

        Returns:
            DataFrame with corporate news
        """
        # Build query for curated corporate news
        if tickers:
            ticker_queries = [f"tt:{t.lower()}" for t in tickers[:10]]
            if len(ticker_queries) == 1:
                q = f"and({ticker_queries[0]}, T:curated)"
            else:
                ticker_q = f"(or,{','.join(ticker_queries)})"
                q = f"and({ticker_q}, T:curated)"
        else:
            q = "T:curated"

        news = _fetch_tickertick_feed(q, limit=limit)

        if not news:
            return pd.DataFrame()

        df = self._parse_stories(news)

        # Filter for corporate events if we have data
        if not df.empty:
            df = self._filter_corporate_events(df)

        return df

    def get_ticker_news(self, ticker: str, limit: int = 20) -> pd.DataFrame:
        """
        Get all news for a specific ticker

        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of news items

        Returns:
            DataFrame with news articles
        """
        q = f"tt:{ticker.lower()}"
        news = _fetch_tickertick_feed(q, limit=limit)

        if not news:
            return pd.DataFrame()

        return self._parse_stories(news)

    def get_entity_news(self, entity: str, limit: int = 20) -> pd.DataFrame:
        """
        Get news matching an entity (e.g., CEO names, company names)

        Args:
            entity: Entity name to search for
            limit: Maximum number of stories

        Returns:
            DataFrame with matching news
        """
        # Format entity for TickerTick (lowercase, underscores)
        entity_formatted = entity.lower().replace(" ", "_")
        q = f"E:{entity_formatted}"

        news = _fetch_tickertick_feed(q, limit=limit)

        if not news:
            return pd.DataFrame()

        return self._parse_stories(news)

    def _parse_stories(self, stories: list) -> pd.DataFrame:
        """
        Parse TickerTick stories into a DataFrame

        Args:
            stories: List of story dictionaries from TickerTick

        Returns:
            DataFrame with parsed news data
        """
        results = []

        for story in stories:
            try:
                # TickerTick API response structure
                results.append({
                    'title': story.get('title', ''),
                    'publisher': story.get('site', 'Unknown'),
                    'link': story.get('url', ''),
                    'published': self._parse_timestamp(story.get('time')),
                    'tickers': [],  # TickerTick doesn't always include tickers in response
                    'summary': story.get('description', ''),
                    'story_id': story.get('id', ''),
                })
            except Exception:
                continue

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)

        # Sort by published date (newest first)
        if 'published' in df.columns and len(df['published'].dropna()) > 0:
            df = df.sort_values('published', ascending=False).reset_index(drop=True)

        return df

    def get_news_summary(self, ticker: str, days: int = 30) -> List[dict]:
        """
        Get a summary of recent news for a ticker (for backward compatibility)

        Args:
            ticker: Stock ticker symbol
            days: Number of days to look back (default 30)

        Returns:
            List of news summaries with title, source, time, link, summary
        """
        df = self.get_ticker_news(ticker, limit=50)

        if df.empty:
            return []

        # Filter by date if we have published dates
        cutoff_date = datetime.now(timezone.utc) - pd.Timedelta(days=days)

        summaries = []
        for _, row in df.iterrows():
            pub_time = row.get('published')

            # Filter by date
            if pub_time is not None:
                if pub_time.tzinfo is None:
                    pub_time = pub_time.tz_localize('UTC')
                if pub_time < cutoff_date:
                    continue

            # Calculate relative time
            time_str = ""
            if pub_time is not None:
                try:
                    now = pd.Timestamp.now(tz='UTC')
                    diff = now - pub_time

                    if diff.days > 0:
                        time_str = f"{diff.days}d ago"
                    elif diff.seconds >= 3600:
                        hours = diff.seconds // 3600
                        time_str = f"{hours}h ago"
                    elif diff.seconds >= 60:
                        minutes = diff.seconds // 60
                        time_str = f"{minutes}m ago"
                    else:
                        time_str = "Just now"
                except Exception:
                    time_str = ""

            summaries.append({
                'title': row.get('title', ''),
                'publisher': row.get('publisher', 'Unknown'),
                'link': row.get('link', ''),
                'time': time_str,
                'summary': row.get('summary', ''),
                'published': pub_time,
            })

        return summaries

    def _parse_timestamp(self, ts) -> Optional[datetime]:
        """Parse TickerTick timestamp"""
        if not ts:
            return None

        try:
            # TickerTick uses Unix timestamp in milliseconds
            if isinstance(ts, (int, float)):
                if ts > 1e12:  # Milliseconds
                    ts = ts / 1000
                return datetime.fromtimestamp(ts, tz=timezone.utc)
            return pd.to_datetime(ts, utc=True)
        except Exception:
            return None

    def _filter_corporate_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter news for corporate events of interest

        Args:
            df: DataFrame with news

        Returns:
            Filtered DataFrame containing only corporate events
        """
        if df.empty:
            return df

        def is_corporate_event(row) -> bool:
            """Check if news item is a corporate event"""
            title = str(row.get('title', '')).lower()
            summary = str(row.get('summary', '')).lower()
            text = f"{title} {summary}"

            # Check against all corporate event categories
            for category, keywords in CORPORATE_EVENTS.items():
                for keyword in keywords:
                    if keyword in text:
                        return True

            return False

        mask = df.apply(is_corporate_event, axis=1)
        return df[mask].reset_index(drop=True)

    def categorize_news(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add category column to news DataFrame

        Args:
            df: DataFrame with news

        Returns:
            DataFrame with added 'category' column
        """
        if df.empty:
            return df

        def get_category(row) -> str:
            """Determine the category of a news item"""
            title = str(row.get('title', '')).lower()
            summary = str(row.get('summary', '')).lower()
            text = f"{title} {summary}"

            for category, keywords in CORPORATE_EVENTS.items():
                for keyword in keywords:
                    if keyword in text:
                        return category.capitalize()

            return "Other"

        df = df.copy()
        df['category'] = df.apply(get_category, axis=1)
        return df


# Convenience functions for backward compatibility
def get_news_for_ticker(ticker: str, limit: int = 20) -> pd.DataFrame:
    """Get news for a specific ticker (backward compatible interface)"""
    fetcher = NewsFetcher()
    return fetcher.get_ticker_news(ticker, limit)