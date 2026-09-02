---
name: omniverse-g6e-standup
description: Use to stand up NVIDIA Omniverse on an AWS g6e GPU host end-to-end, agentically, from a Claude Code + Bedrock session — quota-check, then provision g6e (or the Spot g6.24xlarge fallback), then install Omniverse Kit headless, then launch the first scene. This is the primary mission of this repo.
---

# Stand up Omniverse on a g6e host (the agentic mission)

The deliverable Exowatt agreed to: a GitHub repo with an
**agentic Bedrock workflow that auto-provisions the GPU host and kicks off
Omniverse**. This skill is that workflow. Four steps, plan-first, each backed by
a `harness/` module. You run this from a Claude Code + Bedrock session (see
`claude-code-on-bedrock`).

## The arc

```
quota-check  ->  provision g6e (or Spot fallback)  ->  install Omniverse Kit  ->  first scene
harness/quota_check.py   harness/provision_g6e.py       harness/omniverse_setup.py  harness/first_scene.py
```

## Step 1 — quota-check (offline, then live)

```bash
python3 harness/quota_check.py --dry-run     # the known baseline
python3 harness/quota_check.py --live        # real value (needs boto3 + creds)
```

The known blocker: **On-Demand G/VT vCPU quota = 0**, so g6e/g6 on-demand
launches fail. A raise to 128 vCPUs (8x g6e.4xlarge L40S) is submitted; JC Yang
is monitoring. If `--live` still shows 0, go to the Spot fallback in Step 2.

## Step 2 — provision the host (plan first; launch is a checkpoint)

```bash
python3 harness/provision_g6e.py --dry-run                 # on-demand g6e.4xlarge (L40S)
python3 harness/provision_g6e.py --strategy spot --dry-run # Spot Fleet g6.24xlarge fallback
```

Fill the `TODO` inputs (AMI, subnet, SG, key, instance profile — see
`docs/SETUP-GUIDE.md`). **The first live RunInstances / RequestSpotFleet is a
human checkpoint** (`agent/AUTOPILOT.md`): show the plan and expected cost
class, then launch by hand. The harness refuses `--run` on purpose.

**g7e-xlarge / g6e-xlarge** are the NVIDIA-recommended alternatives for RTX /
ray tracing — override with `--instance-type` if the account has that capacity.

## Step 3 — install Omniverse Kit headless (on the host, over SSH)

```bash
python3 harness/omniverse_setup.py --plan
```

Then run the steps on the provisioned host: driver check (`nvidia-smi`),
headless GL/Vulkan deps, fetch Kit (needs an `NGC_API_KEY` — see `ngc-api-key`),
headless config, verify. This is the **rendering layer only**.

## Step 4 — first scene (the POC proof)

```bash
python3 harness/first_scene.py --dry-run
```

Author the "hello Omniverse" USD stage inside Kit on the host (see
`first-scene-hello-omniverse`). The saved `.usd` that renders is the proof the
standup works. Then bring Kamel's geometry in (`data-onboarding`) and overlay
his Titan result fields (`physx-render-bridge`).

## Rails

- Plan/dry-run before live; name the mode every time. `make verify` stays green.
- Evidence before claims: a step is done when its artifact exists (plan JSON,
  a reachable host, a saved `.usd`), never before.
- We provision + render; Exowatt owns the physics (Titan). Don't fabricate
  launches, hosts, or results.
