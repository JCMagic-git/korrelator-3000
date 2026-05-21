# Korrelator 3000 - gepruefte Kennzahl-Kandidaten

Stand: 2026-05-21

## Score-Idee
Der Korrelator-Score kombiniert zwei ausgewaehlte Kennzahlen nach Min-Max-Normierung:

```text
norm1 = (wert1 - min1) / (max1 - min1)
norm2 = (wert2 - min2) / (max2 - min2)
score = norm1 * norm2 * 100
```

Das Ergebnis ist eine spielerische Gleichzeitigkeitsskala. 100 Prozent bedeutet: beide Werte liegen am Maximum ihrer jeweiligen Kennzahl. Der Score ist keine echte statistische Korrelation, und die automatisch generierten Begruendungstexte sind absichtlich naiv bis falsch.

## #2 Kneipendichte
- Status: oeffentlich greifbar, Import noch zu bauen
- Quelle: OpenStreetMap ueber Overpass API
- Ebene: einzelne OSM-Objekte, danach Aggregation auf Kreisgrenzen
- Ansatz: `amenity=pub`, `amenity=bar` und optional `amenity=biergarten` zaehlen; durch Einwohnerzahl teilen.
- Risiko: OSM-Vollstaendigkeit variiert regional.

## #4 Durchschnittseinkommen pro Kopf
- Status: direkt importierbar
- Quelle: Statistikportal, Einkommen der privaten Haushalte auf Kreisebene
- Ebene: Kreise und kreisfreie Staedte
- Ansatz: Excel-Datei aus Statistikportal nach CSV/JSON konvertieren; Kreiskennziffern mit GeoJSON mappen.

## #6 AfD Wahlergebnis Bundestagswahl 2025
- Status: direkt importierbar auf Wahlkreisebene, fuer die Kreis-Karte nur mit Naeherung oder Zusatzquelle
- Quelle: Bundeswahlleiterin Open Data
- Ebene: Bund, Laender und Wahlkreise in `kerg2.csv`; keine Kreis- oder Gemeindeergebnisse bei der Bundeswahlleiterin
- Ansatz: fuer MVP Wahlkreiswerte dokumentieren; spaeter Wahlkreis-zu-Kreis-Naeherung oder Landes-/Kommunalquellen pruefen.

## #8 SPD Wahlergebnis Bundestagswahl 2025
- Status: direkt importierbar auf Wahlkreisebene, fuer die Kreis-Karte nur mit Naeherung oder Zusatzquelle
- Quelle: Bundeswahlleiterin Open Data
- Ebene: Bund, Laender und Wahlkreise in `kerg2.csv`; keine Kreis- oder Gemeindeergebnisse bei der Bundeswahlleiterin
- Ansatz: gleicher Importpfad wie AfD, Partei ueber Parteien-Metadaten mappen.

## #14 Schwimmbaeder pro 100.000 Einwohner
- Status: oeffentlich greifbar, Import noch zu bauen
- Quelle: OpenStreetMap ueber Overpass API
- Ebene: einzelne OSM-Objekte, danach Aggregation auf Kreisgrenzen
- Ansatz: `leisure=swimming_pool`, `amenity=swimming_pool`, `sport=swimming` und ggf. `sport=aquatics` zaehlen; durch Einwohnerzahl teilen.
- Risiko: OSM-Tags sind nicht perfekt einheitlich, deshalb Importregeln dokumentieren.
