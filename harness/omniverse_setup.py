#!/usr/bin/env python3
"""omniverse_setup.py — headless NVIDIA Omniverse Kit install plan for the g6e host.

Emits the ordered, on-host steps to bring Omniverse Kit up headless on the
provisioned g6e instance (the render layer for Exowatt's digital twin). These
run ON THE HOST over SSH after provision_g6e; this module PLANS them and does
not execute anything. Live execution is a gated TODO.
"""
from __future__ import annotations

import argparse
import json

# Ordered steps. `command` fields are illustrative on-host commands; confirm
# exact package names/URLs against current NVIDIA Omniverse docs before running.
INSTALL_STEPS = [
    {
        "id": "driver-check",
        "description": "Confirm the NVIDIA driver + GPU are visible on the host.",
        "command": "nvidia-smi",
        "expect": "L40S (or the provisioned GPU) listed; driver + CUDA version shown",
    },
    {
        "id": "system-deps",
        "description": "Install headless GL / Vulkan runtime deps Kit needs with no display.",
        "command": "sudo apt-get update && sudo apt-get install -y libglu1-mesa libxrandr2 libxinerama1 libxcursor1 libgomp1 libvulkan1",
    },
    {
        "id": "fetch-kit",
        "description": "Fetch the Omniverse Kit SDK / kit-app-template (headless). Requires an NGC API key for nvcr.io pulls (see the ngc-api-key skill).",
        "command": "# per NVIDIA Omniverse Kit docs: clone kit-app-template or pull the Kit container from nvcr.io",
        "needs": "NGC_API_KEY",
    },
    {
        "id": "headless-config",
        "description": "Configure Kit for headless operation (no local display; optional Omniverse streaming for a remote viewport).",
        "command": "# run kit with --no-window / the headless streaming app config",
    },
    {
        "id": "verify-kit",
        "description": "Launch Kit headless once and confirm it initializes the renderer and exits cleanly.",
        "command": "./kit --no-window --exec 'print(\"kit up\")'",
        "expect": "renderer initializes; 'kit up' printed; exit 0",
    },
]


def build_install_steps() -> dict:
    """Return the ordered headless-Kit install plan (inspectable, not executed)."""
    return {
        "target": "provisioned g6e host (see provision_g6e.py)",
        "layer": "rendering only — Omniverse renders Exowatt's own Titan physics output",
        "steps": INSTALL_STEPS,
        "count": len(INSTALL_STEPS),
        "live_run": (
            "TODO (gated, on-host): these steps run on the g6e instance over SSH "
            "after it is provisioned and reachable. Not automated here."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Plan the headless Omniverse Kit install (does not execute).")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--plan", action="store_true", help="print the step plan (default)")
    ap.add_argument("--dry-run", action="store_true", help="alias for --plan")
    ap.add_argument("--run", action="store_true", help="refuse: on-host install is a gated TODO")
    args = ap.parse_args(argv)

    if args.run:
        print("REFUSED: the install runs on the provisioned host over SSH and is "
              "a gated TODO here (see 'live_run'). Provision the host first.")
        return 3

    plan = build_install_steps()
    if args.json:
        print(json.dumps(plan, indent=2))
        return 0

    print(f"Headless Omniverse Kit install plan — {plan['count']} steps ({plan['layer']})")
    for i, step in enumerate(plan["steps"], 1):
        print(f"  {i}. [{step['id']}] {step['description']}")
        print(f"       $ {step['command']}")
        if step.get("needs"):
            print(f"       needs: {step['needs']}")
        if step.get("expect"):
            print(f"       expect: {step['expect']}")
    print(f"live run: {plan['live_run']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
