# Kafka Contract - Message Formats and Topics

## Topic Definitions

| Topic Name | Type | Producer | Consumer | Description |
|------------|------|----------|----------|-------------|
| `raw.keepa_updates` | Pub/Sub | Producer Worker | Enrichment Consumer | Raw price updates from Keepa API |
| `products.enriched` | Pub/Sub | Enrichment Consumer | Arbitrage Detector | Enriched and validated product data |
| `arbitrage.alerts` | Pub/Sub | Arbitrage Detector | Alert Dispatcher | High-margin arbitrage opportunities |

## Message Schemas

### Topic: `raw.keepa_updates`

**Schema Type:** JSON (Keepa API native format)

**Producer:** `src/producer/keepa_producer.py`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Keepa Raw Update",
  "type": "object",
  "required": ["asin", "marketplace", "timestamp"],
  "properties": {
    "asin": {
      "type": "string",
      "pattern": "^[A-Z0-9]{10}$",
      "description": "Amazon ASIN"
    },
    "marketplace": {
      "type": "string",
      "enum": ["DE", "IT", "ES", "UK", "FR"],
      "description": "Keepa marketplace code"
    },
    "domain_id": {
      "type": "integer",
      "description": "Keepa domain ID (1=DE, 3=UK, 5=IT, 6=ES, 8=FR)"
    },
    "current": {
      "type": ["number", "null"],
      "description": "Current price in cents (Keepa format)"
    },
    "current_prices": {
      "type": "object",
      "description": "Current prices by type (NEW, USED, REFURBISHED)"
    },
    "price_history": {
      "type": "array",
      "description": "Price history points"
    },
    "avg_price": {
      "type": ["number", "null"],
      "description": "30-day average price"
    },
    "buy_box_price": {
      "type": ["number", "null"],
      "description": "Buy Box price"
    },
    "buy_box_shipping": {
      "type": ["number", "null"],
      "description": "Buy Box shipping"
    },
    "last_update": {
      "type": "integer",
      "description": "Unix timestamp of last update"
    },
    "ean": {
      "type": ["string", "null"],
      "description": "EAN/UPC code"
    },
    "mpn": {
      "type": ["string", "null"],
      "description": "Manufacturer part number"
    },
    "brand": {
      "type": ["string", "null"],
      "description": "Brand name"
    },
    "title": {
      "type": ["string", "null"],
      "description": "Product title"
    },
    "image": {
      "type": ["string", "null"],
      "description": "Product image URL"
    },
    "url": {
      "type": ["string", "null"],
      "description": "Amazon product URL"
    },
    "category_id": {
      "type": ["integer", "null"],
      "description": "Keepa category ID"
    },
    "category_tree": {
      "type": ["string", "null"],
      "description": "Category path string"
    }
  }
}
```

**Example Message:**
```json
{
  "asin": "B09V3KXJPB",
  "marketplace": "DE",
  "domain_id": 1,
  "current": 14999,
  "current_prices": {
    "NEW": 14999,
    "USED": 9900
  },
  "price_history": [
    {"date": 1705315200, "price": 14999, "type": "NEW"},
    {"date": 1705228800, "price": 15499, "type": "NEW"}
  ],
  "avg_price": 15200,
  "buy_box_price": 14999,
  "buy_box_shipping": 0,
  "last_update": 1705321500,
  "ean": "5099206094075",
  "mpn": "920-011395",
  "brand": "Logitech",
  "title": "Logitech MX Keys Mini Tastatur QWERTZ DE",
  "image": "https://m.media-amazon.com/images/I/31V7P5AE3L._AC_US218_.jpg",
  "url": "https://www.amazon.de/dp/B09V3KXJPB",
  "category_id": 4279657031,
  "category_tree": "Computer & Zubehör > Tastaturen, Mäuse & Eingabegeräte > Tastaturen"
}
```

---

### Topic: `products.enriched`

**Schema Type:** JSON (Canonical format)

**Producer:** `src/consumer/enrichment_consumer.py`

**Consumer:** `src/arbitrage/detector.py`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Enriched Product",
  "type": "object",
  "required": ["asin", "current_prices", "last_updated"],
  "properties": {
    "asin": {
      "type": "string",
      "pattern": "^[A-Z0-9]{10}$"
    },
    "title": {
      "type": "string"
    },
    "brand": {
      "type": ["string", "null"]
    },
    "image_url": {
      "type": ["string", "null"],
      "format": "uri"
    },
    "product_url": {
      "type": ["string", "null"],
      "format": "uri"
    },
    "category": {
      "type": ["string", "null"]
    },
    "current_prices": {
      "type": "object",
      "properties": {
        "DE": {"type": "number"},
        "IT": {"type": "number"},
        "ES": {"type": "number"},
        "UK": {"type": "number"},
        "FR": {"type": "number"}
      },
      "additionalProperties": False
    },
    "price_history": {
      "type": "object",
      "description": "Historical prices per marketplace",
      "properties": {
        "DE": {"type": "array"},
        "IT": {"type": "array"},
        "ES": {"type": "array"},
        "UK": {"type": "array"},
        "FR": {"type": "array"}
      }
    },
    "last_updated": {
      "type": "string",
      "format": "date-time"
    },
    "first_seen": {
      "type": "string",
      "format": "date-time"
    },
    "is_active": {
      "type": "boolean",
      "default": true
    },
    "metadata": {
      "type": "object",
      "description": "Additional product metadata"
    }
  }
}
```

**Example Message:**
```json
{
  "asin": "B09V3KXJPB",
  "title": "Logitech MX Keys Mini Tastatur QWERTZ DE",
  "brand": "Logitech",
  "image_url": "https://m.media-amazon.com/images/I/31V7P5AE3L._AC_US218_.jpg",
  "product_url": "https://www.amazon.de/dp/B09V3KXJPB",
  "category": "Computer & Accessories > Keyboards",
  "current_prices": {
    "DE": 149.99,
    "IT": 89.99,
    "ES": 92.50,
    "UK": 95.00,
    "FR": 94.00
  },
  "price_history": {
    "DE": [{"price": 149.99, "timestamp": "2024-01-15T10:30:00Z"}, ...],
    "IT": [{"price": 89.99, "timestamp": "2024-01-15T10:30:00Z"}, ...]
  },
  "last_updated": "2024-01-15T10:30:00Z",
  "first_seen": "2024-01-01T00:00:00Z",
  "is_active": true,
  "metadata": {
    "ean": "5099206094075",
    "mpn": "920-011395"
  }
}
```

---

### Topic: `arbitrage.alerts`

**Schema Type:** JSON

**Producer:** `src/arbitrage/detector.py`

**Consumer:** `src/alert/dispatcher.py`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Arbitrage Alert",
  "type": "object",
  "required": ["asin", "source_marketplace", "target_marketplace", "margin", "profit"],
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique alert ID"
    },
    "asin": {
      "type": "string",
      "pattern": "^[A-Z0-9]{10}$"
    },
    "title": {
      "type": "string"
    },
    "image_url": {
      "type": ["string", "null"],
      "format": "uri"
    },
    "source_marketplace": {
      "type": "string",
      "enum": ["IT", "ES", "UK", "FR"]
    },
    "target_marketplace": {
      "type": "string",
      "enum": ["DE", "IT", "ES", "UK", "FR"]
    },
    "source_price": {
      "type": "number",
      "description": "Price at source marketplace (EUR)"
    },
    "target_price": {
      "type": "number",
      "description": "Price at target marketplace (EUR)"
    },
    "margin": {
      "type": "number",
      "description": "Gross margin percentage"
    },
    "profit": {
      "type": "number",
      "description": "Gross profit in EUR"
    },
    "estimated_fees": {
      "type": "number",
      "description": "Estimated Amazon fees (15% of target)",
      "default": 0
    },
    "net_profit": {
      "type": "number",
      "description": "Profit after estimated fees"
    },
    "confidence": {
      "type": "string",
      "enum": ["low", "medium", "high"],
      "description": "Confidence level of the opportunity"
    },
    "alert_type": {
      "type": "string",
      "enum": ["new_opportunity", "price_drop", "margin_increase"],
      "description": "Type of alert"
    },
    "priority": {
      "type": "integer",
      "description": "Priority score (higher = more urgent)",
      "minimum": 0,
      "maximum": 100
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "expires_at": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "When this opportunity may expire"
    }
  }
}
```

**Example Message:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "asin": "B09V3KXJPB",
  "title": "Logitech MX Keys Mini Tastatur QWERTZ DE",
  "image_url": "https://m.media-amazon.com/images/I/31V7P5AE3L._AC_US218_.jpg",
  "source_marketplace": "IT",
  "target_marketplace": "DE",
  "source_price": 89.99,
  "target_price": 149.99,
  "margin": 40.0,
  "profit": 60.00,
  "estimated_fees": 22.50,
  "net_profit": 37.50,
  "confidence": "high",
  "alert_type": "new_opportunity",
  "priority": 85,
  "timestamp": "2024-01-15T10:30:00Z",
  "expires_at": "2024-01-16T10:30:00Z"
}
```

---

## Kafka Configuration

### Broker Settings
```yaml
bootstrap.servers: kafka:9092
security.protocol: PLAINTEXT
auto.offset.reset: latest
enable.auto.commit: false
session.timeout.ms: 30000
heartbeat.interval.ms: 10000
max.poll.records: 100
fetch.min.bytes: 1
fetch.max.wait.ms: 500
```

### Topic Configurations
```bash
# Create topics with appropriate partitions and replication
kafka-topics.sh --bootstrap-server kafka:9092 \
  --create --topic raw.keepa_updates \
  --partitions 3 --replication-factor 1

kafka-topics.sh --bootstrap-server kafka:9092 \
  --create --topic products.enriched \
  --partitions 3 --replication-factor 1

kafka-topics.sh --bootstrap-server kafka:9092 \
  --create --topic arbitrage.alerts \
  --partitions 1 --replication-factor 1
```

### Consumer Groups
```yaml
enrichment-consumer:
  topics: [raw.keepa_updates]
  auto.offset.reset: earliest
  max.poll.interval.ms: 300000

arbitrage-detector:
  topics: [products.enriched]
  auto.offset.reset: earliest

alert-dispatcher:
  topics: [arbitrage.alerts]
  auto.offset.reset: latest
```

---

## Serialization

### Key Serialization
- **Format:** UTF-8 encoded string (ASIN)
- **Example:** `B09V3KXJPB`

### Value Serialization
- **Format:** JSON (UTF-8 encoded)
- **Content-Type:** `application/json`
- **Compression:** `lz4` (recommended for throughput)

### Schema Registry (Optional)
For production, consider using Confluent Schema Registry:
```yaml
schema.registry.url: http://schema-registry:8081
basic.auth.credentials.source: USER_INFO
```

---

## Message Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              KAFKA CLUSTER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ raw.keepa_updates (Partitioned by ASIN hash)                        │    │
│  │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │    │
│  │ │ Msg #1  │ │ Msg #2  │ │ Msg #3  │ │ Msg #4  │ │ Msg #5  │ ...   │    │
│  │ │ ASIN: A │ │ ASIN: F │ │ ASIN: K │ │ ASIN: P │ │ ASIN: Z │       │    │
│  │ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                          │
│                                    ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ products.enriched (Partitioned by ASIN hash)                        │    │
│  │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │    │
│  │ │ Prod #1 │ │ Prod #2 │ │ Prod #3 │ │ Prod #4 │ │ Prod #5 │ ...   │    │
│  │ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                          │
│                                    ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ arbitrage.alerts (Single partition - ordered alerts)                │    │
│  │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │    │
│  │ │ Alert 1 │ │ Alert 2 │ │ Alert 3 │ │ Alert 4 │ │ Alert 5 │ ...   │    │
│  │ │ Prio:99 │ │ Prio:85 │ │ Prio:72 │ │ Prio:60 │ │ Prio:45 │       │    │
│  │ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Message Processing Guarantees

### raw.keepa_updates
- **Producer:** At-least-once (with retries)
- **Consumer:** At-least-once (manual commit)
- **Ordering:** Per-ASIN ordering guaranteed (same partition)

### products.enriched
- **Producer:** At-least-once
- **Consumer:** At-least-once
- **Idempotency:** Deduplicated by ASIN in Elasticsearch

### arbitrage.alerts
- **Producer:** Exactly-once (transactional)
- **Consumer:** At-least-once
- **Deduplication:** By alert ID (UUID)
