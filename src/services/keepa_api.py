"""
Keepa API Client for Keeper System
Uses official keepa library (keepa==1.5.x)
With async Token Bucket management for rate limiting
"""

import asyncio
import time
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from keepa import Keepa
from config import get_settings

logger = logging.getLogger(__name__)


class KeepaAPIError(Exception):
    """Base exception for Keepa API errors"""

    pass


class InvalidAsin(KeepaAPIError):
    """Raised when ASIN is invalid"""

    pass


class NoDealAccessError(KeepaAPIError):
    """Raised when user doesn't have deal API access"""

    pass


class TokenLimitError(KeepaAPIError):
    """Raised when rate limit is exceeded"""

    pass


class TokenInsufficientError(TokenLimitError):
    """Raised when not enough tokens available"""

    pass


@dataclass
class DealFilters:
    """Filters for deal search"""

    page: int = 0
    domain_id: int = 3  # 3 = Germany (DE)
    include_categories: Optional[List[int]] = None
    exclude_categories: Optional[List[int]] = None
    price_types: Optional[List[str]] = None
    min_rating: int = 4
    min_reviews: int = 10
    exclude_warehouses: bool = True
    sort: str = "SCORE"


@dataclass
class TokenStatus:
    """Token bucket status"""

    tokens_available: int = 20
    tokens_per_minute: int = 20
    last_refill: float = field(default_factory=time.time)
    refill_interval: int = 60  # seconds

    def tokens_needed(self, cost: int) -> bool:
        return self.tokens_available >= cost

    def time_until_refill(self) -> float:
        elapsed = time.time() - self.last_refill
        remaining = self.refill_interval - elapsed
        return max(0, remaining)


class AsyncTokenBucket:
    """
    Async Token Bucket for rate limiting Keepa API calls.

    Implements a token bucket algorithm where:
    - Tokens refill at a constant rate (20 per 60 seconds by default)
    - Each API call consumes a specific number of tokens
    - If not enough tokens, automatically waits for refill
    """

    def __init__(
        self,
        tokens_per_minute: int = 20,
        refill_interval: int = 60,
        executor: Optional[ThreadPoolExecutor] = None,
    ):
        self.tokens_per_minute = tokens_per_minute
        self.refill_interval = refill_interval
        self.tokens_available = tokens_per_minute
        self.last_refill = time.time()
        self.executor = executor or ThreadPoolExecutor(max_workers=4)

    def refill(self) -> int:
        """
        Refill tokens based on time elapsed.

        Returns:
            Number of tokens refilled
        """
        now = time.time()
        elapsed = now - self.last_refill

        if elapsed >= self.refill_interval:
            # Full refill
            tokens_added = self.tokens_per_minute - self.tokens_available
            self.tokens_available = self.tokens_per_minute
            self.last_refill = now
            if tokens_added > 0:
                logger.info(f"🔄 Token bucket refilled: +{tokens_added} tokens")
            return tokens_added

        return 0

    def consume(self, cost: int) -> bool:
        """
        Try to consume tokens from the bucket.

        Args:
            cost: Number of tokens to consume

        Returns:
            True if successful, False if insufficient tokens
        """
        self.refill()

        if self.tokens_available >= cost:
            self.tokens_available -= cost
            logger.info(
                f"📊 Token consumed: -{cost}, Remaining: {self.tokens_available}"
            )
            return True

        return False

    async def wait_for_tokens(
        self, cost: int, max_wait: float = 120.0, check_interval: float = 5.0
    ) -> bool:
        """
        Wait until enough tokens are available.

        Args:
            cost: Number of tokens needed
            max_wait: Maximum time to wait in seconds
            check_interval: How often to check token status

        Returns:
            True if tokens obtained, False if timeout
        """
        start_time = time.time()

        while True:
            self.refill()

            if self.tokens_available >= cost:
                self.tokens_available -= cost
                wait_time = time.time() - start_time
                if wait_time > 1:
                    logger.info(f"⏳ Waited {wait_time:.1f}s for tokens")
                logger.info(
                    f"📊 Token consumed: -{cost}, Remaining: {self.tokens_available}"
                )
                return True

            elapsed = time.time() - start_time
            if elapsed >= max_wait:
                logger.warning(f"⏰ Timeout waiting for tokens after {max_wait}s")
                raise TokenInsufficientError(
                    f"Timeout after {max_wait}s waiting for {cost} tokens. "
                    f"Currently have {self.tokens_available} tokens."
                )

            time_until_refill = self.refill_interval - (time.time() - self.last_refill)
            wait_for = min(check_interval, time_until_refill)

            logger.info(f"⏳ Waiting {wait_for:.1f}s for token refill...")
            await asyncio.sleep(wait_for)

    def get_status(self) -> TokenStatus:
        """Get current token bucket status"""
        self.refill()
        return TokenStatus(
            tokens_available=self.tokens_available,
            tokens_per_minute=self.tokens_per_minute,
            last_refill=self.last_refill,
            refill_interval=self.refill_interval,
        )


class KeepaAPIClient:
    """
    Keepa API Client for Amazon price monitoring and deal finding.

    Features:
    - Async token bucket for rate limiting
    - Automatic token refill from Keepa API status
    - Thread-safe operations
    - Proper error handling

    Domain IDs: 1=US, 2=UK, 3=DE, 4=FR, 5=ES, 6=IT, 7=IN, 8=CA, 9=JP, 10=AU, 11=BR, 12=MX
    """

    DOMAIN_MAP = {
        1: "US",
        2: "UK",
        3: "DE",
        4: "FR",
        5: "ES",
        6: "IT",
        7: "IN",
        8: "CA",
        9: "JP",
        10: "AU",
        11: "BR",
        12: "MX",
    }

    # Token costs for different API calls (approximate)
    TOKEN_COSTS = {
        "query": 15,  # Product query
        "deals": 5,  # Deal search
        "category": 5,  # Category lookup
        "best_sellers": 3,  # Best sellers
        "seller": 5,  # Seller query
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Keepa API client with async token management.

        Args:
            api_key: Keepa API key (defaults to settings.KEEPA_API_KEY)
        """
        settings = get_settings()
        self._api_key = api_key or settings.keepa_api_key

        # Initialize Keepa API
        try:
            self._api = Keepa(self._api_key)
            self._is_initialized = True
            logger.info("✅ Keepa API initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Keepa API: {e}")
            self._api = None
            self._is_initialized = False

        # Initialize token bucket with default values
        # Will be updated from actual API status
        self._token_bucket = AsyncTokenBucket(tokens_per_minute=20, refill_interval=60)

        # Thread pool for sync Keepa calls
        self._executor = ThreadPoolExecutor(max_workers=4)

    def _ensure_initialized(self):
        """Ensure API is initialized before use"""
        if not self._is_initialized or self._api is None:
            raise KeepaAPIError("Keepa API not initialized. Check API key.")

    async def _sync_call(self, func, *args, **kwargs):
        """Run a synchronous Keepa API call in executor"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, lambda: func(*args, **kwargs))

    async def update_token_status(self):
        """Update token bucket from Keepa API status"""
        try:
            status = await self._sync_call(self._api.status)
            if status:
                tokens_per_min = getattr(status, "tokensPerMin", 20) or 20
                refill_in = getattr(status, "refillIn", 60) or 60

                self._token_bucket.tokens_per_minute = tokens_per_min
                self._token_bucket.refill_interval = refill_in

                # Also update available tokens if available
                tokens_left = self._api.tokens_left
                if tokens_left is not None:
                    self._token_bucket.tokens_available = tokens_left

                logger.debug(
                    f"🔄 Token status updated: {tokens_left}/{tokens_per_min} tokens"
                )
        except Exception as e:
            logger.warning(f"⚠️ Could not update token status: {e}")

    async def query_product(self, asin: str) -> Dict[str, Any]:
        """
        Query single product by ASIN with token management.

        Args:
            asin: Amazon product ASIN (10 characters)

        Returns:
            dict with product data:
            {
                'asin': str,
                'title': str,
                'current_price': float,
                'list_price': float,
                'category': str,
                'rating': float,
                'offers_count': int,
                'buy_box_price': float,
                'price_history_count': int,
                'timestamp': int
            }

        Raises:
            InvalidAsin: If ASIN is not 10 characters
            KeepaAPIError: If API returns an error
            TokenLimitError: If rate limit exceeded
        """
        self._ensure_initialized()

        if len(asin) != 10:
            raise InvalidAsin(f"Invalid ASIN: {asin}. Must be 10 characters.")

        # Wait for tokens
        cost = self.TOKEN_COSTS["query"]
        await self._token_bucket.wait_for_tokens(cost)

        try:
            # Make API call
            products = await self._sync_call(
                lambda: self._api.query(asin, domain=self.DOMAIN_MAP[3])
            )

            if not products:
                raise KeepaAPIError(f"No product found for ASIN: {asin}")

            product = products[0]

            # Extract prices (Keepa stores in cents)
            current_price = 0
            current_data = product.get("current")
            if (
                current_data
                and isinstance(current_data, (list, tuple))
                and len(current_data) >= 2
            ):
                current_price = current_data[1] / 100.0

            list_price = 0
            list_data = product.get("listPrice")
            if (
                list_data
                and isinstance(list_data, (list, tuple))
                and len(list_data) >= 2
            ):
                list_price = list_data[1] / 100.0

            buy_box = 0
            buybox_data = product.get("buyBoxPrice")
            if (
                buybox_data
                and isinstance(buybox_data, (list, tuple))
                and len(buybox_data) >= 2
            ):
                buy_box = buybox_data[1] / 100.0

            rating = product.get("rating", 0) or 0
            offers = product.get("offers", 0) or 0

            # Count price history points
            csv_data = product.get("csv", [])
            history_count = (
                len([c for c in csv_data if c is not None]) if csv_data else 0
            )

            # Get category
            category = ""
            if product.get("categories") and product["categories"]:
                category = str(product["categories"][-1])

            return {
                "asin": asin,
                "title": product.get("title", "Unknown"),
                "current_price": current_price,
                "list_price": list_price,
                "category": category,
                "rating": float(rating),
                "offers_count": int(offers),
                "buy_box_price": buy_box,
                "price_history_count": history_count,
                "timestamp": int(datetime.utcnow().timestamp()),
            }

        except KeepaAPIError:
            raise
        except Exception as e:
            raise KeepaAPIError(f"Error querying product {asin}: {str(e)}")

    async def search_deals(self, filters: DealFilters) -> Dict[str, Any]:
        """
        Search for deals using Keepa deals() with token management.

        Args:
            filters: DealFilters object with search parameters

        Returns:
            dict with deals data:
            {
                'deals': [...],
                'total': int,
                'page': int,
                'category_names': list[str]
            }

        Raises:
            NoDealAccessError: If deal API not available for account
            TokenLimitError: If rate limit exceeded
        """
        self._ensure_initialized()

        # Wait for tokens
        cost = self.TOKEN_COSTS["deals"]
        await self._token_bucket.wait_for_tokens(cost)

        try:
            # Build deal search parameters
            deal_params = {}

            if filters.min_rating > 0:
                deal_params["minRating"] = int(filters.min_rating * 20)

            if filters.min_reviews > 0:
                deal_params["reviews"] = filters.min_reviews

            if filters.page > 0:
                deal_params["page"] = filters.page

            if filters.include_categories:
                deal_params["includeCategories"] = filters.include_categories

            if filters.exclude_categories:
                deal_params["excludeCategories"] = filters.exclude_categories

            if filters.price_types:
                deal_params["priceTypes"] = filters.price_types

            # Call deals API
            result = await self._sync_call(
                lambda: self._api.deals(
                    deal_params, domain=self.DOMAIN_MAP.get(filters.domain_id, "DE")
                )
            )

            # Parse deals
            deals = []
            if result and "deals" in result:
                for deal in result["deals"]:
                    deals.append(
                        {
                            "asin": deal.get("asin", ""),
                            "title": deal.get("title", "Unknown"),
                            "current_price": deal.get("price", 0) / 100.0,
                            "list_price": deal.get("listPrice", deal.get("price", 0))
                            / 100.0,
                            "discount_percent": deal.get("savingsPercent", 0),
                            "rating": (deal.get("rating", 0) / 20.0)
                            if deal.get("rating")
                            else 0,
                            "prime_eligible": deal.get("isPrime", False),
                            "reviews": deal.get("reviews", 0),
                            "url": f"https://amazon.{self.DOMAIN_MAP.get(filters.domain_id, 'de')}/dp/{deal.get('asin', '')}",
                        }
                    )

            return {
                "deals": deals,
                "total": result.get("totalDeals", len(deals)),
                "page": filters.page,
                "category_names": result.get("categoryNames", []),
            }

        except Exception as e:
            error_msg = str(e).upper()
            tokens_left = self._api.tokens_left if self._api else 0

            if "REQUEST_REJECTED" in error_msg or tokens_left == 0:
                raise TokenLimitError(
                    "No tokens available. Please wait for token refill."
                )
            if "404" in error_msg or "NOT FOUND" in error_msg:
                raise NoDealAccessError("Deal API not available for this account.")
            if "RATE" in error_msg:
                raise TokenLimitError(
                    "Rate limit exceeded. Please wait before trying again."
                )
            raise KeepaAPIError(f"Error searching deals: {str(e)}")

    async def get_price_history(
        self, asin: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get price history for product over last N days."""
        self._ensure_initialized()

        # Wait for tokens
        cost = self.TOKEN_COSTS["query"]
        await self._token_bucket.wait_for_tokens(cost)

        try:
            products = await self._sync_call(
                lambda: self._api.query(asin, domain=self.DOMAIN_MAP[3])
            )

            if not products:
                return []

            product = products[0]
            history = []
            csv_data = product.get("csv", [])

            if csv_data and len(csv_data) > 1:
                timestamps = csv_data[0]
                new_prices = csv_data[3] if len(csv_data) > 3 else []
                cutoff = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)

                for i, ts in enumerate(timestamps):
                    if ts >= cutoff:
                        price = new_prices[i] / 100.0 if i < len(new_prices) else 0
                        if price > 0:
                            history.append(
                                {
                                    "timestamp": int(ts),
                                    "price": price,
                                    "currency": "EUR",
                                }
                            )

            return sorted(history, key=lambda x: x["timestamp"])

        except Exception as e:
            logger.error(f"Error getting price history for {asin}: {e}")
            return []

    def get_token_status(self) -> Dict[str, Any]:
        """Get current token bucket status."""
        status = self._token_bucket.get_status()
        return {
            "tokens_available": status.tokens_available,
            "tokens_per_minute": status.tokens_per_minute,
            "last_refill": datetime.fromtimestamp(status.last_refill).isoformat(),
            "refill_interval": status.refill_interval,
            "time_until_refill": status.time_until_refill(),
        }

    def check_rate_limit(self) -> Dict[str, Any]:
        """Check current rate limit status from Keepa API."""
        self._ensure_initialized()

        try:
            tokens_left = self._api.tokens_left
            refill_time = getattr(self._api, "time_to_refill", 0)

            if callable(refill_time):
                try:
                    refill_time = refill_time()
                except:
                    refill_time = 0

            return {
                "tokens_available": tokens_left,
                "tokens_per_minute": 20,
                "refill_in_seconds": refill_time,
                "refill_in_minutes": refill_time // 60 if refill_time else 0,
            }
        except Exception as e:
            return {
                "tokens_available": 0,
                "tokens_per_minute": 20,
                "error": str(e),
            }


# Singleton instances
_keepa_client: Optional[KeepaAPIClient] = None
_legacy_client: Optional["_LegacyKeepaClient"] = None


def get_keepa_client() -> KeepaAPIClient:
    """Get or create the Keepa API client singleton"""
    global _keepa_client
    if _keepa_client is None:
        _keepa_client = KeepaAPIClient()
    return _keepa_client


class _LegacyKeepaClient:
    """Legacy wrapper for backward compatibility with async support"""

    def __init__(self):
        self._client = KeepaAPIClient()
        self._executor = ThreadPoolExecutor(max_workers=2)

    async def query_product(self, asin: str) -> Optional[Dict[str, Any]]:
        """Query product by ASIN"""
        try:
            return await self._client.query_product(asin)
        except Exception as e:
            logger.error(f"Error querying product: {e}")
            return None

    async def query_deals(self, **kwargs) -> List[Dict[str, Any]]:
        """Query deals"""
        try:
            filters = DealFilters(
                page=kwargs.get("page", 0),
                domain_id=kwargs.get("domain_id", 3),
                min_rating=int(kwargs.get("min_rating", 4)),
                min_reviews=kwargs.get("min_reviews", 10),
            )
            result = await self._client.search_deals(filters)
            return result.get("deals", [])
        except Exception as e:
            logger.error(f"Error querying deals: {e}")
            return []

    def get_rate_limit_status(self) -> Dict[str, int]:
        """Get rate limit status"""
        try:
            status = self._client.get_token_status()
            return {"remaining": status.get("tokens_available", 0)}
        except Exception:
            return {"remaining": 0}


def get_keepa_client_legacy() -> _LegacyKeepaClient:
    """Get or create the legacy Keepa client singleton"""
    global _legacy_client
    if _legacy_client is None:
        _legacy_client = _LegacyKeepaClient()
    return _legacy_client


# Export the legacy keepa_client for compatibility
keepa_client = get_keepa_client_legacy()
