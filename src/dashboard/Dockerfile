FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.7.1

COPY pyproject.toml ./
COPY src/ ./src/

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

EXPOSE 8501
CMD ["streamlit", "run", "src/dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
