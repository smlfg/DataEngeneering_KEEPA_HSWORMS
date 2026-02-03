"""
Unit tests for Producer main module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os
from src.producer.main import WatchlistManager, KeepaProducer, load_config


class TestWatchlistManager:
    """Tests for WatchlistManager."""

    def test_load_from_file(self):
        """Test loading watchlist from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("# Comment line\n")
            f.write("B09V3KXJPB\n")
            f.write("B07Y19G9H2\n")
            f.write("INVALID\n")  # Invalid ASIN
            f.write("\n")  # Empty line
            temp_path = f.name

        try:
            manager = WatchlistManager(temp_path)
            watchlist = manager.get_watchlist()

            assert "B09V3KXJPB" in watchlist
            assert "B07Y19G9H2" in watchlist
            assert "INVALID" not in watchlist
            assert len(watchlist) == 2

        finally:
            os.unlink(temp_path)

    def test_load_from_env(self):
        """Test loading watchlist from environment."""
        with patch.dict(
            os.environ, {"ASIN_WATCHLIST": "B09V3KXJPB,B07Y19G9H2,B0000000000"}
        ):
            manager = WatchlistManager()
            watchlist = manager.get_watchlist()

            assert "B09V3KXJPB" in watchlist
            assert "B07Y19G9H2" in watchlist
            assert "B0000000000" in watchlist

    def test_file_not_found(self):
        """Test handling when watchlist file doesn't exist."""
        manager = WatchlistManager("/nonexistent/path.txt")
        watchlist = manager.get_watchlist()

        assert len(watchlist) == 0

    def test_add_asin(self):
        """Test adding ASIN to watchlist."""
        manager = WatchlistManager()

        result = manager.add_asin("B09V3KXJPB")
        assert result is True
        assert "B09V3KXJPB" in manager.get_watchlist()

        result = manager.add_asin("B09V3KXJPB")  # Duplicate
        assert result is False

    def test_add_invalid_asin(self):
        """Test adding invalid ASIN."""
        manager = WatchlistManager()

        result = manager.add_asin("TOOSHORT")
        assert result is False

        result = manager.add_asin("TOOLONG12345")
        assert result is False

    def test_remove_asin(self):
        """Test removing ASIN from watchlist."""
        manager = WatchlistManager()
        manager.add_asin("B09V3KXJPB")

        result = manager.remove_asin("B09V3KXJPB")
        assert result is True
        assert "B09V3KXJPB" not in manager.get_watchlist()

        result = manager.remove_asin("NOTEXIST")  # Doesn't exist
        assert result is False

    def test_asin_case_normalization(self):
        """Test that ASINs are normalized to uppercase."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("b09v3kxjpb\n")
            temp_path = f.name

        try:
            manager = WatchlistManager(temp_path)
            watchlist = manager.get_watchlist()

            assert "B09V3KXJPB" in watchlist

        finally:
            os.unlink(temp_path)


class TestKeepaProducer:
    """Tests for KeepaProducer."""

    @patch("src.producer.main.create_keepa_client")
    @patch("src.producer.main.create_kafka_producer")
    def test_producer_initialization(self, mock_kafka, mock_keepa):
        """Test producer initialization."""
        mock_keepa_client = Mock()
        mock_kafka_client = Mock()
        mock_keepa.return_value = mock_keepa_client
        mock_kafka.return_value = mock_kafka_client

        watchlist = WatchlistManager()
        watchlist.add_asin("B09V3KXJPB")

        producer = KeepaProducer(
            keepa_client=mock_keepa_client,
            kafka_producer=mock_kafka_client,
            watchlist_manager=watchlist,
            poll_interval=300,
            domain=1,
            batch_size=20,
        )

        assert producer.poll_interval == 300
        assert producer.domain == 1
        assert producer.batch_size == 20

    @patch("src.producer.main.create_keepa_client")
    @patch("src.producer.main.create_kafka_producer")
    def test_convert_to_message(self, mock_kafka, mock_keepa):
        """Test converting KeepaProduct to Kafka message."""
        from src.producer.keepa_client import KeepaProduct
        from src.producer.kafka_producer import KeepaUpdateMessage

        mock_keepa_client = Mock()
        mock_kafka_client = Mock()
        mock_keepa.return_value = mock_keepa_client
        mock_kafka.return_value = mock_kafka_client

        watchlist = WatchlistManager()

        producer = KeepaProducer(
            keepa_client=mock_keepa_client,
            kafka_producer=mock_kafka_client,
            watchlist_manager=watchlist,
        )

        product = KeepaProduct(
            asin="B09V3KXJPB",
            domain_id=1,
            title="Test Product",
            current_prices={"DE": 149.99, "IT": 89.99},
        )

        message = producer._convert_to_message(product)

        assert isinstance(message, KeepaUpdateMessage)
        assert message.asin == "B09V3KXJPB"
        assert message.marketplace == "DE"
        assert message.title == "Test Product"

    @patch("src.producer.main.create_keepa_client")
    @patch("src.producer.main.create_kafka_producer")
    def test_fetch_and_publish(self, mock_kafka, mock_keepa):
        """Test fetch and publish loop."""
        from src.producer.keepa_client import KeepaProduct

        mock_keepa_client = Mock()
        mock_kafka_client = Mock()
        mock_keepa_client.product_query.return_value = [
            KeepaProduct(asin="B09V3KXJPB", domain_id=1, title="Test")
        ]
        mock_kafka_client.send_batch.return_value = 1
        mock_keepa.return_value = mock_keepa_client
        mock_kafka.return_value = mock_kafka_client

        watchlist = WatchlistManager()
        watchlist.add_asin("B09V3KXJPB")

        producer = KeepaProducer(
            keepa_client=mock_keepa_client,
            kafka_producer=mock_kafka_client,
            watchlist_manager=watchlist,
        )

        sent = producer._fetch_and_publish()

        assert sent == 1
        mock_keepa_client.product_query.assert_called_once()
        mock_kafka_client.send_batch.assert_called_once()


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_from_file(self):
        """Test loading configuration from YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("poll_interval: 600\n")
            f.write("batch_size: 50\n")
            f.write("domain: 3\n")
            temp_path = f.name

        try:
            config = load_config(temp_path)

            assert config["poll_interval"] == 600
            assert config["batch_size"] == 50
            assert config["domain"] == 3

        finally:
            os.unlink(temp_path)

    def test_load_config_file_not_found(self):
        """Test loading config when file doesn't exist."""
        config = load_config("/nonexistent/config.yaml")

        assert config == {}

    def test_load_config_empty_file(self):
        """Test loading config from empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            config = load_config(temp_path)

            assert config == {}

        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
