"""
BBTerminal - Bloomberg Launchpad Style Dashboard
A comprehensive financial market monitoring dashboard for daily DQ workflow
"""
import streamlit as st
import time
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="BBTerminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Bloomberg-style appearance
st.markdown("""
<style>
    .main {
        background-color: #1a1a1a;
    }
    .stMetric {
        background-color: #2d2d2d;
        padding: 10px;
        border-radius: 5px;
    }
    .stMetric label {
        color: #888888 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ff6600 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2d2d2d;
        color: #888888;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3d3d3d !important;
        color: #ffffff !important;
    }
    .stDataFrame {
        background-color: #2d2d2d;
    }
    .stSidebar {
        background-color: #1a1a1a;
    }
    /* Success/Info/Warning/Error message styling */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Import components
from components.market_summary import render_market_summary, render_quick_stats
from components.equities_panel import render_equities_panel
from components.rates_panel import render_rates_panel
from components.mortgages_panel import render_mortgages_panel
from components.commodities_panel import render_commodities_panel
from components.economic_panel import render_economic_panel
from components.alerts_panel import render_alerts_panel, render_market_status
from components.holidays_panel import render_holidays_panel, render_compact_holidays


def main():
    """Main dashboard application"""
    # Header
    st.title("📊 BBTerminal")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    st.markdown("---")

    # Market Summary Row
    try:
        render_market_summary()
        render_quick_stats()
    except Exception as e:
        st.warning(f"Market summary temporarily unavailable: {str(e)}")

    st.markdown("---")

    # Main Dashboard Grid
    col1, col2 = st.columns([2, 1])

    with col1:
        # Left column: Equities and Commodities
        equities_tab, commodities_tab = st.tabs(["📈 Equities", "🛢️ Commodities"])

        with equities_tab:
            try:
                render_equities_panel()
            except Exception as e:
                st.error(f"Error loading equities: {str(e)}")

        with commodities_tab:
            try:
                render_commodities_panel()
            except Exception as e:
                st.error(f"Error loading commodities: {str(e)}")

    with col2:
        # Right column: Interest Rates
        try:
            render_rates_panel()
        except Exception as e:
            st.error(f"Error loading rates: {str(e)}")

    # Second row
    col3, col4, col5 = st.columns([1, 1, 1])

    with col3:
        try:
            render_mortgages_panel()
        except Exception as e:
            st.error(f"Error loading mortgages: {str(e)}")

    with col4:
        try:
            render_economic_panel()
        except Exception as e:
            st.error(f"Error loading economic data: {str(e)}")

    with col5:
        try:
            render_alerts_panel()
        except Exception as e:
            st.error(f"Error loading alerts: {str(e)}")

    # Sidebar: Holidays and Market Status
    with st.sidebar:
        st.markdown("---")
        render_compact_holidays()
        st.markdown("---")
        render_market_status()
        st.markdown("---")
        render_holidays_panel()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666;">
            <small>
                BBTerminal - Financial Dashboard for DQ Monitoring<br>
                Data sources: Yahoo Finance (yfinance) | FRED | pandas-market-calendars<br>
                Auto-refresh: 5 minutes | Press R to manually refresh
            </small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()