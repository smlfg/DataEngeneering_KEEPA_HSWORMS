# API Contract - Amazon Arbitrage Tracker

## OpenAPI 3.0 Specification

```yaml
openapi: 3.0.3
info:
  title: Amazon Arbitrage Tracker API
  description: |
    REST API for accessing Amazon product price data and arbitrage opportunities.
    This API is the contract between the Frontend (Streamlit) and the Backend (FastAPI).
  version: 1.0.0
  contact:
    name: Data Engineering Team
    email: team@arbitrage.local

servers:
  - url: http://localhost:8000
    description: Local development server
  - url: http://api.arbitrage.local
    description: Production server (when deployed)

tags:
  - name: Products
    description: Product operations
  - name: Arbitrage
    description: Arbitrage opportunity operations
  - name: Health
    description: System health checks

paths:
  /health:
    get:
      tags:
        - Health
      summary: Health check endpoint
      description: Returns the health status of all services
      operationId: health_check
      responses:
        '200':
          description: All services healthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'
        '503':
          description: One or more services unhealthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'

  /products:
    get:
      tags:
        - Products
      summary: List products with optional filters
      description: |
        Returns a paginated list of products with optional filtering by
        marketplace, price range, and arbitrage margin.
      operationId: list_products
      parameters:
        - name: page
          in: query
          description: Page number (1-based)
          schema:
            type: integer
            default: 1
            minimum: 1
        - name: page_size
          in: query
          description: Number of items per page
          schema:
            type: integer
            default: 20
            minimum: 1
            maximum: 100
        - name: marketplace
          in: query
          description: Filter by target marketplace (DE, IT, ES, UK, FR)
          schema:
            type: string
            enum: [DE, IT, ES, UK, FR]
        - name: min_margin
          in: query
          description: Minimum arbitrage margin percentage
          schema:
            type: number
            minimum: 0
            maximum: 100
            default: 0
        - name: max_price
          in: query
          description: Maximum target price in EUR
          schema:
            type: number
            minimum: 0
        - name: category
          in: query
          description: Product category filter
          schema:
            type: string
        - name: sort_by
          in: query
          description: Sort field and direction
          schema:
            type: string
            enum: [margin_desc, margin_asc, price_asc, price_desc, updated_desc]
            default: updated_desc
      responses:
        '200':
          description: Paginated list of products
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProductListResponse'

  /products/{asin}:
    get:
      tags:
        - Products
      summary: Get product details by ASIN
      description: Returns detailed information for a specific product
      operationId: get_product
      parameters:
        - name: asin
          in: path
          required: true
          description: Amazon ASIN (e.g., B09V3KXJPB)
          schema:
            type: string
            pattern: '^[A-Z0-9]{10}$'
      responses:
        '200':
          description: Product details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProductDetail'
        '404':
          description: Product not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /products/watch:
    post:
      tags:
        - Products
      summary: Add ASIN to watchlist
      description: Adds a product ASIN to the active monitoring list
      operationId: add_to_watchlist
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WatchlistRequest'
      responses:
        '201':
          description: ASIN added to watchlist
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WatchlistResponse'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /products/watch:
    get:
      tags:
        - Products
      summary: Get watchlist
      description: Returns the list of ASINs currently being monitored
      operationId: get_watchlist
      responses:
        '200':
          description: List of watched ASINs
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WatchlistResponse'

  /arbitrage:
    get:
      tags:
        - Arbitrage
      summary: List arbitrage opportunities
      description: |
        Returns a list of products with profitable arbitrage opportunities,
        sorted by margin (highest first).
      operationId: list_arbitrage
      parameters:
        - name: min_margin
          in: query
          description: Minimum profit margin percentage
          schema:
            type: number
            default: 15
            minimum: 0
            maximum: 100
        - name: min_profit
          in: query
          description: Minimum absolute profit in EUR
          schema:
            type: number
            default: 10
            minimum: 0
        - name: limit
          in: query
          description: Maximum number of results
          schema:
            type: integer
            default: 50
            minimum: 1
            maximum: 500
        - name: source_marketplace
          in: query
          description: Filter by source marketplace
          schema:
            type: string
            enum: [IT, ES, UK, FR]
        - name: target_marketplace
          in: query
          description: Filter by target marketplace
          schema:
            type: string
            enum: [DE, IT, ES, UK, FR]
            default: DE
      responses:
        '200':
          description: List of arbitrage opportunities
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ArbitrageListResponse'

  /arbitrage/top:
    get:
      tags:
        - Arbitrage
      summary: Get top arbitrage opportunities
      description: Returns the top N arbitrage opportunities with highest margins
      operationId: get_top_arbitrage
      parameters:
        - name: limit
          in: query
          description: Number of top opportunities to return
          schema:
            type: integer
            default: 10
            minimum: 1
            maximum: 100
      responses:
        '200':
          description: Top arbitrage opportunities
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ArbitrageListResponse'

  /stats:
    get:
      tags:
        - Products
      summary: Get statistics
      description: Returns aggregated statistics about tracked products
      operationId: get_stats
      responses:
        '200':
          description: Statistics overview
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StatsResponse'

# Schema Definitions
components:
  schemas:
    # Core Models
    PriceData:
      type: object
      description: Price information for a single marketplace
      properties:
        marketplace:
          type: string
          enum: [DE, IT, ES, UK, FR]
          example: DE
        current_price:
          type: number
          description: Current price in EUR
          example: 149.99
          minimum: 0
        currency:
          type: string
          enum: [EUR, GBP]
          default: EUR
        last_updated:
          type: string
          format: date-time
          description: Timestamp of last price update
          example: "2024-01-15T10:30:00Z"
        price_history:
          type: array
          description: Historical price points (last 30 days)
          items:
            type: object
            properties:
              price:
                type: number
              timestamp:
                type: string
                format: date-time

    ProductSummary:
      type: object
      required:
        - asin
        - title
        - current_prices
        - best_margin
        - last_updated
      properties:
        asin:
          type: string
          pattern: '^[A-Z0-9]{10}$'
          example: "B09V3KXJPB"
        title:
          type: string
          example: "Logitech MX Keys Mini Tastatur QWERTZ DE"
        image_url:
          type: string
          format: uri
          description: Product image URL
        category:
          type: string
          example: "Computer & Accessories"
        current_prices:
          type: object
          additionalProperties:
            type: number
          example:
            DE: 149.99
            IT: 89.99
            UK: 95.00
            ES: 92.50
            FR: 94.00
        best_margin:
          type: number
          description: Best arbitrage margin percentage
          example: 40.0
        best_source:
          type: string
          description: Marketplace with lowest price
          enum: [IT, ES, UK, FR]
          example: IT
        target_marketplace:
          type: string
          enum: [DE, IT, ES, UK, FR]
          default: DE
        estimated_profit:
          type: number
          description: Estimated profit in EUR (DE price - source price)
          example: 60.00
        last_updated:
          type: string
          format: date-time

    ProductDetail:
      allOf:
        - $ref: '#/components/schemas/ProductSummary'
        - type: object
          properties:
            description:
              type: string
            brand:
              type: string
            url:
              type: string
              format: uri
              description: Amazon product URL
            price_history:
              type: array
              items:
                type: object
                properties:
                  marketplace:
                    type: string
                  history:
                    type: array
                    items:
                      type: object
                      properties:
                        price:
                          type: number
                        timestamp:
                          type: string
                          format: date-time
            arbitrage_opportunities:
              type: array
              items:
                type: object
                properties:
                  source_marketplace:
                    type: string
                  target_marketplace:
                    type: string
                  source_price:
                    type: number
                  target_price:
                    type: number
                  margin:
                    type: number
                  profit:
                    type: number
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time

    # Request/Response Models
    ProductListResponse:
      type: object
      properties:
        success:
          type: boolean
          default: true
        data:
          type: object
          properties:
            products:
              type: array
              items:
                $ref: '#/components/schemas/ProductSummary'
            pagination:
              type: object
              properties:
                page:
                  type: integer
                page_size:
                  type: integer
                total_items:
                  type: integer
                total_pages:
                  type: integer
                has_next:
                  type: boolean
                has_previous:
                  type: boolean
        filters_applied:
          type: object
          description: Currently active filters

    ArbitrageOpportunity:
      type: object
      properties:
        asin:
          type: string
        title:
          type: string
        image_url:
          type: string
          format: uri
        source_marketplace:
          type: string
          enum: [IT, ES, UK, FR]
        target_marketplace:
          type: string
          enum: [DE, IT, ES, UK, FR]
        source_price:
          type: number
        target_price:
          type: number
        margin:
          type: number
          description: Profit margin percentage
        profit:
          type: number
          description: Absolute profit in EUR
        fees:
          type: number
          description: Estimated Amazon fees (15% of target price)
          default: 0
        net_profit:
          type: number
          description: Profit after fees
        last_updated:
          type: string
          format: date-time

    ArbitrageListResponse:
      type: object
      properties:
        success:
          type: boolean
          default: true
        data:
          type: object
          properties:
            opportunities:
              type: array
              items:
                $ref: '#/components/schemas/ArbitrageOpportunity'
            summary:
              type: object
              properties:
                total_count:
                  type: integer
                avg_margin:
                  type: number
                avg_profit:
                  type: number
                highest_margin:
                  type: number
                highest_profit:
                  type: number

    WatchlistRequest:
      type: object
      required:
        - asin
      properties:
        asin:
          type: string
          pattern: '^[A-Z0-9]{10}$'
          example: "B09V3KXJPB"
        notes:
          type: string
          maxLength: 500

    WatchlistResponse:
      type: object
      properties:
        success:
          type: boolean
        watchlist:
          type: array
          items:
            type: object
            properties:
              asin:
                type: string
              added_at:
                type: string
                format: date-time
              notes:
                type: string

    HealthResponse:
      type: object
      properties:
        status:
          type: string
          enum: [healthy, degraded, unhealthy]
        timestamp:
          type: string
          format: date-time
        version:
          type: string
        services:
          type: object
          properties:
            elasticsearch:
              type: object
              properties:
                status:
                  type: string
                  enum: [up, down]
                response_time_ms:
                  type: number
            kafka:
              type: object
              properties:
                status:
                  type: string
                  enum: [up, down]
                connected:
                  type: boolean
            keepa_api:
              type: object
              properties:
                status:
                  type: string
                  enum: [up, down, rate_limited]

    StatsResponse:
      type: object
      properties:
        total_products:
          type: integer
        products_with_opportunities:
          type: integer
        avg_margin:
          type: number
        top_marketplace:
          type: string
        last_sync:
          type: string
          format: date-time

    ErrorResponse:
      type: object
      properties:
        success:
          type: boolean
          default: false
        error:
          type: object
          properties:
            code:
              type: string
              example: "NOT_FOUND"
            message:
              type: string
            details:
              type: object

# Kafka Consumer Groups
x-kafka-config:
  consumer_groups:
    - name: "enrichment-consumer"
      topics: ["raw.keepa_updates"]
      concurrency: 3
    - name: "arbitrage-detector"
      topics: ["products.enriched"]
      concurrency: 2
    - name: "alert-dispatcher"
      topics: ["arbitrage.alerts"]
      concurrency: 1
```

## Integration Points

### Consumer → Elasticsearch
```python
# Must match ProductDetail schema
es_client.index(
    index="products",
    id=asin,
    body={
        "asin": "B09V3KXJPB",
        "title": "...",
        "current_prices": {"DE": 149.99, "IT": 89.99},
        "best_margin": 40.0,
        "best_source": "IT",
        "last_updated": "2024-01-15T10:30:00Z"
    }
)
```

### Producer → Kafka
```python
# Must match KeepaUpdate schema
producer.send(
    topic="raw.keepa_updates",
    key=asin.encode(),
    value={
        "asin": "B09V3KXJPB",
        "marketplace": "DE",
        "current_price": 149.99,
        "timestamp": "2024-01-15T10:30:00Z"
    }
)
```

### API → Frontend Response
```python
# Streamlit will receive ArbitrageListResponse
{
    "success": True,
    "data": {
        "opportunities": [
            {
                "asin": "B09V3KXJPB",
                "title": "Logitech MX Keys Mini",
                "source_marketplace": "IT",
                "target_marketplace": "DE",
                "source_price": 89.99,
                "target_price": 149.99,
                "margin": 40.0,
                "profit": 60.0
            }
        ]
    }
}
```
