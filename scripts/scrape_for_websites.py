"""
Free version — find websites for business names from a GeoJSON file (no API key required)
Uses DuckDuckGo via ddgs library (no HTML scraping)

Input:  dealers.geojson (FeatureCollection with properties.name)
Output: results.csv (name, domain, url, title, confidence)
"""

import json
import csv
import time
import random
import re
from urllib.parse import urlparse
from ddgs import DDGS

INPUT_GEOJSON = "geojson/all_dealers_without_websites.geojson"
OUTPUT_CSV = "website_scrape/results.csv"

SEARCH_QUERIES = [
    " bike shop website",
    " bike shop site",
    " website bike shop",
    " bike shops website",
    " bike shops site",
    " website bikes shop",
    " online",
    " contact website",
    " website email"
]

BLOCKED_DOMAINS = [
    "yelp.",
    "facebook.",
    "tripadvisor.",
    "maps.google.",
    "yellowpages."
]

# --- helper functions ---

def domain_from_url(url):
    """Extract domain from full URL."""
    try:
        p = urlparse(url)
        domain = p.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def name_token_confidence(business_name, candidate_title, candidate_domain):
    """Token overlap confidence score."""
    tokens = re.findall(r"[a-z0-9]+", business_name.lower())
    if not tokens:
        return 0.0

    haystack = f"{candidate_title or ''} {candidate_domain or ''}".lower()
    found = sum(1 for t in tokens if t in haystack)
    return round(found / len(tokens), 2)


def is_blocked_domain(domain):
    return any(b in domain for b in BLOCKED_DOMAINS)


def find_website_for_business(name, max_results=8):
    """Search for a business website using ddgs."""
    query = name + random.choice(SEARCH_QUERIES)

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                max_results=max_results,
                safesearch="moderate"
            ))

        best_candidate = None

        for r in results:
            url = r.get("href", "")
            title = r.get("title", "")
            domain = domain_from_url(url)

            if not domain or is_blocked_domain(domain):
                continue

            confidence = name_token_confidence(name, title, domain)

            candidate = {
                "domain": domain,
                "url": url,
                "title": title,
                "confidence": confidence
            }

            # prefer strong matches
            if confidence >= 0.4:
                return candidate

            # otherwise track best fallback
            if not best_candidate or confidence > best_candidate["confidence"]:
                best_candidate = candidate

        if best_candidate:
            return best_candidate

    except Exception as e:
        print(f"Error searching for {name}: {e}")

    return {"domain": "", "url": "", "title": "", "confidence": 0.0}


# --- main pipeline ---

def main():
    with open(INPUT_GEOJSON, encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    names = [
        feat["properties"].get("name", "").strip()
        for feat in features
        if feat.get("properties") and feat["properties"].get("name")
    ]

    print(f"Found {len(names)} business names in {INPUT_GEOJSON}")

    results = []
    delay = 4  # ddgs is lighter than HTML scraping

    for i, name in enumerate(names, start=1):
        print(f"[{i}/{len(names)}] Searching: {name}")
        site = find_website_for_business(name)

        results.append({
            "name": name,
            "domain": site["domain"],
            "url": site["url"],
            "title": site["title"],
            "confidence": site["confidence"]
        })

        time.sleep(delay + random.random() * 2)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["name", "domain", "url", "title", "confidence"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
