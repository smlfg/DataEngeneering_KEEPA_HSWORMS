# Project: Amazon Arbitrage Price Tracker
# Purpose: Detect arbitrage opportunities between European Amazon marketplaces
# Duration: 3 days (24 hours)
# Team Size: 2-4 parallel workers

## Architecture Overview
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL SERVICES                               │
├───────────────┬───────────────┬───────────────┬───────────────┬─────────────┤
│   Keepa API   │   Amazon DE   │   Amazon IT   │   Amazon ES   │   Amazon UK │
│  (Preisdaten) │   (Zielmarkt) │   (Quelle)    │   (Quelle)    │   (Quelle)  │
└───────┬───────┴───────┬───────┴───────┬───────┴───────┬───────┴──────┬────────┘
        │               │               │               │              │
        ▼               ▼               ▼               ▼              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              KAFKA CLUSTER                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐   │
│  │ Topic: raw      │  │ Topic: products │  │ Topic: arbitrage_alerts     │   │
│  │ - keepa_updates │  │ - enriched_prod │  │ - high_margin_opps          │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
        │               │               │
        ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CONSUMERS / WORKERS                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐   │
│  │ Producer        │  │ Enrichment      │  │ Arbitrage Detector          │   │
│  │ (Worker 1)      │  │ Consumer        │  │ (Worker 2)                  │   │
│  │ Responsibility: │  │ Responsibility: │  │ Responsibility:             │   │
│  │ - Fetch from    │  │ - Transform     │  │ - Calculate margins         │   │
│  │   Keepa API     │  │ - Add metadata  │  │ - Detect opportunities      │   │
│  │ - Publish to    │  │ - Index to ES   │  │ - Publish alerts            │   │
│  │   raw_updates   │  │                 │  │                             │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
        │               │
        ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA STORES                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                    ELASTICSEARCH CLUSTER                             │     │
│  │  Index: products                                                     │     │
│  │  - price_history[]                                                   │     │
│  │  - current_prices{DE, IT, ES, UK}                                    │     │
│  │  - arbitrage_scores[]                                                │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                         FASTAPI                                      │     │
│  │  Endpoints:                                                          │     │
│  │  GET  /products         → List products with filters                 │     │
│  │  GET  /products/{asin}  → Product details                            │     │
│  │  GET  /arbitrage        → List arbitrage opportunities               │     │
│  │  POST /products/watch   → Add ASIN to watchlist                      │     │
│  │  GET  /health           → Service health check                       │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                       STREAMLIT DASHBOARD                            │     │
│  │  Features:                                                           │     │
│  │  - Top Arbitrage Opportunities (table)                               │     │
│  │  - Price History Charts                                              │     │
│  │  - Country Filter                                                    │     │
│  │  - Margin Slider                                                     │     │
│  │  - Refresh Button                                                    │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology Stack
| Layer          | Technology      | Purpose                           | Port |
|----------------|-----------------|-----------------------------------|------|
| Message Queue  | Apache Kafka 7.5| Event streaming                   | 9092 |
| Database       | Elasticsearch 8.11| Product storage & search         | 9200 |
| API            | FastAPI (Python)| REST API                          | 8000 |
| Frontend       | Streamlit       | Dashboard UI                      | 8501 |
| Orchestration  | Docker Compose  | Container management              | -    |
| Monitoring     | Kafkacat        | Debugging                         | -    |

## Data Flow
```
1. Producer fetches price data from Keepa API every X minutes
2. Raw prices → Kafka topic 'raw.keepa_updates'
3. Enrichment Consumer:
   - Receives raw updates
   - Transforms to canonical product format
   - Upserts to Elasticsearch
   - Publishes to 'products.enriched'
4. Arbitrage Detector:
   - Consumes enriched products
   - Calculates cross-market margins
   - Publishes high-margin items to 'arbitrage.alerts'
5. FastAPI exposes Elasticsearch data via REST
6. Streamlit queries API for dashboard display
```

## Sprints (8h each)
- **Day 1**: Infrastructure + Producer + Kafka + Basic ES
- **Day 2**: Enrichment Consumer + API + Arbitrage Logic
- **Day 3**: Dashboard + Testing + Documentation
