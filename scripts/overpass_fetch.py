import sys
import urllib.parse
import urllib.request
from pathlib import Path


QUERIES = {
    "test": """
[out:json][timeout:25];
area["name"="Deutschland"]["boundary"="administrative"]["admin_level"="2"]->.de;
node(area.de)["amenity"="pub"];
out 1;
""",
    "kneipen": """
[out:json][timeout:180];
(
  node(47.1,5.5,55.2,15.6)["amenity"="pub"];
  node(47.1,5.5,55.2,15.6)["amenity"="bar"];
  node(47.1,5.5,55.2,15.6)["amenity"="biergarten"];
);
out body;
""",
    "schwimmbaeder": """
[out:json][timeout:180];
(
  node(47.1,5.5,55.2,15.6)["leisure"="swimming_pool"];
  node(47.1,5.5,55.2,15.6)["amenity"="swimming_pool"];
  node(47.1,5.5,55.2,15.6)["sport"="swimming"];
  node(47.1,5.5,55.2,15.6)["sport"="aquatics"];
);
out body;
""",
}


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in QUERIES:
        print("Usage: python scripts/overpass_fetch.py {test|kneipen|schwimmbaeder} OUTPUT")
        return 2

    query = QUERIES[sys.argv[1]]
    output = Path(sys.argv[2])
    output.parent.mkdir(parents=True, exist_ok=True)
    body = urllib.parse.urlencode({"data": query}).encode("utf-8")
    request = urllib.request.Request(
        "https://overpass.openstreetmap.fr/api/interpreter",
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Korrelator3000/0.1 (https://github.com/JCMagic-git/korrelator-3000)",
        },
    )

    with urllib.request.urlopen(request, timeout=240) as response:
        output.write_bytes(response.read())

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
