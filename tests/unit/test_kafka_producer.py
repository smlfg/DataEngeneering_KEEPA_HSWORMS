"""
Unit tests for Kafka Producer.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from src.producer.kafka_producer import (
    KeepaUpdateMessage,
    KafkaProducerClient,
)


class TestKeepaUpdateMessage:
    """Tests for KeepaUpdateMessage dataclass."""

    def test_message_creation(self):
        """Test basic message creation."""
        message = KeepaUpdateMessage(
            asin="B09V3KXJPB",
            marketplace="DE",
            domain_id=1,
            title="Test Product",
            current_price=149.99,
        )

        assert message.asin == "B09V3KXJPB"
        assert message.marketplace == "DE"
        assert message.domain_id == 1
        assert message.current_price == 149.99
        assert message.timestamp is not None

    def test_message_with_prices(self):
        """Test message with multiple marketplace prices."""
        message = KeepaUpdateMessage(
            asin="B09V3KXJPB",
            marketplace="DE",
            domain_id=1,
            current_prices={"DE": 149.99, "IT": 89.99, "ES": 92.50},
        )

        assert message.current_prices["DE"] == 149.99
        assert message.current_prices["IT"] == 89.99
        assert message.current_prices["ES"] == 92.50

    def test_to_dict(self):
        """Test message serialization to dict."""
        message = KeepaUpdateMessage(
            asin="B09V3KXJPB",
            marketplace="DE",
            domain_id=1,
            title="Test Product",
        )

        data = message.to_dict()

        assert data["asin"] == "B09V3KXJPB"
        assert data["marketplace"] == "DE"
        assert data["title"] == "Test Product"
        assert "timestamp" in data

    def test_to_json(self):
        """Test message serialization to JSON bytes."""
        message = KeepaUpdateMessage(
            asin="B09V3KXJPB",
            marketplace="DE",
            domain_id=1,
        )

        json_bytes = message.to_json()

        assert isinstance(json_bytes, bytes)
        data = json.loads(json_bytes)
        assert data["asin"] == "B09V3KXJPB"


class TestKafkaProducerClient:
    """Tests for KafkaProducerClient."""

    @patch("src.producer.kafka_producer.Producer")
    def test_client_initialization(self, mock_producer_class):
        """Test client initialization."""
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer

        client = KafkaProducerClient(
            bootstrap_servers="localhost:9092",
            topic="test-topic",
        )

        mock_producer_class.assert_called_once()
        call_kwargs = mock_producer_class.call_args[1]
        assert call_kwargs["bootstrap.servers"] == "localhost:9092"
        assert call_kwargs["acks"] == "all"

    @patch("src.producer.kafka_producer.Producer")
    def test_send_product_update(self, mock_producer_class):
        """Test sending a single product update."""
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer

        client = KafkaProducerClient(bootstrap_servers="localhost:9092")

        message = KeepaUpdateMessage(
            asin="B09V3KXJPB",
            marketplace="DE",
            domain_id=1,
            title="Test Product",
        )

        client.send_product_update(message)

        mock_producer.produce.assert_called_once()
        call_kwargs = mock_producer.produce.call_args[1]
        assert call_kwargs["topic"] == "raw.keepa_updates"
        assert call_kwargs["key"] == b"B09V3KXJPB"
        assert "value" in call_kwargs

    @patch("src.producer.kafka_producer.Producer")
    def test_send_batch(self, mock_producer_class):
        """Test sending a batch of messages."""
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer

        client = KafkaProducerClient(bootstrap_servers="localhost:9092")

        messages = [
            KeepaUpdateMessage(
                asin=f"ASIN{i:04d}",
                marketplace="DE",
                domain_id=1,
            )
            for i in range(5)
        ]

        sent_count = client.send_batch(messages)

        assert sent_count == 5
        assert mock_producer.produce.call_count == 5

    @patch("src.producer.kafka_producer.Producer")
    def test_flush(self, mock_producer_class):
        """Test flushing pending messages."""
        mock_producer = Mock()
        mock_producer.flush.return_value = 0
        mock_producer_class.return_value = mock_producer

        client = KafkaProducerClient(bootstrap_servers="localhost:9092")
        result = client.flush(timeout=5.0)

        mock_producer.flush.assert_called_once_with(5.0)
        assert result == 0

    @patch("src.producer.kafka_producer.Producer")
    def test_partition_key(self, mock_producer_class):
        """Test that partition key is ASIN."""
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer

        client = KafkaProducerClient(bootstrap_servers="localhost:9092")

        message = KeepaUpdateMessage(
            asin="B09V3KXJPB",
            marketplace="DE",
            domain_id=1,
        )

        client.send_product_update(message)

        call_kwargs = mock_producer.produce.call_args[1]
        assert call_kwargs["key"] == b"B09V3KXJPB"


class TestEnsureTopicExists:
    """Tests for ensure_topic_exists function."""

    @patch("src.producer.kafka_producer.AdminClient")
    def test_topic_already_exists(self, mock_admin_class):
        """Test when topic already exists."""
        from src.producer.kafka_producer import ensure_topic_exists

        mock_admin = Mock()
        mock_metadata = Mock()
        mock_metadata.topics = {"raw.keepa_updates": Mock()}
        mock_admin.list_topics.return_value = mock_metadata
        mock_admin_class.return_value = mock_admin

        result = ensure_topic_exists("localhost:9092", "raw.keepa_updates")

        assert result is True

    @patch("src.producer.kafka_producer.AdminClient")
    def test_create_new_topic(self, mock_admin_class):
        """Test creating a new topic."""
        from src.producer.kafka_producer import ensure_topic_exists

        mock_admin = Mock()
        mock_metadata = Mock()
        mock_metadata.topics = {}
        mock_admin.list_topics.return_value = mock_metadata

        mock_future = Mock()
        mock_future.result.return_value = None
        mock_admin.create_topics.return_value = {"raw.keepa_updates": mock_future}

        mock_admin_class.return_value = mock_admin

        result = ensure_topic_exists("localhost:9092", "raw.keepa_updates")

        assert result is True
        mock_admin.create_topics.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
