#!/bin/bash
# Show logs for a specific service

SERVICE=${1:-producer}

cd "$(dirname "$0")/.."

echo "📜 Showing logs for: $SERVICE"
sudo docker logs -f "arbitrage-$SERVICE"
