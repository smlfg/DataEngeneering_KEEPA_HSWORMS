# Keeper System - Amazon Price Monitoring & Deal Finder

Multi-Agent System für Amazon-Preisüberwachung und Deal-Suche.

## Architektur

```
┌─────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR AGENT                     │
│  (LangGraph Workflow - Zentrale Koordination)           │
└───────────┬─────────────────┬───────────────────────────┘
            │                 │
    ┌───────▼───────┐   ┌─────▼─────────┐
    │ PRICE MONITOR │   │ DEAL FINDER   │
    │   AGENT       │   │    AGENT      │
    └───────┬───────┘   └───────┬───────┘
            │                   │
            └─────────┬─────────┘
                      │
            ┌─────────▼─────────┐
            │ ALERT DISPATCHER  │
            │     AGENT         │
            └───────────────────┘
```

## Features

- **Preis-Überwachung**: Automatische Alerts bei Preis Drops
- **Deal-Finder**: Tägliche personalisierte Deal-Reports
- **Multi-Channel**: Email, Telegram, Discord Support
- **DSGVO-konform**: Audit Logging, Daten-Verschlüsselung

## Quick Start

```bash
# 1. Environment kopieren
cp .env.example .env

# 2. API Keys eintragen
nano .env

# 3. Docker starten
docker-compose up -d

# 4. API testen
curl http://localhost:8000/health
```

## Struktur

```
keeper-system/
├── prompts/              # Agent System Prompts
├── src/
│   ├── agents/           # Agent-Implementierungen
│   ├── services/         # Business Logic
│   ├── graph/            # LangGraph States/Nodes
│   └── api/              # REST Endpoints
├── tests/                # Unit Tests
└── docker-compose.yml
```

## API Endpoints

| Methode | Endpoint | Beschreibung |
|---------|----------|--------------|
| GET | /health | Health Check |
| POST | /api/v1/watches | Produkt überwachen |
| GET | /api/v1/watches | Alle watches abrufen |
| DELETE | /api/v1/watches/{id} | Watch löschen |
| POST | /api/v1/deals/search | Deals suchen |
| GET | /api/v1/reports/{id} | Report abrufen |

## Environment Variablen

| Variable | Beschreibung | Required |
|----------|--------------|----------|
| KEEPA_API_KEY | Keepa API Key | Yes |
| OPENAI_API_KEY | OpenAI API Key | Yes |
| DATABASE_URL | PostgreSQL Connection | Yes |
| REDIS_URL | Redis Connection | Yes |
| SMTP_HOST | Email Server | No |
| TELEGRAM_BOT_TOKEN | Telegram Bot Token | No |
| DISCORD_WEBHOOK | Discord Webhook URL | No |

## Lizenz

MIT
