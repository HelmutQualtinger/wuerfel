"""Würfel 60 mm, Kanten R2, Durchgangsbohrungen Ø10 (X/Y/Z), auf allen sechs Seiten
eine gleiche Stufenbohrung Ø20/30/40/50.

Die Stufen sind so tief, dass sich die Bohrungen benachbarter Seiten durchdringen:
Jede Stufe bricht die Kanten der darunter liegenden Ebene auf. So entstehen
ineinander geschachtelte Würfelrahmen, die über Stege auf den Raumdiagonalen
(an den Ecken) miteinander verbunden sind.

Halbe Kantenlänge des Würfels k:  a_k = r_k + STEG   (r_k = Radius der Bohrung durch Würfel k)
Steg (Rahmenstärke) und Spalt zwischen den Rahmen: je 2,5 mm (Radiensprung 5 mm).
Alle inneren Kanten gerundet R1.
Einheiten: mm.
"""
from build123d import *

A = 60.0           # Kantenlänge
R_KANTE = 2.0      # Kantenradius außen
R_INNEN = 1.0      # Kantenradius aller inneren Kanten (Stege 2,5 mm -> max. ~1,2)
D_DURCH = 10.0     # Durchgangsbohrungen

# Stufenbohrung je Seite: (Durchmesser, Tiefe); Boden jeder Stufe = Fläche des nächsten Würfels
STEG = 2.5
SACKLOECHER = [(d, A / 2 - (d / 2 - 5 + STEG)) for d in (20.0, 30.0, 40.0, 50.0)]
# -> Ø20 T22,5 · Ø30 T17,5 · Ø40 T12,5 · Ø50 T7,5

ROT = {"X": (0, 90, 0), "Y": (90, 0, 0), "Z": (0, 0, 0)}


def build() -> Part:
    with BuildPart() as p:
        Box(A, A, A)
        fillet(p.edges(), R_KANTE)
        for ax in "XYZ":
            Cylinder(D_DURCH / 2, A + 2, rotation=ROT[ax], mode=Mode.SUBTRACT)
            for s in (+1, -1):
                for d, t in SACKLOECHER:
                    laenge = t + 1                       # 1 mm Überstand außen
                    mitte = s * (A / 2 - t + laenge / 2)
                    pos = {"X": (mitte, 0, 0), "Y": (0, mitte, 0), "Z": (0, 0, mitte)}[ax]
                    with Locations(Pos(*pos)):
                        Cylinder(d / 2, laenge, rotation=ROT[ax], mode=Mode.SUBTRACT)
    part = p.part
    return part.fillet(R_INNEN, [e for e in part.edges() if _scharf(part, e)])


def _scharf(part: Part, e: Edge) -> bool:
    """Kante ist nicht tangential (z. B. keine Übergangskante der R2-Rundung)."""
    fs = [f for f in part.faces() if any(e.is_same(x) for x in f.edges())]
    if len(fs) != 2:
        return True
    m = e @ 0.5
    return fs[0].normal_at(m).dot(fs[1].normal_at(m)) < 0.99


if __name__ == "__main__":
    part = build()
    print("Volumen mm³:", round(part.volume, 1), "valid:", part.is_valid,
          "Körper:", len(part.solids()))
    bb = part.bounding_box()
    print("BBox:", bb.min, bb.max)
