# Keeper System — Prüfungspräsentation

> Dieses Dokument ist dein roter Faden für die mündliche Prüfung.
> Lies es von oben nach unten, in genau dieser Reihenfolge.

---

## 1. Die Idee (30 Sekunden)

**Ein Satz:** "Ich habe ein System gebaut, das Amazon-Keyboard-Preise automatisch überwacht und die besten Deals findet."

**Das Problem:** Wer Amazon-Preise vergleichen will, muss ständig manuell nachschauen. Preise ändern sich mehrmals täglich. Das gleiche Keyboard kostet in verschiedenen EU-Ländern unterschiedlich viel.

**Die Lösung:** Ein automatisiertes System das:
- Regelmäßig Preise bei der Keepa API abfragt
- Deals erkennt (Preis gefallen? Rabatt groß genug?)
- Ergebnisse in drei Systemen speichert (je nach Stärke)
- User benachrichtigt wenn ihr Wunschpreis erreicht ist

**Zielgruppe:** Keyboard-Enthusiasten und Schnäppchenjäger im EU-Raum.

---

## 2. Der Tech Stack (2 Minuten)

### Warum diese 6 Technologien?

| Technologie | Aufgabe | Warum genau diese? |
|---|---|---|
| **PostgreSQL** | Daten sicher speichern | Source of Truth. ACID-Garantien: entweder wird alles gespeichert oder nichts. Relationale Verknüpfungen (User → Watch → Alert) |
| **Apache Kafka** | Events streamen | Entkoppelt Producer von Consumer. Neue Services hinzufügen ohne bestehenden Code zu ändern. Puffert Nachrichten wenn ein Consumer ausfällt |
| **Elasticsearch** | Deals durchsuchbar machen | Full-Text-Suche ("finde alle mechanischen Keyboards unter 50€"). Aggregationen (Durchschnittspreis, Top-Rabatte). Millisekunden-Antwortzeiten |
| **Kibana** | Dashboards & Visualisierung | Zeigt Preistrends, Deal-Statistiken, Token-Verbrauch als Grafiken. Sitzt auf Elasticsearch |
| **FastAPI** | REST-API für Zugriff von außen | Async, automatische API-Dokumentation unter /docs. Endpoints für Watches erstellen, Deals suchen, Health-Check |
| **Docker Compose** | Alles zusammen starten | Ein Befehl startet alle 7 Container. Reproduzierbar auf jedem Rechner |

### Warum DREI Speichersysteme?

Jedes System hat eine Superkraft die die anderen nicht haben:

```
PostgreSQL  → Daten SICHER speichern (ACID, Transaktionen, Relationen)
Kafka       → Events ENTKOPPELT weiterleiten (Replay, Pufferung, Consumer Groups)
Elastic     → Daten SCHNELL durchsuchen (Full-Text, Aggregationen, Dashboards)
```

Ohne PostgreSQL: Datenverlust bei Crashes möglich.
Ohne Elasticsearch: Keine effiziente Keyword-Suche über tausende Deals.
Ohne Kafka: Jede neue Funktion erfordert Änderungen am Scheduler.

---

## 3. Die Architektur (2 Minuten)

### Das Gesamtbild

```
┌─────────────────────────────────────────────────────────────┐
│                       KEEPER SYSTEM                          │
│                                                              │
│   ⏰ SCHEDULER (alle 6h Preise, alle 1h Deals)              │
│       │                                                      │
│       ▼                                                      │
│   🌐 KEEPA API CLIENT (Token Bucket: 20 Tokens/Min)         │
│       │                                                      │
│       ▼                                                      │
│   📝 TRIPLE-WRITE ─────┬──────────────┬──────────────┐      │
│       │                 │              │              │      │
│       ▼                 ▼              ▼              │      │
│   🐘 PostgreSQL    📨 Kafka      🔍 Elasticsearch    │      │
│   (Port 5432)      (Port 9092)   (Port 9200)         │      │
│   Source of Truth   2 Topics      3 Indices           │      │
│                     │                   │             │      │
│                     ▼                   ▼             │      │
│              2 Consumer Groups    📊 Kibana (5601)    │      │
│                                                       │      │
│   🔔 ALERT DISPATCHER (Email / Telegram / Discord)    │      │
│                                                       │      │
│   🌐 FASTAPI (Port 8000) — REST-API + Swagger Docs   │      │
└─────────────────────────────────────────────────────────────┘
```

### Die 7 Docker Container

| Container | Was er tut | Port |
|---|---|---|
| **db** | PostgreSQL — speichert Watches, Alerts, Deals, User | 5432 |
| **kafka** | Apache Kafka — Event Streaming zwischen Services | 9092 |
| **zookeeper** | Verwaltet Kafka (interne Koordination) | 2181 |
| **elasticsearch** | Such-Engine für Deals (3 Indices) | 9200 |
| **kibana** | Dashboard-Visualisierung für Elasticsearch | 5601 |
| **app** | FastAPI Web-Server — REST-API | 8000 |
| **scheduler** | Das Herzstück — zwei Loops, steuert alles | — |

### Die 7 PostgreSQL-Tabellen

| Tabelle | Zweck |
|---|---|
| `users` | Registrierte Nutzer |
| `watched_products` | Welche ASINs werden überwacht, mit Zielpreis |
| `price_alerts` | Ausgelöste Benachrichtigungen |
| `price_history` | Preisverlauf über Zeit |
| `collected_deals` | Gefundene Deals aus dem Deal Collector |
| `deal_filters` | User-definierte Suchfilter für Deal Reports |
| `deal_reports` | Generierte Berichte |

### Die 3 Kafka Topics

| Topic | Inhalt | Consumer Group |
|---|---|---|
| `price-updates` | Preisänderungen von Watches | `keeper-consumer-group` |
| `deal-updates` | Neue Deals vom Deal Collector | `keeper-consumer-group-deals` |
| `keepa-raw-deals` | Rohdaten direkt von Keepa | — |

### Die 3 Elasticsearch Indices

| Index | Inhalt | Kibana Dashboard |
|---|---|---|
| `keeper-prices` | Preis-Updates mit Zeitstempel | Preis-Trends |
| `keeper-deals` | Gesammelte Deals (1046 Dokumente) | Deal-Übersicht |
| `keeper-metrics` | API Token-Verbrauch pro Call | Token Budget |

---

## 4. Der Datenfluss (2 Minuten)

### Loop A: Price Watch (alle 6 Stunden)

```
1. Scheduler holt aktive Watches aus PostgreSQL
       ↓
2. Für jedes Watch → Keepa API fragen (parallel, max 5 gleichzeitig)
       ↓
3. Triple-Write: Preis → PostgreSQL + Kafka + Elasticsearch
       ↓
4. Wenn Preis ≤ Zielpreis → Alert erstellen → User benachrichtigen
```

### Loop B: Deal Collector (jede Stunde)

```
1. Seed-ASINs aus Datei laden (50 Keyboards)
       ↓
2. Batch an Keepa API schicken → Preise zurückbekommen
       ↓
3. Ist es ein Keyboard? (Title-Keywords: "tastatur", "keyboard", etc.)
       ↓
4. Rabatt berechnen: (1 - aktueller_preis / listenpreis) × 100
       ↓
5. In Elasticsearch indexieren + in PostgreSQL speichern
```

### Was passiert bei einem Keepa API Call?

```
Mein System                              Keepa Server
    │                                        │
    │  HTTP GET /product?asin=B09V3KXJPB     │
    │──────────────────────────────────────→  │
    │                                        │
    │  JSON Response: Preise in Cent,        │
    │  Rating, Titel, Kategorie              │
    │  ←──────────────────────────────────── │
    │                                        │
    │  Tokens verbraucht: 15                 │
    │  Tokens übrig: 185                     │
```

Keepa liefert Preise in **Cent** (3999 = 39,99€) und `-1` bedeutet "kein Preis verfügbar".

---

## 5. Schlüsselkonzepte (für Prof-Fragen)

### Token Bucket — Rate Limiting

Die Keepa API erlaubt nur 20 Tokens pro Minute. Der Token Bucket Algorithmus:
- Bucket startet mit Tokens (aufgefüllt nach jedem API-Call von Keepa gemeldet)
- Jeder API-Call verbraucht Tokens (~15 pro Produktabfrage)
- Wenn leer → System wartet asynchron (async await), blockiert nicht
- `asyncio.Lock` verhindert Race Conditions bei parallelen Requests

### Graceful Degradation — Was wenn Kafka ausfällt?

- Scheduler loggt eine Warnung und **läuft weiter**
- Preise werden weiterhin in PostgreSQL und Elasticsearch geschrieben
- Nur die Kafka-Events gehen verloren
- Wenn Kafka wieder da ist → neue Events fließen normal
- **Bewusste Design-Entscheidung:** Kein Retry-Buffer für Einfachheit

### Lazy Reconnect — `_ensure_connections()`

Docker startet alle Container gleichzeitig. Der Scheduler kann bereit sein bevor Kafka/Elasticsearch hochgefahren sind. Vor jedem Zyklus prüft `_ensure_connections()` ob die Verbindungen stehen und verbindet neu falls nötig. Das verhindert dass ein fehlgeschlagener Startup die Pipeline dauerhaft deaktiviert.

### asyncio.gather() mit Semaphore

Statt 50 Preise nacheinander abzufragen (langsam), fragt das System bis zu 5 gleichzeitig ab (parallel). Der Semaphore begrenzt die Gleichzeitigkeit damit die API nicht überlastet wird. `return_exceptions=True` sorgt dafür dass ein fehlgeschlagener Call nicht alle anderen abbricht.

---

## 6. Live-Demo Kurzversion (3 Minuten)

Falls der Prof eine Demo sehen will — diese 5 Befehle zeigen:

```bash
# 1. Alle Container laufen
docker-compose ps

# 2. System ist gesund
curl -s http://localhost:8000/health | python3 -m json.tool

# 3. Kafka hat echte Events
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# 4. Elasticsearch hat 1046 Deals
curl -s 'http://localhost:9200/keeper-deals/_count?pretty'

# 5. Scheduler-Logs zeigen echte Pipeline-Aktivität
docker-compose logs --tail=20 scheduler
```

**Was man sieht:** 7 laufende Container, Health-Check grün, 3 Kafka Topics, 1046 indexierte Deals, strukturierte Pipeline-Logs mit Timestamps.

---

## 7. Bewusste Entscheidungen & Limitationen

### Was wir bewusst NICHT gemacht haben

| Entscheidung | Begründung |
|---|---|
| Kein Redis-Cache | Keepa hat eigenes Rate Limiting, Cache wäre Over-Engineering |
| Kein Kafka-Cluster | Single-Broker reicht für ~100 Nachrichten pro Zyklus |
| Kein ES-Cluster | Single-Node für Demo/Dev, Production bräuchte 3+ Nodes |
| Kein ML-Scoring | Regelbasiertes Scoring reicht für den Use Case |
| Kein Frontend | Kibana + Swagger UI decken Visualisierung ab |
| Kein Echtzeit-System | 6h-Intervall reicht, Echtzeit wäre 100× teurer an Tokens |

### Bekannte Limitationen (ehrlich sein!)

- **Nur deutscher Markt:** Multi-Market ist architektonisch vorbereitet, aber aktuell queried der Code nur domain_id=3 (DE)
- **Seed-Daten nicht perfekt:** Manche ASINs sind keine Keyboards (Keepa-Kategorie zu breit)
- **Preise teilweise 0.0:** Keepa liefert nicht für alle ASINs Preise
- **Prototype, kein Production-System:** Single-Node ES, kein SSL, keine Auth

### Was in Production anders wäre

```
Dev/Demo (jetzt)              →  Production
──────────────────────────────────────────────
Single-Node ES                →  3-Node Cluster mit Replicas
1 Kafka Broker                →  3 Broker mit Replication Factor 2
Keine Auth                    →  OAuth2 + API Keys
6h Intervall                  →  Dynamisch nach Token-Budget
50 Seed-ASINs                 →  10.000+ mit automatischer Discovery
Kein Monitoring               →  Prometheus + Grafana
```

---

## 8. Die 5 Prof-Killer-Fragen

### "Warum Kafka UND PostgreSQL?"

> "PostgreSQL speichert den State — was ist der aktuelle Preis. Kafka streamt die Events — was ist passiert. PostgreSQL gibt ACID-Garantien. Kafka entkoppelt Producer von Consumer, so kann ich neue Services hinzufügen ohne bestehenden Code zu ändern."

### "Wie funktioniert euer Rate Limiting?"

> "Token Bucket Algorithmus: 20 Tokens pro Minute. Jeder API-Call kostet Tokens. Keepa meldet nach jedem Call die verbleibenden Tokens zurück. Wenn leer, wartet mein Code asynchron — er blockiert nicht das gesamte System. Ein asyncio Lock verhindert Race Conditions bei parallelen Requests."

### "Was passiert wenn Kafka ausfällt?"

> "Graceful Degradation. Der Scheduler loggt eine Warnung und läuft weiter. Preise werden weiterhin in PostgreSQL geschrieben. Nur die Kafka-Events gehen verloren. Das ist eine bewusste Design-Entscheidung — kein Retry-Buffer, zugunsten von Einfachheit."

### "Warum nicht alles in einer Datenbank?"

> "Jedes System hat eine Stärke die die anderen nicht haben. PostgreSQL: ACID-Transaktionen und relationale Verknüpfungen. Elasticsearch: Full-Text-Suche in Millisekunden. Kafka: Entkopplung und Replay von Events. Man könnte alles in PostgreSQL machen, aber die Suche wäre langsam und die Kopplung eng."

### "Wie würdet ihr das System skalieren?"

> "Drei Hebel: Kafka bekommt mehr Partitions und Consumer für parallele Verarbeitung. Elasticsearch geht von Single-Node auf einen 3-Node-Cluster mit Sharding. Der Scheduler wird auf mehrere Instanzen verteilt mit Offset-Koordination. PostgreSQL wäre der Bottleneck — da würde man Read Replicas oder Partitionierung der Price-History-Tabelle einsetzen."

---

## 9. Zusammenfassung in einem Absatz

> "Mein System überwacht Amazon-Keyboard-Preise über die Keepa API. Ein Scheduler fragt alle 6 Stunden Preise ab und sammelt jede Stunde neue Deals. Jede Preisänderung wird dreifach geschrieben: PostgreSQL als Source of Truth, Kafka für Event-Streaming, Elasticsearch für Full-Text-Suche. Kibana visualisiert die Daten in Dashboards. Wenn ein Preis unter den Zielpreis fällt, wird der User per Email, Telegram oder Discord benachrichtigt. Das System läuft als 7 Docker Container und ist über eine FastAPI REST-API erreichbar."

---

*Erstellt am 2026-02-26 — Keeper System Prüfungspräsentation*
