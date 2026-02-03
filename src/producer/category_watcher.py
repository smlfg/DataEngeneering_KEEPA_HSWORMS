"""
Category Watcher - Fetches ASINs from Keepa Category Bestsellers

Features:
- Redis-based caching for ASINs (6 hour TTL)
- Token usage tracking
- Automatic cache refresh when TTL expires
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from producer.keepa_client import KeepaClient, create_keepa_client

logger = logging.getLogger(__name__)


@dataclass
class CategoryConfig:
    """Configuration for a single category."""

    keepa_id: int
    name: str
    limit: int = 50


@dataclass
class CountryConfig:
    """Configuration for a country."""

    domain_id: int
    name: str
    currency: str = "EUR"
    categories: Dict[str, CategoryConfig] = field(default_factory=dict)


class RedisCache:
    """Redis-based cache for ASINs and token tracking."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """Initialize Redis connection."""
        self.host = host
        self.port = port
        self.db = db
        self._client = None

    @property
    def client(self):
        """Lazy initialization of Redis client."""
        if self._client is None:
            try:
                import redis

                self._client = redis.Redis(
                    host=self.host, port=self.port, db=self.db, decode_responses=True
                )
                self._client.ping()
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
                self._client = None
        return self._client

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if self.client:
            try:
                return self.client.get(key)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        return None

    def set(self, key: str, value: str, ttl: int = 21600) -> bool:
        """Set value in cache with TTL."""
        if self.client:
            try:
                self.client.setex(key, ttl, value)
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if self.client:
            try:
                self.client.delete(key)
                return True
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
        return False

    def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        if self.client:
            try:
                return self.client.keys(pattern)
            except Exception as e:
                logger.warning(f"Redis keys error: {e}")
        return []


class CategoryWatcher:
    """
    Watches Keepa categories and collects ASINs from bestsellers.

    Features:
    - Redis caching with configurable TTL
    - Automatic cache refresh
    - Token usage tracking
    """

    def __init__(
        self,
        config_path: str = "config/categories.yaml",
        keepa_client: Optional[KeepaClient] = None,
        redis_host: Optional[str] = None,
        cache_ttl: int = 21600,  # 6 hours default
    ):
        self.config_path = config_path
        self.keepa_client = keepa_client or create_keepa_client()
        self.countries: Dict[str, CountryConfig] = {}
        self._all_asins: Set[str] = set()
        self._last_fetch: Optional[datetime] = None
        self.cache_ttl = cache_ttl

        # Initialize Redis cache
        redis_host = redis_host or os.getenv("REDIS_HOST", "localhost")
        self.cache = RedisCache(host=redis_host, port=6379, db=0)

        # Token tracking
        self._tokens_used = 0

        self._load_config()

    def _load_config(self) -> None:
        """Load category configuration from YAML."""
        path = Path(self.config_path)
        if not path.exists():
            logger.warning(f"Category config not found: {self.config_path}")
            return

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        for country_code, country_data in data.get("COUNTRIES", {}).items():
            categories = {}
            for cat_name, cat_data in country_data.get("categories", {}).items():
                categories[cat_name] = CategoryConfig(
                    keepa_id=cat_data["keepa_id"],
                    name=cat_data["name"],
                    limit=cat_data.get("limit", 50),
                )

            self.countries[country_code] = CountryConfig(
                domain_id=country_data["domain_id"],
                name=country_data["name"],
                currency=country_data.get("currency", "EUR"),
                categories=categories,
            )

        logger.info(f"Loaded {len(self.countries)} countries with categories")

    def _get_cache_key(self, country_code: str, category_name: str) -> str:
        """Generate cache key for a category."""
        return f"keepa:category:{country_code}:{category_name}"

    def _get_asins_cache_key(self) -> str:
        """Generate cache key for all ASINs."""
        return "keepa:category:all_asins"

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self._last_fetch:
            return False
        elapsed = datetime.utcnow() - self._last_fetch
        return elapsed < timedelta(seconds=self.cache_ttl)

    def _get_cached_asins(self) -> Optional[Set[str]]:
        """Try to get ASINs from Redis cache."""
        cache_key = self._get_asins_cache_key()
        cached = self.cache.get(cache_key)
        if cached:
            try:
                asins = set(json.loads(cached))
                logger.info(f"Cache hit: {len(asins)} ASINs from Redis")
                return asins
            except json.JSONDecodeError:
                logger.warning("Failed to decode cached ASINs")
        return None

    def _cache_asins(self, asins: Set[str]) -> None:
        """Store ASINs in Redis cache."""
        cache_key = self._get_asins_cache_key()
        try:
            self.cache.set(cache_key, json.dumps(list(asins)), self.cache_ttl)
            logger.info(f"Cached {len(asins)} ASINs (TTL: {self.cache_ttl}s)")
        except Exception as e:
            logger.warning(f"Failed to cache ASINs: {e}")

    def fetch_category_asins(self, country_code: str, category_name: str) -> Set[str]:
        """
        Fetch ASINs for a specific category with caching.

        Returns:
            Set of ASINs for this category
        """
        cache_key = self._get_cache_key(country_code, category_name)

        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            try:
                return set(json.loads(cached))
            except json.JSONDecodeError:
                pass

        # Fetch from API
        country_config = self.countries.get(country_code)
        if not country_config:
            logger.warning(f"Unknown country: {country_code}")
            return set()

        category_config = country_config.categories.get(category_name)
        if not category_config:
            logger.warning(f"Unknown category: {category_name}")
            return set()

        try:
            asins = self.keepa_client.category_bestsellers(
                category_id=category_config.keepa_id,
                domain=country_config.domain_id,
                limit=category_config.limit,
            )

            # Track token usage (category query = 5 tokens)
            self._tokens_used += 5

            # Cache result
            self.cache.set(cache_key, json.dumps(asins), self.cache_ttl)

            logger.info(
                f"{country_config.name}/{category_config.name}: {len(asins)} ASINs"
            )

            return set(asins)

        except Exception as e:
            logger.error(f"Failed to fetch {country_code}/{category_name}: {e}")
            return set()

    def fetch_all_asins(self, force_refresh: bool = False) -> Set[str]:
        """
        Fetch ASINs from all configured categories.

        Args:
            force_refresh: Ignore cache and fetch fresh data

        Returns:
            Set of all unique ASINs found
        """
        # Check if we can use cached data
        if not force_refresh and self._is_cache_valid():
            cached = self._get_cached_asins()
            if cached:
                self._all_asins = cached
                return self._all_asins

        all_asins: Set[str] = set()

        for country_code, country_config in self.countries.items():
            logger.info(f"Fetching ASINs for {country_config.name}...")

            for cat_name in country_config.categories.keys():
                asins = self.fetch_category_asins(country_code, cat_name)
                all_asins.update(asins)

        self._all_asins = all_asins
        self._last_fetch = datetime.utcnow()

        # Cache all ASINs
        self._cache_asins(all_asins)

        logger.info(f"Total unique ASINs: {len(self._all_asins)}")
        return self._all_asins

    def get_asins(self, force_refresh: bool = False) -> Set[str]:
        """
        Get ASINs, using cache if available.

        Args:
            force_refresh: Ignore cache and fetch fresh data
        """
        if not self._all_asins or force_refresh:
            self.fetch_all_asins(force_refresh)
        return self._all_asins

    def get_countries(self) -> Dict[str, CountryConfig]:
        """Get country configurations."""
        return self.countries

    def get_tokens_used(self) -> int:
        """Get total tokens used in this session."""
        return self._tokens_used

    def clear_cache(self) -> bool:
        """Clear all cached ASINs."""
        keys = self.cache.keys("keepa:category:*")
        success = True
        for key in keys:
            if not self.cache.delete(key):
                success = False
        if success:
            logger.info("Cache cleared successfully")
        return success

    def get_summary(self) -> Dict:
        """Get summary of loaded categories."""
        return {
            "countries": len(self.countries),
            "total_asins": len(self._all_asins),
            "last_fetch": self._last_fetch.isoformat() if self._last_fetch else None,
            "cache_ttl_seconds": self.cache_ttl,
            "tokens_used": self._tokens_used,
            "cache_available": self.cache.client is not None,
            "breakdown": {
                code: {
                    "name": config.name,
                    "currency": config.currency,
                    "categories": len(config.categories),
                    "domain_id": config.domain_id,
                }
                for code, config in self.countries.items()
            },
        }


def create_category_watcher(
    config_path: Optional[str] = None,
) -> CategoryWatcher:
    """Factory function to create CategoryWatcher."""
    path = config_path or os.getenv("CATEGORY_CONFIG", "config/categories.yaml")
    return CategoryWatcher(config_path=path)


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)

    watcher = create_category_watcher()

    print("\n📊 Category Configuration Summary:")
    summary = watcher.get_summary()
    print(json.dumps(summary, indent=2, default=str))

    print("\n🔄 Fetching ASINs from all categories...")
    asins = watcher.fetch_all_asins()
    print(f"\n✅ Found {len(asins)} unique ASINs")
    print(f"📊 Tokens used: {watcher.get_tokens_used()}")
