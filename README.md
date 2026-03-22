# BBTerminal

A Bloomberg Launchpad-style financial dashboard for daily market monitoring and Data Quality (DQ) workflow. Built with Streamlit.

## Features

- **Market Summary**: Real-time indices overview (S&P 500, Nasdaq 100, Russell 2000, VIX)
- **Equities Panel**: Sector performance heatmap, key stocks, corporate actions tracking
- **Interest Rates**: US Treasury yield curve visualization and key rate monitoring
- **Mortgage Rates**: Current mortgage rates and spreads to Treasuries
- **Commodities**: Energy, metals, and agricultural commodity prices
- **Economic Indicators**: CPI, Unemployment, GDP, Non-Farm Payrolls tracking
- **Data Quality Alerts**: Outlier detection, stale data warnings, missing data identification
- **Holiday Calendar**: Global exchange holiday tracking (US, UK, Japan, Germany, Hong Kong, China)

## Data Sources

| Data Type | Source | Library |
|-----------|--------|---------|
| Equities & Commodities | Yahoo Finance | `yfinance` |
| Interest Rates & Mortgages | FRED | `fredapi` |
| Economic Data | FRED | `fredapi` |
| Holiday Calendars | pandas-market-calendars | `pandas_market_calendars` |

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get FRED API Key

1. Go to [FRED API](https://fred.stlouisfed.org/docs/api/api_key.html)
2. Create a free account and request an API key

### 3. Configure Environment

Copy `.env.example` to `.env` and add your FRED API key:

```bash
cp .env.example .env
```

Edit `.env`:
```
FRED_API_KEY=your_actual_api_key_here
```

## Usage

Run the Streamlit dashboard:

```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## Project Structure

```
BBTerminal/
├── app.py                    # Main Streamlit application
├── config/
│   └── settings.py           # Tickers, series IDs, thresholds
├── data/
│   ├── fetcher.py            # Base data fetcher with caching
│   ├── equities.py           # Equity data (yfinance)
│   ├── rates.py              # Interest rate data (FRED)
│   ├── mortgages.py          # Mortgage rate data (FRED)
│   ├── commodities.py        # Commodity futures (yfinance)
│   ├── economic.py           # Economic indicators (FRED)
│   └── calendars.py          # Holiday calendars
├── components/
│   ├── market_summary.py      # Top row market indices
│   ├── equities_panel.py      # Equities grid
│   ├── rates_panel.py         # Yield curve & rates
│   ├── mortgages_panel.py     # Mortgage rates
│   ├── commodities_panel.py   # Commodity prices
│   ├── economic_panel.py      # Economic indicators
│   ├── alerts_panel.py        # DQ alerts
│   └── holidays_panel.py      # Holiday calendar
├── utils/
│   ├── dq_checks.py           # Outlier detection, gap identification
│   ├── calculations.py        # Returns, volatility, z-scores
│   └── formatters.py          # Display formatting
├── requirements.txt
└── .env
```

## Auto-Refresh

The dashboard auto-refreshes data every 5 minutes. Press `R` to manually refresh.

## DQ Features

- **Outlier Detection**: Z-score based volatility spike detection
- **Stale Data Warnings**: Alerts for data not updated within expected timeframe
- **Missing Data**: Gap identification in time series
- **Corporate Actions**: Recent dividends and stock splits
- **Holiday Awareness**: Cross-reference missing data with market holidays

## Customization

Edit `config/settings.py` to:
- Add/remove tracked tickers
- Modify outlier detection thresholds
- Change refresh intervals
- Add new exchange calendars

## License

MIT License