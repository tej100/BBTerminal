# CLAUDE.md

## Development Guidelines

### Git Commits
- **Do NOT include Claude as co-author** in commits - all commits are authored by the human developer only
- Use clear, descriptive commit messages following conventional commits format (`refactor:`, `feat:`, `fix:`, etc.)

### Code Standards
- **PEP8 Compliance**: All Python code must follow [PEP8](https://www.python.org/dev/peps/pep-0008/) style guidelines
  - 4-space indentation (not tabs)
  - Max line length: 100 characters (soft), 120 characters (hard limit)
  - Use snake_case for functions/variables, PascalCase for classes
  - Two blank lines between top-level definitions; one between methods

## Recent Updates (March 2026)

### Key Risk Indicators (KRI) Framework - Tier 1
- **Dynamic Severity**: Each KRI has `low_threshold` and optional `high_threshold`
  - If only `low_threshold` set: triggers low severity (🟡 yellow)
  - If both set: triggers low at `low_threshold`, high at `high_threshold` (🔴 red)
- **Minimal Config**: {ticker/tickers, low_threshold, [high_threshold], metric, condition}
- **Tier 1 KRIs**:
  - `vix_elevated`: VIX 25-35 (low-high thresholds)
  - `spy_large_move`: SPY daily % 1.0%-2.0% (low-high thresholds)
  - `sector_extreme_move`: Sector ETF daily % 3%-5% (low-high thresholds)
  - `commodity_zscore_alert`: Commodity z-score 2.0-3.0 (low-high thresholds)
- **Generic Framework**: `KRIChecker.check_all()` auto-discovers and evaluates all KRIs
- **UI**: "Active" tab shows triggered KRIs (auto-colored), "All KRIs" tab shows framework status
- **Config Location**: KRIs defined in `config/kri_config.py` (separate from settings)
- **Ticker Groups**: `KRI_TICKER_GROUPS` in settings.py contains all Yahoo Finance groups (`MARKET_SUMMARY_TICKERS`, `SECTOR_ETFS`, `COMMODITIES`)

### UI Layout Improvements
- **Market Summary**: Consolidated all summary cards (indices, commodities, yields) into single horizontal row for compact display
- **Dynamic Configuration**: Market summary now uses dynamic ticker sets from `config/settings.py` instead of hardcoded values
- **Header Cleanup**: Removed redundant `####` headers and text from all component tabs (Current, Trend, etc.) since tab names provide context

### Data Architecture Refactoring
- **Generic FredFetcher**: Created unified `FredFetcher` class for all FRED API data (mortgages, economics, treasury)
- **Generic YahooFinanceFetcher**: Consolidated all Yahoo Finance data fetching into single `YahooFinanceFetcher` class in `yfinance_fetcher.py` - accepts any ticker config dictionary
- **Removed Specialized Fetchers**: Deleted `equities.py`, `commodities.py`, and `__init__.py` files across all packages for minimal codebase clutter
- **Date-Based Calculations**: Updated `FredFetcher`, `TreasuryFetcher`, `YahooFinanceFetcher` (equities/commodities) to calculate weekly/monthly changes based on actual calendar dates rather than record count (uses `timedelta` for days, `DateOffset` for weeks/months)
- **Enhanced DQ Monitoring**: Updated alerts panel to monitor all ticker categories (market summary, sector ETFs, commodities) for comprehensive data quality checks

### Styling & Performance
- **Chart Updates**: Replaced deprecated `use_container_width=True` with `width='stretch'` across all Plotly charts
- **Table Enhancements**: 
  - Treasury yields table: Added bps (basis points) display style
  - Mortgage rates table: Added weekly/monthly bps change columns with dynamic dropdown selection
  - Sector table: Fixed height for all 11 rows without scroll; increased Sector column width to 'medium' for better readability
- **Centralized Styling**: Moved conditional coloring functions (`color_rate_changes`, `color_price_changes`) to `styles/theme.py` for reusability across components
- **Compact Design**: Streamlined component layouts for better space utilization; adjusted main layout to [1, 3] ratio (25% equities, 75% right side) for optimal horizontal distribution
- **Removed Captions**: Eliminated all `st.caption()` calls throughout components to reduce vertical height and enable single-screen dashboard viewing

### Configuration
- **Enhanced Settings**: Expanded `MORTGAGE_RATES` and `ECONOMIC_DATA` dictionaries in `config/settings.py` for full config-driven operation
- **Unified Patterns**: All FRED-based data now follows consistent fetcher pattern

### Code Quality Improvements
- **Import Organization**: Moved all import statements to the top of files following Python best practices
- **Centralized Styling**: Moved conditional coloring functions (`color_rate_changes`, `color_price_changes`) to `styles/theme.py` for reusability across components
- **DRY Principle**: Eliminated code duplication by centralizing common styling logic
- **Code Condensation**: Simplified `TreasuryFetcher.get_latest_yields()` logic by removing redundant calculations and using helper functions
- **DRY Principle**: Eliminated code duplication in alerts panel by creating reusable `_check_ticker_category()` helper function and combining all ticker configurations

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
- **yfinance-based**: `YahooFinanceFetcher` - generic fetcher for equities, commodities, and indices from Yahoo Finance
- **FRED-based**: `FredFetcher` - unified fetcher for mortgage rates, economic indicators, and treasury data
- **Treasury**: `TreasuryFetcher` - treasury yields from FRED (GS10, GS20, etc.)
- **Corporate actions**: `CorporateActionsFetcher` - stock splits, delistings, acquisitions (from stockanalysis.com)

### Components (`components/`)
Streamlit UI panels with tabs for different views:
- `market_summary.py` - Market status, key indices, dashboard header (single row layout)
- `equities_panel.py` - Sector performance table + corporate actions tab
- `commodities_panel.py` - Commodity prices + historical chart tab
- `rates_panel.py` - Yield curve chart + treasury yields table (bps style)
- `mortgages_panel.py` - Mortgage rates + 30Y trend chart (bps columns, dynamic dropdown)
- `economic_panel.py` - Economic indicators + historical chart tab
- `alerts_panel.py`, `holidays_panel.py` - DQ alerts and market holidays

### Styling (`styles/`)
- `theme.py` - Centralized Bloomberg-style CSS (`BASE_CSS`, `HEADER_CSS`, `COMPACT_CARD_CSS`)
- Apply via `from styles import apply_theme; apply_theme()`

### Configuration (`config/settings.py`)
- FRED API key from `.env` (`FRED_API_KEY`)
- Ticker dictionaries: `MARKET_SUMMARY_TICKERS`, `SECTOR_ETFS`, `MORTGAGE_RATES`, `COMMODITIES`, `ECONOMIC_DATA`
- `KRI_TICKER_GROUPS`: Groups available for multi-ticker KRIs (all Yahoo Finance tickers)
- DQ thresholds, refresh intervals, exchange calendars

### KRI Configuration (`config/kri_config.py`)
- All KRI definitions in separate file for easy management
- Metrics: `last_price`, `daily_pct_change`, `z_score`, `z_score_abs`
- Conditions: `>=`, `<=`, `abs`, `abs_le`, `spike`

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
st.plotly_chart(fig, width='stretch', config={'displayModeBar': True, 'displaylogo': False, 'scrollZoom': False})
```

### KPI Metrics Order
Standard layout: `Current | 30D High | 30D Low` (not abbreviated)

### Adding New Data Source
1. Add ticker/series ID to `config/settings.py`
2. Create fetcher in `data/` inheriting from `DataFetcher`
3. Create component in `components/` following existing patterns

### Adding New KRIs
Each KRI is 100% configurable via `config/kri_config.py`. Example with dual thresholds:

```python
KRI_CONFIG = {
    "my_kri": {
        "ticker": "SYMBOL",           # or "tickers": "SECTOR_ETFS" for multi-ticker
        "low_threshold": 2.0,         # Required: triggers low severity (yellow)
        "high_threshold": 3.5,        # Optional: triggers high severity (red)
        "metric": "daily_pct_change",  # "last_price" | "daily_pct_change" | "z_score" | "z_score_abs"
        "condition": "abs",           # ">=" | "<=" | "abs" | "abs_le" | "spike"
        "lookback": 30,               # Optional: days for z-score calculation
        "description": "Brief description"
    }
}
```

**Metrics:**
- `last_price`: Current price value
- `daily_pct_change`: Day-over-day percentage change
- `z_score`: Value relative to rolling mean/std (negative = below average)
- `z_score_abs`: Absolute z-score (magnitude of deviation from norm)

**Conditions:**
- `>=`: Value >= threshold (for upward spikes)
- `<=`: Value <= threshold (for downward spikes)
- `abs`: |Value| >= threshold (for both directions)
- `abs_le`: |Value| <= threshold (for bounded ranges)

**Examples:**
- Oil spike (low=2%, high=4%): `{"ticker": "CL=F", "low_threshold": 2.0, "high_threshold": 4.0, "metric": "daily_pct_change", "condition": "abs"}`
- VIX elevated (low=25, high=35): `{"ticker": "^VIX", "low_threshold": 25.0, "high_threshold": 35.0, "metric": "last_price", "condition": ">="}`
- Sector unusual movement: `{"tickers": "SECTOR_ETFS", "low_threshold": 2.0, "high_threshold": 3.0, "metric": "z_score_abs", "condition": ">="}`

**Done!** `KRIChecker.check_all()` auto-discovers and runs all KRIs — no code changes needed

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
| `config/settings.py` | All configuration constants (tickers, thresholds, API keys) |
| `config/kri_config.py` | KRI definitions (separate for easy management) |
| `styles/theme.py` | Centralized CSS theme + conditional coloring functions (`color_rate_changes`, `color_price_changes`) |
| `data/fetcher.py` | Base DataFetcher class with caching |
| `data/yfinance_fetcher.py` | Generic Yahoo Finance fetcher (accepts any ticker config) |
| `data/fred_fetcher.py` | Unified FRED API fetcher for mortgages, economics, treasury |
| `data/kri_checker.py` | KRI framework (discovers and runs all KRIs from config) |
| `data/kri_metrics.py` | Pluggable metric handlers for KRI calculations |
| `data/treasury.py` | Treasury yield curve data |
| `data/corporate_actions.py` | Corporate actions calendar |