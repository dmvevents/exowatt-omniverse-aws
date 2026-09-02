"""Honesty guard: the harness PLANS, it does not fabricate launches or results.

No plan may contain a concrete AWS resource id (they are all TODO placeholders),
and every live path is a gated TODO / refuses at --run. This is the anti-slop
check: no invented instance ids, AMIs, or 'running' statuses.
"""
import json
import re
from unittest import mock

import quota_check
import provision_g6e
import omniverse_setup
import first_scene

# Concrete AWS resource ids that would betray a fabricated launch/result.
_FABRICATED_ID = re.compile(r"\b(?:ami|i|sg|subnet|vol|eni|sfr|fleet)-[0-9a-f]{6,}\b")


def _all_plans_json():
    return "\n".join([
        json.dumps(quota_check.build_quota_report(live=False)),
        json.dumps(provision_g6e.build_launch_plan(strategy="ondemand")),
        json.dumps(provision_g6e.build_launch_plan(strategy="spot")),
        json.dumps(omniverse_setup.build_install_steps()),
        json.dumps(first_scene.build_scene_spec()),
    ])


def test_no_fabricated_aws_resource_ids_in_any_plan():
    blob = _all_plans_json()
    hit = _FABRICATED_ID.search(blob)
    assert hit is None, f"fabricated-looking AWS resource id in a plan: {hit.group(0)!r}"


def test_provision_operator_inputs_are_todo_placeholders():
    p = provision_g6e.build_launch_plan(strategy="ondemand")
    for field in ("image_id", "key_name", "subnet_id", "iam_instance_profile"):
        assert str(p[field]).startswith("TODO"), f"{field} is not a TODO placeholder"
    assert p["security_group_ids"][0].startswith("TODO")


def test_every_live_path_is_gated_todo_or_refuses():
    assert "TODO" in provision_g6e.build_launch_plan()["live_launch"]
    assert "TODO" in omniverse_setup.build_install_steps()["live_run"]
    assert "TODO" in first_scene.build_scene_spec()["live_author"]
    # --run entry points refuse (exit 3) rather than fabricate a result
    assert provision_g6e.main(["--run"]) == 3
    assert omniverse_setup.main(["--run"]) == 3
    with mock.patch.object(first_scene, "_have_usd", return_value=False):
        assert first_scene.main(["--run"]) == 3
