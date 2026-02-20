import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from elasticsearch import AsyncElasticsearch

from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


PRICE_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "asin": {"type": "keyword"},
            "product_title": {
                "type": "text",
                "analyzer": "standard",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "current_price": {"type": "float"},
            "target_price": {"type": "float"},
            "previous_price": {"type": "float"},
            "price_change_percent": {"type": "float"},
            "domain": {"type": "keyword"},
            "currency": {"type": "keyword"},
            "timestamp": {"type": "date"},
            "event_type": {"type": "keyword"},
        }
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "index": {
            "max_result_window": 50000,
        },
    },
}

DEAL_INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "deal_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "german_stemmer", "asciifolding"],
                }
            },
            "filter": {"german_stemmer": {"type": "stemmer", "language": "german"}},
        },
    },
    "mappings": {
        "properties": {
            "asin": {"type": "keyword"},
            "title": {
                "type": "text",
                "analyzer": "deal_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "suggest": {"type": "completion"},
                },
            },
            "description": {"type": "text", "analyzer": "deal_analyzer"},
            "current_price": {"type": "float"},
            "original_price": {"type": "float"},
            "discount_percent": {"type": "float"},
            "rating": {"type": "float"},
            "review_count": {"type": "integer"},
            "sales_rank": {"type": "integer"},
            "domain": {"type": "keyword"},
            "category": {"type": "keyword"},
            "prime_eligible": {"type": "boolean"},
            "url": {"type": "keyword"},
            "deal_score": {"type": "float"},
            "timestamp": {"type": "date"},
            "event_type": {"type": "keyword"},
        }
    },
}


class ElasticsearchService:
    def __init__(self):
        self.client: Optional[AsyncElasticsearch] = None
        self.prices_index = settings.elasticsearch_index_prices
        self.deals_index = settings.elasticsearch_index_deals

    async def connect(self):
        self.client = AsyncElasticsearch([settings.elasticsearch_url])
        await self._create_indices()
        logger.info(f"Connected to Elasticsearch at {settings.elasticsearch_url}")

    async def close(self):
        if self.client:
            await self.client.close()
            logger.info("Elasticsearch connection closed")

    async def _create_indices(self):
        if not self.client:
            return

        for index_name, mapping in [
            (self.prices_index, PRICE_INDEX_MAPPING),
            (self.deals_index, DEAL_INDEX_MAPPING),
        ]:
            try:
                if not await self.client.indices.exists(index=index_name):
                    await self.client.indices.create(index=index_name, body=mapping)
                    logger.info(f"Created Elasticsearch index: {index_name}")
            except Exception as e:
                logger.error(f"Error creating index {index_name}: {e}")

    async def index_price_update(self, price_data: Dict[str, Any]) -> bool:
        if not self.client:
            return False

        try:
            await self.client.index(
                index=self.prices_index,
                document=price_data,
            )
            return True
        except Exception as e:
            logger.error(f"Error indexing price update: {e}")
            return False

    async def index_deal_update(self, deal_data: Dict[str, Any]) -> bool:
        if not self.client:
            return False

        try:
            await self.client.index(
                index=self.deals_index,
                document=deal_data,
            )
            return True
        except Exception as e:
            logger.error(f"Error indexing deal update: {e}")
            return False

    async def search_prices(
        self,
        asin: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        domain: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 0,
        size: int = 20,
    ) -> Dict[str, Any]:
        if not self.client:
            return {"hits": []}

        must_clauses = []

        if asin:
            must_clauses.append({"term": {"asin": asin}})

        if min_price or max_price:
            price_range = {"range": {"current_price": {}}}
            if min_price:
                price_range["range"]["current_price"]["gte"] = min_price
            if max_price:
                price_range["range"]["current_price"]["lte"] = max_price
            must_clauses.append(price_range)

        if domain:
            must_clauses.append({"term": {"domain": domain}})

        if from_date or to_date:
            date_range = {"range": {"timestamp": {}}}
            if from_date:
                date_range["range"]["timestamp"]["gte"] = from_date.isoformat()
            if to_date:
                date_range["range"]["timestamp"]["lte"] = to_date.isoformat()
            must_clauses.append(date_range)

        query = {"bool": {"must": must_clauses}} if must_clauses else {"match_all": {}}

        try:
            result = await self.client.search(
                index=self.prices_index,
                query=query,
                from_=page * size,
                size=size,
                sort=[{"timestamp": "desc"}],
            )
            return result
        except Exception as e:
            logger.error(f"Error searching prices: {e}")
            return {"hits": []}

    async def get_price_statistics(self, asin: str) -> Dict[str, Any]:
        if not self.client:
            return {}

        query = {"term": {"asin": asin}}

        try:
            result = await self.client.search(
                index=self.prices_index,
                query=query,
                size=0,
                aggs={
                    "price_stats": {"stats": {"field": "current_price"}},
                    "price_changes": {
                        "histogram": {
                            "field": "current_price",
                            "interval": 10,
                        }
                    },
                },
            )
            return result.get("aggregations", {})
        except Exception as e:
            logger.error(f"Error getting price statistics: {e}")
            return {}

    async def get_deal_aggregations(
        self,
        min_discount: float = 0,
        min_rating: float = 0,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.client:
            return {}

        must_clauses = [
            {"range": {"discount_percent": {"gte": min_discount}}},
            {"range": {"rating": {"gte": min_rating}}},
        ]

        if domain:
            must_clauses.append({"term": {"domain": domain}})

        query = {"bool": {"must": must_clauses}}

        try:
            result = await self.client.search(
                index=self.deals_index,
                query=query,
                size=0,
                aggs={
                    "by_discount": {"terms": {"field": "discount_percent", "size": 10}},
                    "by_domain": {"terms": {"field": "domain"}},
                    "avg_price": {"avg": {"field": "current_price"}},
                    "avg_discount": {"avg": {"field": "discount_percent"}},
                },
            )
            return result.get("aggregations", {})
        except Exception as e:
            logger.error(f"Error getting deal aggregations: {e}")
            return {}

    async def delete_old_data(self, days: int = 90) -> int:
        if not self.client:
            return 0

        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        try:
            result = await self.client.delete_by_query(
                index=f"{self.prices_index},{self.deals_index}",
                query={"range": {"timestamp": {"lt": cutoff_date.isoformat()}}},
            )
            deleted = result.get("deleted", 0)
            logger.info(f"Deleted {deleted} old documents")
            return deleted
        except Exception as e:
            logger.error(f"Error deleting old data: {e}")
            return 0


es_service = ElasticsearchService()
