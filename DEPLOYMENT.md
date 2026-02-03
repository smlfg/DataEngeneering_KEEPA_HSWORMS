# Deployment Guide - Amazon Arbitrage Tracker

## Overview

This document describes how to deploy and run the Amazon Arbitrage Tracker system. The system uses Docker Compose for orchestration and includes Apache Airflow for workflow management.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose V2
- At least 8GB RAM available for containers
- Keepa API Key (get one at https://keepa.com/#/api)

## Quick Start

### 1. Clone and Setup

```bash
cd ~/Dokumente/WS2025/DataEnge/arbitrage-tracker

# Copy environment file
cp .env.example .env

# Edit .env and add your Keepa API key
nano .env
```

### 2. Configure Environment

Edit `.env` and set:
- `KEEPA_API_KEY`: Your Keepa API key
- `CATEGORY_MODE`: true/false (use category mode or watchlist)
- Other settings as needed

### 3. Start the System

```bash
# Start all services (includes Airflow initialization)
docker compose up -d

# Or for faster startup (skip Airflow init)
docker compose up -d elasticsearch kafka zookeeper api dashboard
```

### 4. Verify Services

```bash
# Check running containers
docker compose ps

# Check API health
curl http://localhost:8000/health/

# Check Elasticsearch
curl http://localhost:9200/_cluster/health
```

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Dashboard | http://localhost:8501 | None |
| API Docs | http://localhost:8000/docs | None |
| Airflow UI | http://localhost:8080 | admin/admin |
| Kibana | http://localhost:5601 | None |
| Elasticsearch | http://localhost:9200 | None |

## Airflow Setup

### First Time Initialization

```bash
# Initialize Airflow database and create admin user
docker compose run airflow-init

# Or if already initialized, just start the services
docker compose up -d airflow-webserver airflow-scheduler airflow-worker
```

### Airflow DAGs

The main DAG is located at `dags/keepa_arbitrage_pipeline.py` and includes:

1. **determine_fetch_mode** - Decides between Category Mode and ASIN Watchlist
2. **fetch_asins_category/watchlist** - Gets ASINs from Keepa
3. **deduplicate_asins** - Removes duplicates
4. **check_rate_limits** - Verifies Keepa API limits
5. **batch_asins** - Creates batches for processing
6. **fetch_prices_batch_{N}** - Fetches prices for each batch
7. **push_to_kafka** - Publishes to Kafka
8. **verify_index** - Verifies Elasticsearch indexing

### Trigger DAG Manually

```bash
# Via Airflow CLI
docker exec arbitrage-airflow-webserver airflow dags unpause keepa_arbitrage_pipeline
docker exec arbitrage-airflow-webserver airflow dags trigger keepa_arbitrage_pipeline
```

## Production Deployment

### 1. Environment Variables

For production, use a secure `.env` file:

```bash
# Generate secure Fernet key for Airflow
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to .env
AIRFLOW_FERNET_KEY=your_generated_key
```

### 2. Resource Allocation

Update `docker-compose.yml` for production:

```yaml
services:
  elasticsearch:
    environment:
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data

  kafka:
    environment:
      - KAFKA_NUM_PARTITIONS=6
      - KAFKA_LOG_RETENTION_HOURS=720
```

### 3. Monitoring

```bash
# View all logs
docker compose logs -f

# View specific service
docker compose logs -f arbitrage-producer

# View metrics
docker stats
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs arbitrage-producer

# Remove and rebuild
docker compose rm -f arbitrage-producer
docker compose build arbitrage-producer
docker compose up -d arbitrage-producer
```

### Kafka Connection Issues

```bash
# Restart Kafka
docker compose restart kafka zookeeper

# Check Kafka health
docker exec arbitrage-kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

### Elasticsearch Not Healthy

```bash
# Check ES logs
docker logs arbitrage-elasticsearch

# Reset ES data
docker compose down -v
docker compose up -d elasticsearch
```

### Airflow Webserver Not Starting

```bash
# Check initialization
docker logs arbitrage-airflow-init

# Re-run init
docker compose rm -f airflow-init
docker compose run airflow-init
```

## Scaling

### Horizontal Scaling

```bash
# Add more workers
docker compose up -d --scale airflow-worker=3
```

### Kafka Partition Scaling

```bash
# Increase partitions (requires topic recreation)
docker exec arbitrage-kafka kafka-topics.sh --bootstrap-server localhost:9092 \
  --alter --topic raw.keepa_updates --partitions 6
```

## Backup and Restore

### Elasticsearch Backup

```bash
# Create snapshot repository
curl -X PUT "localhost:9200/_snapshot/arbitrage_backup" \
  -H 'Content-Type: application/json' \
  -d '{"type": "fs", "settings": {"location": "/usr/share/elasticsearch/backups"}}'

# Take snapshot
curl -X PUT "localhost:9200/_snapshot/arbitrage_backup/snapshot_1?wait_for_completion=true"
```

### Restore from Snapshot

```bash
curl -X POST "localhost:9200/_snapshot/arbitrage_backup/snapshot_1/_restore"
```

## Security Considerations

1. **Change default passwords** in `.env`:
   - `AIRFLOW__WEBSERVER__RBAC=true` with secure credentials
   - Postgres password for Airflow

2. **Enable TLS** for Kafka in production

3. **Use secrets management** (Docker Swarm secrets, Vault, etc.)

4. **Network isolation**: Use custom networks and firewall rules

## File Structure

```
arbitrage-tracker/
├── docker-compose.yml          # Main orchestration file
├── .env                        # Environment variables (git-ignored)
├── dags/                       # Airflow DAGs
│   └── keepa_arbitrage_pipeline.py
├── config/                     # Configuration files
│   ├── categories.yaml         # Category mode config
│   └── watchlist.txt           # ASIN watchlist
├── src/                        # Source code
│   ├── producer/               # Data ingestion
│   ├── consumer/               # Data processing
│   ├── arbitrage/              # Opportunity detection
│   ├── api/                    # REST API
│   └── dashboard/              # Streamlit UI
├── logs/                       # Airflow logs
├── tests/                      # Unit tests
└── scripts/                    # Helper scripts
```

## Support

- **GitHub Issues**: Report bugs and feature requests
- **Airflow Documentation**: https://airflow.apache.org/docs/
- **Keepa API**: https://keepa.com/#/docs
