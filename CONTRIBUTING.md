# Contributing to this repo

This repo backs an active Exowatt x AWS x NVIDIA customer engagement. Most
changes land as part of a standup session, a customer ask, or a planned POC
milestone. Whether you are adding a harness step, refreshing a doc, or fixing
a typo, this guide covers the conventions that keep the repo coherent.

## Before you start

```bash
git clone git@github.com:dmvevents/exowatt-omniverse-aws.git
cd exowatt-omniverse-aws
python3 -m venv .venv && source .venv/bin/activate
make verify
```

`make verify` runs the offline harness self-test (quota-check plan,
provisioning plan, Omniverse install plan, first-scene plan) in about a second
with no AWS spend and no GPU. If it fails on a clean clone, stop and fix it
before making other changes.

## Style guide

- Sentence-case headings (`## Quick start`, not `## Quick Start`).
- Active voice, present tense, second person.
- ISO 8601 dates (`2026-09-02`).
- Code blocks language-tagged (`bash`, `python`, `yaml`, `json`).
- Repo-relative cross-links in inline code formatting.
- Evidence before claims: never present a dry-run plan as a live result.

## Adding a harness step

The harness (`harness/`) is deliberately small — a single g6e host plus
Omniverse, not a cluster framework. To add a step:

1. Add a module under `harness/` that exposes a pure `build_*_plan()` function
   returning a plain dict (no live calls at import time).
2. Give it a CLI `main()` with an offline `--dry-run` default; guard any
   `boto3` import so the offline path needs only the standard library.
3. Mark any cloud-spending or on-host action as an explicit `TODO` that exits
   with a clear message — never fabricate a launch or a result.
4. Register it in `harness/selftest.py` so `make verify` exercises it.

## Adding a skill

Skills live in `.claude/skills/<name>/SKILL.md` with YAML front matter
(`name`, `description`). Keep them task-shaped and evidence-first. Register the
skill in the table in `CLAUDE.md` and, if it is a customer-facing verb, in
`AGENTS.md`.

## Pull requests

Branch from `main`. Run `make verify` before every commit. Use
[Conventional Commits](https://www.conventionalcommits.org/):

```
feat(harness): add Spot Fleet g6.24xlarge fallback plan
fix(quota): correct the On-Demand G/VT quota code
docs(architecture): clarify render-layer-only boundary with Titan
```

Open the pull request against `main`. Link the customer ask or POC milestone.
Keep PRs scoped to one logical concern.

## Issues

For repo bugs, open a GitHub issue using the bug template. For everything else
(cloud account, NVIDIA, quota escalation), see [SUPPORT.md](SUPPORT.md).

## Next steps

- Where to ask for help: [SUPPORT.md](SUPPORT.md)
- Repo overview: [README.md](README.md)
- POC plan: [docs/POC-PLAN.md](docs/POC-PLAN.md)
