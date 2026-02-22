#!/usr/bin/env python3
"""
Keyboard Collector Orchestrator — Layout-Mismatch Discovery
============================================================
Merges ASINs from multiple sources, validates via Keepa /product,
applies 4-layer layout detection, and outputs keyboard_targets_1000.csv.

Sources:
1. Static ASIN pool (discover_1000_qwertz.py)
2. Amazon scraper output (scrape_amazon_asins.py → amazon_asins_raw.csv)
3. Keepa /deals API (keyboard category)
4. Chrome Extension sessions (manual CSV drops)

Layout Detection Layers:
1. Title keywords (highest confidence)
2. Brand + Model database
3. EAN/GTIN prefix (German origin indicator)
4. Cross-market category presence (suspect)

Output: data/keyboard_targets_1000.csv
"""

import asyncio
import csv
import json
import logging
import os
import sys
import time
import argparse
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Project root for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("collect_keyboards")

KEEPA_API_BASE = "https://api.keepa.com"

# Domain IDs and expected layouts per market
MARKETS = {
    "DE": {"domain_id": 3, "expected_layout": "QWERTZ"},
    "UK": {"domain_id": 2, "expected_layout": "QWERTY"},
    "FR": {"domain_id": 4, "expected_layout": "AZERTY"},
    "IT": {"domain_id": 8, "expected_layout": "QWERTY"},
    "ES": {"domain_id": 9, "expected_layout": "QWERTY"},
}

# Keyboard category IDs per domain (Keepa)
KEYBOARD_CATEGORIES = {
    3: [340843031],  # DE
    2: [340831031],  # UK
    4: [430332031],  # FR
    8: [460161031],  # IT
    9: [937912031],  # ES
}

# ---------------------------------------------------------------------------
# Layer 1: Title-based layout keywords
# ---------------------------------------------------------------------------
LAYOUT_KEYWORDS = {
    "QWERTZ": [
        "qwertz",
        "deutsch",
        "deutsche",
        "deutscher",
        "deutsches",
        "german layout",
        "german-layout",
        "tastatur",
        "iso-de",
        "de layout",
        "de-layout",
        "layout de",
        "germanisch",
        "german version",
        "(de)",
        "[de]",
        "- de",
        "/ de",
    ],
    "AZERTY": [
        "azerty",
        "francais",
        "fran\u00e7ais",
        "french layout",
        "french-layout",
        "clavier fr",
        "disposition fran",
        "layout fr",
        "(fr)",
        "[fr]",
        "- fr",
    ],
    "QWERTY": [
        "qwerty",
        "english layout",
        "us layout",
        "uk layout",
        "us-layout",
        "uk-layout",
        "ansi",
        "english version",
        "international layout",
        "(en)",
        "(us)",
        "(uk)",
    ],
}

# ---------------------------------------------------------------------------
# Layer 2: Known QWERTZ models by brand
# ---------------------------------------------------------------------------
KNOWN_QWERTZ_MODELS = {
    "Cherry": [
        "KC 1000",
        "KC 6000",
        "KC 1068",
        "KC 200",
        "KC 4500",
        "Stream",
        "Stream Desktop",
        "G80",
        "G84",
        "G85",
        "MX Board",
        "MX 2.0S",
        "MX 3.0S",
        "MX 8.2",
        "MX 10.0",
        "DW 3000",
        "DW 5100",
        "DW 9100",
        "B.Unlimited",
        "JK-8500",
        "Strait",
        "GENTIX",
    ],
    "Logitech": [
        "K120 DE",
        "K120 Deutsch",
        "K380 DE",
        "K400 Plus",
        "K400",
        "MX Keys DE",
        "MX Keys S DE",
        "MX Mechanical DE",
        "K780 DE",
        "K580 DE",
        "K270 DE",
        "K375s DE",
        "Craft DE",
        "G213",
        "G413",
        "G513",
        "G PRO",
        "G915",
    ],
    "Microsoft": [
        "Sculpt DE",
        "Sculpt Ergonomic DE",
        "Ergonomic DE",
        "Surface DE",
        "Designer Compact DE",
        "Wired 600 DE",
        "Wireless 850 DE",
    ],
    "Corsair": [
        "K70 DE",
        "K70 RGB DE",
        "K100 DE",
        "K100 RGB DE",
        "K65 DE",
        "K55 DE",
        "K95 DE",
        "K60 DE",
        "K57 DE",
        "Strafe DE",
    ],
    "Razer": [
        "BlackWidow DE",
        "BlackWidow V3 DE",
        "BlackWidow V4",
        "Huntsman DE",
        "Huntsman V2 DE",
        "Huntsman V3",
        "Ornata DE",
        "Ornata V3 DE",
        "Cynosa DE",
        "DeathStalker DE",
    ],
    "SteelSeries": [
        "Apex Pro DE",
        "Apex 7 DE",
        "Apex 3 DE",
        "Apex 5 DE",
        "Apex 9 DE",
    ],
    "HyperX": [
        "Alloy Origins DE",
        "Alloy Elite DE",
        "Alloy FPS DE",
        "Alloy Core DE",
    ],
    "Keychron": [
        "K1 DE",
        "K2 DE",
        "K3 DE",
        "K4 DE",
        "K6 DE",
        "K8 DE",
        "K10 DE",
        "K12 DE",
        "K14 DE",
        "Q1 DE",
        "Q2 DE",
        "Q3 DE",
        "Q5 DE",
        "V1 DE",
        "V3 DE",
        "V5 DE",
    ],
    "Perixx": [
        "PERIBOARD",
        "PERIDUO",
    ],
    "ASUS": [
        "ROG Strix DE",
        "ROG Falchion DE",
        "ROG Azoth DE",
        "TUF Gaming DE",
    ],
    "Roccat": [
        "Vulcan DE",
        "Vulcan TKL DE",
        "Vulcan II DE",
        "Magma DE",
        "Pyro DE",
    ],
}

# ---------------------------------------------------------------------------
# Layer 3: EAN/GTIN prefix ranges by country
# ---------------------------------------------------------------------------
# GS1 prefixes 400-440 = Germany
GERMAN_EAN_PREFIXES = [str(i) for i in range(400, 441)]


def ean_indicates_german(ean_list: list) -> bool:
    """Check if any EAN in the list has a German GS1 prefix (400-440)."""
    for ean in ean_list or []:
        ean_str = str(ean).strip()
        if len(ean_str) >= 3 and ean_str[:3] in GERMAN_EAN_PREFIXES:
            return True
    return False


# ---------------------------------------------------------------------------
# Layout detection engine
# ---------------------------------------------------------------------------


def detect_layout_from_title(title: str) -> Optional[tuple[str, str]]:
    """Layer 1: Detect layout from title keywords.
    Returns (layout, matched_keyword) or None."""
    title_lower = title.lower()
    for layout, keywords in LAYOUT_KEYWORDS.items():
        for kw in keywords:
            if kw in title_lower:
                return layout, kw
    return None


def detect_layout_from_brand_model(
    title: str, brand: str
) -> Optional[tuple[str, str]]:
    """Layer 2: Detect QWERTZ from known brand+model combinations.
    Returns ('QWERTZ', matched_model) or None.
    Two-phase: exact model match first, then base model (without DE/Deutsch suffix)."""
    title_lower = title.lower()
    brand_lower = (brand or "").lower()

    for known_brand, models in KNOWN_QWERTZ_MODELS.items():
        kb_lower = known_brand.lower()
        if kb_lower not in title_lower and kb_lower not in brand_lower:
            continue
        for model in models:
            # Exact match (highest confidence)
            if model.lower() in title_lower:
                return "QWERTZ", f"{known_brand} {model}"
            # Base match without " DE" / " Deutsch" suffix
            base = model.replace(" DE", "").replace(" Deutsch", "").strip()
            if base and base.lower() in title_lower and base.lower() != kb_lower:
                return "QWERTZ", f"{known_brand} {base} (inferred)"
    return None


def detect_layout(
    title: str,
    brand: str,
    ean_list: list,
    exists_on_de: bool,
    market: str,
) -> tuple[str, str, str]:
    """
    4-layer layout detection.

    Returns: (detected_layout, confidence, detection_layer)
    Confidence levels: confident_layout, known_model_layout,
                       ean_inferred_layout, cross_market_suspect, unknown
    """
    # Layer 1: Title keywords
    result = detect_layout_from_title(title)
    if result:
        return result[0], "confident_layout", f"title_keyword:{result[1]}"

    # Layer 2: Brand + Model database
    result = detect_layout_from_brand_model(title, brand)
    if result:
        return result[0], "known_model_layout", f"brand_model:{result[1]}"

    # Layer 3: EAN/GTIN prefix
    if ean_indicates_german(ean_list):
        return "QWERTZ", "ean_inferred_layout", "ean_prefix:400-440"

    # Layer 4: Cross-market presence
    if exists_on_de and market != "DE":
        return "unknown", "cross_market_suspect", f"exists_on_de_listed_on_{market}"

    return "unknown", "unknown", "no_match"


# ---------------------------------------------------------------------------
# Keepa API helpers
# ---------------------------------------------------------------------------


def get_api_key() -> str:
    api_key = os.environ.get("KEEPA_API_KEY", "")
    if not api_key:
        for env_path in [
            Path(__file__).parent.parent / ".env",
            Path(__file__).parent.parent.parent / ".env",
        ]:
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith("KEEPA_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    return api_key


async def check_tokens(client: httpx.AsyncClient, api_key: str) -> dict:
    try:
        resp = await client.get(
            f"{KEEPA_API_BASE}/token", params={"key": api_key}, timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {"tokensLeft": 0, "refillIn": 60}


async def wait_for_tokens(
    client: httpx.AsyncClient, api_key: str, needed: int = 10, max_wait: int = 180
):
    """Wait for Keepa API tokens with timeout."""
    start = time.time()
    while True:
        status = await check_tokens(client, api_key)
        tokens = status.get("tokensLeft", 0)
        if tokens >= needed:
            return tokens
        elapsed = time.time() - start
        if elapsed > max_wait:
            log.warning(f"Token wait timeout after {elapsed:.0f}s (have {tokens}, need {needed})")
            return tokens
        wait = min(status.get("refillIn", 60), 30)
        log.info(f"Tokens: {tokens}/{needed}, waiting {wait}s...")
        await asyncio.sleep(wait + 2)


async def fetch_keepa_deals(
    client: httpx.AsyncClient,
    api_key: str,
    domain_id: int,
    category_ids: list[int],
) -> list[dict]:
    """Fetch keyboard deals from Keepa /deals API."""
    await wait_for_tokens(client, api_key, needed=50)

    params = {
        "key": api_key,
        "domain": domain_id,
        "page": 0,
    }
    if category_ids:
        params["includeCategories"] = ",".join(str(c) for c in category_ids)

    try:
        resp = await client.get(
            f"{KEEPA_API_BASE}/deals", params=params, timeout=30
        )
        if resp.status_code == 404:
            log.warning(f"Deals API not available (404) for domain {domain_id}")
            return []
        if resp.status_code == 429:
            log.warning("Rate limited on /deals, waiting 60s...")
            await asyncio.sleep(60)
            return []
        if resp.status_code != 200:
            log.warning(f"Deals API error {resp.status_code} for domain {domain_id}")
            return []

        data = resp.json()
        items = data if isinstance(data, list) else data.get("deals", data.get("dr", []))

        results = []
        for item in items:
            asin = item.get("asin", "")
            if not asin or len(asin) != 10:
                continue
            results.append(
                {
                    "asin": asin.upper(),
                    "title": item.get("title", ""),
                    "source": "keepa_deals",
                }
            )
        log.info(f"  Keepa /deals domain={domain_id}: {len(results)} ASINs")
        return results

    except Exception as e:
        log.warning(f"Deals API error: {e}")
        return []


async def validate_batch_keepa(
    client: httpx.AsyncClient,
    api_key: str,
    asins: list[str],
    domain_id: int,
    batch_size: int = 50,
) -> list[dict]:
    """Validate ASINs via Keepa /product in batches. Returns enriched product data."""
    validated = []

    for i in range(0, len(asins), batch_size):
        batch = asins[i : i + batch_size]
        await wait_for_tokens(client, api_key, needed=len(batch) + 5)

        try:
            resp = await client.get(
                f"{KEEPA_API_BASE}/product",
                params={
                    "key": api_key,
                    "domain": domain_id,
                    "asin": ",".join(batch),
                },
                timeout=30,
            )

            if resp.status_code == 429:
                log.warning("Rate limited on /product, waiting 60s...")
                await asyncio.sleep(60)
                continue

            if resp.status_code != 200:
                log.warning(f"Product API error {resp.status_code}")
                continue

            data = resp.json()
            products = data.get("products", [])

            for p in products:
                asin = p.get("asin", "")
                title = p.get("title", "")
                if not asin or not title:
                    continue

                csv_data = p.get("csv", [])

                def get_price(idx):
                    if (
                        csv_data
                        and len(csv_data) > idx
                        and csv_data[idx]
                        and isinstance(csv_data[idx], list)
                        and len(csv_data[idx]) >= 2
                        and csv_data[idx][-1] > 0
                    ):
                        return csv_data[idx][-1] / 100
                    return None

                new_price = get_price(1)
                used_price = get_price(2)
                amazon_price = get_price(0)

                # Brand extraction
                brand = p.get("brand", "") or ""
                if not brand:
                    # Try to extract from manufacturer
                    brand = p.get("manufacturer", "") or ""

                # EAN list
                ean_list = p.get("eanList", []) or []

                # Category
                category_tree = p.get("categoryTree", [])
                category = ""
                if category_tree:
                    last_cat = category_tree[-1]
                    if isinstance(last_cat, dict):
                        category = last_cat.get("name", "")
                    else:
                        category = str(last_cat)

                # Rating
                rating = p.get("rating")
                if rating and isinstance(rating, (int, float)):
                    rating = rating / 10 if rating > 10 else rating
                else:
                    rating = None

                validated.append(
                    {
                        "asin": asin.upper(),
                        "title": title[:200],
                        "brand": brand,
                        "new_price": new_price,
                        "used_price": used_price,
                        "amazon_price": amazon_price,
                        "ean_list": ean_list,
                        "category": category,
                        "rating": rating,
                        "domain_id": domain_id,
                    }
                )

        except Exception as e:
            log.warning(f"Product batch error: {e}")

        await asyncio.sleep(2)

    return validated


# ---------------------------------------------------------------------------
# Source loaders
# ---------------------------------------------------------------------------


def load_static_pool() -> list[dict]:
    """Load ASINs from discover_1000_qwertz.py static pool."""
    pool_file = Path(__file__).parent / "discover_1000_qwertz.py"
    if not pool_file.exists():
        log.warning(f"Static pool not found: {pool_file}")
        return []

    asins = []
    in_pool = False
    content = pool_file.read_text()
    for line in content.splitlines():
        if "ASIN_POOL" in line and "=" in line:
            in_pool = True
            continue
        if in_pool:
            if line.strip().startswith("]"):
                break
            # Strip inline comments before parsing
            line = line.split("#")[0].strip().strip(",").strip()
            if line.startswith('"') or line.startswith("'"):
                asin = line.strip("\"'").strip()
                if len(asin) == 10 and asin.startswith("B"):
                    asins.append(
                        {"asin": asin.upper(), "title": "", "source": "static_pool"}
                    )

    log.info(f"Static pool: {len(asins)} ASINs")
    return asins


def load_amazon_scrape(csv_path: Path) -> list[dict]:
    """Load ASINs from Amazon scraper CSV output."""
    if not csv_path.exists():
        log.warning(f"Amazon scrape CSV not found: {csv_path}")
        return []

    results = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            asin = (row.get("asin") or "").strip().upper()
            if len(asin) == 10 and asin.startswith("B"):
                results.append(
                    {
                        "asin": asin,
                        "title": row.get("title", ""),
                        "market": row.get("market", ""),
                        "source": "amazon_scrape",
                    }
                )

    log.info(f"Amazon scrape: {len(results)} ASINs from {csv_path}")
    return results


def load_chrome_session(csv_path: Path) -> list[dict]:
    """Load ASINs from Chrome Extension session CSV."""
    if not csv_path.exists():
        log.info(f"Chrome session CSV not found (optional): {csv_path}")
        return []

    results = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            asin = (row.get("asin") or row.get("ASIN") or "").strip().upper()
            if len(asin) == 10 and asin.startswith("B"):
                results.append(
                    {
                        "asin": asin,
                        "title": row.get("title", row.get("Title", "")),
                        "source": "chrome_session",
                    }
                )

    log.info(f"Chrome session: {len(results)} ASINs from {csv_path}")
    return results


def load_keepa_deals_csv(csv_path: Path) -> list[dict]:
    """Load ASINs from previously saved Keepa deals CSV."""
    if not csv_path.exists():
        return []

    results = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            asin = (row.get("asin") or "").strip().upper()
            if len(asin) == 10 and asin.startswith("B"):
                results.append(
                    {
                        "asin": asin,
                        "title": row.get("title", ""),
                        "source": "keepa_deals",
                    }
                )

    log.info(f"Keepa deals CSV: {len(results)} ASINs")
    return results


# Also load from discover_eu_qwertz_asins.py output files
def load_seed_files(data_dir: Path) -> list[dict]:
    """Load ASINs from seed files (JSON + TXT)."""
    results = []

    json_file = data_dir / "seed_asins_eu_qwertz.json"
    if json_file.exists():
        try:
            data = json.loads(json_file.read_text())
            asins = data.get("asins", [])
            for asin in asins:
                asin = str(asin).strip().upper()
                if len(asin) == 10 and asin.startswith("B"):
                    results.append(
                        {"asin": asin, "title": "", "source": "seed_file"}
                    )
            log.info(f"Seed JSON: {len(results)} ASINs from {json_file}")
        except Exception as e:
            log.warning(f"Error reading seed JSON: {e}")

    txt_file = data_dir / "seed_asins_eu_qwertz.txt"
    if txt_file.exists() and not results:
        try:
            content = txt_file.read_text().strip()
            for asin in content.split(","):
                asin = asin.strip().upper()
                if len(asin) == 10 and asin.startswith("B"):
                    results.append(
                        {"asin": asin, "title": "", "source": "seed_file"}
                    )
            log.info(f"Seed TXT: {len(results)} ASINs from {txt_file}")
        except Exception as e:
            log.warning(f"Error reading seed TXT: {e}")

    return results


# ---------------------------------------------------------------------------
# Merge + Dedup
# ---------------------------------------------------------------------------


def merge_sources(all_sources: list[list[dict]]) -> list[dict]:
    """Merge ASINs from all sources, deduplicating by ASIN.
    Enriches existing entries with missing fields from later sources."""
    seen = {}
    for source_list in all_sources:
        for item in source_list:
            asin = item["asin"]
            if asin not in seen:
                seen[asin] = dict(item)
            else:
                existing = seen[asin]
                if not existing.get("title") and item.get("title"):
                    existing["title"] = item["title"]
                if not existing.get("market") and item.get("market"):
                    existing["market"] = item["market"]
                existing.setdefault("sources", [existing.get("source", "unknown")])
                if item.get("source") and item["source"] not in existing["sources"]:
                    existing["sources"].append(item["source"])

    merged = list(seen.values())
    log.info(f"Merged: {len(merged)} unique ASINs from {len(all_sources)} sources")
    return merged


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


async def run(
    skip_keepa_deals: bool = False,
    skip_validation: bool = False,
    output_path: Path = None,
    data_dir: Path = None,
):
    """Main orchestration: merge, validate, detect layouts, output CSV."""

    project_root = Path(__file__).parent.parent
    if data_dir is None:
        data_dir = project_root / "data"
    if output_path is None:
        output_path = data_dir / "keyboard_targets_1000.csv"

    api_key = get_api_key()
    if not api_key and not skip_keepa_deals:
        log.warning("No KEEPA_API_KEY found. Skipping Keepa API calls.")
        skip_keepa_deals = True
        skip_validation = True

    # Phase 1: Load all sources
    log.info("=" * 60)
    log.info("PHASE 1: Loading sources")
    log.info("=" * 60)

    source_static = load_static_pool()
    source_scrape = load_amazon_scrape(data_dir / "amazon_asins_raw.csv")
    source_chrome = load_chrome_session(data_dir / "chrome_session_asins.csv")
    source_keepa_csv = load_keepa_deals_csv(data_dir / "keepa_deals_keyboards.csv")
    source_seeds = load_seed_files(data_dir)

    # Phase 2: Keepa /deals API (if available)
    source_keepa_deals = []
    if not skip_keepa_deals and api_key:
        log.info("\n" + "=" * 60)
        log.info("PHASE 2: Keepa /deals API")
        log.info("=" * 60)

        async with httpx.AsyncClient() as client:
            for market, info in MARKETS.items():
                if market == "DE":
                    continue  # DE is baseline, we look for mismatches on other markets
                domain_id = info["domain_id"]
                cat_ids = KEYBOARD_CATEGORIES.get(domain_id, [])
                deals = await fetch_keepa_deals(client, api_key, domain_id, cat_ids)
                for d in deals:
                    d["market"] = market
                source_keepa_deals.extend(deals)

        # Save deals to CSV for reuse
        if source_keepa_deals:
            deals_csv = data_dir / "keepa_deals_keyboards.csv"
            deals_csv.parent.mkdir(parents=True, exist_ok=True)
            with open(deals_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["asin", "title", "source", "market"])
                writer.writeheader()
                writer.writerows(source_keepa_deals)
            log.info(f"Saved {len(source_keepa_deals)} deals to {deals_csv}")

    # Phase 3: Merge all sources
    log.info("\n" + "=" * 60)
    log.info("PHASE 3: Merge + Dedup")
    log.info("=" * 60)

    all_merged = merge_sources(
        [
            source_static,
            source_scrape,
            source_keepa_deals,
            source_keepa_csv,
            source_chrome,
            source_seeds,
        ]
    )

    source_counts = {
        "static_pool": len(source_static),
        "amazon_scrape": len(source_scrape),
        "keepa_deals": len(source_keepa_deals) + len(source_keepa_csv),
        "chrome_session": len(source_chrome),
        "seed_files": len(source_seeds),
        "merged_unique": len(all_merged),
    }
    log.info(f"Source counts: {json.dumps(source_counts, indent=2)}")

    # Phase 4: Keepa /product validation (enrich with title, brand, EAN, prices)
    log.info("\n" + "=" * 60)
    log.info("PHASE 4: Keepa /product validation")
    log.info("=" * 60)

    # Build ASIN -> enriched data map
    enriched_map: dict[str, dict] = {}

    if not skip_validation and api_key:
        all_asins = [item["asin"] for item in all_merged]

        async with httpx.AsyncClient() as client:
            # Validate on each target market (non-DE markets for mismatch detection)
            for market, info in MARKETS.items():
                if market == "DE":
                    continue
                domain_id = info["domain_id"]
                log.info(f"  Validating {len(all_asins)} ASINs on {market} (domain={domain_id})...")
                validated = await validate_batch_keepa(
                    client, api_key, all_asins, domain_id, batch_size=50
                )
                for v in validated:
                    key = (v["asin"], domain_id)
                    enriched_map[f"{v['asin']}_{domain_id}"] = {
                        **v,
                        "market": market,
                    }
                log.info(f"  {market}: {len(validated)} products found on Keepa")

            # Also check DE to know which ASINs exist there (for Layer 4)
            log.info(f"  Validating {len(all_asins)} ASINs on DE (baseline)...")
            de_validated = await validate_batch_keepa(
                client, api_key, all_asins, 3, batch_size=50
            )
            de_asins = {v["asin"] for v in de_validated}
            log.info(f"  DE: {len(de_asins)} products found on Keepa")
    else:
        de_asins = set()
        # Use title/source info from merge if no validation
        for item in all_merged:
            item_market = item.get("market")
            for market, info in MARKETS.items():
                if market == "DE":
                    continue
                # Only create entry for the source market, or if no market known
                if item_market and item_market != market and item_market != "DE":
                    continue
                domain_id = info["domain_id"]
                enriched_map[f"{item['asin']}_{domain_id}"] = {
                    "asin": item["asin"],
                    "title": item.get("title", ""),
                    "brand": "",
                    "new_price": None,
                    "used_price": None,
                    "amazon_price": None,
                    "ean_list": [],
                    "category": "",
                    "rating": None,
                    "domain_id": domain_id,
                    "market": market,
                }

    # Phase 5: Layout detection + mismatch classification
    log.info("\n" + "=" * 60)
    log.info("PHASE 5: Layout detection + mismatch classification")
    log.info("=" * 60)

    output_rows = []
    confidence_counts = defaultdict(int)

    for key, product in enriched_map.items():
        asin = product["asin"]
        market = product["market"]
        domain_id = product["domain_id"]
        title = product.get("title", "")
        brand = product.get("brand", "")
        ean_list = product.get("ean_list", [])
        exists_on_de = asin in de_asins

        # Detect layout
        detected_layout, confidence, detection_layer = detect_layout(
            title=title,
            brand=brand,
            ean_list=ean_list,
            exists_on_de=exists_on_de,
            market=market,
        )

        # Determine expected layout for this market
        expected_layout = MARKETS[market]["expected_layout"]

        # Is it a mismatch?
        is_mismatch = (
            detected_layout != "unknown"
            and detected_layout != expected_layout
        )

        # Find source from merged data
        source = "unknown"
        for item in all_merged:
            if item["asin"] == asin:
                source = item.get("source", "unknown")
                break

        confidence_counts[confidence] += 1

        output_rows.append(
            {
                "asin": asin,
                "domain_id": domain_id,
                "market": market,
                "title": title[:200],
                "detected_layout": detected_layout,
                "expected_layout": expected_layout,
                "is_mismatch": str(is_mismatch).lower(),
                "confidence": confidence,
                "detection_layer": detection_layer,
                "new_price": product.get("new_price"),
                "used_price": product.get("used_price"),
                "brand": brand,
                "source": source,
            }
        )

    # Sort: mismatches first, then by confidence
    confidence_order = {
        "confident_layout": 0,
        "known_model_layout": 1,
        "ean_inferred_layout": 2,
        "cross_market_suspect": 3,
        "unknown": 4,
    }
    output_rows.sort(
        key=lambda r: (
            r["is_mismatch"] != "true",
            confidence_order.get(r["confidence"], 99),
        )
    )

    # Phase 6: Write output
    log.info("\n" + "=" * 60)
    log.info("PHASE 6: Output")
    log.info("=" * 60)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "asin",
        "domain_id",
        "market",
        "title",
        "detected_layout",
        "expected_layout",
        "is_mismatch",
        "confidence",
        "detection_layer",
        "new_price",
        "used_price",
        "brand",
        "source",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    mismatch_count = sum(1 for r in output_rows if r["is_mismatch"] == "true")
    unique_asins = len(set(r["asin"] for r in output_rows))

    log.info(f"Total rows: {len(output_rows)}")
    log.info(f"Unique ASINs: {unique_asins}")
    log.info(f"Mismatches: {mismatch_count}")
    log.info(f"Confidence distribution: {dict(confidence_counts)}")
    log.info(f"Output: {output_path}")

    # Summary JSON
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_rows": len(output_rows),
        "unique_asins": unique_asins,
        "mismatches": mismatch_count,
        "source_counts": source_counts,
        "confidence_distribution": dict(confidence_counts),
    }
    summary_path = output_path.with_suffix(".json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log.info(f"Summary: {summary_path}")

    return output_rows


async def main():
    parser = argparse.ArgumentParser(
        description="Keyboard Collector Orchestrator — Layout-Mismatch Discovery"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="data/keyboard_targets_1000.csv",
        help="Output CSV path",
    )
    parser.add_argument(
        "--skip-deals",
        action="store_true",
        help="Skip Keepa /deals API calls",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip Keepa /product validation (use cached/source data only)",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Data directory (default: project_root/data)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    data_dir = Path(args.data_dir) if args.data_dir else project_root / "data"
    output_path = project_root / args.output

    log.info("Keyboard Collector Orchestrator v3")
    log.info(f"  Output: {output_path}")
    log.info(f"  Data dir: {data_dir}")
    log.info(f"  Skip deals: {args.skip_deals}")
    log.info(f"  Skip validation: {args.skip_validation}")

    start = time.time()
    results = await run(
        skip_keepa_deals=args.skip_deals,
        skip_validation=args.skip_validation,
        output_path=output_path,
        data_dir=data_dir,
    )
    elapsed = time.time() - start
    log.info(f"\nDone in {elapsed/60:.1f} minutes. Total: {len(results)} rows.")


if __name__ == "__main__":
    asyncio.run(main())
