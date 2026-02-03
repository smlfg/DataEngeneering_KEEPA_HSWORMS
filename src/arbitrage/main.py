"""
Main entry point for the Arbitrage Detector service.

This service analyzes products from Elasticsearch and generates
arbitrage alerts to Kafka.
"""

import os
import sys
import signal
import logging
from typing import Optional
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from consumer.indexer import ElasticsearchIndexer, create_indexer
from arbitrage.calculator import ArbitrageCalculator, create_calculator
from arbitrage.detector import (
    ArbitrageDetector,
    AlertDispatcher,
    create_detector,
    create_dispatcher,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ArbitrageService:
    """Orchestrates arbitrage detection."""

    def __init__(
        self,
        detector: ArbitrageDetector,
        indexer: ElasticsearchIndexer,
        poll_interval: int = 60,
    ):
        self.detector = detector
        self.indexer = indexer
        self.poll_interval = poll_interval

        self._running = False
        self._metrics = {
            "scans_completed": 0,
            "products_analyzed": 0,
            "opportunities_found": 0,
            "alerts_sent": 0,
        }

    def scan_and_detect(self) -> int:
        """
        Scan all products and detect arbitrage opportunities.

        Returns:
            Number of opportunities found
        """
        logger.info("Scanning products for arbitrage opportunities...")

        try:
            result = self.indexer.search(
                query={"term": {"is_active": True}},
                size=1000,
            )

            products = result.get("hits", [])

            if not products:
                logger.warning("No active products found")
                return 0

            opportunities = self.detector.detect_all(products)

            self._metrics["scans_completed"] += 1
            self._metrics["products_analyzed"] += self.detector.get_metrics()[
                "products_analyzed"
            ]
            self._metrics["opportunities_found"] += len(opportunities)
            self._metrics["alerts_sent"] += self.detector.get_metrics()["alerts_sent"]

            logger.info(
                f"Scan complete: {len(products)} products, "
                f"{len(opportunities)} opportunities found"
            )

            return len(opportunities)

        except Exception as e:
            logger.error(f"Scan failed: {e}")
            return 0

    def start(self) -> None:
        """Start the arbitrage detection service."""
        self._running = True

        logger.info("Starting Arbitrage Detector Service...")

        try:
            while self._running:
                self.scan_and_detect()

                if self._running:
                    logger.info(f"Sleeping for {self.poll_interval} seconds...")
                    import time

                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the service gracefully."""
        self._running = False
        self._print_final_metrics()

    def _print_final_metrics(self) -> None:
        """Print final metrics."""
        logger.info("=" * 50)
        logger.info("Final Metrics:")
        logger.info(f"  Scans completed: {self._metrics['scans_completed']}")
        logger.info(f"  Products analyzed: {self._metrics['products_analyzed']}")
        logger.info(f"  Opportunities found: {self._metrics['opportunities_found']}")
        logger.info(f"  Alerts sent: {self._metrics['alerts_sent']}")
        logger.info("=" * 50)


def create_service() -> ArbitrageService:
    """Factory function to create ArbitrageService."""
    indexer = create_indexer()
    dispatcher = create_dispatcher()
    detector = create_detector(dispatcher=dispatcher)

    poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))

    return ArbitrageService(
        detector=detector,
        indexer=indexer,
        poll_interval=poll_interval,
    )


def main():
    """Main entry point."""
    logger.info("=" * 50)
    logger.info("Arbitrage Detector Service Starting")
    logger.info("=" * 50)

    service = create_service()

    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        service.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    service.start()


if __name__ == "__main__":
    main()
