"""
Key Risk Indicators (KRI) Configuration

Format: kri_name: {ticker/tickers, low_threshold, [high_threshold], metric, condition, [lookback], [description]}

Thresholds:
- If only low_threshold: triggers low severity (yellow)
- If both thresholds: triggers low at low_threshold, high at high_threshold (red)

Metrics:
- last_price: Current price value
- daily_pct_change: Day-over-day percentage change
- z_score: Value relative to rolling mean/std (negative = below average)
- z_score_abs: Absolute z-score (magnitude of deviation)

Conditions:
- ">=": Value >= threshold
- "<=": Value <= threshold
- "abs": |Value| >= threshold
- "abs_le": |Value| <= threshold
"""

KRI_CONFIG = {
    # === PRICE-BASED KRIs ===
    "vix_elevated": {
        "ticker": "^VIX",
        "low_threshold": 25,
        "high_threshold": 35,
        "metric": "last_price",
        "condition": ">=",
        "description": "VIX at elevated levels"
    },

    "spy_large_move": {
        "ticker": "SPY",
        "low_threshold": 1.0,
        "high_threshold": 2.0,
        "metric": "daily_pct_change",
        "condition": "abs",
        "description": "SPY large daily move"
    },

    "sector_extreme_move": {
        "tickers": "SECTOR_ETFS",
        "low_threshold": 3.0,
        "high_threshold": 5.0,
        "metric": "daily_pct_change",
        "condition": "abs",
        "description": "Sector ETF extreme move"
    },

    # === Z-SCORE BASED KRIs ===
    "commodity_zscore_alert": {
        "tickers": "COMMODITIES",
        "low_threshold": 2.0,
        "high_threshold": 3.0,
        "metric": "z_score_abs",
        "condition": ">=",
        "lookback": 30,
        "description": "Sector unusual movement vs 30-day history"
    }
}