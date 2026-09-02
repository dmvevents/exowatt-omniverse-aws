# AGENTS.md — how to drive this repo from a conversation

You are an agent an operator (or an Exowatt engineer) talks to in plain
language. They will say things like *"check the quota and stand up Omniverse on
a g6e"*, *"here's a CAD file, get it into the twin"*, or *"draw the first
scene"*, and expect you to **do it end to end** and report with evidence — the
same autonomous loop you're reading this in.

This file is the map. `CLAUDE.md` (repo root) is the standing house rules; the
skills in `.claude/skills/` are the verbs. Read this, then act.

## The one rule: route -> run -> report from evidence

Every request routes to a skill. Invoke it, run the command it gives you, and
narrate from the artifact it produces (a plan JSON, a reachable host, a saved
`.usd`) — never from memory, never from a scraped screen.

| The operator... | Skill to invoke |
|---|---|
| wants to stand up Omniverse on a GPU host (the whole arc) | **`omniverse-g6e-standup`** |
| asks about GPU capacity / the quota | **`omniverse-g6e-standup`** (step 1) |
| provides CAD / CFD / Python to bring into the twin | **`data-onboarding`** |
| wants Exowatt's physics (Titan) output rendered | **`physx-render-bridge`** |
| wants the first scene / a render proof | **`first-scene-hello-omniverse`** |
| needs Bedrock / Claude-on-Bedrock / NGC set up | **`bedrock-setup`**, **`claude-code-on-bedrock`**, **`ngc-api-key`** |
| is on Windows and needs to reach the EC2 agent | **`windows-wsl-setup`** |
| is running/rehearsing the standup session | **`run-workshop`** |
| wants the tracked tmux agent loop | **`agent-loop`** |

## The shape of the system (what you're driving)

```
operator speech
      |
  omniverse-g6e-standup            <- the mission router
      |
  harness/  (python3 harness/...)  <- the verbs, all offline-first
      |- quota_check.py     is there G/VT headroom, or the quota-0 blocker?
      |- provision_g6e.py   the RunInstances g6e / Spot g6.24xlarge plan (live = TODO)
      |- omniverse_setup.py the headless Kit install steps (on-host = TODO)
      |- first_scene.py     the "hello Omniverse" USD target (author in Kit = TODO)
      |
  evidence: plan JSON (--json), green `make verify`, a saved .usd  <- cite these
```

## Non-negotiables (from CLAUDE.md — these override convenience)

1. **Evidence before claims.** A step is done when its artifact exists. Cite the
   path + the exact values. If a command failed, quote the failure — never bluff.
2. **Plan/dry-run before live.** The harness live paths refuse `--run`; the first
   live AWS call (RunInstances / Spot Fleet) is a human checkpoint. Never present
   a dry-run plan as a live result.
3. **Nothing fabricated.** No fake instance IDs, no fake frames, no invented
   physics values. The quota-0 blocker is real — say so.
4. **The boundary is fixed.** Omniverse renders; Exowatt owns the physics
   (Titan). If asked to "size PhysX / the physics workload", redirect: that is
   Exowatt's solver, not ours. We size the render host (g6e).
5. **Customer inputs are confidential.** CAD/CFD/Python stay in `scratch/`
   (gitignored), never committed. The repo is private; publish nothing without a
   human's OK.

## Provider is swappable (Claude/Bedrock today)

The standup runs on Claude Code + Bedrock, but the pattern is
provider-agnostic. The only model seam is the **driving agent** (`agent/loop.sh`
— claude/codex/OSS). The harness itself makes no LLM calls, so the plans are the
same regardless of who drives.

## Running from a laptop agent (two-agent setup)

If you are a coding agent on a **laptop** (not on the EC2), the standup runs on a
remote EC2 host reachable over SSH. Use `agent/laptop-connect.sh`
(`status` / `attach` / `run "<make target>"` / `ask "<nl>"` / `upload <file>`) —
never open a network port. Windows path: the `windows-wsl-setup` skill.

## First moves in a fresh session

```bash
make verify                              # baseline green (offline, no spend)
python3 harness/quota_check.py --dry-run # the known standup blocker
```

Then let the operator's words pick the skill, and drive from evidence.
