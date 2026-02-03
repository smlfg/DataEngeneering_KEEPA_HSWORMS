import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from src.consumer.kafka_consumer import KafkaConsumerClient, KeepaUpdateMessage


class TestKafkaConsumerClient:
    def setup_method(self):
        self.mock_consumer = MagicMock()
        self.client = KafkaConsumerClient(
            bootstrap_servers="localhost:9092",
            topic="raw.keepa_updates",
            group_id="test-consumer",
            consumer=self.mock_consumer,
        )

    def test_subscribe(self):
        """Test Topic-Subscription"""
        self.client.subscribe()

        self.mock_consumer.subscribe.assert_called_once_with(["raw.keepa_updates"])

    def test_poll_single_message(self):
        """Test Polling mit einer Nachricht"""
        mock_message = MagicMock()
        mock_message.value.return_value = {
            "asin": "B09V3KXJPB",
            "marketplace": "DE",
            "current_price": 99.99,
        }
        mock_message.partition.return_value = 0
        mock_message.offset.return_value = 100
        self.mock_consumer.poll.return_value = {0: [mock_message]}

        messages = self.client.poll(timeout_ms=1000)

        assert len(messages) == 1
        assert messages[0]["asin"] == "B09V3KXJPB"

    def test_poll_no_message(self):
        """Test Polling ohne Nachrichten"""
        self.mock_consumer.poll.return_value = {}

        messages = self.client.poll(timeout_ms=1000)

        assert len(messages) == 0

    def test_poll_multiple_partitions(self):
        """Test Polling mit mehreren Partitionen"""
        msg1 = MagicMock()
        msg1.value.return_value = {"asin": "B09V3KXJPB", "marketplace": "DE"}
        msg1.partition.return_value = 0
        msg1.offset.return_value = 100

        msg2 = MagicMock()
        msg2.value.return_value = {"asin": "B09V3KXJPX", "marketplace": "IT"}
        msg2.partition.return_value = 1
        msg2.offset.return_value = 50

        self.mock_consumer.poll.return_value = {0: [msg1], 1: [msg2]}

        messages = self.client.poll(timeout_ms=1000)

        assert len(messages) == 2

    def test_commit(self):
        """Test Offset-Commit"""
        self.client.commit()

        self.mock_consumer.commit.assert_called_once()

    def test_close(self):
        """Test Consumer schließen"""
        self.client.close()

        self.mock_consumer.close.assert_called_once()

    def test_seek(self):
        """Test Seek zu Offset"""
        self.client.seek(partition=0, offset=100)

        self.mock_consumer.seek.assert_called_once()

    def test_assignment(self):
        """Test Partition-Assignment"""
        self.mock_consumer.assignment.return_value = [0, 1, 2]

        assignment = self.client.assignment()

        assert len(assignment) == 3

    def test_position(self):
        """Test Position-Abfrage"""
        self.mock_consumer.position.return_value = 500

        pos = self.client.position(partition=0)

        assert pos == 500


class TestKeepaUpdateMessage:
    def test_create_message(self):
        """Test Nachricht erstellen"""
        msg = KeepaUpdateMessage(
            asin="B09V3KXJPB",
            marketplace="DE",
            domain_id=1,
            title="Test Product",
            current_price=99.99,
        )

        assert msg.asin == "B09V3KXJPB"
        assert msg.marketplace == "DE"
        assert msg.domain_id == 1
        assert msg.title == "Test Product"
        assert msg.current_price == 99.99

    def test_message_to_dict(self):
        """Test Nachricht zu Dictionary"""
        msg = KeepaUpdateMessage(
            asin="B09V3KXJPB", marketplace="DE", domain_id=1, current_price=99.99
        )

        msg_dict = msg.to_dict()

        assert msg_dict["asin"] == "B09V3KXJPB"
        assert msg_dict["marketplace"] == "DE"
        assert msg_dict["current_price"] == 99.99
        assert "timestamp" in msg_dict

    def test_message_from_dict(self):
        """Test Nachricht aus Dictionary erstellen"""
        data = {
            "asin": "B09V3KXJPB",
            "marketplace": "DE",
            "domain_id": 1,
            "title": "Test",
            "current_price": 99.99,
            "current_prices": {"DE": 99.99, "IT": 89.99},
        }

        msg = KeepaUpdateMessage.from_dict(data)

        assert msg.asin == "B09V3KXJPB"
        assert msg.current_prices["DE"] == 99.99
        assert msg.current_prices["IT"] == 89.99

    def test_message_with_optional_fields(self):
        """Test Nachricht mit optionalen Feldern"""
        msg = KeepaUpdateMessage(
            asin="B09V3KXJPB",
            marketplace="DE",
            domain_id=1,
            title="Test Product",
            brand="TestBrand",
            current_price=99.99,
            avg_price=109.99,
            buy_box_price=97.99,
            ean="1234567890123",
            mpn="ABC123",
            image="https://example.com/image.jpg",
            url="https://amazon.de/dp/B09V3KXJPB",
        )

        assert msg.brand == "TestBrand"
        assert msg.avg_price == 109.99
        assert msg.ean == "1234567890123"
        assert msg.mpn == "ABC123"

    def test_message_default_values(self):
        """Test Standardwerte"""
        msg = KeepaUpdateMessage(asin="B09V3KXJPB", marketplace="DE", domain_id=1)

        assert msg.title is None
        assert msg.brand is None
        assert msg.current_price is None
        assert msg.current_prices == {}
        assert msg.timestamp is not None

    def test_message_equality(self):
        """Test Nachrichten-Vergleich"""
        msg1 = KeepaUpdateMessage(
            asin="B09V3KXJPB",
            marketplace="DE",
            domain_id=1,
            timestamp="2025-01-10T12:00:00",
        )
        msg2 = KeepaUpdateMessage(
            asin="B09V3KXJPB",
            marketplace="DE",
            domain_id=1,
            timestamp="2025-01-10T12:00:00",
        )

        assert msg1 == msg2

    def test_message_inequality(self):
        """Test Nachrichten-Ungleichheit"""
        msg1 = KeepaUpdateMessage(asin="B09V3KXJPB", marketplace="DE", domain_id=1)
        msg2 = KeepaUpdateMessage(asin="B09V3KXJPX", marketplace="DE", domain_id=1)

        assert msg1 != msg2

    def test_message_serialization(self):
        """Test JSON-Serialisierung"""
        msg = KeepaUpdateMessage(
            asin="B09V3KXJPB", marketplace="DE", domain_id=1, current_price=99.99
        )

        json_str = msg.to_json()
        assert '"asin": "B09V3KXJPB"' in json_str
        assert '"marketplace": "DE"' in json_str

    def test_message_deserialization(self):
        """Test JSON-Deserialisierung"""
        json_str = '{"asin": "B09V3KXJPB", "marketplace": "DE", "domain_id": 1, "current_price": 99.99}'

        msg = KeepaUpdateMessage.from_json(json_str)

        assert msg.asin == "B09V3KXJPB"
        assert msg.current_price == 99.99
