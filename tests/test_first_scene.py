"""Offline tests for harness.first_scene — the 'hello Omniverse' USD target."""
from unittest import mock

import first_scene


def test_hello_omniverse_usd_target_spec():
    spec = first_scene.build_scene_spec()
    assert spec["target_usd"].endswith(".usd")
    assert "hello" in spec["target_usd"].lower()
    assert spec["up_axis"] == "Z"
    assert spec["prim_count"] == len(spec["prims"])
    assert spec["prim_count"] >= 4
    paths = {p["path"] for p in spec["prims"]}
    assert {"/World", "/World/Light", "/World/Ground",
            "/World/Cube", "/World/Camera"} <= paths
    assert "from pxr import" in spec["authoring_snippet"]
    assert "TODO" in spec["live_author"]


def test_dry_run_and_json_entry_points_return_zero():
    assert first_scene.main(["--dry-run"]) == 0
    assert first_scene.main(["--json"]) == 0
    assert first_scene.main([]) == 0


def test_run_refuses_when_usd_unavailable():
    # pxr/USD exists only inside an Omniverse Kit runtime; --run must refuse
    # (exit 3) rather than fabricate an authored/rendered result.
    with mock.patch.object(first_scene, "_have_usd", return_value=False):
        assert first_scene.main(["--run"]) == 3
