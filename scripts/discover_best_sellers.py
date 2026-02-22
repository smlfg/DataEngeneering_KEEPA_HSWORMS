import os
import csv
import requests
from dotenv import load_dotenv

load_dotenv()

KEEPA_API_KEY = os.getenv("KeepaAPIKey")
CATEGORY = 162463031
DOMAINS = {
    2: "UK",
    3: "DE",
    4: "FR",
    8: "IT",
    9: "ES",
}
FILTER_TERMS = ["qwertz", "flat", "slim", "flach", "plat"]
OUTPUT_FILE = "data/seed_best_sellers.csv"
RANGES = [0, 30, 60, 90]


def check_api_access() -> bool:
    url = f"https://api.keepa.com/bestsellers/?key={KEEPA_API_KEY}&domain=3&category=1"
    response = requests.get(url, timeout=30)
    data = response.json()
    return "bestSellersList" in data and data["bestSellersList"] is not None


def fetch_bestsellers(domain: int, range_offset: int = 0) -> list:
    url = f"https://api.keepa.com/bestsellers/?key={KEEPA_API_KEY}&domain={domain}&category={CATEGORY}&range={range_offset}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("bestSellersList", [])


def fetch_product_titles(domain: int, asins: list) -> dict:
    if not asins:
        return {}
    asins_str = ",".join(asins[:100])
    url = f"https://api.keepa.com/product/?key={KEEPA_API_KEY}&domain={domain}&ids={asins_str}&stats=0"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    titles = {}
    for product in data.get("products", []):
        asin = product.get("asin", "")
        title = product.get("title", "")
        if asin and title:
            titles[asin] = title
    return titles


def filter_keyboards(asins: list, titles: dict, domain_name: str) -> list:
    filtered = []
    for asin in asins:
        title = titles.get(asin, "").lower()
        if any(term in title for term in FILTER_TERMS):
            filtered.append(
                {
                    "asin": asin,
                    "title": titles.get(asin, ""),
                    "domain": domain_name,
                }
            )
    return filtered


def main():
    print("Checking Keepa API bestsellers access...")
    if not check_api_access():
        print(
            "WARNING: API key does not have bestsellers access (free tier limitation)"
        )
        print("Creating empty seed file. Manual ASIN entry required.")
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["asin", "title", "domain"])
            writer.writeheader()
        print(f"Created empty file: {OUTPUT_FILE}")
        return

    all_keyboards = []

    for domain_id, domain_name in DOMAINS.items():
        print(f"Fetching best sellers from {domain_name} (domain {domain_id})...")
        try:
            all_asins = []
            for range_offset in RANGES:
                asins = fetch_bestsellers(domain_id, range_offset)
                all_asins.extend(asins)

            print(f"  Got {len(all_asins)} ASINs, fetching titles...")

            titles = fetch_product_titles(domain_id, all_asins)
            keyboards = filter_keyboards(all_asins, titles, domain_name)
            all_keyboards.extend(keyboards)
            print(f"  Found {len(keyboards)} matching keyboards")
        except Exception as e:
            print(f"  Error fetching {domain_name}: {e}")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["asin", "title", "domain"])
        writer.writeheader()
        writer.writerows(all_keyboards)

    print(f"\nSaved {len(all_keyboards)} keyboards to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
