"""
Unit tests for Keepa API client.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
from src.producer.keepa_client import (
    KeepaClient,
    KeepaProduct,
    KeepaRateLimitError,
    KeepaAPIError,
    KEEPA_DOMAIN_MAP,
    MARKETPLACE_DOMAIN_MAP,
)


class TestKeepaProduct:
    """Tests for KeepaProduct dataclass."""

    def test_product_creation(self):
        """Test basic product creation."""
        product = KeepaProduct(
            asin="B09V3KXJPB",
            domain_id=1,
            title="Test Product",
            brand="TestBrand",
        )

        assert product.asin == "B09V3KXJPB"
        assert product.domain_id == 1
        assert product.title == "Test Product"
        assert product.brand == "TestBrand"
        assert product.marketplace == "DE"

    def test_marketplace_property(self):
        """Test marketplace property returns correct code."""
        product = KeepaProduct(asin="TEST123", domain_id=1)
        assert product.marketplace == "DE"

        product = KeepaProduct(asin="TEST123", domain_id=3)
        assert product.marketplace == "UK"

        product = KeepaProduct(asin="TEST123", domain_id=5)
        assert product.marketplace == "IT"

        product = KeepaProduct(asin="TEST123", domain_id=99)
        assert product.marketplace == "UNKNOWN"

    def test_to_dict(self):
        """Test product serialization to dict."""
        product = KeepaProduct(
            asin="B09V3KXJPB",
            domain_id=1,
            title="Test Product",
            current_prices={"DE": 149.99, "IT": 89.99},
        )

        data = product.to_dict()

        assert data["asin"] == "B09V3KXJPB"
        assert data["marketplace"] == "DE"
        assert data["title"] == "Test Product"
        assert data["current_prices"]["DE"] == 149.99

    def test_from_keepa_response(self):
        """Test creating product from Keepa API response."""
        response = {
            "asin": "B09V3KXJPB",
            "domain": 1,
            "title": "Logitech MX Keys Mini",
            "brand": "Logitech",
            "img": "https://example.com/image.jpg",
            "url": "https://amazon.de/dp/B09V3KXJPB",
            "price": [
                {"marketplace": 1, "price": 14999},
                {"marketplace": 5, "price": 8999},
            ],
            "avg": 13999,
            "buyBox": 14999,
            "lastUpdate": 1705315200,
        }

        product = KeepaProduct.from_keepa_response(response)

        assert product.asin == "B09V3KXJPB"
        assert product.domain_id == 1
        assert product.title == "Logitech MX Keys Mini"
        assert product.current_prices["DE"] == 14999
        assert product.current_prices["IT"] == 8999
        assert product.avg_price == 13999


class TestKeepaClient:
    """Tests for KeepaClient."""

    @patch("src.producer.keepa_client.requests.Session")
    def test_client_initialization(self, mock_session_class):
        """Test client initialization with API key."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        client = KeepaClient(api_key="test_key")

        assert client.api_key == "test_key"
        assert client.requests_per_minute == 100
        assert mock_session.headers["Authorization"] == "Token test_key"

    def test_client_initialization_without_key(self):
        """Test client raises error without API key."""
        with pytest.raises(ValueError):
            KeepaClient(api_key=None)

    @patch("src.producer.keepa_client.requests.Session")
    def test_rate_limiting(self, mock_session_class):
        """Test rate limiting between requests."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"products": []}
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = KeepaClient(api_key="test_key", requests_per_minute=60)

        start_time = time.time()
        client._request("product", {"asin": "TEST123"})
        client._request("product", {"asin": "TEST456"})
        elapsed = time.time() - start_time

        assert elapsed >= 1.0  # At least 1 second between requests (60/min)

    @patch("src.producer.keepa_client.requests.Session")
    def test_request_handles_error(self, mock_session_class):
        """Test error handling in requests."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = KeepaClient(api_key="test_key")

        with pytest.raises(KeepaAPIError):
            client._request("product", {"asin": "TEST123"})

    @patch("src.producer.keepa_client.requests.Session")
    def test_product_query(self, mock_session_class):
        """Test product query method."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "products": [
                {
                    "asin": "B09V3KXJPB",
                    "domain": 1,
                    "title": "Test Product",
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = KeepaClient(api_key="test_key")
        products = client.product_query(["B09V3KXJPB"], domain=1)

        assert len(products) == 1
        assert products[0].asin == "B09V3KXJPB"
        mock_session.get.assert_called_once()


class TestDomainMapping:
    """Tests for domain mapping constants."""

    def test_keepa_domain_map(self):
        """Test Keepa domain ID mapping."""
        assert KEEPA_DOMAIN_MAP[1] == "DE"
        assert KEEPA_DOMAIN_MAP[3] == "UK"
        assert KEEPA_DOMAIN_MAP[5] == "IT"
        assert KEEPA_DOMAIN_MAP[6] == "ES"
        assert KEEPA_DOMAIN_MAP[8] == "FR"

    def test_marketplace_domain_map(self):
        """Test marketplace to domain ID mapping."""
        assert MARKETPLACE_DOMAIN_MAP["DE"] == 1
        assert MARKETPLACE_DOMAIN_MAP["UK"] == 3
        assert MARKETPLACE_DOMAIN_MAP["IT"] == 5
        assert MARKETPLACE_DOMAIN_MAP["ES"] == 6
        assert MARKETPLACE_DOMAIN_MAP["FR"] == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
