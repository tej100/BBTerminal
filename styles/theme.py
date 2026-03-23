"""
BBTerminal Theme Module
Centralized Bloomberg-style CSS for professional dashboard appearance
"""

# Color Palette
COLORS = {
    'bg_primary': '#0d1117',
    'bg_secondary': '#161b22',
    'bg_tertiary': '#21262d',
    'bg_card': '#1c2128',
    'text_primary': '#e6edf3',
    'text_secondary': '#8b949e',
    'text_muted': '#6e7681',
    'accent_orange': '#ff6b00',
    'accent_orange_dim': '#ff6b0033',
    'positive': '#3fb950',
    'negative': '#f85149',
    'warning': '#d29922',
    'info': '#58a6ff',
    'border': '#30363d',
}

# Base CSS applied to all pages
BASE_CSS = """
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Root variables */
    :root {
        --bg-primary: #0d1117;
        --bg-secondary: #161b22;
        --bg-tertiary: #21262d;
        --bg-card: #1c2128;
        --text-primary: #e6edf3;
        --text-secondary: #8b949e;
        --text-muted: #6e7681;
        --accent-orange: #ff6b00;
        --accent-orange-dim: rgba(255, 107, 0, 0.15);
        --positive: #3fb950;
        --negative: #f85149;
        --warning: #d29922;
        --info: #58a6ff;
        --border: #30363d;
    }

    /* Global overrides */
    .stApp {
        background-color: var(--bg-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Remove default padding */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: var(--accent-orange) !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        margin-bottom: 0.25rem !important;
        margin-top: 0.5rem !important;
    }

    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.25rem !important; }
    h3 { font-size: 1.1rem !important; }
    h4 { font-size: 1rem !important; }

    /* Metric cards */
    .stMetric {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        margin: 0.25rem 0;
    }

    .stMetric > label {
        color: var(--text-secondary) !important;
        font-size: 0.75rem !important;
        font-weight: 500;
        margin-bottom: 0.125rem !important;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 1.25rem !important;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }

    .stMetric [data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
        font-family: 'JetBrains Mono', monospace;
    }

    .stMetric [data-testid="stMetricDelta"] > svg {
        display: none;
    }

    /* Dataframes */
    .stDataFrame {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 6px;
    }

    .stDataFrame table {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }

    .stDataFrame th {
        background-color: var(--bg-tertiary) !important;
        color: var(--text-secondary) !important;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stDataFrame td {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: var(--bg-secondary);
        padding: 4px;
        border-radius: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: var(--bg-tertiary);
        color: var(--text-secondary);
        border-radius: 4px;
        padding: 0.375rem 0.75rem;
        font-size: 0.8rem;
        font-weight: 500;
        border: none;
        margin: 0;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--bg-card);
        color: var(--text-primary);
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--accent-orange-dim) !important;
        color: var(--accent-orange) !important;
        border: 1px solid var(--accent-orange) !important;
    }

    /* Sidebar */
    .stSidebar {
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border);
    }

    .stSidebar .block-container {
        padding-top: 0.5rem !important;
    }

    /* Columns - reduce gap */
    .stColumns {
        gap: 0.5rem !important;
    }

    /* Expander */
    .stExpander {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 6px;
    }

    .stExpander header {
        background-color: var(--bg-tertiary);
        color: var(--text-primary);
    }

    /* Messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        font-size: 0.85rem;
    }

    .stSuccess {
        background-color: rgba(63, 185, 80, 0.1);
        border: 1px solid var(--positive);
        color: var(--positive);
    }

    .stInfo {
        background-color: rgba(88, 166, 255, 0.1);
        border: 1px solid var(--info);
        color: var(--info);
    }

    .stWarning {
        background-color: rgba(210, 153, 34, 0.1);
        border: 1px solid var(--warning);
        color: var(--warning);
    }

    .stError {
        background-color: rgba(248, 81, 73, 0.1);
        border: 1px solid var(--negative);
        color: var(--negative);
    }

    /* Plots */
    .stPlotlyChart {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 6px;
        overflow: visible !important;
        overscroll-behavior: contain;
        touch-action: pan-x pan-y;
    }

    .stPlotlyChart > div {
        overflow: visible !important;
        padding-bottom: 0 !important;
    }

    .js-plotly-plot {
        overflow: visible !important;
        touch-action: pan-x pan-y;
    }

    .plotly-graph-div {
        overflow: visible !important;
    }

    /* Plotly modebar styling - position in title area */
    .modebar {
        background-color: rgba(22, 27, 34, 0.9) !important;
        border-radius: 4px;
        top: 0 !important;
        right: 0 !important;
    }

    .modebar-group {
        padding: 2px 4px !important;
    }

    .modebar-btn {
        font-size: 14px !important;
        padding: 3px 4px !important;
    }

    /* Horizontal rules */
    hr {
        border: none;
        border-top: 1px solid var(--border);
        margin: 0.5rem 0;
    }

    /* Captions and small text */
    .stCaption, p, small {
        color: var(--text-secondary);
        font-size: 0.8rem;
    }

    /* Buttons */
    .stButton button {
        background-color: var(--bg-tertiary);
        border: 1px solid var(--border);
        color: var(--text-primary);
        border-radius: 4px;
    }

    .stButton button:hover {
        background-color: var(--accent-orange-dim);
        border-color: var(--accent-orange);
        color: var(--accent-orange);
    }

    /* Select box */
    .stSelectbox label {
        color: var(--text-secondary);
        font-size: 0.8rem;
    }

    div[data-baseweb="select"] > div {
        background-color: var(--bg-tertiary);
        border-color: var(--border);
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--accent-orange);
    }

    /* Hide scrollbars */
    ::-webkit-scrollbar {
        display: none;
    }
    * {
        scrollbar-width: none;
        -ms-overflow-style: none;
    }

    /* Hide links and anchors */
    a, a:hover, a:visited, a:active {
        color: inherit !important;
        text-decoration: none !important;
        pointer-events: none;
    }
    .stMarkdown a {
        display: none;
    }
</style>
"""

# Compact card component CSS for metrics
COMPACT_CARD_CSS = """
<style>
    .metric-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        margin: 0.25rem;
    }
    .metric-card .label {
        color: var(--text-secondary);
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 0.125rem;
    }
    .metric-card .value {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-card .change {
        font-size: 0.85rem;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-card .change.positive {
        color: var(--positive);
    }
    .metric-card .change.negative {
        color: var(--negative);
    }
</style>
"""

# Dashboard header CSS
HEADER_CSS = """
<style>
    .dashboard-header {
        background: linear-gradient(90deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        border-bottom: 2px solid var(--accent-orange);
        padding: 0.5rem 1rem;
        margin: -1rem -1rem 0.5rem -1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .dashboard-title {
        color: var(--accent-orange);
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.25rem;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .dashboard-timestamp {
        color: var(--text-secondary);
        font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace;
    }
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .status-open {
        background-color: rgba(63, 185, 80, 0.15);
        color: var(--positive);
        border: 1px solid var(--positive);
    }
    .status-closed {
        background-color: rgba(248, 81, 73, 0.15);
        color: var(--negative);
        border: 1px solid var(--negative);
    }
</style>
"""


def get_metric_card_html(label: str, value: str, change: str = None, is_positive: bool = None) -> str:
    """
    Generate HTML for a compact metric card.

    Args:
        label: Metric label text
        value: Main value to display
        change: Optional change/delta text
        is_positive: Whether change is positive (for color). None = neutral.

    Returns:
        HTML string for the metric card
    """
    change_html = ""
    if change:
        change_class = "positive" if is_positive is True else ("negative" if is_positive is False else "")
        change_html = f'<div class="change {change_class}">{change}</div>'

    return f"""
    <div class="metric-card">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        {change_html}
    </div>
    """


def apply_theme():
    """Apply all theme CSS to the Streamlit app."""
    import streamlit as st
    st.markdown(BASE_CSS, unsafe_allow_html=True)
    st.markdown(COMPACT_CARD_CSS, unsafe_allow_html=True)
    st.markdown(HEADER_CSS, unsafe_allow_html=True)


def render_header():
    """Render the compact dashboard header."""
    from datetime import datetime
    import streamlit as st

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    st.markdown(f"""
    <div class="dashboard-header">
        <div class="dashboard-title">
            <span>BBTerminal</span>
        </div>
        <div class="dashboard-timestamp">
            {timestamp}
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_status_badge(is_open: bool) -> str:
    """Generate HTML for a market status badge."""
    status_class = "status-open" if is_open else "status-closed"
    status_text = "OPEN" if is_open else "CLOSED"
    dot_color = "#3fb950" if is_open else "#f85149"

    return f"""
    <span class="status-indicator {status_class}">
        <span style="width: 6px; height: 6px; border-radius: 50%; background: {dot_color};"></span>
        {status_text}
    </span>
    """