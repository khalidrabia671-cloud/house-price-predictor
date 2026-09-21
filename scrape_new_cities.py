"""
scrape_new_cities.py
---------------------
Sirf Jhelum aur Wazirabad ka data scrape karta hai (Gujrat/Gujranwala/Sialkot
already scrape ho chuke hain, unhe dobara scrape karne ki zaroorat nahi).

Usage:
    python scrape_new_cities.py

Output:
    data/raw_data_new_cities.csv
"""

import re
import time
import random
import csv
import os
import sys

import requests
from bs4 import BeautifulSoup

CITIES = {
    "Jhelum": 19,
    "Wazirabad": 1395,
}

PROPERTY_TYPE_PATHS = {
    "House": "Houses_Property",
    "Flat": "Flats_Apartments",
}

URL_TEMPLATE = "https://www.zameen.com/{type_path}/{city}-{city_id}-{page}.html"
MAX_PAGES_PER_TYPE = 60

MIN_DELAY = 2.0
MAX_DELAY = 4.5

OUTPUT_PATH = os.path.join("data", "raw_data_new_cities.csv")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

PRICE_RE = re.compile(r"PKR\s*([\d,.]+)\s*(Crore|Lakh|Lac|Arab)?", re.IGNORECASE)
SIZE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(Marla|Kanal)", re.IGNORECASE)


def parse_price(text):
    m = PRICE_RE.search(text)
    if not m:
        return None, None
    value = m.group(1).replace(",", "")
    unit = m.group(2)
    try:
        return float(value), unit
    except ValueError:
        return None, unit


def parse_size(text):
    m = SIZE_RE.search(text)
    if not m:
        return None, None
    return float(m.group(1)), m.group(2)


def price_to_pkr(value, unit):
    if value is None:
        return None
    unit = (unit or "").lower()
    if unit == "crore":
        return value * 1_00_00_000
    if unit in ("lakh", "lac"):
        return value * 1_00_000
    if unit == "arab":
        return value * 1_00_00_00_000
    return value


def size_to_marla(value, unit):
    if value is None:
        return None
    if (unit or "").lower() == "kanal":
        return value * 20
    return value


def scrape_page(url, city):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    rows = []
    seen_urls = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "/Property/" not in href:
            continue

        full_url = href if href.startswith("http") else "https://www.zameen.com" + href
        if full_url in seen_urls:
            continue

        container = a_tag
        text = ""
        for _ in range(8):
            if container.parent is None:
                break
            container = container.parent
            candidate_text = container.get_text(" ", strip=True)
            if "PKR" in candidate_text and len(candidate_text) < 1500:
                text = candidate_text
                break

        if not text:
            continue

        seen_urls.add(full_url)

        price_val, price_unit = parse_price(text)
        size_val, size_unit = parse_size(text)
        title = a_tag.get("title") or a_tag.get_text(strip=True)

        rows.append({
            "Title": title,
            "Price_Raw": f"{price_val} {price_unit}" if price_val else None,
            "Price_PKR": price_to_pkr(price_val, price_unit),
            "Size_Raw": f"{size_val} {size_unit}" if size_val else None,
            "Size_Marla": size_to_marla(size_val, size_unit),
            "Listing_URL": full_url,
            "City": city,
        })

    return rows


def main():
    all_rows = []
    os.makedirs("data", exist_ok=True)

    for city, city_id in CITIES.items():
        for property_type, type_path in PROPERTY_TYPE_PATHS.items():
            print(f"\n=== Scraping {property_type}s in {city} ===")
            for page in range(1, MAX_PAGES_PER_TYPE + 1):
                url = URL_TEMPLATE.format(type_path=type_path, city=city, city_id=city_id, page=page)
                print(f"  Page {page}: {url}")

                try:
                    rows = scrape_page(url, city)
                except requests.exceptions.RequestException as e:
                    print(f"  !! Request failed: {e} — stopping.")
                    break

                if not rows:
                    print("  No listings found — reached last page.")
                    break

                for r in rows:
                    r["Property_Type"] = property_type
                all_rows.extend(rows)
                print(f"  -> {len(rows)} listings (total so far: {len(all_rows)})")

                time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    if not all_rows:
        print("\nKoi data scrape nahi hua.")
        sys.exit(1)

    fieldnames = list(all_rows[0].keys())
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nDone! {len(all_rows)} listings saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
