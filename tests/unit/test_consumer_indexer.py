import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from src.consumer.indexer import ElasticsearchIndexer


class TestElasticsearchIndexer:
    def setup_method(self):
        self.mock_es = MagicMock()
        self.indexer = ElasticsearchIndexer(
            host="http://localhost:9200", index_name="products", es_client=self.mock_es
        )

    def test_ping_success(self):
        """Test erfolgreicher Ping"""
        self.mock_es.ping.return_value = True

        result = self.indexer.ping()

        assert result is True
        self.mock_es.ping.assert_called_once()

    def test_ping_failure(self):
        """Test fehlgeschlagener Ping"""
        self.mock_es.ping.return_value = False

        result = self.indexer.ping()

        assert result is False

    def test_upsert_product_new(self):
        """Test Upsert für neues Produkt"""
        product = {
            "asin": "B09V3KXJPB",
            "title": "Test Product",
            "current_prices": {"DE": 99.99},
        }

        self.indexer.upsert_product(product)

        self.mock_es.index.assert_called_once()
        call_kwargs = self.mock_es.index.call_args[1]
        assert call_kwargs["index"] == "products"
        assert call_kwargs["id"] == "B09V3KXJPB"
        assert call_kwargs["document"]["asin"] == "B09V3KXJPB"

    def test_upsert_product_existing(self):
        """Test Upsert für bestehendes Produkt"""
        product = {"asin": "B09V3KXJPB", "title": "Updated Product"}

        self.indexer.upsert_product(product)

        self.mock_es.index.assert_called_once()

    def test_search_products_basic(self):
        """Test Produktsuche"""
        self.mock_es.search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [{"_source": {"asin": "B09V3KXJPB", "title": "Test"}}],
            }
        }

        results = self.indexer.search_products()

        assert results["total"] == 1
        assert len(results["products"]) == 1
        assert results["products"][0]["asin"] == "B09V3KXJPB"

    def test_search_products_empty(self):
        """Test leere Suchergebnisse"""
        self.mock_es.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}

        results = self.indexer.search_products()

        assert results["total"] == 0
        assert len(results["products"]) == 0

    def test_search_with_filters(self):
        """Test Suche mit Filtern"""
        self.mock_es.search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [{"_source": {"asin": "B09V3KXJPB", "marketplace": "DE"}}],
            }
        }

        results = self.indexer.search_products(
            marketplace="DE", min_margin=15, max_price=200
        )

        self.mock_es.search.assert_called_once()

    def test_get_product_by_asin(self):
        """Test Produkt nach ASIN abrufen"""
        self.mock_es.get.return_value = {
            "_source": {"asin": "B09V3KXJPB", "title": "Test"}
        }

        product = self.indexer.get_product_by_asin("B09V3KXJPB")

        assert product["asin"] == "B09V3KXJPB"
        self.mock_es.get.assert_called_once_with(index="products", id="B09V3KXJPB")

    def test_get_product_not_found(self):
        """Test Produkt nicht gefunden"""
        self.mock_es.get.side_effect = Exception("Not found")

        product = self.indexer.get_product_by_asin("NOTEXIST")

        assert product is None

    def test_get_stats(self):
        """Test Statistiken abrufen"""
        self.mock_es.search.return_value = {
            "hits": {"total": {"value": 100}, "hits": []},
            "aggregations": {"avg_price": {"value": 50.0}},
        }

        stats = self.indexer.get_stats()

        assert "total_products" in stats
        assert "avg_price" in stats

    def test_delete_product(self):
        """Test Produkt löschen"""
        self.indexer.delete_product("B09V3KXJPB")

        self.mock_es.delete.assert_called_once_with(index="products", id="B09V3KXJPB")

    def test_create_index_if_not_exists(self):
        """Test Index-Erstellung wenn nicht vorhanden"""
        self.mock_es.indices.exists.return_value = False

        self.indexer.create_index_if_not_exists()

        self.mock_es.indices.create.assert_called_once()

    def test_create_index_already_exists(self):
        """Test keine Index-Erstellung wenn bereits vorhanden"""
        self.mock_es.indices.exists.return_value = True

        self.indexer.create_index_if_not_exists()

        self.mock_es.indices.create.assert_not_called()

    def test_refresh_index(self):
        """Test Index-Refresh"""
        self.indexer.refresh_index()

        self.mock_es.indices.refresh.assert_called_once_with(index="products")

    def test_get_mapping(self):
        """Test Index-Mapping abrufen"""
        self.mock_es.indices.get_mapping.return_value = {
            "products": {"mappings": {"properties": {}}}
        }

        mapping = self.indexer.get_mapping()

        assert "properties" in mapping

    def test_bulk_index(self):
        """Test Bulk-Indexing"""
        products = [
            {"asin": "B09V3KXJPB", "title": "Product 1"},
            {"asin": "B09V3KXJPX", "title": "Product 2"},
        ]

        self.indexer.bulk_index(products)

        self.mock_es.bulk.assert_called_once()

    def test_count_documents(self):
        """Test Dokumenten-Anzahl"""
        self.mock_es.count.return_value = {"count": 42}

        count = self.indexer.count_documents()

        assert count == 42
        self.mock_es.count.assert_called_once()

    def test_search_arbitrage_opportunities(self):
        """Test Arbitrage-Opportunitätssuche"""
        self.mock_es.search.return_value = {
            "hits": {
                "total": {"value": 5},
                "hits": [
                    {"_source": {"asin": "B09V3KXJPB", "margin": 25.0}},
                    {"_source": {"asin": "B09V3KXJPX", "margin": 30.0}},
                ],
            }
        }

        opportunities = self.indexer.search_arbitrage_opportunities(min_margin=15)

        assert opportunities["total"] >= 0

    def test_update_product_field(self):
        """Test einzelnes Feld aktualisieren"""
        self.indexer.update_product_field(
            asin="B09V3KXJPB", field="current_prices.DE", value=119.99
        )

        self.mock_es.update.assert_called_once()
