# Poetry - Python Dependency Management

## Was ist Poetry?

**Poetry** ist ein modernes Tool für **Python-Dependency-Management** und **Packaging**.

### Das Problem ohne Poetry

**Klassisch mit requirements.txt:**

```
# requirements.txt
requests==2.31.0
pandas==2.0.3
numpy==1.24.3
```

**Probleme:**
- ❌ Keine Unterscheidung zwischen direkten und indirekten Dependencies
- ❌ Keine automatische Konfliktauflösung
- ❌ Keine virtuelle Umgebung integriert
- ❌ Kein Packaging-Support

### Die Lösung mit Poetry

**pyproject.toml:**

```toml
[tool.poetry]
name = "arbitrage-tracker"
version = "1.0.0"
description = "Amazon Arbitrage Tracker"

[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31.0"
pandas = "^2.0.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
```

**Vorteile:**
- ✅ Klare Trennung: Produktion vs. Development
- ✅ Automatische Konfliktauflösung
- ✅ Lock-File für reproduzierbare Builds
- ✅ Virtuelle Umgebungen automatisch
- ✅ Publishing zu PyPI

## Installation

```bash
# Via pip
pip install poetry

# Via Homebrew (macOS)
brew install poetry

# Via curl (Linux)
curl -sSL https://install.python-poetry.org | python3 -
```

**Version prüfen:**
```bash
poetry --version
```

## Projekt initialisieren

### Neues Projekt

```bash
poetry new arbitrage-tracker
```

**Erstellt:**
```
arbitrage-tracker/
├── arbitrage_tracker/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
└── README.md
```

### Existierendes Projekt

```bash
cd existing-project
poetry init
```

Interaktiver Wizard für `pyproject.toml`.

## pyproject.toml - Die Konfigurations-Datei

### Komplettes Beispiel

```toml
[tool.poetry]
name = "arbitrage-tracker"
version = "1.0.0"
description = "Amazon Arbitrage Tracker System"
authors = ["Your Name <you@example.com>"]
readme = "README.md"
license = "MIT"
homepage = "https://github.com/user/arbitrage-tracker"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
elasticsearch = "^8.11.0"
confluent-kafka = "^2.3.0"
streamlit = "^1.28.0"
pandas = "^2.1.0"
requests = "^2.31.0"
pydantic = "^2.5.0"
python-dotenv = "^1.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
black = "^23.11.0"
flake8 = "^6.1.0"
mypy = "^1.7.0"

[tool.poetry.group.airflow.dependencies]
apache-airflow = "^2.8.0"
apache-airflow-providers-apache-kafka = "^1.3.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Sections erklärt

#### 1. **[tool.poetry]** - Projekt-Metadaten

```toml
[tool.poetry]
name = "arbitrage-tracker"           # Projekt-Name
version = "1.0.0"                     # Semantic Versioning
description = "..."                   # Beschreibung
authors = ["Name <email>"]            # Autoren
license = "MIT"                       # Lizenz
```

#### 2. **[tool.poetry.dependencies]** - Produktions-Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.11"              # Python-Version erforderlich
fastapi = "^0.104.0"          # FastAPI Version >= 0.104.0, < 1.0.0
requests = "~2.31.0"          # Requests >= 2.31.0, < 2.32.0
pandas = "*"                  # Neueste Version
```

**Version Constraints:**

| Syntax | Bedeutung | Beispiel |
|--------|-----------|----------|
| `^1.2.3` | >= 1.2.3, < 2.0.0 | Major-kompatibel |
| `~1.2.3` | >= 1.2.3, < 1.3.0 | Minor-kompatibel |
| `1.2.*` | >= 1.2.0, < 1.3.0 | Wildcard |
| `>=1.2.3` | >= 1.2.3 | Minimum |
| `*` | Beliebig | Neueste |

#### 3. **[tool.poetry.group.dev.dependencies]** - Development-Dependencies

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"        # Testing
black = "^23.11.0"       # Code-Formatter
mypy = "^1.7.0"          # Type-Checker
```

**Werden nicht in Production installiert!**

## Dependency Management

### Dependencies hinzufügen

```bash
# Produktion
poetry add requests

# Mit Version
poetry add "fastapi>=0.104.0"

# Development
poetry add --group dev pytest

# Mehrere gleichzeitig
poetry add fastapi uvicorn elasticsearch
```

**Poetry:**
1. Prüft Kompatibilität
2. Updated `pyproject.toml`
3. Updated `poetry.lock`
4. Installiert Package

### Dependencies entfernen

```bash
poetry remove requests

# Development
poetry remove --group dev pytest
```

### Dependencies aktualisieren

```bash
# Alle auf neueste kompatible Version
poetry update

# Nur ein Package
poetry update fastapi

# Alle auf absolute neueste (ignoriert Constraints)
poetry update --latest
```

### Dependencies anzeigen

```bash
# Alle Dependencies
poetry show

# Details zu einem Package
poetry show fastapi

# Dependency-Tree
poetry show --tree

# Nur outdated
poetry show --outdated
```

## poetry.lock - Der Lock-File

**poetry.lock** speichert **exakte Versionen** aller Dependencies (inkl. indirekter).

**Beispiel:**

```
[[package]]
name = "fastapi"
version = "0.104.1"
requires_python = ">=3.8"

[[package]]
name = "starlette"
version = "0.27.0"
requires_python = ">=3.7"

[[package]]
name = "uvicorn"
version = "0.24.0"
```

**Warum wichtig?**

```
Dev-Machine:    fastapi 0.104.1  →  starlette 0.27.0
Production:     fastapi 0.104.1  →  starlette 0.27.0
                ✅ Identisch
```

**Best Practice:** `poetry.lock` in Git committen!

## Virtuelle Umgebungen

### Automatische venv-Verwaltung

```bash
# Venv erstellen & Dependencies installieren
poetry install

# Wo liegt die venv?
poetry env info --path
# → /home/user/.cache/pypoetry/virtualenvs/arbitrage-tracker-xyz
```

### Befehle in venv ausführen

```bash
# Python in venv
poetry run python app.py

# Pytest in venv
poetry run pytest

# Script in venv
poetry run uvicorn main:app
```

### Shell in venv

```bash
# Shell starten
poetry shell

# Jetzt direkt ohne "poetry run"
python app.py
pytest
```

## Projekt-Installation

### Als Entwickler

```bash
git clone https://github.com/user/arbitrage-tracker
cd arbitrage-tracker

# Alle Dependencies (inkl. dev)
poetry install

# Nur Production-Dependencies
poetry install --only main
```

### Als Nutzer

```bash
# Von PyPI
pip install arbitrage-tracker

# Von GitHub
pip install git+https://github.com/user/arbitrage-tracker
```

## Packaging & Publishing

### Build

```bash
# Erstellt wheel und sdist
poetry build

# Erstellt:
# dist/arbitrage_tracker-1.0.0-py3-none-any.whl
# dist/arbitrage_tracker-1.0.0.tar.gz
```

### Publish zu PyPI

```bash
# PyPI-Token konfigurieren
poetry config pypi-token.pypi your-token

# Publishen
poetry publish

# Build + Publish in einem
poetry publish --build
```

## Scripts definieren

```toml
[tool.poetry.scripts]
arbitrage = "arbitrage_tracker.cli:main"
start-producer = "arbitrage_tracker.producer:run"
start-consumer = "arbitrage_tracker.consumer:run"
```

**Nutzung:**

```bash
poetry run arbitrage
poetry run start-producer
```

## Poetry in Docker

### Dockerfile mit Poetry

```dockerfile
FROM python:3.11-slim

# Poetry installieren
RUN pip install poetry

# Konfiguration
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Nur pyproject.toml & lock kopieren (Layer-Caching)
COPY pyproject.toml poetry.lock ./

# Dependencies installieren
RUN poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR

# Code kopieren
COPY . .

# App installieren
RUN poetry install --only main

# App starten
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Multi-Stage Build (kleiner)

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# venv kopieren
COPY --from=builder /app/.venv .venv

# Code kopieren
COPY . .

# venv aktivieren
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

## Poetry vs. andere Tools

| Feature | Poetry | pip + venv | Pipenv | conda |
|---------|--------|-----------|--------|-------|
| **Dependency Resolution** | ✅ | ❌ | ✅ | ✅ |
| **Lock File** | ✅ | ❌ | ✅ | ✅ |
| **Virtual Env** | ✅ Auto | ⚠️ Manuell | ✅ Auto | ✅ Auto |
| **Packaging** | ✅ | ⚠️ setuptools | ❌ | ❌ |
| **Performance** | ⚡ Schnell | ⚡ Schnell | 🐌 Langsam | 🐌 Langsam |
| **Standard** | Moderner Standard | Alt | Veraltet | Wissenschaft |

## Troubleshooting

### Dependency-Konflikte

```bash
# Detaillierte Fehler
poetry add package --verbose

# Lock-File neu erstellen
poetry lock --no-update

# Cache löschen
poetry cache clear pypi --all
```

### Venv-Probleme

```bash
# Venv löschen
poetry env remove python3.11

# Neu erstellen
poetry install

# Alle venvs anzeigen
poetry env list
```

### Alte Lock-File

```bash
# Lock-File aktualisieren ohne Dependency-Update
poetry lock --no-update

# Lock-File mit neuesten Versionen
poetry lock
```

## Best Practices

### 1. **Dependency-Gruppen nutzen**

```toml
[tool.poetry.group.test.dependencies]
pytest = "^7.4.0"

[tool.poetry.group.lint.dependencies]
black = "^23.11.0"
flake8 = "^6.1.0"

[tool.poetry.group.docs.dependencies]
sphinx = "^7.2.0"
```

**Installation:**
```bash
poetry install --with test,lint
poetry install --without docs
```

### 2. **Poetry.lock committen**

```bash
git add poetry.lock
git commit -m "Update dependencies"
```

### 3. **Version-Constraints präzise**

```toml
# ✅ Gut
fastapi = "^0.104.0"  # Breaking changes in 1.0.0 nicht automatisch

# ❌ Zu locker
fastapi = "*"  # Unvorhersehbare Updates

# ❌ Zu strikt
fastapi = "0.104.1"  # Keine Bugfix-Updates
```

### 4. **Dev-Dependencies trennen**

```toml
[tool.poetry.dependencies]
fastapi = "^0.104.0"  # Produktion

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"  # Nur Development
```

## Konfiguration

### Config-Optionen

```bash
# venv im Projekt-Ordner
poetry config virtualenvs.in-project true

# PyPI-Token
poetry config pypi-token.pypi your-token

# Private Repository
poetry config repositories.private https://private.pypi.org

# Config anzeigen
poetry config --list
```

### .poetry-config

```toml
# poetry.toml (Projekt-spezifisch)
[virtualenvs]
in-project = true
create = true
```

## Zusammenfassung

| **Feature** | **Beschreibung** | **Unser Einsatz** |
|-------------|------------------|-------------------|
| **pyproject.toml** | Dependency-Definition | Projekt-Config |
| **poetry.lock** | Exakte Versionen | Reproduzierbare Builds |
| **poetry install** | Dependencies installieren | Dev-Setup |
| **poetry add** | Package hinzufügen | Dependency-Management |
| **poetry run** | Befehl in venv | Script-Ausführung |
| **Groups** | Dev/Test/Docs trennen | Organisation |

**Poetry macht unser System:**
- 🔒 Deterministisch (Lock-File)
- 📦 Reproduzierbar (Gleiche Versionen überall)
- ⚡ Schnell (Dependency-Resolution)
- 🧹 Sauber (Automatische venv-Verwaltung)
