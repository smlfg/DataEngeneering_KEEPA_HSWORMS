"""
Seed script to populate Elasticsearch with sample price data.
This fixes the empty current_prices issue in the dashboard.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.consumer.indexer import ElasticsearchIndexer, create_indexer
import random

SAMPLE_PRICES = {
    "DE": (25.99, 299.99),
    "IT": (22.99, 279.99),
    "ES": (24.99, 289.99),
    "UK": (21.99, 259.99),
    "FR": (23.99, 285.99),
}


def generate_prices():
    """Generate realistic prices for arbitrage."""
    prices = {}
    de_price = round(random.uniform(*SAMPLE_PRICES["DE"]), 2)
    prices["DE"] = de_price

    for mp in ["IT", "ES", "UK", "FR"]:
        if mp == "DE":
            continue
        low, high = SAMPLE_PRICES[mp]
        source_price = round(random.uniform(low, high), 2)
        if source_price < de_price:
            prices[mp] = source_price
        else:
            prices[mp] = round(source_price * 0.85, 2)

    return prices


def seed_prices(indexer: ElasticsearchIndexer, sample_count: int = 50):
    """Add sample prices to existing products."""
    print(f"Fetching existing products from index '{indexer.index}'...")

    result = indexer.search(query={"match_all": {}}, size=500)
    products = result.get("hits", [])
    print(f"Found {len(products)} products")

    updated = 0
    for product in products:
        asin = product.get("asin")
        if not asin:
            continue

        existing_prices = product.get("current_prices", {})

        if not existing_prices or len(existing_prices) < 2:
            new_prices = generate_prices()
            merged_prices = {**existing_prices, **new_prices}

            success = indexer.upsert_product(
                {
                    **product,
                    "current_prices": merged_prices,
                }
            )

            if success:
                updated += 1
                print(f"  Updated {asin}: DE={merged_prices.get('DE')} EUR")
            else:
                print(f"  Failed {asin}")

        if updated >= sample_count:
            break

    print(f"\nUpdated {updated} products with sample prices")
    return updated


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    indexer = create_indexer()

    if indexer.ping():
        print("Connected to Elasticsearch")

        if indexer.create_index_if_not_exists():
            print(f"Index '{indexer.index}' ready")

            updated = seed_prices(indexer, sample_count=50)
            print(f"\nDone! Updated {updated} products")

            stats = indexer.search(query={"term": {"is_active": True}}, size=1)
            print(f"\nVerification: {stats['total']} active products in index")
    else:
        print("Failed to connect to Elasticsearch")
        sys.exit(1)
