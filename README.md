# Amazon Arbitrage Price Tracker

A 3-day Data Engineering project for detecting arbitrage opportunities between European Amazon marketplaces.

## Quick Start

```bash
# 1. Clone and enter directory
cd arbitrage-tracker

# 2. Copy environment file
cp .env.example .env

# 3. Edit .env and add your Keepa API key
#    Get one at https://keepa.com/#/api
nano .env

# 4. Start all services
docker-compose up -d

# 5. Check status
docker-compose ps

# 6. Access the dashboard
#    http://localhost:8501
```

## Architecture

```
Keepa API → Producer → Kafka → Enrichment → Elasticsearch
                                        ↓
                                    FastAPI → Streamlit Dashboard
```

## Project Structure

```
arbitrage-tracker/
├── docker-compose.yml          # All services
├── README.md                   # This file
├── ARCHITECTURE.md             # System architecture
├── docs/
│   ├── API_CONTRACT.md         # REST API specification
│   ├── KAFKA_CONTRACT.md       # Kafka topics and message formats
│   ├── ELASTICSEARCH_SCHEMA.md # ES index configuration
│   └── WORKER_TASKS.md         # Task assignments for agents
├── src/
│   ├── producer/               # Data ingestion (Keepa → Kafka)
│   ├── consumer/               # Data enrichment (Kafka → ES)
│   ├── arbitrage/              # Opportunity detection
│   ├── api/                    # REST API (FastAPI)
│   └── dashboard/              # UI (Streamlit)
├── tests/
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
└── config/
    └── watchlist.txt           # ASINs to monitor
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Elasticsearch | 9200 | Product database |
| Kibana | 5601 | ES visualization (optional) |
| Kafka | 9092 | Message queue |
| API | 8000 | REST API |
| Dashboard | 8501 | Web UI |

## API Endpoints

```bash
# Get arbitrage opportunities
curl http://localhost:8000/arbitrage?min_margin=20

# List products
curl http://localhost:8000/products?page=1&page_size=20

# Health check
curl http://localhost:8000/health
```

## Development

### Without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Start Elasticsearch and Kafka manually, then:
python -m src.producer.main
python -m src.consumer.main
python -m src.api.main
streamlit run src/dashboard/app.py
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## Team Workflow

### Daily Standup (10 min)

Each worker reports:
1. **Yesterday**: Completed tasks
2. **Today**: Current task
3. **Blockers**: Dependencies blocked
4. **Help**: What you need

### Task Tracking

See `docs/WORKER_TASKS.md` for detailed task assignments. Each task has:
- Clear inputs/outputs
- Dependencies
- Acceptance criteria
- Definition of done

### Communication Protocol

1. **Blocker detected?** → Create issue in tracker
2. **Task complete?** → Mark "ready for review"
3. **Review done?** → Accept and mark complete

## Key Files for Reference

| File | Purpose |
|------|---------|
| `docs/API_CONTRACT.md` | REST API contract (binding for API/Dashboard workers) |
| `docs/KAFKA_CONTRACT.md` | Kafka topics and message schemas (binding for Producer/Consumer) |
| `docs/ELASTICSEARCH_SCHEMA.md` | ES index mapping (binding for Consumer/API workers) |
| `docs/WORKER_TASKS.md` | Detailed task breakdown for each worker |

## Troubleshooting

### Kafka not starting
```bash
docker-compose logs kafka
# Check if Zookeeper is running first
```

### Elasticsearch connection refused
```bash
# ES takes time to start
docker-compose logs elasticsearch
# Wait for "health green" message
```

### No data in dashboard
```bash
# Check if topics have messages
docker-compose exec kafkacat kafkacat -b kafka:9092 -L

# Check producer logs
docker-compose logs producer
```

## Learning Outcomes

This project demonstrates:
- Apache Kafka for event streaming
- Elasticsearch for full-text search and aggregations
- FastAPI for REST API development
- Streamlit for rapid prototyping
- Docker Compose for container orchestration
- Multi-worker collaboration patterns

## License

MIT
