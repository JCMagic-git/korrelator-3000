# Korrelator 3000

Korrelator 3000 ist ein experimentelles Web-Dashboard fuer ueberraschende Korrelationen zwischen Deutschland-Datensaetzen. Der aktuelle MVP zeigt eine Leaflet-Karte mit deutschen Kreis-Geometrien, macht fuenf Kennzahl-Kandidaten aus den GitHub-Issues auswaehlbar und dokumentiert die oeffentlichen Datenquellen direkt im UI.

Die Kartenwerte sind aktuell deterministische MVP-Platzhalter. Sie sind keine echten statistischen Aussagen. Die Quellen sind aber bereits geprueft und in `docs/data/metrics.json` hinterlegt.

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
- Hover- und Klick-Tooltips pro Kreis
- robuste Fehlermeldung, falls JSON-Dateien nicht geladen werden

## Datenquellen-Check

- Bundestagswahl 2025: Die Bundeswahlleiterin bietet Open Data im CSV-Format an. Wahlkreiswerte sind direkt verfuegbar; Kreis- oder Gemeindeergebnisse werden dort nicht bereitgestellt.
- Einkommen: Statistikportal/VGR der Laender bietet Einkommen der privaten Haushalte fuer Kreise und kreisfreie Staedte als Excel-Datei an.
- Kneipen und Schwimmbaeder: OpenStreetMap/Overpass ist oeffentlich nutzbar; hier braucht der Import Zaehllogik plus Aggregation auf Kreisgrenzen.

Details stehen in `IDEAS.md` und maschinenlesbar in `docs/data/metrics.json`.

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
|     `- metrics.json
|- IDEAS.md
|- AGENTS.md
|- CODEX_BRIEFING.md
|- CODEX_TASKS.md
|- CODEX_PROMPT.txt
`- README.md
```

## Naechste Schritte

1. Einkommens-Excel vom Statistikportal in `data/processed/` als JSON fuer Kreise konvertieren.
2. Bundeswahlleiterin-CSV fuer AfD/SPD importieren und entscheiden: Wahlkreise separat anzeigen, auf Kreise naehern oder bessere Landes-/Kommunalquellen nutzen.
3. Overpass-Importer fuer Kneipen und Schwimmbaeder bauen.
4. Platzhalterwerte in `docs/app.js` durch echte Werte aus `docs/data/processed_metrics.json` ersetzen.
