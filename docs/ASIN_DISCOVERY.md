# ASIN Discovery System

## Overview

The ASIN Discovery System is an automated pipeline component designed to identify German QWERTZ keyboard products from category bestsellers across European Amazon marketplaces that can be arbitraged to Germany (DE). The system leverages Keepa's product search and bestsellers APIs to discover new arbitrage opportunities and automatically adds them to the price monitoring watchlist.

The core discovery logic is implemented in `scripts/discover_german_keyboards.py`, which:
- Fetches category bestsellers from UK, IT, ES, and FR marketplaces
- Analyzes product prices across all EU marketplaces
- Identifies products with arbitrage potential (profit margin >= 20%)
- Exports discovered ASINs to the watchlist for continuous price monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ASIN Discovery System                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐  │
│  │ Keepa Best-     │────▶│ Discovery Script │────▶│ Output Files        │  │
│  │ sellers API     │     │ (Python)         │     │ - watchlist_*.txt   │  │
│  │ (1 token/query) │     │                  │     │ - arbitrage_*.json  │  │
│  └─────────────────┘     └──────────────────┘     └─────────────────────┘  │
│                                                                             │
│                              │                                              │
│                              ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    config/watchlist.txt                                │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│                              ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    Airflow DAG Pipeline                                │  │
│  │  ┌─────────┐   ┌──────────┐   ┌─────────┐   ┌─────────────────────┐  │  │
│  │  │ Watchlist│──▶│ Producer │──▶│  Kafka  │──▶│ Consumer / Arbitrage │  │  │
│  │  │  (File) │   │  (Batch) │   │  Topic  │   │      Detector       │  │  │
│  │  └─────────┘   └──────────┘   └─────────┘   └─────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## How It Works

### 1. Keepa Product Search

The discovery system uses Keepa's `/bestsellers` endpoint to fetch top products from keyboard categories:

**Endpoint:** `https://api.keepa.com/bestsellers`

**Parameters:**
- `category`: Category node ID (e.g., `13978270031` for UK PC Gaming Keyboards)
- `domain`: Marketplace domain ID (2=UK, 3=DE, 4=FR, 8=IT, 9=ES)
- `range`: Time range in days (30 = last 30 days bestsellers)

**Token Cost:** 1 token per bestsellers query (range=30)

**Response:** Returns up to 10,000 ASINs from the category bestsellers list.

### 2. Price Analysis and Arbitrage Detection

For each discovered ASIN, the system:

1. Queries product prices across all marketplaces using `/product` endpoint
2. Identifies the cheapest source market (UK, IT, ES, or FR)
3. Compares against German (DE) target market price
4. Calculates profit margin: `margin = (DE_price - source_price) / DE_price * 100`
5. Filters for opportunities with minimum 20% margin and max €200 DE price

### 3. Cross-Marketplace Strategy

**Source Markets:**
| Code | Domain ID | Category Type | Category IDs |
|------|-----------|---------------|--------------|
| UK   | 2         | Gaming        | 13978270031  |
| UK   | 2         | General       | 430565031    |
| IT   | 8         | Gaming        | 13900031031  |
| IT   | 8         | General       | 460154031    |
| ES   | 9         | Gaming        | 911112031    |
| ES   | 9         | General       | 937892031    |
| FR   | 4         | Gaming        | 430334031    |
| FR   | 4         | General       | 430328031    |

**Target Market:** Germany (DE, domain ID 3)

## Usage

### Manual Discovery Run

```bash
# Discover in all EU marketplaces (default)
python scripts/discover_german_keyboards.py

# Specific marketplace only
python scripts/discover_german_keyboards.py --marketplace FR

# Custom search parameters
python scripts/discover_german_keyboards.py --min-margin 25 --max-price 150

# Limit products per country
python scripts/discover_german_keyboards.py --products 50

# All options combined
python scripts/discover_german_keyboards.py --min-margin 20 --max-price 200 --products 100
```

**Arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `--api-key` | env:KEEPA_API_KEY | Keepa API key |
| `--min-margin` | 20.0 | Minimum profit margin percentage |
| `--max-price` | 200.0 | Maximum DE price in EUR |
| `--products` | 100 | Products per country to analyze |
| `--output-dir` | data/discovery | Output directory for results |

### Scheduled Discovery (Airflow)

The Airflow DAG `keepa_arbitrage_pipeline.py` runs every 30 minutes and processes ASINs from the watchlist. To integrate discovery into scheduled runs:

1. **Trigger manual discovery:**
   ```bash
   python scripts/discover_german_keyboards.py
   ```

2. **The discovered ASINs are automatically added to:** `config/watchlist.txt`

3. **Restart the producer to pick up new ASINs:**
   ```bash
   docker compose restart producer
   ```

4. **View results in the dashboard:** `http://localhost:8501`

### Output Files

**Location:** `data/discovery/`

| File | Format | Description |
|------|--------|-------------|
| `watchlist_german_keyboards.txt` | Plain text | ASINs ready for monitoring |
| `arbitrage_opportunities.json` | JSON | Full opportunity details |
| `asins_{marketplace}.txt` | Plain text | Raw ASINs per marketplace |

**Watchlist Format (`watchlist_german_keyboards.txt`):**
```
# German QWERTZ Keyboard Watchlist
# Generated: 2025-01-11T22:53:00.000000
# Total products: 42
#
# Format: ASIN | Source | DE Price | Margin | Title
#

B09V3KXJPB | UK | €89.99 | 28.5% | Corsair K70 RGB Pro Gaming Keyboard
B07Y19G9H2 | FR | €129.99 | 22.3% | Logitech MX Keys QWERTZ
```

## Rate Limiting

### Keepa Token Budget

**Plan Assumption:** 20 tokens/minute bucket rate

**Discovery Cost Breakdown:**
| Operation | Tokens | Frequency |
|-----------|--------|-----------|
| Bestsellers query (per category) | 1 | 8 queries (4 markets x 2 categories) |
| Product price query (per ASIN) | 1 | ~400 ASINs |
| Product details (top 50) | 1 | 50 ASINs |
| **Total per run** | ~458 tokens | ~3-5 minutes at 20/min |

**Recommendation:** Run discovery weekly to conserve tokens for daily price monitoring.

### Token Tracking

The discovery script tracks token usage from the Keepa API response headers:
- `x-keepa-tokens-left`: Current tokens in bucket
- `x-keepa-tokens-refill-in`: Milliseconds until next token

The script includes automatic rate limiting (3-second delays between category queries) to avoid exhausting the token bucket.

## Configuration

### Environment Variables

```bash
# Required
export KEEPA_API_KEY=your_key_here

# Optional
export DISCOVERY_OUTPUT_DIR=data/discovery
export WATCHLIST_PATH=config/watchlist.txt
```

### Customizing Search Terms

Modify the `CATEGORIES` dictionary in `scripts/discover_german_keyboards.py`:

```python
CATEGORIES = {
    "UK": {
        "gaming": 13978270031,  # PC Gaming Keyboards
        "general": 430565031,   # Keyboards
    },
    # Add new marketplace
    "PL": {  # Poland (if available)
        "gaming": XXXXXXXXXX,
        "general": XXXXXXXXXX,
    },
}
```

### Marketplace Selection

The script is pre-configured for UK, IT, ES, and FR as source markets. To modify:

```python
# In GermanKeyboardDiscovery class
SOURCE_DOMAINS = {
    "UK": 2,
    "IT": 8,
    "ES": 9,
    "FR": 4,
    # Add or remove markets here
}
```

## Integration with Price Monitoring

The discovered ASINs flow into the existing pipeline:

```
1. Discovery Script → Adds ASINs to config/watchlist.txt
2. Watchlist File   → Read by Airflow DAG (fetch_watchlist task)
3. DAG              → Fetches prices via Keepa API (1 token/ASIN)
4. Kafka            → Raw updates published to raw.keepa_updates topic
5. Consumer         → Processes updates, detects arbitrage
6. Elasticsearch    → Indexed for dashboard and alerts
```

See [KAFKA_CONTRACT.md](KAFKA_CONTRACT.md) for Kafka topic details and [WORKER_TASKS.md](WORKER_TASKS.md) for producer/consumer implementation.

## Troubleshooting

### "Rate limit exceeded"

**Symptoms:** HTTP 429 errors, "Token limit reached" messages

**Solutions:**
1. Check token consumption in logs: `grep tokens_used logs/*.log`
2. Reduce discovery frequency (weekly instead of daily)
3. Limit marketplaces: `python scripts/discover_german_keyboards.py --marketplace UK`
4. Reduce products per country: `--products 50`

### "No ASINs found"

**Symptoms:** Discovery returns 0 opportunities

**Solutions:**
1. Verify search terms are correct: check category IDs
2. Test API key: `curl "https://api.keepa.com/?key=$KEEPA_API_KEY&domain=1"`
3. Reduce minimum margin: `--min-margin 10`
4. Increase maximum price: `--max-price 300`
5. Check marketplace domain IDs in `SOURCE_DOMAINS`

### "Duplicate ASINs"

**Explanation:** Duplicate ASINs are normal - the same product can appear in:
- Multiple categories (gaming + general)
- Multiple marketplaces
- Multiple search results

**Solution:** The script deduplicates ASINs before analysis. Check the watchlist for existing entries.

### "API key invalid"

**Symptoms:** 401 Unauthorized errors

**Solutions:**
1. Verify API key in `.env` file
2. Check `KEEPA_API_KEY` environment variable
3. Ensure key has bestsellers endpoint access

### Discovery runs slowly

**Explanation:** Discovery queries ~400 ASINs at 1 token each, plus 8 category queries.

**Solutions:**
1. Reduce `--products` parameter (fewer ASINs to query)
2. Limit marketplaces (fewer category queries)
3. Run during off-peak hours

## Best Practices

1. **Run discovery weekly** - Conserve tokens for daily price monitoring
2. **Monitor token consumption** - Check logs for token usage per run
3. **Review discovered ASINs** - Manually verify arbitrage potential before adding
4. **Archive old results** - Move old discovery files to `data/discovery/archive/`
5. **Test with single marketplace** - Use `--marketplace UK` for initial testing
6. **Set appropriate thresholds** - Start with `--min-margin 15` and adjust
7. **Check category IDs** - Verify category node IDs are current

## Metrics & Monitoring

Track discovery effectiveness with these metrics:

| Metric | Description | Target |
|--------|-------------|--------|
| ASINs discovered | New ASINs found per run | >100 |
| Duplicate rate | % of ASINs already in watchlist | <30% |
| Token consumption | Tokens used per run | ~458 |
| WHD hit rate | % with warehouse deals potential | >10% |
| High-margin rate | % with margin >30% | >20% |

**Log file location:** `logs/discover_german_keyboards_{timestamp}.log`

## Future Enhancements

1. **ML-based ASIN ranking** - Predict arbitrage potential based on historical data
2. **Brand filtering** - Auto-accept trusted brands, flag unknown ones
3. **Price range filtering** - Dynamic ranges based on category averages
4. **Automatic watchlist pruning** - Remove unprofitable ASINs after N days
5. **Multi-category support** - Beyond keyboards (e.g., mice, headsets)
6. **Real-time discovery** - Trigger on new bestsellers entries
7. **Warehouse Deals detection** - Filter for Amazon Warehouse sellers

## References

- [Keepa API Documentation](https://keepa.com/#/api/)
- [KAFKA_CONTRACT.md](KAFKA_CONTRACT.md) - Kafka topic specifications
- [WORKER_TASKS.md](WORKER_TASKS.md) - Producer/consumer details
- [KEEPA_API_GUIDE.md](KEEPA_API_GUIDE.md) - Complete API reference
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture overview
- Airflow DAG: `dags/keepa_arbitrage_pipeline.py`
- Discovery Script: `scripts/discover_german_keyboards.py`
