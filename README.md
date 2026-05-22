# Korrelator 3000

Korrelator 3000 ist ein experimentelles Web-Dashboard fuer ueberraschende Korrelationen zwischen Deutschland-Datensaetzen. Der aktuelle MVP zeigt eine Leaflet-Karte mit deutschen Kreis-Geometrien, macht fuenf Kennzahl-Kandidaten aus den GitHub-Issues auswaehlbar und dokumentiert die oeffentlichen Datenquellen direkt im UI.

Die Kartenwerte kommen inzwischen aus echten oeffentlichen Datenquellen. Einige Werte sind wegen der aktuellen GADM-Kreisgeometrie ohne amtliche Kreisschluessel per Namensnaeherung gemappt; fehlende Werte erscheinen im UI als `nicht gemappt`.

## Aktueller MVP

- Leaflet-Karte unter `docs/`, GitHub-Pages-faehig
- Kreis-GeoJSON unter `docs/data/kreise.geojson`
- auswaehlbare Kennzahlen:
  - #2 Kneipendichte
  - #4 Durchschnittseinkommen pro Kopf
  - #6 AfD Bundestagswahl 2025
  - #8 SPD Bundestagswahl 2025
  - #14 Schwimmbaeder pro 100.000 Einwohner
- Quellencheck im UI
- Korrelator-Score aus zwei min-max-normalisierten Kennzahlen
- `Kein Vergleich`-Modus fuer reine Verteilungsansicht einer einzelnen Kennzahl
- Hover- und Klick-Tooltips pro Kreis
- robuste Fehlermeldung, falls JSON-Dateien nicht geladen werden
- echte Wertedatei `docs/data/real_metrics.json`

## Korrelator-Score

Der Score ist bewusst naiv:

```text
norm1 = (wert1 - min1) / (max1 - min1)
norm2 = (wert2 - min2) / (max2 - min2)
score = norm1 * norm2 * 100
```

Wenn beide Kennzahlen in einem Kreis am oberen Ende liegen, landet der Kreis bei 100 Prozent. Das ist keine statistische Korrelation und keine Kausalitaetsaussage, sondern eine spielerische Gleichzeitigkeitsskala. Der automatisch erzeugte Begruendungstext ist absichtlich humoristisch und ausdruecklich Quatsch.

## Datenquellen-Check

- Bundestagswahl 2025: Die Bundeswahlleiterin bietet Open Data im CSV-Format an. Wahlkreiswerte sind direkt importiert; Kreis- oder Gemeindeergebnisse werden dort nicht bereitgestellt, daher ist die Kartenzuordnung eine Namensnaeherung.
- Einkommen: Statistikportal/VGR der Laender liefert verfuegbares Einkommen je Einwohner 2023 sowie Einwohnerzahlen auf Kreisebene.
- Kneipen und Schwimmbaeder: OpenStreetMap/Overpass-Nodes wurden gezaehlt und mit Einwohnerzahlen auf Werte pro 100.000 Einwohner umgerechnet. OSM-Polygone sind im MVP noch nicht enthalten.

Details stehen in `IDEAS.md` und maschinenlesbar in `docs/data/metrics.json`.
Die importierten Werte stehen in `docs/data/real_metrics.json`. Der Importer liegt in `scripts/build_real_metrics.py`; Overpass-Rohdaten werden mit `scripts/overpass_fetch.py` erzeugt.

## Lokal starten

Am zuverlaessigsten laeuft die Karte ueber einen lokalen Webserver:

```powershell
cd "C:\Users\rockw\Documents\Korrelator 3000 - Projekt\docs"
python -m http.server 8765 --bind 127.0.0.1
```

Danach im Browser oeffnen:

```text
http://127.0.0.1:8765
```

Ein Doppelklick auf `docs/index.html` kann wegen Browser-Sicherheitsregeln beim Laden von `docs/data/kreise.geojson` oder `docs/data/metrics.json` scheitern.

## Projektstruktur

```text
korrelator-3000/
|- docs/
|  |- index.html
|  |- styles.css
|  |- app.js
|  `- data/
|     |- kreise.geojson
|     |- metrics.json
|     `- real_metrics.json
|- IDEAS.md
|- AGENTS.md
|- CODEX_BRIEFING.md
|- CODEX_TASKS.md
|- CODEX_PROMPT.txt
`- README.md
```

## Naechste Schritte

1. GADM-Kreisgeometrie durch BKG/VG250 oder eine andere Kreisdatei mit amtlichem Kreisschluessel ersetzen.
2. Wahlwerte entweder als eigene Wahlkreis-Karte anzeigen oder mit einer echten Wahlkreis-zu-Kreis-Bruecke mappen.
3. OSM-Importer um Ways/Relations erweitern, damit polygonal gemappte Schwimmbaeder und Kneipen mitgezaehlt werden.
