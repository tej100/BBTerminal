"""
Unified data fetcher with caching
"""
import time
from typing import Optional, Dict, Any
import pandas as pd
import streamlit as st

class DataFetcher:
    """Base class for data fetching with Streamlit caching support"""

    def __init__(self, cache_duration: int = 300):
        """
        Initialize data fetcher with cache duration in seconds

        Args:
            cache_duration: Cache duration in seconds (default 5 minutes)
        """
        self.cache_duration = cache_duration
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and still valid"""
        if key not in self._cache:
            return False
        cached_time = self._cache[key].get("timestamp", 0)
        return (time.time() - cached_time) < self.cache_duration

    def _get_cached(self, key: str) -> Optional[pd.DataFrame]:
        """Get cached data if valid"""
        if self._is_cached(key):
            return self._cache[key].get("data")
        return None

    def _set_cache(self, key: str, data: pd.DataFrame) -> None:
        """Cache data with current timestamp"""
        self._cache[key] = {
            "data": data,
            "timestamp": time.time()
        }

    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()

    def clear_expired_cache(self) -> None:
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self._cache.items()
            if (current_time - value.get("timestamp", 0)) >= self.cache_duration
        ]
        for key in expired_keys:
            del self._cache[key]


def cached_fetch(ttl: int = 300):
    """
    Decorator for Streamlit-based caching that persists across reruns.

    Use this on data fetching methods to prevent unnecessary API calls
    when Streamlit widgets trigger page reruns.

    Args:
        ttl: Time-to-live in seconds (default 5 minutes)
    """
    return st.cache_data(ttl=ttl)