# Keepa API - Amazon Preis-Tracker

## Was ist Keepa?

**Keepa** ist ein externer Service, der **Amazon-Preise** über alle Marktplätze hinweg **trackt und historisiert**.

### Was liefert Keepa?

- 📊 **Aktuelle Preise** von Amazon-Produkten
- 📈 **Preis-Historie** (z.B. letzte 30 Tage)
- 🌍 **Multimarktplatz-Daten** (DE, UK, IT, ES, FR, etc.)
- 📦 **Produkt-Informationen** (Titel, Bilder, Kategorie)
- ⭐ **Bestseller-Rankings**
- 🔔 **Preis-Alerts** (extern via Keepa-Website)

## Warum Keepa statt direktem Amazon-Scraping?

| Amazon Scraping | Keepa API |
|----------------|-----------|
| ❌ Gegen Terms of Service | ✅ Offiziell erlaubt |
| ❌ IP-Blocks | ✅ Stabil |
| ❌ HTML-Änderungen brechen Code | ✅ JSON-API |
| ❌ Langsam | ✅ Schnell |
| ❌ Keine Historie | ✅ Preis-Historie inklusive |

## Keepa API Basics

### Authentifizierung

Keepa nutzt einen **API-Key** für alle Requests.

```python
import requests

API_KEY = "ph28mvoh2pe0cdicgseei87pmmr8ja97j4u7n4iuveqaeodg22q11qsg5uoj04la"
BASE_URL = "https://api.keepa.com"

# Produkt abfragen
response = requests.get(
    f"{BASE_URL}/product",
    params={
        "key": API_KEY,
        "domain": 3,  # Deutschland
        "asin": "B0D1XD1ZV3",
        "stats": "30"  # 30-Tage-Statistiken
    }
)

data = response.json()
```

### Domain IDs - Amazon Marktplätze

Keepa nutzt **Domain IDs** statt Ländercodes:

```python
KEEPA_DOMAIN_MAP = {
    1: "US",   # Amazon.com (USA)
    2: "UK",   # Amazon.co.uk (Großbritannien)
    3: "DE",   # Amazon.de (Deutschland)
    4: "FR",   # Amazon.fr (Frankreich)
    5: "JP",   # Amazon.co.jp (Japan)
    6: "CA",   # Amazon.ca (Kanada)
    8: "IT",   # Amazon.it (Italien)
    9: "ES",   # Amazon.es (Spanien)
    10: "IN",  # Amazon.in (Indien)
}
```

**Für Arbitrage wichtig:** EU-Märkte (DE, UK, IT, ES, FR)

## Keepa API Endpoints

### 1. Product Query - Produkt-Daten

**Zweck:** Informationen zu einem oder mehreren ASINs abrufen

**Request:**
```python
GET https://api.keepa.com/product?key=API_KEY&domain=3&asin=B0D1XD1ZV3&stats=30
```

**Response:**
```json
{
  "products": [
    {
      "asin": "B0D1XD1ZV3",
      "domain": 3,
      "title": "Amazon Echo Dot (5. Generation) | Anthrazit",
      "brand": "Amazon",
      "img": "https://m.media-amazon.com/images/I/61FB5JvNpjL._AC_SL1000_.jpg",
      "url": "https://www.amazon.de/dp/B0D1XD1ZV3",
      "categoryTree": [
        {"catId": 3581, "name": "Elektronik"}
      ],
      "stats": {
        "current": 4999,     // Aktueller Preis in Cent
        "avg30": 5200,       // 30-Tage-Durchschnitt
        "min30": 4599,       // 30-Tage-Minimum
        "max30": 5999        // 30-Tage-Maximum
      }
    }
  ]
}
```

**Token-Kosten:** 1 Token pro ASIN

### 2. Deals - Produkte mit Preisänderungen

**Zweck:** Produkte finden, die kürzlich im Preis gefallen sind

**Request:**
```python
GET https://api.keepa.com/deals?key=API_KEY&domain=3&date_range=24&range=150
```

**Parameter:**
- `date_range`: Nur Produkte mit Updates in letzten X Stunden (1-168)
- `range`: Maximale Anzahl Ergebnisse (max 150)

**Token-Kosten:** 5 Tokens pro Request

### 3. Bestsellers - Top-Produkte

**Zweck:** ASINs der Bestseller einer Kategorie

**Request:**
```python
GET https://api.keepa.com/bestsellers?key=API_KEY&domain=3&category=281052&range=100
```

**Token-Kosten:** 5 Tokens pro Request

### 4. Search - Produkt-Suche

**Zweck:** Produkte nach Keyword suchen

**Request:**
```python
GET https://api.keepa.com/search?key=API_KEY&domain=3&search=echo+dot&range=20
```

**Token-Kosten:** 5 Tokens pro Request

## Token System & Rate Limits

### Was sind Tokens?

Keepa berechnet API-Nutzung in **Tokens** (nicht Requests).

**Unser Plan:**
- **20 Tokens pro Minute**
- **1200 verfügbare Tokens**
- **Gültig bis:** 10. Februar 2026

### Token-Verbrauch

| Operation | Token-Kosten |
|-----------|-------------|
| 1 ASIN abfragen | 1 Token |
| 5 ASINs abfragen | 5 Tokens |
| Deals abrufen | 5 Tokens |
| Bestsellers | 5 Tokens |
| Search | 5 Tokens |

### Rate Limiting im Code

```python
import time

class KeepaClient:
    def __init__(self, tokens_per_minute=20):
        self.tokens_per_minute = tokens_per_minute
        self.request_interval = 60.0 / tokens_per_minute  # 3 Sekunden
        self._last_request_time = 0.0

    def _rate_limit(self):
        """Warte zwischen Requests"""
        now = time.time()
        elapsed = now - self._last_request_time

        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)

        self._last_request_time = time.time()

    def product_query(self, asins):
        self._rate_limit()  # Warte falls zu schnell
        response = requests.get(...)
        return response.json()
```

**Ergebnis:** Maximal 20 Requests pro Minute

## Keepa Client Implementierung

### Unsere Wrapper-Klasse

**Datei:** `src/producer/keepa_client.py`

```python
class KeepaClient:
    def __init__(self, api_key: str, requests_per_minute: int = 20):
        self.api_key = api_key
        self.requests_per_minute = requests_per_minute
        self._session = requests.Session()

    def product_query(self, asins: List[str], domain: int = 1) -> List[KeepaProduct]:
        """Produkt-Daten für mehrere ASINs abrufen"""
        asin_string = ",".join(asins)

        params = {
            "key": self.api_key,
            "asin": asin_string,
            "domain": domain,
            "stats": "30"  # 30-Tage-Statistiken
        }

        data = self._request("product", params=params)

        products = []
        for item in data.get("products", []):
            product = KeepaProduct.from_keepa_response(item)
            products.append(product)

        return products
```

### KeepaProduct Dataclass

```python
from dataclasses import dataclass

@dataclass
class KeepaProduct:
    asin: str
    domain_id: int
    title: Optional[str] = None
    brand: Optional[str] = None
    image: Optional[str] = None
    url: Optional[str] = None
    current_prices: Dict[str, float] = field(default_factory=dict)
    price_history: List[Dict] = field(default_factory=list)
    avg_price: Optional[float] = None

    @property
    def marketplace(self) -> str:
        return KEEPA_DOMAIN_MAP.get(self.domain_id, "UNKNOWN")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asin": self.asin,
            "marketplace": self.marketplace,
            "title": self.title,
            "current_prices": self.current_prices,
            # ...
        }
```

## Integration in Producer

### Producer-Logik

```python
# src/producer/producer.py

from keepa_client import KeepaClient
from confluent_kafka import Producer
import os

# Keepa initialisieren
keepa = KeepaClient(
    api_key=os.getenv("KEEPA_API_KEY"),
    requests_per_minute=20
)

# Kafka initialisieren
kafka_producer = Producer({'bootstrap.servers': 'kafka:9092'})

# ASIN-Watchlist aus ENV
asin_watchlist = os.getenv("ASIN_WATCHLIST", "").split(",")

# Polling-Loop
while True:
    # 1. Keepa abfragen
    products = keepa.product_query(
        asins=asin_watchlist,
        domain=3  # Deutschland
    )

    # 2. An Kafka senden
    for product in products:
        kafka_producer.produce(
            topic='raw.keepa_updates',
            key=product.asin.encode('utf-8'),
            value=json.dumps(product.to_dict()).encode('utf-8')
        )

    kafka_producer.flush()

    # 3. Warten bis nächste Abfrage
    time.sleep(int(os.getenv("POLL_INTERVAL_SECONDS", 300)))
```

### Umgebungsvariablen

```bash
# .env
KEEPA_API_KEY=ph28mvoh2pe0cdicgseei87pmmr8ja97j4u7n4iuveqaeodg22q11qsg5uoj04la
ASIN_WATCHLIST=B075CYMYK6,B08G9PKCGK,B0D1XD1ZV3
POLL_INTERVAL_SECONDS=60
CATEGORY_MODE=false
```

## Strategien für Arbitrage

### Strategie 1: ASIN-Watchlist (Aktuell)

**Konzept:** Feste Liste von Produkten regelmäßig prüfen

**Vorteile:**
- ✅ Volle Kontrolle über Produkte
- ✅ Geringer Token-Verbrauch
- ✅ Einfach zu debuggen

**Nachteile:**
- ❌ Muss manuell gepflegt werden
- ❌ Neue Opportunities werden verpasst

**Token-Verbrauch:**
- 3 ASINs × 20 Abfragen/Stunde = 60 Tokens/Stunde

### Strategie 2: Category Bestsellers

**Konzept:** Bestseller einer Kategorie regelmäßig scannen

```python
# Elektronik-Bestseller
bestseller_asins = keepa.category_bestsellers(
    category_id=3581,  # Elektronik
    domain=3,
    limit=100
)

# Alle Bestseller abfragen
products = keepa.product_query(bestseller_asins, domain=3)
```

**Token-Verbrauch:**
- Bestseller-Liste: 5 Tokens
- 100 Produkte: 100 Tokens
- **Total: 105 Tokens** (alle 2 Stunden möglich)

### Strategie 3: Deals Finder

**Konzept:** Produkte mit kürzlichen Preissenkungen

```python
deals = keepa.fetch_deals(
    domain=3,
    date_range=24,  # Letzte 24 Stunden
    limit=150
)
```

**Token-Verbrauch:**
- 5 Tokens pro Request
- Maximal 4× pro Minute möglich

## Multimarktplatz-Arbitrage

### Cross-Market Price Comparison

Um Arbitrage zu finden, brauchen wir **Preise aus mehreren Ländern**:

```python
def fetch_multimarket_prices(asin: str) -> Dict[str, int]:
    """Preise für ein Produkt in allen EU-Märkten"""
    markets = [
        (3, "DE"),
        (2, "UK"),
        (8, "IT"),
        (9, "ES"),
        (4, "FR")
    ]

    prices = {}
    for domain_id, market_code in markets:
        product = keepa.product_query_single(asin, domain=domain_id)

        if product and product.current_prices:
            prices[market_code] = product.current_prices.get(market_code)

    return prices

# Beispiel
prices = fetch_multimarket_prices("B0D1XD1ZV3")
# → {"DE": 4999, "UK": 4500, "IT": 5499, "ES": 4799, "FR": 5200}
```

**Problem:** 1 ASIN × 5 Märkte = **5 Tokens**

**Besser:** Keepa kann mehrere Domains in einem Request abfragen (API-Feature)

## Error Handling

### Typische Fehler

```python
class KeepaRateLimitError(Exception):
    """API-Limit überschritten"""
    pass

class KeepaAPIError(Exception):
    """Allgemeiner API-Fehler"""
    pass

def _request(self, endpoint, params):
    try:
        response = self._session.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        if "error" in data:
            error_msg = data.get("error", "Unknown error")

            if "too many requests" in error_msg.lower():
                raise KeepaRateLimitError(error_msg)

            raise KeepaAPIError(error_msg)

        return data

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            raise KeepaRateLimitError("Rate limit exceeded")
        raise KeepaAPIError(f"HTTP Error: {e}")
```

### Retry-Logik

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_product_with_retry(asin):
    return keepa.product_query_single(asin)
```

## Keepa Preis-Format

### Cent-Konvertierung

Keepa liefert Preise in **Cent** (ohne Komma):

```python
keepa_price = 4999  # Von API

# Umrechnung
euro_price = keepa_price / 100  # 49.99€
```

### Null-Werte

- `-1` oder `None` = Preis nicht verfügbar
- `0` = Produkt aktuell nicht verkauft

## Zusammenfassung

| **Feature** | **Details** | **Unser Einsatz** |
|-------------|-------------|-------------------|
| **API-Endpoint** | https://api.keepa.com | ✅ |
| **Authentifizierung** | API-Key in Params | ✅ |
| **Rate Limit** | 20 Tokens/Minute | 3s zwischen Requests |
| **Domain IDs** | 1=US, 3=DE, 8=IT, etc. | EU-Märkte |
| **Token-Kosten** | 1 per ASIN, 5 per Deals | Watchlist-Modus |
| **Datenformat** | JSON | KeepaProduct-Klasse |
| **Preis-Format** | Cent (Integer) | Division durch 100 |

**Keepa ermöglicht:**
- 🌍 Multimarktplatz-Preisvergleich
- 📊 Historische Preisentwicklung
- ⚡ Schnellen Zugriff auf Amazon-Daten
- 🔒 Legale Alternative zu Scraping
