Erzeuge einen Würfel als Volumenmodell (Einheiten mm).

## Geometrie
- Würfel mit Kantenlänge 60 mm, Mittelpunkt im Ursprung.
- Alle äußeren Würfelkanten mit Radius 2 mm abrunden.
- Drei durchgehende Bohrungen Ø10 entlang der X-, Y- und Z-Achse durch die Würfelmitte.
- Auf **allen sechs Seiten identisch** eine zentrisch in der Seitenfläche liegende Stufenbohrung mit flachem Grund. Die Bohrungen liegen auf derselben Achse, und je größer der Durchmesser, desto flacher die Bohrung:
  - Ø50, Tiefe 7,5
  - Ø40, Tiefe 12,5
  - Ø30, Tiefe 17,5
  - Ø20, Tiefe 22,5
- Bei diesen Tiefen durchdringen sich die Bohrungen benachbarter Seiten. So entstehen Durchbrüche: vier ineinander geschachtelte Würfelrahmen (45, 35, 25 und 15 mm) im äußeren Rahmen. Die inneren Rahmenstäbe und die Spalte zwischen den Rahmen sind je 2,5 mm. Alle Rahmen sind an den Ecken über Stege auf den Raumdiagonalen verbunden.
- Danach alle inneren, nicht tangentialen Kanten mit Radius 1 mm abrunden.
- Das Ergebnis muss **ein einziger zusammenhängender, gültiger Körper** sein.

## Ausgabe
1. **STL** `wuerfel.stl`: binär, geschlossen und mannigfaltig, Sehnenabweichung 0,02 mm, Winkeltoleranz 0,25 rad.
2. **3D-Datei mit gebürstetem Gold** `wuerfel_gold.glb`:
   - PBR-Material: baseColor (1.0, 0.766, 0.336), metallic 1.0, roughness 0.35
   - Erweiterung `KHR_materials_anisotropy` mit Stärke 0.7
   - Y-Achse nach oben, Einheit Meter, Vertex-Normalen aus dem Dreiecksnetz
3. **STEP** `wuerfel.step` zur Weiterbearbeitung.
4. **Technische Zeichnung** `wuerfel_zeichnung.pdf` und `.png`:
   - A3 quer, Maßstab 1:1, Projektionsmethode 1, Rahmen und Schriftfeld (Benennung, Maßstab, Einheit, Datum, Oberfläche, Format, Zeichnungsnummer, Projektionssymbol)
   - Vorderansicht mit Schnittverlauf A–A, bemaßt: 60 × 60, „3× Ø10 durchgehend“, „R2 (alle Kanten)“
   - Schnitt A–A (Ebene z = 0, schraffiert): alle vier Durchmesser und Tiefen gestaffelt außerhalb der Kontur bemaßt
   - Isometrie ohne Maßstab
   - Hinweise: zentrische Bohrungen, Stufenbohrung auf allen 6 Seiten gleich, Rundungen R2 außen und R1 innen, ISO 2768-m, Oberfläche Gold gebürstet
   - Keine überlappenden Maße oder Texte
5. **Vorschau** `wuerfel_vorschau.png`: goldfarben schattiert, einmal gesamt und einmal aufgeschnitten.

## Umsetzung
- Python 3 mit build123d in einer lokalen `.venv`. Für die Zeichnung matplotlib mit Hidden-Line-Projektion aus build123d.
- Skripte: `wuerfel.py` (Modell), `export.py` (STL/STEP/GLB), `zeichnung.py` (Zeichnung).
- Prüfen und Ergebnis melden:
  - Körper gültig, genau 1 Solid
  - STL ohne nicht-mannigfaltige Kanten
  - GLB-Dreiecke einheitlich nach außen orientiert
  - Zeichnung visuell kontrolliert
