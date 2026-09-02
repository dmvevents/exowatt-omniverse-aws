# Working-session agenda — Exowatt × AWS Omniverse digital twin

> Read this when running the Exowatt working session. This is the customer-facing
> agenda of record; the plan behind it is [`docs/POC-PLAN.md`](POC-PLAN.md), the
> target shape and the render-only boundary are in
> [`docs/ARCHITECTURE.md`](ARCHITECTURE.md), and the prerequisites are in
> [`docs/SETUP-GUIDE.md`](SETUP-GUIDE.md).
>
> The through-line is the **agentic Omniverse standup**: a Claude Code + Bedrock
> agent runs quota-check → provision a g6e GPU host → install Omniverse Kit
> headless → render a first scene, all from plain language — then we bring
> Kamel's geometry and Titan result fields in. **Omniverse is the render layer
> only; Exowatt owns the physics (Titan).** The facilitator run book is
> [`.claude/skills/run-workshop/SKILL.md`](../.claude/skills/run-workshop/SKILL.md).

A focused working session (screen-share or in person) with Exowatt's engineering
lead and the AWS team. The goal is to move from "the standup workflow is scaffolded"
to "we agree the digital-twin architecture, the capacity path is clear, and the
agentic standup + first-scene path is demonstrated" — so the first live g6e render
is unblocked the moment capacity lands.

## Attendees

| Role | Org | Present | Why |
|------|-----|---------|-----|
| Kamel Boussaid (engineering lead) | Exowatt | required | Primary hands-on contact; owns the Titan physics sim + the geometry to ingest |
| Jingchao "JC" Yang (Solutions Architect) | AWS | required | Pulled the specialist in; owns/monitors the g6e capacity + quota path |
| Anton Alexander (NVIDIA specialist) | AWS | required | Drives the session; owns Omniverse + the agentic standup |
| Robert Harris-Crawford (account / spec) | AWS | optional | Account + spec-requirements context |
| John (NVIDIA) | NVIDIA | optional | EC2/GPU instance-spec guidance (g6e/g7e, L40S) |

## Prerequisites — how we connect on the day

The offline harness (`make verify`, `make plan`) needs **no AWS account and no
GPU** — it validates the four standup plans (quota, provision, Omniverse, scene)
with the standard library only, no spend. The live steps (launch, install,
render) are gated human checkpoints. Customer prerequisites — direct **Bedrock
access**, SSH keys, GitHub, Claude Code on WSL for Windows engineers — are in
[`docs/SETUP-GUIDE.md`](SETUP-GUIDE.md). The session is driven as **two
cooperating agents** (laptop agent + EC2 jump-box agent that provisions and
drives the g6e host); wiring is in
[`docs/TWO-AGENT-SETUP.md`](TWO-AGENT-SETUP.md), and why this single host uses the
tracked loop rather than the standalone harness is in
[`docs/HARNESS-DEPLOY.md`](HARNESS-DEPLOY.md).

## Agenda — working session

**Block 1 — Goals (15 min)**
- Session goals in one slide: agree the architecture + the render-only boundary,
  confirm the capacity path, demonstrate the agentic standup + first-scene path,
  and agree the data-ingestion roadmap.
- Frame the subject: a physics-based **digital twin of Exowatt's P3 solar +
  thermal-battery system**.

**Block 2 — Digital-twin architecture: Titan physics + Omniverse render layer (35 min)**
- Walk [`docs/ARCHITECTURE.md`](ARCHITECTURE.md): **Exowatt runs the physics
  simulation** (thermodynamic / energy-balance model of the P3 system) on
  **Titan**; **Omniverse is the rendering layer** bound to USD geometry with the
  Titan result fields overlaid. AWS provisions the GPU host and the render layer;
  we do not own, run, or size the physics (not PhysX).
- Confirm the boundary out loud — it shapes every downstream decision.

**Block 3 — g6e / L40S capacity status (20 min)**
- Status as of this session: the **G/VT On-Demand vCPU quota is cleared to 128**
  (8× g6e.4xlarge L40S) — quota is no longer the blocker. The live blocker is now
  **g6e/L40S capacity availability** in region.
- Interim path: **Spot Fleet g6.24xlarge** (already exercised as the fallback);
  a capacity block / on-demand capacity reservation is the durable path. See
  milestone 2 in [`docs/POC-PLAN.md`](POC-PLAN.md) and the quota steps in
  [`docs/SETUP-GUIDE.md`](SETUP-GUIDE.md).
- RUN (offline baseline): `make quota` and `make provision` /
  `make provision-spot` (the launch plans; `harness/quota_check.py` +
  `harness/provision_g6e.py` — no instances launched).

**Block 4 — Agentic Omniverse standup + first-scene demo (40 min)**
- Walk the standup the agent drives end to end from plain language:
  quota-check → provision g6e → install Omniverse Kit headless → render the
  "hello Omniverse" scene. Surfaces: the
  [`omniverse-g6e-standup`](../.claude/skills/omniverse-g6e-standup/SKILL.md) and
  [`first-scene-hello-omniverse`](../.claude/skills/first-scene-hello-omniverse/SKILL.md)
  skills, `harness/omniverse_setup.py`, and
  [`harness/first_scene.py`](../harness/first_scene.py).
- RUN (offline plans): `make plan` (all four standup plans), then `make omniverse`
  and `make scene` (the install + `hello_exowatt.usd` scene targets).
- Honesty rail: the harness **plans and validates**; the live launch/install/render
  are gated checkpoints — no fabricated frames or launches.

**Block 5 — Real-data ingestion + sim-vs-actual roadmap (25 min)**
- The path from first scene to digital twin (POC-PLAN milestones 6–7): ingest
  Kamel's Python / CFD / CAD geometry into USD, then overlay a **Titan result
  field** via the
  [`physx-render-bridge`](../.claude/skills/physx-render-bridge/SKILL.md) skill;
  onboarding via [`data-onboarding`](../.claude/skills/data-onboarding/SKILL.md).
- The digital-twin loop: a **synthetic-design field now**, **real-system data
  later**, rendering the **sim-vs-actual delta** (see
  [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)).
- Capture from Kamel: the geometry format, the Titan output field schema, and
  the NVIDIA EC2-spec guidance + a rough architecture diagram.

**Block 6 — Next steps & owners (5 min)**
- Confirm owners/dates: capacity path (JC); Kamel to send the geometry + Titan
  field schema + the NVIDIA spec guidance; the first live g6e launch as a human
  checkpoint.
- Set the next milestone date on the calendar.

## Success criteria — what "session succeeded" means

By the end of the session, all of the following are TRUE:

1. **The render-only boundary is confirmed** — Exowatt owns Titan physics;
   Omniverse renders.
2. **The capacity status is clear** — quota cleared to 128; the g6e/L40S capacity
   path (Spot interim, capacity reservation durable) is agreed.
3. **The agentic standup was walked** and the four plans validated offline (`make plan`).
4. **The first-scene path was demonstrated** (offline `make scene`), with the live
   render as a named gated checkpoint.
5. **The data-ingestion roadmap is agreed** — geometry + Titan field, then
   sim-vs-actual.
6. **Next steps have named owners and dates**, and the next milestone is on the calendar.

## What Exowatt takes away

- The scaffold + `make verify` / `make plan` to re-run the standup plans at $0.
- The render-only boundary written down so scope stays clear.
- A capacity path (Spot interim → capacity reservation) and an ingestion roadmap.

## What AWS takes away

- Kamel's geometry format + Titan result-field schema to wire the render bridge.
- The NVIDIA EC2-spec confirmation and a rough architecture diagram.
- The capacity path to unblock the first live g6e render.

## Logistics

- Format: focused working session, screen-share or in person.
- Setup: projector/second screen for architecture + terminal in parallel; SSH
  egress to the jump box for the live path (offline `make` covers a blocked network).
- Recording: optional; AWS owns the clip, Exowatt reviews before any external share.

## Pre-read (~35 min, send 5 days ahead)

1. [`README.md`](../README.md) — what the repo is + the render-only boundary (10 min).
2. [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) — the digital-twin architecture (15 min).
3. [`docs/POC-PLAN.md`](POC-PLAN.md) — milestones, people, blockers (10 min).

## After the session

Within 5 business days:
- AWS sends a session summary (~2 pages) with the action list and owners.
- Kamel sends the geometry + Titan field schema + the NVIDIA EC2-spec guidance.
- AWS confirms the capacity path and the first-launch checkpoint date.

Once capacity lands:
- Provision the g6e host, install Omniverse Kit headless, and render
  `hello_exowatt.usd` on the host — the first live proof point (POC-PLAN milestones 3–5).

## Next steps

- Plan + milestones: [`docs/POC-PLAN.md`](POC-PLAN.md)
- Prerequisites (quota / Bedrock / IAM / SSH / GitHub): [`docs/SETUP-GUIDE.md`](SETUP-GUIDE.md)
- Two-agent connect: [`docs/TWO-AGENT-SETUP.md`](TWO-AGENT-SETUP.md)
