---
name: data-onboarding
description: Use when the customer uploads or points at input files for the digital twin — Python, CFD output, CAD (STEP/STL/OBJ), meshes, or existing USD — to bring into the Omniverse render layer. This is the ingestion front door. It identifies the source type, maps it toward a USD-ready asset, reports coverage and gaps, and keeps customer files in scratch/ (gitignored). It never fabricates geometry or physics values.
---

# Data onboarding — turn a customer input into a USD-ready asset

An Exowatt engineer just gave you a file. It might be a CAD part (STEP/STL/OBJ)
of the P3 system, a CFD/thermal result to visualize, a Python script that
builds geometry, or an existing USD. Your job: **identify it, map it toward a
USD asset the Omniverse render layer can load, report what's there and what's
missing, and keep the raw file in `scratch/` — never commit it.**

Remember the boundary: **Omniverse is the rendering layer.** Exowatt runs its
own physics simulation on Titan. You ingest and render their geometry and their
result fields; you do not compute the physics and you do not fabricate values.

## Step 1 — identify the source type

```bash
ls -la <upload path>
```

- **CAD** (`.step`/`.stp`/`.stl`/`.obj`/`.fbx`/`.gltf`) -> geometry to convert to USD.
- **USD/USDZ** (`.usd`/`.usda`/`.usdc`/`.usdz`) -> already the target format; validate and reference it.
- **CFD / result field** (VTK, CSV of node values, image stacks) -> a field to
  map onto existing geometry as color/attributes for visualization.
- **Python** -> a script that authors geometry or drives Kit; read it, do not run
  it blind.
- **Mixed** -> do each part, then compose into one USD stage.

## Step 2 — map toward USD (on the g6e host, inside Kit)

CAD -> USD conversion and USD authoring need `pxr`/USD, which lives inside the
Omniverse Kit runtime on the host. Plan the conversion; run it on the host:

- CAD: use the Omniverse CAD importer / Kit converter to produce a `.usd` under
  `scratch/usd/`. Record units and up-axis (the hello scene is Z-up).
- CFD field: map values onto the mesh as a primvar / display color; note the
  field name, range, and units.
- Keep every raw input and derived USD under `scratch/` (gitignored).

If you cannot convert on this machine (no Kit here), say so and write the exact
on-host command the operator should run — do not pretend a USD was produced.

## Step 3 — report, then hand off

Report in plain language: what the file is, geometry/units/up-axis, any field
mapped, where the USD landed (`scratch/usd/...`), and what is missing (units?
scale? a field legend?). Then:

- If a USD is ready: hand to `first-scene-hello-omniverse` (to prove it renders)
  or `physx-render-bridge` (to overlay a Titan result field).
- If it can't be converted here: state the exact on-host step and stop — never
  fabricate the asset.

## Honesty rails (always)

- Evidence before claims: cite the file paths and the exact USD prim/field
  names. If a step failed, report it verbatim.
- Customer inputs stay in `scratch/` — never commit them, never echo more than
  the report needs.
- Geometry is ingested as given; physics/result values come from Exowatt's
  Titan sim. Never invent a value or a field.
