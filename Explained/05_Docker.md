# Docker & Docker Compose - Containerisierung

## Was ist Docker?

**Docker** ermöglicht es, Anwendungen in **isolierten Containern** zu verpacken und auszuführen.

### Die Container-Schiff-Analogie

```
┌─────────────────────────────────────┐
│      Container-Schiff (Server)       │
│                                      │
│  ┌────────┐ ┌────────┐ ┌────────┐  │
│  │Container│ │Container│ │Container│  │
│  │  API   │ │  DB    │ │ Kafka  │  │
│  └────────┘ └────────┘ └────────┘  │
└─────────────────────────────────────┘
```

**Vorteile:**
- 📦 Jeder Container ist isoliert
- 🚢 Einfach zu transportieren (auf andere Server)
- 🔄 Gleich auf allen Umgebungen (Dev = Prod)

## Container vs. Virtuelle Maschine

| **Container** | **VM** |
|--------------|--------|
| Teilt OS-Kernel | Eigenes OS |
| Startet in Sekunden | Startet in Minuten |
| Wenige MB groß | GB groß |
| Leichtgewichtig | Schwergewichtig |

```
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│         Container               │   │      Virtual Machine            │
│                                 │   │                                 │
│  App A │ App B │ App C          │   │  ┌───────────┐ ┌───────────┐  │
│  ───────────────────────────    │   │  │   App A   │ │   App B   │  │
│     Docker Engine               │   │  │  Guest OS │ │  Guest OS │  │
│     Host OS                     │   │  └───────────┘ └───────────┘  │
│     Hardware                    │   │      Hypervisor                │
│                                 │   │      Host OS                   │
└─────────────────────────────────┘   │      Hardware                  │
                                      └─────────────────────────────────┘
```

## Docker Grundkonzepte

### 1. **Image** (Blaupause)

Ein Image ist eine **Vorlage** für Container (wie eine Klasse in OOP).

**Beispiel:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

**Image bauen:**
```bash
docker build -t arbitrage-producer .
```

### 2. **Container** (Laufende Instanz)

Ein Container ist eine **laufende Instanz** eines Images (wie ein Objekt).

**Container starten:**
```bash
docker run -d --name my-producer arbitrage-producer
```

**Container-Lifecycle:**
```
Build → Create → Start → (Running) → Stop → Remove
```

### 3. **Dockerfile** (Build-Anleitung)

Das Dockerfile definiert **wie** ein Image gebaut wird.

**Unser Producer-Dockerfile:**

```dockerfile
# src/producer/Dockerfile
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# Dependencies installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code kopieren
COPY . .

# Container starten
CMD ["python", "producer.py"]
```

**Wichtige Befehle:**

| Befehl | Zweck |
|--------|-------|
| `FROM` | Basis-Image |
| `WORKDIR` | Arbeitsverzeichnis |
| `COPY` | Dateien kopieren |
| `RUN` | Befehl während Build |
| `CMD` | Befehl beim Start |
| `ENV` | Umgebungsvariablen |
| `EXPOSE` | Port freigeben |

### 4. **Volume** (Datenspeicher)

Volumes speichern Daten **außerhalb** des Containers.

```
┌──────────────┐
│  Container   │
│              │
│  /data   ────┼──────▶ ┌─────────────┐
│              │        │   Volume    │
└──────────────┘        │ (Host-Disk) │
                        └─────────────┘
```

**Warum?** Daten bleiben auch nach Container-Neustart erhalten.

### 5. **Network** (Netzwerk)

Container können über Docker-Netzwerke kommunizieren.

```
┌─────────────────────────────────────┐
│      arbitrage-network              │
│                                     │
│  ┌─────────┐      ┌─────────┐     │
│  │   API   │─────▶│   ES    │     │
│  │  :8000  │      │  :9200  │     │
│  └─────────┘      └─────────┘     │
└─────────────────────────────────────┘
```

**Container können sich per Namen erreichen:**
```python
# Im API-Container
es = Elasticsearch(["http://elasticsearch:9200"])
```

## Docker Compose - Mehrere Container

**Docker Compose** orchestriert **mehrere Container** mit einer YAML-Datei.

### Unsere docker-compose.yml

```yaml
version: '3.8'

services:
  # Service 1: Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: arbitrage-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - arbitrage-network

  # Service 2: Kafka
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: arbitrage-kafka
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper
    networks:
      - arbitrage-network

  # Service 3: Producer (selbst gebaut)
  producer:
    build:
      context: .
      dockerfile: src/producer/Dockerfile
    container_name: arbitrage-producer
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - KEEPA_API_KEY=${KEEPA_API_KEY}
    depends_on:
      kafka:
        condition: service_healthy
    networks:
      - arbitrage-network

volumes:
  elasticsearch-data:

networks:
  arbitrage-network:
    driver: bridge
```

### Compose-Befehle

```bash
# Alle Services starten
docker compose up -d

# Einzelnen Service starten
docker compose up -d elasticsearch

# Services stoppen
docker compose down

# Services neu bauen
docker compose build

# Logs anzeigen
docker compose logs -f producer

# Status anzeigen
docker compose ps
```

## Unser System-Setup

### Services-Übersicht

```
┌─────────────────────────────────────────────────────────┐
│             Docker Compose Stack                        │
│                                                         │
│  DATA STORES:                                           │
│  ├─ elasticsearch:9200                                  │
│  ├─ kibana:5601                                         │
│  └─ postgres:5432                                       │
│                                                         │
│  MESSAGE QUEUE:                                         │
│  ├─ kafka:9092                                          │
│  ├─ zookeeper:2181                                      │
│  └─ redis:6379                                          │
│                                                         │
│  APPLICATION:                                           │
│  ├─ producer                                            │
│  ├─ enrichment-consumer                                 │
│  ├─ arbitrage-detector                                  │
│  ├─ api:8000                                            │
│  └─ dashboard:8501                                      │
│                                                         │
│  ORCHESTRATION:                                         │
│  ├─ airflow-webserver:8080                              │
│  ├─ airflow-scheduler                                   │
│  └─ airflow-worker                                      │
└─────────────────────────────────────────────────────────┘
```

### Port-Mapping

| Service | Container-Port | Host-Port | Zweck |
|---------|---------------|-----------|-------|
| Elasticsearch | 9200 | 9200 | REST API |
| Kibana | 5601 | 5601 | Web UI |
| Kafka | 9092 | 9092 | Broker |
| API | 8000 | 8000 | FastAPI |
| Dashboard | 8501 | 8501 | Streamlit |
| Airflow | 8080 | 8080 | Web UI |
| Redis | 6379 | 6379 | Cache |

### Environment Variables

```yaml
producer:
  environment:
    - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    - KEEPA_API_KEY=${KEEPA_API_KEY}  # Von .env
    - POLL_INTERVAL_SECONDS=60
```

**.env-Datei:**
```bash
KEEPA_API_KEY=ph28mvoh2pe0cdicgseei87pmmr8ja97j4u7n4iuveqaeodg22q11qsg5uoj04la
POLL_INTERVAL_SECONDS=60
```

### Volumes (Datenpersistenz)

```yaml
volumes:
  elasticsearch-data:      # Produkt-Daten
  kafka-data:              # Kafka-Nachrichten
  postgres-data:           # Airflow-Metadaten
  zookeeper-data:          # Zookeeper-State
  redis-data:              # Redis-Cache
```

**Speicherort auf Host:**
```bash
/var/lib/docker/volumes/arbitrage-tracker_elasticsearch-data/_data
```

### Networks

```yaml
networks:
  arbitrage-network:
    driver: bridge
```

**Alle Container im selben Netzwerk können sich erreichen:**
```
elasticsearch → kafka
kafka → enrichment-consumer
enrichment-consumer → elasticsearch
```

## Health Checks

Health Checks prüfen, ob ein Service **bereit** ist.

```yaml
elasticsearch:
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Bedeutung:**
- Alle 10s wird `curl` ausgeführt
- Timeout nach 5s
- Nach 5 Fehlversuchen gilt Service als "unhealthy"

**Service-Dependencies:**
```yaml
producer:
  depends_on:
    kafka:
      condition: service_healthy  # Warte bis Kafka healthy
```

## Docker Build Prozess

### Multi-Stage Builds

Optimierung für kleinere Images:

```dockerfile
# Stage 1: Build
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
WORKDIR /app
CMD ["python", "app.py"]
```

**Vorteil:** Runtime-Image enthält keine Build-Tools (kleiner)

### Layer Caching

Docker cached jede Zeile im Dockerfile:

```dockerfile
# ❌ Langsam (bei jeder Code-Änderung neu installiert)
COPY . .
RUN pip install -r requirements.txt

# ✅ Schnell (Cache genutzt wenn requirements.txt gleich)
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

## Docker CLI Befehle

### Container Management

```bash
# Container starten
docker run -d --name my-app nginx

# Container stoppen
docker stop my-app

# Container entfernen
docker rm my-app

# Logs anzeigen
docker logs -f my-app

# In Container einsteigen
docker exec -it my-app /bin/bash

# Container-Prozesse anzeigen
docker top my-app
```

### Image Management

```bash
# Images auflisten
docker images

# Image bauen
docker build -t my-app:latest .

# Image entfernen
docker rmi my-app:latest

# Image von Registry pullen
docker pull elasticsearch:8.11.0
```

### System Management

```bash
# Alle gestoppten Container entfernen
docker container prune

# Ungenutzte Images entfernen
docker image prune

# Volumes aufräumen
docker volume prune

# Komplette System-Bereinigung
docker system prune -a
```

## Debugging

### Container-Logs

```bash
# Letzte 50 Zeilen
docker logs --tail 50 arbitrage-producer

# Live-Logs
docker logs -f arbitrage-producer

# Mit Timestamps
docker logs -t arbitrage-producer
```

### Container-Shell

```bash
# Bash-Shell im laufenden Container
docker exec -it arbitrage-producer /bin/bash

# Python-Shell
docker exec -it arbitrage-producer python

# Einzelner Befehl
docker exec arbitrage-producer ls -la /app
```

### Network-Debugging

```bash
# Netzwerke auflisten
docker network ls

# Netzwerk inspizieren
docker network inspect arbitrage-network

# Welche Container in Netzwerk?
docker network inspect arbitrage-network | grep Name
```

### Resource Usage

```bash
# CPU/Memory-Nutzung
docker stats

# Detaillierte Container-Infos
docker inspect arbitrage-producer
```

## Best Practices

### 1. **Kleine Images**

```dockerfile
# ❌ Groß (1.2 GB)
FROM python:3.11

# ✅ Klein (150 MB)
FROM python:3.11-slim

# ✅ Noch kleiner (50 MB)
FROM python:3.11-alpine
```

### 2. **Non-Root User**

```dockerfile
# Sicherheit: Nicht als Root laufen
RUN useradd -m appuser
USER appuser
```

### 3. **.dockerignore**

Verhindert unnötige Dateien im Image:

```
# .dockerignore
__pycache__/
*.pyc
.git/
.env
node_modules/
*.md
```

### 4. **Restart Policies**

```yaml
producer:
  restart: unless-stopped  # Automatisch neu starten
```

Optionen:
- `no`: Kein Auto-Restart
- `always`: Immer neu starten
- `on-failure`: Nur bei Fehler
- `unless-stopped`: Außer manuell gestoppt

## Troubleshooting

### Container startet nicht

```bash
# Logs prüfen
docker logs arbitrage-producer

# Detaillierte Fehler
docker events --filter container=arbitrage-producer

# Container-Exit-Code
docker inspect arbitrage-producer | grep ExitCode
```

### Port bereits belegt

```bash
# Herausfinden welcher Prozess Port 9200 nutzt
sudo lsof -i :9200

# Prozess beenden
sudo kill -9 <PID>
```

### Volume-Probleme

```bash
# Volume löschen und neu erstellen
docker volume rm arbitrage-tracker_elasticsearch-data
docker compose up -d elasticsearch
```

### Network-Probleme

```bash
# DNS-Auflösung testen
docker exec arbitrage-producer ping elasticsearch

# Connectivity testen
docker exec arbitrage-producer curl http://elasticsearch:9200
```

## Zusammenfassung

| **Konzept** | **Beschreibung** | **Unser Einsatz** |
|-------------|------------------|-------------------|
| **Image** | Vorlage | `arbitrage-producer:latest` |
| **Container** | Laufende Instanz | 13 Container |
| **Volume** | Datenspeicher | elasticsearch-data, kafka-data |
| **Network** | Kommunikation | arbitrage-network |
| **Compose** | Multi-Container | docker-compose.yml |

**Docker macht unser System:**
- 🔒 Isoliert (Jeder Service in eigenem Container)
- 🚀 Portabel (Läuft überall gleich)
- 📦 Reproduzierbar (Gleiche Builds auf Dev & Prod)
- ⚡ Schnell (Container starten in Sekunden)
