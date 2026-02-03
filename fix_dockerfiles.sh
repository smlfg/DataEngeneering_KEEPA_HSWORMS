#!/bin/bash
# Fix Dockerfiles for arbitrage-tracker project
# This script creates corrected Dockerfiles that use Poetry

set -e  # Exit on error

PROJECT_DIR="$HOME/Dokumente/WS2025/DataEnge/arbitrage-tracker"
cd "$PROJECT_DIR"

echo "🔧 Fixing Dockerfiles for arbitrage-tracker..."
echo "================================================"
echo ""

# Backup old Dockerfiles
echo "📦 Step 1: Backing up old Dockerfiles..."
mkdir -p .old_dockerfiles
if [ -f src/api/Dockerfile ]; then
    cp src/api/Dockerfile .old_dockerfiles/api.Dockerfile.backup
fi
if [ -f src/producer/Dockerfile ]; then
    cp src/producer/Dockerfile .old_dockerfiles/producer.Dockerfile.backup
fi
if [ -f src/consumer/Dockerfile ]; then
    cp src/consumer/Dockerfile .old_dockerfiles/consumer.Dockerfile.backup
fi
if [ -f src/arbitrage/Dockerfile ]; then
    cp src/arbitrage/Dockerfile .old_dockerfiles/arbitrage.Dockerfile.backup
fi
if [ -f src/dashboard/Dockerfile ]; then
    cp src/dashboard/Dockerfile .old_dockerfiles/dashboard.Dockerfile.backup
fi
echo "✅ Backups created in .old_dockerfiles/"
echo ""

# Create API Dockerfile
echo "📝 Step 2: Creating API Dockerfile..."
cat > src/api/Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.7.1

COPY pyproject.toml ./
COPY src/ ./src/

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
echo "✅ API Dockerfile created"

# Create Producer Dockerfile
echo "📝 Step 3: Creating Producer Dockerfile..."
cat > src/producer/Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.7.1

COPY pyproject.toml ./
COPY src/ ./src/

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

CMD ["python", "-m", "src.producer.main"]
EOF
echo "✅ Producer Dockerfile created"

# Create Consumer Dockerfile
echo "📝 Step 4: Creating Consumer Dockerfile..."
cat > src/consumer/Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.7.1

COPY pyproject.toml ./
COPY src/ ./src/

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

CMD ["python", "-m", "src.consumer.main"]
EOF
echo "✅ Consumer Dockerfile created"

# Create Arbitrage Dockerfile
echo "📝 Step 5: Creating Arbitrage Dockerfile..."
cat > src/arbitrage/Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.7.1

COPY pyproject.toml ./
COPY src/ ./src/

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

CMD ["python", "-m", "src.arbitrage.main"]
EOF
echo "✅ Arbitrage Dockerfile created"

# Create Dashboard Dockerfile
echo "📝 Step 6: Creating Dashboard Dockerfile..."
cat > src/dashboard/Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.7.1

COPY pyproject.toml ./
COPY src/ ./src/

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

EXPOSE 8501
CMD ["streamlit", "run", "src/dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF
echo "✅ Dashboard Dockerfile created"
echo ""

echo "🎉 All Dockerfiles have been fixed!"
echo ""
echo "📋 Summary:"
echo "  - Backups saved to: .old_dockerfiles/"
echo "  - 5 Dockerfiles created/updated"
echo "  - Using Poetry for dependency management"
echo ""
echo "🚀 Next steps:"
echo "  1. Run: docker compose build"
echo "  2. Run: docker compose up -d"
echo "  3. Check status: docker compose ps"
echo ""
