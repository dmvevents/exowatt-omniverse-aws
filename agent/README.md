# agent/ — the tracked agent loop

The operating pattern this repo runs on: agents on AWS Bedrock (Claude as the
backbone), every workstream a named tmux session with its transcript kept,
autonomous work between human checkpoints, evidence before claims.

```
agent/
  loop.sh          one-command launcher: tmux + transcript + agent
  AUTOPILOT.md     the standing mission an unattended agent executes
  laptop-connect.sh  the laptop's SSH bridge to the EC2 standup agent
  demo-two-agents.sh a narrated offline demo: provisioning agent + render agent
  transcripts/     kept pane transcripts (gitignored), one per session+date
```

## Quick start

```bash
# prerequisites (one-time): the claude-code-on-bedrock and bedrock-setup skills
agent/loop.sh standup          # starts the loop on the AUTOPILOT mission
tmux attach -t standup         # watch or steer
```

Give it a specific mission instead:

```bash
agent/loop.sh quota "Run the omniverse-g6e-standup skill: quota-check, then plan the g6e launch"
```

## Why tmux + transcripts

- The session survives your laptop closing; the agent keeps working.
- `agent/transcripts/<name>-<stamp>.log` is the audit trail — when the agent
  claims something, the transcript is where you check.
- Multiple workstreams run side by side (`tmux ls`), each isolated.

## The contract

The agent's rules live in three layers, most general first:

1. `CLAUDE.md` (repo root) — house rules, always loaded.
2. Folder context (`harness/README.md`, `docs/`) — local context.
3. `agent/AUTOPILOT.md` — the mission + the human checkpoints (live AWS
   spend, anything leaving the machine, anything destructive).

Skills in `.claude/skills/` are the verbs: `omniverse-g6e-standup`,
`physx-render-bridge`, `first-scene-hello-omniverse`, `bedrock-setup`,
`claude-code-on-bedrock`, `ngc-api-key`, `windows-wsl-setup`,
`data-onboarding`, `run-workshop`, `agent-loop`.
