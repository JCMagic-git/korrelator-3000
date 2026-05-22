import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "kreisgrenzen_2024.geojson"
OUT = ROOT / "docs" / "data" / "kreise.geojson"


def sq_distance(point, start, end):
    px, py = point[:2]
    sx, sy = start[:2]
    ex, ey = end[:2]
    dx = ex - sx
    dy = ey - sy
    if dx == 0 and dy == 0:
        return (px - sx) ** 2 + (py - sy) ** 2
    t = max(0, min(1, ((px - sx) * dx + (py - sy) * dy) / (dx * dx + dy * dy)))
    qx = sx + t * dx
    qy = sy + t * dy
    return (px - qx) ** 2 + (py - qy) ** 2


def simplify_ring(points, tolerance):
    if len(points) <= 4:
        return points
    closed = points[0][:2] == points[-1][:2]
    work = points[:-1] if closed else points
    if len(work) <= 3:
        return points

    keep = {0, len(work) - 1}
    stack = [(0, len(work) - 1)]
    tolerance_sq = tolerance * tolerance

    while stack:
        start, end = stack.pop()
        max_distance = -1
        index = None
        for candidate in range(start + 1, end):
            distance = sq_distance(work[candidate], work[start], work[end])
            if distance > max_distance:
                max_distance = distance
                index = candidate
        if index is not None and max_distance > tolerance_sq:
            keep.add(index)
            stack.append((start, index))
            stack.append((index, end))

    simplified = [work[index] for index in sorted(keep)]
    if closed and simplified[0][:2] != simplified[-1][:2]:
        simplified.append(simplified[0])
    if len(simplified) < 4 and closed:
        return points
    return [[round(point[0], 5), round(point[1], 5)] for point in simplified]


def simplify_geometry(geometry, tolerance=0.0012):
    if geometry["type"] == "Polygon":
        return {
            "type": "Polygon",
            "coordinates": [
                simplify_ring(ring, tolerance) for ring in geometry["coordinates"]
            ],
        }
    if geometry["type"] == "MultiPolygon":
        return {
            "type": "MultiPolygon",
            "coordinates": [
                [simplify_ring(ring, tolerance) for ring in polygon]
                for polygon in geometry["coordinates"]
            ],
        }
    return geometry


def main():
    data = json.loads(RAW.read_text(encoding="utf-8"))
    features = []
    for feature in data["features"]:
        props = feature["properties"]
        ags = props["AGS"]
        features.append(
            {
                "type": "Feature",
                "id": ags,
                "properties": {
                    "AGS": ags,
                    "ARS": props.get("ARS"),
                    "GEN": props.get("GEN"),
                    "BEZ": props.get("BEZ"),
                    "NUTS": props.get("NUTS"),
                    "SN_L": props.get("SN_L"),
                    "SN_R": props.get("SN_R"),
                    "SN_K": props.get("SN_K"),
                    "source": "VG250 Kreisgrenzen 2024, BKG/Esri Deutschland",
                },
                "geometry": simplify_geometry(feature["geometry"]),
            }
        )

    output = {
        "type": "FeatureCollection",
        "name": "VG250 Kreisgrenzen 2024",
        "source": "© BKG 2024 dl-de/by-2-0, via ArcGIS Living Atlas Kreisgrenzen 2024",
        "features": features,
    }
    OUT.write_text(
        json.dumps(output, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(json.dumps({"features": len(features), "bytes": OUT.stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
