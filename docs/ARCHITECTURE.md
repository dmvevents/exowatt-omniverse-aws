# Architecture — the Exowatt digital twin on AWS

## The one boundary that shapes everything

**Omniverse is the rendering layer. Exowatt owns the physics.**

Kamel's team builds their own physics simulation of the P3 system — a
thermodynamic / energy-balance model (sunlight -> thermal store -> Stirling
engine -> electricity) — and runs it on **Titan**. NVIDIA Omniverse is used
purely to **render and visualize** that simulation's output. We (AWS + NVIDIA)
provide the GPU infrastructure, the Omniverse render layer, and the agentic
workflow that stands both up. We do **not** own, run, or size the physics
(neither native Omniverse Physics / USD Physics nor PhysX).

```
        EXOWATT (owns)                          AWS + NVIDIA (this repo, owns)
  +-------------------------+            +--------------------------------------+
  |  Physics simulation     |  result    |  Omniverse render layer on a g6e host |
  |  (thermo / energy bal.) |  fields    |                                      |
  |  on Titan               | ---------> |  USD geometry  <-- CAD import         |
  |  P3: sun -> store ->    |            |  + bound result field (primvar/color) |
  |  Stirling -> power      |            |  -> headless Kit render / stream      |
  +-------------------------+            +--------------------------------------+
                                                    ^
                                          agentic Bedrock workflow (harness/)
                                          quota -> provision g6e -> install Kit -> scene
```

## The digital-twin data flow (three stages)

The twin matures in three stages. The render layer is the same throughout; what
changes is the source and meaning of the field it renders.

1. **Synthetic-data design stage (now).**
   Exowatt is in design. The physics sim runs on **synthetic / design inputs**.
   Omniverse renders that synthetic result over the design geometry so the team
   can see the system behave before hardware exists. Nothing here claims to be
   measured.

2. **Real-system-data ingestion (later).**
   As the P3 hardware (with partner **Digimatrix**) produces telemetry, that
   **real system data** is ingested as a second field on the same geometry.
   Ingestion is data handling, not physics — see the `data-onboarding` and
   `physx-render-bridge` skills.

3. **Sim-vs-actual delta (the payoff).**
   With both fields on the same twin, the visualization shows the **delta
   between the simulation and the real system** — where the model and the
   hardware agree and where they diverge. That delta is the digital twin's
   product; computing the physics that explains it stays with Exowatt.

## The AWS + NVIDIA layer (what this repo stands up)

- **Compute:** a single **g6e** EC2 host (NVIDIA **L40S**) — the recommended
  Omniverse instance. NVIDIA-recommended alternatives for RTX / ray
  tracing: **g7e-xlarge / g6e-xlarge**. Interim fallback while the On-Demand
  G/VT quota is 0: **Spot Fleet g6.24xlarge**. This is one render host, not a
  cluster — see `harness/`.
- **Render:** **Omniverse Kit** installed headless on that host; optional
  Omniverse streaming for a remote viewport. USD is the scene format.
- **Ingest:** CAD (STEP/STL/OBJ) -> USD; CFD / result fields -> bound primvars.
- **Drive:** a **Claude Code + Bedrock** agent runs the standup from plain
  language (`agent/`, `.claude/skills/`). The customer's engineers already use
  Claude Code + Bedrock; direct Bedrock access is the access prerequisite.

## Two workloads, sized separately (and who owns each)

The engagement noted two distinct workloads. The ownership split is the
important part:

| Workload | Owner | Sized against |
|---|---|---|
| Modeling / rendering (USD, scene, visualization) | **AWS + NVIDIA (us)** | the g6e / L40S render host |
| Physics simulation (thermo / energy balance) | **Exowatt (Kamel, on Titan)** | their own solver — not us |

An earlier framing had us sizing PhysX for the physics workload; that was
corrected — we render Exowatt's Titan output and provide the agentic
provisioning; the physics sizing is theirs.

## Where this lives in the repo

- `harness/` — the four-step standup (quota -> provision -> install -> scene).
- `.claude/skills/omniverse-g6e-standup` — the agentic workflow that runs it.
- `.claude/skills/physx-render-bridge` — the physics-output-to-render bridge.
