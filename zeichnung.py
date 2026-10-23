"""Technische Zeichnung A3 quer, Maßstab 1:1, Projektionsmethode 1 (DIN ISO 128 / 5456-2)."""
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Rectangle, Circle
from matplotlib.path import Path
from build123d import Box, Plane, Pos, Mode

from wuerfel import A, SACKLOECHER, D_DURCH, R_KANTE, build

part = build()
W, H = 420, 297
fig = plt.figure(figsize=(W / 25.4, H / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")

LW_VIS, LW_THIN = 0.7, 0.25          # Linienbreiten in pt (0,5 / 0,25 mm Gruppe)
TXT = 10                              # ≈ 3,5 mm Schrifthöhe
FONT = dict(fontsize=TXT, family="DejaVu Sans")


def edge_pts(e, n=None):
    if n is None:
        n = 2 if e.geom_type.name == "LINE" else 64
    return np.array([[p.X, p.Y] for p in (e @ t for t in np.linspace(0, 1, n))])


def draw_view(shape, origin, up, cx, cy, hidden=False):
    vis, hid = shape.project_to_viewport(origin, up, (0, 0, 0))
    for e in vis:
        p = edge_pts(e)
        ax.plot(p[:, 0] + cx, p[:, 1] + cy, "k", lw=LW_VIS, solid_capstyle="round")
    if hidden:
        for e in hid:
            p = edge_pts(e)
            ax.plot(p[:, 0] + cx, p[:, 1] + cy, "k", lw=LW_THIN, ls=(0, (4, 2)))


def centerline(x0, y0, x1, y1):
    ax.plot([x0, x1], [y0, y1], "k", lw=LW_THIN, ls=(0, (12, 2, 2, 2)))


def cross(cx, cy, r):
    centerline(cx - r, cy, cx + r, cy)
    centerline(cx, cy - r, cx, cy + r)


def arrow(p_from, p_to):
    ax.annotate("", xy=p_to, xytext=p_from,
                arrowprops=dict(arrowstyle="-|>,head_length=0.6,head_width=0.2",
                                lw=LW_THIN, color="k", shrinkA=0, shrinkB=0))


def dim(p1, p2, off, text, ext=True, text_shift=0.0):
    """Lineares Maß zwischen p1 und p2, Maßlinie um `off` senkrecht versetzt."""
    p1, p2 = np.array(p1, float), np.array(p2, float)
    d = p2 - p1
    u = d / np.linalg.norm(d)
    n = np.array([-u[1], u[0]])
    a, b = p1 + n * off, p2 + n * off
    if ext:
        s = np.sign(off)
        for p, q in ((p1, a), (p2, b)):
            ax.plot([p[0] + n[0] * s * 1, q[0] + n[0] * s * 2],
                    [p[1] + n[1] * s * 1, q[1] + n[1] * s * 2], "k", lw=LW_THIN)
    ax.plot([a[0], b[0]], [a[1], b[1]], "k", lw=LW_THIN)
    m = (a + b) / 2
    arrow(m, a)
    arrow(m, b)
    ang = np.degrees(np.arctan2(u[1], u[0]))
    if ang > 90.1 or ang < -89.9:
        ang = (ang + 180) % 360 - 180 if abs(ang) > 90.1 else 90.0
    if ang < -89.9:
        ang += 180
    r = np.radians(ang)
    tp = m + np.array([-np.sin(r), np.cos(r)]) * 1.0 + np.array([np.cos(r), np.sin(r)]) * text_shift
    ax.text(tp[0], tp[1], text, rotation=ang, ha="center", va="bottom",
            rotation_mode="anchor", **FONT)


def dia_leader(cx, cy, r, ang_deg, text, length=14):
    a = np.radians(ang_deg)
    p = np.array([cx + r * np.cos(a), cy + r * np.sin(a)])
    q = p + length * np.array([np.cos(a), np.sin(a)])
    ax.plot([q[0], p[0]], [q[1], p[1]], "k", lw=LW_THIN)
    arrow(q, p)
    k = 1 if np.cos(a) >= 0 else -1
    q2 = q + np.array([k * (len(text) * 2.3 + 2), 0])
    ax.plot([q[0], q2[0]], [q[1], q2[1]], "k", lw=LW_THIN)
    ax.text((q[0] + q2[0]) / 2, q[1] + 0.8, text, ha="center", va="bottom", **FONT)


def label(x, y, text, size=12):
    ax.text(x, y, text, ha="center", va="bottom", fontsize=size, family="DejaVu Sans")


# --- Rahmen ------------------------------------------------------------------
ax.add_patch(Rectangle((20, 10), W - 30, H - 20, fill=False, lw=1.0))

# --- Lage der Ansichten (Projektionsmethode 1) -------------------------------
FX, FY = 95, 205       # Vorderansicht (Blick in +Y)
SX, SY = 95, 75        # Schnitt A–A, unter der Vorderansicht (Blick in −Z)
IX, IY = 290, 200      # Isometrie
h = A / 2

# Vorderansicht
draw_view(part, (0, -500, 0), (0, 0, 1), FX, FY)
cross(FX, FY, h + 6)
dim((FX - h, FY + h), (FX + h, FY + h), 10, "60")
dim((FX - h, FY - h), (FX - h, FY + h), 20, "60", text_shift=14)
dia_leader(FX, FY, 5, 220, "3× Ø10 durchgehend", length=30)
ax.text(FX + h + 7, FY - h - 7.2, "R2 (alle Kanten)", ha="left", va="bottom", **FONT)
ax.plot([FX + h - 0.6, FX + h + 6, FX + h + 40], [FY - h + 0.6, FY - h - 8, FY - h - 8], "k", lw=LW_THIN)
# Schnittverlauf A–A in z = 0
for x0, x1 in ((FX - h - 10, FX - h - 2), (FX + h + 2, FX + h + 10)):
    ax.plot([x0, x1], [FY, FY], "k", lw=1.4)
for xa in (FX - h - 6, FX + h + 6):
    arrow((xa, FY), (xa, FY - 8))
    ax.text(xa + (-3 if xa < FX else 3), FY - 9, "A", ha="center", va="top", fontsize=12)
label(FX, FY + h + 18, "Vorderansicht")

# Schnitt A–A: untere Hälfte von oben, Schnittfläche schraffiert
unten = part - Pos(0, 0, A / 2) * Box(A + 10, A + 10, A)
draw_view(unten, (0, 0, 500), (0, 1, 0), SX, SY)
schnitt = part.intersect(Plane.XY)
for f in schnitt.faces():
    verts, codes = [], []
    for w in [f.outer_wire(), *f.inner_wires()]:
        p = np.array([[q.X, q.Y] for q in (w @ t for t in np.linspace(0, 1, 400))])
        verts += list(p + [SX, SY]) + [p[0] + [SX, SY]]
        codes += [Path.MOVETO] + [Path.LINETO] * (len(p) - 1) + [Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor="none", edgecolor="k",
                           hatch="////", lw=LW_VIS))
plt.rcParams["hatch.linewidth"] = 0.3
cross(SX, SY, h + 6)
label(SX - 25, SY + h + 30, "Schnitt A–A")

# Stufenbohrung rechts bemaßt (alle sechs Seiten gleich)
for k, (d, t) in enumerate(SACKLOECHER):
    r = d / 2
    dim((SX + h, SY - r), (SX + h, SY + r), -(8 + 8 * k), f"Ø{d:.0f}")
    dim((SX + h, SY + r), (SX + h - t, SY + r), -(h + 6 + 6 * k - r), f"{t:g}".replace(".", ","))

# Isometrie (ohne Maßstab)
draw_view(part, (500, -500, 400), (0, 0, 1), IX, IY)
label(IX, IY + 52, "Isometrie (ohne Maßstab)")

# --- Hinweise ------------------------------------------------------------------
notes = [
    "Hinweise:",
    "1. Alle Bohrungen zentrisch in der jeweiligen Seitenfläche.",
    "2. Ø10 durchgehend in X-, Y- und Z-Richtung.",
    "3. Stufenbohrung auf allen 6 Seiten gleich (flacher Grund):",
    "    " + " · ".join(f"Ø{d:.0f} T{t:g}".replace(".", ",") for d, t in reversed(SACKLOECHER)) + ".",
    "    Bohrungen benachbarter Seiten durchdringen sich -> geschachtelte",
    "    Würfelrahmen (Steg/Spalt 2,5), an den Ecken über Diagonalstege verbunden.",
    "4. Äußere Würfelkanten gerundet R2, alle inneren Kanten R1.",
    "5. Allgemeintoleranzen ISO 2768-m.  Maße in mm.",
    "6. Oberfläche: Gold, gebürstet.",
]
for i, n in enumerate(notes):
    ax.text(200, 120 - i * 6, n, ha="left", va="top", **FONT)

# --- Schriftfeld (180 × 36) ----------------------------------------------------
x0, y0, bw, bh = W - 10 - 180, 10, 180, 36
ax.add_patch(Rectangle((x0, y0), bw, bh, fill=False, lw=1.0))
for y in (y0 + 12, y0 + 24):
    ax.plot([x0, x0 + bw], [y, y], "k", lw=0.5)
for x in (x0 + 60, x0 + 120):
    ax.plot([x, x], [y0, y0 + 24], "k", lw=0.5)
ax.text(x0 + 3, y0 + 30, "Würfel 60 mm mit Bohrungen", fontsize=14, va="center",
        family="DejaVu Sans", weight="bold")
cells = [
    (x0, y0 + 12, "Maßstab", "1:1"),
    (x0 + 60, y0 + 12, "Einheit", "mm"),
    (x0 + 120, y0 + 12, "Datum", "23.10.2026"),
    (x0, y0, "Werkstoff / Oberfläche", "Gold gebürstet"),
    (x0 + 60, y0, "Format", "A3"),
    (x0 + 120, y0, "Zeichnungs-Nr.", "WF-060-001"),
]
for x, y, k, v in cells:
    ax.text(x + 2, y + 10, k, fontsize=6.5, va="top", family="DejaVu Sans")
    ax.text(x + 2, y + 2, v, fontsize=10, va="bottom", family="DejaVu Sans")
# Symbol Projektionsmethode 1
sx, sy = x0 + 100, y0 + 18
ax.plot([sx - 9, sx - 3, sx - 3, sx - 9, sx - 9], [sy - 2, sy - 3.5, sy + 3.5, sy + 2, sy - 2], "k", lw=0.5)
ax.add_patch(Circle((sx + 4, sy), 3.5, fill=False, lw=0.5))
ax.add_patch(Circle((sx + 4, sy), 1.8, fill=False, lw=0.5))

fig.savefig("wuerfel_zeichnung.pdf")
fig.savefig("wuerfel_zeichnung.png", dpi=150)
print("ok")
