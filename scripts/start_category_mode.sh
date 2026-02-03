#!/bin/bash
# Start with Category Mode - Track keyboard categories across European markets
# Usage: ./scripts/start_category_mode.sh

cd "$(dirname "$0")/.."

echo "🎯 CATEGORY MODE: Tracking Keyboard Categories"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env not found! Creating..."
    cp .env.example .env
    echo "📝 Please edit .env and add KEEPA_API_KEY!"
    exit 1
fi

# Check KEEPA_API_KEY
if ! grep -q "KEEPA_API_KEY=" .env || [ -z "$(grep "KEEPA_API_KEY=" .env | cut -d'=' -f2)" ]; then
    echo "⚠️  KEEPA_API_KEY not set in .env!"
    exit 1
fi

# Check if category config exists
if [ ! -f config/categories.yaml ]; then
    echo "⚠️  config/categories.yaml not found!"
    exit 1
fi

echo "📊 Category Configuration:"
cat config/categories.yaml | grep -E "^[A-Z]{2}:" | while read line; do
    country=$(echo "$line" | cut -d':' -f1)
    echo "   - $country"
done
echo ""

# Stop existing
echo "🛑 Stopping existing containers..."
sudo docker-compose down -v --remove-orphans 2>/dev/null

# Start in category mode
echo "🚀 Starting with CATEGORY_MODE=true..."
CATEGORY_MODE=true sudo docker-compose up -d zookeeper elasticsearch kafka
sleep 5
CATEGORY_MODE=true sudo docker-compose up -d enrichment-consumer arbitrage-detector api dashboard init-topics
CATEGORY_MODE=true sudo docker-compose up -d producer

echo ""
echo "✅ Category Mode started!"
echo ""
echo "📊 Dashboard: http://localhost:8501"
echo ""
echo "💡 The producer will now:"
echo "   1. Fetch ASINs from keyboard category bestsellers"
echo "   2. Track prices across DE, IT, ES, UK, FR"
echo "   3. Identify arbitrage opportunities"
