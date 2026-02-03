"""
Data enrichment logic for transforming Keepa data to canonical format.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from .kafka_consumer import KeepaUpdateMessage

logger = logging.getLogger(__name__)


KEEPA_TO_MARKETPLACE = {
    1: "DE",
    3: "UK",
    4: "US",
    5: "IT",
    6: "ES",
    7: "NL",
    8: "FR",
    9: "SE",
    10: "PL",
    11: "TR",
    12: "JP",
}


@dataclass
class EnrichedProduct:
    """Canonical product format for Elasticsearch."""

    asin: str
    title: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    category: Optional[str] = None
    current_prices: Dict[str, Optional[float]] = field(default_factory=dict)
    price_history: Dict[str, Any] = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    first_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asin": self.asin,
            "title": self.title,
            "brand": self.brand,
            "image_url": self.image_url,
            "product_url": self.product_url,
            "category": self.category,
            "current_prices": self.current_prices,
            "price_history": self.price_history,
            "last_updated": self.last_updated,
            "first_seen": self.first_seen,
            "is_active": self.is_active,
            "metadata": self.metadata,
        }


class ProductEnricher:
    """Transforms raw Keepa data to canonical format."""

    def __init__(self):
        self._known_products: Dict[str, Dict[str, Any]] = {}

    def enrich(self, raw_message: KeepaUpdateMessage) -> EnrichedProduct:
        """
        Transform raw Keepa update to canonical format.

        Args:
            raw_message: Raw message from Kafka

        Returns:
            EnrichedProduct ready for Elasticsearch
        """
        asin = raw_message.asin

        existing_data = self._known_products.get(asin, {})

        current_prices = existing_data.get("current_prices", {}).copy()
        if raw_message.current_prices:
            current_prices.update(raw_message.current_prices)
        elif raw_message.current_price is not None:
            current_prices[raw_message.marketplace] = raw_message.current_price

        price_history = existing_data.get("price_history", {}).copy()
        self._add_price_to_history(
            price_history,
            raw_message.marketplace,
            raw_message.current_price,
            raw_message.timestamp,
        )

        first_seen = existing_data.get("first_seen", datetime.utcnow().isoformat())

        # Extract category name from category_tree
        # categoryTree can be: string, dict {catId, name}, or list of dicts
        category = raw_message.category_tree
        if isinstance(category, list) and len(category) > 0:
            # Get the most specific category (last in tree)
            category = category[-1].get("name") if isinstance(category[-1], dict) else None
        elif isinstance(category, dict):
            category = category.get("name")
        # If still not a string, fallback to existing
        category = category if isinstance(category, str) else existing_data.get("category")

        enriched = EnrichedProduct(
            asin=asin,
            title=raw_message.title or existing_data.get("title"),
            brand=raw_message.brand or existing_data.get("brand"),
            image_url=raw_message.image or existing_data.get("image_url"),
            product_url=raw_message.url or existing_data.get("product_url"),
            category=category,
            current_prices=current_prices,
            price_history=price_history,
            first_seen=first_seen,
            last_updated=datetime.utcnow().isoformat(),
            metadata={
                "ean": raw_message.ean or existing_data.get("metadata", {}).get("ean"),
                "mpn": raw_message.mpn or existing_data.get("metadata", {}).get("mpn"),
                "domain_id": raw_message.domain_id or existing_data.get("domain_id"),
            },
        )

        self._known_products[asin] = enriched.to_dict()

        return enriched

    def _add_price_to_history(
        self,
        history: Dict[str, Any],
        marketplace: str,
        price: Optional[float],
        timestamp: Optional[str],
    ) -> None:
        """Add a price point to the history."""
        if price is None:
            return

        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()

        if marketplace not in history:
            history[marketplace] = []

        history[marketplace].append(
            {
                "price": price,
                "timestamp": timestamp,
            }
        )

        history[marketplace] = history[marketplace][-30:]

    def merge_updates(
        self, existing: Dict[str, Any], new: EnrichedProduct
    ) -> Dict[str, Any]:
        """
        Merge new enriched data with existing Elasticsearch document.

        Args:
            existing: Existing document from Elasticsearch
            new: New enriched product

        Returns:
            Merged document ready for indexing
        """
        merged = existing.copy()

        merged["title"] = new.title or existing.get("title")
        merged["brand"] = new.brand or existing.get("brand")
        merged["image_url"] = new.image_url or existing.get("image_url")
        merged["product_url"] = new.product_url or existing.get("product_url")
        merged["category"] = new.category or existing.get("category")

        existing_prices = existing.get("current_prices", {})
        new_prices = new.current_prices
        merged["current_prices"] = {**existing_prices, **new_prices}

        existing_history = existing.get("price_history", {})
        new_history = new.price_history
        merged["price_history"] = self._merge_history(existing_history, new_history)

        merged["last_updated"] = new.last_updated
        merged["is_active"] = new.is_active

        merged["metadata"] = {**(existing.get("metadata", {})), **(new.metadata or {})}

        return merged

    def _merge_history(
        self,
        existing: Dict[str, Any],
        new: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge price histories, keeping only last 30 days."""
        merged = {}

        all_keys = set(existing.keys()) | set(new.keys())

        for key in all_keys:
            existing_points = existing.get(key, [])
            new_points = new.get(key, [])

            merged[key] = (existing_points + new_points)[-30:]

        return merged


def create_enricher() -> ProductEnricher:
    """Factory function to create ProductEnricher."""
    return ProductEnricher()


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)

    raw = KeepaUpdateMessage(
        asin="B09V3KXJPB",
        marketplace="DE",
        domain_id=1,
        title="Logitech MX Keys Mini Tastatur QWERTZ DE",
        brand="Logitech",
        current_price=149.99,
        current_prices={"DE": 149.99, "IT": 89.99},
        avg_price=139.99,
        image="https://example.com/image.jpg",
        url="https://amazon.de/dp/B09V3KXJPB",
        category_tree="Computer & Zubehör > Tastaturen",
    )

    enricher = create_enricher()
    enriched = enricher.enrich(raw)

    print("Enriched Product:")
    print(json.dumps(enriched.to_dict(), indent=2, default=str))
