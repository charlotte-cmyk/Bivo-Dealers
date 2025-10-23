import xml.etree.ElementTree as ET
import requests
import time
from xml.dom import minidom

# --- CONFIGURATION ---
INPUT_KML = "all_dealers_fixed3.kml"
OUTPUT_KML = "all_dealers_fixed_selective3.kml"
USER_AGENT = "kml-fixer/1.0 (andrew@drinkbivo.com)"
SLEEP_BETWEEN_REQUESTS = 1

# --- FLIP TARGETS ---
# Define bounding boxes (min_lat, max_lat, min_lon, max_lon)
# Any coordinate falling inside one of these boxes will have its lat/lon flipped.
# Example: (30, 50, -130, -60) means within the continental US roughly
FLIP_RANGES = [
    (-15, 15, 30, 60),
]

# --- NAMESPACE ---
ns = {'kml': 'http://www.opengis.net/kml/2.2'}

# --- GEOCODING FUNCTION ---
def nominatim_geocode(address):
    """Lookup coordinates for an address using OpenStreetMap Nominatim."""
    if not address.strip():
        return None, None
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    try:
        resp = requests.get(url, params=params, headers={'User-Agent': USER_AGENT}, timeout=10)
        data = resp.json()
        if data:
            lon = float(data[0]["lon"])
            lat = float(data[0]["lat"])
            return lon, lat
    except Exception as e:
        print(f"⚠️ Error geocoding '{address}': {e}")
    return None, None

# --- HELPER FUNCTIONS ---
def should_flip(lon, lat):
    """Check if this coordinate falls inside one of the defined flip ranges."""
    for (min_lat, max_lat, min_lon, max_lon) in FLIP_RANGES:
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            return True
    return False

def flip_coordinate_order(coord_text):
    """Flip lon/lat order if inside defined range."""
    if not coord_text:
        return None
    parts = coord_text.strip().split(",")
    if len(parts) < 2:
        return None
    try:
        lon_f, lat_f = float(parts[0]), float(parts[1])
    except ValueError:
        return None

    # Only flip if in specified region
    if should_flip(lon_f, lat_f):
        return f"{lat_f},{lon_f},0"
    return f"{lon_f},{lat_f},0"

# --- MAIN PROCESS ---
def main():
    print(f"Loading {INPUT_KML} ...")
    ET.register_namespace('', "http://www.opengis.net/kml/2.2")
    tree = ET.parse(INPUT_KML)
    root = tree.getroot()
    total_flipped = 0

    for placemark in root.findall(".//kml:Placemark", ns):
        name_elem = placemark.find("kml:name", ns)
        name = name_elem.text.strip() if name_elem is not None else "(Unnamed)"
        coord_elem = placemark.find(".//kml:coordinates", ns)

        if coord_elem is not None and coord_elem.text.strip():
            parts = coord_elem.text.strip().split(",")
            if len(parts) >= 2:
                try:
                    lon, lat = float(parts[0]), float(parts[1])
                except ValueError:
                    continue
                if should_flip(lon, lat):
                    flipped = flip_coordinate_order(coord_elem.text)
                    coord_elem.text = flipped
                    print(f"🔁 Flipped coordinates for '{name}' ({lon},{lat}) → {flipped}")
                    total_flipped += 1

    # --- Write KML Output ---
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    with open(OUTPUT_KML, "w", encoding="utf-8") as f:
        f.write(reparsed.toprettyxml(indent="  "))

    print("Done!")
    print(f"  ↳ {total_flipped} coordinates flipped")
    print(f"  ↳ Output file: {OUTPUT_KML}")

if __name__ == "__main__":
    main()
