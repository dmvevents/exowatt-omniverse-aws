# Security policy

This is a private POC repository. It is not a public open-source project,
and its security model reflects that.

## Reporting a security issue

Vulnerability reports go through the AWS account team, not GitHub Issues.
Do not file public issues for suspected vulnerabilities.

Contacts:

- Anton Alexander (AWS NVIDIA Specialist)
- Jingchao "JC" Yang (AWS Solutions Architect)
- Robert Harris-Crawford (AWS account)

Use the AWS-internal channel for the engagement to reach the account team.
The account team coordinates with Exowatt security as the primary affected
party. Disclosure follows a 90-day coordinated-disclosure standard; the
customer (Exowatt) is informed first.

## What's in scope

- Code in this repository (the `harness/` provisioning + scene scripts,
  the agent loop, the hooks and skills).
- The provisioning plans emitted by `harness/` in dry-run.

## What's out of scope

- Live AWS infrastructure (covered by AWS Security Bulletins).
- NVIDIA Omniverse / Kit / PhysX binaries (covered by NVIDIA PSIRT).
- Exowatt's own physics solver (Titan) and production system data.

## Hardening notes for any pilot deployment

This is POC scaffolding. Before any pilot on a real Exowatt account:

- Provision the g6e host in a private subnet; reach it over SSH or SSM
  Session Manager, never a public Omniverse streaming port.
- Use an EC2 instance role for Bedrock and Service Quotas access — no
  long-lived keys on the host.
- Rotate any NGC API keys and AWS access keys used during standup.
- Restrict the security group to the operator's IP and the customer's
  VPN egress only.
- Keep customer CAD / CFD / Python inputs in `scratch/` (gitignored) and,
  on the host, in an encrypted volume.

## Known limitations

- The `harness/` live paths (RunInstances, Spot Fleet, Omniverse install,
  scene launch) are intentionally left as gated TODOs — this repo plans
  and validates them offline; it does not execute cloud spend.
- No production-grade authentication on any host-side service.
- Quota state is read at run time; a stale report does not reflect a
  pending increase.

## Next steps

- Engagement contacts: [SUPPORT.md](SUPPORT.md)
- Repository license: [LICENSE](LICENSE)
- Third-party notices: [NOTICE](NOTICE)
