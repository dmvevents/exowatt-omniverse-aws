#!/usr/bin/env python3
"""provision_g6e.py — the plan to stand up the Omniverse GPU host.

Primary: an On-Demand g6e.4xlarge (NVIDIA L40S) — the recommended Omniverse
instance. NVIDIA-recommended alternatives for RTX / ray tracing:
g7e.xlarge or g6e.xlarge. Fallback while the On-Demand G/VT quota is 0: a Spot
Fleet request for g6.24xlarge.

This module CODES THE PLAN. It does not launch anything. The live path
(actual RunInstances / RequestSpotFleet) is a gated human checkpoint and is
left as an explicit TODO — no fabricated instance IDs, no fabricated results.
"""
from __future__ import annotations

import argparse
import json

# Instance options for the single-host Omniverse standup. GPU notes are from
# the engagement; verify current specs against the AWS
# EC2 instance-types page before a live launch.
INSTANCE_OPTIONS = {
    "g6e.4xlarge": {"vcpus": 16, "gpu": "1x NVIDIA L40S", "role": "recommended Omniverse host"},
    "g6e.xlarge":  {"vcpus": 4,  "gpu": "1x NVIDIA L40S", "role": "NVIDIA-recommended (RTX/ray tracing), smaller"},
    "g7e.xlarge":  {"vcpus": 4,  "gpu": "NVIDIA RTX-class (newer gen)", "role": "NVIDIA-recommended (RTX/ray tracing)"},
    "g6.24xlarge": {"vcpus": 96, "gpu": "4x NVIDIA L4", "role": "Spot Fleet interim fallback (quota-0 workaround)"},
}

DEFAULT_ONDEMAND = "g6e.4xlarge"
DEFAULT_SPOT = "g6.24xlarge"


def build_launch_plan(strategy: str = "ondemand",
                      instance_type: str | None = None,
                      region: str = "us-east-1") -> dict:
    """Return the launch plan for the chosen strategy — inspectable, not executed."""
    strategy = strategy.lower()
    if strategy not in ("ondemand", "spot"):
        raise ValueError(f"strategy must be 'ondemand' or 'spot', got {strategy!r}")

    if instance_type is None:
        instance_type = DEFAULT_ONDEMAND if strategy == "ondemand" else DEFAULT_SPOT
    if instance_type not in INSTANCE_OPTIONS:
        raise ValueError(f"unknown instance type {instance_type!r}; "
                         f"known: {sorted(INSTANCE_OPTIONS)}")

    spec = INSTANCE_OPTIONS[instance_type]
    plan: dict = {
        "strategy": strategy,
        "region": region,
        "instance_type": instance_type,
        "instance_spec": spec,
        # Placeholders the operator fills at launch time; kept null so nothing
        # is fabricated. The DLAMI GPU AMI id is region-specific.
        "image_id": "TODO: NVIDIA GPU-optimized / DLAMI AMI id for this region",
        "key_name": "TODO: EC2 key pair name (see docs/SETUP-GUIDE.md, SSH keys)",
        "subnet_id": "TODO: private subnet id",
        "security_group_ids": ["TODO: SG allowing SSH/SSM from operator only"],
        "iam_instance_profile": "TODO: role with Bedrock + ServiceQuotas + SSM",
        "block_device_root_gb": 512,  # Omniverse Kit + USD assets need headroom
        "tags": {"Project": "exowatt-omniverse-aws", "POC": "true"},
    }

    if strategy == "ondemand":
        plan["api"] = "ec2:RunInstances"
        plan["run_instances_params"] = {
            "ImageId": plan["image_id"],
            "InstanceType": instance_type,
            "MinCount": 1,
            "MaxCount": 1,
            "KeyName": plan["key_name"],
            "SubnetId": plan["subnet_id"],
            "SecurityGroupIds": plan["security_group_ids"],
            "BlockDeviceMappings": [{
                "DeviceName": "/dev/sda1",
                "Ebs": {"VolumeSize": plan["block_device_root_gb"], "VolumeType": "gp3"},
            }],
        }
        plan["precondition"] = (
            "On-Demand G/VT vCPU quota must be > 0 for this region "
            "(quota_check.py). If it is 0, use --strategy spot."
        )
    else:  # spot
        plan["api"] = "ec2:RequestSpotFleet"
        plan["spot_fleet_note"] = (
            "Interim fallback while the On-Demand G/VT quota increase is pending. "
            "Spot capacity for g6.24xlarge is not guaranteed; expect interruptions."
        )
        plan["spot_fleet_request_config"] = {
            "AllocationStrategy": "capacityOptimized",
            "TargetCapacity": 1,
            "LaunchSpecifications": [{
                "InstanceType": instance_type,
                "ImageId": plan["image_id"],
                "SubnetId": plan["subnet_id"],
            }],
            "IamFleetRole": "TODO: aws-ec2-spot-fleet-tagging-role ARN",
        }

    plan["live_launch"] = (
        "TODO (gated human checkpoint): executing this plan spends money and is "
        "NOT implemented here. Confirm quota, AMI, subnet, SG, and key, then run "
        "the launch by hand or wire boto3 behind an explicit --i-understand-costs flag."
    )
    return plan


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Plan the Omniverse GPU host launch (does not execute).")
    ap.add_argument("--strategy", choices=["ondemand", "spot"], default="ondemand")
    ap.add_argument("--instance-type", default=None,
                    help=f"override; known: {sorted(INSTANCE_OPTIONS)}")
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan (default). Live launch is intentionally not implemented.")
    ap.add_argument("--run", action="store_true",
                    help="refuse: live launch is a gated human checkpoint, not automated here")
    args = ap.parse_args(argv)

    if args.run:
        print("REFUSED: live launch is a gated human checkpoint and is not "
              "implemented (see the 'live_launch' TODO). Confirm quota + inputs first.")
        return 3

    plan = build_launch_plan(strategy=args.strategy,
                             instance_type=args.instance_type,
                             region=args.region)
    if args.json:
        print(json.dumps(plan, indent=2))
        return 0

    spec = plan["instance_spec"]
    print(f"Provision plan — {plan['strategy']} — {plan['instance_type']} "
          f"({spec['vcpus']} vCPUs, {spec['gpu']}) in {plan['region']}")
    print(f"  role: {spec['role']}")
    print(f"  API : {plan['api']}")
    if plan["strategy"] == "ondemand":
        print(f"  precondition: {plan['precondition']}")
    else:
        print(f"  note: {plan['spot_fleet_note']}")
    print(f"  live launch: {plan['live_launch']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
