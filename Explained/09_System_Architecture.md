# System-Architektur - Wie alles zusammenspielt

## Der komplette Datenfluss

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Amazon Arbitrage Tracker System                  │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ Keepa API    │  Externe Datenquelle (Amazon-Preise)
│ (External)   │
└──────┬───────┘
       │ HTTPS Requests (alle 60s)
       ▼
┌──────────────────────────────────────────────────────────────────┐
│                         PRODUCER                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  1. Keepa Client (keepa_client.py)                          │ │
│  │     - API-Requests mit Rate-Limiting (20/min)               │ │
│  │     - ASIN-Watchlist abfragen                               │ │
│  │     - Preis-Daten extrahieren                               │ │
│  │                                                              │ │
│  │  2. Kafka Producer (producer.py)                            │ │
│  │     - JSON-Serialisierung                                   │ │
│  │     - Message-Key = ASIN                                    │ │
│  │     - Send to topic: raw.keepa_updates                      │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │   KAFKA CLUSTER     │
                    │                     │
                    │  Topic:             │
                    │  raw.keepa_updates  │
                    │  (3 Partitions)     │
                    └──────────┬──────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                   ENRICHMENT CONSUMER                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  1. Kafka Consumer                                          │ │
│  │     - Poll messages from raw.keepa_updates                  │ │
│  │     - Consumer Group: enrichment-consumer                   │ │
│  │                                                              │ │
│  │  2. Data Enrichment                                         │ │
│  │     - Validate JSON structure                               │ │
│  │     - Convert prices (Cent → Euro)                          │ │
│  │     - Add timestamps                                        │ │
│  │     - Calculate price statistics                            │ │
│  │                                                              │ │
│  │  3. Elasticsearch Writer                                    │ │
│  │     - Index products by ASIN                                │ │
│  │     - Update existing documents                             │ │
│  │     - Index: products                                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │  ELASTICSEARCH      │
                    │                     │
                    │  Index: products    │
                    │  (~8 documents)     │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴───────────────┐
                │                              │
                ▼                              ▼
┌─────────────────────────┐      ┌─────────────────────────┐
│  ARBITRAGE DETECTOR     │      │      FASTAPI            │
│                         │      │                         │
│  1. Query Products      │      │  REST API Endpoints:    │
│     - All active        │      │                         │
│     - Has prices        │      │  GET /health            │
│                         │      │  GET /products          │
│  2. Calculate Margins   │      │  GET /products/{asin}   │
│     - For each pair     │      │  GET /opportunities     │
│     - DE→IT, UK→ES, ... │      │  GET /stats             │
│                         │      │                         │
│  3. Find Opportunities  │      │  Features:              │
│     - margin > 10%      │      │  - CORS enabled         │
│     - Active products   │      │  - Auto-docs (/docs)    │
│                         │      │  - ES queries           │
│  4. Update ES           │      └────────────┬────────────┘
│     - Add margin fields │                   │
│     - Set is_active     │                   │ HTTP
└─────────────────────────┘                   │
                                              ▼
                              ┌──────────────────────────────┐
                              │      STREAMLIT DASHBOARD      │
                              │                               │
                              │  UI Components:               │
                              │  ┌─────────────────────────┐  │
                              │  │ Sidebar                 │  │
                              │  │  - Min Margin Slider    │  │
                              │  │  - Market Filters       │  │
                              │  │  - Limit Input          │  │
                              │  └─────────────────────────┘  │
                              │                               │
                              │  ┌─────────────────────────┐  │
                              │  │ Metrics Row             │  │
                              │  │  - Total Products       │  │
                              │  │  - Opportunities        │  │
                              │  │  - Markets              │  │
                              │  └─────────────────────────┘  │
                              │                               │
                              │  ┌─────────────────────────┐  │
                              │  │ Opportunities Table     │  │
                              │  │  - ASIN, Title          │  │
                              │  │  - Buy/Sell Markets     │  │
                              │  │  - Prices & Margins     │  │
                              │  └─────────────────────────┘  │
                              │                               │
                              │  ┌─────────────────────────┐  │
                              │  │ Product Details         │  │
                              │  │  - Product Image        │  │
                              │  │  - Amazon Links         │  │
                              │  └─────────────────────────┘  │
                              └───────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION (Airflow)                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Scheduler:                                                 │ │
│  │    - Triggers DAGs based on schedule                        │ │
│  │                                                              │ │
│  │  Worker (Celery):                                           │ │
│  │    - Executes tasks from queue                              │ │
│  │                                                              │ │
│  │  DAG: keepa_category_scraper                                │ │
│  │    - fetch_bestsellers → fetch_details → send_to_kafka      │ │
│  │    - Schedule: Every 2 hours                                │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## Technologie-Stack im Detail

### Data Layer

```
┌─────────────────────────────────────┐
│          DATA STORES                │
├─────────────────────────────────────┤
│  Elasticsearch  │  Products         │ → NoSQL Database
│  PostgreSQL     │  Airflow Metadata │ → Relational DB
│  Redis          │  Celery Queue     │ → In-Memory Cache
│  Kafka          │  Message Queue    │ → Event Stream
│  Zookeeper      │  Kafka Metadata   │ → Coordination
└─────────────────────────────────────┘
```

### Application Layer

```
┌─────────────────────────────────────┐
│       APPLICATION SERVICES          │
├─────────────────────────────────────┤
│  Producer       │  Data Collection  │ → Python + Kafka
│  Consumer       │  Data Enrichment  │ → Python + ES
│  Detector       │  Arbitrage Logic  │ → Python
│  API            │  REST Endpoints   │ → FastAPI
│  Dashboard      │  User Interface   │ → Streamlit
└─────────────────────────────────────┘
```

### Infrastructure Layer

```
┌─────────────────────────────────────┐
│        INFRASTRUCTURE               │
├─────────────────────────────────────┤
│  Docker         │  Containerization │
│  Docker Compose │  Orchestration    │
│  Poetry         │  Dependencies     │
│  Airflow        │  Workflow Mgmt    │
└─────────────────────────────────────┘
```

## Kommunikations-Patterns

### 1. Producer → Kafka (Async Messaging)

```python
# Producer
producer.produce(
    topic='raw.keepa_updates',
    key=asin,
    value=json_data
)
producer.flush()
```

**Pattern:** Fire-and-Forget
**Vorteil:** Producer wartet nicht auf Verarbeitung

### 2. Consumer → Elasticsearch (Indexing)

```python
# Consumer
es.index(
    index='products',
    id=asin,
    document=enriched_data
)
```

**Pattern:** Write-heavy
**Vorteil:** Schnelles Schreiben, langsames Lesen optimiert

### 3. API → Elasticsearch (Query)

```python
# API
response = es.search(
    index='products',
    query={'match_all': {}},
    sort=[{'margin_percentage': {'order': 'desc'}}]
)
```

**Pattern:** Read-heavy
**Vorteil:** Komplexe Queries, schnelle Suche

### 4. Dashboard → API (HTTP)

```python
# Dashboard
response = requests.get(
    'http://api:8000/opportunities',
    params={'min_margin': 10}
)
```

**Pattern:** Request-Response
**Vorteil:** Standardisiert, cachebare Responses

## Daten-Transformationen

### Stage 1: Raw Keepa Data

```json
{
  "asin": "B0D1XD1ZV3",
  "domain": 3,
  "title": "Amazon Echo Dot (5. Gen)",
  "stats": {
    "current": 4999
  }
}
```

**Format:** Keepa API Response
**Location:** Kafka Topic `raw.keepa_updates`

### Stage 2: Enriched Product Data

```json
{
  "asin": "B0D1XD1ZV3",
  "title": "Amazon Echo Dot (5. Gen)",
  "brand": "Amazon",
  "current_prices": {
    "DE": 4999,
    "IT": 5499,
    "ES": 4799
  },
  "last_updated": "2026-01-11T12:05:00Z",
  "first_seen": "2026-01-11T12:05:00Z",
  "is_active": true
}
```

**Format:** Normalized JSON
**Location:** Elasticsearch Index `products`

### Stage 3: Arbitrage Opportunities

```json
{
  "asin": "B0D1XD1ZV3",
  "title": "Amazon Echo Dot (5. Gen)",
  "source_market": "ES",
  "target_market": "IT",
  "source_price": 4799,
  "target_price": 5499,
  "margin": 700,
  "margin_percentage": 14.58,
  "is_active": true
}
```

**Format:** Calculated Opportunities
**Location:** Elasticsearch (updated documents)

### Stage 4: Dashboard Display

```python
# DataFrame for Display
df = pd.DataFrame([
    {
        "ASIN": "B0D1XD1ZV3",
        "Produkt": "Amazon Echo Dot (5. Gen)",
        "Kaufmarkt": "ES",
        "Verkaufsmarkt": "IT",
        "Kaufpreis (€)": 47.99,
        "Verkaufspreis (€)": 54.99,
        "Gewinn (€)": 7.00,
        "Marge %": 14.58
    }
])
```

**Format:** Pandas DataFrame
**Location:** Streamlit UI

## Fehlerbehandlung & Resilienz

### Retry-Strategien

```python
# Producer: Kafka Retry
producer = Producer({
    'retries': 3,
    'retry.backoff.ms': 1000
})

# Consumer: Manual Retry
for attempt in range(3):
    try:
        es.index(...)
        break
    except Exception as e:
        if attempt == 2:
            raise
        time.sleep(2 ** attempt)

# API: Keepa Rate Limit
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_keepa_data():
    ...
```

### Health Checks

```yaml
# docker-compose.yml
elasticsearch:
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health"]
    interval: 10s
    retries: 5

kafka:
  healthcheck:
    test: ["CMD-SHELL", "kafka-broker-api-versions --bootstrap-server kafka:9092"]
    interval: 10s
    retries: 10

api:
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://localhost:8000/health"]
    interval: 10s
    retries: 3
```

### Graceful Degradation

```python
# Dashboard: Fallback bei API-Fehler
try:
    opportunities = fetch_opportunities(min_margin)
    st.dataframe(opportunities)
except requests.exceptions.RequestException:
    st.error("API nicht erreichbar - Bitte später versuchen")
    st.stop()

# API: Elasticsearch Fallback
try:
    products = es.search(index='products', ...)
except Exception:
    return {
        "error": "Database unavailable",
        "products": []
    }
```

## Skalierungs-Strategien

### Horizontal Scaling

```yaml
# docker-compose.yml
enrichment-consumer:
  deploy:
    replicas: 3  # 3 Consumer-Instanzen

kafka:
  environment:
    KAFKA_NUM_PARTITIONS: 3  # 3 Partitionen = 3 parallele Consumer
```

**Resultat:**
- 3 Consumer teilen sich 3 Partitionen
- 3× höherer Durchsatz

### Vertical Scaling

```yaml
elasticsearch:
  environment:
    - "ES_JAVA_OPTS=-Xms2g -Xmx2g"  # 2GB RAM statt 512MB
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
```

### Caching-Strategie

```python
# API: Response-Caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://redis:6379")
    FastAPICache.init(RedisBackend(redis), prefix="api-cache")

@app.get("/opportunities")
@cache(expire=60)  # 60s Cache
async def get_opportunities():
    ...

# Dashboard: Session State
if "opportunities" not in st.session_state:
    st.session_state.opportunities = fetch_opportunities()
```

## Monitoring & Observability

### Logging-Strategie

```python
# Strukturiertes Logging
import logging
import json

logger = logging.getLogger(__name__)

logger.info(json.dumps({
    "event": "product_indexed",
    "asin": "B0D1XD1ZV3",
    "timestamp": datetime.now().isoformat(),
    "index": "products"
}))
```

### Metriken sammeln

```python
# Prometheus Metrics
from prometheus_client import Counter, Histogram

products_indexed = Counter('products_indexed_total', 'Total products indexed')
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration')

# Nutzen
products_indexed.inc()
with api_request_duration.time():
    response = es.search(...)
```

### Dashboard-Monitoring

```python
# Streamlit: System-Status
col1, col2, col3 = st.columns(3)

with col1:
    es_health = check_elasticsearch_health()
    st.metric("Elasticsearch", "✅ UP" if es_health else "❌ DOWN")

with col2:
    kafka_health = check_kafka_health()
    st.metric("Kafka", "✅ UP" if kafka_health else "❌ DOWN")

with col3:
    api_health = check_api_health()
    st.metric("API", "✅ UP" if api_health else "❌ DOWN")
```

## Deployment-Strategie

### Lokale Entwicklung

```bash
# 1. Services starten
docker compose up -d elasticsearch kafka zookeeper

# 2. Python-Services lokal (für Debugging)
cd src/producer
poetry install
poetry run python producer.py

# 3. Tests
poetry run pytest
```

### Staging/Production

```bash
# 1. Alle Services als Container
docker compose up -d

# 2. Health Checks warten
docker compose ps

# 3. Logs monitoren
docker compose logs -f
```

### CI/CD Pipeline (Beispiel)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          poetry install
          poetry run pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build images
        run: docker compose build

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          docker compose -f docker-compose.prod.yml up -d
```

## Performance-Optimierungen

### 1. Elasticsearch Bulk Indexing

```python
from elasticsearch.helpers import bulk

# Statt einzelner Inserts
for product in products:
    es.index(index='products', id=product['asin'], document=product)

# Bulk-Insert
actions = [
    {
        "_index": "products",
        "_id": product["asin"],
        "_source": product
    }
    for product in products
]
bulk(es, actions)
```

### 2. Kafka Batch Processing

```python
# Consumer: Batch statt einzeln
messages = consumer.consume(num_messages=100, timeout=1.0)

products = []
for msg in messages:
    products.append(parse_message(msg))

# Batch in ES schreiben
bulk_index_to_elasticsearch(products)

# Batch-Commit
consumer.commit()
```

### 3. Streamlit Caching

```python
@st.cache_data(ttl=60, show_spinner=False)
def fetch_opportunities(min_margin):
    return api.get_opportunities(min_margin=min_margin)

# Wird nur alle 60s neu geladen
opportunities = fetch_opportunities(min_margin)
```

## Zusammenfassung der Architektur-Entscheidungen

| **Entscheidung** | **Begründung** | **Alternativen** |
|------------------|----------------|------------------|
| **Kafka** | Entkopplung, Skalierbarkeit | RabbitMQ, Redis Streams |
| **Elasticsearch** | Schnelle Suche, Analytics | MongoDB, PostgreSQL |
| **FastAPI** | Performance, Auto-Docs | Flask, Django |
| **Streamlit** | Schnelle UI-Entwicklung | React, Vue.js |
| **Docker** | Portabilität, Isolation | VMs, Kubernetes |
| **Airflow** | Workflow-Management | Cron, Luigi |
| **Poetry** | Moderne Dependencies | pip, Pipenv |

## System-Metriken (Aktuell)

```
Services:        13 Container
Produkte:        ~8 in Elasticsearch
Kafka Topics:    3 (raw, enriched, alerts)
API Endpoints:   5 (/health, /products, /products/{asin}, /opportunities, /stats)
Update-Interval: 60 Sekunden
Keepa-Limit:     20 Tokens/Minute
```

## Nächste Schritte (Erweiterungen)

1. **Preis-Historie visualisieren** (Charts mit Plotly)
2. **E-Mail-Alerts** bei neuen High-Margin Opportunities
3. **Multi-Domain Support** (Preise aus allen EU-Märkten gleichzeitig)
4. **Machine Learning** (Preis-Prognosen)
5. **Product-Ranking** (Bestseller-Score)
6. **Competitor-Tracking** (Mehrere Seller pro Produkt)
