#!/usr/bin/env python3
"""quota_check.py — is there GPU headroom on this account, or the quota-0 blocker?

Reads the AWS Service Quotas that gate GPU EC2 launches for the Exowatt
Omniverse standup.

The real blocker on this engagement: the org's
On-Demand G/VT vCPU quota is 0, so a g6.8xlarge (32 vCPUs) launch fails with
VcpuLimitExceeded. A quota increase to 128 vCPUs is submitted (Jingchao "JC"
Yang monitoring), enough for 8x g6e.4xlarge (16 vCPUs each = the L40S
Omniverse instance). Spot Fleet g6.24xlarge is the interim fallback.

Offline by default: with no --live flag (or no boto3 installed) it returns the
known engagement baseline so the plan is inspectable with zero AWS calls. With
--live plus boto3 and credentials it queries Service Quotas for the real
current values.
"""
from __future__ import annotations

import argparse
import json

# AWS Service Quotas codes that gate GPU EC2 launches (service code "ec2").
# Verify against the account: aws service-quotas get-service-quota \
#   --service-code ec2 --quota-code <code> --region <region>
ON_DEMAND_G_VT = "L-DB2E81BA"  # Running On-Demand G and VT instances (vCPUs)
SPOT_G_VT = "L-3819A6DF"       # All G and VT Spot Instance Requests (vCPUs)

# The recommended Omniverse instance for this engagement and its vCPU cost.
RECOMMENDED_INSTANCE = "g6e.4xlarge"   # NVIDIA L40S
RECOMMENDED_VCPUS_EACH = 16
TARGET_FLEET = 8                       # 8 x 16 = 128 vCPUs (the requested increase)


def build_quota_report(region: str = "us-east-1", live: bool = False) -> dict:
    """Return the GPU-quota picture for `region`.

    Offline (live=False): the known engagement baseline. Live: real values
    from AWS Service Quotas (requires boto3 + credentials). Never raises on a
    missing dependency — falls back to the baseline and records why.
    """
    report = {
        "region": region,
        "mode": "live" if live else "offline-baseline",
        "recommended_instance": RECOMMENDED_INSTANCE,
        "target_fleet_vcpus": RECOMMENDED_VCPUS_EACH * TARGET_FLEET,
        "quotas": {
            "on_demand_g_vt": {
                "code": ON_DEMAND_G_VT,
                "name": "Running On-Demand G and VT instances (vCPUs)",
                "current_vcpus": 0,          # baseline: the real blocker
                "requested_vcpus": 128,      # increase submitted (JC monitoring)
                "status": "increase submitted",
            },
            "spot_g_vt": {
                "code": SPOT_G_VT,
                "name": "All G and VT Spot Instance Requests (vCPUs)",
                "current_vcpus": None,       # unknown offline; check --live
                "note": "Spot Fleet g6.24xlarge is the interim fallback",
            },
        },
        "source": "engagement baseline; run --live to refresh",
    }

    if live:
        try:
            import boto3  # lazy: only needed for the live path
        except ImportError:
            report["mode"] = "offline-baseline (boto3 not installed)"
        else:
            sq = boto3.client("service-quotas", region_name=region)
            for key, code in (("on_demand_g_vt", ON_DEMAND_G_VT),
                              ("spot_g_vt", SPOT_G_VT)):
                try:
                    resp = sq.get_service_quota(ServiceCode="ec2", QuotaCode=code)
                    value = resp["Quota"]["Value"]
                    report["quotas"][key]["current_vcpus"] = value
                except Exception as exc:  # noqa: BLE001 - report, do not crash
                    report["quotas"][key]["error"] = f"{type(exc).__name__}: {exc}"
            report["source"] = "AWS Service Quotas (live)"

    od = report["quotas"]["on_demand_g_vt"].get("current_vcpus")
    report["blocker"] = (od == 0)
    if report["blocker"]:
        report["recommendation"] = (
            "On-Demand G/VT vCPU quota is 0 -> cannot launch g6e/g6 on demand. "
            "Push the pending increase to 128 vCPUs; meanwhile provision the "
            "host via Spot Fleet g6.24xlarge (see provision_g6e.py --strategy spot)."
        )
    else:
        need = report["target_fleet_vcpus"]
        report["recommendation"] = (
            f"On-Demand G/VT headroom present ({od} vCPUs). Target fleet needs "
            f"{need} vCPUs for {TARGET_FLEET}x {RECOMMENDED_INSTANCE}."
        )
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check GPU (G/VT) vCPU quotas for the Omniverse standup.")
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--live", action="store_true",
                    help="query AWS Service Quotas (needs boto3 + credentials); default is offline baseline")
    ap.add_argument("--json", action="store_true", help="emit the raw report as JSON")
    # --dry-run is accepted as a no-op alias (offline is already the default).
    ap.add_argument("--dry-run", action="store_true", help="offline baseline (default behavior)")
    args = ap.parse_args(argv)

    report = build_quota_report(region=args.region, live=args.live)
    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"GPU quota check — region {report['region']} ({report['mode']})")
    for key, q in report["quotas"].items():
        cur = q.get("current_vcpus")
        cur_s = "unknown" if cur is None else f"{cur:g} vCPUs"
        print(f"  {q['name']} [{q['code']}]: {cur_s}")
        if q.get("error"):
            print(f"    ! {q['error']}")
    print(f"blocker: {'YES' if report['blocker'] else 'no'}")
    print(f"-> {report['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
