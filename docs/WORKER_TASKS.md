# Worker Tasks - Multi-Agent Task Assignment

## Overview

This document defines the specific tasks for each worker/agent in the arbitrage tracking system. Each task is self-contained with clear inputs, outputs, and dependencies.

---

## Task Assignment Summary

| Worker | Primary Responsibility | Dependencies | Est. Hours |
|--------|------------------------|--------------|------------|
| **Producer Worker** | Data ingestion from Keepa API | Kafka, Keepa API | 6h |
| **Enrichment Worker** | Data transformation & ES indexing | Kafka, Elasticsearch | 4h |
| **Arbitrage Worker** | Margin calculation & alerts | Elasticsearch | 4h |
| **API Worker** | REST API development | Elasticsearch, Kafka | 6h |
| **Dashboard Worker** | Streamlit UI development | API | 4h |

---

## Worker 1: Producer (Data Ingestion)

### Task 1.1: Keepa API Client Implementation
```
ID: PRODUCER-1
Task: Implement Keepa API client
Priority: HIGH
Estimated Time: 2 hours

Inputs:
  - Keepa API Key (env: KEEPA_API_KEY)
  - Keepa API documentation

Outputs:
  - src/producer/keepa_client.py
  - Tests: tests/unit/test_keepa_client.py

Requirements:
  [ ] Authentication with API key
  [ ] Product query endpoint (GET /product)
  [ ] Best sellers endpoint (GET /category/{categoryId}/bestsellers)
  [ ] Price history endpoint (GET /priceHistory)
  [ ] Rate limiting handling (100 requests/minute free tier)
  [ ] Error handling and retries

Dependencies:
  - None (foundational)

Acceptance Criteria:
  [ ] Can fetch product data for any ASIN
  [ ] Handles API rate limits gracefully
  [ ] Unit tests cover main functionality
  [ ] Type hints on all public methods

Definition of Done:
  - [ ] Code reviewed
  - [ ] Tests passing (pytest)
  - [ ] Type checked (mypy)
  - [ ] Documented (docstrings)
```

### Task 1.2: Kafka Producer Implementation
```
ID: PRODUCER-2
Task: Implement Kafka producer for raw updates
Priority: HIGH
Estimated Time: 2 hours

Inputs:
  - Running Kafka instance (kafka:9092)
  - Keepa client from PRODUCER-1
  - Kafka topic: raw.keepa_updates

Outputs:
  - src/producer/kafka_producer.py
  - src/producer/main.py
  - Tests: tests/unit/test_kafka_producer.py

Requirements:
  [ ] Connect to Kafka cluster
  [ ] Serialize messages as JSON
  [ ] Partition by ASIN hash (consistent ordering)
  [ ] Batch sending for efficiency
  [ ] Delivery guarantees (at-least-once)
  [ ] Error handling and dead letter queue

Code Structure:
  ```python
  class KeepaKafkaProducer:
      def __init__(self, bootstrap_servers: str, topic: str):
          ...

      def send_product_update(self, product_data: dict) -> None:
          """Send single product update to Kafka"""
          ...

      def send_batch(self, products: List[dict]) -> None:
          """Send batch of product updates"""
          ...
  ```

Dependencies:
  - PRODUCER-1 (Keepa client)

Acceptance Criteria:
  [ ] Messages published to correct topic
  [ ] Partitioning ensures per-ASIN ordering
  [ ] Handles broker unavailability
  [ ] Unit tests with mocked Kafka
```

### Task 1.3: Main Loop and Watchlist Management
```
ID: PRODUCER-3
Task: Implement main polling loop
Priority: MEDIUM
Estimated Time: 2 hours

Inputs:
  - ASIN watchlist (env: ASIN_WATCHLIST or config file)
  - Poll interval (env: POLL_INTERVAL_SECONDS, default: 300)

Outputs:
  - src/producer/main.py (updated)
  - config/producer.yaml

Requirements:
  [ ] Load and manage ASIN watchlist
  [ ] Poll Keepa API at configured interval
  [ ] Handle new ASIN additions at runtime
  [ ] Graceful shutdown on SIGTERM/SIGINT
  [ ] Metrics: messages sent, errors, latency

Configuration:
  ```yaml
  producer:
    poll_interval_seconds: 300
    batch_size: 20
    retry_attempts: 3
    retry_delay_seconds: 5

  watchlist:
    source: file  # or env
    path: config/watchlist.txt
  ```

Dependencies:
  - PRODUCER-1, PRODUCER-2

Acceptance Criteria:
  [ ] Polls at correct interval
  [ ] Handles watchlist changes
  [ ] Proper signal handling
  [ ] Logs metrics to stdout
```

---

## Worker 2: Enrichment Consumer

### Task 2.1: Kafka Consumer Implementation
```
ID: ENRICHMENT-1
Task: Implement Kafka consumer for raw updates
Priority: HIGH
Estimated Time: 1.5 hours

Inputs:
  - Kafka topic: raw.keepa_updates
  - Consumer group: enrichment-consumer

Outputs:
  - src/consumer/kafka_consumer.py
  - Tests: tests/unit/test_enrichment_consumer.py

Requirements:
  [ ] Consume from Kafka topic
  [ ] Manual offset commit (at-least-once)
  [ ] Handle rebalancing
  [ ] Error handling with dead letter queue
  [ ] Metrics: messages consumed, processing time

Dependencies:
  - Kafka running (from docker-compose)

Acceptance Criteria:
  [ ] Consumes messages from raw.keepa_updates
  [ ] Commits offsets correctly
  [ ] Handles consumer group rebalance
  [ ] Logs processing metrics
```

### Task 2.2: Data Enrichment Logic
```
ID: ENRICHMENT-2
Task: Implement product data enrichment
Priority: HIGH
Estimated Time: 2 hours

Inputs:
  - Raw Keepa data from Kafka
  - Marketplace configuration

Outputs:
  - src/consumer/enricher.py
  - src/consumer/models.py

Requirements:
  [ ] Convert Keepa price format (cents to EUR)
  [ ] Normalize marketplace codes (Keepa ID → DE/IT/ES/UK/FR)
  [ ] Calculate derived fields (avg_price, price_trend)
  [ ] Merge data for same ASIN from multiple marketplaces
  [ ] Add timestamp and metadata

Code Structure:
  ```python
  class ProductEnricher:
      KEEPA_DOMAIN_MAP = {
          1: "DE",  # Amazon.de
          3: "UK",  # Amazon.co.uk
          5: "IT",  # Amazon.it
          6: "ES",  # Amazon.es
          8: "FR",  # Amazon.fr
      }

      def enrich(self, raw_data: dict) -> EnrichedProduct:
          """Transform raw Keepa data to canonical format"""
          ...

      def merge_updates(self, existing: dict, new: dict) -> dict:
          """Merge new data with existing product"""
          ...
  ```

Dependencies:
  - ENRICHMENT-1

Acceptance Criteria:
  [ ] Correct price conversion (cents → EUR)
  [ ] All marketplaces mapped correctly
  [ ] Merge strategy handles partial updates
  [ ] Unit tests with sample data
```

### Task 2.3: Elasticsearch Indexer
```
ID: ENRICHMENT-3
Task: Implement Elasticsearch indexing
Priority: HIGH
Estimated Time: 1.5 hours

Inputs:
  - Enriched product data
  - Elasticsearch index: products

Outputs:
  - src/consumer/indexer.py
  - Tests: tests/integration/test_elasticsearch.py

Requirements:
  [ ] Connect to Elasticsearch
  [ ] Upsert products by ASIN (idempotent)
  [ ] Update price history (append only, limit to 30 days)
  [ ] Refresh index after writes
  [ ] Handle connection failures

Code Structure:
  ```python
  class ElasticsearchIndexer:
      def __init__(self, host: str, index: str):
          ...

      def upsert_product(self, product: dict) -> None:
          """Upsert product to Elasticsearch"""
          ...

      def update_price_history(self, asin: str, price_data: dict) -> None:
          """Append price to history"""
          ...
  ```

Dependencies:
  - ENRICHMENT-2
  - ES schema (docs/ELASTICSEARCH_SCHEMA.md)

Acceptance Criteria:
  [ ] Products indexed with correct mapping
  [ ] Upsert preserves existing data
  [ ] Price history properly maintained
  [ ] Integration test against real ES
```

---

## Worker 3: Arbitrage Detector

### Task 3.1: Margin Calculation Engine
```
ID: ARBITRAGE-1
Task: Implement arbitrage margin calculation
Priority: HIGH
Estimated Time: 2 hours

Inputs:
  - Product data from Elasticsearch
  - Fee configuration (Amazon FBA fees ~15%)

Outputs:
  - src/arbitrage/calculator.py
  - Tests: tests/unit/test_calculator.py

Requirements:
  [ ] Calculate margin: (target_price - source_price) / target_price * 100
  [ ] Calculate profit: target_price - source_price
  [ ] Calculate net profit: profit - fees
  [ ] Find best source market for each product
  [ ] Confidence scoring based on price stability

Formulas:
  ```python
  gross_margin = (target_price - source_price) / target_price * 100
  gross_profit = target_price - source_price
  estimated_fees = target_price * 0.15  # FBA fee estimate
  net_profit = gross_profit - estimated_fees
  confidence = 1.0 - (price_volatility / avg_price)

  # Confidence levels
  HIGH: confidence >= 0.9
  MEDIUM: confidence >= 0.7
  LOW: confidence < 0.7
  ```

Dependencies:
  - None (can work with sample data)

Acceptance Criteria:
  [ ] Correct margin/profit calculations
  [ ] Fee estimates configurable
  [ ] Confidence scoring implemented
  [ ] Unit tests with known inputs/outputs
```

### Task 3.2: Opportunity Detection
```
ID: ARBITRAGE-2
Task: Implement opportunity detection logic
Priority: HIGH
Estimated Time: 1 hour

Inputs:
  - All products from Elasticsearch
  - Threshold: min_margin (default: 15%)

Outputs:
  - src/arbitrage/detector.py
  - src/arbitrage/models.py

Requirements:
  [ ] Query Elasticsearch for all active products
  [ ] Calculate margins for all marketplace pairs
  [ ] Filter by minimum margin threshold
  [ ] Rank opportunities by margin/profit
  [ ] Emit alerts for high-priority opportunities

Opportunity Ranking:
  ```
  Priority Score = margin_weight * margin + profit_weight * normalized_profit

  Where:
  - margin_weight = 0.6
  - profit_weight = 0.4
  - normalized_profit = profit / max_profit_in_dataset
  ```

Dependencies:
  - ARBITRAGE-1
  - ES schema

Acceptance Criteria:
  [ ] Finds all opportunities above threshold
  [ ] Correctly ranks by priority
  [ ] Configurable threshold
  [ ] Efficient query (aggregations preferred)
```

### Task 3.3: Kafka Alert Publisher
```
ID: ARBITRAGE-3
Task: Implement Kafka alert publishing
Priority: MEDIUM
Estimated Time: 1 hour

Inputs:
  - Detected opportunities
  - Kafka topic: arbitrage.alerts

Outputs:
  - src/arbitrage/publisher.py

Requirements:
  [ ] Connect to Kafka
  [ ] Publish alerts with unique ID (UUID)
  [ ] Include all relevant metadata
  [ ] Handle publish failures

Dependencies:
  - ARBITRAGE-2

Acceptance Criteria:
  [ ] Alerts published to correct topic
  [ ] Each alert has unique ID
  [ ] Alert format matches KAFKA_CONTRACT.md
  [ ] Retry on failure
```

---

## Worker 4: API Developer

### Task 4.1: FastAPI Setup and Configuration
```
ID: API-1
Task: Set up FastAPI project structure
Priority: HIGH
Estimated Time: 1 hour

Inputs:
  - OpenAPI contract (docs/API_CONTRACT.md)

Outputs:
  - src/api/main.py
  - src/api/routes/products.py
  - src/api/routes/arbitrage.py
  - src/api/routes/health.py
  - Tests: tests/api/

Requirements:
  [ ] Initialize FastAPI app with OpenAPI
  [ ] Configure CORS for dashboard origin
  [ ] Error handling middleware
  [ ] Request logging
  [ ] Health check endpoint

Code Structure:
  ```python
  # src/api/main.py
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware

  app = FastAPI(
      title="Amazon Arbitrage Tracker API",
      version="1.0.0",
      docs_url="/docs",
      redoc_url="/redoc"
  )

  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_methods=["*"],
      allow_headers=["*"],
  )

  # Include routers
  from src.api.routes import products, arbitrage, health
  app.include_router(products.router, prefix="/products", tags=["Products"])
  app.include_router(arbitrage.router, prefix="/arbitrage", tags=["Arbitrage"])
  app.include_router(health.router, prefix="/health", tags=["Health"])
  ```

Dependencies:
  - None (foundational)

Acceptance Criteria:
  [ ] API starts successfully
  [ ] OpenAPI spec generated
  [ ] CORS configured
  [ ] Health endpoint returns service status
```

### Task 4.2: Products Endpoints
```
ID: API-2
Task: Implement products API endpoints
Priority: HIGH
Estimated Time: 2.5 hours

Inputs:
  - Elasticsearch client
  - OpenAPI spec for /products

Outputs:
  - src/api/routes/products.py
  - src/api/dependencies.py (ES client)

Requirements:
  [ ] GET /products (list with pagination, filters)
  [ ] GET /products/{asin} (detail)
  [ ] GET /products/watch (get watchlist)
  [ ] POST /products/watch (add to watchlist)
  [ ] Query Elasticsearch efficiently
  [ ] Transform ES response to API schema

Query Parameters:
  ```python
  class ProductListParams:
      page: int = Query(1, ge=1)
      page_size: int = Query(20, ge=1, le=100)
      marketplace: Optional[str] = Query(None, regex="^(DE|IT|ES|UK|FR)$")
      min_margin: float = Query(0, ge=0, le=100)
      max_price: Optional[float] = Query(None, ge=0)
      category: Optional[str] = None
      sort_by: str = Query("updated_desc", regex="^(margin|price|updated)_(desc|asc)$")
  ```

Dependencies:
  - API-1
  - ES schema

Acceptance Criteria:
  [ ] All endpoints match API contract
  [ ] Pagination works correctly
  [ ] Filters applied to ES query
  [ ] Response matches schema
  [ ] Error handling (404, 400)
```

### Task 4.3: Arbitrage Endpoints
```
ID: API-3
Task: Implement arbitrage API endpoints
Priority: HIGH
Estimated Time: 2 hours

Inputs:
  - Elasticsearch client
  - OpenAPI spec for /arbitrage

Outputs:
  - src/api/routes/arbitrage.py

Requirements:
  [ ] GET /arbitrage (list opportunities)
  [ ] GET /arbitrage/top (top N opportunities)
  [ ] Query with margin/profit filters
  [ ] Calculate summary statistics
  [ ] Cache responses (optional, Redis)

Dependencies:
  - API-1

Acceptance Criteria:
  [ ] All endpoints match API contract
  [ ] Filters correctly applied
  [ ] Summary statistics calculated
  [ ] Response matches schema
```

### Task 4.4: Service Health Checks
```
ID: API-4
Task: Implement comprehensive health checks
Priority: MEDIUM
Estimated Time: 0.5 hours

Inputs:
  - Elasticsearch, Kafka connections

Outputs:
  - src/api/routes/health.py

Requirements:
  [ ] Check Elasticsearch connectivity
  [ ] Check Kafka connectivity
  [ ] Check Keepa API status (optional)
  [ ] Return detailed status with response times

Dependencies:
  - API-1

Acceptance Criteria:
  [ ] All services checked
  [ ] Response times included
  [ ] Degraded state handled
```

---

## Worker 5: Dashboard Developer

### Task 5.1: Streamlit Setup
```
ID: DASH-1
Task: Set up Streamlit application
Priority: HIGH
Estimated Time: 0.5 hours

Inputs:
  - API base URL

Outputs:
  - src/dashboard/app.py
  - src/dashboard/config.py

Requirements:
  [ ] Initialize Streamlit app
  [ ] Configure API client
  [ ] Set up session state
  [ ] Page configuration

Code Structure:
  ```python
  # src/dashboard/app.py
  import streamlit as st
  import requests

  st.set_page_config(
      page_title="Amazon Arbitrage Tracker",
      page_icon="📈",
      layout="wide"
  )

  API_BASE_URL = st.secrets["api_base_url"]

  class APIClient:
      @staticmethod
      def get_products(params):
          return requests.get(f"{API_BASE_URL}/products", params=params)

      @staticmethod
      def get_arbitrage(params):
          return requests.get(f"{API_BASE_URL}/arbitrage", params=params)
  ```

Dependencies:
  - API running

Acceptance Criteria:
  [ ] App starts without errors
  [ ] API client configured correctly
  [ ] Session state initialized
```

### Task 5.2: Main Dashboard Layout
```
ID: DASH-2
Task: Implement main dashboard layout
Priority: HIGH
Estimated Time: 1.5 hours

Inputs:
  - API endpoints for products and arbitrage

Outputs:
  - src/dashboard/app.py (updated)

Requirements:
  [ ] Header with title and metrics summary
  [ ] Sidebar with filters (marketplace, margin, price)
  [ ] Main content area with data tables
  [ ] Auto-refresh capability
  [ ] Loading states

Layout:
  ```python
  st.title("📈 Amazon Arbitrage Tracker")

  # Sidebar filters
  with st.sidebar:
      st.header("Filters")
      target_marketplace = st.selectbox("Target Market", ["DE", "IT", "ES", "UK", "FR"])
      min_margin = st.slider("Min Margin %", 0, 100, 15)
      max_price = st.number_input("Max Price (€)", 0, 10000, 500)

  # Main content
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Total Products", stats["total"])
  col2.metric("Opportunities", stats["opportunities"])
  col3.metric("Avg Margin", f"{stats['avg_margin']:.1f}%")
  col4.metric("Best Profit", f"€{stats['best_profit']:.2f}")
  ```

Dependencies:
  - DASH-1

Acceptance Criteria:
  [ ] Clean, professional layout
  [ ] Filters work correctly
  [ ] Metrics displayed
  [ ] Auto-refresh button
```

### Task 5.3: Opportunities Table
```
ID: DASH-3
Task: Implement opportunities data table
Priority: HIGH
Estimated Time: 1 hour

Inputs:
  - GET /arbitrage endpoint

Outputs:
  - src/dashboard/app.py (updated)

Requirements:
  [ ] Display opportunities in AgGrid or Streamlit dataframe
  [ ] Columns: ASIN, Title, Source, Target, Price, Margin, Profit
  [ ] Sortable by any column
  [ ] Searchable by ASIN/title
  [ ] Link to Amazon product page

Dependencies:
  - DASH-2

Acceptance Criteria:
  [ ] Table displays all relevant data
  [ ] Sorting works
  [ ] Search filters results
  [ ] Clickable links to Amazon
```

### Task 5.4: Price History Charts
```
ID: DASH-4
Task: Implement price history visualization
Priority: MEDIUM
Estimated Time: 1 hour

Inputs:
  - Product detail endpoint with price history

Outputs:
  - src/dashboard/app.py (updated)

Requirements:
  [ ] Line chart for price history
  [ ] Multi-marketplace comparison
  [ ] Interactive chart (Plotly/Altair)
  [ ] Select product to view

Dependencies:
  - DASH-3

Acceptance Criteria:
  [ ] Chart displays correctly
  [ ] Multiple marketplaces shown
  [ ] Interactive tooltips
  [ ] Responsive design
```

---

## Integration Testing

### Task 6.1: End-to-End Integration Test
```
ID: TEST-1
Task: Run end-to-end integration test
Priority: HIGH
Estimated Time: 1 hour

Inputs:
  - All services running
  - Test ASIN list

Outputs:
  - tests/integration/test_e2e.py
  - Test report

Requirements:
  [ ] Producer sends test data
  [ ] Consumer processes and indexes
  [ ] Arbitrage detector finds opportunities
  [ ] API returns data
  [ ] Dashboard displays correctly

Test Steps:
  1. Start all services via docker-compose
  2. Producer fetches data for test ASINs
  3. Wait for processing (check ES)
  4. Query API for arbitrage opportunities
  5. Verify data in dashboard

Dependencies:
  - All tasks complete

Acceptance Criteria:
  [ ] All services healthy
  [ ] Data flows through entire pipeline
  [ ] Latency < 30 seconds end-to-end
  [ ] No errors in logs
```

---

## Communication Protocol

### Daily Standup Format
```
Each worker reports:
1. Yesterday: What I completed
2. Today: What I'm working on
3. Blockers: Any dependencies blocked
4. Help: What I need from others

Example:
- Producer: ✅ Keepa client done, working on Kafka producer (blocked by ES schema)
- Enrichment: ⏳ Waiting for Kafka topics to be created
- Arbitrage: ✅ Calculator done, can start testing with sample data
- API: ✅ FastAPI setup done, starting products endpoints
- Dashboard: ⏳ Waiting for API endpoints (blocked by API-2)
```

### Blocked Issues Protocol
1. Mark task as blocked in task tracker
2. Note which worker can unblock
3. Schedule sync call if critical path
4. Document workaround if available

### Handshake Protocol
When Worker A needs output from Worker B:
1. Worker A creates issue: "Need output from WORKER_B-X"
2. Worker B marks as "ready for review" when complete
3. Worker A reviews and accepts or requests changes
4. Both mark task complete in their tracker
