"""
Interest Rates Panel Component
Yield curve and key rates display - Compact version
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.treasury import TreasuryFetcher
from styles.theme import color_rate_changes


def render_rates_panel():
    """Render the interest rates panel"""
    st.markdown("### Interest Rates")

    treasury = TreasuryFetcher()

    # Tabs for different views
    tab1, tab2 = st.tabs(["Yield Curve", "Rates"])

    with tab1:
        _render_yield_curve(treasury)

    with tab2:
        _render_all_rates(treasury)


def _render_yield_curve(treasury: TreasuryFetcher):
    """Render yield curve visualization"""
    try:
        yield_curve = treasury.get_yield_curve()

        if yield_curve.empty:
            st.info("Yield curve data not available")
            return

        # Compact yield curve plot
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=yield_curve['maturity'],
            y=yield_curve['rate'],
            mode='lines+markers',
            name='Current',
            line=dict(color='#ff6b00', width=2),
            marker=dict(size=6, color='#ff6b00')
        ))

        fig.update_layout(
            title=" ",
            xaxis_title="",
            yaxis_title="Yield %",
            height=280,
            showlegend=False,
            margin=dict(l=40, r=20, t=35, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e6edf3', size=10),
            xaxis=dict(gridcolor='#30363d', tickfont=dict(size=9)),
            yaxis=dict(gridcolor='#30363d', tickfont=dict(size=9))
        )

        st.plotly_chart(fig, width='stretch', config={'displayModeBar': True, 'displaylogo': False, 'scrollZoom': False})

        # Compact spreads row
        col1, col2, col3 = st.columns(3)

        yields = yield_curve.set_index('maturity')['rate'].to_dict()

        with col1:
            if '2Y' in yields and '10Y' in yields:
                spread = yields['10Y'] - yields['2Y']
                color = "normal" if spread >= 0 else "inverse"
                st.metric("2Y-10Y", f"{spread*100:.0f}bp", delta_color=color)
                if spread < 0:
                    st.caption("Inverted")

        with col2:
            if '3M' in yields and '10Y' in yields:
                spread = yields['10Y'] - yields['3M']
                st.metric("3M-10Y", f"{spread*100:.0f}bp")

        with col3:
            if '2Y' in yields and '30Y' in yields:
                spread = yields['30Y'] - yields['2Y']
                st.metric("2Y-30Y", f"{spread*100:.0f}bp")

    except Exception as e:
        st.error(f"Error loading yield curve: {str(e)}")


def _render_all_rates(treasury: TreasuryFetcher):
    """Render all treasury rates table"""
    try:
        rates_data = treasury.get_all_rates()

        if rates_data.empty:
            st.info("Treasury rate data not available")
            return

        # Style dataframe with conditional coloring (inverse: lower yields = green)
        # Format values
        df = rates_data.copy()
        df['Yield'] = df['Yield'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "-")
        df['Daily (bps)'] = df['Daily'].apply(lambda x: f"{x*100:+.0f}" if pd.notna(x) and x is not None else "-")
        df['Weekly (bps)'] = df['Weekly'].apply(lambda x: f"{x*100:+.0f}" if pd.notna(x) and x is not None else "-")
        df['Monthly (bps)'] = df['Monthly'].apply(lambda x: f"{x*100:+.0f}" if pd.notna(x) and x is not None else "-")
        
        # Drop old columns
        df = df[['Maturity', 'Yield', 'Daily (bps)', 'Weekly (bps)', 'Monthly (bps)']]

        styled_df = df.style.apply(color_rate_changes, subset=['Daily (bps)', 'Weekly (bps)', 'Monthly (bps)'])

        st.dataframe(
            styled_df,
            width='stretch',
            hide_index=True,
            column_config={
                'Maturity': st.column_config.TextColumn(width='small'),
                'Yield': st.column_config.TextColumn(width='small'),
                'Daily (bps)': st.column_config.TextColumn(width='small'),
                'Weekly (bps)': st.column_config.TextColumn(width='small'),
                'Monthly (bps)': st.column_config.TextColumn(width='small')
            }
        )

        st.caption("*Treasury yields updated daily (end of day)*")

    except Exception as e:
        st.error(f"Error loading rate data: {str(e)}")