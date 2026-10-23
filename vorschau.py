"""Goldfarben schattierte Vorschau (gesamt + aufgeschnitten): python vorschau.py wuerfel_vorschau.png"""
import sys, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

from build123d import Box, Pos
from wuerfel import build
part = build()
half = part - Pos(0, -40, 0) * Box(80, 80, 80)  # vordere Hälfte weg (y<0)... keep y>0
def mesh(s):
    v, t = s.tessellate(0.05, 0.2)
    return np.array([[p.X, p.Y, p.Z] for p in v]), np.array(t)
fig, axs = plt.subplots(1, 2, figsize=(14, 7))
for ax, s, ttl in ((axs[0], part, "gesamt"), (axs[1], half, "halbiert")):
    V, T = mesh(s)
    d = np.array([1, -1.3, 0.9]); d /= np.linalg.norm(d)
    up = np.array([0, 0, 1.0]); rgt = np.cross(up, d); rgt /= np.linalg.norm(rgt); up2 = np.cross(d, rgt)
    P = np.c_[V @ rgt, V @ up2]; depth = V @ d
    tri = V[T]; n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
    vis = n @ d > 0
    L = np.array([0.4, -0.6, 0.7]); L /= np.linalg.norm(L)
    sh = 0.35 + 0.65 * np.clip(n @ L, 0, 1)
    order = np.argsort(depth[T].mean(1))
    order = order[vis[order]]
    col = np.outer(sh[order], [1.0, 0.77, 0.34])
    ax.add_collection(PolyCollection(P[T[order]], facecolors=np.clip(col, 0, 1), edgecolors=np.clip(col, 0, 1), linewidths=0.3))
    ax.set_xlim(-50, 50); ax.set_ylim(-50, 50); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(ttl)
fig.savefig(sys.argv[1], dpi=110, bbox_inches="tight")
