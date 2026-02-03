#!/bin/bash
# Complete Reset and Start - Fixes all issues and starts system
# Usage: ./scripts/reset_start.sh

cd "$(dirname "$0")/.."

echo "🔄 COMPLETE SYSTEM RESET & START"
echo "================================="
echo ""

# Step 1: Check .env
echo "1️⃣  Checking .env..."
if [ ! -f .env ]; then
    echo "   Creating .env from template..."
    cp .env.example .env
    echo "   ⚠️  Please edit .env and add KEEPA_API_KEY!"
    exit 1
fi

if ! grep -q "KEEPA_API_KEY=" .env || grep -q "KEEPA_API_KEY=$" .env 2>/dev/null; then
    echo "   ⚠️  KEEPA_API_KEY not set in .env!"
    exit 1
fi
echo "   ✅ .env OK"

# Step 2: Fix imports
echo ""
echo "2️⃣  Fixing import paths..."
sed -i 's/from keepa_client/from producer.keepa_client/g' src/producer/main.py
sed -i 's/from kafka_producer/from producer.kafka_producer/g' src/producer/main.py
sed -i 's/from kafka_consumer/from consumer.kafka_consumer/g' src/consumer/main.py
sed -i 's/from enricher/from consumer.enricher/g' src/consumer/main.py
sed -i 's/from indexer/from consumer.indexer/g' src/consumer/main.py
sed -i 's/from indexer/from consumer.indexer/g' src/arbitrage/main.py
sed -i 's/from calculator/from arbitrage.calculator/g' src/arbitrage/main.py
sed -i 's/from detector/from arbitrage.detector/g' src/arbitrage/main.py
echo "   ✅ Imports fixed"

# Step 3: Stop all containers
echo ""
echo "3️⃣  Stopping all containers..."
sudo docker-compose down -v --remove-orphans 2>/dev/null
echo "   ✅ All containers stopped"

# Step 4: Build all images fresh
echo ""
echo "4️⃣  Building all images (this takes a few minutes)..."
sudo docker-compose build --no-cache
echo "   ✅ All images built"

# Step 5: Start data stores
echo ""
echo "5️⃣  Starting data stores..."
sudo docker-compose up -d zookeeper elasticsearch kafka
echo "   Waiting for services..."

# Wait for Elasticsearch
for i in {1..30}; do
    if curl -s http://localhost:9200/_cluster/health 2>/dev/null | grep -q '"status":"green\|yellow"'; then
        echo "   ✅ Elasticsearch ready!"
        break
    fi
    echo "   ⏳ Waiting... ($i/30)"
    sleep 2
done

# Step 6: Start all other services
echo ""
echo "6️⃣  Starting application services..."
sudo docker-compose up -d enrichment-consumer arbitrage-detector api dashboard init-topics

# Step 7: Start producer
echo ""
echo "7️⃣  Starting producer..."
sudo docker-compose up -d producer

# Final status
echo ""
echo "=========================================="
echo "✅ SYSTEM STARTED SUCCESSFULLY!"
echo "=========================================="
echo ""
echo "🌐 Access Points:"
echo "   📊 Dashboard:     http://localhost:8501"
echo "   🔌 API Docs:      http://localhost:8000/docs"
echo "   🔍 Elasticsearch: http://localhost:9200"
echo ""
echo "📜 Useful Commands:"
echo "   ./scripts/status.sh     - Check system status"
echo "   ./scripts/logs.sh producer - See producer logs"
echo "   ./scripts/stop_all.sh   - Stop everything"
