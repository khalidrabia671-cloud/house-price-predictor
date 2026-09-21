"""
geocode_areas.py
-----------------
Har unique (Area, City) combination ko latitude/longitude coordinates mein
convert karta hai, taake map pe plot ho sakein. OpenStreetMap ka free
Nominatim service use karta hai (koi API key nahi chahiye).

Usage:
    python geocode_areas.py

Output:
    data/area_coordinates.csv   (Area, City, Latitude, Longitude)

NOTE: Nominatim ka free tier rate-limited hai (~1 request/second), aur
ye sirf unique areas ko geocode karta hai (na ke har listing ko), isliye
zyada time nahi lagna chahiye (typically 20-50 unique areas honge).
"""

import time
import os

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

INPUT_PATH = os.path.join("data", "clean_data.csv")
OUTPUT_PATH = os.path.join("data", "area_coordinates.csv")


def main():
    df = pd.read_csv(INPUT_PATH)

    if "Area" not in df.columns:
        print("'Area' column nahi mili. Pehle data_cleaning.ipynb chalayein.")
        return

    unique_areas = df[["Area", "City"]].drop_duplicates().reset_index(drop=True)
    print(f"Total unique areas to geocode: {len(unique_areas)}")

    geolocator = Nominatim(user_agent="house_price_predictor_project")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.2)

    results = []
    for i, row in unique_areas.iterrows():
        query = f"{row['Area']}, {row['City']}, Punjab, Pakistan"
        print(f"[{i+1}/{len(unique_areas)}] Geocoding: {query}")

        try:
            location = geocode(query)
        except Exception as e:
            print(f"  Failed: {e}")
            location = None

        if location:
            results.append({
                "Area": row["Area"],
                "City": row["City"],
                "Latitude": location.latitude,
                "Longitude": location.longitude,
            })
            print(f"  -> {location.latitude:.4f}, {location.longitude:.4f}")
        else:
            # Fallback: agar area specifically na mile, city ka center use karo
            city_query = f"{row['City']}, Punjab, Pakistan"
            try:
                city_location = geocode(city_query)
            except Exception:
                city_location = None

            if city_location:
                results.append({
                    "Area": row["Area"],
                    "City": row["City"],
                    "Latitude": city_location.latitude,
                    "Longitude": city_location.longitude,
                })
                print(f"  -> (city fallback) {city_location.latitude:.4f}, {city_location.longitude:.4f}")
            else:
                print("  -> Could not geocode, skipping.")

    result_df = pd.DataFrame(results)
    result_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nDone! Saved {len(result_df)} geocoded areas to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
