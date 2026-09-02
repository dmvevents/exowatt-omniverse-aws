# Getting help

This repo backs the Exowatt x AWS x NVIDIA Omniverse digital-twin
engagement. Where you go for help depends on what you need.

| You need help with... | Go to |
|---|---|
| First-time setup (laptop -> Bedrock -> EC2 -> Omniverse) | [docs/SETUP-GUIDE.md](docs/SETUP-GUIDE.md) |
| A repo bug, a broken make target, a doc error | Open a GitHub issue with the bug template |
| G/VT vCPU quota increase, Spot Fleet approval | Contact Jingchao "JC" Yang (AWS SA) |
| AWS account, IAM, Bedrock model access | Contact Robert Harris-Crawford (AWS account) |
| NVIDIA Omniverse / Kit / instance sizing (g7e vs g6e) | Contact Anton Alexander (AWS NVIDIA Specialist) |
| Exowatt physics model (Titan), CAD/CFD inputs | Contact Kamel Boussaid (Exowatt engineering lead) |

## What's in scope

The maintainers of this repo can help with:

- Repo bugs: broken make targets, harness import errors, doc typos.
- The harness: what `quota_check`, `provision_g6e`, `omniverse_setup`, and
  `first_scene` plan, and how to wire the live steps once quota clears.
- The agent loop: driving the standup from a Claude Code + Bedrock session.

## What's out of scope

- Exowatt internal IT, VPN, or account access. Route those to Exowatt IT.
- AWS billing or commit changes. Route those to the AWS account team.
- The physics of the P3 system. The digital twin renders Exowatt's own
  Titan simulation output; it does not model the thermodynamics.

## How to file a useful bug report

A good bug report has three things:

- **Environment**: Python version (`python3 --version`), OS, branch and
  commit (`git log -1 --oneline`), output of `make verify`.
- **Repro steps**: the exact command(s) you ran, in order, on a clean
  checkout.
- **Expected vs. actual**: what you expected and what you got, with the
  full error and traceback.

Re-run `make clean && make verify` before filing if you see a flaky
failure — stale local state is the most common false positive.

## Next steps

- Report a bug: open a GitHub issue with the template.
- Onboarding: [docs/SETUP-GUIDE.md](docs/SETUP-GUIDE.md)
- Contributing changes: [CONTRIBUTING.md](CONTRIBUTING.md)
