# Anforderungen fuer Data Engineering

## Zweck der Datei
Diese Datei fasst die Anforderungen fuer die Projektabgabe im Fach Data Engineering zusammen.  
Sie trennt klar zwischen:
- verbindlichen **MUSS**-Kriterien aus der Pruefungsleistung,
- **SOLL/KANN**-Kriterien aus den Uebungen (technische Vertiefung).

## Quellenbasis
- `VomProfPDF/VL1_Einführung.md` (insb. Abschnitt "Pruefungsleistung: Projektarbeit")
- `VomProfPDF/VL5_Elasticsearch_3.md` (insb. Abschnitt "Abschlussprojekt")
- `VomProfPDF/VL7_Kafka.md` (insb. Abschnitt "Abschlussprojekt")
- `VomProfPDF/Übung1_Elasticsearch.md`
- `VomProfPDF/Übung 2 - Elasticsearch 2.md`
- `VomProfPDF/Übung 3 - Elasticsearch mit Movie-Datensatz.md`
- `VomProfPDF/Übung 5 - Apache Kafka mit Movie-Datensatz.md`

## A. Verbindliche MUSS-Anforderungen (Pruefung)

| ID | Anforderung (MUSS) | Konkret pruefbar durch |
|---|---|---|
| M1 | End-to-End-Loesung zur **Erfassung, Verarbeitung und Speicherung** von Daten | Laufende Pipeline + Architekturerklaerung + Live-Demo |
| M2 | Daten aus einer Quelle laden (z. B. API/Scraping) | Code fuer Ingestion + Nachweis der eingehenden Daten |
| M3 | Daten **periodisch** abgreifen (Scheduling) | Scheduler-Job/Service + dokumentierter Intervall |
| M4 | **Vorverarbeitung** der Daten (nicht nur 1:1 speichern) | Transformations-/Filter-/Anreicherungslogik im Code |
| M5 | Speicherung in einem fuer den Use Case sinnvollen System | DB-Wahl begruendet + persistente Speicherung nachweisbar |
| M6 | Datenbank-Einstellungen und Optimierung betrachten | Index-/Schema-/Performance-Entscheidungen dokumentiert |
| M7 | Deployment mit passenden Einstellungen | Startbares Deployment (z. B. Docker Compose) |
| M8 | Einstellungen als Code, keine manuellen Klickpfade | Konfigurationsdateien/Skripte im Repo |
| M9 | Code muss in zugaenglichem Git-Repository liegen | Repo-Link und reproduzierbarer Stand |
| M10 | Abschlusspraesentation mit Begruendung der Entscheidungen | Folien/Handout + Architekturentscheidungen + Trade-offs |

## B. Use-Case-Auswahl (mind. eine Richtung klar abdecken)
Aus den Vorlesungen ergeben sich drei moegliche Schwerpunkte:
- Klassischer Analytics Use Case
- Such-Optimierung
- Verarbeitung von Echtzeitdaten

Hinweis: Es ist nicht noetig, alle drei maximal auszubauen. Pruefungsrelevant ist ein konsistenter End-to-End-Use-Case mit nachvollziehbaren Entscheidungen.

## C. SOLL/KANN aus den Uebungen (Ergaenzungen)

Diese Punkte sind starke Pluspunkte fuer die Qualitaet der Abgabe, aber nicht automatisch alle als harte MUSS-Kriterien definiert.

### C1. Elasticsearch (SOLL)
- Cluster-Grundlagen und Rollen verstehen (mehrere Nodes).
- Index, Mapping und sinnvolle Feldtypen.
- Alias ueber mehrere Indizes.
- Index Templates, Rollover/ILM-Verstaendnis.
- Ingest Pipelines (Transformation beim Schreiben).
- Analyzer fuer Suchqualitaet.
- Batch-Indexierung und Query-Auswertung.

### C2. Kafka (SOLL)
- Kafka per Docker Compose deployen.
- Producer (CSV/JSON -> Topic).
- Zwei Consumer in getrennten Consumer Groups.
- Cluster-Skalierung (mehr Broker).
- Topic-Partitionierung erhoehen und Verhalten verifizieren.

## D. Abnahme-Checkliste (ausgefuellt)

| Kriterium | Status | Nachweis im Repo | Demo-Satz fuer Praesentation |
|---|---|---|---|
| M1 End-to-End | [x] | `docker-compose.yml` startet gesamte Pipeline; `curl localhost:8000/health` prueft alle Services; `ExplanationForSamuel.md` enthaelt Demo-Runbook | "Unser System erfasst Amazon-Preise ueber Keepa, verarbeitet sie via Kafka, speichert in PostgreSQL + Elasticsearch, und liefert Deals ueber die REST API." |
| M2 Ingestion | [x] | `src/services/keepa_api.py` — Keepa REST API Client mit Token-Bucket Rate Limiting; `src/agents/deal_finder.py` Zeile 240-293 — ASIN-basierte Produktabfrage | "Wir laden Preisdaten ueber die Keepa API — ein kommerzieller Wrapper fuer Amazon-Produktdaten mit Rate Limiting." |
| M3 Scheduling | [x] | `src/scheduler.py` — APScheduler mit konfigurierbarem Intervall (`DEAL_SCAN_INTERVAL_SECONDS`); `docker-compose.yml` Zeile 95-112 — Scheduler als eigener Service | "Der Scheduler laeuft als eigenstaendiger Docker-Service und ruft alle 6 Stunden die Keepa API ab." |
| M4 Vorverarbeitung | [x] | `src/agents/deal_finder.py` Zeile 295-338 — `_normalize_deal()` normalisiert camelCase zu snake_case; Zeile 340-400 — `_build_deal_from_product()` berechnet Discount, extrahiert Preise; `filter_spam()` entfernt Low-Quality Deals | "Rohdaten werden normalisiert (Feldnamen), angereichert (Discount-Berechnung, Scoring), und gefiltert (Spam-Erkennung)." |
| M5 Speicherung | [x] | `src/services/database.py` — SQLAlchemy Models (watches, price_history, collected_deals); `src/services/elasticsearch_service.py` — ES-Indexing (keeper-prices, keeper-deals); PostgreSQL fuer ACID, ES fuer Suche/Analytics | "PostgreSQL sichert konsistente Preis-History, Elasticsearch ermoeglicht schnelle Volltext-Suche und Aggregationen — bewusster Dual-Storage Trade-off." |
| M6 DB-Optimierung | [x] | `src/services/database.py` — Indices auf ASIN + Timestamp fuer schnelle Lookups; `src/services/elasticsearch_service.py` — Mapping-Definitionen fuer optimale Feldtypen; `docs/ARCHITECTURE.md` Sektion 2 — dokumentierte Entscheidungen | "Wir indexieren nach ASIN und Timestamp fuer O(log n) Lookups. ES-Mappings sind explizit definiert statt dynamic — bessere Speicher- und Sucheffizienz." |
| M7 Deployment | [x] | `docker-compose.yml` — 8 Services orchestriert; `Dockerfile` — Python App Container; `.env.example` — Template fuer Konfiguration; `README.md` — 3-Schritt-Quickstart | "Ein `docker-compose up -d` startet das komplette System — PostgreSQL, Kafka, Elasticsearch, Kibana, API und Scheduler." |
| M8 Einstellungen als Code | [x] | `.env.example` — alle Environment-Variablen dokumentiert; `src/config.py` — Pydantic Settings mit Defaults; `docker-compose.yml` — Service-Konfiguration; `pytest.ini` — Test-Konfiguration | "Alle Einstellungen liegen als Code im Repo — keine manuellen Klickpfade. `.env.example` dient als Template." |
| M9 Git-Repo | [x] | `https://github.com/smlfg/DataEngeneering_KEEPA_HSWORMS` — oeffentliches Repository; Branch `KeepaPreisSystem` mit gesamtem Code; `.gitignore` schliesst Secrets aus | "Das komplette Projekt liegt auf GitHub. Ein frischer Clone + 3 Befehle = lauffaehiges System." |
| M10 Praesentation der Entscheidungen | [x] | `docs/ARCHITECTURE.md` — Architekturdiagramm, Technologie-Entscheidungen mit Begruendung, Trade-offs, 5 Prueferfragen mit Antworten, 10-Minuten-Storyline | "Jede Technologie-Entscheidung ist begruendet: Warum Dual-Storage? Warum Kafka statt direktem Write? Warum periodisch statt Echtzeit?" |

## E. Bewertungsorientierte Mindestdefinition ("bestanden")

Das Projekt ist pruefungsreif, wenn:
1. Eine durchgaengige Pipeline laeuft (Daten rein -> verarbeitet -> gespeichert -> abrufbar/analysefaehig).
2. Periodischer Lauf und Deployment reproduzierbar per Code gestartet werden koennen.
3. Die wichtigsten Architekturentscheidungen und Trade-offs klar erklaert werden koennen.
4. Alle obigen MUSS-Kriterien in der Checkliste mit konkreten Nachweisen gefuellt sind.

---

## F. Ausfuehrliche VL-Inhalte (technische Details)

### VL2 - NOSQL Databases (Zusaetzliche Details)

**NOSQL-Typen:**
- Key-Value Stores (Redis)
- Wide-Column Stores (Cassandra)
- Graphen-Datenbanken (Neo4J)
- Dokumentenorientiert (MongoDB, Elasticsearch)
- Vektor-Datenbanken (pgvector)

**Wichtige Konzepte:**
- Schema-on-Read vs. Schema-on-Write
- Data Locality (denormalisierte Speicherung)
- BASE vs. ACID
- CAP Theorem (Consistency, Availability, Partition Tolerance)
- Sharding: Range-based, Hash-based, Geo-sharding

### VL3 - Elasticsearch Basics

**Grundkonzepte:**
- Verteilte Suchmaschine und dokumentenorientierte Datenbank basierend auf Apache Lucene
- Core Concepts: Indices, Documents, Mappings, Metadata fields (_id, _index)

**Verteilte Architektur:**
- Node Roles: Master, Data, Ingest, Coordinating, ML
- Quorum-basiertes Voting (N/2 + 1)
- Shards: Primary und Replicas
- Segments (Lucene Indices) - unveränderlich

### VL4 - Elasticsearch Advanced

**Index Management:**
- Rollover: Verwaltung von Time-Series-Daten
- Index Templates: Component Templates + Index Templates
- Aliases: Alternative Namen fuer Index-Gruppen

**Datenverarbeitung:**
- Ingest Pipelines: Vorverarbeitung (Processors, Grok, Enrich)
- Reindex: Kopieren zwischen Indices

### VL5 - Search & Relevance

**Suchanalyse:**
- Analyzer: Character Filters -> Tokenizer -> Token Filters
- Inverted Index: Zentrale Such-Datenstruktur
- Scoring: TF x IDF x FieldNorm

**Query-Typen:**
- Match, Boolean (must, filter, should, must_not), Boosting
- Custom Analyzers: Synonyms, Stemmers, N-grams

### VL6 - Aggregations

**Bucket Aggregations:**
- Terms, Histogram, Date Histogram, Range, Categorize Text

**Metric Aggregations:**
- Avg, Max, Min, Percentiles, Stats

**Pipeline Aggregations:**
- Average Bucket, Bucket Selector

### VL7 - Apache Kafka

**Core Concepts:**
- Topics (equivalent zu Queues ohne Exhaustion)
- Producer/Consumer
- Partitions: Skalierung, Ordering
- Consumer Groups: Geteilter Pointer, unabhaengige Gruppen
- Replication: Leader/Follower, acks=all/1

### Uebungsanforderungen (Details)

**Uebung 1 - Elasticsearch Basics:**
- 3-Node Elasticsearch Cluster
- Python Integration mit elasticsearch-py
- Bulk-Upload
- Mappings und Aliases

**Uebung 2 - Elasticsearch Advanced:**
- Index Templates mit Rollover
- Ingest Pipelines mit Grok
- Aliases ueber mehrere Indices

**Uebung 3 - Elasticsearch Movie Dataset:**
- Kaggle Movie Dataset
- Custom Mappings (title, genres, release_date, overview)
- Custom Analyzers mit Synonymen
- Batch-Indexierung
- Volltextsuche

**Uebung 5 - Kafka:**
- Docker Compose mit Kafka
- Python Producer (CSV/JSON -> Topic)
- Zwei Consumer in getrennten Consumer Groups
- Cluster-Skalierung (3 Broker)
- Partitionierung erhoehen und verifizieren
