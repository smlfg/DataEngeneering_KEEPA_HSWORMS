"""
Streamlit dashboard for Amazon Arbitrage Tracker.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import os
import socket

st.set_page_config(
    page_title="Amazon Arbitrage Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_api_base_url():
    """Determine the correct API base URL based on environment."""
    env_url = os.getenv("API_BASE_URL", "")
    if env_url:
        return env_url

    # Check if running inside Docker
    hostname = socket.gethostname()
    # If we're running in Docker (arbitrage-dashboard container), use internal network
    if hostname == "arbitrage-dashboard" or os.path.exists("/.dockerenv"):
        return "http://api:8000"
    # Otherwise use localhost for browser access
    return "http://localhost:8000"


API_BASE_URL = get_api_base_url()


class APIClient:
    """API client for dashboard."""

    @staticmethod
    def get_products(params: dict = None) -> dict:
        """Fetch products from API."""
        try:
            response = requests.get(
                f"{API_BASE_URL}/products/", params=params, timeout=10
            )
            return response.json()
        except Exception as e:
            st.error(f"Error fetching products: {e}")
            return {"data": {"products": []}}

    @staticmethod
    def get_product(asin: str) -> dict:
        """Fetch single product."""
        try:
            response = requests.get(f"{API_BASE_URL}/products/{asin}", timeout=10)
            return response.json()
        except Exception as e:
            st.error(f"Error fetching product: {e}")
            return {"data": None}

    @staticmethod
    def get_arbitrage(params: dict = None) -> dict:
        """Fetch arbitrage opportunities."""
        try:
            response = requests.get(
                f"{API_BASE_URL}/arbitrage/", params=params, timeout=10
            )
            return response.json()
        except Exception as e:
            st.error(f"Error fetching arbitrage: {e}")
            return {"data": {"opportunities": []}}

    @staticmethod
    def get_health() -> dict:
        """Fetch health status."""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "services": {}}


def format_currency(value: float) -> str:
    """Format value as currency."""
    if value is None:
        return "N/A"
    return f"€{value:.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage."""
    if value is None:
        return "N/A"
    return f"{value:.1f}%"


def sidebar_filters():
    """Render sidebar filters."""
    st.sidebar.header("🎛️ Filter")

    marketplace = st.sidebar.selectbox(
        "Target Market",
        ["DE", "IT", "ES", "UK", "FR"],
        index=0,
        help="Select the marketplace where you want to sell",
    )

    min_margin = st.sidebar.slider(
        "Minimum Margin %",
        min_value=0,
        max_value=100,
        value=15,
        help="Filter opportunities below this margin",
    )

    max_price = st.sidebar.number_input(
        "Max Price (€)",
        min_value=0,
        max_value=10000,
        value=500,
        help="Maximum product price to consider",
    )

    source_marketplace = st.sidebar.multiselect(
        "Source Market(s)",
        ["IT", "ES", "UK", "FR"],
        default=["IT", "ES", "UK", "FR"],
        help="Filter by source marketplace(s)",
    )

    st.sidebar.markdown("---")
    st.sidebar.header("🔄 Refresh")

    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=False)
    refresh_interval = 60
    if auto_refresh:
        refresh_interval = st.sidebar.slider(
            "Refresh interval (seconds)",
            min_value=30,
            max_value=300,
            value=60,
        )

    return {
        "marketplace": marketplace,
        "min_margin": min_margin,
        "max_price": max_price,
        "source_marketplace": source_marketplace,
        "auto_refresh": auto_refresh,
        "refresh_interval": refresh_interval,
    }


def show_metrics_summary(data: dict):
    """Show top-level metrics."""
    opportunities = data.get("data", {}).get("opportunities", [])
    summary = data.get("data", {}).get("summary", {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Opportunities",
            summary.get("total_count", len(opportunities)),
            delta=None,
        )

    with col2:
        avg_margin = summary.get("avg_margin")
        st.metric(
            "Avg Margin",
            format_percentage(avg_margin) if avg_margin else "N/A",
        )

    with col3:
        avg_profit = summary.get("avg_profit")
        st.metric(
            "Avg Profit",
            format_currency(avg_profit) if avg_profit else "N/A",
        )

    with col4:
        highest_margin = summary.get("highest_margin")
        st.metric(
            "Best Margin",
            format_percentage(highest_margin) if highest_margin else "N/A",
        )


def show_opportunities_table(opportunities: list):
    """Show opportunities in a dataframe."""
    if not opportunities:
        st.info("No opportunities found matching your filters.")
        return

    df = pd.DataFrame(opportunities)

    st.subheader(f"📊 Top {len(opportunities)} Opportunities")

    display_df = df[
        [
            "asin",
            "title",
            "source_marketplace",
            "target_marketplace",
            "source_price",
            "target_price",
            "margin",
            "profit",
            "net_profit",
            "confidence",
        ]
    ].copy()

    display_df["title"] = display_df["title"].str[:40] + "..."

    st.dataframe(
        display_df,
        column_config={
            "asin": st.column_config.LinkColumn("ASIN", help="Click to view on Amazon"),
            "title": "Product",
            "source_marketplace": "From",
            "target_marketplace": "To",
            "source_price": st.column_config.NumberColumn("Buy (€)", format="%.2f"),
            "target_price": st.column_config.NumberColumn("Sell (€)", format="%.2f"),
            "margin": st.column_config.NumberColumn("Margin %", format="%.1f"),
            "profit": st.column_config.NumberColumn("Profit (€)", format="%.2f"),
            "net_profit": st.column_config.NumberColumn("Net (€)", format="%.2f"),
            "confidence": "Confidence",
        },
        hide_index=True,
        use_container_width=True,
    )

    return df


def show_margin_chart(df: pd.DataFrame):
    """Show margin distribution chart."""
    if df.empty:
        return

    st.subheader("📈 Margin Distribution")

    fig = px.histogram(
        df,
        x="margin",
        nbins=20,
        color="source_marketplace",
        title="Margin Distribution by Source Market",
        labels={"margin": "Margin (%)", "count": "Count"},
        opacity=0.7,
    )

    fig.update_layout(
        xaxis_title="Margin (%)",
        yaxis_title="Number of Products",
        showlegend=True,
    )

    st.plotly_chart(fig, use_container_width=True)


def show_profit_vs_margin(df: pd.DataFrame):
    """Show scatter plot of profit vs margin."""
    if df.empty:
        return

    st.subheader("💰 Profit vs Margin")

    fig = px.scatter(
        df,
        x="margin",
        y="profit",
        color="source_marketplace",
        size="target_price",
        hover_data=["asin", "title"],
        title="Profit vs Margin by Source Market",
        labels={
            "margin": "Margin (%)",
            "profit": "Profit (€)",
            "source_marketplace": "Source",
        },
    )

    fig.update_layout(
        xaxis_title="Margin (%)",
        yaxis_title="Profit (€)",
    )

    st.plotly_chart(fig, use_container_width=True)


def show_source_marketplace_breakdown(opportunities: list):
    """Show breakdown by source marketplace."""
    if not opportunities:
        return

    df = pd.DataFrame(opportunities)

    st.subheader("🌍 Source Market Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        counts = df["source_marketplace"].value_counts()
        fig = px.pie(
            values=counts.values,
            names=counts.index,
            title="Opportunities by Source Market",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        avg_by_source = (
            df.groupby("source_marketplace")
            .agg(
                {
                    "margin": "mean",
                    "profit": "mean",
                }
            )
            .round(2)
        )

        fig = px.bar(
            avg_by_source,
            x=avg_by_source.index,
            y="margin",
            title="Average Margin by Source Market",
            labels={"source_marketplace": "Market", "margin": "Avg Margin (%)"},
        )
        fig.update_layout(yaxis_title="Average Margin (%)")
        st.plotly_chart(fig, use_container_width=True)


def show_health_status():
    """Show service health status."""
    health = APIClient.get_health()

    st.sidebar.markdown("---")
    st.sidebar.header("🏥 System Status")

    if health.get("status") == "healthy":
        st.sidebar.success("All services healthy ✓")
    elif health.get("status") == "degraded":
        st.sidebar.warning("Some services degraded ⚠️")
    else:
        st.sidebar.error("System unhealthy ✗")

    services = health.get("services", {})
    for name, status in services.items():
        if isinstance(status, dict):
            s = status.get("status", "unknown")
            if s == "up":
                st.sidebar.text(f"✓ {name}")
            elif s == "down":
                st.sidebar.text(f"✗ {name}")
            else:
                st.sidebar.text(f"? {name}")


def main():
    """Main dashboard function."""
    st.title("📈 Amazon Arbitrage Tracker")
    st.markdown(
        "Find profitable arbitrage opportunities between European Amazon marketplaces"
    )

    filters = sidebar_filters()

    show_health_status()

    with st.spinner("Loading arbitrage opportunities..."):
        params = {
            "min_margin": filters["min_margin"],
            "min_profit": 0,
            "limit": 100,
            "target_marketplace": filters["marketplace"],
        }

        if filters["source_marketplace"]:
            params["source_marketplace"] = ",".join(filters["source_marketplace"])

        data = APIClient.get_arbitrage(params)

    show_metrics_summary(data)

    opportunities = data.get("data", {}).get("opportunities", [])

    if opportunities:
        df = show_opportunities_table(opportunities)

        col1, col2 = st.columns(2)

        with col1:
            show_margin_chart(df)

        with col2:
            show_profit_vs_margin(df)

        show_source_marketplace_breakdown(opportunities)

    else:
        st.info(
            f"No opportunities found with margin >= {filters['min_margin']}%. "
            "Try lowering the minimum margin filter."
        )

    with st.expander("ℹ️ About this dashboard"):
        st.markdown("""
        **Amazon Arbitrage Tracker**

        This dashboard shows arbitrage opportunities between European Amazon marketplaces.
        - **Source Market**: Where you buy the product (cheapest)
        - **Target Market**: Where you sell the product (most expensive)
        - **Margin**: (Target Price - Source Price) / Target Price × 100
        - **Net Profit**: Profit after estimated Amazon fees (~15%)

        Data is refreshed automatically from Elasticsearch.
        """)


if __name__ == "__main__":
    main()
