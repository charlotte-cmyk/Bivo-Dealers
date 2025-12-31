import json
import csv

# -----------------------
# File paths
# -----------------------
GEOJSON_INPUT = "geojson/all_dealers_unique.geojson"
CSV_INPUT = "website_scrape/results.csv"
GEOJSON_OUTPUT = "geojson/all_dealers_unique_with_websites.geojson"

CONFIDENCE_THRESHOLD = 0.3

# -----------------------
# Load CSV into lookup
# -----------------------
website_lookup = {}

with open(CSV_INPUT, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            confidence = float(row.get("confidence", 0))
        except ValueError:
            continue

        if confidence > CONFIDENCE_THRESHOLD:
            name = row["name"].strip()
            website_lookup[name] = row["url"].strip()

# -----------------------
# Load GeoJSON
# -----------------------
with open(GEOJSON_INPUT, encoding="utf-16") as f:
    geojson = json.load(f)

# -----------------------
# Update Website fields
# -----------------------
updated_count = 0

for feature in geojson.get("features", []):
    props = feature.get("properties", {})
    feature_name = props.get("name", "").strip()

    if feature_name in website_lookup:
        props["Website"] = website_lookup[feature_name]
        updated_count += 1

# -----------------------
# Save updated GeoJSON
# -----------------------
with open(GEOJSON_OUTPUT, "w", encoding="utf-16") as f:
    json.dump(
        geojson,
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"Updated {updated_count} features with Website URLs.")
