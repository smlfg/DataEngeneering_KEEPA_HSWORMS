#!/bin/bash
# Check system status

cd "$(dirname "$0")/.."

echo "📊 Arbitrage Tracker System Status"
echo "===================================="
echo ""

echo "🐳 Docker Containers:"
sudo docker-compose ps
echo ""

echo "🔍 Elasticsearch:"
curl -s http://localhost:9200/_cluster/health 2>/dev/null | head -1 || echo "   ❌ Not running"
echo ""

echo "📈 API Health:"
curl -s http://localhost:8000/health 2>/dev/null | head -1 || echo "   ❌ Not running"
echo ""

echo "📦 Product Count:"
curl -s http://localhost:9200/products/_count 2>/dev/null | grep -o '"count":[0-9]*' || echo "   0 products"
echo ""

echo "🎯 Arbitrage Opportunities:"
curl -s "http://localhost:8000/arbitrage?min_margin=10" 2>/dev/null | grep -o '"total":[0-9]*' || echo "   0 opportunities"
