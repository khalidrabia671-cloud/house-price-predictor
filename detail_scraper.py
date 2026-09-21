"""
detail_scraper.py
------------------
data/raw_data.csv mein maujood har Listing_URL ko visit kar ke uske
individual detail page se Bedroom(s), Bath(s), aur exact Location nikalta hai.

Ye har listing ke liye ek page load karta hai, isliye pehle scraper (scraper.py)
se zyada waqt lega. ~1400 listings ke liye roughly 45-60 minute lag sakta hai.

Usage:
    python detail_scraper.py

Output:
    data/raw_data_detailed.csv   (original columns + Bedrooms, Bathrooms, Location)

NOTE: Beech mein rok kar dobara chalayein to ye already-scraped listings
skip kar dega (checkpoint save hota hai har 50 rows ke baad).
"""

import re
import time
import random
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup

INPUT_PATH = os.path.join("data", "raw_data.csv")
OUTPUT_PATH = os.path.join("data", "raw_data_detailed.csv")

MIN_DELAY = 1.5
MAX_DELAY = 3.0

SAVE_EVERY = 50  # har 50 listings ke baad progress save karo

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def extract_details(url):
    """Ek listing ke detail page se Bedrooms, Bathrooms, Location nikalo.

    Page ka structure aisa hai ke label ("Bedroom(s)", "Bath(s)", "Location")
    aur uski value alag-alag lines pe aati hain, isliye hum label dhoondh kar
    uske turant baad wali line ko value maante hain.
    """
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    lines = [l.strip() for l in soup.get_text("\n").split("\n") if l.strip()]

    bedrooms, bathrooms, location = None, None, None

    for i, line in enumerate(lines):
        next_line = lines[i + 1] if i + 1 < len(lines) else ""

        if line == "Bedroom(s)" and bedrooms is None:
            bedrooms = None if next_line in ("", "-") else next_line
        elif line == "Bath(s)" and bathrooms is None:
            bathrooms = None if next_line in ("", "-") else next_line
        elif line == "Location" and location is None:
            location = None if next_line in ("", "-") else next_line

    return bedrooms, bathrooms, location


def main():
    df = pd.read_csv(INPUT_PATH)

    # Agar pehle se partial progress hai to usay resume karo
    if os.path.exists(OUTPUT_PATH):
        done_df = pd.read_csv(OUTPUT_PATH)
        done_urls = set(done_df["Listing_URL"])
        print(f"Resuming: {len(done_urls)} listings already done.")
    else:
        done_df = pd.DataFrame()
        done_urls = set()

    results = [done_df] if not done_df.empty else []
    buffer = []

    remaining = df[~df["Listing_URL"].isin(done_urls)]
    print(f"Total remaining to scrape: {len(remaining)}")

    for i, row in enumerate(remaining.itertuples(), 1):
        url = row.Listing_URL
        try:
            bedrooms, bathrooms, location = extract_details(url)
        except requests.exceptions.RequestException as e:
            print(f"  [{i}/{len(remaining)}] FAILED: {url} ({e})")
            bedrooms, bathrooms, location = None, None, None

        new_row = row._asdict()
        new_row.pop("Index", None)
        new_row["Bedrooms"] = bedrooms
        new_row["Bathrooms"] = bathrooms
        new_row["Location"] = location
        buffer.append(new_row)

        print(f"  [{i}/{len(remaining)}] Beds={bedrooms} Baths={bathrooms} Loc={location}")

        if i % SAVE_EVERY == 0 or i == len(remaining):
            combined = pd.concat(results + [pd.DataFrame(buffer)], ignore_index=True)
            combined.to_csv(OUTPUT_PATH, index=False)
            results = [combined]
            buffer = []
            print(f"  --- Progress saved ({len(combined)} total rows) ---")

        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    print(f"\nDone! Detailed data saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
