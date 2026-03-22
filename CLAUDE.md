# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BBTerminal is a Bloomberg Launchpad-style financial dashboard for daily market monitoring and Data Quality (DQ) workflow. Built with Streamlit, it aggregates data from Yahoo Finance (yfinance), FRED API (fredapi), and exchange calendars (pandas-market-calendars).

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py

# Dashboard runs at http://localhost:8501
```

## Architecture

### Data Layer (`data/`)
- All fetchers inherit from `DataFetcher` base class (`data/fetcher.py`) which provides time-based caching
- `EquitiesFetcher` / `CommoditiesFetcher` use `yfinance` library
- `RatesFetcher` / `MortgagesFetcher` / `EconomicFetcher` use `fredapi` library
- Each fetcher returns pandas DataFrames

### Configuration (`config/settings.py`)
Central configuration file containing:
- FRED API key (loaded from `.env` via `FRED_API_KEY`)
- Refresh intervals, outlier thresholds, volatility windows
- Ticker/series dictionaries: `EQUITY_INDICES`, `SECTOR_ETFS`, `KEY_STOCKS`, `INTEREST_RATES`, `MORTGAGE_RATES`, `COMMODITIES`, `ECONOMIC_DATA`
- Exchange calendar mappings: `EXCHANGE_CALENDARS`

### Components (`components/`)
Streamlit UI panels that render different dashboard sections. Each component imports fetchers from `data/` and renders via Streamlit components. Panels handle their own error catching.

### Utilities (`utils/`)
- `dq_checks.py` - `DQChecker` class for outlier/stale/missing data detection using z-scores
- `calculations.py` - Returns, volatility, z-score calculations
- `formatters.py` - Display formatting utilities

## Key Patterns

**Adding a new data source:**
1. Add ticker/series ID to `config/settings.py`
2. Create fetcher in `data/` inheriting from `DataFetcher`
3. Create component in `components/` to render the data

**Data caching:**
The `DataFetcher` base class caches data for 5 minutes (300s) by default. Override `cache_duration` in subclass constructors if needed.

**DQ Alert System:**
`DQChecker.check_outliers()` returns a list of `DQAlert` dataclass objects with severity levels (low/medium/high). Uses z-score thresholds from settings.

## Environment Setup

Required: FRED API key in `.env` file:
```
FRED_API_KEY=your_actual_api_key_here
```
Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html