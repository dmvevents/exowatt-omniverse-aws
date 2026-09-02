"""Exowatt Omniverse standup harness.

A deliberately small harness for a single g6e EC2 host running NVIDIA
Omniverse — not a GPU/Kubernetes cluster framework. Four steps:

    quota_check     -> is there GPU headroom, or the On-Demand G/VT quota-0 blocker?
    provision_g6e   -> the RunInstances / Spot Fleet plan for the host
    omniverse_setup -> the headless Omniverse Kit install steps on that host
    first_scene     -> the target "hello Omniverse" USD scene

Every module is offline-first: pure standard library, boto3 imported lazily,
dry-run by default. Cloud-spending and on-host actions are gated TODOs — the
harness plans and validates; it does not fabricate launches or results.
"""

__all__ = ["quota_check", "provision_g6e", "omniverse_setup", "first_scene"]
