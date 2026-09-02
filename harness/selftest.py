#!/usr/bin/env python3
"""selftest.py — the offline verification `make verify` runs.

Imports every harness module, exercises its pure planning function, and
asserts the plan invariants. Uses the Python standard library only: no boto3,
no AWS calls, no GPU, no network, no cost. Exit 0 iff every plan is valid.
"""
from __future__ import annotations

import os
import sys

# Make the sibling harness modules importable no matter the caller's cwd.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import quota_check      # noqa: E402
import provision_g6e    # noqa: E402
import omniverse_setup  # noqa: E402
import first_scene      # noqa: E402

CHECKS: list[tuple[str, "callable"]] = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


@check("quota_check: reports the On-Demand G/VT quota-0 blocker offline")
def _c1():
    r = quota_check.build_quota_report(region="us-east-1", live=False)
    assert r["region"] == "us-east-1"
    assert r["quotas"]["on_demand_g_vt"]["code"] == "L-DB2E81BA"
    assert r["quotas"]["on_demand_g_vt"]["current_vcpus"] == 0
    assert r["blocker"] is True
    assert r["target_fleet_vcpus"] == 128
    assert quota_check.main(["--dry-run"]) == 0
    assert quota_check.main(["--json"]) == 0


@check("provision_g6e: on-demand g6e.4xlarge plan, live launch gated")
def _c2():
    p = provision_g6e.build_launch_plan(strategy="ondemand")
    assert p["instance_type"] == "g6e.4xlarge"
    assert p["instance_spec"]["gpu"] == "1x NVIDIA L40S"
    assert p["api"] == "ec2:RunInstances"
    assert "TODO" in p["live_launch"]
    assert p["image_id"].startswith("TODO")  # nothing fabricated
    assert provision_g6e.main(["--dry-run"]) == 0
    # --run must refuse (non-zero), never launch.
    assert provision_g6e.main(["--run"]) == 3


@check("provision_g6e: Spot Fleet g6.24xlarge fallback plan")
def _c3():
    p = provision_g6e.build_launch_plan(strategy="spot")
    assert p["instance_type"] == "g6.24xlarge"
    assert p["api"] == "ec2:RequestSpotFleet"
    assert "fallback" in p["instance_spec"]["role"].lower()
    assert provision_g6e.main(["--strategy", "spot", "--dry-run"]) == 0


@check("omniverse_setup: headless Kit install plan is render-layer-only")
def _c4():
    plan = omniverse_setup.build_install_steps()
    assert plan["count"] >= 4
    ids = {s["id"] for s in plan["steps"]}
    assert {"driver-check", "verify-kit"} <= ids
    assert "render" in plan["layer"].lower()
    assert "TODO" in plan["live_run"]
    assert omniverse_setup.main(["--plan"]) == 0
    assert omniverse_setup.main(["--run"]) == 3


@check("first_scene: hello-Omniverse USD target, authoring gated")
def _c5():
    spec = first_scene.build_scene_spec()
    assert spec["target_usd"].endswith(".usd")
    assert spec["up_axis"] == "Z"
    assert spec["prim_count"] == len(spec["prims"]) >= 4
    assert "from pxr import" in spec["authoring_snippet"]
    assert "TODO" in spec["live_author"]
    assert first_scene.main(["--dry-run"]) == 0


def main() -> int:
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionError as exc:
            failures += 1
            print(f"  FAIL  {name}\n        {exc}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"  ERROR {name}\n        {type(exc).__name__}: {exc}")
        else:
            print(f"  PASS  {name}")
    total = len(CHECKS)
    print()
    if failures:
        print(f"harness selftest: FAIL ({total - failures}/{total} passed)")
        return 1
    print(f"harness selftest: PASS ({total}/{total} plans valid, offline, no AWS calls)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
