---
name: physx-render-bridge
description: Use to bring Exowatt's own physics-simulation output (their thermodynamic / energy-balance solver on Titan) into NVIDIA Omniverse as a rendered visualization. This is the physics-to-render bridge. Critical boundary — we do NOT own, run, or size the physics simulation (not native Omniverse Physics, not PhysX); we ingest Exowatt's result fields and render them over their geometry.
---

# The physics-to-render bridge (we render; Kamel simulates)

The architecture decision on this engagement: **Kamel's
team builds their own physics simulation** (thermodynamic / energy-balance model
of the P3 solar + thermal-battery system: sunlight -> store -> Stirling engine
-> electricity) **on Titan**. **Omniverse is purely the rendering layer** for
that output. Native Omniverse Physics (USD Physics / PhysX) is available, but
Kamel keeps his own solver. So this bridge does one job: **turn a Titan result
into a rendered Omniverse view.** We do not own, run, or size the physics.

## What comes in, what goes out

```
Exowatt's Titan physics sim  ->  result fields (per-node/per-cell values,
  (thermo / energy balance)       time series, or images)          ->  THIS BRIDGE
                                                                          |
                             map values onto the USD geometry as primvars / display color
                                                                          |
                                                             Omniverse Kit renders it
```

## Steps

1. **Take the geometry as USD.** The P3 system geometry comes in via
   `data-onboarding` (CAD -> USD on the host). This is the surface the results
   paint onto.
2. **Take the Titan result as data, not physics.** Ingest Kamel's output
   (VTK / CSV of node values / time series / image stack). Record the field
   name, units, and range. Never recompute it and never invent values.
3. **Bind the field to the geometry.** In Kit on the host, attach the values as
   a USD primvar / display color on the matching prims; for a time series,
   author time samples so the twin animates. Keep intermediates in `scratch/`.
4. **Render / stream.** Use headless Kit (optionally Omniverse streaming) to
   render the visualized field; the frame or the `.usd` with bound values is the
   artifact.
5. **(Design stage) synthetic vs real.** Early on the field is synthetic design
   data; later it is real system telemetry. Show the **sim-vs-actual delta** as
   a second bound field — see `docs/ARCHITECTURE.md`.

## Boundary rules (do not cross)

- **We do not own the physics.** No claim about thermodynamic accuracy, energy
  balance, or Stirling behavior comes from us — it comes from Kamel's Titan sim.
- **We do not size PhysX.** If asked to "size the physics workload", redirect:
  that is Exowatt's solver on Titan. We size the **render** host (g6e — see
  `omniverse-g6e-standup`).
- **Values are ingested, never fabricated.** A missing field is reported as
  missing, not filled with a plausible number.
