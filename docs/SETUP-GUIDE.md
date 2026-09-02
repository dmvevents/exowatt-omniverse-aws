# Setup guide — prerequisites for the Exowatt Omniverse standup

This is the IT-admin / operator checklist to go from nothing to "the agent can
stand up Omniverse on a g6e host." Do these before the standup session. Nothing
here spends money except the GPU host itself (a gated, explicit step).

## 0. Run the offline harness first (no account needed)

```bash
git clone git@github.com:dmvevents/exowatt-omniverse-aws.git
cd exowatt-omniverse-aws
python3 -m venv .venv && source .venv/bin/activate    # Python 3.11+
make verify        # offline self-test: no AWS, no GPU, no spend
make plan          # see all four standup plans
```

## 1. GPU capacity — the G/VT vCPU quota (the real blocker)

Launching a GPU instance needs **Running On-Demand G and VT instances**
(measured in vCPUs) quota > 0. On this engagement it is **0** — a `g6.8xlarge`
launch failed with `VcpuLimitExceeded`.

- **Quota code:** `L-DB2E81BA` (On-Demand G/VT), `L-3819A6DF` (Spot G/VT).
- **Requested:** 128 vCPUs = 8x g6e.4xlarge (L40S, 16 vCPUs each). JC Yang is
  monitoring the increase.
- **Check it:**

  ```bash
  aws service-quotas get-service-quota --service-code ec2 \
      --quota-code L-DB2E81BA --region us-east-1
  # or, from the harness:
  python3 harness/quota_check.py --live
  ```

- **Request an increase:** Service Quotas console -> EC2 -> the quota above ->
  Request increase. Approvals can take from ~30 minutes to longer.
- **Interim fallback:** Spot Fleet `g6.24xlarge` while the On-Demand increase is
  pending (`python3 harness/provision_g6e.py --strategy spot`).

Instance choice: **g6e.4xlarge** (L40S) is the recommended Omniverse host.
**g7e-xlarge / g6e-xlarge** are the NVIDIA-recommended alternatives for RTX /
ray tracing. See `harness/provision_g6e.py` for the options table.

## 2. Bedrock + Claude Code access (to drive the standup)

The agent that runs the standup is Claude Code on Bedrock. The customer
currently **lacks direct Bedrock access** — that is a prerequisite. Their
engineers (Tim, Kamau) already use Claude Code + Bedrock, so the pattern is
familiar.

- Request Claude model access in the Bedrock console (see the `bedrock-setup`
  skill).
- Point Claude Code at Bedrock (see the `claude-code-on-bedrock` skill):
  `CLAUDE_CODE_USE_BEDROCK=1`, `AWS_REGION`, a real `ANTHROPIC_MODEL`
  inference-profile ID.
- Verify: `claude -p "reply with the single word verified"` -> `verified`.

## 3. IAM for the EC2 host / operator role

One role covers the standup. Least-privilege actions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {"Sid": "Bedrock", "Effect": "Allow",
     "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream",
                "bedrock:Converse", "bedrock:ConverseStream",
                "bedrock:ListInferenceProfiles", "bedrock:GetInferenceProfile"],
     "Resource": ["arn:aws:bedrock:*:*:inference-profile/*",
                  "arn:aws:bedrock:*:*:foundation-model/*"]},
    {"Sid": "Quotas", "Effect": "Allow",
     "Action": ["servicequotas:GetServiceQuota", "servicequotas:ListServiceQuotas",
                "servicequotas:RequestServiceQuotaIncrease"],
     "Resource": "*"},
    {"Sid": "ProvisionGpuHost", "Effect": "Allow",
     "Action": ["ec2:DescribeInstances", "ec2:DescribeImages", "ec2:DescribeSubnets",
                "ec2:DescribeSecurityGroups", "ec2:RunInstances", "ec2:CreateTags",
                "ec2:RequestSpotFleet", "ec2:DescribeSpotFleetRequests"],
     "Resource": "*"}
  ]
}
```

Prefer an **EC2 instance role** on the host over long-lived keys. Scope
`Resource` down to the specific subnet / SG / AMI ARNs for a pilot.

## 4. SSH keys (laptop -> EC2)

```bash
ssh-keygen -t ed25519 -C "exowatt-standup-$(whoami)"   # a passphrase is fine
cat ~/.ssh/id_ed25519.pub                               # give the PUBLIC key to the AWS SA
```

The SA adds the public key to the host user's `~/.ssh/authorized_keys` (or use
SSM Session Manager and skip inbound SSH entirely). Never share the private key.
Windows engineers: do this inside WSL2 — see the `windows-wsl-setup` skill.
Keep keys out of the repo: `*.pem` and `*.key` are gitignored.

## 5. GitHub access

This repo is **private** (`dmvevents/exowatt-omniverse-aws`). Grant the
customer's engineers read access as needed. Clone over SSH:

```bash
git clone git@github.com:dmvevents/exowatt-omniverse-aws.git
```

Configure `~/.exowatt-remote` so `agent/laptop-connect.sh` can reach the host
(see the `windows-wsl-setup` skill, step 5).

## 6. NGC (for the Omniverse Kit pull, on the host)

Fetching Omniverse Kit from `nvcr.io` needs an `NGC_API_KEY` — see the
`ngc-api-key` skill. This runs on the g6e host during `omniverse_setup`.

## You're ready when

`make verify` is green, `aws sts get-caller-identity` shows the right account,
the Bedrock converse smoke returns `verified`, `python3 harness/quota_check.py
--live` shows the quota state, and you can SSH to (or SSM into) the host once it
exists. Then run the `omniverse-g6e-standup` skill.
