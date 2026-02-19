# Keeper System - Amazon Price Monitoring & Deal Finder

**Data Engineering Project** - End-to-end Data Pipeline with Kafka + Elasticsearch

## Architektur

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KEEPER SYSTEM                                        │
│                    Data Engineering Pipeline                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │  KEEPA API  │───▶│  KAFKA      │───▶│ CONSUMER    │───▶│ POSTGRESQL  │ │
│  │ (Scraping)  │    │  Producer   │    │             │    │  Database   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│                           │                                                │
│                           │              ┌─────────────┐                   │
│                           └─────────────▶│ELASTICSEARCH│                   │
│                                          │  (Analytics)│                   │
│                                          └─────────────┘                   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                        AGENT SYSTEM                                          │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                   │
│  │ Price Monitor │  │  Deal Finder  │  │Alert Dispatch│                   │
│  │    Agent      │  │    Agent      │  │    Agent     │                   │
│  └───────────────┘  └───────────────┘  └───────────────┘                   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                        FASTAPI REST API                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Engineering Features

### ✅ Three Pillars Architecture

1. **Scraping Layer** - Keepa API für Amazon Daten
2. **Processing Layer** - Kafka Producers/Consumers + Data Transformation
3. **Storage Layer** - PostgreSQL + Elasticsearch

### ✅ Apache Kafka Integration

- Topic: `price-updates` - Für Preis-Änderungen
- Topic: `deal-updates` - Für Deal-Daten
- Producer: Sendet Daten aus Scheduler
- Consumer: Verarbeitet und speichert in DB
- Consumer Groups für Skalierbarkeit

### ✅ Elasticsearch Integration

- Index: `keeper-prices` - Preis-Historie durchsuchbar
- Index: `keeper-deals` - Deals für Analytics
- Suchfunktionen mit Filtern
- Aggregations für Statistiken
- Kibana Visualisierung (Port 5601)

## Features

- **Preis-Überwachung**: Automatische Alerts bei Preis Drops
- **Deal-Finder**: Tägliche personalisierte Deal-Reports
- **Multi-Channel**: Email, Telegram, Discord Support
- **Analytics**: Volltext-Suche und Aggregations via Elasticsearch

## Quick Start

```bash
# 1. Environment kopieren
cp .env.example .env

# 2. API Keys eintragen
nano .env

# 3. Docker starten (inkl. Kafka, Elasticsearch, Kibana)
docker-compose up -d

# 4. Warten bis alle Services ready sind (~30s)
# 5. API testen
curl http://localhost:8000/health

# 6. Kibana für Analytics öffnen
# http://localhost:5601
```

## Services

| Service | Port | Beschreibung |
|---------|------|--------------|
| FastAPI | 8000 | REST API |
| PostgreSQL | 5432 | Primäre Datenbank |
| Redis | 6379 | Cache |
| Kafka | 9092 | Event Streaming |
| Zookeeper | 2181 | Kafka Coordination |
| Elasticsearch | 9200 | Suchmaschine |
| Kibana | 5601 | Visualisierung |

## Struktur

```
keeper-system/
├── prompts/              # Agent System Prompts
├── src/
│   ├── agents/           # Agent-Implementierungen
│   ├── services/         # Business Logic
│   │   ├── keepa_api.py          # Keepa API Client
│   │   ├── database.py           # SQLAlchemy Models
│   │   ├── notification.py       # Email/Telegram/Discord
│   │   ├── kafka_producer.py     # Kafka Producer ⭐
│   │   ├── kafka_consumer.py    # Kafka Consumer ⭐
│   │   └── elasticsearch_service.py  # ES Client ⭐
│   ├── api/              # REST Endpoints
│   └── scheduler.py      # Background Jobs + Pipeline
├── tests/                # Unit Tests
├── docker-compose.yml    # Alle Services
└── .env                  # Environment Variables
```

## API Endpoints

| Methode | Endpoint | Beschreibung |
|---------|----------|--------------|
| GET | /health | Health Check |
| POST | /api/v1/watches | Produkt überwachen |
| GET | /api/v1/watches | Alle watches abrufen |
| DELETE | /api/v1/watches/{id} | Watch löschen |
| POST | /api/v1/deals/search | Deals suchen |
| GET | /api/v1/reports/{id} | Report abrufen |

## Environment Variablen

| Variable | Beschreibung | Required |
|----------|--------------|----------|
| KEEPA_API_KEY | Keepa API Key | Yes |
| DEAL_SOURCE_MODE | Deal mode (`product_only`) | Yes |
| DEAL_SEED_ASINS | Optional inline ASIN seeds | No |
| DEAL_SEED_FILE | Fallback seed file path | No |
| DEAL_SCAN_INTERVAL_SECONDS | Collector interval in seconds | No |
| DEAL_SCAN_BATCH_SIZE | ASINs scanned per collector cycle | No |
| DATABASE_URL | PostgreSQL Connection | Yes |
| REDIS_URL | Redis Connection | Yes |
| KAFKA_BOOTSTRAP_SERVERS | Kafka Server | Yes |
| ELASTICSEARCH_URL | Elasticsearch URL | Yes |
| SMTP_HOST | Email Server | No |
| TELEGRAM_BOT_TOKEN | Telegram Bot Token | No |
| DISCORD_WEBHOOK | Discord Webhook URL | No |

## Data Pipeline Flow

```
1. Scheduler ruft Keepa API auf (alle 6h)
       │
       ▼
2. Preis-Daten werden geprüft
       │
       ├──────────────────┬──────────────────┐
       ▼                  ▼                  ▼
3. Kafka Producer   Elasticsearch     PostgreSQL
   (price-updates)  (keeper-prices)   (PriceHistory)
       │                  │                  │
       ▼                  ▼                  ▼
4. Kafka Consumer ──▶ Database ──▶ Alerts
```

## Automatic EU ASIN Discovery (No Manual List)

Use the script to discover keyboard ASINs directly via Keepa endpoints
(`query`, `search category`, `bestsellers`) and write a large seed file.

Keepa domain IDs used here:
- UK=`2`
- FR=`4`
- IT=`8`
- ES=`9`

```bash
# 1) Discover around 1000 QWERTZ-focused ASINs from UK/FR/IT/ES
python scripts/discover_eu_qwertz_asins.py \
  --api-key "$KEEPA_API_KEY" \
  --markets UK,FR,IT,ES \
  --seed-limit 1000 \
  --finder-pages 10 \
  --finder-per-page 600 \
  --max-categories 100 \
  --output-json data/seed_asins_eu_qwertz.json \
  --output-txt data/seed_asins_eu_qwertz.txt

# 2) Apply file-based seeds to .env automatically
python scripts/apply_seed_env.py \
  --seed-file data/seed_asins_eu_qwertz.txt \
  --env-file .env \
  --inline-limit 0
```

## Overnight Storage Run

```bash
# Start pipeline services
docker-compose up -d db redis kafka elasticsearch scheduler

# Check scheduler logs
docker-compose logs -f scheduler

# The collector rotates through the seed list via offset each cycle, so large
# seed files (e.g. 1000 ASINs) are processed over time.

# Optional: speed up overnight fill rate (scan more ASINs per cycle)
# DEAL_SCAN_INTERVAL_SECONDS=300 and DEAL_SCAN_BATCH_SIZE=50 is a safe default.

# Verify PostgreSQL growth (inside db container)
docker-compose exec db psql -U postgres -d keeper -c "SELECT count(*) FROM collected_deals;"

# Verify Elasticsearch growth (correct index name is keeper-deals)
curl -s "http://localhost:9200/keeper-deals/_count" | python3 -m json.tool
```

## Testing

```bash
# Tests ausführen
pytest

# Mit Coverage
pytest --cov=src
```

##Lizenz

MIT
