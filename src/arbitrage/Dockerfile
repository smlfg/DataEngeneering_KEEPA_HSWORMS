FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.7.1

COPY pyproject.toml ./
COPY src/ ./src/

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

CMD ["python", "-m", "src.arbitrage.main"]
