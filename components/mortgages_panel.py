"""
Mortgages Panel Component
Mortgage rates and spreads - Compact version
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.fred_fetcher import FredFetcher
from data.treasury import TreasuryFetcher
from config.settings import MORTGAGE_RATES
from styles.theme import color_rate_changes


def render_mortgages_panel():
    """Render the mortgages panel"""
    st.markdown("### Mortgage Rates")

    mortgages = FredFetcher(series_dict=MORTGAGE_RATES)

    # Tabs for different views
    tab1, tab2 = st.tabs(["Rates", "Trend"])

    with tab1:
        _render_current_rates(mortgages)

    with tab2:
        _render_historical_trend(mortgages)


def _render_current_rates(mortgages: FredFetcher):
    """Render current mortgage rates"""
    try:
        rates_data = mortgages.get_all_rates()

        if rates_data.empty:
            st.info("Mortgage rate data not available")
            return

        # Style dataframe with conditional coloring
        # Format dataframe
        df = rates_data.copy()
        df['Type'] = df['name'].str.replace(' Mortgage', '').str.replace(' Fixed', '')
        df['Rate'] = df['value'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "-")
        df['Daily (bps)'] = df['daily'].apply(lambda x: f"{x*100:+.0f}" if pd.notna(x) else "-")
        df['Weekly (bps)'] = df['weekly'].apply(lambda x: f"{x*100:+.0f}" if pd.notna(x) else "-")
        df['Monthly (bps)'] = df['monthly'].apply(lambda x: f"{x*100:+.0f}" if pd.notna(x) else "-")
        
        # Select and reorder columns
        df = df[['Type', 'Rate', 'Daily (bps)', 'Weekly (bps)', 'Monthly (bps)']]

        styled_df = df.style.apply(color_rate_changes, subset=['Daily (bps)', 'Weekly (bps)', 'Monthly (bps)'])

        st.dataframe(
            styled_df,
            width='stretch',
            hide_index=True,
            column_config={
                'Type': st.column_config.TextColumn(width='small'),
                'Rate': st.column_config.TextColumn(width='small'),
                'Daily (bps)': st.column_config.TextColumn(width='small'),
                'Weekly (bps)': st.column_config.TextColumn(width='small'),
                'Monthly (bps)': st.column_config.TextColumn(width='small')
            }
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


def _render_historical_trend(mortgages: FredFetcher):
    """Render historical mortgage rate trends with dynamic dropdown"""
    # Create dropdown menu - use config dict (inverted: name -> series_id)
    mortgage_options = {name: series_id for series_id, name in MORTGAGE_RATES.items()}
    selected = st.selectbox("Select", list(mortgage_options.keys()), label_visibility="collapsed")
    series_id = mortgage_options[selected]

    try:
        hist_data = mortgages.get_historical_rates(series_id, days=30)

        if hist_data.empty:
            st.info("Historical data not available")
            return

        # Compact chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hist_data['date'],
            y=hist_data['value'],
            mode='lines',
            name=selected,
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

        st.plotly_chart(fig, width='stretch', config={'displayModeBar': True, 'displaylogo': False, 'scrollZoom': False})

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