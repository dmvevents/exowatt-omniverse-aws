"""Offline tests for harness.provision_g6e — the launch PLAN, never a launch."""
import pytest

import provision_g6e


def test_default_ondemand_plan_is_g6e_4xlarge_l40s():
    p = provision_g6e.build_launch_plan(strategy="ondemand")
    assert p["strategy"] == "ondemand"
    assert p["instance_type"] == "g6e.4xlarge"
    assert p["instance_spec"]["vcpus"] == 16
    assert p["instance_spec"]["gpu"] == "1x NVIDIA L40S"
    assert p["api"] == "ec2:RunInstances"
    assert p["run_instances_params"]["InstanceType"] == "g6e.4xlarge"
    # nothing fabricated — operator inputs are TODO placeholders
    assert p["image_id"].startswith("TODO")
    assert "TODO" in p["live_launch"]
    assert "quota" in p["precondition"].lower()


def test_spot_fallback_plan_is_g6_24xlarge():
    p = provision_g6e.build_launch_plan(strategy="spot")
    assert p["instance_type"] == "g6.24xlarge"
    assert p["api"] == "ec2:RequestSpotFleet"
    assert "fallback" in p["instance_spec"]["role"].lower()
    assert p["spot_fleet_request_config"]["TargetCapacity"] == 1
    assert "TODO" in p["live_launch"]


def test_instance_ladder_covers_l40s_then_rtx_then_spot():
    opts = provision_g6e.INSTANCE_OPTIONS
    # primary L40S Omniverse host
    assert "recommended" in opts["g6e.4xlarge"]["role"].lower()
    assert opts["g6e.4xlarge"]["gpu"] == "1x NVIDIA L40S"
    # John@NVIDIA RTX / ray-tracing alternatives
    assert "g6e.xlarge" in opts
    assert "g7e.xlarge" in opts
    role7 = opts["g7e.xlarge"]["role"].lower()
    assert "rtx" in role7 or "ray tracing" in role7
    # Spot interim fallback (quota-0 workaround)
    assert "fallback" in opts["g6.24xlarge"]["role"].lower()
    assert provision_g6e.DEFAULT_ONDEMAND == "g6e.4xlarge"
    assert provision_g6e.DEFAULT_SPOT == "g6.24xlarge"


def test_build_plan_rejects_bad_strategy_and_instance():
    with pytest.raises(ValueError):
        provision_g6e.build_launch_plan(strategy="reserved")
    with pytest.raises(ValueError):
        provision_g6e.build_launch_plan(instance_type="p5.48xlarge")


def test_live_run_refuses_with_exit_3():
    # The gated human checkpoint: --run must REFUSE (exit 3), never launch.
    assert provision_g6e.main(["--run"]) == 3


def test_dry_run_and_json_entry_points_return_zero():
    assert provision_g6e.main(["--dry-run"]) == 0
    assert provision_g6e.main(["--strategy", "spot", "--dry-run"]) == 0
    assert provision_g6e.main(["--json"]) == 0
    assert provision_g6e.main([]) == 0
