# Apache Kafka - Message Queue System

## Was ist Apache Kafka?

**Apache Kafka** ist ein **verteiltes Event-Streaming-System** für asynchrone Datenverarbeitung.

### Einfach erklärt: Die Post-Analogie

```
┌─────────────┐     ┌──────────┐     ┌─────────────┐
│   Absender  │────▶│ Postfach │────▶│ Empfänger   │
│  (Producer) │     │ (Topic)  │     │ (Consumer)  │
└─────────────┘     └──────────┘     └─────────────┘
```

- **Producer** = Absender (schreibt Nachrichten)
- **Topic** = Postfach (speichert Nachrichten)
- **Consumer** = Empfänger (liest Nachrichten)

## Warum Kafka statt direkter Kommunikation?

### ❌ Ohne Kafka (Direkt):

```
Producer ────▶ Consumer 1
         ────▶ Consumer 2
         ────▶ Consumer 3
```

**Probleme:**
- Producer muss auf alle Consumer warten
- Wenn Consumer 2 abstürzt, gehen Daten verloren
- Schwer skalierbar

### ✅ Mit Kafka:

```
Producer ────▶ Kafka Topic ────▶ Consumer 1
                           ────▶ Consumer 2
                           ────▶ Consumer 3
```

**Vorteile:**
- Producer sendet einmal und ist fertig
- Nachrichten bleiben gespeichert (keine Verluste)
- Consumer lesen in eigenem Tempo
- Einfach neue Consumer hinzufügen

## Kernkonzepte

### 1. **Topic** (Thema/Kategorie)

Ein Topic ist wie ein Ordner für Nachrichten.

**Unsere Topics:**

```
raw.keepa_updates      → Rohdaten von Keepa API
products.enriched      → Angereicherte Produkt-Daten
arbitrage.alerts       → Gefundene Arbitrage-Möglichkeiten
```

### 2. **Producer** (Daten-Sender)

Ein Producer schreibt Nachrichten in Topics.

**Unser Producer:**

```python
from confluent_kafka import Producer

producer = Producer({'bootstrap.servers': 'kafka:9092'})

# Produkt-Daten senden
product_data = {
    "asin": "B0D1XD1ZV3",
    "title": "Amazon Echo Dot",
    "prices": {"DE": 4999, "IT": 5499}
}

producer.produce(
    topic='raw.keepa_updates',
    value=json.dumps(product_data).encode('utf-8'),
    key=product_data['asin'].encode('utf-8')
)

producer.flush()  # Warten bis gesendet
```

### 3. **Consumer** (Daten-Empfänger)

Ein Consumer liest Nachrichten aus Topics.

**Unser Enrichment-Consumer:**

```python
from confluent_kafka import Consumer

consumer = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'enrichment-consumer',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['raw.keepa_updates'])

while True:
    msg = consumer.poll(1.0)  # Warte 1 Sekunde auf Nachricht

    if msg is None:
        continue

    product_data = json.loads(msg.value().decode('utf-8'))

    # Daten anreichern und in Elasticsearch speichern
    enriched = enrich_product(product_data)
    save_to_elasticsearch(enriched)

    consumer.commit()  # Markiere als verarbeitet
```

### 4. **Consumer Group** (Verbraucher-Gruppe)

Mehrere Consumer in einer Gruppe teilen sich die Arbeit.

```
Topic (Partition 0) ────▶ Consumer A ┐
Topic (Partition 1) ────▶ Consumer B ├─ Consumer Group
Topic (Partition 2) ────▶ Consumer C ┘
```

**Vorteil:** Parallele Verarbeitung = höherer Durchsatz

### 5. **Partition** (Teil-Warteschlange)

Ein Topic ist in Partitionen aufgeteilt.

```
Topic: raw.keepa_updates

Partition 0: [MSG1, MSG4, MSG7]
Partition 1: [MSG2, MSG5, MSG8]
Partition 2: [MSG3, MSG6, MSG9]
```

**Regeln:**
- Nachrichten mit gleichem **Key** gehen in gleiche Partition
- Reihenfolge nur **innerhalb einer Partition** garantiert

### 6. **Offset** (Position)

Der Offset ist die Position einer Nachricht in der Partition.

```
Partition 0: [MSG1, MSG2, MSG3, MSG4, MSG5]
Offset:       0     1     2     3     4
                          ↑
                    Consumer-Position
```

**Commit:** Consumer sagt Kafka "Ich habe bis Offset 2 verarbeitet"

## Kafka in unserem System

### Datenfluss

```
┌──────────────┐
│   Producer   │
│ (Keepa API)  │
└──────┬───────┘
       │ Sendet Rohdaten
       ▼
┌─────────────────────────┐
│ Topic: raw.keepa_updates│
└──────┬──────────────────┘
       │ Liest Rohdaten
       ▼
┌──────────────────────┐
│ Enrichment Consumer  │
│ - Validiert Daten    │
│ - Speichert in ES    │
└──────┬───────────────┘
       │ Sendet angereicherte Daten
       ▼
┌─────────────────────────┐
│ Topic: products.enriched│
└──────┬──────────────────┘
       │ Liest Produkte
       ▼
┌──────────────────────┐
│ Arbitrage Detector   │
│ - Vergleicht Preise  │
│ - Findet Margins     │
└──────┬───────────────┘
       │ Sendet Alerts
       ▼
┌─────────────────────┐
│ Topic: arbitrage.   │
│       alerts        │
└─────────────────────┘
```

### Topic-Konfiguration

**In docker-compose.yml:**

```yaml
kafka:
  environment:
    KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
    KAFKA_NUM_PARTITIONS: 3              # 3 Partitionen pro Topic
    KAFKA_LOG_RETENTION_HOURS: 168       # 7 Tage Speicherung
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

**Manuelle Erstellung:**

```bash
kafka-topics.sh --bootstrap-server kafka:9092 \
  --create \
  --topic raw.keepa_updates \
  --partitions 3 \
  --replication-factor 1
```

## Message Format

### Anatomy einer Kafka-Nachricht

```json
{
  "key": "B0D1XD1ZV3",           // ASIN als Key
  "value": {                      // Payload (JSON)
    "asin": "B0D1XD1ZV3",
    "title": "Amazon Echo Dot",
    "domain_id": 1,
    "current_prices": {
      "DE": 4999,
      "IT": 5499
    },
    "timestamp": "2026-01-11T12:00:00Z"
  },
  "timestamp": 1736597520000,     // Kafka-Timestamp
  "partition": 1,                 // Partition
  "offset": 42                    // Position
}
```

### Warum Keys wichtig sind

```python
# Mit Key (ASIN) → Gleiche Partition
producer.produce(
    topic='raw.keepa_updates',
    key='B0D1XD1ZV3',  # Alle Updates für dieses Produkt in Partition 1
    value=product_json
)

# Ohne Key → Zufällige Partition
producer.produce(
    topic='raw.keepa_updates',
    value=product_json  # Round-robin über Partitionen
)
```

**Vorteil mit Key:** Reihenfolge für ein Produkt garantiert

## Garantien & Zuverlässigkeit

### At-Least-Once Delivery

Kafka garantiert: **Jede Nachricht wird mindestens einmal zugestellt**

```python
# Producer: Warte auf Bestätigung
producer = Producer({
    'bootstrap.servers': 'kafka:9092',
    'acks': 'all',  # Warte auf alle Replicas
    'retries': 3    # 3 Versuche bei Fehler
})
```

### Consumer Offset Management

```python
# Auto-Commit (alle 5 Sekunden)
consumer = Consumer({
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 5000
})

# Manuelles Commit (sicherer)
consumer = Consumer({
    'enable.auto.commit': False
})

msg = consumer.poll()
process(msg)
consumer.commit()  # Erst nach erfolgreicher Verarbeitung
```

## Kafka Monitoring

### Topics anzeigen

```bash
docker exec arbitrage-kafka kafka-topics.sh \
  --bootstrap-server kafka:9092 \
  --list
```

**Output:**
```
raw.keepa_updates
products.enriched
arbitrage.alerts
```

### Nachrichten konsumieren (Debugging)

```bash
docker exec arbitrage-kafka kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 \
  --topic raw.keepa_updates \
  --from-beginning
```

### Consumer Groups anzeigen

```bash
docker exec arbitrage-kafka kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --list
```

**Output:**
```
enrichment-consumer
arbitrage-detector
```

### Offset-Status prüfen

```bash
docker exec arbitrage-kafka kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --group enrichment-consumer \
  --describe
```

**Output:**
```
TOPIC              PARTITION  CURRENT-OFFSET  LAG
raw.keepa_updates  0          142             0
raw.keepa_updates  1          138             2
raw.keepa_updates  2          145             0
```

- **CURRENT-OFFSET**: Wo steht der Consumer
- **LAG**: Wie viele Nachrichten noch ausstehend

## Vorteile von Kafka

### ✅ Entkopplung
Producer und Consumer kennen sich nicht → unabhängige Entwicklung

### ✅ Pufferung
Kafka speichert Nachrichten → Consumer können in eigenem Tempo lesen

### ✅ Skalierbarkeit
Mehr Partitionen = mehr parallele Consumer möglich

### ✅ Replay
Consumer können alte Nachrichten nochmal lesen (Offset zurücksetzen)

### ✅ Persistenz
Nachrichten werden 7 Tage gespeichert (konfigurierbar)

## Typische Anwendungsfälle

### 1. **Event Streaming**
Echtzeit-Verarbeitung von Events (Clicks, Logs, Sensordaten)

### 2. **Microservices-Kommunikation**
Services kommunizieren über Events statt direkte Calls

### 3. **Data Pipeline**
ETL-Prozesse (Extract, Transform, Load)

### 4. **Log Aggregation**
Zentrale Sammlung von Logs aus verteilten Systemen

## Kafka vs. andere Message Queues

| Feature | Kafka | RabbitMQ | Redis |
|---------|-------|----------|-------|
| **Durchsatz** | Sehr hoch | Mittel | Hoch |
| **Persistenz** | Ja (Disk) | Optional | Optional |
| **Replay** | Ja | Nein | Nein |
| **Latency** | ~10ms | ~1ms | <1ms |
| **Best for** | Big Data | Task Queue | Caching |

## Zookeeper - Kafka's Koordinator

**Zookeeper** verwaltet Kafka-Cluster-Metadaten.

```yaml
zookeeper:
  image: confluentinc/cp-zookeeper:7.5.0
  environment:
    ZOOKEEPER_CLIENT_PORT: 2181
```

**Was macht Zookeeper?**
- Leader-Election für Partitionen
- Broker-Registrierung
- Topic-Konfiguration
- Consumer-Group-Koordination

**Hinweis:** Ab Kafka 3.x kann Zookeeper durch **KRaft** ersetzt werden.

## Performance-Tipps

### 1. Batch-Größe optimieren

```python
producer = Producer({
    'batch.size': 16384,        # 16KB Batches
    'linger.ms': 10,            # Warte 10ms für mehr Nachrichten
    'compression.type': 'snappy'  # Kompression
})
```

### 2. Parallele Consumer

```yaml
# docker-compose.yml
enrichment-consumer:
  deploy:
    replicas: 3  # 3 Consumer-Instanzen
```

### 3. Mehr Partitionen

```bash
# Für hohen Durchsatz
kafka-topics.sh --alter --topic raw.keepa_updates --partitions 10
```

## Troubleshooting

### Consumer hängt fest (Lag wächst)

```bash
# Lag prüfen
kafka-consumer-groups.sh --describe --group enrichment-consumer

# Lösung: Mehr Consumer starten
docker compose up -d --scale enrichment-consumer=3
```

### Nachrichten verloren

```python
# Producer: Warte auf Bestätigung
producer = Producer({'acks': 'all'})

# Consumer: Manuelles Commit
consumer.commit(asynchronous=False)
```

### Disk voll

```yaml
# Retention reduzieren
kafka:
  environment:
    KAFKA_LOG_RETENTION_HOURS: 24  # Nur 1 Tag statt 7
```

## Zusammenfassung

| **Komponente** | **Zweck** | **Unser Setup** |
|----------------|-----------|-----------------|
| **Broker** | Kafka-Server | kafka:9092 |
| **Zookeeper** | Koordination | zookeeper:2181 |
| **Topics** | Nachrichten-Kategorien | raw.keepa_updates, products.enriched, arbitrage.alerts |
| **Partitions** | Parallelisierung | 3 pro Topic |
| **Retention** | Speicherdauer | 7 Tage |

**Kafka macht unser System:**
- 🔄 Asynchron (Services warten nicht aufeinander)
- 🛡️ Robust (keine Nachrichtenverluste)
- 📈 Skalierbar (einfach mehr Consumer)
- 🔁 Wiederholbar (Daten können neu verarbeitet werden)
