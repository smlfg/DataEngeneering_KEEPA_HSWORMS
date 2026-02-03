"""
Keepa API Client for fetching Amazon product data.
Documentation: https://keepa.com/#/api
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import requests

logger = logging.getLogger(__name__)


KEEPA_API_BASE = "https://api.keepa.com"


# Based on Keepa API official documentation
# https://keepa.com/#/api
# Domain IDs mapping to Amazon marketplaces
KEEPA_DOMAIN_MAP = {
    1: "US",  # Amazon.com (United States)
    2: "UK",  # Amazon.co.uk (United Kingdom)
    3: "DE",  # Amazon.de (Germany)
    4: "FR",  # Amazon.fr (France)
    5: "JP",  # Amazon.co.jp (Japan)
    6: "CA",  # Amazon.ca (Canada)
    7: "CN",  # Amazon.cn (China)
    8: "IT",  # Amazon.it (Italy)
    9: "ES",  # Amazon.es (Spain)
    10: "IN",  # Amazon.in (India)
    11: "MX",  # Amazon.com.mx (Mexico)
    12: "BR",  # Amazon.com.br (Brazil)
    13: "AU",  # Amazon.com.au (Australia)
}


MARKETPLACE_DOMAIN_MAP = {v: k for k, v in KEEPA_DOMAIN_MAP.items()}


@dataclass
class KeepaProduct:
    """Represents a product from Keepa API."""

    asin: str
    domain_id: int
    title: Optional[str] = None
    brand: Optional[str] = None
    image: Optional[str] = None
    url: Optional[str] = None
    category_id: Optional[int] = None
    category_tree: Optional[str] = None
    ean: Optional[str] = None
    mpn: Optional[str] = None
    current_prices: Dict[str, Optional[float]] = field(default_factory=dict)
    price_history: List[Dict[str, Any]] = field(default_factory=list)
    avg_price: Optional[float] = None
    buy_box_price: Optional[float] = None
    buy_box_shipping: Optional[float] = None
    last_update: Optional[int] = None

    @property
    def marketplace(self) -> str:
        return KEEPA_DOMAIN_MAP.get(self.domain_id, "UNKNOWN")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asin": self.asin,
            "domain_id": self.domain_id,
            "marketplace": self.marketplace,
            "title": self.title,
            "brand": self.brand,
            "image": self.image,
            "url": self.url,
            "category_id": self.category_id,
            "category_tree": self.category_tree,
            "ean": self.ean,
            "mpn": self.mpn,
            "current_prices": self.current_prices,
            "price_history": self.price_history,
            "avg_price": self.avg_price,
            "buy_box_price": self.buy_box_price,
            "buy_box_shipping": self.buy_box_shipping,
            "last_update": self.last_update,
        }

    @classmethod
    def from_keepa_response(cls, data: Dict[str, Any]) -> "KeepaProduct":
        """Create KeepaProduct from Keepa API response."""
        price_data = data.get("price", [])

        current_prices = {}
        for i, price_entry in enumerate(price_data):
            if isinstance(price_entry, dict) and "marketplace" in price_entry:
                mp_id = price_entry["marketplace"]
                mp_code = KEEPA_DOMAIN_MAP.get(mp_id)
                if mp_code:
                    current_prices[mp_code] = price_entry.get("price")

        price_history = []
        if "priceHistory" in data:
            for entry in data["priceHistory"]:
                if isinstance(entry, dict):
                    price_history.append(
                        {
                            "marketplace": entry.get("marketplace"),
                            "date": entry.get("date"),
                            "price": entry.get("price"),
                            "type": entry.get("type"),
                        }
                    )

        return cls(
            asin=data.get("asin", ""),
            domain_id=data.get("domain", 1),
            title=data.get("title"),
            brand=data.get("brand"),
            image=data.get("img"),
            url=data.get("url"),
            category_id=data.get("category"),
            category_tree=data.get("categoryTree"),
            ean=data.get("ean"),
            mpn=data.get("mpn"),
            current_prices=current_prices,
            price_history=price_history,
            avg_price=data.get("avg"),
            buy_box_price=data.get("buyBox"),
            buy_box_shipping=data.get("buyBoxShipping"),
            last_update=data.get("lastUpdate"),
        )


class KeepaRateLimitError(Exception):
    """Raised when Keepa API rate limit is exceeded."""

    pass


class KeepaAPIError(Exception):
    """Raised when Keepa API returns an error."""

    pass


class KeepaClient:
    """
    Client for Keepa Amazon Price Tracker API.

    Free tier: 100 requests per minute
    Documentation: https://keepa.com/#/api
    """

    def __init__(self, api_key: Optional[str] = None, requests_per_minute: int = 20):
        """
        Initialize Keepa API client.

        Args:
            api_key: Keepa API key (optional, will use KEEPA_API_KEY env var)
            requests_per_minute: Rate limit (default: 20 tokens/min for this plan)
        """
        self.api_key = api_key or os.getenv("KEEPA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Keepa API key is required. Set KEEPA_API_KEY env variable."
            )

        self.requests_per_minute = requests_per_minute
        self.request_interval = 60.0 / requests_per_minute  # 3 seconds between requests
        self._last_request_time = 0.0
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Content-Type": "application/json",
            }
        )

    def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        self._last_request_time = time.time()

    def _request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the Keepa API."""
        self._rate_limit()

        url = f"{KEEPA_API_BASE}/{endpoint}"

        # Add API key to params
        if params is None:
            params = {}
        params["key"] = self.api_key

        try:
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "error" in data:
                error_msg = data.get("error", "Unknown error")
                if "too many requests" in error_msg.lower():
                    raise KeepaRateLimitError(error_msg)
                raise KeepaAPIError(error_msg)

            return data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise KeepaRateLimitError("Rate limit exceeded")
            raise KeepaAPIError(f"HTTP Error: {e}")
        except requests.exceptions.RequestException as e:
            raise KeepaAPIError(f"Request failed: {e}")

    def product_query(
        self,
        asins: List[str],
        domain: int = 1,
        include_history: bool = False,
        update_by: str = "update",
    ) -> List[KeepaProduct]:
        """
        Query product data by ASIN(s).

        Token Cost: 1 token per ASIN
        Rate Limit: 20 requests/minute (configurable)

        Args:
            asins: List of Amazon ASINs
            domain: Keepa domain ID (1=US, 2=UK, 3=DE, 4=FR, 5=JP, 6=CA, 8=IT, 9=ES, 10=IN)
            include_history: Include price history (costs extra tokens)
            update_by: Sort by 'update' or 'asin'

        Returns:
            List of KeepaProduct objects
        """
        asin_string = ",".join(asins)

        params = {
            "asin": asin_string,
            "domain": domain,
            "stats": "30",  # Get 30-day statistics for current prices
        }

        if include_history:
            params["history"] = "1"

        data = self._request("product", params=params)

        products = []
        for item in data.get("products", []):
            try:
                product = KeepaProduct.from_keepa_response(item)
                products.append(product)
            except Exception as e:
                logger.error(f"Failed to parse product: {e}")
                continue

        return products

    def product_query_single(
        self,
        asin: str,
        domain: int = 1,
        include_history: bool = False,
    ) -> Optional[KeepaProduct]:
        """Query a single product by ASIN."""
        products = self.product_query([asin], domain, include_history)
        return products[0] if products else None

    def category_bestsellers(
        self,
        category_id: int,
        domain: int = 1,
        limit: int = 100,
    ) -> List[str]:
        """
        Get bestsellers from a category.

        Token Cost: 1 token (for range=30)
        Rate Limit: 20 requests/minute (configurable)

        Args:
            category_id: Keepa category ID
            domain: Keepa domain ID
            limit: Maximum number of ASINs to return

        Returns:
            List of ASINs (top sellers in category)
        """
        # Note: Keepa bestsellers 'range' parameter only accepts: 0, 30, 90, 180
        # Using range=30 gives bestsellers from last 30 days
        params = {
            "category": category_id,
            "domain": domain,
            "range": 30,
        }

        data = self._request("bestsellers", params=params)

        # Parse response - bestSellersList contains asinList
        bsl = data.get("bestSellersList", {})
        asin_list = bsl.get("asinList", [])

        asins = []
        for asin in asin_list[:limit]:
            if isinstance(asin, str):
                asins.append(asin)
            elif isinstance(asin, dict) and "asin" in asin:
                asins.append(asin["asin"])

        return asins

    def search_products(
        self,
        query: str,
        domain: int = 1,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search for products by keyword.

        Args:
            query: Search term
            domain: Keepa domain ID
            limit: Maximum results

        Returns:
            List of search results
        """
        params = {
            "term": query,  # Note: Keepa uses 'term', not 'search'
            "domain": domain,
            "range": limit,
        }

        data = self._request("search", params=params)

        return data.get("search", [])[:limit]

    def get_product_updates(
        self,
        asins: List[str],
        domain: int = 1,
    ) -> List[KeepaProduct]:
        """
        Get latest updates for specific products.

        This is optimized for checking price changes.
        """
        return self.product_query(
            asins, domain, include_history=False, update_by="update"
        )

    def fetch_deals(
        self,
        domain: int = 1,
        date_range: int = 24,
        page: int = 0,
        limit: int = 150,
    ) -> List[Dict[str, Any]]:
        """
        Fetch deals - products with recent price changes.

        Token Cost: 5 tokens per request (up to 150 deals)
        Documentation: https://keepa.com/#/api

        Args:
            domain: Keepa domain ID
            date_range: Only include products updated within X hours (1-168)
            page: Page number for pagination
            limit: Maximum results (max 150 per request)

        Returns:
            List of deal items with product info
        """
        params = {
            "domain": domain,
            "date_range": date_range,
            "page": page,
            "range": limit,
        }

        data = self._request("deals", params=params)

        deals = data.get("deals", [])
        logger.info(f"Fetched {len(deals)} deals from domain {domain}")

        return deals

    def get_category(
        self,
        domain: int = 1,
        category_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get category information.

        Token Cost: 5 tokens per request

        Args:
            domain: Keepa domain ID
            category_id: Specific category ID (None for all categories)

        Returns:
            List of category information
        """
        params = {"domain": domain}
        if category_id:
            params["category"] = category_id

        data = self._request("category", params=params)

        categories = data.get("categories", [])
        return categories


def create_keepa_client(api_key: Optional[str] = None) -> KeepaClient:
    """Factory function to create KeepaClient with env fallback."""
    key = api_key or os.getenv("KEEPA_API_KEY")
    return KeepaClient(api_key=key)


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)

    client = create_keepa_client()

    print("Testing Keepa API connection...")
    print(f"API Key configured: {'Yes' if client.api_key else 'No'}")

    test_asins = ["B09V3KXJPB", "B07Y19G9H2"]

    try:
        products = client.product_query(test_asins, domain=1, include_history=True)
        print(f"\nFetched {len(products)} products:")

        for product in products:
            print(
                f"\n{product.asin}: {product.title[:50] if product.title else 'N/A'}..."
            )
            print(f"  Marketplace: {product.marketplace}")
            print(f"  Current Prices: {product.current_prices}")
            if product.avg_price:
                print(
                    f"  Avg Price: €{product.avg_price / 100:.2f}"
                    if product.avg_price
                    else "N/A"
                )

    except KeepaAPIError as e:
        print(f"API Error: {e}")
    except KeepaRateLimitError as e:
        print(f"Rate Limited: {e}")
