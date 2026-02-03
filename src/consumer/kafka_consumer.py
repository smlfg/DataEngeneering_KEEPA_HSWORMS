"""
Kafka Consumer for processing raw Keepa updates.
"""

import json
import logging
from typing import Optional, Callable, Dict, Any, Union
from dataclasses import dataclass
from confluent_kafka import Consumer, KafkaError, KafkaException  # type: ignore[import]
from confluent_kafka.admin import AdminClient, NewTopic  # type: ignore[import]

logger = logging.getLogger(__name__)


@dataclass
class KeepaUpdateMessage:
    """Message structure for raw.keepa_updates topic."""

    asin: str
    marketplace: str
    domain_id: int
    title: Optional[str] = None
    brand: Optional[str] = None
    current_price: Optional[float] = None
    current_prices: Optional[Dict[str, Optional[float]]] = None
    avg_price: Optional[float] = None
    buy_box_price: Optional[float] = None
    buy_box_shipping: Optional[float] = None
    last_update: Optional[int] = None
    ean: Optional[str] = None
    mpn: Optional[str] = None
    image: Optional[str] = None
    url: Optional[str] = None
    category_id: Optional[int] = None
    category_tree: Optional[Union[str, Dict[str, Any]]] = None
    timestamp: Optional[str] = None

    def __post_init__(self) -> None:
        if self.current_prices is None:
            self.current_prices = {}
        if self.timestamp is None:
            from datetime import datetime

            self.timestamp = datetime.utcnow().isoformat()

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "KeepaUpdateMessage":
        """Create message from JSON dictionary."""
        current_prices = data.get("current_prices")
        if current_prices is None:
            price_val = data.get("current_price")
            marketplace = data.get("marketplace", "")
            current_prices = {marketplace: price_val} if price_val else {}

        return cls(
            asin=data.get("asin", ""),
            marketplace=data.get("marketplace", ""),
            domain_id=data.get("domain_id", 0),
            title=data.get("title"),
            brand=data.get("brand"),
            current_price=data.get("current_price"),
            current_prices=current_prices,
            avg_price=data.get("avg_price"),
            buy_box_price=data.get("buy_box_price"),
            buy_box_shipping=data.get("buy_box_shipping"),
            last_update=data.get("last_update"),
            ean=data.get("ean"),
            mpn=data.get("mpn"),
            image=data.get("image"),
            url=data.get("url"),
            category_id=data.get("category_id"),
            category_tree=data.get("category_tree"),
            timestamp=data.get("timestamp"),
        )


class KafkaConsumerClient:
    """
    Kafka consumer for processing Keepa price updates.

    Supports manual offset commit for at-least-once processing.
    """

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        auto_offset_reset: str = "earliest",
        enable_auto_commit: bool = False,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id

        config = {
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": auto_offset_reset,
            "enable.auto.commit": enable_auto_commit,
            "session.timeout.ms": 30000,
            "heartbeat.interval.ms": 10000,
            "max.poll.interval.ms": 300000,
        }

        self._consumer = Consumer(config)
        self._running = False
        logger.info(f"Kafka consumer initialized for topic: {topic}, group: {group_id}")

    def subscribe(self) -> None:
        """Subscribe to the configured topic."""
        self._consumer.subscribe([self.topic])
        logger.info(f"Subscribed to topic: {self.topic}")

    def consume(
        self,
        callback: Callable[[KeepaUpdateMessage], bool],
        max_records: int = 100,
    ) -> int:
        """
        Consume messages and call callback for each.

        Args:
            callback: Function to process each message, returns True on success
            max_records: Maximum records to consume in one batch

        Returns:
            Number of messages processed
        """
        processed = 0
        timeout_ms = 1000

        while processed < max_records:
            msg = self._consumer.poll(timeout_ms)

            if msg is None:
                break

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug(
                        f"Reached end of partition {msg.partition()} "
                        f"at offset {msg.offset()}"
                    )
                else:
                    raise KafkaException(msg.error())
            else:
                try:
                    data = json.loads(msg.value().decode("utf-8"))
                    message = KeepaUpdateMessage.from_json(data)

                    success = callback(message)
                    if success:
                        self._consumer.commit(asynchronous=False)
                        processed += 1
                        logger.debug(f"Processed message for {message.asin}")

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        return processed

    def consume_forever(
        self,
        callback: Callable[[KeepaUpdateMessage], bool],
        poll_interval: float = 1.0,
    ) -> None:
        """
        Consume messages continuously.

        Args:
            callback: Function to process each message
            poll_interval: Time between polls when no messages available
        """
        self._running = True
        self.subscribe()

        logger.info("Starting continuous consumption...")

        try:
            while self._running:
                processed = self.consume(callback, max_records=100)
                if processed == 0:
                    import time

                    time.sleep(poll_interval)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, stopping consumer...")
        finally:
            self.close()

    def stop(self) -> None:
        """Signal the consumer to stop."""
        self._running = False

    def close(self) -> None:
        """Close the consumer."""
        self._consumer.close()
        logger.info("Kafka consumer closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def ensure_topic_exists(
    bootstrap_servers: str,
    topic: str,
    num_partitions: int = 3,
    replication_factor: int = 1,
) -> bool:
    """
    Ensure the Kafka topic exists.

    Args:
        bootstrap_servers: Kafka broker addresses
        topic: Topic name
        num_partitions: Number of partitions
        replication_factor: Replication factor

    Returns:
        True if topic exists or was created successfully
    """
    admin = AdminClient({"bootstrap.servers": bootstrap_servers})

    try:
        metadata = admin.list_topics(timeout=10)

        if topic in metadata.topics:
            logger.info(f"Topic '{topic}' already exists")
            return True

        new_topic = NewTopic(
            topic,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
        )

        futures = admin.create_topics([new_topic])

        for topic_name, future in futures.items():
            try:
                future.result(timeout=10)
                logger.info(f"Topic '{topic_name}' created successfully")
            except Exception as e:
                logger.error(f"Failed to create topic '{topic_name}': {e}")
                return False

        return True

    except Exception as e:
        logger.error(f"Failed to check/create topic: {e}")
        return False


def create_consumer(
    bootstrap_servers: Optional[str] = None,
    topic: Optional[str] = None,
    group_id: Optional[str] = None,
) -> KafkaConsumerClient:
    """Factory function to create KafkaConsumerClient."""
    import os

    servers = bootstrap_servers or os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
    )
    kafka_topic = topic or os.getenv("KAFKA_TOPIC_RAW_UPDATES", "raw.keepa_updates")
    consumer_group = group_id or os.getenv("CONSUMER_GROUP", "enrichment-consumer")

    return KafkaConsumerClient(
        bootstrap_servers=servers,
        topic=kafka_topic,
        group_id=consumer_group,
    )


if __name__ == "__main__":
    import os

    logging.basicConfig(level=logging.INFO)

    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC_RAW_UPDATES", "raw.keepa_updates")
    group = os.getenv("CONSUMER_GROUP", "enrichment-consumer")

    print(f"Testing Kafka consumer...")
    print(f"Bootstrap servers: {bootstrap}")
    print(f"Topic: {topic}")
    print(f"Group: {group}")

    if ensure_topic_exists(bootstrap, topic):
        consumer = create_consumer(bootstrap, topic, group)

        def process_message(msg: KeepaUpdateMessage) -> bool:
            print(f"Received: {msg.asin} - {msg.title[:50] if msg.title else 'N/A'}...")
            return True

        print("Starting consumer (press Ctrl+C to stop)...")
        try:
            consumer.consume_forever(process_message)
        except KeyboardInterrupt:
            print("\nStopping consumer...")
            consumer.close()
    else:
        print("Failed to ensure topic exists")
