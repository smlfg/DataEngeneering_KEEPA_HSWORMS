# Elasticsearch - NoSQL Datenbank

## Was ist Elasticsearch?

**Elasticsearch** ist eine **NoSQL-Datenbank**, die speziell für **schnelle Suche** und **große Datenmengen** entwickelt wurde.

### Der Unterschied zu SQL-Datenbanken

| **SQL (z.B. MySQL)** | **NoSQL (Elasticsearch)** |
|----------------------|---------------------------|
| Tabellen mit festen Spalten | Flexible JSON-Dokumente |
| Langsam bei Textsuche | Sehr schnell bei Suche |
| Gut für Transaktionen | Gut für Analysen |
| Vertikal skalierbar | Horizontal skalierbar |

## Kernkonzepte

### 1. **Index** (= Datenbank)

Ein Index ist wie eine Datenbank in SQL. In unserem System:

```
Index: "products"
```

Hier werden alle Amazon-Produkte gespeichert.

### 2. **Dokument** (= Zeile/Row)

Ein Dokument ist ein einzelner Datensatz im JSON-Format.

**Beispiel-Produkt in Elasticsearch:**

```json
{
  "_index": "products",
  "_id": "B0D1XD1ZV3",
  "_source": {
    "asin": "B0D1XD1ZV3",
    "title": "Amazon Echo Dot (5th Gen)",
    "brand": "Amazon",
    "current_prices": {
      "DE": 4999,
      "IT": 5499,
      "ES": 4799,
      "UK": 4500,
      "FR": 5200
    },
    "last_updated": "2026-01-11T12:05:00Z"
  }
}
```

### 3. **Mapping** (= Schema)

Das Mapping definiert, welche Felder welchen Datentyp haben.

**Unser Produkt-Mapping:**

```json
{
  "mappings": {
    "properties": {
      "asin": { "type": "keyword" },
      "title": { "type": "text" },
      "brand": { "type": "keyword" },
      "current_prices": {
        "properties": {
          "DE": { "type": "integer" },
          "IT": { "type": "integer" },
          "ES": { "type": "integer" }
        }
      },
      "last_updated": { "type": "date" }
    }
  }
}
```

## Wie funktioniert die Suche?

### Inverted Index (Umgekehrter Index)

Elasticsearch erstellt einen **Inverted Index**, der schnelle Textsuche ermöglicht.

**Normaler Index (wie ein Buch):**
```
Seite 1 → "Amazon Echo Dot"
Seite 2 → "Kindle Paperwhite"
Seite 3 → "Amazon Fire TV"
```

**Inverted Index (wie ein Stichwortverzeichnis):**
```
"Amazon" → [Seite 1, Seite 3]
"Echo" → [Seite 1]
"Kindle" → [Seite 2]
"Fire" → [Seite 3]
```

### Suchbeispiel

**Query:**
```json
GET /products/_search
{
  "query": {
    "match": {
      "title": "Echo"
    }
  }
}
```

**Ergebnis:** Alle Produkte mit "Echo" im Titel in < 10ms!

## Elasticsearch in unserem System

### Wie wir Elasticsearch nutzen

```
┌──────────────┐     ┌──────────────────┐
│   Consumer   │────▶│  Elasticsearch   │
│  (Enricher)  │     │   Index: products│
└──────────────┘     └──────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  Arbitrage       │
                     │  Detector        │
                     └──────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │   Dashboard      │
                     └──────────────────┘
```

### 1. **Produkt-Speicherung** (Consumer)

Der Enrichment-Consumer schreibt Produkte in Elasticsearch:

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(["http://elasticsearch:9200"])

# Produkt speichern
es.index(
    index="products",
    id="B0D1XD1ZV3",
    document={
        "asin": "B0D1XD1ZV3",
        "title": "Amazon Echo Dot",
        "current_prices": {
            "DE": 4999,
            "IT": 5499
        }
    }
)
```

### 2. **Arbitrage-Suche** (Detector)

Der Arbitrage-Detector findet profitable Produkte:

```python
# Suche alle aktiven Produkte
response = es.search(
    index="products",
    query={
        "bool": {
            "must": [
                {"term": {"is_active": True}},
                {"exists": {"field": "current_prices.DE"}},
                {"exists": {"field": "current_prices.IT"}}
            ]
        }
    },
    size=1000
)

for hit in response["hits"]["hits"]:
    product = hit["_source"]
    # Berechne Margin zwischen DE und IT
    margin = product["current_prices"]["IT"] - product["current_prices"]["DE"]
```

### 3. **Dashboard-Abfragen** (API)

Die FastAPI liest Daten für das Dashboard:

```python
# Top 10 Arbitrage-Opportunities
response = es.search(
    index="products",
    query={"match_all": {}},
    sort=[{"margin_percentage": {"order": "desc"}}],
    size=10
)
```

## Wichtige Operationen

### Dokument einfügen/aktualisieren

```python
# Neues Produkt
es.index(index="products", id="ASIN123", document={...})

# Aktualisieren
es.update(index="products", id="ASIN123", doc={
    "current_prices": {"DE": 5999}
})
```

### Suchen

```python
# Alle Produkte mit Preis < 50€
es.search(index="products", query={
    "range": {
        "current_prices.DE": {"lte": 5000}
    }
})
```

### Löschen

```python
# Einzelnes Produkt
es.delete(index="products", id="ASIN123")

# Alle Produkte älter als 30 Tage
es.delete_by_query(index="products", query={
    "range": {
        "last_updated": {"lt": "now-30d"}
    }
})
```

## Vorteile von Elasticsearch

### ✅ Geschwindigkeit
- Millionen Dokumente in Millisekunden durchsuchen
- Inverted Index für schnelle Textsuche
- In-Memory-Caching

### ✅ Skalierbarkeit
- Horizontal skalierbar (einfach weitere Nodes hinzufügen)
- Automatisches Sharding (Datenverteilung)
- Replikation für Ausfallsicherheit

### ✅ Flexibilität
- Schema-less (Felder können nachträglich hinzugefügt werden)
- JSON-Format (einfach zu verarbeiten)
- Keine Joins notwendig

### ✅ Analytics
- Aggregationen (Durchschnitt, Summe, Min, Max)
- Histogramme und Statistiken
- Zeitreihenanalyse

## Elasticsearch Architektur

### Cluster, Nodes, Shards

```
┌─────────────────────────────────────────┐
│           Elasticsearch Cluster          │
│                                          │
│  ┌─────────────┐      ┌─────────────┐  │
│  │   Node 1    │      │   Node 2    │  │
│  │             │      │             │  │
│  │ Shard 0     │      │ Shard 1     │  │
│  │ Shard 2     │      │ Replica 0   │  │
│  └─────────────┘      └─────────────┘  │
└─────────────────────────────────────────┘
```

- **Cluster**: Gruppe von Elasticsearch-Servern
- **Node**: Ein einzelner Elasticsearch-Server
- **Shard**: Teil eines Index (Datenpartition)
- **Replica**: Kopie eines Shards (Backup)

In unserem System: **Single-Node-Cluster** (Entwicklung)

## Elasticsearch Konfiguration

**In docker-compose.yml:**

```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
  environment:
    - discovery.type=single-node      # Kein Cluster
    - xpack.security.enabled=false    # Keine Authentifizierung
    - "ES_JAVA_OPTS=-Xms512m -Xmx512m"  # 512MB RAM
  ports:
    - "9200:9200"  # REST API
    - "9300:9300"  # Node-to-Node Kommunikation
```

## Kibana - Visualisierung

**Kibana** ist das Web-UI für Elasticsearch.

**Zugriff:** http://localhost:5601

### Was kann Kibana?

1. **Dev Tools**: Elasticsearch-Queries testen
2. **Discover**: Dokumente durchsuchen
3. **Visualize**: Grafiken erstellen
4. **Dashboard**: Metriken überwachen

**Beispiel - Alle Produkte anzeigen:**

```
GET /products/_search
{
  "query": {
    "match_all": {}
  }
}
```

## Performance-Tipps

### 1. **Bulk-Operationen**

Statt einzelner Inserts:

```python
# Langsam (1000 Requests)
for product in products:
    es.index(index="products", document=product)

# Schnell (1 Request)
from elasticsearch.helpers import bulk

actions = [
    {"_index": "products", "_id": p["asin"], "_source": p}
    for p in products
]
bulk(es, actions)
```

### 2. **Refresh Interval**

```python
# Für schnelle Bulk-Inserts
es.indices.put_settings(index="products", body={
    "index": {"refresh_interval": "30s"}
})
```

### 3. **Mapping vorher definieren**

Bessere Performance durch korrektes Mapping:

```python
es.indices.create(index="products", mappings={...})
```

## Zusammenfassung

| **Feature** | **Beschreibung** | **Unser Einsatz** |
|-------------|------------------|-------------------|
| **Index** | Datenbank | `products` |
| **Dokument** | JSON-Objekt | Produkt-Daten |
| **Search** | Schnelle Suche | Arbitrage-Finder |
| **Aggregation** | Statistiken | Preis-Durchschnitte |
| **Kibana** | Web-UI | Daten-Exploration |

**Elasticsearch macht unser System:**
- ⚡ Schnell (Millionen Produkte durchsuchbar)
- 📈 Skalierbar (mehr Daten = kein Problem)
- 🔍 Durchsuchbar (komplexe Queries)
- 📊 Analysierbar (Statistiken & Trends)
