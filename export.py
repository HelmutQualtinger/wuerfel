"""Exportiert STL, STEP und GLB (gebürstetes Gold, PBR) des Würfels."""
import json
import struct

import numpy as np
from build123d import Vector, export_step, export_stl

from wuerfel import build

part = build()
export_stl(part, "wuerfel.stl", tolerance=0.02, angular_tolerance=0.25)
export_step(part, "wuerfel.step")

# --- GLB mit gebürstetem Gold ---------------------------------------------
pos, nor, idx = [], [], []
for face in part.faces():
    verts, tris = face.tessellate(0.02, 0.25)
    base = len(pos)
    fv = np.array([(v.X, v.Y, v.Z) for v in verts])
    ft = np.array(tris).reshape(-1, 3)
    # Vertex-Normalen aus Dreiecken (normal_at versagt an Kugelpolen der Rundungen)
    fn = np.cross(fv[ft[:, 1]] - fv[ft[:, 0]], fv[ft[:, 2]] - fv[ft[:, 0]])
    vn = np.zeros_like(fv)
    for k in range(3):
        np.add.at(vn, ft[:, k], fn)
    pos.extend(map(tuple, fv))
    nor.extend(map(tuple, vn))
    idx.extend((base + a, base + b, base + c) for a, b, c in ft)

# glTF: Y nach oben, Meter (Drehung um X: Würfel-Z -> glTF-Y)
P = np.array(pos, np.float32)[:, [0, 2, 1]] * np.array([1, 1, -1], np.float32) / 1000
N = np.array(nor, np.float32)[:, [0, 2, 1]] * np.array([1, 1, -1], np.float32)
I = np.array(idx, np.uint32)
N /= np.linalg.norm(N, axis=1, keepdims=True)

blob = P.tobytes() + N.tobytes() + I.tobytes()
gltf = {
    "asset": {"version": "2.0", "generator": "build123d + numpy"},
    "extensionsUsed": ["KHR_materials_anisotropy"],
    "scene": 0,
    "scenes": [{"nodes": [0]}],
    "nodes": [{"mesh": 0, "name": "Wuerfel"}],
    "meshes": [{"name": "Wuerfel", "primitives": [{
        "attributes": {"POSITION": 0, "NORMAL": 1}, "indices": 2, "material": 0}]}],
    "materials": [{
        "name": "Gold gebuerstet",
        "pbrMetallicRoughness": {
            "baseColorFactor": [1.0, 0.766, 0.336, 1.0],
            "metallicFactor": 1.0,
            "roughnessFactor": 0.35,
        },
        "extensions": {"KHR_materials_anisotropy": {"anisotropyStrength": 0.7,
                                                    "anisotropyRotation": 0.0}},
    }],
    "buffers": [{"byteLength": len(blob)}],
    "bufferViews": [
        {"buffer": 0, "byteOffset": 0, "byteLength": P.nbytes, "target": 34962},
        {"buffer": 0, "byteOffset": P.nbytes, "byteLength": N.nbytes, "target": 34962},
        {"buffer": 0, "byteOffset": P.nbytes + N.nbytes, "byteLength": I.nbytes, "target": 34963},
    ],
    "accessors": [
        {"bufferView": 0, "componentType": 5126, "count": len(P), "type": "VEC3",
         "min": P.min(0).tolist(), "max": P.max(0).tolist()},
        {"bufferView": 1, "componentType": 5126, "count": len(N), "type": "VEC3"},
        {"bufferView": 2, "componentType": 5125, "count": I.size, "type": "SCALAR"},
    ],
}
js = json.dumps(gltf).encode()
js += b" " * (-len(js) % 4)
blob += b"\0" * (-len(blob) % 4)
with open("wuerfel_gold.glb", "wb") as f:
    f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)))
    f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
    f.write(struct.pack("<II", len(blob), 0x004E4942) + blob)

print("Dreiecke:", len(I), "Vertices:", len(P))
