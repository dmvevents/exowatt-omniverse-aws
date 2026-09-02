# harness/ — stand up one Omniverse GPU host, agentically

This is a deliberately small harness: **a single g6e EC2 host running NVIDIA
Omniverse**, not a GPU/Kubernetes cluster framework. Exowatt's digital twin
needs one render host, not a fleet scheduler.

Four steps, each a pure planning module you can inspect offline:

```
harness/
  quota_check.py     is there GPU (G/VT) vCPU headroom, or the quota-0 blocker?
  provision_g6e.py   the RunInstances g6e.4xlarge / g7e plan, or Spot g6.24xlarge fallback
  omniverse_setup.py the headless Omniverse Kit install steps on that host
  first_scene.py     the target "hello Omniverse" USD scene (the POC proof)
  selftest.py        the offline check `make verify` runs (stdlib only)
```

## Run the plans offline

```bash
python3 harness/quota_check.py --dry-run       # or --live (needs boto3 + creds)
python3 harness/provision_g6e.py --dry-run     # --strategy spot for the fallback
python3 harness/omniverse_setup.py --plan
python3 harness/first_scene.py --dry-run
python3 harness/selftest.py                    # what `make verify` runs
```

## Design rules (why this is safe to run anywhere)

- **Offline-first.** Every module is pure standard library; `boto3` is
  imported lazily and only for the `--live` quota read. `make verify` needs no
  dependencies, no network, no GPU, and spends nothing.
- **Nothing is fabricated.** Provisioning, install, and scene authoring have
  real, live effects (cost, on-host changes, rendered frames). Those paths are
  **gated TODOs**: they print the plan and refuse to execute (`--run` exits
  non-zero). No fake instance IDs, no fake render results.
- **The blocker is first-class.** `quota_check` encodes the real engagement
  state: On-Demand G/VT vCPU quota is 0, increase to 128 vCPUs submitted (JC
  Yang monitoring), Spot Fleet g6.24xlarge as the interim fallback.
- **Render layer only.** `omniverse_setup` and `first_scene` stand up the
  *rendering* layer. Exowatt runs its own physics simulation on Titan; we do
  not own or size PhysX. See [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

## The live path (when quota clears)

1. `quota_check.py --live` shows On-Demand G/VT > 0.
2. Fill the `TODO` inputs in the `provision_g6e` plan (AMI, subnet, SG, key,
   instance profile) and launch by hand — the first RunInstances is a human
   checkpoint (see [../agent/AUTOPILOT.md](../agent/AUTOPILOT.md)).
3. SSH to the host and run the `omniverse_setup` steps.
4. Author `first_scene` inside Kit; the saved `.usd` is the POC proof.
