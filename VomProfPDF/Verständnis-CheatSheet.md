# Dein Projekt - Kurz erklärt

## Was macht das System?

**In 30 Sekunden:**
> Mein System überwacht Amazon-Preise. Der User gibt eine ASIN ein (z.B. B0DHTYW7P8), ich prüfe regelmäßig die Preise und sende E-Mail-Alerts wenn der Preis unter einen Zielpreis fällt. Zusätzlich suche ich täglich die besten Deals und speichere sie in Elasticsearch für schnelle Volltextsuche.

---

## Die Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER                                     │
│   • Legt Preis-Alarm an (ASIN + Zielpreis)                     │
│   • Sucht Deals (Volltextsuche in ES)                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FASTAPI (Port 8000)                         │
│   Empfängt Requests, validiert, leitet weiter                   │
│   • POST /watches - Preisalarm anlegen                          │
│   • GET /deals - Deals suchen                                   │
│   • POST /deals/es-search - ES-Volltextsuche                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌───────────┐
   │   POST   │  │ REDIS    │  │ELASTICSEARCH│
   │GRESQL    │  │(Cache)   │  │(Suche)     │
   └─────────┘  └──────────┘  └───────────┘
        │             │             │
        └─────────────┼─────────────┘
                      ▼
            ┌─────────────────┐
            │   KEEPA API     │
            │ (Amazon Daten)  │
            └─────────────────┘
```

---

## Die 3 wichtigsten Komponenten

### 1. Price Monitor Agent
- Checkt alle X Stunden die Preise
- Vergleicht mit Zielpreis
- Trigger Alert wenn Preis fällt

### 2. Deal Finder Agent  
- Sucht täglich nach Deals
- Bewertet Deals nach Rabatt + Rating
- **Speichert in Elasticsearch** ← Das zeigt Kurswissen!

### 3. Alert Dispatcher
- Sendet E-Mail bei Preisalarm
- (Telegram/Discord sind Stubs)

---

## Was zeigt Kurswissen?

| Kurs-Thema | Bei dir |
|------------|---------|
| **Elasticsearch** | ✅ Deal-Suche in ES mit Fuzzy-Suche, Aggregations |
| **Docker Compose** | ✅ Multi-Container Setup |
| **Python API** | ✅ FastAPI mit async/await |
| **Kafka** | ⚠️ Container läuft, aber nicht genutzt |
| **Redis** | ⚠️ Container läuft, als Cache |

---

## Was der Prof sehen will

### 1. Pipeline läuft
```bash
docker-compose up -d
curl http://localhost:8000/health
```

### 2. Elasticsearch funktioniert
```bash
# Index erstellen (wird automatisch gemacht)
# Suche mit Fuzzy
curl -X POST http://localhost:8000/api/v1/deals/es-search \
  -d '{"query": "smartphon", "min_discount": 30}'
```

### 3. Aggregations
```bash
curl http://localhost:8000/api/v1/deals/aggregations?min_discount=20
```

---

## Typische Prof-Fragen & Antworten

### "Warum Elasticsearch?"
> "Weil PostgreSQL keine gute Volltextsuche hat. Mit Elasticsearch kann ich fuzzy search (Tippfehler tolerieren), relevancia-basiertes Ranking und Aggregations für Statistiken."

### "Warum kein Kafka?"
> "Für unsere Last ist direkte Verarbeitung einfacher. Aber Kafka ist im Docker-Container bereit für skalierung."

### "Wie skaliert das?"
> "Horizontal durch Docker. PostgreSQL kann auf Read-Replicas, ES skaliert nativ mit Shards."

---

## Wichtige Files

| File | Was drin ist |
|------|--------------|
| `src/api/main.py` | Alle API-Endpoints |
| `src/agents/deal_finder.py` | Deal-Suche + ES-Indexierung |
| `src/services/elasticsearch_service.py` | ES-Client + Queries |
| `docker-compose.yml` | Alle Services |

---

## Cheat Sheet für die Präsentation

```bash
# Starten
docker-compose up -d

# Status
docker-compose ps
curl http://localhost:8000/health

# Deals suchen (ES)
curl -X POST http://localhost:8000/api/v1/deals/es-search \
  -H "Content-Type: application/json" \
  -d '{"query": "iphone", "min_discount": 30}'

# Preis-Alarm anlegen
curl -X POST "http://localhost:8000/api/v1/watches?user_id=user1" \
  -H "Content-Type: application/json" \
  -d '{"asin": "B0DHTYW7P8", "target_price": 800}'

# Alle Watches
curl "http://localhost:8000/api/v1/watches?user_id=user1"
```
