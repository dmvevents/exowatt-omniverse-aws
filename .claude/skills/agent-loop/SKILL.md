---
name: agent-loop
description: Use when starting, joining, or operating the tracked agent loop — the tmux-session-per-workstream pattern with kept transcripts, human checkpoints, and the autopilot mission file. Also use when asked to "start the agent" or "let the agent take over".
---

# The agent loop

The operating pattern this project runs on (the same one we run our own
engineering with): every workstream is a **named tmux session** with its
transcript kept, an agent works **autonomously between human checkpoints**,
and every claim is **verified against evidence** before it is believed.

## Anatomy

```
agent/
  loop.sh          # launcher: tmux session + transcript + agent, one command
  AUTOPILOT.md     # the standing mission the agent executes when told "go"
  transcripts/     # kept pane transcripts (gitignored), one per session+date
```

## Start a workstream

```bash
agent/loop.sh <session-name> [initial prompt]
# e.g.
agent/loop.sh standup "Read CLAUDE.md, then run the omniverse-g6e-standup skill: quota-check, then plan the g6e launch"
agent/loop.sh render            # interactive; agent reads AUTOPILOT.md
```

What it does: creates tmux session `<session-name>` (or errors if it exists —
one workstream, one name), turns on `pipe-pane` so the full transcript streams
to `agent/transcripts/<name>-<UTC-date>.log`, and launches Claude Code with the
repo `CLAUDE.md` as standing context.

Join / observe: `tmux attach -t <name>` (read-only: `tmux attach -rt <name>`).

## Rules of the loop

1. **One session = one workstream = one name.** Don't multiplex missions in a
   pane; start a second session.
2. **Transcripts are evidence.** Never delete `agent/transcripts/*`; they are
   how a claim gets audited later. Cite `transcript:line` when reporting what a
   session did.
3. **Human checkpoints** (the agent stops and asks; defined in
   `agent/AUTOPILOT.md`): first live AWS spend of the session (any
   RunInstances / RequestSpotFleet, or turning on a GPU host), anything leaving
   the machine (push, publish, send, upload), anything destructive.
4. **Evidence before claims** — a mission is done when its artifact exists (the
   plan JSON, green `make verify`, a saved `.usd`), not when the agent says so.
5. **Capture learnings**: non-obvious fixes get appended to the relevant
   `CLAUDE.md` before the session ends.

## Operating loop for the agent inside a session

```
read CLAUDE.md (root + folder)  ->  make verify (baseline)
  -> work the mission (AUTOPILOT.md or the prompt)
  -> verify each claim against an artifact
  -> checkpoint with the human where the mission says to
  -> append learnings -> leave the session running (do not kill it)
```
