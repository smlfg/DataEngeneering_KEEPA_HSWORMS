#!/bin/bash
# Fix Import Paths in all Python files
# Führt dieses Skript aus nach Code-Änderungen

echo "🔧 Fixing import paths..."

cd "$(dirname "$0")/.."

# Fix producer/main.py
sed -i 's/from keepa_client/from producer.keepa_client/g' src/producer/main.py
sed -i 's/from kafka_producer/from producer.kafka_producer/g' src/producer/main.py

# Fix consumer/main.py
sed -i 's/from kafka_consumer/from consumer.kafka_consumer/g' src/consumer/main.py
sed -i 's/from enricher/from consumer.enricher/g' src/consumer/main.py
sed -i 's/from indexer/from consumer.indexer/g' src/consumer/main.py

# Fix arbitrage/main.py
sed -i 's/from indexer/from consumer.indexer/g' src/arbitrage/main.py
sed -i 's/from calculator/from arbitrage.calculator/g' src/arbitrage/main.py
sed -i 's/from detector/from arbitrage.detector/g' src/arbitrage/main.py

echo "✅ Import paths fixed!"
