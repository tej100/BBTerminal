# CLAUDE.md

## Project Overview

BBTerminal is a Bloomberg Launchpad-style financial dashboard for daily market monitoring and Data Quality (DQ) workflow. Built with Streamlit, it aggregates data from Yahoo Finance (yfinance), FRED API (fredapi), and exchange calendars (pandas-market-calendars).

## Commands

```bash
pip install -r requirements.txt  # Install dependencies
streamlit run app.py            # Run dashboard at http://localhost:8501
```

## Architecture

### Data Layer (`data/`)
- **Base class**: `DataFetcher` (`fetcher.py`) provides time-based caching (default 5 min)
- **yfinance-based**: `EquitiesFetcher`, `CommoditiesFetcher` - stock/commodity prices
- **FRED-based**: `MortgagesFetcher`, `EconomicFetcher` - mortgage rates & economic indicators
- **Treasury**: `TreasuryFetcher` - treasury yields from FRED (GS10, GS20, etc.)
- **Corporate actions**: `CorporateActionsFetcher` - stock splits, delistings, acquisitions (from stockanalysis.com)

### Components (`components/`)
Streamlit UI panels with tabs for different views:
- `market_summary.py` - Market status, key indices, dashboard header
- `equities_panel.py` - Sector performance table + corporate actions tab
- `commodities_panel.py` - Commodity prices + historical chart tab
- `rates_panel.py` - Yield curve chart + treasury yields table
- `mortgages_panel.py` - Mortgage rates + 30Y trend chart
- `economic_panel.py` - Economic indicators + historical chart tab
- `alerts_panel.py`, `holidays_panel.py` - DQ alerts and market holidays

### Styling (`styles/`)
- `theme.py` - Centralized Bloomberg-style CSS (`BASE_CSS`, `HEADER_CSS`, `COMPACT_CARD_CSS`)
- Apply via `from styles import apply_theme; apply_theme()`

### Configuration (`config/settings.py`)
- FRED API key from `.env` (`FRED_API_KEY`)
- Ticker dictionaries: `EQUITY_INDICES`, `SECTOR_ETFS`, `MORTGAGE_RATES`, `COMMODITIES`, `ECONOMIC_DATA`
- DQ thresholds, refresh intervals, exchange calendars

### Utilities (`utils/`)
- `dq_checks.py` - `DQChecker` for outlier/stale data detection

## Key Patterns

### Chart Styling (Plotly)
All charts follow this pattern:
```python
fig.update_layout(
    title=" ",                    # Blank title for toolbar space
    xaxis_title="",
    yaxis_title=...,
    height=280,
    showlegend=False,
    margin=dict(l=40, r=20, t=35, b=0),  # Tight margins
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e6edf3', size=10),
    xaxis=dict(gridcolor='#30363d', tickfont=dict(size=9), tickformat='%b %d'),  # Date format
    yaxis=dict(gridcolor='#30363d', tickfont=dict(size=9))
)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False, 'scrollZoom': False})
```

### KPI Metrics Order
Standard layout: `Current | 30D High | 30D Low` (not abbreviated)

### Adding New Data Source
1. Add ticker/series ID to `config/settings.py`
2. Create fetcher in `data/` inheriting from `DataFetcher`
3. Create component in `components/` following existing patterns

## Environment Setup

Required in `.env`:
```
FRED_API_KEY=your_key_here
```
Get free key at https://fred.stlouisfed.org/docs/api/api_key.html

## File Reference

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit app, renders all panels |
| `config/settings.py` | All configuration constants |
| `styles/theme.py` | Centralized CSS theme |
| `data/fetcher.py` | Base DataFetcher class with caching |
| `data/treasury.py` | Treasury yield curve data |
| `data/corporate_actions.py` | Corporate actions calendar |