# Erklärungen - Amazon Arbitrage Tracker System

Willkommen zur technischen Dokumentation des Amazon Arbitrage Tracker Systems!

Diese Dokumentation erklärt **alle verwendeten Technologien** von Grund auf - perfekt für das Verständnis des kompletten Systems.

## 📚 Dokumentations-Übersicht

### 🎯 Start hier

**[00_OVERVIEW.md](./00_OVERVIEW.md)** - **System-Übersicht**
- Was ist Arbitrage?
- Wie funktioniert das System?
- Welche Komponenten gibt es?
- Wie fließen die Daten?

### 🔧 Technologien im Detail

#### Datenbanken & Speicher

**[01_Elasticsearch.md](./01_Elasticsearch.md)** - **NoSQL Datenbank**
- Was ist Elasticsearch?
- Wie funktioniert die Suche?
- Indices, Dokumente, Mappings
- Kibana-Nutzung

**[02_Kafka.md](./02_Kafka.md)** - **Message Queue System**
- Was ist Apache Kafka?
- Topics, Producer, Consumer
- Partitionen & Consumer Groups
- Monitoring & Debugging

#### Datenquellen & APIs

**[03_Keepa.md](./03_Keepa.md)** - **Amazon Preis-Tracker API**
- Keepa API Basics
- Endpoints & Token-System
- Rate Limiting
- Multimarktplatz-Abfragen

#### Workflow & Orchestrierung

**[04_Airflow.md](./04_Airflow.md)** - **Workflow Scheduler**
- Was sind DAGs?
- Tasks & Operators
- Scheduler, Worker, Executor
- Airflow Web UI

#### Containerisierung & Deployment

**[05_Docker.md](./05_Docker.md)** - **Container-Technologie**
- Images vs. Container
- Dockerfile-Syntax
- Docker Compose
- Volumes & Networks

#### Backend & Frontend

**[06_FastAPI.md](./06_FastAPI.md)** - **REST API Framework**
- HTTP Basics
- Routes & Endpoints
- Pydantic Models
- Auto-Dokumentation (Swagger)

**[07_Streamlit.md](./07_Streamlit.md)** - **Dashboard Framework**
- Widgets & Display-Elemente
- Layout & Sidebar
- Caching
- Interaktivität

#### Dependency Management

**[08_Poetry.md](./08_Poetry.md)** - **Python Package Manager**
- pyproject.toml & poetry.lock
- Dependency-Management
- Virtuelle Umgebungen
- Docker-Integration

### 🏗️ Gesamtsystem

**[09_System_Architecture.md](./09_System_Architecture.md)** - **System-Architektur**
- Kompletter Datenfluss
- Kommunikations-Patterns
- Daten-Transformationen
- Skalierungs-Strategien

## 📖 Lese-Reihenfolge

### Für Einsteiger

1. **[00_OVERVIEW.md](./00_OVERVIEW.md)** - Verstehe das große Ganze
2. **[05_Docker.md](./05_Docker.md)** - Wie Services laufen
3. **[01_Elasticsearch.md](./01_Elasticsearch.md)** - Wo Daten gespeichert werden
4. **[02_Kafka.md](./02_Kafka.md)** - Wie Daten fließen
5. **[09_System_Architecture.md](./09_System_Architecture.md)** - Wie alles zusammenspielt

### Für Entwickler

1. **[00_OVERVIEW.md](./00_OVERVIEW.md)** - System-Übersicht
2. **[08_Poetry.md](./08_Poetry.md)** - Dependencies verwalten
3. **[05_Docker.md](./05_Docker.md)** - Services starten
4. **[06_FastAPI.md](./06_FastAPI.md)** - API entwickeln
5. **[07_Streamlit.md](./07_Streamlit.md)** - Dashboard bauen
6. **[09_System_Architecture.md](./09_System_Architecture.md)** - Architektur verstehen

### Für Data Engineers

1. **[02_Kafka.md](./02_Kafka.md)** - Event Streaming
2. **[01_Elasticsearch.md](./01_Elasticsearch.md)** - NoSQL Database
3. **[04_Airflow.md](./04_Airflow.md)** - Workflow Orchestration
4. **[03_Keepa.md](./03_Keepa.md)** - External API Integration
5. **[09_System_Architecture.md](./09_System_Architecture.md)** - Complete Pipeline

## 🎓 Was du lernen wirst

Nach dem Durcharbeiten dieser Dokumentation verstehst du:

- ✅ Wie **Event-Driven Architectures** funktionieren
- ✅ Wie **NoSQL-Datenbanken** (Elasticsearch) Daten speichern und durchsuchen
- ✅ Wie **Message Queues** (Kafka) Services entkoppeln
- ✅ Wie **REST APIs** (FastAPI) Backend-Logik bereitstellen
- ✅ Wie **Workflow-Scheduler** (Airflow) Tasks automatisieren
- ✅ Wie **Container** (Docker) Services isolieren
- ✅ Wie **moderne Python-Tools** (Poetry) Dependencies verwalten
- ✅ Wie **Web-Dashboards** (Streamlit) gebaut werden

## 🚀 Schnellstart

### System verstehen

```bash
# 1. Übersicht lesen
cat Explained/00_OVERVIEW.md

# 2. Docker-Services starten
docker compose up -d

# 3. Dashboard öffnen
open http://localhost:8501

# 4. API-Docs öffnen
open http://localhost:8000/docs

# 5. Kibana öffnen (Elasticsearch UI)
open http://localhost:5601

# 6. Airflow öffnen
open http://localhost:8080
```

### Logs verfolgen

```bash
# Producer
docker logs -f arbitrage-producer

# Consumer
docker logs -f arbitrage-enrichment-consumer

# API
docker logs -f arbitrage-api
```

## 📊 Diagramme & Visualisierungen

Alle Markdown-Dateien enthalten:
- 📈 ASCII-Diagramme für Architektur
- 💻 Code-Beispiele mit Syntax-Highlighting
- 📋 Vergleichs-Tabellen
- ✅ Best Practices
- ⚠️ Troubleshooting-Tipps

## 🤝 Beitragen

Diese Dokumentation ist Teil des Arbitrage-Tracker-Projekts.

Bei Fragen oder Verbesserungsvorschlägen:
- Issue erstellen
- Pull Request öffnen
- Dokumentation erweitern

## 📝 Lizenz

Diese Dokumentation steht unter der gleichen Lizenz wie das Hauptprojekt.

---

**Viel Erfolg beim Lernen! 🎉**

*Erstellt: 2026-01-11*
*Version: 1.0.0*
