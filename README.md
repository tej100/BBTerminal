# BBTerminal

A Bloomberg Launchpad-style financial dashboard for daily market monitoring and Data Quality (DQ) workflow. Built with Streamlit.

## Features

- **Market Summary**: Real-time indices overview (S&P 500, Nasdaq 100, Russell 2000, VIX)
- **Equities Panel**: Sector performance heatmap, key stocks, corporate actions tracking
- **Treasury Yields**: Full yield curve visualization (1M to 30Y) with daily/weekly/monthly changes
- **Mortgage Rates**: Current mortgage rates (30Y, 15Y, 5/1 ARM) and historical trends
- **Commodities**: Energy, metals, and agricultural commodity futures prices
- **Economic Indicators**: CPI, Unemployment, GDP, Non-Farm Payrolls, PCE, Retail Sales
- **Data Quality Alerts**: Outlier detection, stale data warnings, missing data identification
- **Holiday Calendar**: Global exchange holiday tracking (US, UK, Japan, Germany, Hong Kong, China)
- **Corporate Actions**: Stock splits, delistings, acquisitions, IPOs from stockanalysis.com

## Data Sources

| Data Type | Source | Library/API |
|-----------|--------|-------------|
| Equities & Commodities | Yahoo Finance | `yfinance` |
| Treasury Yield Curve | Treasury.gov | `fiscaldata.treasury.gov` XML API |
| Mortgages | FRED | `fredapi` |
| Economic Data | FRED | `fredapi` |
| Corporate Actions | stockanalysis.com | Web scraping |
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

Add your FRED API key to `.env`:

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
├── app.py                      # Main Streamlit application
├── config/
│   └── settings.py             # Tickers, series IDs, thresholds
├── data/
│   ├── fetcher.py              # Base data fetcher with time-based caching
│   ├── yfinance_fetcher.py     # Generic Yahoo Finance fetcher for equities & commodities
│   ├── fred_fetcher.py         # Unified FRED API fetcher for mortgages, economics, treasury
│   ├── treasury.py             # Treasury yields from FRED
│   ├── corporate_actions.py    # Corporate actions (stockanalysis.com)
│   └── calendars.py            # Holiday calendars
├── components/
│   ├── market_summary.py       # Top row market indices & quick stats
│   ├── equities_panel.py       # Equities grid with corporate actions tab
│   ├── rates_panel.py          # Yield curve chart & treasury yields table
│   ├── mortgages_panel.py      # Mortgage rates & 30Y trend chart
│   ├── commodities_panel.py    # Commodity prices & historical chart
│   ├── economic_panel.py       # Economic indicators & historical chart
│   ├── alerts_panel.py         # DQ alerts & market status
│   └── holidays_panel.py       # Holiday calendar
├── styles/
│   └── theme.py                # Centralized Bloomberg-style CSS
├── utils/
│   └── dq_checks.py            # Outlier detection, gap identification
├── requirements.txt
└── .env
```

## Auto-Refresh

The dashboard auto-refreshes data every 5 minutes. Press `R` to manually refresh.

## DQ Features

- **Outlier Detection**: Z-score based volatility spike detection
- **Stale Data Warnings**: Alerts for data not updated within expected timeframe
- **Missing Data**: Gap identification in time series
- **Corporate Actions**: Stock splits, delistings, acquisitions, IPOs, symbol changes
- **Holiday Awareness**: Cross-reference missing data with market holidays

## Styling

The dashboard uses a centralized Bloomberg-style theme (`styles/theme.py`) with:
- Dark color palette optimized for financial data
- JetBrains Mono for numeric data, Inter for text
- Compact card components for metrics
- Plotly chart styling with transparent backgrounds

## Customization

Edit `config/settings.py` to:
- Add/remove tracked tickers
- Modify outlier detection thresholds
- Change refresh intervals
- Add new exchange calendars

## License

MIT License