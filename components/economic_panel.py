"""
Economic Data Panel Component
Key economic indicators - Compact version
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.economic import EconomicFetcher
from config.settings import ECONOMIC_DATA


def render_economic_panel():
    """Render the economic indicators panel"""
    st.markdown("### Economic Data")

    economic = EconomicFetcher()

    # Tabs for different views
    tab1, tab2 = st.tabs(["Indicators", "Chart"])

    with tab1:
        _render_key_indicators(economic)

    with tab2:
        _render_historical_view(economic)


def _render_key_indicators(economic: EconomicFetcher):
    """Render key economic indicators"""
    st.markdown("#### Current")

    try:
        indicators = economic.get_all_indicators()

        if indicators.empty:
            st.info("Economic data not available")
            return

        # Compact table
        df = indicators[['name', 'value', 'yoy_change', 'mom_change']].copy()
        df.columns = ['Indicator', 'Value', 'YoY', 'MoM']

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=250
        )

    except Exception as e:
        st.error(f"Error loading economic data: {str(e)}")


def _render_historical_view(economic: EconomicFetcher):
    """Render historical economic data view"""
    st.markdown("#### Trend")

    # Select indicator - use config dict (inverted: name -> series_id)
    indicator_options = {name: series_id for series_id, name in ECONOMIC_DATA.items()}

    selected = st.selectbox("Select", list(indicator_options.keys()), label_visibility="collapsed")
    series_id = indicator_options[selected]

    try:
        hist_data = economic.get_historical(series_id, months=12)

        if hist_data.empty:
            st.info("Historical data not available")
            return

        # Compact chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hist_data['date'],
            y=hist_data['value'],
            mode='lines+markers',
            name=selected,
            line=dict(color='#ff6b00', width=1.5),
            marker=dict(size=4)
        ))

        fig.update_layout(
            title=" ",
            xaxis_title="",
            yaxis_title=selected,
            height=280,
            showlegend=False,
            margin=dict(l=40, r=20, t=35, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6edf3', size=10),
            xaxis=dict(gridcolor='#30363d', tickfont=dict(size=9), tickformat='%b %d'),
            yaxis=dict(gridcolor='#30363d', tickfont=dict(size=9))
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'scrollZoom': False})

    except Exception as e:
        st.error(f"Error loading historical data: {str(e)}")