"""
Elasticsearch indexer for storing enriched products.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, NotFoundError  # type: ignore[import]

logger = logging.getLogger(__name__)


class ElasticsearchIndexer:
    """Handles indexing and querying of products in Elasticsearch."""

    def __init__(
        self,
        host: str,
        index: str = "products",
        refresh: bool = True,
    ):
        self.host = host
        self.index = index
        self.refresh = refresh

        self._client = Elasticsearch([host])
        logger.info(f"Elasticsearch indexer initialized for {host}/{index}")

    def ping(self) -> bool:
        """Check if Elasticsearch is available."""
        try:
            return self._client.ping()
        except Exception as e:
            logger.error(f"Failed to ping Elasticsearch: {e}")
            return False

    def create_index_if_not_exists(
        self, mapping: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create the products index if it doesn't exist.

        Args:
            mapping: Optional index mapping

        Returns:
            True if index exists or was created
        """
        try:
            if self._client.indices.exists(index=self.index):
                logger.info(f"Index '{self.index}' already exists")
                return True

            default_mapping = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "refresh_interval": "5s",
                },
                "mappings": {
                    "dynamic": "strict",
                    "properties": {
                        "asin": {"type": "keyword"},
                        "title": {
                            "type": "text",
                            "fields": {"keyword": {"type": "keyword"}},
                        },
                        "brand": {"type": "keyword"},
                        "category": {"type": "keyword"},
                        "image_url": {"type": "keyword", "index": False},
                        "product_url": {"type": "keyword", "index": False},
                        "current_prices": {
                            "type": "object",
                            "properties": {
                                "DE": {"type": "float"},
                                "IT": {"type": "float"},
                                "ES": {"type": "float"},
                                "UK": {"type": "float"},
                                "FR": {"type": "float"},
                            },
                        },
                        "price_history": {
                            "type": "nested",
                            "properties": {
                                "marketplace": {"type": "keyword"},
                                "price": {"type": "float"},
                                "timestamp": {"type": "date"},
                            },
                        },
                        "last_updated": {"type": "date"},
                        "first_seen": {"type": "date"},
                        "is_active": {"type": "boolean"},
                        "metadata": {"type": "object", "enabled": False},
                    },
                },
            }

            final_mapping = mapping or default_mapping
            self._client.indices.create(index=self.index, body=final_mapping)
            logger.info(f"Created index '{self.index}'")
            return True

        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False

    def upsert_product(self, product: Dict[str, Any]) -> bool:
        """
        Upsert a product document.

        Args:
            product: Product data dictionary

        Returns:
            True if successful
        """
        try:
            asin = product["asin"]

            self._client.update(
                index=self.index,
                id=asin,
                body={
                    "doc": product,
                    "doc_as_upsert": True,
                },
                refresh=self.refresh,
            )

            logger.debug(f"Upserted product: {asin}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to upsert product {product.get('asin', 'unknown')}: {e}"
            )
            return False

    def upsert_enriched_product(
        self,
        product: Dict[str, Any],
        existing: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Upsert enriched product, optionally merging with existing.

        Args:
            product: New product data
            existing: Existing document from Elasticsearch (optional)

        Returns:
            True if successful
        """
        try:
            asin = product["asin"]

            if existing:
                doc = self._merge_documents(existing, product)
            else:
                doc = product

            self._client.index(
                index=self.index,
                id=asin,
                body=doc,
                refresh=self.refresh,
            )

            logger.debug(f"Indexed product: {asin}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to index product {product.get('asin', 'unknown')}: {e}"
            )
            return False

    def _merge_documents(
        self, existing: Dict[str, Any], new: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge existing and new documents, preferring new values."""
        merged = existing.copy()

        for key, value in new.items():
            if value is not None:
                if key == "current_prices":
                    merged[key] = {**(existing.get(key, {})), **value}
                elif key == "price_history":
                    merged[key] = self._merge_price_history(
                        existing.get(key, {}),
                        value,
                    )
                elif key == "metadata":
                    merged[key] = {**(existing.get(key, {})), **(value or {})}
                else:
                    merged[key] = value

        return merged

    def _merge_price_history(
        self,
        existing: Dict[str, Any],
        new: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge price histories, keeping last 30 days per marketplace."""
        merged = {}
        cutoff = (datetime.utcnow() - timedelta(days=30)).isoformat()

        all_keys = set(existing.keys()) | set(new.keys())

        for key in all_keys:
            existing_points = existing.get(key, [])
            new_points = new.get(key, [])

            merged[key] = (existing_points + new_points)[-30:]

        return merged

    def get_product(self, asin: str) -> Optional[Dict[str, Any]]:
        """Get a product by ASIN."""
        try:
            result = self._client.get(index=self.index, id=asin)
            return result["_source"]
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to get product {asin}: {e}")
            return None

    def search(
        self,
        query: Optional[Dict[str, Any]] = None,
        size: int = 100,
        from_: int = 0,
        sort: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Search products.

        Args:
            query: Elasticsearch query (default: match all)
            size: Number of results
            from_: Offset for pagination
            sort: Sort configuration

        Returns:
            Search results
        """
        try:
            body = {}
            if query:
                body["query"] = query
            if sort:
                body["sort"] = sort

            result = self._client.search(
                index=self.index,
                body=body,
                size=size,
                from_=from_,
            )

            return {
                "total": result["hits"]["total"]["value"],
                "hits": [hit["_source"] for hit in result["hits"]["hits"]],
            }

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"total": 0, "hits": []}

    def search_arbitrage(
        self,
        min_margin: float = 15.0,
        target_marketplace: str = "DE",
        size: int = 100,
    ) -> Dict[str, Any]:
        """
        Search for arbitrage opportunities.

        Args:
            min_margin: Minimum margin percentage
            target_marketplace: Target marketplace code
            size: Number of results

        Returns:
            Products with potential arbitrage
        """
        query = {
            "bool": {
                "must": [
                    {"term": {"is_active": True}},
                ]
            }
        }

        result = self.search(query=query, size=1000)

        opportunities = []
        for product in result["hits"]:
            current_prices = product.get("current_prices", {})
            target_price = current_prices.get(target_marketplace)

            if not target_price:
                continue

            best_margin = 0
            best_source = None

            for source_mp, source_price in current_prices.items():
                if source_mp == target_marketplace or source_price is None:
                    continue

                margin = (target_price - source_price) / target_price * 100
                if margin > best_margin and margin >= min_margin:
                    best_margin = margin
                    best_source = source_mp

            if best_source:
                opportunities.append(
                    {
                        **product,
                        "best_margin": round(best_margin, 2),
                        "best_source": best_source,
                        "best_target": target_marketplace,
                        "best_profit": round(
                            target_price - current_prices.get(best_source, 0), 2
                        ),
                    }
                )

        opportunities.sort(key=lambda x: x["best_margin"], reverse=True)

        return {
            "total": len(opportunities),
            "hits": opportunities[:size],
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics."""
        try:
            result = self._client.search(
                index=self.index,
                body={
                    "size": 0,
                    "aggs": {
                        "total_products": {"value_count": {"field": "asin"}},
                        "avg_margin": {
                            "avg": {"script": {"source": "doc['best_margin'].value"}}
                        },
                        "highest_margin": {
                            "max": {"script": {"source": "doc['best_margin'].value"}}
                        },
                        "by_category": {
                            "terms": {"field": "category", "size": 20},
                        },
                    },
                },
            )

            aggs = result["aggregations"]

            return {
                "total_products": aggs["total_products"]["value"],
                "avg_margin": aggs["avg_margin"]["value"],
                "highest_margin": aggs["highest_margin"]["value"],
                "categories": aggs["by_category"]["buckets"],
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    def delete_product(self, asin: str) -> bool:
        """Delete a product by ASIN."""
        try:
            self._client.delete(index=self.index, id=asin, refresh=True)
            return True
        except NotFoundError:
            return False
        except Exception as e:
            logger.error(f"Failed to delete product {asin}: {e}")
            return False


def create_indexer(
    host: Optional[str] = None,
    index: Optional[str] = None,
) -> ElasticsearchIndexer:
    """Factory function to create ElasticsearchIndexer."""
    import os

    es_host = host or os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
    es_index = index or os.getenv("ELASTICSEARCH_INDEX", "products")

    return ElasticsearchIndexer(host=es_host, index=es_index)


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)

    indexer = create_indexer()

    print(f"Checking Elasticsearch connection...")
    if indexer.ping():
        print("✓ Connected to Elasticsearch")

        print(f"\nCreating index if not exists...")
        indexer.create_index_if_not_exists()

        print(f"\nIndex stats:")
        stats = indexer.get_stats()
        print(json.dumps(stats, indent=2, default=str))
    else:
        print("✗ Failed to connect to Elasticsearch")
