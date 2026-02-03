"""
Arbitrage opportunity detection and alert generation.
"""

import json
import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import asdict
from confluent_kafka import Producer  # type: ignore[import]

from .calculator import (
    ArbitrageCalculator,
    ArbitrageOpportunity,
    ConfidenceLevel,
    create_calculator,
)

logger = logging.getLogger(__name__)


class AlertDispatcher:
    """Dispatches arbitrage alerts to Kafka."""

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str = "arbitrage.alerts",
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic

        config = {
            "bootstrap.servers": bootstrap_servers,
            "acks": "all",
            "enable.idempotence": True,
        }

        self._producer = Producer(config)
        logger.info(f"Alert dispatcher initialized for topic: {topic}")

    def send_alert(self, opportunity: ArbitrageOpportunity) -> bool:
        """
        Send an arbitrage alert to Kafka.

        Args:
            opportunity: The arbitrage opportunity

        Returns:
            True if sent successfully
        """
        try:
            alert_data = {
                "id": str(uuid.uuid4()),
                "asin": opportunity.asin,
                "title": opportunity.title,
                "image_url": opportunity.image_url,
                "source_marketplace": opportunity.source_marketplace,
                "target_marketplace": opportunity.target_marketplace,
                "source_price": opportunity.source_price,
                "target_price": opportunity.target_price,
                "margin": opportunity.margin,
                "profit": opportunity.profit,
                "estimated_fees": opportunity.estimated_fees,
                "net_profit": opportunity.net_profit,
                "confidence": opportunity.confidence.value,
                "alert_type": "new_opportunity",
                "priority": opportunity.priority,
                "timestamp": opportunity.timestamp,
                "expires_at": (
                    datetime.utcnow() + datetime.timedelta(days=1)
                ).isoformat(),
            }

            self._producer.produce(
                topic=self.topic,
                key=opportunity.asin.encode("utf-8"),
                value=json.dumps(alert_data).encode("utf-8"),
            )
            self._producer.poll(0)

            logger.info(
                f"Alert sent for {opportunity.asin}: {opportunity.margin:.1f}% margin"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False

    def send_batch(self, opportunities: List[ArbitrageOpportunity]) -> int:
        """
        Send multiple alerts.

        Args:
            opportunities: List of opportunities

        Returns:
            Number of alerts sent
        """
        sent = 0
        for opp in opportunities:
            if self.send_alert(opp):
                sent += 1
        return sent

    def flush(self) -> None:
        """Flush pending messages."""
        self._producer.flush()


class ArbitrageDetector:
    """
    Detects arbitrage opportunities and generates alerts.

    Consumes enriched products from Elasticsearch and publishes alerts.
    """

    def __init__(
        self,
        calculator: ArbitrageCalculator,
        dispatcher: Optional[AlertDispatcher] = None,
        target_marketplace: str = "DE",
    ):
        self.calculator = calculator
        self.dispatcher = dispatcher
        self.target_marketplace = target_marketplace

        self._metrics = {
            "products_analyzed": 0,
            "opportunities_found": 0,
            "alerts_sent": 0,
        }

    def detect_for_product(
        self,
        product: Dict[str, Any],
    ) -> List[ArbitrageOpportunity]:
        """
        Detect arbitrage opportunities for a single product.

        Args:
            product: Product data from Elasticsearch

        Returns:
            List of arbitrage opportunities
        """
        asin = product.get("asin", "unknown")
        title = product.get("title")
        image_url = product.get("image_url")
        current_prices = product.get("current_prices", {})

        opportunities = self.calculator.find_opportunities(
            current_prices=current_prices,
            target_marketplace=self.target_marketplace,
        )

        for opp in opportunities:
            opp.asin = asin
            opp.title = title
            opp.image_url = image_url

        self._metrics["products_analyzed"] += 1
        self._metrics["opportunities_found"] += len(opportunities)

        if opportunities and self.dispatcher:
            for opp in opportunities:
                if self.dispatcher.send_alert(opp):
                    self._metrics["alerts_sent"] += 1

        return opportunities

    def detect_all(
        self,
        products: List[Dict[str, Any]],
    ) -> List[ArbitrageOpportunity]:
        """
        Detect arbitrage opportunities for multiple products.

        Args:
            products: List of product data

        Returns:
            List of all arbitrage opportunities
        """
        all_opportunities = []

        for product in products:
            opportunities = self.detect_for_product(product)
            all_opportunities.extend(opportunities)

        all_opportunities.sort(key=lambda x: x.priority, reverse=True)

        return all_opportunities

    def get_metrics(self) -> Dict[str, int]:
        """Get detector metrics."""
        return dict(self._metrics)


def create_detector(
    target_marketplace: Optional[str] = None,
    dispatcher: Optional[AlertDispatcher] = None,
) -> ArbitrageDetector:
    """Factory function to create ArbitrageDetector."""
    import os

    calculator = create_calculator()

    target = target_marketplace or os.getenv("TARGET_MARKETPLACE", "DE")

    return ArbitrageDetector(
        calculator=calculator,
        dispatcher=dispatcher,
        target_marketplace=target,
    )


def create_dispatcher(
    bootstrap_servers: Optional[str] = None,
    topic: Optional[str] = None,
) -> AlertDispatcher:
    """Factory function to create AlertDispatcher."""
    import os

    servers = bootstrap_servers or os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
    )
    alert_topic = topic or os.getenv("KAFKA_TOPIC_ALERTS", "arbitrage.alerts")

    return AlertDispatcher(
        bootstrap_servers=servers,
        topic=alert_topic,
    )


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)

    detector = create_detector()

    test_products = [
        {
            "asin": "B09V3KXJPB",
            "title": "Logitech MX Keys Mini Tastatur QWERTZ DE",
            "image_url": "https://example.com/image.jpg",
            "current_prices": {
                "DE": 149.99,
                "IT": 89.99,
                "ES": 92.50,
                "UK": 95.00,
                "FR": 94.00,
            },
        },
        {
            "asin": "B07Y19G9H2",
            "title": "Apple Magic Keyboard",
            "current_prices": {
                "DE": 199.99,
                "IT": 149.99,
                "ES": 159.99,
                "UK": 165.00,
                "FR": 162.00,
            },
        },
    ]

    print("Testing Arbitrage Detector...")
    print(f"Target marketplace: {detector.target_marketplace}")

    opportunities = detector.detect_all(test_products)

    print(f"\nFound {len(opportunities)} opportunities:")
    for opp in opportunities:
        print(f"\n{opp.asin}: {opp.title[:40]}...")
        print(f"  {opp.source_marketplace} → {opp.target_marketplace}")
        print(
            f"  Margin: {opp.margin:.1f}% | Profit: €{opp.profit:.2f} | Net: €{opp.net_profit:.2f}"
        )
        print(f"  Confidence: {opp.confidence.value} | Priority: {opp.priority}")

    print(f"\nMetrics: {detector.get_metrics()}")
