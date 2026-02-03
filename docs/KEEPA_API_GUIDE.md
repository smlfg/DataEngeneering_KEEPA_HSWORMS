# Keepa API Documentation & Cheatsheet

**Status:** Critical Resource
**Base URL:** `https://api.keepa.com/`
**Official Docs:** [https://keepa.com/#/api/](https://keepa.com/#/api/)

---

## 1. Authentication & Basics

*   **Authentication:** Done via the `key` query parameter.
*   **SSL:** HTTPS is required.
*   **Format:** Responses are always JSON.
*   **Compression:** GZIP is recommended (`Accept-Encoding: gzip`).

**Example Request:**
```bash
https://api.keepa.com/product?key=<YOUR_API_KEY>&domain=3&asin=B000000000
```

---

## 2. The Token System (Quota)

Keepa does **not** use a simple "requests per minute" limit. It uses a **Leaky Bucket** algorithm.

*   **Tokens:** Every request costs tokens.
*   **Bucket:** You have a bucket size (e.g., 300 tokens) that allows for bursts.
*   **Refill:** The bucket refills at a specific rate (e.g., 12 tokens/minute for the Free plan, much higher for paid).
*   **Cost:**
    *   Fetching 1 ASIN = **1 Token**
    *   Fetching 1 ASIN with extensive history = **Can be higher**
    *   Search Request = **10 Tokens** (usually)
    *   Best Sellers Request = **1 Token**

**Response Headers to Watch:**
*   `x-keepa-tokens-left`: How many tokens are currently in your bucket.
*   `x-keepa-tokens-refill-in`: Milliseconds until the next token is added.

> ⚠️ **Important:** If you hit 0 tokens, you get an HTTP 429. The `producer` should sleep if `tokens-left` gets too low.

---

## 3. Domain IDs (Marketplaces)

Keepa uses integer IDs for countries. Use these in the `domain` parameter.

| ID | Country | TLD | Currency |
|----|---------|-----|----------|
| 1  | US      | .com | USD |
| 2  | UK      | .co.uk | GBP |
| 3  | DE      | .de | EUR |
| 4  | FR      | .fr | EUR |
| 5  | JP      | .co.jp | JPY |
| 6  | CA      | .ca | CAD |
| 8  | IT      | .it | EUR |
| 9  | ES      | .es | EUR |
| 10 | IN      | .in | INR |

*(Note: There are others like MX, BR, AU, but these are the main ones).*

---

## 4. Key Endpoints

### A. Retrieve Product Data (`/product`)
The core endpoint. Retrieves price history and details.

*   **Params:**
    *   `asin`: Comma-separated list of ASINs (up to 100 per request).
    *   `history`: `1` to include price history data (default `0`).
    *   `update`: `0` (default) gives cached data. Using non-zero triggers a live update (costs more tokens/time).

### B. Category Best Sellers (`/bestsellers`)
Returns the list of ASINs that are best sellers in a specific category.

*   **Params:**
    *   `category`: The Category Node ID (long integer).
    *   `range`: Range of results (e.g., `100` for top 100).

### C. Search (`/search`)
Find products by keyword.

*   **Params:**
    *   `term`: The search keyword (e.g., "keyboard").
    *   `type`: `product` (default).

---

## 5. The "csv" Price History Format

Keepa saves space by returning price history as compressed integer arrays, not JSON objects.

**Structure:**
The `csv` field in the response is an array of arrays. Each inner array corresponds to a **Price Type**.

**Index Mapping (Most Important):**
| Index | Type | Description |
|-------|------|-------------|
| 0     | AMAZON | Sold and shipped by Amazon |
| 1     | NEW | Lowest New Price (3rd Party) |
| 2     | USED | Lowest Used Price |
| 3     | SALES | Sales Rank |
| 4     | LISTPRICE | List Price (MSRP) |
| 18    | BUY_BOX | The Buy Box Price |

**Data Format within the Array:**
`[time, price, time, price, time, price, ...]`

1.  **Time:** Compressed "Keepa Time Minutes".
    *   **Formula:** `(KeepaTime + 21564000) * 60000 = Unix Timestamp (ms)`
    *   *Simplified:* Keepa Time starts from **2011-01-01**.
2.  **Price:** Integer.
    *   If current price is €19.99, Keepa returns `1999`.
    *   **-1** indicates "Out of Stock" or "No Data".

**Example Decoding:**
Array: `[5000000, 2500, 5000060, 2400, 5000120, -1]`
1.  At time `5000000`, price was `25.00`.
2.  At time `5000060` (1 hour later), price dropped to `24.00`.
3.  At time `5000120`, item went Out of Stock (`-1`).

---

## 6. Important Object Fields

When you get a `product` object back, these are the fields needed for the Arbitrage Tracker:

*   `asin`: The ID.
*   `title`: Product Name.
*   `imagesCSV`: Comma-separated list of image filenames (base: `https://images-na.ssl-images-amazon.com/images/I/`).
*   `brand`: Manufacturer.
*   `categories`: Array of category IDs.
*   `stats`: Contains calculated statistics (current avg, 90-day avg).
    *   `current`: Array of current prices by type.
    *   `avg`: Array of average prices (90 days).
    *   `buyBoxPrice`: Current Buy Box.

---

## 7. Best Practices for this Project

1.  **Batching:** Always request multiple ASINs in one call (up to 20-50 recommended to avoid timeouts) to save overhead, though token cost is per-ASIN.
2.  **Category Mode:** Since we use the `bestsellers` endpoint, remember this list changes. An ASIN might be top 10 today and gone tomorrow.
3.  **Cross-Marketplace:** ASINs are global *usually*. Use the same ASIN to query `domain=3` (DE) and `domain=9` (ES) to detect arbitrage.
