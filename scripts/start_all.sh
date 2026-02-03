#!/bin/bash
# Start Complete System with all services

cd "$(dirname "$0")/.."

echo "🚀 Starting Arbitrage Tracker System..."

# 1. Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env not found! Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env and add your KEEPA_API_KEY!"
    exit 1
fi

# 2. Check if KEEPA_API_KEY is set
if ! grep -q "KEEPA_API_KEY=" .env || grep -q "KEEPA_API_KEY=$" .env; then
    echo "⚠️  KEEPA_API_KEY not set in .env!"
    echo "📝 Please edit .env and add your API key!"
    exit 1
fi

# 3. Stop existing containers
echo "🛑 Stopping existing containers..."
sudo docker-compose down -v --remove-orphans 2>/dev/null

# 4. Build all services
echo "🔨 Building all services..."
sudo docker-compose build --no-cache

# 5. Start data stores
echo "📦 Starting data stores (Elasticsearch, Kafka, Zookeeper)..."
sudo docker-compose up -d zookeeper elasticsearch kafka

# 6. Wait for Elasticsearch
echo "⏳ Waiting for Elasticsearch..."
for i in {1..30}; do
    if curl -s http://localhost:9200/_cluster/health | grep -q '"status":"green\|yellow"'; then
        echo "✅ Elasticsearch is ready!"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 2
done

# 7. Start all other services
echo "🚀 Starting application services..."
sudo docker-compose up -d enrichment-consumer arbitrage-detector api dashboard init-topics

# 8. Start producer (last, needs Kafka)
echo "📡 Starting producer..."
sudo docker-compose up -d producer

# 9. Show status
echo ""
echo "✅ All services started!"
echo ""
echo "📊 Dashboard:     http://localhost:8501"
echo "🔌 API Docs:      http://localhost:8000/docs"
echo "🔍 Elasticsearch: http://localhost:9200"
echo ""
echo "📋 To see logs:"
echo "   sudo docker logs -f arbitrage-producer"
