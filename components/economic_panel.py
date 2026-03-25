"""
Economic Data Panel Component
Key economic indicators - Compact version
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.fred_fetcher import FredFetcher
from config.settings import ECONOMIC_DATA


def _calculate_yoy_mom(series_id: str, fred_fetcher: FredFetcher) -> dict:
    """
    Calculate YoY (year-over-year) and MoM (month-over-month) changes for an economic series.
    
    Args:
        series_id: FRED series ID
        fred_fetcher: FredFetcher instance
        
    Returns:
        Dict with name, value, yoy_change, mom_change
    """
    try:
        fred = fred_fetcher.fred
        series = fred.get_series(series_id)
        
        if series is not None and len(series) > 0:
            latest = series.iloc[-1]
            latest_date = series.index[-1]
            
            # Calculate YoY and MoM changes
            yoy_change = None
            mom_change = None
            
            if len(series) >= 13:  # At least 12 months for YoY
                yoy_value = series.iloc[-13]
                if yoy_value != 0:
                    yoy_change = ((latest - yoy_value) / abs(yoy_value)) * 100
            
            if len(series) >= 2:
                prev = series.iloc[-2]
                if prev != 0:
                    mom_change = ((latest - prev) / abs(prev)) * 100
            
            return {
                'series_id': series_id,
                'name': ECONOMIC_DATA.get(series_id, series_id),
                'value': round(latest, 2),
                'date': latest_date.strftime('%Y-%m-%d'),
                'yoy_change': round(yoy_change, 2) if yoy_change is not None else None,
                'mom_change': round(mom_change, 2) if mom_change is not None else None
            }
    except Exception:
        pass
    
    return None


def render_economic_panel():
    """Render the economic indicators panel"""
    st.markdown("### Economic Data")

    economic = FredFetcher(series_dict=ECONOMIC_DATA)

    # Tabs for different views
    tab1, tab2 = st.tabs(["Indicators", "Chart"])

    with tab1:
        _render_key_indicators(economic)

    with tab2:
        _render_historical_view(economic)


def _render_key_indicators(economic: FredFetcher):
    """Render key economic indicators"""
    try:
        # Get all indicators with YoY/MoM calculations
        results = []
        for series_id in ECONOMIC_DATA.keys():
            data = _calculate_yoy_mom(series_id, economic)
            if data:
                results.append(data)
        
        indicators = pd.DataFrame(results)

        if indicators.empty:
            st.info("Economic data not available")
            return

        # Compact table
        df = indicators[['name', 'value', 'yoy_change', 'mom_change']].copy()
        df.columns = ['Indicator', 'Value', 'YoY', 'MoM']

        st.dataframe(
            df,
            width='stretch',
            hide_index=True,
            height=250
        )

    except Exception as e:
        st.error(f"Error loading economic data: {str(e)}")


def _render_historical_view(economic: FredFetcher):
    """Render historical economic data view"""
    # Select indicator - use config dict (inverted: name -> series_id)
    indicator_options = {name: series_id for series_id, name in ECONOMIC_DATA.items()}

    selected = st.selectbox("Select", list(indicator_options.keys()), label_visibility="collapsed")
    series_id = indicator_options[selected]

    try:
        hist_data = economic.get_historical_rates(series_id, days=365)

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

        st.plotly_chart(fig, width='stretch', config={'displayModeBar': True, 'displaylogo': False, 'scrollZoom': False})

    except Exception as e:
        st.error(f"Error loading historical data: {str(e)}")