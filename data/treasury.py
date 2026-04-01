"""
Treasury Yield Curve data fetcher using fiscaldata.treasury.gov API
"""
import pandas as pd
import requests
import streamlit as st
import xml.etree.ElementTree as ET
from datetime import datetime
from .fetcher import DataFetcher
from config.settings import TREASURY_TENORS


# Streamlit-cached function for HTTP requests - prevents repeated API calls
# Treasury data only updates once daily (end of day), so cache for 24 hours
@st.cache_data(ttl=86400)
def _fetch_treasury_xml(year: int) -> str:
    """
    Fetch Treasury yield curve XML data.
    Cached by Streamlit to prevent repeated API calls on widget interactions.
    """
    base_url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"
    url = f"{base_url}?data=daily_treasury_yield_curve&field_tdr_date_value={year}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


class TreasuryFetcher(DataFetcher):
    """Fetch Treasury yield curve data from fiscaldata.treasury.gov"""

    # Maturity columns from config: {API_column: display_name}
    MATURITIES = TREASURY_TENORS

    # Ordered list of display names for sorting (values preserve dict insertion order)
    MATURITY_ORDER = list(TREASURY_TENORS.values())

    def __init__(self, cache_duration: int = 300):
        super().__init__(cache_duration)

    def _parse_xml_yields(self, xml_content: str) -> pd.DataFrame:
        """Parse XML yield curve data into DataFrame"""
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            # Try with namespace handling
            try:
                # Remove namespace prefix
                xml_content = xml_content.replace('m:', '')
                xml_content = xml_content.replace('d:', '')
                root = ET.fromstring(xml_content)
            except:
                return pd.DataFrame()

        records = []

        # Find all entry elements
        for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
            content = entry.find('{http://www.w3.org/2005/Atom}content')
            if content is None:
                continue

            properties = content.find('{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties')
            if properties is None:
                continue

            record = {}
            for prop in properties:
                # Remove namespace from tag
                tag = prop.tag.split('}')[-1] if '}' in prop.tag else prop.tag
                if tag == 'NEW_DATE':
                    record['date'] = prop.text
                elif tag.startswith('BC_'):
                    maturity = tag
                    try:
                        record[maturity] = float(prop.text) if prop.text else None
                    except (ValueError, TypeError):
                        record[maturity] = None

            if record.get('date'):
                records.append(record)

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date', ascending=False)

    def get_yield_curve_data(self, days: int = 30) -> pd.DataFrame:
        """
        Get yield curve data for recent days

        Args:
            days: Number of days of history to fetch

        Returns:
            DataFrame with date and yield columns
        """
        try:
            # Use Streamlit-cached function for API call
            current_year = datetime.now().year
            xml_content = _fetch_treasury_xml(current_year)

            df = self._parse_xml_yields(xml_content)

            if df.empty:
                return pd.DataFrame()

            # Filter to requested days
            cutoff = datetime.now() - pd.Timedelta(days=days)
            df = df[df['date'] >= cutoff]

            return df

        except Exception:
            return pd.DataFrame()

    def get_latest_yields(self) -> pd.DataFrame:
        """
        Get latest yield curve rates for all maturities with daily, weekly, monthly changes

        Returns:
            DataFrame with maturity, rate, daily, weekly, monthly change columns
        """
        try:
            # Get enough history for monthly change (approx 35 days to be safe)
            df = self.get_yield_curve_data(days=35)

            if df.empty or len(df) < 2:
                return pd.DataFrame()

            latest = df.iloc[0]
            latest_date = df['date'].iloc[0]

            # Helper function to get value from target date
            def get_value_at_date(target_date):
                candidates = df[df['date'] <= target_date]
                return candidates.iloc[0] if not candidates.empty else None

            results = []
            for col, maturity in self.MATURITIES.items():
                if col not in latest.index or pd.isna(latest[col]):
                    continue

                rate = latest[col]

                # Daily change: previous available data point
                daily = round(rate - df.iloc[1][col], 3) if pd.notna(df.iloc[1][col]) else None

                # Weekly change: value ~7 days before latest
                weekly_value = get_value_at_date(latest_date - pd.DateOffset(weeks=1))
                weekly = round(rate - weekly_value[col], 3) if weekly_value is not None and pd.notna(weekly_value[col]) else None

                # Monthly change: value ~1 month before latest
                monthly_value = get_value_at_date(latest_date - pd.DateOffset(months=1))
                monthly = round(rate - monthly_value[col], 3) if monthly_value is not None and pd.notna(monthly_value[col]) else None

                results.append({
                    'maturity': maturity,
                    'rate': round(rate, 3),
                    'daily': daily,
                    'weekly': weekly,
                    'monthly': monthly
                })

            result_df = pd.DataFrame(results)
            # Sort by maturity order
            result_df['sort_order'] = result_df['maturity'].apply(
                lambda x: self.MATURITY_ORDER.index(x) if x in self.MATURITY_ORDER else 999
            )
            result_df = result_df.sort_values('sort_order').drop('sort_order', axis=1).reset_index(drop=True)

            return result_df

        except Exception:
            return pd.DataFrame()

    def get_yield_curve(self) -> pd.DataFrame:
        """
        Get current yield curve for plotting

        Returns:
            DataFrame with maturity and rate columns for charting
        """
        try:
            latest = self.get_latest_yields()
            if latest.empty:
                return pd.DataFrame()

            return latest[['maturity', 'rate']].copy()
        except Exception:
            return pd.DataFrame()

    def get_all_rates(self) -> pd.DataFrame:
        """
        Get all rates for table display

        Returns:
            DataFrame with maturity, rate, daily, weekly, monthly columns
        """
        yields = self.get_latest_yields()

        if yields.empty:
            return pd.DataFrame()

        # Rename for display
        df = yields.copy()
        df = df.rename(columns={
            'maturity': 'Maturity',
            'rate': 'Yield',
            'daily': 'Daily',
            'weekly': 'Weekly',
            'monthly': 'Monthly'
        })

        return df