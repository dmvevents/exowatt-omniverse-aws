---
name: claude-code-on-bedrock
description: Use when installing or configuring Claude Code to run against AWS Bedrock instead of the Anthropic API — no Anthropic API key, auth via the AWS credential chain. Also use when Claude Code says it cannot authenticate on a Bedrock-only account. This is how the customer's engineers drive the standup.
---

# Claude Code on AWS Bedrock

Run Claude Code with the customer's AWS account as the model provider — no
Anthropic API key anywhere. This is the backbone of the agent loop
(`agent/loop.sh`) and how Exowatt's engineers (who already use Claude Code +
Bedrock) drive the standup.

## 1. Install Claude Code

```bash
curl -fsSL https://claude.ai/install.sh | bash    # Linux/macOS
claude --version                                   # sanity
```

> **On Windows?** Run this inside **WSL2**, not PowerShell — do the
> `windows-wsl-setup` skill first, then come back here.

## 2. Point it at Bedrock

Prereq: the `bedrock-setup` skill is done (Claude model access granted,
credentials working, `aws sts get-caller-identity` returns the right account).

```bash
# ~/.bashrc (or the shell profile the agent host uses)
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1
export ANTHROPIC_MODEL="us.anthropic.claude-sonnet-4-6"   # a real inference-profile ID
```

Or per-project via an `env` block in `.claude/settings.json`. This repo's
committed `.claude/settings.json` holds only `$schema` + `hooks` — it does not
set these; add the block yourself, use the shell exports above, or put them in
`.claude/settings.local.json` (gitignored):

```json
{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "us-east-1",
    "ANTHROPIC_MODEL": "us.anthropic.claude-sonnet-4-6"
  }
}
```

Notes:
- `ANTHROPIC_MODEL` takes the **`us.` cross-region inference-profile ID**, not a
  bare model name. List what the account has:
  `aws bedrock list-inference-profiles --region us-east-1`.
- Pin `ANTHROPIC_MODEL` explicitly so the customer controls cost.
- Background/fast model: `ANTHROPIC_DEFAULT_HAIKU_MODEL=<haiku-class profile ID>`.
- Credentials resolve through the standard AWS chain. On the EC2 standup host,
  an **instance role** is cleanest — zero long-lived keys on disk.

## 3. IAM for the calling role

The same Bedrock actions as `bedrock-setup` step 3 cover this — one role can do
both. Scope `Resource` to inference-profile + foundation-model ARNs.

## 4. Verify

```bash
claude -p "reply with the single word verified"
# expect: verified   — served from the customer's Bedrock account
```

Inside an interactive session, `/status` shows Provider: Amazon Bedrock, the
pinned model ID, and the region — the one-look confirmation.

Triage when it fails:
1. `aws sts get-caller-identity` — wrong account / expired creds?
2. The converse smoke from `bedrock-setup` — model access?
3. `echo $ANTHROPIC_MODEL` — is it a real inference-profile ID on this account
   (`list-inference-profiles`), not a guessed name?

## Codex (the mix)

Codex CLI needs its own auth; use it as a second opinion in the loop, not the
backbone. Claude Code alone suffices to drive every mission in this repo.
