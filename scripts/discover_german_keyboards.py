#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import requests
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

DOMAIN_IDS = {
    'DE': 1,
    'UK': 2,
    'FR': 4,
    'IT': 8,
    'ES': 9
}

SEARCH_TERMS = {
    'DE': ['Tastatur QWERTZ', 'Deutsche Tastatur'],
    'FR': ['Clavier QWERTZ', 'Clavier Allemand'],
    'IT': ['Tastiera QWERTZ', 'Tastiera Tedesco'],
    'ES': ['Teclado QWERTZ', 'Teclado Alemán'],
    'UK': ['Keyboard QWERTZ', 'German Layout Keyboard']
}

WHD_SELLER_IDS = [
    'A2NODRKZP88ZB9',
    'A1JVRDC4365J6'
]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KeepaDiscoveryClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.keepa.com/product'
        self.tokens_remaining = None
        self.tokens_refill_ms = None
        self.request_count = 0

    def search_products(self, domain_id: int, search_term: str, max_results: int = 100) -> List[Dict]:
        params = {
            'key': self.api_key,
            'domain': domain_id,
            'search': search_term,
            'maxResults': min(max_results, 100)
        }

        for attempt in range(3):
            try:
                logger.info(f"Searching Keepa API: domain={domain_id}, term='{search_term}'")
                response = requests.get(self.base_url, params=params, timeout=30)
                self._update_token_status(response.headers)

                if response.status_code == 200:
                    data = response.json()
                    self.request_count += 1
                    if 'asinList' in data and data['asinList']:
                        asins = data['asinList']
                        logger.info(f"Found {len(asins)} ASINs for search term '{search_term}'")
                        return [{'asin': asin} for asin in asins]
                    return []
                elif response.status_code == 429:
                    logger.warning(f"Rate limited. Waiting {self.tokens_refill_ms}ms")
                    time.sleep(self.tokens_refill_ms / 1000)
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
        return []

    def get_product_offers(self, asins: List[str], domain_id: int) -> List[Dict]:
        asin_string = ','.join(asins[:20])
        params = {
            'key': self.api_key,
            'domain': domain_id,
            'asin': asin_string,
            'offers': 20
        }

        for attempt in range(3):
            try:
                response = requests.get(self.base_url, params=params, timeout=30)
                self._update_token_status(response.headers)

                if response.status_code == 200:
                    data = response.json()
                    self.request_count += 1
                    return data.get('products', [])
                elif response.status_code == 429:
                    logger.warning(f"Rate limited. Waiting {self.tokens_refill_ms}ms")
                    time.sleep(self.tokens_refill_ms / 1000)
            except Exception as e:
                logger.error(f"Failed to fetch offers (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
        return []

    def check_warehouse_deals(self, products: List[Dict]) -> List[Dict]:
        warehouse_deals = []

        for product in products:
            asin = product.get('asin')
            offers = product.get('offers', [])

            for offer in offers:
                seller_id = offer.get('sellerId', '')
                condition = offer.get('condition', 0)

                if (seller_id in WHD_SELLER_IDS or seller_id.startswith('A2NODRKZP88ZB9')) and condition > 1:
                    warehouse_deals.append({
                        'asin': asin,
                        'title': product.get('title', 'Unknown'),
                        'price': offer.get('price', {}).get('current', 0),
                        'condition': condition,
                        'seller_id': seller_id,
                        'is_warehouse_deal': True
                    })
                    break

        return warehouse_deals

    def _update_token_status(self, headers: dict):
        if 'x-keepa-tokens-left' in headers:
            self.tokens_remaining = int(headers['x-keepa-tokens-left'])
        if 'x-keepa-tokens-refill-in' in headers:
            self.tokens_refill_ms = int(headers['x-keepa-tokens-refill-in'])
        logger.info(f"Tokens remaining: {self.tokens_remaining}, Refill in: {self.tokens_refill_ms}ms")

    def wait_for_tokens(self):
        if self.tokens_remaining is not None and self.tokens_remaining < 5:
            wait_time = (self.tokens_refill_ms / 1000) if self.tokens_refill_ms else 60
            logger.info(f"Low tokens. Waiting {wait_time:.1f} seconds for refill")
            time.sleep(wait_time)


def save_results(results: List[Dict], marketplace: str, output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    asins_file = output_path / f'asins_{marketplace}_{timestamp}.txt'
    json_file = output_path / f'discovery_{marketplace}_{timestamp}.json'

    with open(asins_file, 'w') as f:
        for result in results:
            f.write(f"{result['asin']}\n")

    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"Saved {len(results)} ASINs to {asins_file}")
    logger.info(f"Saved metadata to {json_file}")


def main():
    parser = argparse.ArgumentParser(description='Discover German keyboard ASINs via Keepa API')
    parser.add_argument('--marketplace', type=str, default='all', help='Marketplace code (DE, UK, FR, IT, ES, or all)')
    parser.add_argument('--search-term', type=str, help='Override search term')
    parser.add_argument('--max-results', type=int, default=100, help='Max results per search')
    parser.add_argument('--output-dir', type=str, default='data/discovery/', help='Output directory')
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv('KEEPA_API_KEY')
    if not api_key:
        logger.error("KEEPA_API_KEY not found in environment")
        sys.exit(1)

    client = KeepaDiscoveryClient(api_key)

    marketplaces = [args.marketplace.upper()] if args.marketplace.lower() != 'all' else list(DOMAIN_IDS.keys())
    all_results = []

    for marketplace in marketplaces:
        if marketplace not in DOMAIN_IDS:
            logger.error(f"Unknown marketplace: {marketplace}")
            continue

        domain_id = DOMAIN_IDS[marketplace]
        search_terms = [args.search_term] if args.search_term else SEARCH_TERMS.get(marketplace, [])

        logger.info(f"=== Processing marketplace: {marketplace} (domain={domain_id}) ===")

        for search_term in search_terms:
            client.wait_for_tokens()
            products = client.search_products(domain_id, search_term, args.max_results)

            if products:
                asins = [p['asin'] for p in products]
                offers_data = client.get_product_offers(asins, domain_id)
                warehouse_deals = client.check_warehouse_deals(offers_data)

                for deal in warehouse_deals:
                    deal['marketplace'] = marketplace
                    deal['search_term'] = search_term

                all_results.extend(warehouse_deals)
                logger.info(f"Found {len(warehouse_deals)} warehouse deals for '{search_term}'")

    if all_results:
        save_results(all_results, args.marketplace, args.output_dir)
    else:
        logger.warning("No warehouse deals found")

    logger.info(f"Discovery complete. Total requests: {client.request_count}")


if __name__ == '__main__':
    main()
