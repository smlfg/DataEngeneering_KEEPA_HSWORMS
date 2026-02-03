#!/bin/bash
# Stop all services

cd "$(dirname "$0")/.."

echo "🛑 Stopping all services..."
sudo docker-compose down -v --remove-orphans
echo "✅ All services stopped!"
