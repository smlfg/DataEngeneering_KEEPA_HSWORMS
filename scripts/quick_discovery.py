#!/usr/bin/env python3
"""
German Keyboard Discovery - Sequential with long pauses
"""

import sys
import os
import time
from pathlib import Path
from typing import Set, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.producer.keepa_client import KeepaClient

KEEPA_API_KEY = os.getenv("KEEPA_API_KEY", "")
if not KEEPA_API_KEY:
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().split("\n"):
            if line.startswith("KEEPA_API_KEY="):
                KEEPA_API_KEY = line.split("=", 1)[1].strip()
                break

if not KEEPA_API_KEY:
    print("❌ No API key found")
    sys.exit(1)

DOMAINS = {
    "UK": (2, {430565031: "Keyboards", 13978270031: "Gaming Keyboards"}),
    "IT": (8, {460154031: "Tastiere", 13900031031: "Tastiere da gioco"}),
    "ES": (9, {937892031: "Teclados", 911112031: "Teclados gaming"}),
    "FR": (4, {430328031: "Claviers", 430334031: "Claviers gaming"}),
}

# Use 5 requests per minute to be safe (12 second gap)
client = KeepaClient(api_key=KEEPA_API_KEY, requests_per_minute=5)


def safe_request(func, *args, **kwargs):
    """Execute request with error handling."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "Rate limit" in str(e) or "429" in str(e):
                wait_time = 60 * (attempt + 1)  # 60s, 120s, 180s
                print(f"     ⏳ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    raise Exception(f"Failed after {max_retries} retries")


print("🔍 German Keyboard Discovery")
print("=" * 50)

all_asins: Dict[str, Set[str]] = {}

for market, (domain_id, categories) in DOMAINS.items():
    print(f"\n🌍 {market}:")
    market_asins: Set[str] = set()

    for cat_id, cat_name in categories.items():
        print(f"  📦 {cat_name}...", end=" ", flush=True)

        asins = safe_request(
            client.category_bestsellers, category_id=cat_id, domain=domain_id, limit=50
        )
        print(f"Found {len(asins)}")
        market_asins.update(asins)

        # Wait 15 seconds between requests
        time.sleep(15)

    all_asins[market] = market_asins
    print(f"  ✅ {market}: {len(market_asins)} ASINs")

# Save
output_dir = Path(__file__).parent.parent / "data" / "discovery"
output_dir.mkdir(parents=True, exist_ok=True)

for market, asins in all_asins.items():
    filepath = output_dir / f"asins_{market.lower()}.txt"
    with open(filepath, "w") as f:
        for asin in sorted(asins):
            f.write(f"{asin}\n")

all_unique = set()
for asins in all_asins.values():
    all_unique.update(asins)

filepath = output_dir / "asins_all.txt"
with open(filepath, "w") as f:
    for asin in sorted(all_unique):
        f.write(f"{asin}\n")

print(f"\n✅ Total: {len(all_unique)} unique ASINs")
print(f"💾 Saved to {output_dir}/")
