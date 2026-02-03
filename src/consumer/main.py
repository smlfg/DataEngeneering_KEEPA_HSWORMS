"""
Main entry point for the Enrichment Consumer service.

This service consumes raw Keepa updates from Kafka,
enriches the data, and indexes to Elasticsearch.
"""

import os
import sys
import signal
import logging
from typing import Optional
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from consumer.kafka_consumer import (
    KafkaConsumerClient,
    KeepaUpdateMessage,
    create_consumer,
    ensure_topic_exists,
)
from consumer.enricher import ProductEnricher, EnrichedProduct, create_enricher
from consumer.indexer import ElasticsearchIndexer, create_indexer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class EnrichmentService:
    """Orchestrates consumption, enrichment, and indexing."""

    def __init__(
        self,
        consumer: KafkaConsumerClient,
        enricher: ProductEnricher,
        indexer: ElasticsearchIndexer,
        output_topic: str = "products.enriched",
    ):
        self.consumer = consumer
        self.enricher = enricher
        self.indexer = indexer
        self.output_topic = output_topic

        self._running = False
        self._metrics = {
            "messages_processed": 0,
            "messages_failed": 0,
            "indexed": 0,
            "index_failed": 0,
        }

    def process_message(self, message: KeepaUpdateMessage) -> bool:
        """
        Process a single Keepa update message.

        Args:
            message: Raw message from Kafka

        Returns:
            True if processed successfully
        """
        try:
            logger.debug(f"Processing: {message.asin} from {message.marketplace}")

            enriched = self.enricher.enrich(message)

            success = self.indexer.upsert_enriched_product(enriched.to_dict())
            if success:
                self._metrics["indexed"] += 1
                logger.debug(f"Indexed: {message.asin}")
            else:
                self._metrics["index_failed"] += 1

            self._metrics["messages_processed"] += 1
            return success

        except Exception as e:
            logger.error(f"Failed to process {message.asin}: {e}")
            self._metrics["messages_failed"] += 1
            return False

    def start(self) -> None:
        """Start the enrichment service."""
        self._running = True

        logger.info("Starting Enrichment Consumer Service...")

        try:
            self.consumer.consume_forever(
                callback=self.process_message,
                poll_interval=1.0,
            )
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the service gracefully."""
        self._running = False
        self.consumer.close()
        self._print_final_metrics()

    def _print_final_metrics(self) -> None:
        """Print final metrics."""
        logger.info("=" * 50)
        logger.info("Final Metrics:")
        logger.info(f"  Messages processed: {self._metrics['messages_processed']}")
        logger.info(f"  Messages failed: {self._metrics['messages_failed']}")
        logger.info(f"  Indexed: {self._metrics['indexed']}")
        logger.info(f"  Index failed: {self._metrics['index_failed']}")
        logger.info("=" * 50)


def create_service() -> EnrichmentService:
    """Factory function to create EnrichmentService."""
    consumer = create_consumer()
    enricher = create_enricher()
    indexer = create_indexer()

    output_topic = os.getenv("KAFKA_TOPIC_ENRICHED", "products.enriched")

    return EnrichmentService(
        consumer=consumer,
        enricher=enricher,
        indexer=indexer,
        output_topic=output_topic,
    )


def main():
    """Main entry point."""
    logger.info("=" * 50)
    logger.info("Enrichment Consumer Service Starting")
    logger.info("=" * 50)

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    input_topic = os.getenv("KAFKA_TOPIC_RAW_UPDATES", "raw.keepa_updates")

    if not ensure_topic_exists(bootstrap_servers, input_topic):
        logger.warning(f"Topic {input_topic} may not exist")

    indexer = create_indexer()
    if not indexer.create_index_if_not_exists():
        logger.warning("Could not create Elasticsearch index")

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
