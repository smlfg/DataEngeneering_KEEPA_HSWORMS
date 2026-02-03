"""
Kafka Producer for publishing Keepa price updates.
"""

import json
import logging
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from confluent_kafka import Producer  # type: ignore[import]
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
    current_prices: Dict[str, Optional[float]] = None  # type: ignore[assignment]
    avg_price: Optional[float] = None
    buy_box_price: Optional[float] = None
    buy_box_shipping: Optional[float] = None
    last_update: Optional[int] = None
    ean: Optional[str] = None
    mpn: Optional[str] = None
    image: Optional[str] = None
    url: Optional[str] = None
    category_id: Optional[int] = None
    category_tree: Optional[str] = None
    timestamp: str = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.current_prices is None:
            self.current_prices = {}
        if self.timestamp is None:
            from datetime import datetime

            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> bytes:
        return json.dumps(self.to_dict()).encode("utf-8")


class KafkaProducerClient:
    """
    Kafka producer for publishing Keepa price updates.

    Uses ASIN-based partitioning for consistent ordering per product.
    """

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str = "raw.keepa_updates",
        acks: str = "all",
        retries: int = 3,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.acks = acks
        self.retries = retries

        config = {
            "bootstrap.servers": bootstrap_servers,
            "acks": acks,
            "retries": retries,
            "enable.idempotence": True,
            "max.in.flight.requests.per.connection": 5,
            "linger.ms": 5,
            "compression.type": "lz4",
            "batch.size": 16384,
        }

        self._producer = Producer(config)
        logger.info(f"Kafka producer initialized for topic: {topic}")

    def _delivery_callback(self, err: Optional[Exception], msg) -> None:
        """Callback for delivery confirmation."""
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(
                f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
            )

    def _get_partition_key(self, asin: str) -> bytes:
        """Generate partition key from ASIN for consistent ordering."""
        return asin.encode("utf-8")

    def send_product_update(
        self,
        message: KeepaUpdateMessage,
        callback: Optional[Callable[[Optional[Exception], Any], None]] = None,
    ) -> None:
        """
        Send a single product update to Kafka.

        Args:
            message: KeepaUpdateMessage to send
            callback: Optional callback function(err, msg)
        """
        key = self._get_partition_key(message.asin)
        value = message.to_json()

        try:
            self._producer.produce(
                topic=self.topic,
                key=key,
                value=value,
                callback=callback or self._delivery_callback,
            )
            self._producer.poll(0)

        except BufferError:
            logger.warning("Producer buffer full, flushing...")
            self._producer.flush()
            self.send_product_update(message, callback)

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    def send_batch(
        self,
        messages: List[KeepaUpdateMessage],
        callback: Optional[Callable[[Optional[Exception], Any], None]] = None,
    ) -> int:
        """
        Send a batch of product updates to Kafka.

        Args:
            messages: List of KeepaUpdateMessage objects
            callback: Optional callback function(err, msg)

        Returns:
            Number of messages sent
        """
        sent_count = 0
        for message in messages:
            try:
                self.send_product_update(message, callback)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send message for {message.asin}: {e}")
                continue

        return sent_count

    def flush(self, timeout: float = 10.0) -> int:
        """
        Flush all pending messages.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            Number of messages still in queue (0 if all flushed)
        """
        return self._producer.flush(timeout)

    def close(self) -> None:
        """Close the producer and flush pending messages."""
        self.flush()
        logger.info("Kafka producer closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_kafka_producer(
    bootstrap_servers: Optional[str] = None,
    topic: Optional[str] = None,
) -> KafkaProducerClient:
    """Factory function to create KafkaProducerClient."""
    import os

    servers = bootstrap_servers or os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
    )
    kafka_topic = topic or os.getenv("KAFKA_TOPIC_RAW_UPDATES", "raw.keepa_updates")

    return KafkaProducerClient(
        bootstrap_servers=servers,
        topic=kafka_topic,
    )


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


if __name__ == "__main__":
    import os

    logging.basicConfig(level=logging.INFO)

    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC_RAW_UPDATES", "raw.keepa_updates")

    print(f"Testing Kafka producer...")
    print(f"Bootstrap servers: {bootstrap}")
    print(f"Topic: {topic}")

    if ensure_topic_exists(bootstrap, topic):
        producer = create_kafka_producer(bootstrap, topic)

        test_message = KeepaUpdateMessage(
            asin="B09V3KXJPB",
            marketplace="DE",
            domain_id=1,
            title="Test Product",
            current_price=149.99,
            current_prices={"DE": 149.99, "IT": 89.99},
            avg_price=139.99,
        )

        producer.send_product_update(test_message)
        producer.flush()

        print("Test message sent successfully!")
        producer.close()
    else:
        print("Failed to ensure topic exists")
