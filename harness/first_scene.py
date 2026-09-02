#!/usr/bin/env python3
"""first_scene.py — the "hello Omniverse" USD scene target (the POC proof).

Defines the smallest scene that proves Omniverse Kit renders on the g6e host:
a Z-up stage with a distant light, a ground plane, a cube, and a camera,
authored as a .usd file. This module DESCRIBES the target and prints the USD
authoring code it would run; it does not author or render, because pxr/USD only
exists inside an Omniverse Kit runtime. Live authoring on the host is a TODO.
"""
from __future__ import annotations

import argparse
import json

TARGET_USD = "scenes/hello_exowatt.usd"

# The prims the hello-world stage must contain.
SCENE_PRIMS = [
    {"path": "/World", "type": "Xform", "role": "scene root"},
    {"path": "/World/Light", "type": "DistantLight", "role": "key light (intensity ~3000)"},
    {"path": "/World/Ground", "type": "Mesh", "role": "ground plane (10x10)"},
    {"path": "/World/Cube", "type": "Cube", "role": "the hello-world object"},
    {"path": "/World/Camera", "type": "Camera", "role": "framing camera"},
]

# Illustrative pxr/USD authoring snippet. Runs only inside Omniverse Kit /
# a USD-enabled Python. Kept as a string so this module stays pure stdlib.
USD_AUTHORING_SNIPPET = '''\
from pxr import Usd, UsdGeom, UsdLux, Gf

stage = Usd.Stage.CreateNew("hello_exowatt.usd")
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

world = UsdGeom.Xform.Define(stage, "/World")

light = UsdLux.DistantLight.Define(stage, "/World/Light")
light.CreateIntensityAttr(3000.0)

ground = UsdGeom.Mesh.Define(stage, "/World/Ground")  # a 10x10 quad
cube = UsdGeom.Cube.Define(stage, "/World/Cube")
cube.AddTranslateOp().Set(Gf.Vec3d(0, 0, 1))

cam = UsdGeom.Camera.Define(stage, "/World/Camera")
cam.AddTranslateOp().Set(Gf.Vec3d(8, 8, 6))

stage.GetRootLayer().Save()
print("wrote hello_exowatt.usd")
'''


def build_scene_spec() -> dict:
    """Return the target scene spec (inspectable; nothing is authored or rendered)."""
    return {
        "target_usd": TARGET_USD,
        "up_axis": "Z",
        "prims": SCENE_PRIMS,
        "prim_count": len(SCENE_PRIMS),
        "authoring_snippet": USD_AUTHORING_SNIPPET,
        "live_author": (
            "TODO (gated, on-host): authoring/rendering needs pxr/USD inside an "
            "Omniverse Kit runtime on the g6e host. Not runnable in this offline harness."
        ),
    }


def _have_usd() -> bool:
    try:
        import pxr  # noqa: F401 - only present inside Omniverse Kit
        return True
    except ImportError:
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Show the target 'hello Omniverse' USD scene (does not author/render).")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the target scene + USD code (default)")
    ap.add_argument("--run", action="store_true", help="attempt to author (needs pxr inside Omniverse Kit)")
    args = ap.parse_args(argv)

    spec = build_scene_spec()

    if args.run:
        if not _have_usd():
            print("REFUSED: pxr/USD is not importable here. Author the scene on the "
                  "g6e host inside Omniverse Kit (see 'live_author'). Not fabricated.")
            return 3
        print("pxr present, but on-host authoring is intentionally left to the "
              "operator inside Kit — see the authoring snippet below.")
        return 0

    if args.json:
        print(json.dumps(spec, indent=2))
        return 0

    print(f"Target scene: {spec['target_usd']}  (up-axis {spec['up_axis']}, "
          f"{spec['prim_count']} prims)")
    for p in spec["prims"]:
        print(f"  {p['path']:<16} {p['type']:<12} - {p['role']}")
    print("USD authoring code (runs inside Omniverse Kit):")
    for line in spec["authoring_snippet"].splitlines():
        print(f"    {line}")
    print(f"live author: {spec['live_author']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
