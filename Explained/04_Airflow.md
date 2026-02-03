# Apache Airflow - Workflow Orchestration

## Was ist Apache Airflow?

**Apache Airflow** ist ein **Workflow-Scheduler**, der **Daten-Pipelines automatisiert** und **überwacht**.

### Einfach erklärt: Der Projektmanager

```
Airflow = Projektmanager, der Tasks plant und überwacht
DAG = Projekt mit mehreren abhängigen Aufgaben
Task = Einzelne Aufgabe (z.B. "Daten laden")
Schedule = Wann wird das Projekt ausgeführt (täglich, stündlich, etc.)
```

## Kernkonzepte

### 1. **DAG** (Directed Acyclic Graph)

Ein DAG ist ein **Workflow** - eine Sammlung von Tasks mit Abhängigkeiten.

**Beispiel:**

```python
from airflow import DAG
from datetime import datetime, timedelta

default_args = {
    'owner': 'arbitrage-system',
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'keepa_data_pipeline',
    default_args=default_args,
    description='Fetch Keepa data and process',
    schedule_interval='0 * * * *',  # Jede Stunde
    start_date=datetime(2026, 1, 1),
    catchup=False
)
```

**Visualisierung:**

```
┌─────────────────┐
│ Fetch Keepa     │
│ Bestsellers     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query Product   │
│ Details         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Send to Kafka   │
└─────────────────┘
```

### 2. **Task** (Aufgabe)

Ein Task ist eine **einzelne Operation** im Workflow.

**Task-Typen:**

```python
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Python-Funktion ausführen
python_task = PythonOperator(
    task_id='fetch_keepa_data',
    python_callable=fetch_data_from_keepa,
    dag=dag
)

# Bash-Befehl ausführen
bash_task = BashOperator(
    task_id='cleanup_old_files',
    bash_command='rm -f /tmp/old_data.json',
    dag=dag
)
```

### 3. **Operator** (Task-Template)

Operatoren definieren **was** ein Task macht.

**Wichtige Operatoren:**

| Operator | Zweck | Beispiel |
|----------|-------|----------|
| `PythonOperator` | Python-Funktion | `fetch_data()` |
| `BashOperator` | Shell-Befehl | `curl API` |
| `HttpOperator` | HTTP-Request | API-Call |
| `EmailOperator` | E-Mail senden | Alert |
| `KafkaProducerOperator` | Kafka-Nachricht | Daten senden |

### 4. **Schedule Interval** (Zeitplan)

Definiert **wann** der DAG läuft.

**Cron-Syntax:**

```python
# Jede Stunde
schedule_interval='0 * * * *'

# Jeden Tag um 6 Uhr
schedule_interval='0 6 * * *'

# Jede 15 Minuten
schedule_interval='*/15 * * * *'

# Manuell (kein automatischer Trigger)
schedule_interval=None
```

**Timedelta-Syntax:**

```python
from datetime import timedelta

# Alle 2 Stunden
schedule_interval=timedelta(hours=2)

# Alle 30 Minuten
schedule_interval=timedelta(minutes=30)
```

## Airflow in unserem System

### Unser DAG: Keepa Category Scraper

**Datei:** `dags/keepa_category_scraper_dag.py`

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import yaml
import requests
from confluent_kafka import Producer

# Konfiguration laden
def load_category_config():
    with open('/opt/airflow/config/categories.yaml', 'r') as f:
        return yaml.safe_load(f)

# Keepa Bestsellers abrufen
def fetch_bestsellers_for_category(category_id, domain, **context):
    api_key = "YOUR_API_KEY"
    response = requests.get(
        f"https://api.keepa.com/bestsellers",
        params={
            "key": api_key,
            "domain": domain,
            "category": category_id,
            "range": 100
        }
    )
    asins = response.json().get("bestsellers", [])
    return asins

# Produkt-Details abrufen
def fetch_product_details(asins, domain, **context):
    api_key = "YOUR_API_KEY"
    response = requests.get(
        f"https://api.keepa.com/product",
        params={
            "key": api_key,
            "domain": domain,
            "asin": ",".join(asins),
            "stats": "30"
        }
    )
    return response.json().get("products", [])

# An Kafka senden
def send_to_kafka(products, **context):
    producer = Producer({'bootstrap.servers': 'kafka:9092'})

    for product in products:
        producer.produce(
            topic='raw.keepa_updates',
            key=product['asin'].encode('utf-8'),
            value=json.dumps(product).encode('utf-8')
        )

    producer.flush()

# DAG Definition
default_args = {
    'owner': 'arbitrage-system',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'keepa_category_scraper',
    default_args=default_args,
    description='Scrape Keepa categories for arbitrage opportunities',
    schedule_interval=timedelta(hours=2),  # Alle 2 Stunden
    start_date=datetime(2026, 1, 1),
    catchup=False
)

# Tasks
fetch_bestsellers = PythonOperator(
    task_id='fetch_bestsellers',
    python_callable=fetch_bestsellers_for_category,
    op_kwargs={'category_id': 3581, 'domain': 3},  # Elektronik DE
    dag=dag
)

fetch_details = PythonOperator(
    task_id='fetch_product_details',
    python_callable=fetch_product_details,
    op_kwargs={'domain': 3},
    dag=dag
)

send_kafka = PythonOperator(
    task_id='send_to_kafka',
    python_callable=send_to_kafka,
    dag=dag
)

# Task-Abhängigkeiten
fetch_bestsellers >> fetch_details >> send_kafka
```

### Task-Abhängigkeiten

```python
# Sequenziell (A → B → C)
task_a >> task_b >> task_c

# Parallel (A → [B, C] → D)
task_a >> [task_b, task_c] >> task_d

# Komplexe Abhängigkeiten
#     A
#    / \
#   B   C
#    \ /
#     D
task_a >> task_b >> task_d
task_a >> task_c >> task_d
```

## Airflow Architektur

### Komponenten

```
┌─────────────────────────────────────────┐
│         Airflow System                  │
│                                         │
│  ┌─────────────┐    ┌──────────────┐  │
│  │  Webserver  │    │  Scheduler   │  │
│  │  (UI)       │    │  (Trigger)   │  │
│  └─────────────┘    └──────────────┘  │
│                                         │
│  ┌─────────────┐    ┌──────────────┐  │
│  │  Worker     │    │  Metadata DB │  │
│  │  (Execute)  │    │  (Postgres)  │  │
│  └─────────────┘    └──────────────┘  │
│                                         │
│  ┌─────────────┐                       │
│  │  Redis      │                       │
│  │  (Queue)    │                       │
│  └─────────────┘                       │
└─────────────────────────────────────────┘
```

### 1. **Webserver** (UI)

- **Zugriff:** http://localhost:8080
- **Login:** admin / admin
- **Features:**
  - DAGs visualisieren
  - Tasks starten/stoppen
  - Logs anzeigen
  - Monitoring

### 2. **Scheduler** (Planer)

- Prüft Schedule Intervals
- Triggert DAG-Runs
- Verteilt Tasks an Worker

### 3. **Worker** (Ausführer)

- Führt Tasks aus
- Nutzt Celery für Parallelität
- Kann skaliert werden

### 4. **Metadata DB** (PostgreSQL)

- Speichert DAG-Definitionen
- Task-Status
- Logs
- Benutzer & Permissions

### 5. **Redis** (Message Broker)

- Queue für Celery
- Verteilung von Tasks an Worker

## Executor-Typen

### SequentialExecutor (Entwicklung)

```yaml
environment:
  - AIRFLOW__CORE__EXECUTOR=SequentialExecutor
```

- ❌ Ein Task nach dem anderen
- ✅ Einfach zu debuggen
- ⚠️ Nur für Tests

### LocalExecutor (Kleine Projekte)

```yaml
environment:
  - AIRFLOW__CORE__EXECUTOR=LocalExecutor
```

- ✅ Mehrere Tasks parallel (auf einem Server)
- ❌ Nicht horizontal skalierbar

### CeleryExecutor (Produktion)

```yaml
environment:
  - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
  - AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
```

- ✅ Mehrere Worker-Nodes
- ✅ Horizontal skalierbar
- ✅ Fault-tolerant

**Unser Setup:** CeleryExecutor mit Redis

## Airflow Web UI

### DAGs-Übersicht

```
DAG Name               | Schedule      | Last Run    | Status
-----------------------|---------------|-------------|--------
keepa_category_scraper | */2 hours     | 12:00       | ✅
cleanup_old_data       | 0 6 * * *     | 06:00       | ✅
send_daily_report      | 0 18 * * *    | 18:00       | ❌
```

### DAG Graph View

```
┌──────────────┐
│ fetch_       │
│ bestsellers  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ fetch_       │
│ details      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ send_to_     │
│ kafka        │
└──────────────┘
```

### Task Logs

```
[2026-01-11 12:00:00] INFO - Starting task: fetch_bestsellers
[2026-01-11 12:00:01] INFO - Calling Keepa API...
[2026-01-11 12:00:03] INFO - Received 100 ASINs
[2026-01-11 12:00:03] INFO - Task completed successfully
```

## XCom - Task-Kommunikation

**XCom** (Cross-Communication) ermöglicht **Datenaustausch zwischen Tasks**.

### Daten pushen

```python
def fetch_bestsellers(**context):
    asins = ["B0D1XD1ZV3", "B075CYMYK6"]

    # In XCom speichern
    context['task_instance'].xcom_push(key='asins', value=asins)

    return asins
```

### Daten pullen

```python
def fetch_product_details(**context):
    # Von XCom lesen
    asins = context['task_instance'].xcom_pull(
        task_ids='fetch_bestsellers',
        key='asins'
    )

    # Produkt-Details abrufen
    products = keepa_client.product_query(asins)
    return products
```

### Return Value = Auto-Push

```python
def fetch_bestsellers(**context):
    asins = ["B0D1XD1ZV3"]
    return asins  # Automatisch in XCom

def use_asins(**context):
    asins = context['task_instance'].xcom_pull(task_ids='fetch_bestsellers')
    # asins = ["B0D1XD1ZV3"]
```

## Monitoring & Alerts

### E-Mail bei Fehler

```python
from airflow.operators.email import EmailOperator

default_args = {
    'email': ['admin@example.com'],
    'email_on_failure': True,
    'email_on_retry': False
}
```

### Slack-Benachrichtigung

```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

slack_alert = SlackWebhookOperator(
    task_id='slack_alert',
    http_conn_id='slack_webhook',
    message='Keepa scraper failed!',
    trigger_rule='one_failed'  # Nur bei Fehler
)
```

### Custom Metrics

```python
from airflow.metrics import Stats

def my_task(**context):
    Stats.incr('keepa_products_fetched', count=100)
    Stats.gauge('keepa_api_tokens_remaining', 1200)
```

## Best Practices

### 1. **Idempotenz**

Tasks sollten mehrfach ausführbar sein ohne Probleme:

```python
# ❌ Nicht idempotent
def append_to_file():
    with open('data.txt', 'a') as f:
        f.write('new data')  # Doppelte Daten bei Retry

# ✅ Idempotent
def write_to_file():
    with open('data.txt', 'w') as f:
        f.write('new data')  # Überschreibt alte Daten
```

### 2. **Retries konfigurieren**

```python
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30)
}
```

### 3. **Timeouts setzen**

```python
task = PythonOperator(
    task_id='long_running_task',
    python_callable=slow_function,
    execution_timeout=timedelta(minutes=10),  # Max 10 Minuten
    dag=dag
)
```

### 4. **DAG-File-Structure**

```
dags/
├── keepa_category_scraper_dag.py
├── cleanup_dag.py
└── utils/
    ├── keepa_helpers.py
    └── kafka_helpers.py
```

## Airflow CLI

### DAG-Befehle

```bash
# DAGs auflisten
docker exec arbitrage-airflow-scheduler airflow dags list

# DAG manuell triggern
docker exec arbitrage-airflow-scheduler \
  airflow dags trigger keepa_category_scraper

# DAG pausieren/unpausieren
docker exec arbitrage-airflow-scheduler \
  airflow dags pause keepa_category_scraper
```

### Task-Befehle

```bash
# Task testen (ohne Dependencies)
docker exec arbitrage-airflow-scheduler \
  airflow tasks test keepa_category_scraper fetch_bestsellers 2026-01-11

# Task-Logs anzeigen
docker exec arbitrage-airflow-scheduler \
  airflow tasks logs keepa_category_scraper fetch_bestsellers 2026-01-11
```

## Unser Airflow-Setup

### Docker Compose

```yaml
airflow-webserver:
  image: apache/airflow:2.8.1
  environment:
    - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
    - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
    - AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./config:/opt/airflow/config:ro
  ports:
    - "8080:8080"
```

### DAG-Verzeichnis

```bash
./dags/
└── keepa_category_scraper_dag.py
```

Airflow sucht automatisch nach Python-Files in `./dags/`

## Zusammenfassung

| **Komponente** | **Zweck** | **Unser Setup** |
|----------------|-----------|-----------------|
| **DAG** | Workflow-Definition | `keepa_category_scraper` |
| **Scheduler** | Task-Planung | CeleryExecutor |
| **Worker** | Task-Ausführung | 1 Worker-Node |
| **Webserver** | UI | Port 8080 |
| **Postgres** | Metadaten | Lokaler Container |
| **Redis** | Task-Queue | Lokaler Container |

**Airflow macht unser System:**
- ⏰ Automatisiert (Tasks laufen nach Zeitplan)
- 📊 Überwacht (Web-UI zeigt Status)
- 🔁 Wiederholbar (Retries bei Fehlern)
- 📈 Skalierbar (Mehr Worker bei Bedarf)
