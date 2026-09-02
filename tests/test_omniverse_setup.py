"""Offline tests for harness.omniverse_setup — headless Kit install PLAN only."""
import omniverse_setup


def test_headless_kit_install_plan_is_valid_and_ordered():
    plan = omniverse_setup.build_install_steps()
    assert plan["count"] == len(plan["steps"])
    assert plan["count"] >= 4
    ids = [s["id"] for s in plan["steps"]]
    # ordered: confirm GPU/driver first, verify Kit last
    assert ids[0] == "driver-check"
    assert ids[-1] == "verify-kit"
    assert {"driver-check", "system-deps", "fetch-kit",
            "headless-config", "verify-kit"} <= set(ids)
    # every step is well-formed
    for s in plan["steps"]:
        assert s["id"] and s["description"] and s["command"]
    # render-layer-only boundary + gated live run
    assert "render" in plan["layer"].lower()
    assert "TODO" in plan["live_run"]


def test_fetch_kit_step_declares_ngc_key_need():
    plan = omniverse_setup.build_install_steps()
    fetch = next(s for s in plan["steps"] if s["id"] == "fetch-kit")
    assert fetch.get("needs") == "NGC_API_KEY"


def test_cli_entry_points_and_run_refuses():
    assert omniverse_setup.main(["--plan"]) == 0
    assert omniverse_setup.main(["--json"]) == 0
    assert omniverse_setup.main([]) == 0
    # on-host install is a gated TODO -> --run refuses (exit 3)
    assert omniverse_setup.main(["--run"]) == 3
