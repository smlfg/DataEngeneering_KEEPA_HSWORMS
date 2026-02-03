import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from src.consumer.enricher import ProductEnricher, EnrichedProduct


class TestProductEnricher:
    def setup_method(self):
        self.enricher = ProductEnricher()

    def test_enrich_new_product(self):
        """Test Anreicherung eines neuen Produkts"""
        raw_product = {
            "asin": "B09V3KXJPB",
            "marketplace": "DE",
            "title": "Test Product",
            "brand": "TestBrand",
            "current_price": 99.99,
            "timestamp": "2025-01-10T12:00:00",
        }

        enriched = self.enricher.enrich(raw_product)

        assert enriched["asin"] == "B09V3KXJPB"
        assert enriched["title"] == "Test Product"
        assert enriched["brand"] == "TestBrand"
        assert enriched["current_prices"]["DE"] == 99.99
        assert len(enriched["price_history"]["DE"]) == 1
        assert enriched["price_history"]["DE"][0]["price"] == 99.99

    def test_enrich_existing_product(self):
        """Test Anreicherung mit bestehendem Produkt"""
        existing = {
            "asin": "B09V3KXJPB",
            "title": "Original Title",
            "brand": "OriginalBrand",
            "current_prices": {"DE": 89.99, "IT": 79.99},
            "price_history": {
                "DE": [{"price": 89.99, "timestamp": "2025-01-10T11:00:00"}]
            },
            "first_seen": "2025-01-10T11:00:00",
            "is_active": True,
        }
        self.enricher._known_products["B09V3KXJPB"] = existing

        update = {
            "asin": "B09V3KXJPB",
            "marketplace": "ES",
            "current_price": 95.0,
            "timestamp": "2025-01-10T12:00:00",
        }

        enriched = self.enricher.enrich(update)

        assert enriched["asin"] == "B09V3KXJPB"
        assert enriched["title"] == "Original Title"
        assert enriched["current_prices"]["DE"] == 89.99
        assert enriched["current_prices"]["IT"] == 79.99
        assert enriched["current_prices"]["ES"] == 95.0
        assert enriched["first_seen"] == "2025-01-10T11:00:00"

    def test_merge_current_prices(self):
        """Test dass Prices korrekt gemerged werden"""
        existing = {"asin": "B09V3KXJPB", "current_prices": {"DE": 100.0, "IT": 90.0}}

        update = {"asin": "B09V3KXJPB", "marketplace": "ES", "current_price": 95.0}

        merged = self.enricher._merge_current_prices(existing, update)

        assert merged["DE"] == 100.0
        assert merged["IT"] == 90.0
        assert merged["ES"] == 95.0

    def test_merge_prices_update_existing(self):
        """Test dass bestehende Preise aktualisiert werden"""
        existing = {"asin": "B09V3KXJPB", "current_prices": {"DE": 100.0}}

        update = {"asin": "B09V3KXJPB", "marketplace": "DE", "current_price": 110.0}

        merged = self.enricher._merge_current_prices(existing, update)

        assert merged["DE"] == 110.0

    def test_add_to_price_history(self):
        """Test dass Preis-History korrekt erweitert wird"""
        existing = {
            "asin": "B09V3KXJPB",
            "price_history": {
                "DE": [{"price": 90.0, "timestamp": "2025-01-10T11:00:00"}]
            },
        }

        new_entry = {"price": 100.0, "timestamp": "2025-01-10T12:00:00"}

        history = self.enricher._add_to_price_history(
            existing["price_history"], "DE", new_entry
        )

        assert len(history["DE"]) == 2
        assert history["DE"][0]["price"] == 90.0
        assert history["DE"][1]["price"] == 100.0

    def test_price_history_limit(self):
        """Test dass History auf 30 Einträge begrenzt ist"""
        existing = {
            "asin": "B09V3KXJPB",
            "price_history": {
                "DE": [
                    {"price": 50.0 + i, "timestamp": f"2025-01-10T{10 + i:02d}:00:00"}
                    for i in range(30)
                ]
            },
        }

        new_entry = {"price": 100.0, "timestamp": "2025-01-10T12:00:00"}

        history = self.enricher._add_to_price_history(
            existing["price_history"], "DE", new_entry
        )

        assert len(history["DE"]) == 30
        assert history["DE"][-1]["price"] == 100.0
        assert history["DE"][0]["price"] == 51.0

    def test_preserve_first_seen(self):
        """Test dass first_seen nicht überschrieben wird"""
        existing = {"asin": "B09V3KXJPB", "first_seen": "2025-01-01T00:00:00"}

        update = {
            "asin": "B09V3KXJPB",
            "marketplace": "DE",
            "current_price": 100.0,
            "timestamp": "2025-01-10T12:00:00",
        }

        enriched = self.enricher.enrich(update)

        assert enriched["first_seen"] == "2025-01-01T00:00:00"

    def test_missing_fields(self):
        """Test mit fehlenden optionalen Feldern"""
        raw_product = {"asin": "B09V3KXJPB", "marketplace": "DE"}

        enriched = self.enricher.enrich(raw_product)

        assert enriched["asin"] == "B09V3KXJPB"
        assert enriched["title"] is None
        assert enriched["brand"] is None
        assert enriched["current_prices"]["DE"] is None

    def test_is_active_flag(self):
        """Test dass is_active auf True gesetzt wird"""
        raw_product = {"asin": "B09V3KXJPB", "marketplace": "DE"}

        enriched = self.enricher.enrich(raw_product)

        assert enriched["is_active"] is True

    def test_multiple_marketplaces(self):
        """Test mit mehreren Marketplaces gleichzeitig"""
        raw_product = {
            "asin": "B09V3KXJPB",
            "marketplace": "DE",
            "current_prices": {"DE": 100.0, "IT": 90.0, "ES": 95.0, "FR": 98.0},
        }

        enriched = self.enricher.enrich(raw_product)

        assert len(enriched["current_prices"]) == 4
        assert enriched["current_prices"]["DE"] == 100.0
        assert enriched["current_prices"]["IT"] == 90.0
        assert enriched["current_prices"]["ES"] == 95.0
        assert enriched["current_prices"]["FR"] == 98.0

    def test_enriched_product_dataclass(self):
        """Test EnrichedProduct Dataclass"""
        product = EnrichedProduct(
            asin="B09V3KXJPB",
            title="Test",
            current_prices={"DE": 100.0},
            price_history={
                "DE": [{"price": 100.0, "timestamp": "2025-01-10T12:00:00"}]
            },
            last_updated="2025-01-10T12:00:00",
            first_seen="2025-01-10T12:00:00",
            is_active=True,
        )

        assert product.asin == "B09V3KXJPB"
        assert product.title == "Test"
        assert product.current_prices["DE"] == 100.0
