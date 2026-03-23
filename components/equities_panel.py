"""
Equities Panel Component
Sector heatmap and corporate actions
"""
import streamlit as st
import pandas as pd
from data.equities import EquitiesFetcher
from data.corporate_actions import CorporateActionsFetcher
from config.settings import SECTOR_ETFS


def render_equities_panel():
    """Render the equities panel with sector performance"""
    st.markdown("### Equities")

    equities = EquitiesFetcher()
    corp_actions = CorporateActionsFetcher()

    # Tabs for different views
    tab1, tab2 = st.tabs(["Sectors", "Corp Actions"])

    with tab1:
        _render_sector_heatmap(equities)

    with tab2:
        _render_corporate_actions(corp_actions)


def _render_sector_heatmap(equities: EquitiesFetcher):
    """Render sector performance as a compact table"""
    st.markdown("#### Sector Performance")

    try:
        sector_data = equities.get_sector_performance()

        if sector_data.empty:
            st.info("Sector data not available")
            return

        # Create dataframe with daily, weekly, monthly changes
        df = sector_data[['name', 'price', 'change_pct', 'weekly_pct', 'monthly_pct']].copy()
        df.columns = ['Sector', 'Price', 'Daily', 'Weekly', 'Monthly']

        # Format price
        df['Price'] = df['Price'].apply(lambda x: f"{x:,.2f}")

        # Format change columns
        df['Daily'] = df['Daily'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "-")
        df['Weekly'] = df['Weekly'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "-")
        df['Monthly'] = df['Monthly'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "-")

        # Style dataframe with conditional coloring
        styled_df = df.style.apply(_color_change_columns, subset=['Daily', 'Weekly', 'Monthly'])

        # Display compact dataframe with narrow columns
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Sector': st.column_config.TextColumn(width='small'),
                'Price': st.column_config.TextColumn(width='small'),
                'Daily': st.column_config.TextColumn(width='small'),
                'Weekly': st.column_config.TextColumn(width='small'),
                'Monthly': st.column_config.TextColumn(width='small')
            }
        )

    except Exception as e:
        st.error(f"Error loading sector data: {str(e)}")


def _color_change_columns(series):
    """Apply green/red color to change columns based on positive/negative values"""
    colors = []
    for val in series:
        if val == '-' or pd.isna(val):
            colors.append('color: #8b949e')  # Gray for N/A
        elif str(val).startswith('+') or (str(val).startswith('-') is False and float(val.replace('%', '')) > 0):
            colors.append('color: #3fb950')  # Green for positive
        else:
            colors.append('color: #f85149')  # Red for negative
    return colors


def _render_corporate_actions(corp_actions: CorporateActionsFetcher):
    """Render corporate actions calendar"""
    st.markdown("#### Corporate Actions")

    # Filter by action type
    action_types = ['All', 'Stock Split', 'Delisted', 'Listed', 'Acquisition', 'Spinoff', 'Bankruptcy', 'Symbol Change']
    selected_type = st.selectbox("Filter", action_types, label_visibility="collapsed")

    try:
        # Get actions for past/future 60 days
        df = corp_actions.get_actions(days=60)

        if df.empty:
            st.info("Corporate actions data not available")
            return

        # Filter by type if selected
        if selected_type != 'All':
            df = df[df['Type'] == selected_type]

        # Format date
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

        # Style by action type
        def _color_type_column(series):
            colors = []
            for val in series:
                if val == 'Delisted':
                    colors.append('color: #f85149')  # Red
                elif val == 'Bankruptcy':
                    colors.append('color: #f85149')  # Red
                elif val == 'Listed':
                    colors.append('color: #3fb950')  # Green
                elif val == 'Stock Split':
                    colors.append('color: #58a6ff')  # Blue
                elif val == 'Acquisition':
                    colors.append('color: #d29922')  # Yellow/Orange
                elif val == 'Spinoff':
                    colors.append('color: #a371f7')  # Purple
                else:
                    colors.append('color: #8b949e')  # Gray
            return colors

        styled_df = df.style.apply(_color_type_column, subset=['Type'])

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Date': st.column_config.TextColumn(width='small'),
                'Symbol': st.column_config.TextColumn(width='small'),
                'Type': st.column_config.TextColumn(width='small'),
                'Action': st.column_config.TextColumn(width='large')
            }
        )

        st.caption("*Data from stockanalysis.com • May explain price gaps/spikes in DQ checks*")

    except Exception as e:
        st.error(f"Error loading corporate actions: {str(e)}")