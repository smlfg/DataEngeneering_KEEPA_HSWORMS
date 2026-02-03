"""
Main entry point for the Keepa Producer service - Enhanced with Category Support.

This service can work in two modes:
1. ASIN Mode: Watchlist of specific ASINs (traditional)
2. Category Mode: Fetch ASINs from Keepa category bestsellers

Usage:
    # ASIN Mode (default)
    python -m src.producer.main

    # Category Mode
    CATEGORY_MODE=true python -m src.producer.main
"""

import os
import sys
import time
import signal
import logging
import threading
from typing import Optional, Set
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from producer.keepa_client import KeepaClient, KeepaProduct, create_keepa_client
from producer.kafka_producer import (
    KafkaProducerClient,
    KeepaUpdateMessage,
    create_kafka_producer,
    ensure_topic_exists,
)
from producer.category_watcher import CategoryWatcher, create_category_watcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class WatchlistManager:
    """Manages the ASIN watchlist from file or environment."""

    def __init__(self, watchlist_path: Optional[str] = None):
        self.watchlist_path = watchlist_path
        self._watchlist: Set[str] = set()
        self._lock = threading.Lock()
        self._load_watchlist()

    def _load_watchlist(self) -> None:
        """Load ASINs from file or environment."""
        asins = self._load_from_file()
        asins.update(self._load_from_env())
        self._watchlist = asins
        logger.info(f"Loaded {len(self._watchlist)} ASINs from watchlist")

    def _load_from_file(self) -> Set[str]:
        """Load ASINs from watchlist file."""
        if not self.watchlist_path:
            return set()

        path = Path(self.watchlist_path)
        if not path.exists():
            logger.warning(f"Watchlist file not found: {self.watchlist_path}")
            return set()

        asins = set()
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    asin = line.split()[0].upper()
                    if self._is_valid_asin(asin):
                        asins.add(asin)

        logger.info(f"Loaded {len(asins)} ASINs from file")
        return asins

    def _load_from_env(self) -> Set[str]:
        """Load ASINs from environment variable."""
        env_value = os.getenv("ASIN_WATCHLIST", "")
        if not env_value:
            return set()

        asins = set()
        for asin in env_value.split(","):
            asin = asin.strip().upper()
            if self._is_valid_asin(asin):
                asins.add(asin)

        logger.info(f"Loaded {len(asins)} ASINs from environment")
        return asins

    def _is_valid_asin(self, asin: str) -> bool:
        """Validate ASIN format (10 alphanumeric characters)."""
        return bool(asin and len(asin) == 10 and asin.isalnum())

    def get_watchlist(self) -> Set[str]:
        """Get current watchlist."""
        with self._lock:
            return set(self._watchlist)

    def add_asin(self, asin: str) -> bool:
        """Add a single ASIN to the watchlist."""
        asin = asin.upper()
        if not self._is_valid_asin(asin):
            logger.warning(f"Invalid ASIN: {asin}")
            return False

        with self._lock:
            if asin not in self._watchlist:
                self._watchlist.add(asin)
                logger.info(f"Added ASIN to watchlist: {asin}")
                return True
        return False

    def remove_asin(self, asin: str) -> bool:
        """Remove an ASIN from the watchlist."""
        asin = asin.upper()
        with self._lock:
            if asin in self._watchlist:
                self._watchlist.remove(asin)
                logger.info(f"Removed ASIN from watchlist: {asin}")
                return True
        return False


class KeepaProducer:
    """Main producer service that orchestrates Keepa API fetching and Kafka publishing."""

    def __init__(
        self,
        keepa_client: KeepaClient,
        kafka_producer: KafkaProducerClient,
        watchlist_manager: WatchlistManager,
        poll_interval: int = 300,
        domain: int = 1,
        batch_size: int = 20,
    ):
        self.keepa_client = keepa_client
        self.kafka_producer = kafka_producer
        self.watchlist = watchlist_manager
        self.poll_interval = poll_interval
        self.domain = domain
        self.batch_size = batch_size

        self._running = False
        self._last_poll: Optional[datetime] = None
        self._metrics = {
            "messages_sent": 0,
            "errors": 0,
            "polls_completed": 0,
        }

    def _convert_to_message(self, product: KeepaProduct) -> KeepaUpdateMessage:
        """Convert KeepaProduct to Kafka message."""
        return KeepaUpdateMessage(
            asin=product.asin,
            marketplace=product.marketplace,
            domain_id=product.domain_id,
            title=product.title,
            brand=product.brand,
            current_price=product.current_prices.get(product.marketplace),
            current_prices=product.current_prices,
            avg_price=product.avg_price,
            buy_box_price=product.buy_box_price,
            buy_box_shipping=product.buy_box_shipping,
            last_update=product.last_update,
            ean=product.ean,
            mpn=product.mpn,
            image=product.image,
            url=product.url,
            category_id=product.category_id,
            category_tree=product.category_tree,
        )

    def _fetch_and_publish(self) -> int:
        """Fetch product data from Keepa and publish to Kafka."""
        watchlist = self.watchlist.get_watchlist()
        if not watchlist:
            logger.warning("Watchlist is empty, skipping poll")
            return 0

        asins = list(watchlist)
        total_sent = 0
        total_errors = 0

        for i in range(0, len(asins), self.batch_size):
            batch = asins[i : i + self.batch_size]
            logger.info(
                f"Fetching batch {i // self.batch_size + 1}/{(len(asins) + self.batch_size - 1) // self.batch_size}"
            )

            try:
                products = self.keepa_client.product_query(
                    asins=batch,
                    domain=self.domain,
                    include_history=True,
                )

                messages = [self._convert_to_message(p) for p in products]

                sent = self.kafka_producer.send_batch(messages)
                total_sent += sent

                logger.info(f"Sent {sent} messages for {len(products)} products")

            except Exception as e:
                logger.error(f"Error fetching batch: {e}")
                total_errors += len(batch)

        self._metrics["messages_sent"] += total_sent
        self._metrics["errors"] += total_errors
        self._metrics["polls_completed"] += 1

        return total_sent

    def start(self) -> None:
        """Start the producer loop."""
        self._running = True
        logger.info("Starting Keepa producer...")

        try:
            while self._running:
                try:
                    sent = self._fetch_and_publish()
                    self._last_poll = datetime.utcnow()
                    logger.info(
                        f"Poll completed: {sent} messages sent, "
                        f"total: {self._metrics['messages_sent']}"
                    )

                except Exception as e:
                    logger.error(f"Error during poll: {e}")
                    self._metrics["errors"] += 1

                if self._running:
                    logger.info(f"Sleeping for {self.poll_interval} seconds...")
                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the producer gracefully."""
        self._running = False
        logger.info("Stopping Keepa producer...")
        self.kafka_producer.close()
        self._print_final_metrics()

    def _print_final_metrics(self) -> None:
        """Print final metrics before shutdown."""
        logger.info("=" * 50)
        logger.info("Final Metrics:")
        logger.info(f"  Messages sent: {self._metrics['messages_sent']}")
        logger.info(f"  Errors: {self._metrics['errors']}")
        logger.info(f"  Polls completed: {self._metrics['polls_completed']}")
        logger.info("=" * 50)


class CategoryProducer:
    """Producer that fetches ASINs from Keepa category bestsellers."""

    def __init__(
        self,
        keepa_client: KeepaClient,
        kafka_producer: KafkaProducerClient,
        category_watcher: CategoryWatcher,
        poll_interval: int = 600,
        batch_size: int = 20,
    ):
        self.keepa_client = keepa_client
        self.kafka_producer = kafka_producer
        self.category_watcher = category_watcher
        self.poll_interval = poll_interval
        self.batch_size = batch_size

        self._running = False
        self._last_poll: Optional[datetime] = None
        self._metrics = {
            "messages_sent": 0,
            "errors": 0,
            "polls_completed": 0,
            "asins_tracked": 0,
        }

    def _convert_to_message(
        self, product: KeepaProduct, source_domain: int = 1
    ) -> KeepaUpdateMessage:
        """Convert KeepaProduct to Kafka message."""
        from producer.keepa_client import KEEPA_DOMAIN_MAP

        marketplace = KEEPA_DOMAIN_MAP.get(source_domain, "UNKNOWN")

        return KeepaUpdateMessage(
            asin=product.asin,
            marketplace=marketplace,
            domain_id=source_domain,
            title=product.title,
            brand=product.brand,
            current_price=product.current_prices.get(marketplace),
            current_prices=product.current_prices,
            avg_price=product.avg_price,
            buy_box_price=product.buy_box_price,
            buy_box_shipping=product.buy_box_shipping,
            last_update=product.last_update,
            ean=product.ean,
            mpn=product.mpn,
            image=product.image,
            url=product.url,
            category_id=product.category_id,
            category_tree=product.category_tree,
        )

    def _fetch_and_publish(self) -> int:
        """Fetch products from all categories and publish to Kafka."""
        logger.info("🔄 Fetching ASINs from category bestsellers...")

        asins = self.category_watcher.get_asins()
        if not asins:
            logger.warning("No ASINs found from categories, skipping poll")
            return 0

        self._metrics["asins_tracked"] = len(asins)

        countries = self.category_watcher.get_countries()
        total_sent = 0
        total_errors = 0

        asins_list = list(asins)

        for i in range(0, len(asins_list), self.batch_size):
            batch = asins_list[i : i + self.batch_size]
            logger.info(
                f"Fetching batch {i // self.batch_size + 1}/{(len(asins_list) + self.batch_size - 1) // self.batch_size} "
                f"({len(batch)} ASINs)"
            )

            try:
                # Fetch from all configured countries
                for country_code, country_config in countries.items():
                    try:
                        products = self.keepa_client.product_query(
                            asins=batch,
                            domain=country_config.domain_id,
                            include_history=True,
                        )

                        messages = [
                            self._convert_to_message(p, country_config.domain_id)
                            for p in products
                        ]

                        sent = self.kafka_producer.send_batch(messages)
                        total_sent += sent

                        logger.info(
                            f"  {country_config.name}: {len(products)} products"
                        )

                    except Exception as e:
                        logger.error(f"  Error fetching {country_config.name}: {e}")
                        total_errors += len(batch)

            except Exception as e:
                logger.error(f"Error fetching batch: {e}")
                total_errors += len(batch)

        self._metrics["messages_sent"] += total_sent
        self._metrics["errors"] += total_errors
        self._metrics["polls_completed"] += 1

        return total_sent

    def start(self) -> None:
        """Start the category producer loop."""
        self._running = True
        logger.info("🚀 Starting Category Producer...")

        # Initial fetch
        logger.info("📦 Performing initial category fetch...")
        self._fetch_and_publish()

        try:
            while self._running:
                try:
                    sent = self._fetch_and_publish()
                    self._last_poll = datetime.utcnow()
                    logger.info(
                        f"Poll completed: {sent} messages sent, "
                        f"tracking {self._metrics['asins_tracked']} ASINs"
                    )

                except Exception as e:
                    logger.error(f"Error during poll: {e}")
                    self._metrics["errors"] += 1

                if self._running:
                    logger.info(f"💤 Sleeping for {self.poll_interval} seconds...")
                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the producer gracefully."""
        self._running = False
        logger.info("Stopping Category Producer...")
        self.kafka_producer.close()
        self._print_final_metrics()

    def _print_final_metrics(self) -> None:
        """Print final metrics before shutdown."""
        logger.info("=" * 50)
        logger.info("Final Metrics:")
        logger.info(f"  Messages sent: {self._metrics['messages_sent']}")
        logger.info(f"  Errors: {self._metrics['errors']}")
        logger.info(f"  Polls completed: {self._metrics['polls_completed']}")
        logger.info(f"  ASINs tracked: {self._metrics['asins_tracked']}")
        logger.info("=" * 50)


def load_config(config_path: str = "config/producer.yaml") -> dict:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        return {}

    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


def create_producer() -> KeepaProducer:
    """Factory function to create the producer instance."""
    config = load_config()

    poll_interval = int(
        os.getenv("POLL_INTERVAL_SECONDS", str(config.get("poll_interval", 300)))
    )
    batch_size = int(config.get("batch_size", 20))
    domain = int(config.get("domain", 1))

    watchlist_path = config.get("watchlist", {}).get("source") == "file"
    watchlist_file = config.get("watchlist", {}).get("path", "config/watchlist.txt")

    watchlist_manager = WatchlistManager(watchlist_file)

    keepa_client = create_keepa_client()
    kafka_producer = create_kafka_producer()

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC_RAW_UPDATES", "raw.keepa_updates")

    if not ensure_topic_exists(bootstrap_servers, topic):
        logger.warning(f"Topic {topic} may not exist, proceeding anyway")

    return KeepaProducer(
        keepa_client=keepa_client,
        kafka_producer=kafka_producer,
        watchlist_manager=watchlist_manager,
        poll_interval=poll_interval,
        domain=domain,
        batch_size=batch_size,
    )


def create_category_producer() -> CategoryProducer:
    """Factory function to create category-based producer."""
    config = load_config()

    poll_interval = int(
        os.getenv(
            "CATEGORY_POLL_INTERVAL", str(config.get("category_poll_interval", 600))
        )
    )
    batch_size = int(config.get("batch_size", 20))

    keepa_client = create_keepa_client()
    kafka_producer = create_kafka_producer()
    category_watcher = create_category_watcher()

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC_RAW_UPDATES", "raw.keepa_updates")

    if not ensure_topic_exists(bootstrap_servers, topic):
        logger.warning(f"Topic {topic} may not exist, proceeding anyway")

    return CategoryProducer(
        keepa_client=keepa_client,
        kafka_producer=kafka_producer,
        category_watcher=category_watcher,
        poll_interval=poll_interval,
        batch_size=batch_size,
    )


def main():
    """Main entry point."""
    logger.info("=" * 50)
    logger.info("Keepa Producer Service Starting")
    logger.info("=" * 50)

    # Check if running in category mode - FORCE ASIN MODE if ASIN_WATCHLIST is set
    asin_watchlist = os.getenv("ASIN_WATCHLIST", "")
    category_mode = (
        os.getenv("CATEGORY_MODE", "false").lower() == "true" and not asin_watchlist
    )

    # If ASIN_WATCHLIST is provided, always use ASIN mode
    if asin_watchlist:
        logger.info(f"📋 ASIN_WATCHLIST detected: {asin_watchlist}")
        logger.info("📋 Running in ASIN MODE (watchlist takes priority)")
        category_mode = False

    if category_mode:
        logger.info("🎯 Running in CATEGORY MODE")
        logger.info("Fetching ASINs from Keepa category bestsellers...")
        producer = create_category_producer()
    else:
        logger.info("📋 Running in ASIN MODE")
        logger.info("Fetching specific ASINs from watchlist...")
        producer = create_producer()

    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        producer.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    producer.start()


if __name__ == "__main__":
    main()
