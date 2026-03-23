"""
Interest Rates Panel Component
Yield curve and key rates display - Compact version
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.treasury import TreasuryFetcher


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
    st.markdown("#### Yield Curve")

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

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'scrollZoom': False})

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
    st.markdown("#### Treasury Yields")

    try:
        rates_data = treasury.get_all_rates()

        if rates_data.empty:
            st.info("Treasury rate data not available")
            return

        # Style dataframe with conditional coloring (inverse: lower yields = green)
        def _color_change_columns(series):
            colors = []
            for val in series:
                if val == '-' or pd.isna(val):
                    colors.append('color: #8b949e')  # Gray for N/A
                else:
                    try:
                        num = float(val.replace('+', ''))
                        if num > 0:
                            colors.append('color: #f85149')  # Red for higher yields
                        else:
                            colors.append('color: #3fb950')  # Green for lower yields
                    except (ValueError, AttributeError):
                        colors.append('color: #8b949e')
            return colors

        # Format values
        df = rates_data.copy()
        df['Yield'] = df['Yield'].apply(lambda x: f"{x:.3f}%" if pd.notna(x) else "-")
        df['Daily'] = df['Daily'].apply(lambda x: f"{x:+.3f}" if pd.notna(x) and x is not None else "-")
        df['Weekly'] = df['Weekly'].apply(lambda x: f"{x:+.3f}" if pd.notna(x) and x is not None else "-")
        df['Monthly'] = df['Monthly'].apply(lambda x: f"{x:+.3f}" if pd.notna(x) and x is not None else "-")

        styled_df = df.style.apply(_color_change_columns, subset=['Daily', 'Weekly', 'Monthly'])

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Maturity': st.column_config.TextColumn(width='small'),
                'Yield': st.column_config.TextColumn(width='small'),
                'Daily': st.column_config.TextColumn(width='small'),
                'Weekly': st.column_config.TextColumn(width='small'),
                'Monthly': st.column_config.TextColumn(width='small')
            }
        )

        st.caption("*Treasury yields updated daily (end of day)*")

    except Exception as e:
        st.error(f"Error loading rate data: {str(e)}")