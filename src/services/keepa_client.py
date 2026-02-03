"""
Keepa API Client
Handles all interactions with Keepa API
"""

import hashlib
import time
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config import get_keepa_api_key


KEEPA_API_BASE = "https://api.keepa.com"


class KeepaApiError(Exception):
    """Base exception for Keepa API errors"""

    pass


class KeepaRateLimitError(KeepaApiError):
    """Rate limit exceeded"""

    pass


class KeepaAuthError(KeepaApiError):
    """Authentication failed"""

    pass


class KeepaTimeoutError(KeepaApiError):
    """Request timed out"""

    pass


class KeepaClient:
    """
    Client for Keepa API
    Handles authentication, rate limiting, and response parsing
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_keepa_api_key()
        self.api_key_hash = self._hash_api_key(self.api_key)
        self.rate_limit_remaining: int = 100
        self.rate_limit_reset: Optional[int] = None

    def _hash_api_key(self, key: str) -> str:
        """Hash API key for logging (security)"""
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    async def _make_request(
        self, endpoint: str, params: dict, timeout: float = 30.0
    ) -> dict:
        """
        Make API request with retry logic
        Uses query parameter authentication (key=...)
        """
        url = f"{KEEPA_API_BASE}/{endpoint}"

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, params=params)

            # Update rate limit info from response headers
            self.rate_limit_remaining = int(
                response.headers.get("X-RateLimit-Remaining", 100)
            )
            self.rate_limit_reset = int(response.headers.get("X-RateLimit-Reset", 0))

            if response.status_code == 200:
                return response.json()

            elif response.status_code == 401:
                raise KeepaAuthError("Invalid Keepa API key")

            elif response.status_code == 429:
                raise KeepaRateLimitError("Keepa API rate limit exceeded")

            elif response.status_code == 504:
                raise KeepaTimeoutError("Keepa API timeout")

            else:
                error_msg = response.text[:200] if response.text else "Unknown error"
                raise KeepaApiError(
                    f"Keepa API error {response.status_code}: {error_msg}"
                )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=30, max=120),
        retry=retry_if_exception_type((KeepaRateLimitError, KeepaTimeoutError)),
    )
    async def search_products(
        self,
        search_term: str,
        domain_id: int = 3,
        category: Optional[int] = None,
        page: int = 1,
    ) -> dict:
        """
        Search for products using Keepa API

        Args:
            search_term: Keyword or phrase to search
            domain_id: Amazon domain (1=com, 3=de, 4=co.uk)
            category: Category ID to filter by
            page: Page number (1-based)

        Returns:
            Parsed search response with products
        """
        params = {
            "key": self.api_key,
            "domain": domain_id,
            "search": search_term,
            "page": page,
        }

        if category:
            params["category"] = category

        start_time = time.time()

        try:
            response = await self._make_request("search", params)

            execution_time = int((time.time() - start_time) * 1000)

            return {
                "raw": response,
                "metadata": {
                    "request_id": str(uuid4()),
                    "timestamp": datetime.utcnow().isoformat(),
                    "execution_time_ms": execution_time,
                    "tokens_consumed": response.get("tokensConsumed", 0),
                    "products_found": len(response.get("products", [])),
                    "search_term": search_term,
                },
            }

        except (KeepaRateLimitError, KeepaTimeoutError) as e:
            raise

        except KeepaApiError as e:
            raise KeepaApiError(f"Search failed: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=30, max=120),
        retry=retry_if_exception_type((KeepaRateLimitError, KeepaTimeoutError)),
    )
    async def get_products(
        self,
        asins: list[str],
        domain_id: int = 3,  # Amazon.de
    ) -> dict:
        """
        Get product details from Keepa API

        Args:
            asins: List of ASINs to fetch
            domain_id: Amazon domain (1=com, 3=de, 4=co.uk)

        Returns:
            Parsed product response
        """
        params = {"key": self.api_key, "domain": domain_id, "asin": ",".join(asins)}

        start_time = time.time()

        try:
            response = await self._make_request("product", params)

            execution_time = int((time.time() - start_time) * 1000)

            return {
                "raw": response,
                "metadata": {
                    "request_id": str(uuid4()),
                    "timestamp": datetime.utcnow().isoformat(),
                    "execution_time_ms": execution_time,
                    "tokens_consumed": response.get("tokensConsumed", 0),
                    "products_found": len(response.get("products", [])),
                },
            }

        except (KeepaRateLimitError, KeepaTimeoutError) as e:
            raise

        except KeepaApiError as e:
            raise KeepaApiError(f"Product fetch failed: {str(e)}")

    def parse_products(self, raw_response: dict) -> list[dict]:
        """
        Parse raw Keepa product response into structured format

        Args:
            raw_response: Raw API response

        Returns:
            List of parsed product dictionaries
        """
        products = []
        raw_products = raw_response.get("products", [])

        for product in raw_products:
            parsed = {
                "asin": product.get("asin"),
                "title": product.get("title")
                or f"Product {product.get('asin', 'Unknown')}",
                "category": self._extract_category(product),
                "current_price": self._parse_price_from_csv(
                    product.get("csv"), price_type="current"
                ),
                "original_price": self._parse_price_from_csv(
                    product.get("csv"), price_type="avg"
                ),
                "discount_percent": self._calculate_discount(product),
                "rating": self._parse_rating(product),
                "review_count": self._get_review_count(product),
                "sales_rank": self._extract_sales_rank(product),
                "amazon_url": self._build_amazon_url(
                    product.get("asin"), domain_id=raw_response.get("domain", 3)
                ),
                "image_url": self._extract_image(product),
                "is_amazon_seller": self._check_amazon_seller(product),
                "last_updated": datetime.utcnow().isoformat(),
                "raw_data": product,  # Keep raw data for reference
            }
            products.append(parsed)

        return products

    def _extract_category(self, product: dict) -> Optional[str]:
        """Extract category from product"""
        category_tree = product.get("categoryTree", [])
        if category_tree:
            last_cat = category_tree[-1]
            if isinstance(last_cat, dict):
                return last_cat.get("name")
            return str(last_cat)
        return product.get("productGroup") or product.get("binding")

    def _parse_price_from_csv(
        self, csv_data, price_type: str = "current"
    ) -> Optional[Decimal]:
        """
        Parse price from Keepa CSV data

        CSV format: [amazon_prices, new_prices, used_prices, ...]
        Each price array contains [price, timestamp, price, timestamp, ...] pairs

        Args:
            csv_data: The CSV array from Keepa response
            price_type: "current", "avg", or "new"

        Returns:
            Price as Decimal or None
        """
        if not csv_data or not isinstance(csv_data, list):
            return None

        # Index mapping for price types
        price_indices = {
            "current": 0,  # Amazon price
            "new": 1,  # New price
            "used": 2,  # Used price
        }

        idx = price_indices.get(price_type, 0)
        if idx >= len(csv_data):
            return None

        price_array = csv_data[idx]
        if not price_array or not isinstance(price_array, list):
            return None

        # Find latest non-null price (iterate backwards through pairs)
        # Format: [price1, timestamp1, price2, timestamp2, ...]
        for i in range(len(price_array) - 2, -1, -2):
            price_val = price_array[i]
            if price_val is not None and price_val > 0:
                return Decimal(price_val) / 100  # Convert from cents

        return None

    def _calculate_discount(self, product: dict) -> Optional[int]:
        """Calculate discount percentage from CSV data"""
        csv_data = product.get("csv")
        if not csv_data or not isinstance(csv_data, list) or len(csv_data) < 2:
            return None

        # Get current Amazon price and average new price
        current = self._parse_price_from_csv(csv_data, "current")
        new_price = self._parse_price_from_csv(csv_data, "new")

        if current and new_price and float(new_price) > 0:
            discount = int((1 - float(current) / float(new_price)) * 100)
            return max(0, discount)

        return None

    def _parse_rating(self, product: dict) -> Optional[Decimal]:
        """Parse rating from product"""
        rating = product.get("rating")
        if rating and rating > 0:
            return Decimal(rating) / 20  # Keepa stores rating * 20
        return None

    def _get_review_count(self, product: dict) -> Optional[int]:
        """Get review count from product"""
        # Keepa stores review count in a specific format
        reviews = product.get("reviews")
        if isinstance(reviews, dict):
            return reviews.get("count") or reviews.get("ratedCount")
        elif isinstance(reviews, int) and reviews > 0:
            return reviews
        return None

    def _extract_sales_rank(self, product: dict) -> Optional[int]:
        """Extract sales rank from product"""
        # Sales rank might be in different fields
        sales_rank = product.get("salesRankReference")
        if sales_rank and sales_rank > 0:
            return sales_rank

        sales_ranks = product.get("salesRanks")
        if sales_ranks and isinstance(sales_ranks, list) and len(sales_ranks) > 0:
            # Format: [rank, categoryId, timestamp]
            if isinstance(sales_ranks[0], list) and len(sales_ranks[0]) > 0:
                return sales_ranks[0][0]
            elif isinstance(sales_ranks[0], int):
                return sales_ranks[0]

        return None

    def _extract_image(self, product: dict) -> Optional[str]:
        """Extract image URL from product"""
        images_csv = product.get("imagesCSV")
        if images_csv:
            first_image = images_csv.split(",")[0]
            if first_image:
                return f"https://images-eu.ssl-images-amazon.com/images/I/{first_image}"
        return None

    def _check_amazon_seller(self, product: dict) -> bool:
        """Check if Amazon is the seller (buyBox)"""
        buy_box = product.get("buyBoxSellerIdHistory", [])
        if buy_box and len(buy_box) > 0:
            # Amazon's seller ID is ATVPDKIKX0DER
            return buy_box[-1] == "ATVPDKIKX0DER"
        return False

    def _build_amazon_url(self, asin: str, domain_id: int = 3) -> str:
        """Build Amazon product URL"""
        if not asin:
            return ""

        domain_map = {
            1: "amazon.com",
            3: "amazon.de",
            4: "amazon.co.uk",
            5: "amazon.fr",
        }
        domain = domain_map.get(domain_id, "amazon.de")
        return f"https://www.{domain}/dp/{asin}"


# Singleton instance
_keepa_client: Optional[KeepaClient] = None


def get_keepa_client() -> KeepaClient:
    """Get or create Keepa client singleton"""
    global _keepa_client
    if _keepa_client is None:
        _keepa_client = KeepaClient()
    return _keepa_client


async def close_keepa_client():
    """Cleanup Keepa client"""
    global _keepa_client
    _keepa_client = None
