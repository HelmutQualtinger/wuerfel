"""Video des goldenen Würfels aus wuerfel_gold.glb, Drehung um X, Y und Z.

    python video.py [ausgabe.mp4] [--test]

60 s, 30 fps, 1920×1080. Nahtlose Schleife: X 1, Y 2, Z 1 Umdrehungen.
PBR-Gold mit Studio-Umgebung (prozedurale Cubemap mit Softboxen).
"""
import json
import struct
import sys
import tempfile
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
import pyvista as pv

DAUER, FPS, W, H = 60, 30, 1920, 1080
UMDREHUNGEN = (1, 2, 1)   # X, Y, Z


def lade_glb(pfad):
    b = Path(pfad).read_bytes()
    jl = struct.unpack("<I", b[12:16])[0]
    g = json.loads(b[20:20 + jl])
    off = 20 + jl + 8
    acc = []
    for a in g["accessors"]:
        bv = g["bufferViews"][a["bufferView"]]
        dt = np.float32 if a["componentType"] == 5126 else np.uint32
        n = 3 if a["type"] == "VEC3" else 1
        acc.append(np.frombuffer(b, dt, a["count"] * n, off + bv["byteOffset"]).reshape(-1, n))
    P, N, I = acc
    mesh = pv.PolyData(P * 1000, np.c_[np.full(len(I) // 3, 3), I.reshape(-1, 3)].ravel())
    mesh.point_data["Normals"] = N
    mesh.point_data.active_normals_name = "Normals"
    return mesh


def studio_cubemap(ordner):
    """Sechs Bilder: dunkelgrauer Raum mit hellen Softboxen."""
    s = 512
    u, v = np.meshgrid(np.linspace(-1, 1, s), np.linspace(-1, 1, s))
    pfade = []
    for name, boxen in [
        ("posx", [(0.0, -0.1, 0.5, 0.7, 1.0)]),
        ("negx", [(0.0, 0.0, 0.35, 0.35, 0.45)]),
        ("posy", [(0.0, 0.0, 0.7, 0.7, 1.2)]),        # oben
        ("negy", []),                                  # Boden
        ("posz", [(-0.3, -0.1, 0.25, 0.8, 0.8)]),
        ("negz", [(0.4, 0.0, 0.3, 0.5, 0.6)]),
    ]:
        img = 0.18 + 0.12 * (1 - v) / 2 if name != "negy" else np.full_like(u, 0.05)
        for cx, cy, rx, ry, hell in boxen:
            d = np.maximum(np.abs(u - cx) / rx, np.abs(v - cy) / ry)
            img = img + hell * np.clip((1.15 - d) / 0.15, 0, 1)
        rgb = (np.clip(np.stack([img] * 3, -1), 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)
        p = Path(ordner) / f"{name}.png"
        imageio.imwrite(p, rgb)
        pfade.append(str(p))
    return pv.cubemap_from_filenames(pfade)


def rotation(t):
    ax, ay, az = (2 * np.pi * k * t for k in UMDREHUNGEN)
    cx, sx, cy, sy, cz, sz = np.cos(ax), np.sin(ax), np.cos(ay), np.sin(ay), np.cos(az), np.sin(az)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    M = np.eye(4)
    M[:3, :3] = Rz @ Ry @ Rx
    return M


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    test = "--test" in sys.argv
    ziel = args[0] if args else "wuerfel_rotation.mp4"

    mesh = lade_glb("wuerfel_gold.glb")
    pl = pv.Plotter(off_screen=True, window_size=(W, H))
    pl.set_background("#1a1a1d", top="#3a3a40")
    with tempfile.TemporaryDirectory() as tmp:
        pl.set_environment_texture(studio_cubemap(tmp), is_srgb=True)
    actor = pl.add_mesh(mesh, color=(1.0, 0.766, 0.336), pbr=True, metallic=1.0,
                        roughness=0.35, smooth_shading=True)
    pl.camera.position = (0, -185, 60)
    pl.camera.focal_point = (0, 0, 0)
    pl.camera.up = (0, 0, 1)
    pl.camera.view_angle = 30

    if test:
        for t in (0.05, 0.3, 0.7):
            actor.user_matrix = rotation(t)
            pl.render()
            pl.screenshot(f"{Path(ziel).stem}_test_{t}.png")
        return

    n = DAUER * FPS
    with imageio.get_writer(ziel, fps=FPS, codec="libx264", quality=None, ffmpeg_params=["-crf", "23", "-preset", "slow", "-movflags", "+faststart"],
                            macro_block_size=8, pixelformat="yuv420p") as w:
        for i in range(n):
            actor.user_matrix = rotation(i / n)
            pl.render()
            w.append_data(pl.screenshot(return_img=True))
            if i % 300 == 0:
                print(f"{i}/{n}", flush=True)
    pl.close()
    print("fertig:", ziel)


if __name__ == "__main__":
    main()
