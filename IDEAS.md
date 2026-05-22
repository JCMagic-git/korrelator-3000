# Korrelator 3000 - gepruefte Kennzahl-Kandidaten

Stand: 2026-05-22

## Geometrie und Mapping
- Status: umgesetzt
- Quelle: VG250 Kreisgrenzen 2024, BKG/Esri Deutschland, `© BKG 2024 dl-de/by-2-0`
- Ebene: 400 Kreise und kreisfreie Staedte mit `AGS`, `ARS`, `GEN`, `BEZ`, `NUTS`
- Effekt: Einkommen, Einwohner und OSM-Raten werden per AGS bzw. Geometrie vollstaendig fuer 400 Kreise gemappt.
- Restluecke: Bundestagswahlwerte liegen auf Wahlkreisebene vor und bleiben deshalb eine Namensnaeherung.

## Score-Idee
Der Korrelator-Score kombiniert zwei ausgewaehlte Kennzahlen nach Min-Max-Normierung:

```text
norm1 = (wert1 - min1) / (max1 - min1)
norm2 = (wert2 - min2) / (max2 - min2)
score = norm1 * norm2 * 100
```

Das Ergebnis ist eine spielerische Gleichzeitigkeitsskala. 100 Prozent bedeutet: beide Werte liegen am Maximum ihrer jeweiligen Kennzahl. Der Score ist keine echte statistische Korrelation, und die automatisch generierten Begruendungstexte sind absichtlich naiv bis falsch.

## #2 Kneipendichte
- Status: importiert als echte OSM-Node-Zaehlung
- Quelle: OpenStreetMap ueber Overpass API
- Ebene: einzelne OSM-Objekte, danach Aggregation auf Kreisgrenzen
- Ansatz: `amenity=pub`, `amenity=bar` und `amenity=biergarten` als Nodes zaehlen; durch Einwohnerzahl 2023 teilen.
- Risiko: OSM-Vollstaendigkeit variiert regional.

## #4 Durchschnittseinkommen pro Kopf
- Status: importiert
- Quelle: Statistikportal, Einkommen der privaten Haushalte auf Kreisebene
- Ebene: Kreise und kreisfreie Staedte
- Ansatz: Excel-Datei aus Statistikportal wird per Importer gelesen; Mapping per AGS.

## #6 AfD Wahlergebnis Bundestagswahl 2025
- Status: importiert als Wahlkreis-Namensnaeherung
- Quelle: Bundeswahlleiterin Open Data
- Ebene: Bund, Laender und Wahlkreise in `kerg2.csv`; keine Kreis- oder Gemeindeergebnisse bei der Bundeswahlleiterin
- Ansatz: fuer MVP Wahlkreiswerte per Namensnaeherung an Kreise haengen; spaeter echte Wahlkreis-zu-Kreis-Bruecke oder Landes-/Kommunalquellen pruefen.

## #8 SPD Wahlergebnis Bundestagswahl 2025
- Status: importiert als Wahlkreis-Namensnaeherung
- Quelle: Bundeswahlleiterin Open Data
- Ebene: Bund, Laender und Wahlkreise in `kerg2.csv`; keine Kreis- oder Gemeindeergebnisse bei der Bundeswahlleiterin
- Ansatz: gleicher Importpfad wie AfD, Partei ueber Parteien-Metadaten mappen.

## #14 Schwimmbaeder pro 100.000 Einwohner
- Status: importiert als echte OSM-Node-Zaehlung
- Quelle: OpenStreetMap ueber Overpass API
- Ebene: einzelne OSM-Objekte, danach Aggregation auf Kreisgrenzen
- Ansatz: `leisure=swimming_pool`, `amenity=swimming_pool`, `sport=swimming` und `sport=aquatics` als Nodes zaehlen; durch Einwohnerzahl 2023 teilen.
- Risiko: OSM-Tags sind nicht perfekt einheitlich, deshalb Importregeln dokumentieren.
