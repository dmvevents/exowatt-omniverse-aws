# Exowatt Omniverse digital twin on AWS

*An AWS + NVIDIA POC scaffold: an agentic Bedrock workflow that stands up NVIDIA
Omniverse on an AWS GPU host and renders Exowatt's physics-based digital twin of
their P3 solar + thermal-battery system.*

Two things get delivered here:

1. **An agentic standup workflow** — a Claude Code + Bedrock agent that runs
   quota-check -> provision a g6e GPU host -> install Omniverse Kit headless ->
   launch a first scene, all from plain language.
2. **The Omniverse render layer** for the digital twin — USD geometry with
   Exowatt's simulation output bound to it, rendered headless on the host.

> **The boundary that shapes everything:** Omniverse is the **rendering layer**.
> Exowatt runs their **own physics simulation** (thermodynamic / energy-balance)
> on Titan; we render its output and provide the infrastructure. We do not own,
> run, or size the physics. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

> **Status:** private customer-engagement POC. Every offline plan runs with no
> AWS spend and no GPU; the live steps (launch, install, render) are gated,
> documented human checkpoints. Nothing here spends money on its own.

## What you get in ~1 second, $0

```bash
git clone git@github.com:dmvevents/exowatt-omniverse-aws.git && cd exowatt-omniverse-aws
python3 -m venv .venv && source .venv/bin/activate   # Python 3.11+
make verify     # offline harness self-test: no AWS, no GPU, no spend
make plan       # print all four standup plans (quota, provision, Omniverse, scene)
```

`make verify` validates the four standup plans offline (standard library only —
no dependencies to install). If it is not green, see
[docs/SETUP-GUIDE.md](docs/SETUP-GUIDE.md).

## How the customer uses it

An Exowatt engineer talks to a **Claude Code session on AWS Bedrock** in plain
language ("check the quota and stand up Omniverse on a g6e") and the agent drives
the standup end to end via the `omniverse-g6e-standup` skill. They can drive it
from their own laptop over SSH — Windows engineers via
[.claude/skills/windows-wsl-setup](.claude/skills/windows-wsl-setup/SKILL.md).

## Repo layout

```
CLAUDE.md           agent operating manual (house rules, skills, folder map)
AGENTS.md           how a cold agent drives the repo from a conversation
Makefile            offline tasks: make verify / plan / quota / provision / omniverse / scene
harness/            the standup: quota_check, provision_g6e, omniverse_setup,
                    first_scene, selftest (offline-first, live paths are gated TODOs)
agent/              tracked agent loop: loop.sh launcher, AUTOPILOT.md mission,
                    laptop-connect.sh (laptop agent -> EC2 over SSH), demo-two-agents.sh
.claude/skills/     10 skills:
                    omniverse-g6e-standup, physx-render-bridge,
                    first-scene-hello-omniverse, bedrock-setup,
                    claude-code-on-bedrock, windows-wsl-setup, ngc-api-key,
                    data-onboarding, run-workshop, agent-loop
.claude/hooks/      session hooks (standup state + intent routing) + settings.json
docs/               POC-PLAN, SETUP-GUIDE, ARCHITECTURE, WORKSHOP-AGENDA,
                    TWO-AGENT-SETUP, HARNESS-DEPLOY
.github/            CODEOWNERS, PR + issue templates, verify workflow (offline CI)
```

## Where to go next

| Your goal | Read |
|---|---|
| Understand the digital-twin architecture + the render-only boundary | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| See the POC plan, milestones, people, blockers | [docs/POC-PLAN.md](docs/POC-PLAN.md) |
| Run the Exowatt x AWS working session | [docs/WORKSHOP-AGENDA.md](docs/WORKSHOP-AGENDA.md) |
| Set up prerequisites (quota, Bedrock, IAM, SSH, GitHub) | [docs/SETUP-GUIDE.md](docs/SETUP-GUIDE.md) |
| Run the standup as an agent | [.claude/skills/omniverse-g6e-standup](.claude/skills/omniverse-g6e-standup/SKILL.md) |
| Understand the harness (quota / provision / install / scene) | [harness/README.md](harness/README.md) |
| Run the tracked agent loop | [agent/README.md](agent/README.md), then [CLAUDE.md](CLAUDE.md) |
| Connect a laptop agent to the EC2 (incl. Windows/WSL) | [.claude/skills/windows-wsl-setup](.claude/skills/windows-wsl-setup/SKILL.md) |
| Run it as two agents (laptop + EC2 jump box) | [docs/TWO-AGENT-SETUP.md](docs/TWO-AGENT-SETUP.md) |
| See why the single g6e host uses the loop, not the agentic-harness | [docs/HARNESS-DEPLOY.md](docs/HARNESS-DEPLOY.md) |

## Make targets

```
make verify         offline harness self-test (what CI runs; no AWS, no GPU)
make plan           print all four standup plans
make quota          GPU (G/VT) vCPU quota check (offline baseline)
make provision      the on-demand g6e.4xlarge launch plan
make provision-spot the Spot Fleet g6.24xlarge fallback plan
make omniverse      the headless Omniverse Kit install plan
make scene          the "hello Omniverse" USD scene target
make clean          remove __pycache__ and scratch artifacts
```

## Caveats

This is POC scaffolding, not production code. Honesty notes that travel with
every customer conversation:

- The **On-Demand G/VT vCPU quota is 0** on this org today — the real blocker. An
  increase to 128 vCPUs is submitted (JC Yang monitoring); Spot Fleet
  g6.24xlarge is the interim fallback.
- The harness **plans and validates**; it does not launch instances, install on
  a host, or render frames. Those are gated TODOs — no fabricated results.
- Omniverse is the **render layer only**. Exowatt owns the physics (Titan). We
  do not size PhysX.
- Instance guidance (g6e.4xlarge L40S; g7e/g6e) is directional; confirm current
  specs against the AWS EC2 instance-types page before a live launch.

## Contributing / help / license

See [CONTRIBUTING.md](CONTRIBUTING.md), [SUPPORT.md](SUPPORT.md), and
[SECURITY.md](SECURITY.md). License: [LICENSE](LICENSE) — private
customer-engagement POC, named-personnel access only at Exowatt / AWS / NVIDIA.
