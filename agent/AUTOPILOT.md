# AUTOPILOT — the standing mission

You were started by `agent/loop.sh` inside a tracked tmux session. Your
transcript is being kept. Execute this mission autonomously, stopping only at
the human checkpoints below.

## Mission

Stand up the Omniverse render host for Exowatt's digital twin, plan-first:

1. **Baseline** — `make verify`. If not green, fixing it IS the mission; stop
   and report if you cannot.
2. **Quota** — run the `omniverse-g6e-standup` skill's first step: check the
   G/VT vCPU quota (`harness/quota_check.py`). If the On-Demand quota is 0
   (the known blocker), note it and plan the Spot Fleet g6.24xlarge fallback.
3. **Provision plan** — produce the launch plan (`harness/provision_g6e.py`)
   for g6e.4xlarge on-demand, and the Spot fallback. Do NOT launch — the first
   live RunInstances is a human checkpoint (below).
4. **Install + scene plan** — produce the headless Omniverse Kit install plan
   (`harness/omniverse_setup.py`) and the first-scene target
   (`harness/first_scene.py`).
5. **Report** — write `scratch/agent-runs/REPORT-<UTC-date>.md`: what ran, the
   plans produced (paths + key values), the quota verdict, any failures
   verbatim, and the exact next human action.

## Human checkpoints (STOP and ask; do not proceed on silence)

- **Live AWS spend**: the first non-dry-run call of this session — any
  RunInstances / RequestSpotFleet, or turning on a running GPU host. Show the
  exact plan and expected cost class first.
- **Anything leaving the machine**: git push, publishing links, sending
  messages/emails, uploading customer CAD/CFD/Python.
- **Anything destructive**: terminating instances, deleting volumes, killing
  other tmux sessions. (Archiving with a timestamp is allowed without asking.)

## Rules while operating

- Plan/dry-run before live, always. Name the mode in every report line.
- Evidence before claims: a step is done when its artifact exists (the plan
  JSON, green `make verify`, a saved `.usd`), never before.
- Customer inputs (CAD/CFD/Python) stay in `scratch/` — never commit them,
  never echo them into the transcript beyond what the report needs.
- We render Exowatt's own Titan physics output; we do NOT own or size the
  physics sim. Do not fabricate physics results.
- If blocked > 15 minutes on the same error, write the failure state into the
  report and stop cleanly rather than thrash.
- Leave the tmux session alive when finished; end your final message with
  `MISSION COMPLETE` or `MISSION BLOCKED: <reason>`.
