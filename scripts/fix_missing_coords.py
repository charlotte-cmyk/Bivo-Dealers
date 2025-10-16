import xml.etree.ElementTree as ET
import requests
import time

# --- CONFIGURATION ---
INPUT_KML = "all_dealers.kml"
OUTPUT_KML = "all_dealers_fixed.kml"
USER_AGENT = "kml-fixer/1.0 (your_email@example.com)"  # Replace with your contact per Nominatim policy
SLEEP_BETWEEN_REQUESTS = 1  # seconds, required by Nominatim usage policy

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

# --- COORDINATE VALIDATOR/FIXER ---
def fix_coordinate_order(coord_text):
    """Return correctly ordered (lon,lat,alt) string or None if invalid."""
    if not coord_text:
        return None
    parts = coord_text.strip().split(",")
    if len(parts) < 2:
        return None
    lon, lat = parts[0].strip(), parts[1].strip()
    try:
        lon_f, lat_f = float(lon), float(lat)
    except ValueError:
        return None

    # Detect reversed order (lat first)
    if abs(lat_f) > 0 and abs(lon_f) > 0 and (abs(lat_f) > 65 or abs(lon_f) < 50):
        # Example: 47.6,-122.3  => swap
        lon_f, lat_f = lat_f, lon_f
    return f"{lon_f},{lat_f},0"

# --- MAIN PROCESS ---
def main():
    print(f"🔍 Loading {INPUT_KML} ...")
    tree = ET.parse(INPUT_KML)
    root = tree.getroot()
    total_fixed = 0
    total_geocoded = 0

    for placemark in root.findall(".//kml:Placemark", ns):
        name_elem = placemark.find("kml:name", ns)
        name = name_elem.text.strip() if name_elem is not None else "(Unnamed)"
        coord_elem = placemark.find(".//kml:coordinates", ns)

        # --- Case 1: Fix reversed coordinates ---
        if coord_elem is not None and coord_elem.text.strip():
            fixed = fix_coordinate_order(coord_elem.text)
            if fixed and fixed != coord_elem.text.strip():
                coord_elem.text = fixed
                print(f"🔁 Fixed coordinate order for '{name}'")
                total_fixed += 1
            continue

        # --- Case 2: Missing coordinates: try to build address ---
        addr_elem = placemark.find("kml:address", ns)
        address = addr_elem.text.strip() if addr_elem is not None and addr_elem.text else ""

        if not address:
            addr_parts = []
            for key in ["Address", "Address 2", "City", "State", "Country", "Zip", "Zip Code"]:
                val_elem = placemark.find(f".//kml:Data[@name='{key}']/kml:value", ns)
                if val_elem is not None and val_elem.text and val_elem.text.strip():
                    addr_parts.append(val_elem.text.strip())
            address = ", ".join(addr_parts)

        if not address:
            print(f"⚠️ Skipping '{name}' — no address to geocode.")
            continue

        # --- Geocode missing coordinate ---
        lon, lat = nominatim_geocode(address)
        if lon is not None and lat is not None:
            point_elem = placemark.find("kml:Point", ns)
            if point_elem is None:
                point_elem = ET.SubElement(placemark, "{http://www.opengis.net/kml/2.2}Point")
            coord_elem = placemark.find(".//kml:coordinates", ns)
            if coord_elem is None:
                coord_elem = ET.SubElement(point_elem, "{http://www.opengis.net/kml/2.2}coordinates")
            coord_elem.text = f"{lon},{lat},0"
            print(f"✅ Added coordinates for '{name}' ({address})")
            total_geocoded += 1
            time.sleep(SLEEP_BETWEEN_REQUESTS)
        else:
            print(f"⚠️ Could not geocode '{name}' ({address})")

    ET.register_namespace('', "http://www.opengis.net/kml/2.2")
    tree.write(OUTPUT_KML, encoding="utf-8", xml_declaration=True)
    print("\n🎉 Done!")
    print(f"  ↳ {total_fixed} coordinates fixed")
    print(f"  ↳ {total_geocoded} placemarks geocoded")
    print(f"  ↳ Output file: {OUTPUT_KML}")

if __name__ == "__main__":
    main()
