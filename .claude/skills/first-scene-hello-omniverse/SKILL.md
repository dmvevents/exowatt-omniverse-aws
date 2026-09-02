---
name: first-scene-hello-omniverse
description: Use to author the minimal "hello Omniverse" USD scene on the g6e host as the POC proof that Omniverse Kit renders — a Z-up stage with a light, a ground plane, a cube, and a camera. Run it after the host is provisioned and Kit is installed.
---

# First scene — "hello Omniverse"

The smallest thing that proves the standup worked: a USD stage that Omniverse
Kit opens and renders on the g6e host. It is the POC proof point: get Kamel's
first scene / code running.

## Prerequisite

The g6e host is provisioned and Omniverse Kit is installed headless (see
`omniverse-g6e-standup` steps 2-3). `pxr`/USD only exists inside the Kit
runtime — this scene is authored **on the host**, not in the offline harness.

## The target

```bash
python3 harness/first_scene.py --dry-run    # prints the target + the USD code
```

Target `scenes/hello_exowatt.usd`, Z-up, with:

| Prim | Type | Role |
|---|---|---|
| `/World` | Xform | scene root |
| `/World/Light` | DistantLight | key light |
| `/World/Ground` | Mesh | ground plane |
| `/World/Cube` | Cube | the hello-world object |
| `/World/Camera` | Camera | framing camera |

## Author it (on the host, inside Kit)

Run the USD authoring snippet `harness/first_scene.py` prints (it uses
`pxr.Usd`, `UsdGeom`, `UsdLux`). Save the stage, then open it headless to
confirm the renderer initializes:

```bash
./kit --no-window --exec 'open scenes/hello_exowatt.usd; print("scene opened")'
```

## Done means

- `scenes/hello_exowatt.usd` exists on the host, and
- Kit opens it and the renderer initializes without error.

Cite the saved `.usd` path — do not claim a rendered frame you did not produce.
Next: bring Kamel's real geometry in (`data-onboarding`) and overlay a Titan
result field (`physx-render-bridge`).
