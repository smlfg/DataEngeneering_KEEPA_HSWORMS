# FastAPI - REST API Framework

## Was ist FastAPI?

**FastAPI** ist ein modernes **Python-Framework** für den Bau von **REST APIs**.

### Einfach erklärt: Der Kellner

```
Client (Dashboard) ─────▶ API (Kellner) ─────▶ Elasticsearch (Küche)
                   Request              Query
                   ◀─────               ◀─────
                   Response             Data
```

Die API ist der **Vermittler** zwischen Frontend und Datenbank.

## Warum FastAPI?

### FastAPI vs. Flask vs. Django

| Feature | FastAPI | Flask | Django |
|---------|---------|-------|--------|
| **Geschwindigkeit** | Sehr schnell | Mittel | Langsam |
| **Type Hints** | ✅ Built-in | ❌ | ❌ |
| **Auto-Docs** | ✅ Swagger UI | ❌ | ❌ |
| **Async** | ✅ Native | ⚠️ Optional | ⚠️ Optional |
| **Learning Curve** | Einfach | Sehr einfach | Komplex |

**Unser Vorteil:** Auto-Dokumentation + schnelle Async-Requests

## HTTP Basics

### Request-Response-Zyklus

```
Client                          Server (FastAPI)
  │                                    │
  ├──── GET /products ───────────────▶│
  │                                    │ [Elasticsearch Query]
  │                                    │
  │◀─── 200 OK + JSON Data ───────────┤
```

### HTTP-Methoden

| Methode | Zweck | Beispiel |
|---------|-------|----------|
| **GET** | Daten abrufen | `GET /products` |
| **POST** | Daten erstellen | `POST /products` |
| **PUT** | Daten aktualisieren | `PUT /products/123` |
| **DELETE** | Daten löschen | `DELETE /products/123` |
| **PATCH** | Teildaten ändern | `PATCH /products/123` |

### HTTP-Status-Codes

| Code | Bedeutung | Wann? |
|------|-----------|-------|
| **200** | OK | Erfolgreiche Anfrage |
| **201** | Created | Ressource erstellt |
| **400** | Bad Request | Ungültige Eingabe |
| **404** | Not Found | Ressource existiert nicht |
| **500** | Server Error | Interner Fehler |

## FastAPI Grundkonzepte

### 1. **Route** (Endpunkt)

Eine Route ist eine URL, die eine Funktion ausführt.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/products")
async def get_products():
    return {"products": [...]}
```

**Zugriff:**
- `GET http://localhost:8000/` → `{"message": "Hello World"}`
- `GET http://localhost:8000/products` → `{"products": [...]}`

### 2. **Path Parameter**

Dynamische Werte in der URL:

```python
@app.get("/products/{asin}")
async def get_product(asin: str):
    product = db.find_by_asin(asin)
    return product

# Aufruf: GET /products/B0D1XD1ZV3
# asin = "B0D1XD1ZV3"
```

### 3. **Query Parameter**

Parameter nach dem `?` in der URL:

```python
@app.get("/products")
async def search_products(
    min_margin: float = 10.0,
    market: str = "DE",
    limit: int = 100
):
    products = db.search(min_margin, market, limit)
    return products

# Aufruf: GET /products?min_margin=15&market=IT&limit=50
# min_margin = 15.0, market = "IT", limit = 50
```

### 4. **Request Body** (POST/PUT)

Daten im Request-Body senden:

```python
from pydantic import BaseModel

class Product(BaseModel):
    asin: str
    title: str
    price: float

@app.post("/products")
async def create_product(product: Product):
    db.insert(product)
    return {"status": "created", "asin": product.asin}

# Request:
# POST /products
# Body: {"asin": "B0D1XD1ZV3", "title": "Echo Dot", "price": 49.99}
```

### 5. **Response Model**

Definiert das Format der Response:

```python
class ProductResponse(BaseModel):
    asin: str
    title: str
    current_prices: Dict[str, int]

@app.get("/products/{asin}", response_model=ProductResponse)
async def get_product(asin: str):
    product = db.get_product(asin)
    return product
```

**Vorteil:** FastAPI validiert automatisch die Response

## Unsere API-Implementierung

### Datei-Struktur

```
src/api/
├── Dockerfile
├── main.py              # FastAPI App
├── routes.py            # Route-Definitionen
├── models.py            # Pydantic Models
└── requirements.txt
```

### main.py - App Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import elasticsearch
import os

app = FastAPI(
    title="Arbitrage Tracker API",
    description="REST API for Amazon arbitrage opportunities",
    version="1.0.0"
)

# CORS aktivieren (für Dashboard-Zugriff)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Elasticsearch-Verbindung
es_client = elasticsearch.Elasticsearch(
    [os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")]
)

# Health Check
@app.get("/health")
async def health_check():
    es_healthy = es_client.ping()

    return {
        "status": "healthy" if es_healthy else "unhealthy",
        "elasticsearch": {
            "status": "up" if es_healthy else "down"
        }
    }
```

### routes.py - Endpunkte

```python
from fastapi import APIRouter, Query
from typing import List, Optional
from models import Product, ArbitrageOpportunity

router = APIRouter()

@router.get("/products", response_model=List[Product])
async def get_products(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Liste aller Produkte"""
    response = es_client.search(
        index="products",
        body={
            "query": {"match_all": {}},
            "from": offset,
            "size": limit
        }
    )

    products = [hit["_source"] for hit in response["hits"]["hits"]]
    return products


@router.get("/products/{asin}", response_model=Product)
async def get_product_by_asin(asin: str):
    """Einzelnes Produkt"""
    response = es_client.get(index="products", id=asin)
    return response["_source"]


@router.get("/opportunities", response_model=List[ArbitrageOpportunity])
async def get_arbitrage_opportunities(
    min_margin: float = Query(10.0, ge=0, description="Mindest-Marge in %"),
    source_market: Optional[str] = Query(None, description="Quellmarkt (z.B. DE)"),
    target_market: Optional[str] = Query(None, description="Zielmarkt (z.B. IT)"),
    limit: int = Query(100, ge=1, le=500)
):
    """Arbitrage-Opportunities"""
    query = {
        "bool": {
            "must": [
                {"term": {"is_active": True}},
                {"range": {"margin_percentage": {"gte": min_margin}}}
            ]
        }
    }

    if source_market:
        query["bool"]["must"].append({"term": {"source_market": source_market}})

    if target_market:
        query["bool"]["must"].append({"term": {"target_market": target_market}})

    response = es_client.search(
        index="products",
        body={
            "query": query,
            "sort": [{"margin_percentage": {"order": "desc"}}],
            "size": limit
        }
    )

    opportunities = [hit["_source"] for hit in response["hits"]["hits"]]
    return opportunities


@router.get("/stats")
async def get_statistics():
    """System-Statistiken"""
    total_products = es_client.count(index="products")["count"]

    opportunities_count = es_client.count(
        index="products",
        body={"query": {"range": {"margin_percentage": {"gte": 10}}}}
    )["count"]

    return {
        "total_products": total_products,
        "total_opportunities": opportunities_count,
        "markets": ["DE", "UK", "IT", "ES", "FR"]
    }
```

### models.py - Datenmodelle

```python
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime

class Product(BaseModel):
    asin: str = Field(..., description="Amazon ASIN")
    title: Optional[str] = Field(None, description="Produkttitel")
    brand: Optional[str] = Field(None, description="Marke")
    image_url: Optional[str] = Field(None, description="Bild-URL")
    current_prices: Dict[str, int] = Field(default_factory=dict, description="Preise pro Markt (in Cent)")
    last_updated: datetime = Field(..., description="Letzte Aktualisierung")
    is_active: bool = Field(True, description="Produkt aktiv?")

class ArbitrageOpportunity(BaseModel):
    asin: str
    title: str
    source_market: str = Field(..., description="Kaufmarkt")
    target_market: str = Field(..., description="Verkaufsmarkt")
    source_price: int = Field(..., description="Kaufpreis (Cent)")
    target_price: int = Field(..., description="Verkaufspreis (Cent)")
    margin: int = Field(..., description="Gewinn (Cent)")
    margin_percentage: float = Field(..., description="Gewinn (%)")
    image_url: Optional[str] = None
```

## Auto-Dokumentation

### Swagger UI

FastAPI generiert **automatisch** eine interaktive API-Dokumentation.

**Zugriff:** http://localhost:8000/docs

```
┌─────────────────────────────────────────────────┐
│          Arbitrage Tracker API                  │
├─────────────────────────────────────────────────┤
│  GET  /health            Health Check           │
│  GET  /products          Liste aller Produkte   │
│  GET  /products/{asin}   Produkt-Details        │
│  GET  /opportunities     Arbitrage-Chancen      │
│  GET  /stats             Statistiken            │
└─────────────────────────────────────────────────┘
```

**Features:**
- ✅ Alle Endpunkte testen
- ✅ Parameter eingeben
- ✅ Response anzeigen
- ✅ Schema-Validierung

### ReDoc

Alternative Dokumentation:

**Zugriff:** http://localhost:8000/redoc

## Middleware

Middleware läuft **vor/nach** jeder Request.

### CORS (Cross-Origin Resource Sharing)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit Dashboard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

**Warum?** Dashboard (Port 8501) kann auf API (Port 8000) zugreifen.

### Logging Middleware

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    print(f"{request.method} {request.url.path} - {duration:.2f}s")

    return response
```

## Dependency Injection

Wiederverwendbare Abhängigkeiten:

```python
from fastapi import Depends

def get_es_client():
    """Elasticsearch-Client"""
    return elasticsearch.Elasticsearch(["http://elasticsearch:9200"])

@app.get("/products")
async def get_products(es: elasticsearch.Elasticsearch = Depends(get_es_client)):
    response = es.search(index="products", body={...})
    return response
```

## Error Handling

### Custom Exceptions

```python
from fastapi import HTTPException

@app.get("/products/{asin}")
async def get_product(asin: str):
    product = es_client.get(index="products", id=asin, ignore=[404])

    if not product.get("found"):
        raise HTTPException(
            status_code=404,
            detail=f"Product with ASIN {asin} not found"
        )

    return product["_source"]
```

### Exception Handler

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )
```

## Async vs. Sync

### Wann async?

```python
# ✅ Async für I/O (Netzwerk, DB)
@app.get("/products")
async def get_products():
    response = await es_client.search(...)  # Wartet nicht blockierend
    return response

# ❌ Sync für CPU-intensive Tasks
@app.get("/calculate")
def heavy_calculation():
    result = complex_algorithm()  # Blockiert
    return result
```

**Vorteil async:** Server kann andere Requests bearbeiten während auf Elasticsearch gewartet wird.

## Testing

### Unit Tests

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_products():
    response = client.get("/products?limit=10")
    assert response.status_code == 200
    assert len(response.json()) <= 10
```

## API-Sicherheit

### API Keys

```python
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = "secret-key-123"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.get("/protected")
async def protected_route(api_key: str = Depends(verify_api_key)):
    return {"message": "Access granted"}
```

**Request:**
```bash
curl -H "X-API-Key: secret-key-123" http://localhost:8000/protected
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/opportunities")
@limiter.limit("10/minute")
async def get_opportunities(request: Request):
    return {...}
```

## Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
api:
  build:
    context: .
    dockerfile: src/api/Dockerfile
  environment:
    - ELASTICSEARCH_HOST=http://elasticsearch:9200
  ports:
    - "8000:8000"
  depends_on:
    - elasticsearch
```

### Produktiv mit Gunicorn

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## API-Nutzung vom Dashboard

### Python Requests

```python
import requests

API_BASE_URL = "http://api:8000"

# Opportunities abrufen
response = requests.get(
    f"{API_BASE_URL}/opportunities",
    params={
        "min_margin": 15,
        "limit": 50
    }
)

opportunities = response.json()
```

### Streamlit Integration

```python
import streamlit as st
import requests

st.title("Arbitrage Dashboard")

min_margin = st.slider("Mindest-Marge (%)", 0, 50, 10)

response = requests.get(
    "http://api:8000/opportunities",
    params={"min_margin": min_margin}
)

if response.status_code == 200:
    opportunities = response.json()
    st.dataframe(opportunities)
```

## Zusammenfassung

| **Feature** | **Beschreibung** | **Unser Einsatz** |
|-------------|------------------|-------------------|
| **Framework** | FastAPI | REST API |
| **Port** | 8000 | HTTP Server |
| **Routes** | GET /products, /opportunities | Daten-Endpunkte |
| **Database** | Elasticsearch | Produkt-Abfragen |
| **Docs** | /docs, /redoc | Auto-Dokumentation |
| **CORS** | Middleware | Dashboard-Zugriff |

**FastAPI macht unser System:**
- ⚡ Schnell (Async I/O)
- 📄 Dokumentiert (Auto-Swagger)
- 🔒 Typsicher (Pydantic)
- 🔌 Modular (Dependency Injection)
