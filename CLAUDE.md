# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Parametric CAD model of a 60 mm cube (German naming throughout): stepped bores on all six faces cut deep enough that adjacent faces' bores intersect, leaving nested cube frames joined by struts along the space diagonals. `prompt.md` is the authoritative spec — keep it in sync when the geometry or outputs change.

## Commands

Python 3.12 venv with build123d + matplotlib (create with `python3 -m venv .venv && .venv/bin/pip install build123d matplotlib`). Run from the repo root — scripts write outputs to the CWD and import `wuerfel`.

```sh
.venv/bin/python wuerfel.py                      # build + print volume, validity, solid count (must be 1)
.venv/bin/python export.py                       # -> wuerfel.stl, wuerfel.step, wuerfel_gold.glb
.venv/bin/python zeichnung.py                    # -> wuerfel_zeichnung.pdf / .png (A3 drawing)
.venv/bin/python vorschau.py wuerfel_vorschau.png  # gold-shaded preview, full + cut open
.venv/bin/python video.py                          # 60 s rotation video from wuerfel_gold.glb (pyvista PBR, ~2 min); --test = 3 stills
```

`README.md` (English) embeds the drawing, preview and `wuerfel_rotation.gif`. After re-rendering the video, rebuild the GIF with the ffmpeg command listed there.

No test suite. Verification after geometry changes: `wuerfel.py` reports `valid: True` and `Körper: 1`; the STL has zero non-manifold edges (weld vertices, drop degenerate triangles, count edges not shared by exactly 2 triangles); look at the rendered PNGs.

## Architecture

- `wuerfel.py` is the single source of geometry. `build()` returns the finished `Part`; all other scripts import `build()` and constants (`A`, `SACKLOECHER`, `D_DURCH`, …) from it, so dimensions are never duplicated.
- Build order matters: box → outer R2 fillet → through-bores Ø10 + stepped bores on ±X/±Y/±Z → R1 fillet on all *sharp* inner edges (`_scharf` skips tangent edges such as the R2 blend seams).
- Bore depths are derived, not hard-coded: depth = A/2 − (r − 5 + `STEG`), i.e. each step's floor sits `STEG` outside the next smaller bore radius. Diameters step by 5 mm, so `STEG` sets frame bar thickness and the gap is 5 − `STEG`. Max inner fillet is ~`STEG`/2, so changing `STEG` may require changing `R_INNEN`.
- `export.py` writes the GLB by hand (no glTF library): per-face tessellation, vertex normals accumulated from triangles (`Face.normal_at` fails at fillet poles), axis remap CAD Z-up mm → glTF Y-up m. The remap is a rotation, so triangle winding must *not* be flipped. Gold material is PBR plus `KHR_materials_anisotropy`; viewers without that extension (macOS Preview) show unbrushed gold.
- `zeichnung.py` draws in sheet millimetres on a full-figure matplotlib axis (A3 420×297, scale 1:1, first-angle projection). Views come from `Part.project_to_viewport` (front: X right/Z up; top: X right/Y up). Section A–A = lower half viewed from +Z plus hatched faces from `part.intersect(Plane.XY)`. Bore dimensions loop over `SACKLOECHER`; the title block, notes and dimension offsets are positioned by hand, so re-check the PNG for overlaps after changes.
- Fine tessellation with the inner fillets explodes triangle count (0.01 mm → ~1.1 M triangles); keep 0.02 mm / 0.25 rad.
