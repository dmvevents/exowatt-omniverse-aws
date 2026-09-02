# POC plan — Exowatt Omniverse digital twin on AWS

## Goal

Deliver, for Exowatt, (1) an **Omniverse simulation/visualization project** on
AWS GPU and (2) an **agentic Bedrock workflow that stands up the GPU infra and
kicks off Omniverse** end-to-end. Prove it with Kamel's first scene rendering on
a g6e host, then bring his geometry and Titan result fields in.

## Scope boundary (read `docs/ARCHITECTURE.md` first)

We provision the GPU host, stand up the Omniverse **render layer**, and provide
the agentic workflow. **Exowatt owns the physics simulation** (thermodynamic /
energy-balance model of the P3 system, on Titan). We render their output; we do
not own, run, or size the physics (not native Omniverse Physics, not PhysX).

## People

| Person | Role |
|---|---|
| Kamel Boussaid | Exowatt engineering lead — primary hands-on contact; owns the Titan physics sim |
| Jingchao "JC" Yang | AWS Solutions Architect — monitoring/escalating the quota |
| Robert Harris-Crawford | AWS — account / spec-req |
| Anton Alexander | AWS NVIDIA Specialist — Omniverse + agentic standup |
| Alex Iankoulski | AWS — harness / do-framework owner |

## Milestones

1. **Prerequisites cleared** — customer gets direct **Bedrock access** (their
   engineers Tim/Kamau already use Claude Code + Bedrock); IT-admin doc sent
   (SSH keys, GitHub, Claude Code on WSL + Bedrock, EC2 policies). See
   `docs/SETUP-GUIDE.md`.
2. **Quota cleared** — the **On-Demand G/VT vCPU quota is 0** today (the real
   blocker); increase to 128 vCPUs (8x g6e.4xlarge L40S) submitted, JC
   monitoring. Interim: Spot Fleet g6.24xlarge.
3. **Host provisioned** — a g6e.4xlarge (L40S), or g7e/g6e,
   or the Spot fallback. First live launch is a human checkpoint.
4. **Omniverse up** — headless Omniverse Kit installed on the host.
5. **First scene** — the "hello Omniverse" USD scene renders (the proof point).
6. **Customer content** — ingest Kamel's Python / CFD / CAD into USD; overlay a
   Titan result field (the physics-to-render bridge).
7. **Digital-twin loop** — synthetic-design field now; real-system data later;
   render the sim-vs-actual delta (`docs/ARCHITECTURE.md`).

## Deliverables (in this repo)

- The agentic standup harness (`harness/` + the `omniverse-g6e-standup` skill).
- The render bridge for Exowatt's Titan output (`physx-render-bridge` skill).
- The first-scene proof (`first-scene-hello-omniverse` skill + `harness/first_scene.py`).
- Setup, architecture, and this plan (`docs/`).
- The customer-facing working-session agenda ([WORKSHOP-AGENDA.md](WORKSHOP-AGENDA.md)).

## How the POC is operated

The engagement is driven as **two cooperating agents** — a laptop agent the
operator talks to and an EC2 jump-box agent (Claude Code on Bedrock) that
provisions and drives the g6e render host over SSH. See
[TWO-AGENT-SETUP.md](TWO-AGENT-SETUP.md) for the laptop + jump-box wiring, and
[HARNESS-DEPLOY.md](HARNESS-DEPLOY.md) for why this single g6e host uses
`agent/loop.sh` rather than the standalone agentic-harness.

## Current blockers / open items

- [ ] Customer direct **Bedrock access** (prerequisite to drive from Claude Code).
- [ ] **G/VT On-Demand quota** approval (0 -> 128 vCPUs); use Spot in the meantime.
- [ ] Connect directly with **Kamel** to stand up Omniverse on the host.
- [ ] Kamel to send the NVIDIA EC2-spec guidance + a rough architecture diagram.

## Definition of done (POC window)

`make verify` green; the standup harness plans validated offline; a g6e host
reachable; Omniverse Kit up; `hello_exowatt.usd` rendering on the host; a first
piece of Kamel's geometry rendered from USD. No fabricated launches or results —
every live step is evidenced.
