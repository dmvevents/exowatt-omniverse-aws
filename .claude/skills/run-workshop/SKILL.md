---
name: run-workshop
description: Use when facilitating, rehearsing, or preparing the Exowatt standup session with Kamel — the preflight checks, the per-beat run commands, and the recovery moves when something fails live (quota-0, no GPU, Bedrock down).
---

# Run the standup session end-to-end

The plan of record: `docs/POC-PLAN.md` (the milestones) and
`docs/SETUP-GUIDE.md` (the prerequisites). The session is one arc: **prove the
pattern offline -> stand up the GPU host -> get the first scene rendering** with
Kamel Boussaid (Exowatt engineering lead).

## T-minus-1-day preflight (all must pass; run in order)

```bash
# 1. Fresh clone in a clean venv — this is what failure in the room looks like
git clone git@github.com:dmvevents/exowatt-omniverse-aws.git ./scratch/preflight && cd ./scratch/preflight
python3 -m venv .venv && source .venv/bin/activate               # any Python 3.11+
make verify                    # offline harness self-test, ~1 s, no AWS, no GPU

# 2. The plans the room will see (all offline)
make plan                      # quota + provision (on-demand + spot) + omniverse + scene
agent/demo-two-agents.sh both  # the narrated provisioning-agent + render-agent demo

# 3. The live prerequisites (do NOT do these live for the first time)
#    - Bedrock converse smoke -> "verified"        (see bedrock-setup skill)
#    - G/VT quota: python3 harness/quota_check.py --live   (is the increase approved yet?)
#    - SSH to the g6e host works (once it exists)   (see windows-wsl-setup / SETUP-GUIDE)
```

## Per-beat commands (facilitator crib)

| Beat | What runs | Command |
|---|---|---|
| 1 - Prove the pattern | offline two-agent demo | `agent/demo-two-agents.sh both` |
| 2 - Quota reality | is there GPU headroom, or the blocker? | `python3 harness/quota_check.py --live` |
| 3 - Provision plan | the g6e launch (or Spot fallback) plan | `make provision` ; `make provision-spot` |
| 4 - Install Omniverse | headless Kit steps on the host | `make omniverse` then run them over SSH on the host |
| 5 - First scene | the "hello Omniverse" USD target | `make scene` then author it in Kit on the host |

Stage any customer CAD/CFD/Python under `scratch/uploads/` — never commit it.
The offline plans (`make plan`) are the fallback whenever a live call or the
GPU host misbehaves.

## When it breaks live (recovery moves, in order)

1. **On-Demand quota still 0** -> switch to the Spot Fleet fallback
   (`make provision-spot`); narrate that this is interim while the increase
   clears (JC Yang is monitoring).
2. **No GPU host yet** -> run the offline plans (`make plan`) and narrate "same
   flow, no cloud touched"; the room still sees the shape.
3. **Bedrock `AccessDeniedException`** -> model-access grant missing; the
   converse smoke (bedrock-setup) is the 5-second triage.
4. **NGC pull fails on the host** -> re-login with `$oauthtoken` (ngc-api-key);
   or pull from the ECR mirror.
5. **Wifi dead** -> everything through `make verify` / `make plan` is offline by
   design.

## Honesty rules in the room

- Never present a dry-run plan as a live result. Name the mode on every run.
- The quota-0 blocker is real; say so plainly and show the fallback.
- Omniverse renders Exowatt's own Titan physics output — we do not model the
  thermodynamics, and we do not size PhysX.
