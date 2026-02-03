# System Übersicht - Amazon Arbitrage Tracker

## Was ist dieses System?

Das **Amazon Arbitrage Tracker System** ist eine vollautomatische Datenengineering-Pipeline, die **Preisunterschiede zwischen verschiedenen Amazon-Marktplätzen in Europa** findet und analysiert.

### Das Prinzip: Arbitrage

**Arbitrage** bedeutet: Ein Produkt in einem Land günstig kaufen und in einem anderen teurer verkaufen.

**Beispiel:**
- Ein Produkt kostet auf Amazon Deutschland: **99,99€**
- Dasselbe Produkt kostet auf Amazon Italien: **129,99€**
- **Arbitrage-Möglichkeit**: 30€ Gewinn pro Verkauf!

## System-Architektur auf einen Blick

```
┌─────────────┐     ┌──────────┐     ┌────────────────┐     ┌──────────────┐
│   Keepa     │────▶│  Kafka   │────▶│ Elasticsearch  │────▶│  Dashboard   │
│   API       │     │ (Queue)  │     │   (Database)   │     │ (Streamlit)  │
└─────────────┘     └──────────┘     └────────────────┘     └──────────────┘
     ▲                    │                    │                     ▲
     │                    ▼                    ▼                     │
     │             ┌──────────────┐    ┌──────────────┐            │
     │             │   Consumer   │    │  Arbitrage   │            │
     └─────────────│  (Enricher)  │    │  Detector    │────────────┘
      (Airflow)    └──────────────┘    └──────────────┘
```

## Die 5 Hauptkomponenten

### 1. **Keepa API** (Datenquelle)
- Sammelt Preis-Daten von Amazon Marktplätzen
- Liefert Produkt-Informationen (Titel, Bilder, Preise)
- Historische Preisentwicklung

### 2. **Apache Kafka** (Message Queue)
- Verbindet alle Services
- Ermöglicht asynchrone Datenverarbeitung
- Garantiert, dass keine Daten verloren gehen

### 3. **Elasticsearch** (NoSQL Datenbank)
- Speichert alle Produkt-Daten
- Ermöglicht schnelle Suche über Millionen Produkte
- Optimiert für große Datenmengen

### 4. **Airflow** (Scheduler/Orchestrator)
- Plant regelmäßige Datenabfragen
- Überwacht alle Prozesse
- Startet Tasks automatisch

### 5. **Streamlit Dashboard** (UI)
- Visualisiert gefundene Arbitrage-Möglichkeiten
- Interaktive Filter (Mindestmarge, Zielmarkt, etc.)
- Echtzeit-Updates

## Datenfluss im Detail

### Schritt 1: Daten sammeln (Producer)
```
Producer → Keepa API abfragen
         → Produkt-Daten erhalten
         → An Kafka senden
```

### Schritt 2: Daten anreichern (Consumer)
```
Consumer → Von Kafka lesen
         → Daten validieren & bereinigen
         → Zusätzliche Infos hinzufügen
         → In Elasticsearch speichern
```

### Schritt 3: Arbitrage erkennen (Arbitrage Detector)
```
Detector → Produkte aus Elasticsearch laden
         → Preise zwischen Märkten vergleichen
         → Margen berechnen
         → Profitable Opportunities identifizieren
```

### Schritt 4: Visualisieren (Dashboard)
```
Dashboard → Opportunities aus Elasticsearch laden
          → Nach Margin/Profit sortieren
          → Interaktiv anzeigen
          → Filter ermöglichen
```

## Warum diese Architektur?

### ✅ Skalierbar
- Kann Millionen Produkte verarbeiten
- Jeder Service läuft unabhängig

### ✅ Fehlertolerant
- Kafka garantiert Datenlieferung
- Services können abstürzen und neu starten
- Keine Datenverluste

### ✅ Modular
- Jeder Service macht nur eine Sache
- Einfach zu testen
- Leicht zu erweitern

### ✅ Echtzeit
- Neue Preise sofort verfügbar
- Dashboard updated automatisch
- Keine Verzögerung

## Die verwendeten Technologien

| Technologie | Zweck | Details |
|-------------|-------|---------|
| **Python** | Programmiersprache | Alle Services |
| **Docker** | Containerisierung | Isolierte Services |
| **Kafka** | Message Queue | Event Streaming |
| **Elasticsearch** | NoSQL Database | Produkt-Speicher |
| **Airflow** | Workflow Scheduler | Task-Orchestrierung |
| **FastAPI** | REST API | Backend |
| **Streamlit** | Dashboard | Frontend |
| **Poetry** | Dependency Management | Python Packages |
| **Keepa** | Datenquelle | Amazon Preise |

## Nächste Schritte

Lies die einzelnen Erklärungen für jede Komponente:

1. [Elasticsearch erklärt](./01_Elasticsearch.md) - NoSQL Datenbank
2. [Kafka erklärt](./02_Kafka.md) - Message Queue System
3. [Keepa API erklärt](./03_Keepa.md) - Amazon Datenquelle
4. [Airflow erklärt](./04_Airflow.md) - Workflow Scheduler
5. [Docker erklärt](./05_Docker.md) - Containerisierung
6. [FastAPI erklärt](./06_FastAPI.md) - REST API Framework
7. [Streamlit erklärt](./07_Streamlit.md) - Dashboard Framework
8. [Poetry erklärt](./08_Poetry.md) - Dependency Management
9. [Gesamtsystem](./09_System_Architecture.md) - Wie alles zusammenspielt
