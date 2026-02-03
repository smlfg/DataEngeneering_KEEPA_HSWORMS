"""
Keepa Arbitrage Pipeline DAG - Optimized Version

Features:
- Token-aware rate limiting (20 tokens/min = 28,800 tokens/day)
- Redis caching for ASINs (6 hour TTL)
- Multiple fetch modes: Category, Watchlist, Deals
- Adaptive batch sizing based on rate limits
- Token usage tracking and alerting

Schedule: Every 30 minutes
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.models import Variable
from airflow.exceptions import AirflowException
import os
import json
import logging
import time
from typing import List, Dict, Any, Optional
import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
KEEPA_API_BASE = "https://api.keepa.com"

# Rate limits (based on user's Keepa plan)
REQUESTS_PER_MINUTE = 20
REQUEST_INTERVAL = 60.0 / REQUESTS_PER_MINUTE  # 3 seconds
DAILY_TOKEN_LIMIT = 28800  # 20 tokens/min * 60 min * 24 hours

# Default DAG arguments
default_args = {
    "owner": "arbitrage-tracker",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "execution_timeout": timedelta(hours=2),
}

# DAG Definition
dag = DAG(
    "keepa_arbitrage_pipeline_v2",
    default_args=default_args,
    description="Optimized Keepa price fetching with token-aware rate limiting",
    schedule_interval="*/30 * * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["keepa", "arbitrage", "v2", "token-aware"],
    max_active_runs=1,
)


# =============================================================================
# Helper Functions
# =============================================================================


def get_keepa_api_key() -> str:
    """Get Keepa API key from environment or Airflow variable."""
    api_key = os.getenv("KEEPA_API_KEY")
    if not api_key:
        api_key = Variable.get("KEEPA_API_KEY", default_var=None)
    if not api_key:
        raise ValueError("KEEPA_API_KEY not configured")
    return api_key


def get_kafka_bootstrap_servers() -> str:
    """Get Kafka bootstrap servers."""
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")


def get_category_mode() -> bool:
    """Check if running in category mode."""
    return os.getenv("CATEGORY_MODE", "false").lower() == "true"


def get_deals_mode() -> bool:
    """Check if running in deals mode."""
    return os.getenv("DEALS_MODE", "false").lower() == "true"


def get_redis_host() -> str:
    """Get Redis host."""
    return os.getenv("REDIS_HOST", "redis")


def make_keepa_request(
    endpoint: str, params: Dict[str, Any], tokens_used: List[int]
) -> Dict[str, Any]:
    """
    Make a request to Keepa API with rate limiting.

    Args:
        endpoint: API endpoint
        params: Query parameters
        tokens_used: List to track token usage [count]

    Returns:
        API response
    """
    api_key = get_keepa_api_key()
    url = f"{KEEPA_API_BASE}/{endpoint}"

    # Rate limiting
    time.sleep(REQUEST_INTERVAL)

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    # Estimate token cost (simplified)
    if endpoint == "product":
        tokens_used[0] += params.get("asin", "").count(",") + 1
    elif endpoint in ("category", "bestsellers", "deals"):
        tokens_used[0] += 5

    return data


# =============================================================================
# Task 1: Check Rate Limits and Daily Budget
# =============================================================================


def check_rate_limits_and_budget(**context) -> str:
    """
    Check current rate limits and daily token budget.

    Returns:
        'proceed', 'wait_for_rate_limit', or 'wait_for_daily_reset'
    """
    api_key = get_keepa_api_key()

    try:
        # Check remaining requests from header
        response = requests.get(
            f"{KEEPA_API_BASE}/", params={"key": api_key, "domain": 1}, timeout=10
        )

        remaining = int(response.headers.get("X-RateLimit-Remaining", 20))
        context["ti"].xcom_push(key="rate_limit_remaining", value=remaining)

        # Check daily tokens used
        tokens_used = context["ti"].xcom_pull(key="daily_tokens_used") or 0
        context["ti"].xcom_push(key="daily_tokens_used", value=tokens_used)

        remaining_daily = DAILY_TOKEN_LIMIT - tokens_used

        logger.info(
            f"Rate limit remaining: {remaining}, Daily tokens remaining: {remaining_daily}"
        )

        # Decision logic
        if remaining < 3:
            return "wait_for_rate_limit"

        if remaining_daily < 100:  # Less than 100 tokens left
            return "wait_for_daily_reset"

        return "proceed"

    except Exception as e:
        logger.warning(f"Could not check rate limits: {e}, proceeding anyway")
        return "proceed"


check_rate_limits = BranchPythonOperator(
    task_id="check_rate_limits_and_budget",
    python_callable=check_rate_limits_and_budget,
    dag=dag,
)


wait_for_rate_limit = EmptyOperator(
    task_id="wait_for_rate_limit",
    dag=dag,
)

wait_for_daily_reset = EmptyOperator(
    task_id="wait_for_daily_reset",
    dag=dag,
)


# =============================================================================
# Task 2: Determine Fetch Mode
# =============================================================================


def determine_fetch_mode(**context) -> str:
    """Determine which fetch mode to use."""
    if get_deals_mode():
        return "fetch_deals"
    elif get_category_mode():
        return "fetch_category"
    else:
        return "fetch_watchlist"


determine_mode = BranchPythonOperator(
    task_id="determine_fetch_mode",
    python_callable=determine_fetch_mode,
    dag=dag,
)


# =============================================================================
# Task 3a: Fetch from Category Bestsellers (with Redis Cache)
# =============================================================================


def fetch_category_asins(**context):
    """
    Fetch ASINs from Keepa category bestsellers with Redis caching.

    Token Cost: 5 tokens per category
    """
    import sys

    sys.path.insert(0, "/opt/airflow/dags")

    from src.producer.category_watcher import CategoryWatcher

    config_path = os.getenv("CATEGORY_CONFIG", "config/categories.yaml")
    redis_host = get_redis_host()

    watcher = CategoryWatcher(
        config_path=config_path,
        redis_host=redis_host,
        cache_ttl=21600,  # 6 hours
    )

    force_refresh = context.get("force_refresh", False)

    try:
        asins = watcher.fetch_all_asins(force_refresh=force_refresh)
        unique_asins = list(set(asins))

        context["ti"].xcom_push(key="asins", value=unique_asins)
        context["ti"].xcom_push(key="tokens_used", value=watcher.get_tokens_used())
        context["ti"].xcom_push(key="fetch_mode", value="category")

        logger.info(f"Category mode: Found {len(unique_asins)} unique ASINs")
        return len(unique_asins)

    except Exception as e:
        logger.error(f"Error in category fetch: {e}")
        context["ti"].xcom_push(key="asins", value=[])
        return 0


fetch_category = PythonOperator(
    task_id="fetch_category",
    python_callable=fetch_category_asins,
    dag=dag,
)


# =============================================================================
# Task 3b: Fetch from Watchlist
# =============================================================================


def fetch_watchlist_asins(**context):
    """Fetch ASINs from watchlist file (no token cost)."""
    watchlist_path = os.getenv("ASIN_WATCHLIST_PATH", "config/watchlist.txt")

    try:
        asins = []
        with open(watchlist_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    asin = line.split()[0].upper()
                    if len(asin) == 10 and asin.isalnum():
                        asins.append(asin)

        unique_asins = list(set(asins))
        context["ti"].xcom_push(key="asins", value=unique_asins)
        context["ti"].xcom_push(key="tokens_used", value=0)
        context["ti"].xcom_push(key="fetch_mode", value="watchlist")

        logger.info(f"Watchlist mode: Found {len(unique_asins)} ASINs")
        return len(unique_asins)

    except Exception as e:
        logger.error(f"Error reading watchlist: {e}")
        context["ti"].xcom_push(key="asins", value=[])
        return 0


fetch_watchlist = PythonOperator(
    task_id="fetch_watchlist",
    python_callable=fetch_watchlist_asins,
    dag=dag,
)


# =============================================================================
# Task 3c: Fetch from Deals (Alternative Source)
# =============================================================================


def fetch_deals_asins(**context):
    """
    Fetch ASINs from Keepa Deals API.

    Token Cost: 5 tokens for up to 150 deals
    """
    tokens_used = [0]
    all_deals = []

    countries = [
        {"code": "DE", "domain_id": 3},
        {"code": "IT", "domain_id": 8},
        {"code": "ES", "domain_id": 9},
        {"code": "UK", "domain_id": 2},
        {"code": "FR", "domain_id": 4},
    ]

    for country in countries:
        try:
            data = make_keepa_request(
                "deals",
                {
                    "key": get_keepa_api_key(),
                    "domain": country["domain_id"],
                    "date_range": 24,  # Last 24 hours
                    "range": 150,  # Max deals
                },
                tokens_used,
            )

            deals = data.get("deals", [])
            for deal in deals:
                if "asin" in deal:
                    all_deals.append(
                        {
                            "asin": deal["asin"],
                            "country": country["code"],
                            "price": deal.get("price"),
                            "rating": deal.get("rating"),
                            "reviews": deal.get("reviews"),
                        }
                    )

            logger.info(f"Deals {country['code']}: {len(deals)} deals")

        except Exception as e:
            logger.error(f"Error fetching deals for {country['code']}: {e}")

    # Extract unique ASINs
    asins = list(set(deal["asin"] for deal in all_deals))

    context["ti"].xcom_push(key="asins", value=asins)
    context["ti"].xcom_push(key="tokens_used", value=tokens_used[0])
    context["ti"].xcom_push(key="fetch_mode", value="deals")
    context["ti"].xcom_push(key="deals_data", value=all_deals)

    logger.info(
        f"Deals mode: Found {len(asins)} unique ASINs from {len(all_deals)} deals"
    )
    return len(asins)


fetch_deals = PythonOperator(
    task_id="fetch_deals",
    python_callable=fetch_deals_asins,
    dag=dag,
)


# =============================================================================
# Task 4: Calculate Optimal Batch Size
# =============================================================================


def calculate_batch_size(**context) -> int:
    """
    Calculate optimal batch size based on rate limits and remaining tokens.

    Strategy:
    - Leave at least 20% rate limit buffer
    - Leave at least 500 tokens for daily budget
    """
    asins = context["ti"].xcom_pull(key="asins") or []
    rate_limit_remaining = context["ti"].xcom_pull(key="rate_limit_remaining") or 20
    daily_tokens_used = context["ti"].xcom_pull(key="daily_tokens_used") or 0

    if not asins:
        context["ti"].xcom_push(key="batches", value=[])
        context["ti"].xcom_push(key="batch_count", value=0)
        return 0

    # Calculate safe batch size (leave 20% buffer)
    safe_requests = int(rate_limit_remaining * 0.8)

    # Calculate daily token budget
    daily_remaining = DAILY_TOKEN_LIMIT - daily_tokens_used
    safe_daily = int(daily_remaining * 0.95)

    # Each batch of N ASINs costs N tokens
    # We need to split ASINs into multiple batches if we have many
    max_batches_by_rate = max(1, safe_requests)
    max_batches_by_daily = max(1, safe_daily // max(1, len(asins)))

    max_batches = min(max_batches_by_rate, max_batches_by_daily)
    batch_size = max(1, len(asins) // max_batches)

    # Create batches
    batches = [asins[i : i + batch_size] for i in range(0, len(asins), batch_size)]

    context["ti"].xcom_push(key="batches", value=batches)
    context["ti"].xcom_push(key="batch_count", value=len(batches))
    context["ti"].xcom_push(key="batch_size", value=batch_size)

    logger.info(f"Calculated {len(batches)} batches of ~{batch_size} ASINs each")
    return len(batches)


calculate_batches = PythonOperator(
    task_id="calculate_batches",
    python_callable=calculate_batch_size,
    dag=dag,
)


# =============================================================================
# Task 5: Fetch Prices for Batch (Dynamic Task)
# =============================================================================


def create_fetch_prices_task(batch_num: int):
    """Create a task to fetch prices for a specific batch."""

    def fetch_prices_batch(**context):
        api_key = get_keepa_api_key()
        bootstrap_servers = get_kafka_bootstrap_servers()

        batches = context["ti"].xcom_pull(key="batches")
        if not batches or batch_num >= len(batches):
            logger.info(f"Batch {batch_num} does not exist")
            return 0

        batch = batches[batch_num]
        logger.info(
            f"Fetching prices for batch {batch_num + 1}/{len(batches)} ({len(batch)} ASINs)"
        )

        tokens_used = [0]
        products = []

        for i in range(0, len(batch), 100):
            asin_chunk = batch[i : i + 100]
            asin_string = ",".join(asin_chunk)

            try:
                data = make_keepa_request(
                    "product",
                    {
                        "key": api_key,
                        "domain": 3,  # DE (target market)
                        "asin": asin_string,
                        "history": "1",
                    },
                    tokens_used,
                )

                for item in data.get("products", []):
                    products.append(
                        {
                            "asin": item.get("asin"),
                            "title": item.get("title"),
                            "brand": item.get("brand"),
                            "current_price": (item.get("current", [0])[0] / 100)
                            if item.get("current")
                            else None,
                            "current_prices": {
                                k: v / 100
                                for k, v in (item.get("price", {}) or {}).items()
                            },
                            "avg_price": (item.get("avg", [0])[0] / 100)
                            if item.get("avg")
                            else None,
                            "buy_box": (item.get("buyBox", 0) / 100)
                            if item.get("buyBox")
                            else None,
                            "domain_id": item.get("domain"),
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

            except Exception as e:
                logger.warning(f"Error fetching chunk {i // 100}: {e}")
                continue

        context["ti"].xcom_push(key=f"batch_products_{batch_num}", value=products)
        context["ti"].xcom_push(key=f"batch_tokens_{batch_num}", value=tokens_used[0])

        logger.info(
            f"Batch {batch_num + 1}: Fetched {len(products)} products ({tokens_used[0]} tokens)"
        )
        return len(products)

    return PythonOperator(
        task_id=f"fetch_prices_batch_{batch_num}",
        python_callable=fetch_prices_batch,
        dag=dag,
    )


# =============================================================================
# Task 6: Aggregate All Products
# =============================================================================


def aggregate_products(**context):
    """Aggregate products from all batches."""
    batches = context["ti"].xcom_pull(key="batches") or []
    batch_count = len(batches)

    all_products = []
    total_tokens = 0
    total_asins = 0

    for i in range(batch_count):
        products = context["ti"].xcom_pull(key=f"batch_products_{i}") or []
        tokens = context["ti"].xcom_pull(key=f"batch_tokens_{i}") or 0

        all_products.extend(products)
        total_tokens += tokens
        total_asins += len(products)

    # Update total tokens
    daily_tokens = context["ti"].xcom_pull(key="daily_tokens_used") or 0
    context["ti"].xcom_push(key="daily_tokens_used", value=daily_tokens + total_tokens)

    context["ti"].xcom_push(key="all_products", value=all_products)
    context["ti"].xcom_push(key="products_count", value=total_asins)

    logger.info(
        f"Aggregated {total_asins} products from {batch_count} batches ({total_tokens} tokens)"
    )
    return total_asins


aggregate = PythonOperator(
    task_id="aggregate_products",
    python_callable=aggregate_products,
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag,
)


# =============================================================================
# Task 7: Push to Kafka
# =============================================================================


def push_to_kafka(**context):
    """Push all products to Kafka topic."""
    from confluent_kafka import Producer

    bootstrap_servers = get_kafka_bootstrap_servers()
    topic = os.getenv("KAFKA_TOPIC_RAW_UPDATES", "raw.keepa_updates")
    products = context["ti"].xcom_pull(key="all_products") or []

    if not products:
        logger.warning("No products to push to Kafka")
        return 0

    conf = {
        "bootstrap.servers": bootstrap_servers,
        "client.id": "airflow-producer",
        "acks": "all",
        "retries": 3,
    }

    producer = Producer(conf)
    delivered = [0]

    def delivery_callback(err, msg):
        if err:
            logger.error(f"Delivery failed: {err}")
        else:
            delivered[0] += 1

    for product in products:
        try:
            producer.produce(
                topic=topic,
                value=json.dumps(product),
                key=product.get("asin", "").encode("utf-8"),
                callback=delivery_callback,
            )
        except Exception as e:
            logger.warning(f"Error producing message: {e}")

    producer.flush(timeout=30)

    context["ti"].xcom_push(key="kafka_messages_sent", value=delivered[0])
    logger.info(f"Pushed {delivered[0]} messages to Kafka topic {topic}")
    return delivered[0]


push_kafka = PythonOperator(
    task_id="push_to_kafka",
    python_callable=push_to_kafka,
    dag=dag,
)


# =============================================================================
# Task 8: Verify Elasticsearch Index
# =============================================================================


def verify_index(**context):
    """Verify that data was indexed in Elasticsearch."""
    import requests

    es_host = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
    index_name = os.getenv("ELASTICSEARCH_INDEX", "products")

    try:
        response = requests.get(f"{es_host}/{index_name}/_count", timeout=10)
        if response.status_code == 200:
            count = response.json().get("count", 0)
            context["ti"].xcom_push(key="es_product_count", value=count)
            logger.info(f"Elasticsearch product count: {count}")
            return count
        return 0
    except Exception as e:
        logger.error(f"Error verifying ES index: {e}")
        return 0


verify_es = PythonOperator(
    task_id="verify_index",
    python_callable=verify_index,
    dag=dag,
)


# =============================================================================
# Task 9: Publish Metrics
# =============================================================================


def publish_metrics(**context):
    """Publish run metrics."""
    import requests

    products_count = context["ti"].xcom_pull(key="products_count") or 0
    kafka_sent = context["ti"].xcom_pull(key="kafka_messages_sent") or 0
    tokens_used = context["ti"].xcom_pull(key="daily_tokens_used") or 0
    es_count = context["ti"].xcom_pull(key="es_product_count") or 0
    fetch_mode = context["ti"].xcom_pull(key="fetch_mode") or "unknown"

    metrics = {
        "run_timestamp": datetime.utcnow().isoformat(),
        "products_fetched": products_count,
        "kafka_messages_sent": kafka_sent,
        "tokens_used_total": tokens_used,
        "es_product_count": es_count,
        "fetch_mode": fetch_mode,
        "daily_token_budget": DAILY_TOKEN_LIMIT,
        "daily_tokens_remaining": DAILY_TOKEN_LIMIT - tokens_used,
    }

    logger.info(f"📊 Run Metrics: {json.dumps(metrics, indent=2)}")

    # Push to XCom for monitoring
    context["ti"].xcom_push(key="run_metrics", value=metrics)

    return products_count


publish = PythonOperator(
    task_id="publish_metrics",
    python_callable=publish_metrics,
    dag=dag,
)


# =============================================================================
# Task 10: Check for Alerts
# =============================================================================


def check_alerts(**context):
    """Check for critical conditions and send alerts."""
    tokens_used = context["ti"].xcom_pull(key="daily_tokens_used") or 0
    products_count = context["ti"].xcom_pull(key="products_count") or 0

    alerts = []

    # Token budget warning
    token_pct = tokens_used / DAILY_TOKEN_LIMIT * 100
    if token_pct > 90:
        alerts.append(f"⚠️ Token budget at {token_pct:.1f}%")
    elif token_pct > 95:
        alerts.append(f"🚨 Token budget CRITICAL at {token_pct:.1f}%")

    # No products fetched
    if products_count == 0:
        alerts.append("⚠️ No products fetched - check API connection")

    # Success
    if not alerts:
        alerts.append(
            f"✅ Run successful: {products_count} products, {tokens_used} tokens"
        )

    logger.info(" | ".join(alerts))
    context["ti"].xcom_push(key="alerts", value=alerts)

    return len(alerts)


alerts = PythonOperator(
    task_id="check_alerts",
    python_callable=check_alerts,
    dag=dag,
)


# =============================================================================
# DAG Structure
# =============================================================================

start = EmptyOperator(task_id="start", dag=dag)
end = EmptyOperator(
    task_id="end", trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS, dag=dag
)

# Task dependencies
start >> check_rate_limits

check_rate_limits >> [determine_mode, wait_for_rate_limit, wait_for_daily_reset]
wait_for_rate_limit >> determine_mode
wait_for_daily_reset >> determine_mode

determine_mode >> [fetch_category, fetch_watchlist, fetch_deals]
fetch_category >> calculate_batches
fetch_watchlist >> calculate_batches
fetch_deals >> calculate_batches

# Dynamic batch tasks
batch_count = Variable.get("max_batches", default_var=15)
for i in range(min(int(batch_count), 30)):
    batch_task = create_fetch_prices_task(i)
    calculate_batches >> batch_task >> aggregate

aggregate >> push_kafka >> verify_es >> publish >> alerts >> end
