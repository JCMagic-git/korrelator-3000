import csv
import json
import math
import re
import unicodedata
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DOCS_DATA = ROOT / "docs" / "data"
OUT = DOCS_DATA / "real_metrics.json"
METRICS = DOCS_DATA / "metrics.json"
GEOJSON = DOCS_DATA / "kreise.geojson"

XLSX_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
STATE_NAMES = {
    "BW": "baden-wuerttemberg",
    "BY": "bayern",
    "BE": "berlin",
    "BB": "brandenburg",
    "HB": "bremen",
    "HH": "hamburg",
    "HE": "hessen",
    "MV": "mecklenburg-vorpommern",
    "NI": "niedersachsen",
    "NW": "nordrhein-westfalen",
    "RP": "rheinland-pfalz",
    "SL": "saarland",
    "SN": "sachsen",
    "ST": "sachsen-anhalt",
    "SH": "schleswig-holstein",
    "TH": "thueringen",
}
STATE_CODES = {
    "01": "schleswig-holstein",
    "02": "hamburg",
    "03": "niedersachsen",
    "04": "bremen",
    "05": "nordrhein-westfalen",
    "06": "hessen",
    "07": "rheinland-pfalz",
    "08": "baden-wuerttemberg",
    "09": "bayern",
    "10": "saarland",
    "11": "berlin",
    "12": "brandenburg",
    "13": "mecklenburg-vorpommern",
    "14": "sachsen",
    "15": "sachsen-anhalt",
    "16": "thueringen",
}
STATE_BY_NAME = {
    "Baden-Württemberg": "baden-wuerttemberg",
    "Bayern": "bayern",
    "Berlin": "berlin",
    "Brandenburg": "brandenburg",
    "Bremen": "bremen",
    "Hamburg": "hamburg",
    "Hessen": "hessen",
    "Mecklenburg-Vorpommern": "mecklenburg-vorpommern",
    "Niedersachsen": "niedersachsen",
    "Nordrhein-Westfalen": "nordrhein-westfalen",
    "Rheinland-Pfalz": "rheinland-pfalz",
    "Saarland": "saarland",
    "Sachsen": "sachsen",
    "Sachsen-Anhalt": "sachsen-anhalt",
    "Schleswig-Holstein": "schleswig-holstein",
    "Thüringen": "thueringen",
}


def normalize(value):
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.casefold()
    value = value.replace("ß", "ss")
    value = value.replace("kreisfreie stadte", "")
    value = value.replace("kreisfreie stadt", "")
    value = value.replace("stadtkreis", "")
    value = value.replace("landeshauptstadt", "")
    value = value.replace("landkreis", "")
    value = value.replace("kreis", "")
    value = value.replace("staedte", "")
    value = value.replace("stadte", "")
    value = value.replace("stadt", "")
    value = re.sub(r"\([^)]*\)", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def type_bucket(text):
    text = normalize(text)
    if "urban district" in text or "kreisfreie" in text or "stadte" in text:
        return "urban"
    if "rural district" in text or "landkreis" in text:
        return "rural"
    return "any"


def col_index(cell_ref):
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    index = 0
    for char in letters:
        index = index * 26 + ord(char.upper()) - ord("A") + 1
    return index - 1


def read_shared_strings(zip_file):
    root = ET.fromstring(zip_file.read("xl/sharedStrings.xml"))
    values = []
    for item in root.findall("m:si", XLSX_NS):
        values.append(
            "".join(
                text.text or ""
                for text in item.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
            )
        )
    return values


def sheet_rows(zip_file, sheet_path, shared_strings):
    root = ET.fromstring(zip_file.read(sheet_path))
    for row in root.findall(".//m:row", XLSX_NS):
        values = {}
        for cell in row.findall("m:c", XLSX_NS):
            value = cell.find("m:v", XLSX_NS)
            if value is None:
                continue
            text = value.text or ""
            if cell.attrib.get("t") == "s":
                text = shared_strings[int(text)]
            values[col_index(cell.attrib["r"])] = text
        if values:
            max_col = max(values)
            yield [values.get(i, "") for i in range(max_col + 1)]


def read_income_and_population():
    workbook = RAW / "vgrdl_r2b3_bs2024.xlsx"
    with zipfile.ZipFile(workbook) as zip_file:
        shared_strings = read_shared_strings(zip_file)

        def table(sheet_name):
            rows = list(sheet_rows(zip_file, f"xl/worksheets/{sheet_name}", shared_strings))
            header_row = next(
                index
                for index, row in enumerate(rows)
                if "Gebietseinheit" in row and "2023" in row
            )
            headers = rows[header_row]
            year_index = headers.index("2023")
            records = {}
            for row in rows[header_row + 1 :]:
                nuts_level = next((row[i] for i in (4, 5, 6) if len(row) > i and row[i]), "")
                if len(row) <= year_index or nuts_level != "3":
                    continue
                key = row[2]
                records[key] = {
                    "state": STATE_NAMES.get(row[3], normalize(row[3])),
                    "name": row[7],
                    "name_norm": normalize(row[7]),
                    "type": type_bucket(row[7]),
                    "value": float(row[year_index]),
                }
            return records

        income = table("sheet18.xml")
        population = table("sheet19.xml")

    combined = {}
    for key, record in income.items():
        if key not in population:
            continue
        combined[key] = {
            "state": record["state"],
            "name": record["name"],
            "name_norm": record["name_norm"],
            "type": record["type"],
            "einkommen": round(record["value"]),
            "population": round(population[key]["value"] * 1000),
        }
    return combined


def polygon_rings(geometry):
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiPolygon":
        return geometry["coordinates"]
    return []


def ring_contains(point, ring):
    x, y = point
    inside = False
    j = len(ring) - 1
    for i, current in enumerate(ring):
        xi, yi = current[:2]
        xj, yj = ring[j][:2]
        if ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
        ):
            inside = not inside
        j = i
    return inside


def polygon_contains(point, polygon):
    if not polygon or not ring_contains(point, polygon[0]):
        return False
    return not any(ring_contains(point, hole) for hole in polygon[1:])


def feature_contains(feature, point):
    for polygon in polygon_rings(feature["geometry"]):
        if polygon_contains(point, polygon):
            return True
    return False


def bbox_for(feature):
    xs = []
    ys = []
    for polygon in polygon_rings(feature["geometry"]):
        for ring in polygon:
            for x, y, *_ in ring:
                xs.append(x)
                ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def point_from_osm(element):
    if "lat" in element and "lon" in element:
        return element["lon"], element["lat"]
    center = element.get("center")
    if center:
        return center["lon"], center["lat"]
    return None


def count_osm_points(features, path):
    data = json.loads(path.read_text(encoding="utf-8"))
    counts = defaultdict(int)
    prepared = [(feature.get("id"), bbox_for(feature), feature) for feature in features]
    for element in data.get("elements", []):
        point = point_from_osm(element)
        if point is None:
            continue
        x, y = point
        for feature_id, bbox, feature in prepared:
            min_x, min_y, max_x, max_y = bbox
            if min_x <= x <= max_x and min_y <= y <= max_y and feature_contains(feature, point):
                counts[str(feature_id)] += 1
                break
    return counts, len(data.get("elements", []))


def read_election():
    path = RAW / "btw25_kerg2.csv"
    party_rows = {"SPD": defaultdict(list), "AfD": defaultdict(list)}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=";")
        for row in reader:
            if len(row) < 14 or row[0] != "BT" or row[2] != "Wahlkreis":
                continue
            party = row[8]
            vote_type = row[10]
            if party not in party_rows or vote_type != "2":
                continue
            state = STATE_CODES.get(row[6], "")
            district = normalize(row[4])
            try:
                share = float(row[12].replace(",", "."))
            except ValueError:
                continue
            party_rows[party][state].append((district, share))
    return party_rows


def election_for_feature(feature, election, party):
    props = feature["properties"]
    state = STATE_BY_NAME.get(props.get("NAME_1", ""), normalize(props.get("NAME_1", "")))
    name = normalize(props.get("NAME_3", ""))
    if not name:
        return None
    matches = []
    for district, share in election[party].get(state, []):
        tokens = [token for token in name.split() if len(token) >= 4]
        if name in district or any(token in district for token in tokens):
            matches.append(share)
    if not matches:
        return None
    return round(sum(matches) / len(matches), 1)


def find_income_record(feature, income_records):
    props = feature["properties"]
    state = STATE_BY_NAME.get(props.get("NAME_1", ""), normalize(props.get("NAME_1", "")))
    name = normalize(props.get("NAME_3", ""))
    bucket = type_bucket(props.get("ENGTYPE_3", "") + " " + props.get("TYPE_3", ""))
    candidates = [
        record
        for record in income_records.values()
        if record["state"] == state and record["name_norm"] == name
    ]
    typed = [record for record in candidates if record["type"] == bucket]
    if typed:
        return typed[0]
    if candidates:
        return candidates[0]

    # Some GADM labels append "Staedte"; for ambiguous cases keep the state/type guard.
    for record in income_records.values():
        if record["state"] != state or record["type"] not in (bucket, "any"):
            continue
        if record["name_norm"] in name or name in record["name_norm"]:
            return record
    return None


def ranges(values_by_feature):
    result = {}
    for metric_id in [
        "kneipendichte",
        "einkommen",
        "afd_btw2025",
        "spd_btw2025",
        "schwimmbaeder",
    ]:
        values = [
            metrics[metric_id]
            for metrics in values_by_feature.values()
            if metrics.get(metric_id) is not None
        ]
        if values:
            result[metric_id] = [min(values), max(values)]
    return result


def main():
    geojson = json.loads(GEOJSON.read_text(encoding="utf-8"))
    features = geojson["features"]
    income = read_income_and_population()
    election = read_election()
    kneipen_counts, kneipen_total = count_osm_points(features, RAW / "osm_kneipen.json")
    schwimm_counts, schwimm_total = count_osm_points(features, RAW / "osm_schwimmbaeder.json")

    values_by_feature = {}
    coverage = defaultdict(int)
    for feature in features:
        feature_id = str(feature.get("id"))
        income_record = find_income_record(feature, income)
        population = income_record["population"] if income_record else None
        kneipen = kneipen_counts.get(feature_id, 0)
        schwimm = schwimm_counts.get(feature_id, 0)
        values = {
            "einkommen": income_record["einkommen"] if income_record else None,
            "population": population,
            "kneipen_count": kneipen,
            "schwimmbaeder_count": schwimm,
            "kneipendichte": round(kneipen / population * 100000, 1) if population else None,
            "schwimmbaeder": round(schwimm / population * 100000, 1) if population else None,
            "afd_btw2025": election_for_feature(feature, election, "AfD"),
            "spd_btw2025": election_for_feature(feature, election, "SPD"),
        }
        for key, value in values.items():
            if value is not None:
                coverage[key] += 1
        values_by_feature[feature_id] = values

    metric_ranges = ranges(values_by_feature)
    output = {
        "generated_at": "2026-05-21",
        "sources": {
            "einkommen": "Statistikportal/VGRdL Reihe 2 Band 3, Berechnungsstand Februar 2025, Jahr 2023",
            "population": "Statistikportal/VGRdL Reihe 2 Band 3, Einwohnerinnen und Einwohner, Jahr 2023",
            "wahl": "Bundeswahlleiterin kerg2.csv, Bundestagswahl 2025, Zweitstimmenanteile; auf GADM-Kreise per Namensnaeherung gemappt",
            "osm": "OpenStreetMap Overpass, Nodes in Deutschland-Bounding-Box, abgerufen am 2026-05-21",
        },
        "notes": [
            "Die vorhandene GADM-Kreisdatei enthaelt keine amtlichen Kreisschluessel. Deshalb werden Einkommen/Einwohner per Name+Bundesland+Kreistyp gemappt.",
            "Bundestagswahlwerte liegen offiziell auf Wahlkreisebene vor und werden hier als Namensnaeherung an Kreise gehaengt.",
            "OSM-Werte zaehlen Nodes fuer Kneipen/Bars/Biergaerten bzw. Schwimmbaeder; OSM-Polygone sind im MVP noch nicht enthalten.",
        ],
        "coverage": dict(coverage),
        "raw_counts": {
            "osm_kneipen_elements": kneipen_total,
            "osm_schwimmbaeder_elements": schwimm_total,
        },
        "ranges": metric_ranges,
        "values": values_by_feature,
    }
    OUT.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    for metric in metrics:
        if metric["id"] in metric_ranges:
            metric["range"] = metric_ranges[metric["id"]]
            metric["dataStatus"] = "real"
    METRICS.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"coverage": dict(coverage), "ranges": metric_ranges}, indent=2))


if __name__ == "__main__":
    main()
