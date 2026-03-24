"""
Corporate Actions Calendar fetcher from stockanalysis.com
"""
import pandas as pd
import requests
import os
import streamlit as st
from datetime import datetime
from bs4 import BeautifulSoup
from .fetcher import DataFetcher
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Streamlit-cached function for API calls - persists across page reruns
@st.cache_data(ttl=300)
def _fetch_actions_html(year: int) -> list:
    """
    Fetch corporate actions HTML and parse it.
    Cached by Streamlit to prevent repeated API calls on widget interactions.
    """
    base_url = "https://stockanalysis.com/actions"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    # Build proxies from environment variables if set
    proxy_user = os.getenv('PROXY_USER')
    proxy_pass = os.getenv('PROXY_PASS')
    proxy_host = os.getenv('PROXY_HOST')
    proxy_port = os.getenv('PROXY_PORT')
    proxies = None
    if proxy_user and proxy_pass and proxy_host and proxy_port:
        proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
    # Disable SSL verification only if using proxy (required for some corporate proxies)
    verify_ssl = proxies is None

    try:
        url = f"{base_url}/{year}/"
        response = requests.get(url, headers=headers, timeout=30, proxies=proxies, verify=verify_ssl)
        response.raise_for_status()
        data = _parse_html_table(response.text)
        if not data:
            # Fallback: try fetching main page
            response = requests.get(base_url + "/", headers=headers, timeout=30, proxies=proxies, verify=verify_ssl)
            response.raise_for_status()
            data = _parse_html_table(response.text)
        return data

    except requests.exceptions.ProxyError as e:
        st.error(f"Proxy error: {e}. Please check your proxy settings.")
        return []
    except requests.exceptions.ConnectTimeout as e:
        st.error(f"Connection timed out: {e}")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching corporate actions data: {e}")
        return []
    except Exception as e:
        st.error(f"Error fetching corporate actions: {e}")
        return []


def _parse_html_table(html: str) -> list:
    """Extract corporate actions from HTML table"""
    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Find the main data table
        table = soup.find('table')
        if not table:
            return []

        data = []
        rows = table.find_all('tr')

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                # Date cell
                date_cell = cells[0]
                date_text = date_cell.get_text(strip=True)

                # Symbol cell (contains link)
                symbol_cell = cells[1]
                link = symbol_cell.find('a')
                symbol = link.get_text(strip=True) if link else symbol_cell.get_text(strip=True)

                # Type cell
                type_cell = cells[2]
                action_type = type_cell.get_text(strip=True)

                # Action/text cell
                action_cell = cells[3]
                action_text = action_cell.get_text(strip=True)

                data.append({
                    'date': date_text,
                    'symbol': symbol,
                    'type': action_type,
                    'text': action_text
                })

        return data
    except Exception:
        return []


class CorporateActionsFetcher(DataFetcher):
    """Fetch corporate actions calendar from stockanalysis.com"""

    # Action types to track
    ACTION_TYPES = [
        'Stock Split',
        'Symbol Change',
        'Delisted',
        'Listed',
        'Acquisition',
        'Spinoff',
        'Bankruptcy'
    ]

    def __init__(self, cache_duration: int = 300):
        super().__init__(cache_duration)

    def get_actions(self, days: int = 30) -> pd.DataFrame:
        """
        Get corporate actions for upcoming/past days

        Args:
            days: Number of days to include (past and future)

        Returns:
            DataFrame with Date, Symbol, Type, Action columns
        """
        try:
            # Use Streamlit-cached function for API call
            current_year = datetime.now().year
            data = _fetch_actions_html(current_year)

            if not data:
                return pd.DataFrame()

            # Process records (filtering done locally, not cached)
            results = []
            cutoff_date = datetime.now() - pd.Timedelta(days=days)
            future_cutoff = datetime.now() + pd.Timedelta(days=days)

            for record in data:
                try:
                    # Parse date
                    date_str = record.get('date', '')
                    try:
                        date = datetime.strptime(date_str, '%b %d, %Y')
                    except ValueError:
                        continue

                    # Filter to date range
                    if date < cutoff_date or date > future_cutoff:
                        continue

                    results.append({
                        'Date': date,
                        'Symbol': record.get('symbol', ''),
                        'Type': record.get('type', ''),
                        'Action': record.get('text', '')
                    })
                except Exception:
                    continue

            if not results:
                return pd.DataFrame()

            df = pd.DataFrame(results)
            df = df.sort_values('Date', ascending=False).reset_index(drop=True)
            return df

        except Exception:
            return pd.DataFrame()

    def get_actions_by_type(self, action_type: str, days: int = 90) -> pd.DataFrame:
        """
        Get corporate actions filtered by type

        Args:
            action_type: Type of action (Stock Split, Delisted, etc.)
            days: Number of days to include

        Returns:
            DataFrame with filtered actions
        """
        df = self.get_actions(days=days)

        if df.empty:
            return df

        return df[df['Type'] == action_type].reset_index(drop=True)

    def get_splits(self, days: int = 30) -> pd.DataFrame:
        """Get stock splits"""
        return self.get_actions_by_type('Stock Split', days)

    def get_delistings(self, days: int = 90) -> pd.DataFrame:
        """Get delisted stocks"""
        return self.get_actions_by_type('Delisted', days)

    def get_listings(self, days: int = 30) -> pd.DataFrame:
        """Get new listings (IPOs)"""
        return self.get_actions_by_type('Listed', days)

    def get_acquisitions(self, days: int = 90) -> pd.DataFrame:
        """Get acquisitions/mergers"""
        return self.get_actions_by_type('Acquisition', days)