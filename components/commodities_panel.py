"""
Commodities Panel Component
Commodity prices and performance - Compact version
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.commodities import CommoditiesFetcher
from config.settings import COMMODITIES


def render_commodities_panel():
    """Render the commodities panel"""
    st.markdown("### Commodities")

    commodities = CommoditiesFetcher()

    # Tabs for different views
    tab1, tab2 = st.tabs(["Overview", "Chart"])

    with tab1:
        _render_commodities_overview(commodities)

    with tab2:
        _render_commodities_chart(commodities)


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


def _render_commodities_overview(commodities: CommoditiesFetcher):
    """Render commodities overview grid"""
    try:
        prices_data = commodities.get_current_prices()

        if prices_data.empty:
            st.info("Commodity data not available")
            return

        # Create dataframe with daily, weekly, monthly changes
        df = prices_data[['name', 'price', 'change_pct', 'weekly_pct', 'monthly_pct']].copy()
        df.columns = ['Commodity', 'Price', 'Daily', 'Weekly', 'Monthly']

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
            width='stretch',
            hide_index=True,
            column_config={
                'Commodity': st.column_config.TextColumn(width='small'),
                'Price': st.column_config.TextColumn(width='small'),
                'Daily': st.column_config.TextColumn(width='small'),
                'Weekly': st.column_config.TextColumn(width='small'),
                'Monthly': st.column_config.TextColumn(width='small')
            }
        )

    except Exception as e:
        st.error(f"Error loading commodity data: {str(e)}")


def _render_commodities_chart(commodities: CommoditiesFetcher):
    """Render commodity chart selector"""
    # Select commodity - use config dict (inverted: name -> ticker)
    commodity_options = {name: ticker for ticker, name in COMMODITIES.items()}

    selected = st.selectbox("Select", list(commodity_options.keys()), label_visibility="collapsed")
    ticker = commodity_options[selected]

    try:
        # Get historical data
        hist_data = commodities.get_historical(ticker, period="1mo")

        if hist_data.empty:
            st.info("Historical data not available")
            return

        # Compact price chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hist_data.index,
            y=hist_data['Close'],
            mode='lines',
            name='Price',
            line=dict(color='#ff6b00', width=1.5)
        ))

        fig.update_layout(
            title=" ",
            xaxis_title="",
            yaxis_title="$",
            height=280,
            showlegend=False,
            margin=dict(l=40, r=20, t=35, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6edf3', size=10),
            xaxis=dict(gridcolor='#30363d', tickfont=dict(size=9), tickformat='%b %d'),
            yaxis=dict(gridcolor='#30363d', tickfont=dict(size=9))
        )

        st.plotly_chart(fig, width='stretch', config={'displayModeBar': True, 'displaylogo': False, 'scrollZoom': False})

        # Compact stats
        col1, col2, col3 = st.columns(3)

        current = hist_data['Close'].iloc[-1]
        high_30d = hist_data['Close'].max()
        low_30d = hist_data['Close'].min()
        change_pct = ((current - hist_data['Close'].iloc[0]) / hist_data['Close'].iloc[0]) * 100

        with col1:
            st.metric("Current", f"${current:,.2f}")
        with col2:
            st.metric("30D High", f"${high_30d:,.2f}")
        with col3:
            st.metric("30D Low", f"${low_30d:,.2f}")

    except Exception as e:
        st.error(f"Error loading chart: {str(e)}")