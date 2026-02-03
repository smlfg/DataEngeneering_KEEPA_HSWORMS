# Elasticsearch Schema and Index Configuration

## Index: `products`

### Index Settings
```json
PUT /products
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "refresh_interval": "5s",
    "max_result_window": 50000,
    "analysis": {
      "analyzer": {
        "product_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "asciifolding", "product_synonyms"]
        }
      },
      "filter": {
        "product_synonyms": {
          "type": "synonym",
          "synonyms": [
            "qwertz, german, de, deutsch",
            "qwerty, us, english",
            "keyboard, tastatur, keyboard",
            "macbook, apple, mac book"
          ]
        }
      }
    }
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "asin": {
        "type": "keyword",
        "normalizer": "lowercase_normalizer"
      },
      "title": {
        "type": "text",
        "analyzer": "product_analyzer",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "brand": {
        "type": "keyword"
      },
      "category": {
        "type": "keyword"
      },
      "image_url": {
        "type": "keyword",
        "index": false
      },
      "product_url": {
        "type": "keyword",
        "index": false
      },
      "current_prices": {
        "type": "object",
        "properties": {
          "DE": {"type": "float"},
          "IT": {"type": "float"},
          "ES": {"type": "float"},
          "UK": {"type": "float"},
          "FR": {"type": "float"}
        }
      },
      "price_history": {
        "type": "nested",
        "properties": {
          "marketplace": {"type": "keyword"},
          "prices": {
            "type": "nested",
            "properties": {
              "price": {"type": "float"},
              "timestamp": {"type": "date"}
            }
          }
        }
      },
      "arbitrage_scores": {
        "type": "nested",
        "properties": {
          "source_marketplace": {"type": "keyword"},
          "target_marketplace": {"type": "keyword"},
          "margin": {"type": "float"},
          "profit": {"type": "float"},
          "net_profit": {"type": "float"},
          "confidence": {"type": "keyword"},
          "calculated_at": {"type": "date"}
        }
      },
      "best_opportunity": {
        "type": "object",
        "properties": {
          "source_marketplace": {"type": "keyword"},
          "target_marketplace": {"type": "keyword"},
          "margin": {"type": "float"},
          "profit": {"type": "float"},
          "net_profit": {"type": "float"}
        }
      },
      "last_updated": {
        "type": "date"
      },
      "first_seen": {
        "type": "date"
      },
      "is_active": {
        "type": "boolean"
      },
      "metadata": {
        "type": "object",
        "enabled": false
      }
    }
  },
  "normalizers": {
    "lowercase_normalizer": {
      "type": "custom",
      "filter": ["lowercase"]
    }
  }
}
```

---

## Complete Mapping Definition

```json
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "refresh_interval": "5s",
    "max_result_window": 50000
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "asin": {
        "type": "keyword",
        "normalizer": "lowercase_normalizer",
        "doc_values": true
      },
      "title": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 500
          }
        }
      },
      "brand": {
        "type": "keyword",
        "doc_values": true
      },
      "category": {
        "type": "keyword",
        "doc_values": true
      },
      "subcategory": {
        "type": "keyword"
      },
      "image_url": {
        "type": "keyword",
        "index": false,
        "doc_values": false
      },
      "product_url": {
        "type": "keyword",
        "index": false,
        "doc_values": false
      },
      "current_prices": {
        "type": "object",
        "properties": {
          "DE": {
            "type": "float",
            "doc_values": true
          },
          "IT": {
            "type": "float",
            "doc_values": true
          },
          "ES": {
            "type": "float",
            "doc_values": true
          },
          "UK": {
            "type": "float",
            "doc_values": true
          },
          "FR": {
            "type": "float",
            "doc_values": true
          }
        }
      },
      "price_history": {
        "type": "nested",
        "properties": {
          "marketplace": {
            "type": "keyword"
          },
          "price": {
            "type": "float"
          },
          "timestamp": {
            "type": "date"
          },
          "condition": {
            "type": "keyword"
          }
        }
      },
      "best_margin": {
        "type": "float",
        "doc_values": true
      },
      "best_profit": {
        "type": "float",
        "doc_values": true
      },
      "best_source": {
        "type": "keyword"
      },
      "best_target": {
        "type": "keyword"
      },
      "arbitrage_count": {
        "type": "integer",
        "doc_values": true
      },
      "avg_margin_30d": {
        "type": "float"
      },
      "is_profitable": {
        "type": "boolean"
      },
      "last_updated": {
        "type": "date",
        "format": "strict_date_optional_time||epoch_millis"
      },
      "first_seen": {
        "type": "date",
        "format": "strict_date_optional_time||epoch_millis"
      },
      "is_active": {
        "type": "boolean"
      },
      "sync_version": {
        "type": "long"
      },
      "metadata": {
        "type": "object",
        "enabled": false,
        "properties": {
          "ean": {
            "type": "keyword"
          },
          "mpn": {
            "type": "keyword"
          },
          "upc": {
            "type": "keyword"
          },
          "weight": {
            "type": "float"
          },
          "dimensions": {
            "type": "object",
            "properties": {
              "length": {"type": "float"},
              "width": {"type": "float"},
              "height": {"type": "float"}
            }
          }
        }
      }
    }
  }
}
```

---

## Query Examples

### 1. Find All Arbitrage Opportunities (Margin > 20%)
```json
GET /products/_search
{
  "query": {
    "bool": {
      "must": [
        {"range": {"best_margin": {"gte": 20}}},
        {"term": {"is_active": true}}
      ]
    }
  },
  "sort": [{"best_margin": "desc"}],
  "size": 100
}
```

### 2. Find Products by Source and Target Marketplace
```json
GET /products/_search
{
  "query": {
    "bool": {
      "must": [
        {"term": {"best_source": "IT"}},
        {"term": {"best_target": "DE"}}
      ]
    }
  }
}
```

### 3. Search by Title with Filter
```json
GET /products/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "logitech tastatur",
            "fields": ["title^2", "title.keyword"],
            "type": "best_fields"
          }
        }
      ],
      "filter": [
        {"range": {"best_margin": {"gte": 15}}},
        {"range": {"current_prices.DE": {"lte": 200}}}
      ]
    }
  }
}
```

### 4. Aggregations for Dashboard Stats
```json
GET /products/_search
{
  "size": 0,
  "query": {
    "term": {"is_active": true}
  },
  "aggs": {
    "total_products": {"value_count": {"field": "asin"}},
    "profitable_count": {
      "filter": {"term": {"is_profitable": true}}
    },
    "avg_margin": {"avg": {"field": "best_margin"}},
    "highest_margin": {"max": {"field": "best_margin"}},
    "by_category": {
      "terms": {"field": "category", "size": 20},
      "aggs": {
        "avg_margin": {"avg": {"field": "best_margin"}}
      }
    },
    "by_source_marketplace": {
      "terms": {"field": "best_source"},
      "aggs": {
        "avg_profit": {"avg": {"field": "best_profit"}}
      }
    }
  }
}
```

### 5. Price History for Chart
```json
GET /products/_search
{
  "_source": ["asin", "title", "price_history"],
  "query": {
    "term": {"asin": "B09V3KXJPB"}
  }
}
```

---

## Index Lifecycle Policy

```json
PUT /_ilm/policy/products-policy
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_age": "1d",
            "max_size": "50gb"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": {
            "number_of_shards": 1
          },
          "forcemerge": {
            "max_num_segments": 1
          },
          "set_priority": {
            "priority": 50
          }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "freeze": {},
          "set_priority": {
            "priority": 0
          }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

---

## Data Access Patterns

| Operation | Query Type | Expected QPS |
|-----------|------------|--------------|
| Get by ASIN | `GET /products/_doc/{id}` | ~100 |
| List with filters | `_search` with query | ~50 |
| Dashboard aggregations | `_search` with aggs | ~10 |
| Full-text search | `_search` with multi_match | ~20 |
| Price updates | `UPDATE` by ID | ~50 |

---

## Indexing Strategy

### Bulk Indexing for Initial Load
```bash
curl -X POST "localhost:9200/_bulk" -H "Content-Type: application/json" \
  --data-binary @products.jsonl
```

### Incremental Updates (Real-time)
```python
from elasticsearch import Elasticsearch

es = Elasticsearch(["localhost:9200"])

def upsert_product(product_data):
    es.update(
        index="products",
        id=product_data["asin"],
        doc=product_data,
        doc_as_upsert=True
    )
```

### Price History Update (Nested)
```python
def add_price_point(asin, marketplace, price, timestamp):
    es.update(
        index="products",
        id=asin,
        script={
            "source": """
            ctx._source.price_history.add(params.newPoint);
            // Keep only last 30 days
            def cutoff = params.cutoffTime;
            ctx._source.price_history.removeIf(point -> point.timestamp < cutoff);
            """,
            "params": {
                "newPoint": {
                    "marketplace": marketplace,
                    "price": price,
                    "timestamp": timestamp
                },
                "cutoffTime": (datetime.utcnow() - timedelta(days=30)).isoformat()
            }
        }
    )
```
