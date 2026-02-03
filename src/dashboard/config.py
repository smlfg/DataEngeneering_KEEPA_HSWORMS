"""
Dashboard configuration and utilities.
"""

import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")

REFRESH_INTERVALS = [30, 60, 120, 300]

DEFAULT_FILTERS = {
    "marketplace": "DE",
    "min_margin": 15,
    "max_price": 500,
    "source_marketplaces": ["IT", "ES", "UK", "FR"],
}

PAGE_CONFIG = {
    "page_title": "Amazon Arbitrage Tracker",
    "page_icon": "📈",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

COLUMN_CONFIG = {
    "asin": {"type": "LinkColumn", "help": "Click to view on Amazon"},
    "margin": {"type": "NumberColumn", "format": "%.1f"},
    "profit": {"type": "NumberColumn", "format": "%.2f"},
}
