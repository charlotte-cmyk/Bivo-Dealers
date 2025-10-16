import xml.etree.ElementTree as ET

def find_placemarks_without_points(kml_path):
    # Parse the XML with namespace handling
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    tree = ET.parse(kml_path)
    root = tree.getroot()

    missing = []

    # Iterate through all Placemark elements
    for placemark in root.findall('.//kml:Placemark', ns):
        name_elem = placemark.find('kml:name', ns)
        name = name_elem.text.strip() if name_elem is not None else "(Unnamed placemark)"

        # Look for Point/coordinates tags
        point_elem = placemark.find('kml:Point', ns)
        coords_elem = placemark.find('.//kml:coordinates', ns)

        if point_elem is None or coords_elem is None or not coords_elem.text.strip():
            missing.append(name)

    return missing


if __name__ == "__main__":
    kml_file = r'all_dealers_fixed.kml'   # path to your KML file
    missing_points = find_placemarks_without_points(kml_file)

    if missing_points:
        print("Placemark(s) missing coordinates:\n")
        for name in missing_points:
            print(" -", name)
    else:
        print("✅ All placemarks have <Point>/<coordinates> data.")
