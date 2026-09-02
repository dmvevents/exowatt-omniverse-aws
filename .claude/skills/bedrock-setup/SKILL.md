---
name: bedrock-setup
description: Use when standing up AWS Bedrock for this engagement on a new account — requesting Claude model access, configuring credentials/region, and verifying with a live converse smoke. Also use when Bedrock calls fail with AccessDeniedException. The customer currently lacks direct Bedrock access; this is a prerequisite to unblock Claude Code for their engineers.
---

# Set up AWS Bedrock for the Exowatt standup

Bedrock powers the **driving agent** (Claude Code), not a workflow model — the
standup harness itself makes no LLM calls. The engagement blocker: the customer
lacks direct Bedrock access; their engineers (Tim, Kamau) already use Claude Code
+ Bedrock elsewhere, so unblocking access is a prerequisite.

Target region is **us-east-1** by default — but confirm it matches the region
where the G/VT vCPU quota increase was requested, so the GPU host and Bedrock
live in the same place.

## 1. Credentials + region

```bash
aws configure --profile exowatt-poc          # or the customer's profile name
export AWS_PROFILE=exowatt-poc
export AWS_DEFAULT_REGION=us-east-1
aws sts get-caller-identity                  # must return the right account
```

On the EC2 host, prefer an **instance role** over long-lived keys.

## 2. Request Claude model access (human step, console)

Bedrock console -> **Model access** -> request the Claude models the driving
agent will use. Anthropic models may show a one-time use-case form. Grants are
usually minutes but can take longer — request them before the standup session,
never the morning of.

Pin an inference profile that actually exists on the account — do not guess an
ID from memory:

```bash
aws bedrock list-inference-profiles --region us-east-1
# use a current Claude Sonnet cross-region profile, e.g. us.anthropic.claude-sonnet-4-6
```

## 3. IAM (least privilege)

The calling role needs Bedrock invoke/converse:

```json
{"Effect": "Allow",
 "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream",
            "bedrock:Converse", "bedrock:ConverseStream",
            "bedrock:ListInferenceProfiles", "bedrock:GetInferenceProfile"],
 "Resource": ["arn:aws:bedrock:*:*:inference-profile/*",
              "arn:aws:bedrock:*:*:foundation-model/*"]}
```

## 4. Verify — the 5-second smoke

```bash
python3 -c "
import boto3
b = boto3.client('bedrock-runtime', region_name='us-east-1')
r = b.converse(modelId='us.anthropic.claude-sonnet-4-6',
    messages=[{'role':'user','content':[{'text':'reply with the word verified'}]}],
    inferenceConfig={'maxTokens':16,'temperature':0.0})
print(r['output']['message']['content'][0]['text'])
"
# expect: verified
```

Run this before every live session. It is the ground-truth answer to "is
Bedrock actually up on this account?" Next: point Claude Code at Bedrock with
the `claude-code-on-bedrock` skill.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `AccessDeniedException` | model access not granted, or IAM missing Converse | console Model access; add the IAM actions above |
| `NoCredentialsError` | profile not exported / no instance role | `export AWS_PROFILE=...` or attach an instance role |
| `ValidationException` on modelId | bare model name vs inference-profile ID | use the `us.` profile ID from `list-inference-profiles` |
| works in us-east-1, fails elsewhere | model not enabled in that region | enable it, or stay in us-east-1 |
