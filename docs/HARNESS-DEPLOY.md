# Deploying with the agentic-harness — what it does, and how it fits Exowatt

Two different things share the word "harness" in this project; keep them straight:

- **This repo's `harness/`** — the in-tree Python package (`quota_check.py`,
  `provision_g6e.py`, `omniverse_setup.py`, `first_scene.py`, `selftest.py`). It
  is the four-step **single-host** standup (quota -> provision g6e -> install Kit
  -> first scene) that `make verify` exercises offline. This doc is **not** about
  that.
- **The agentic-harness** — a separate AWS tool: a standalone
  "one message -> autonomous GPU-**cluster** bring-up" agent run as
  `python3 -m cluster_ops`. This doc is about *that* tool and why this POC
  deliberately does **not** use it.

## What the agentic-harness actually is

A **deterministic AWS GPU-cluster bring-up agent**. A conversational goal -> a
synthesized runbook of modules -> an empirical-ladder run against
`kubectl` / `eksctl` / CloudFormation / `aws sagemaker` / capacity-blocks, with a
redacted audit trail. Its worked example is "2-node HyperPod EKS p5, run NCCL,
run FSDP, then teardown" -> ~15 modules (capacity -> VPC -> EKS -> HyperPod ->
host-prep DaemonSets -> NCCL bandwidth gate -> ...). Its selling point: the
language model **never invents a number** — capacity discovery and plan synthesis
are pure functions.

```bash
python3 -m cluster_ops orchestrate "2-node HyperPod EKS p5, FSDP Llama-3-7B" --mode dry-run
# modes: dry-run (offline) . stage (read-only probes) . demo . prod (gated)
```

## The honest fit for Exowatt (verified 2026-09-02)

**The harness cannot stand up the Exowatt render host as-is — and that is fine,
because Exowatt is a single g6e host, not a cluster.** Verified in the harness
source on this host:

- **It builds GPU K8s *clusters*, not single hosts.** Its drivers are a `kubectl`
  driver + an SSH-bastion driver; every orchestrate goal synthesizes a multi-node
  runbook (VPC -> EKS -> HyperPod -> host-prep DaemonSets -> NCCL bandwidth gate).
  A single Omniverse render host needs **none** of that — no EKS, no HyperPod, no
  NCCL, no DaemonSets.
- **No generic single-instance launch.** There is no `RunInstances` /
  launch-template / user-data path anywhere in `cluster_ops/`; it knows GPU
  *instance types* but never launches one for a plain host, and it has no
  Omniverse-Kit install path.

So "use the harness to provision the g6e + install Omniverse + render the first
scene" would be net-new code outside its design center — a bigger build than this
POC needs.

**What that means in practice:** the g6e render host uses the lightweight
single-host bring-up already in this repo — `harness/provision_g6e.py` (the g6e /
Spot launch plan) + `agent/loop.sh` (the tracked agent) + the
`omniverse-g6e-standup` skill (quota -> provision -> install Kit -> scene). No
Kubernetes, no cluster. Rule of thumb: the agentic-harness is for **clusters**,
so a **single host** uses the lightweight path.

**When the harness WOULD be the right tool:** if Exowatt's *next* problem is a
GPU **cluster** — a multi-node rendering / simulation farm, or training a model on
HyperPod/EKS. That is the harness's design center; this single-host render POC is
not.

## What we borrow from the harness (patterns, not a dependency)

This repo does not vendor or import `cluster_ops`; it mirrors two of its patterns:

1. **The tmux session-per-agent launcher.** The harness launches its agent with
   `tmux new-session -d -s <name>` then `send-keys` and polls the pane. This
   repo's `agent/loop.sh` is the same pattern — one operating pattern across
   tools.
2. **The redacted audit trail.** The harness writes crash-safe, secret-redacted
   JSON to `~/.claude-sessions/<run_id>/`. This repo's equivalent is the kept
   tmux transcript (`agent/transcripts/`) + the plan JSON under `scratch/`. Same
   discipline: every run leaves an auditable trail.

## Provider coupling — good news for the self-hosted path

The harness is **not coupled to Bedrock.** Its deterministic core makes zero LLM
calls; the only hard provider reference is the `claude` CLI in its tmux launcher
— the same single swap point this repo has (`agent/loop.sh` tries `claude`, then
`codex`; `AGENTS.md` notes the one model seam is provider-agnostic). Both tools
graduate to a self-hosted model the same way: redirect the launcher's agent
binary and point that seam at an OpenAI-compatible endpoint (vLLM/Ollama).
Neither locks Exowatt to Claude or Bedrock.

## Seeing the pattern in a demo

This POC's own demo does not invoke the harness (a single host needs no cluster
bring-up); `agent/demo-two-agents.sh` narrates the two standup roles offline
(provisioning + render). The same operating pattern applies to the cluster case
if Exowatt's scope ever grows.

## Bottom line

- **Exowatt render host today** -> the single-host bring-up in this repo
  (`harness/provision_g6e.py` + `agent/loop.sh` + the `omniverse-g6e-standup`
  skill), **not** the agentic-harness.
- **Agentic-harness** -> the tool for a future GPU **cluster** (multi-node
  render/sim farm or HyperPod/EKS training), not a single Omniverse host.
- **Shared spine** -> tmux-session-per-agent, kept audit trail, provider-swap at
  one seam. That consistency is why the same operating pattern reads the same in
  both places.
