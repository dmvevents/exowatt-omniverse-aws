"""Offline tests for harness.quota_check — no real AWS calls, ever.

boto3 IS installed on the dev/CI host, so the live path is exercised with a
mocked boto3 injected into sys.modules; nothing contacts AWS Service Quotas.
"""
import sys
import types
from unittest import mock

import quota_check


def test_offline_baseline_flags_the_quota0_blocker():
    r = quota_check.build_quota_report(region="us-east-1", live=False)
    assert r["region"] == "us-east-1"
    assert r["mode"] == "offline-baseline"
    od = r["quotas"]["on_demand_g_vt"]
    assert od["code"] == quota_check.ON_DEMAND_G_VT == "L-DB2E81BA"
    assert od["current_vcpus"] == 0            # the real blocker on this engagement
    assert od["requested_vcpus"] == 128
    assert r["blocker"] is True
    assert r["target_fleet_vcpus"] == 128      # 8 x 16-vCPU g6e.4xlarge
    assert "Spot Fleet g6.24xlarge" in r["recommendation"]


def _fake_boto3(od_value, spot_value, seen):
    fake = types.ModuleType("boto3")

    def _client(service, region_name=None):
        seen["service"] = service
        seen["region"] = region_name
        client = mock.MagicMock()

        def _get(ServiceCode, QuotaCode):
            seen.setdefault("service_codes", []).append(ServiceCode)
            value = od_value if QuotaCode == quota_check.ON_DEMAND_G_VT else spot_value
            return {"Quota": {"Value": value}}

        client.get_service_quota.side_effect = _get
        return client

    fake.client = _client
    return fake


def test_live_path_flags_blocker_from_mocked_service_quotas():
    seen = {}
    fake = _fake_boto3(od_value=0.0, spot_value=64.0, seen=seen)
    with mock.patch.dict(sys.modules, {"boto3": fake}):
        r = quota_check.build_quota_report(region="us-west-2", live=True)
    # the live boto3 path really ran — but only against the mock
    assert seen["service"] == "service-quotas"
    assert seen["region"] == "us-west-2"
    assert seen["service_codes"] == ["ec2", "ec2"]
    assert r["mode"] == "live"
    assert r["source"] == "AWS Service Quotas (live)"
    assert r["quotas"]["on_demand_g_vt"]["current_vcpus"] == 0.0
    assert r["quotas"]["spot_g_vt"]["current_vcpus"] == 64.0
    assert r["blocker"] is True                # G/VT On-Demand vCPU == 0
    assert "Spot Fleet g6.24xlarge" in r["recommendation"]


def test_live_path_reports_headroom_when_quota_nonzero():
    seen = {}
    fake = _fake_boto3(od_value=128.0, spot_value=256.0, seen=seen)
    with mock.patch.dict(sys.modules, {"boto3": fake}):
        r = quota_check.build_quota_report(region="us-east-1", live=True)
    assert r["quotas"]["on_demand_g_vt"]["current_vcpus"] == 128.0
    assert r["blocker"] is False
    assert "headroom" in r["recommendation"].lower()


def test_live_without_boto3_falls_back_to_baseline():
    # None in sys.modules makes `import boto3` raise ImportError.
    with mock.patch.dict(sys.modules, {"boto3": None}):
        r = quota_check.build_quota_report(region="us-east-1", live=True)
    assert "boto3 not installed" in r["mode"]
    assert r["blocker"] is True                # baseline still shows the quota-0 blocker


def test_cli_entry_points_return_zero():
    assert quota_check.main(["--dry-run"]) == 0
    assert quota_check.main(["--json"]) == 0
    assert quota_check.main([]) == 0
