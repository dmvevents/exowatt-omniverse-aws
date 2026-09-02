# Exowatt Omniverse standup — agent operating manual

You are an agent working in the Exowatt Omniverse-on-AWS repo. This file is your
standing context. The repo stands up NVIDIA Omniverse on an AWS GPU host and
renders Exowatt's digital twin; read `docs/ARCHITECTURE.md` for the shape.

## What this repo does

An agentic Bedrock workflow (`.claude/skills/omniverse-g6e-standup`, backed by
`harness/`) that takes the standup end to end:

```
quota-check -> provision g6e (or Spot fallback) -> install Omniverse Kit -> first scene
```

Then it renders Exowatt's content: ingest their CAD/CFD/Python as USD
(`data-onboarding`) and overlay their Titan physics output
(`physx-render-bridge`).

**The boundary:** Omniverse is the **rendering layer**. Exowatt owns the physics
simulation (thermodynamic / energy-balance, on Titan). We provision + render; we
do not own, run, or size the physics (not native Omniverse Physics, not PhysX).

## The agent loop

You operate inside a tracked loop (see `agent/README.md`):

- **Every workstream is a named tmux session** whose transcript is kept. If you
  were not started by `agent/loop.sh`, note it.
- **Autonomy between checkpoints.** Work end-to-end without asking, but stop at
  the human gates in `agent/AUTOPILOT.md` (first live AWS spend, data-out,
  git-push, destructive ops).
- **Evidence before claims.** Never say "done" without the artifact: green
  `make verify`, a plan JSON, a reachable host, a saved `.usd`. If a command
  failed, report it verbatim — do not bluff.
- **Capture learnings.** Append non-obvious fixes to the relevant `CLAUDE.md` or
  `README.md` so the next session starts smarter.

## House rules

- `make verify` green before and after any change you commit (offline, no AWS
  spend, no GPU, ~1 s).
- **Plan/dry-run first, then live.** The harness live paths (RunInstances,
  install, render) are gated TODOs that refuse `--run`. The first live AWS call
  is a human checkpoint. Never present a dry-run plan as a live result.
- **Nothing is fabricated.** No fake instance IDs, no fake render frames, no
  invented physics values. Missing = reported missing.
- **Ephemeral work goes in `./scratch/<topic>/`**, never `/tmp`. `scratch/` is
  gitignored; customer CAD/CFD/Python inputs and derived USD live there. Never
  commit them; archive with a timestamp instead of deleting.
- **Secrets stay out of git.** AWS creds via instance role or `~/.aws`; NGC keys
  in env vars. `*.env`, `*.pem`, `*.key` are gitignored. Never paste a key into
  a committed file, a log, or a chat reply.
- **This repo is private.** Anything you publish is private unless a human says
  otherwise.
- Python 3.11+ only.

## Skills (in `.claude/skills/`)

| Skill | Use when |
|---|---|
| `omniverse-g6e-standup` | the primary mission: quota -> provision g6e -> install Kit -> first scene |
| `physx-render-bridge` | bring Exowatt's Titan physics output into Omniverse as a rendered field (we don't own the physics) |
| `first-scene-hello-omniverse` | author the minimal "hello Omniverse" USD scene as the POC proof |
| `bedrock-setup` | stand up Bedrock model access on a new AWS account |
| `claude-code-on-bedrock` | point Claude Code at Bedrock (no Anthropic API key) |
| `windows-wsl-setup` | a Windows engineer needs WSL2 + Claude Code + SSH to the EC2 agent |
| `ngc-api-key` | pull Omniverse Kit containers from nvcr.io on the host |
| `data-onboarding` | the customer provides CAD/CFD/Python; map it toward a USD asset |
| `run-workshop` | facilitating or rehearsing the standup session with Kamel |
| `agent-loop` | starting/joining the tracked tmux agent loop |

## Fast map

| Path | What |
|---|---|
| `harness/` | the four standup steps + the offline `selftest.py` that `make verify` runs |
| `agent/` | the agent loop: `loop.sh`, `AUTOPILOT.md`, `laptop-connect.sh`, `demo-two-agents.sh` |
| `.claude/skills/` | the 10 skills above (the verbs) |
| `.claude/hooks/` | session-start orientation + prompt intent routing |
| `docs/` | POC-PLAN, SETUP-GUIDE, ARCHITECTURE, WORKSHOP-AGENDA, TWO-AGENT-SETUP, HARNESS-DEPLOY |

Start any session with `make verify` (baseline green), then read the folder's
`README.md`/`CLAUDE.md` for wherever you're about to work.
