"""
BBTerminal - Bloomberg Launchpad Style Dashboard
A comprehensive financial market monitoring dashboard for daily DQ workflow
"""
import streamlit as st
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure page FIRST before any other Streamlit commands
st.set_page_config(
    page_title="BBTerminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapsed by default for more screen space
)

# Apply custom theme
from styles.theme import apply_theme, render_header

apply_theme()

# Import components
from components.market_summary import render_market_summary
from components.equities_panel import render_equities_panel
from components.rates_panel import render_rates_panel
from components.mortgages_panel import render_mortgages_panel
from components.commodities_panel import render_commodities_panel
from components.economic_panel import render_economic_panel
from components.alerts_panel import render_alerts_panel
from components.holidays_panel import render_holidays_panel


def main():
    """Main dashboard application"""
    # Compact header
    render_header()

    # Main layout: Equities on left (1/3), Indices on right (2/3)
    col_left, col_right = st.columns([1, 2])

    with col_left:
        # Left column: Equities
        try:
            render_equities_panel()
        except Exception as e:
            st.error(f"Error loading equities: {str(e)}")

    with col_right:
        # Right column top: Market summary and quick stats
        try:
            render_market_summary()
        except Exception as e:
            st.warning(f"Market summary temporarily unavailable: {str(e)}")

        # Right column: Rates, Commodities, Mortgages in a row
        col_r1, col_r2, col_r3 = st.columns([1, 1, 1])

        with col_r1:
            try:
                render_rates_panel()
            except Exception as e:
                st.error(f"Error loading rates: {str(e)}")

        with col_r2:
            try:
                render_commodities_panel()
            except Exception as e:
                st.error(f"Error loading commodities: {str(e)}")

        with col_r3:
            try:
                render_mortgages_panel()
            except Exception as e:
                st.error(f"Error loading mortgages: {str(e)}")

    # Second row - Holidays, Economic, and Alerts
    col7, col8, col9 = st.columns([1, 1, 1])

    with col7:
        try:
            render_holidays_panel()
        except Exception as e:
            st.error(f"Error loading holidays: {str(e)}")

    with col8:
        try:
            render_economic_panel()
        except Exception as e:
            st.error(f"Error loading economic data: {str(e)}")

    with col9:
        try:
            render_alerts_panel()
        except Exception as e:
            st.error(f"Error loading alerts: {str(e)}")

    # Minimal footer
    st.markdown("""
    <div style="text-align: center; color: #6e7681; font-size: 0.7rem; padding-top: 0.5rem; border-top: 1px solid #30363d;">
        BBTerminal • Yahoo Finance • FRED • Auto-refresh: 5m • Press 'r' to manually refresh
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()