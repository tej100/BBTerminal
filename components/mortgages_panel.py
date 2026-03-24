"""
Mortgages Panel Component
Mortgage rates and spreads - Compact version
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.mortgages import MortgagesFetcher
from data.treasury import TreasuryFetcher


def render_mortgages_panel():
    """Render the mortgages panel"""
    st.markdown("### Mortgage Rates")

    mortgages = MortgagesFetcher()

    # Tabs for different views
    tab1, tab2 = st.tabs(["Rates", "Trend"])

    with tab1:
        _render_current_rates(mortgages)

    with tab2:
        _render_historical_trend(mortgages)


def _render_current_rates(mortgages: MortgagesFetcher):
    """Render current mortgage rates"""
    st.markdown("#### Current")

    try:
        rates_data = mortgages.get_all_rates()

        if rates_data.empty:
            st.info("Mortgage rate data not available")
            return

        # Compact dataframe
        df = rates_data[['name', 'value', 'change']].copy()
        df['name'] = df['name'].str.replace(' Mortgage', '').str.replace(' Fixed', '')
        df.columns = ['Type', 'Rate', 'Chg']

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=150
        )

        # Spreads to 10Y Treasury (from treasury.gov)
        st.markdown("#### Spread to 10Y")

        treasury = TreasuryFetcher()
        yields = treasury.get_latest_yields()

        if not yields.empty:
            ten_year_row = yields[yields['maturity'] == '10Y']
            if not ten_year_row.empty:
                ten_year_rate = ten_year_row.iloc[0]['rate']

                col1, col2, col3 = st.columns(3)

                for idx, row in rates_data.iterrows():
                    spread = row['value'] - ten_year_rate
                    name = row['name'].replace(" Mortgage", "").replace(" Fixed", "")

                    with [col1, col2, col3][idx % 3]:
                        st.metric(f"{name}", f"{spread*100:.0f}bp")

    except Exception as e:
        st.error(f"Error loading mortgage data: {str(e)}")


def _render_historical_trend(mortgages: MortgagesFetcher):
    """Render historical mortgage rate trends"""
    st.markdown("#### 30Y Fixed")

    try:
        hist_data = mortgages.get_historical_rates("MORTGAGE30US", days=30)

        if hist_data.empty:
            st.info("Historical data not available")
            return

        # Compact chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hist_data['date'],
            y=hist_data['value'],
            mode='lines',
            name='30Y Fixed',
            line=dict(color='#ff6b00', width=1.5)
        ))

        fig.update_layout(
            title=" ",
            xaxis_title="",
            yaxis_title="%",
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

        # Compact stats
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Current", f"{hist_data['value'].iloc[-1]:.2f}%")
        with col2:
            st.metric("30D High", f"{hist_data['value'].max():.2f}%")
        with col3:
            st.metric("30D Low", f"{hist_data['value'].min():.2f}%")

    except Exception as e:
        st.error(f"Error loading historical data: {str(e)}")