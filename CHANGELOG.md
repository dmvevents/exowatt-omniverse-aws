# Changelog

All notable changes to this Exowatt x AWS x NVIDIA Omniverse engagement repo.

## 2026-09-02 - Initial scaffold

### Added
- Agentic standup harness (`harness/`): `quota_check.py` (G/VT vCPU quota,
  encodes the real On-Demand quota-0 blocker + the 128-vCPU request),
  `provision_g6e.py` (on-demand g6e.4xlarge / g7e plan + Spot Fleet g6.24xlarge
  fallback; live launch is a gated TODO), `omniverse_setup.py` (headless
  Omniverse Kit install plan), `first_scene.py` (the "hello Omniverse" USD
  target), and `selftest.py` (the offline check `make verify` runs — standard
  library only, no AWS, no GPU, no spend).
- The agent loop (`agent/`): `loop.sh` launcher, `AUTOPILOT.md` mission,
  `laptop-connect.sh` (laptop -> EC2 over SSH), `demo-two-agents.sh` (a narrated
  offline provisioning-agent + render-agent demo), kept transcripts.
- 10 skills in `.claude/skills/`: three new for this engagement
  (`omniverse-g6e-standup`, `physx-render-bridge`, `first-scene-hello-omniverse`)
  plus seven retargeted (`bedrock-setup`, `claude-code-on-bedrock`,
  `windows-wsl-setup`, `ngc-api-key`, `data-onboarding`, `run-workshop`,
  `agent-loop`).
- Session hooks (`.claude/hooks/`): session-start standup orientation +
  prompt-intent routing toward the standup / scene / data-onboarding skills.
- Docs: `docs/ARCHITECTURE.md` (digital twin: synthetic-design -> real-system
  ingestion -> sim-vs-actual delta; Omniverse = render layer only over Exowatt's
  Titan physics sim), `docs/POC-PLAN.md`, `docs/SETUP-GUIDE.md` (quota, Bedrock +
  Claude Code access, IAM, SSH keys, GitHub, NGC), and `docs/WORKSHOP-AGENDA.md`.
- Repo hygiene: `Makefile` (offline `verify` + `plan` targets), `.github/`
  (CODEOWNERS, PR + issue templates, offline `verify` CI), and the standard
  LICENSE / NOTICE / SECURITY / SUPPORT / CONTRIBUTING / CODE_OF_CONDUCT set.
  `.gitignore` excludes `*.env`, `*.pem`, `*.key`.

### Engagement context
- Subject is the P3 solar + thermal-battery system. Exowatt's team owns the
  physics simulation on Titan; Omniverse is the render layer only. NVIDIA-
  recommended alternatives are g7e-xlarge / g6e-xlarge. The deliverable is this
  repo: an agentic Bedrock provisioning workflow plus the Omniverse standup.
- Known constraints: the On-Demand G6 vCPU quota starts at 0 (Spot Fleet
  g6.24xlarge is the interim fallback); the customer needs direct Bedrock access
  as a prerequisite; Python / CFD / CAD assets are uploaded into Omniverse via
  the agent.
