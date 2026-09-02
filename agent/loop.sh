#!/usr/bin/env bash
# agent/loop.sh — start a tracked agent workstream.
#
# One command: named tmux session + kept transcript + Claude Code launched
# with the repo's CLAUDE.md as standing context. This is the entry point of
# the agent loop described in .claude/skills/agent-loop/SKILL.md.
#
# Usage:
#   agent/loop.sh <session-name> [initial prompt...]
#
# Examples:
#   agent/loop.sh standup            # interactive; agent reads agent/AUTOPILOT.md
#   agent/loop.sh quota "Run the omniverse-g6e-standup skill on the staged plan"
#
# Requirements: tmux, and one agent CLI on PATH (claude / codex).
# The backbone is Claude on Bedrock — see .claude/skills/claude-code-on-bedrock.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRANSCRIPTS="$REPO/agent/transcripts"

NAME="${1:-}"
if [[ -z "$NAME" ]]; then
    echo "usage: agent/loop.sh <session-name> [initial prompt...]" >&2
    exit 2
fi
shift || true
PROMPT="${*:-Read CLAUDE.md at the repo root, then read agent/AUTOPILOT.md and execute the mission. Stop at every human checkpoint it defines.}"

if ! command -v tmux >/dev/null; then
    echo "ERROR: tmux not installed (apt-get install tmux / brew install tmux)" >&2
    exit 1
fi

# One workstream, one name — refuse to trample a live session.
if tmux has-session -t "$NAME" 2>/dev/null; then
    echo "ERROR: tmux session '$NAME' already exists. Join it: tmux attach -t $NAME" >&2
    exit 1
fi

# Pick the agent CLI: Claude Code is the backbone; Codex is a mix-in.
AGENT_CLI=""
for c in claude codex; do
    if command -v "$c" >/dev/null; then AGENT_CLI="$c"; break; fi
done
if [[ -z "$AGENT_CLI" ]]; then
    echo "ERROR: no agent CLI found (tried: claude, codex)." >&2
    echo "Install Claude Code first — see .claude/skills/claude-code-on-bedrock/SKILL.md" >&2
    exit 1
fi

mkdir -p "$TRANSCRIPTS"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$TRANSCRIPTS/${NAME}-${STAMP}.log"

# Session starts at the repo root so CLAUDE.md is auto-loaded as context.
tmux new-session -d -s "$NAME" -c "$REPO"
# Keep the full pane transcript — this is the loop's evidence trail.
tmux pipe-pane -t "$NAME" "cat >> '$LOG'"

case "$AGENT_CLI" in
    claude) tmux send-keys -t "$NAME" "claude '$PROMPT'" C-m ;;
    *)      tmux send-keys -t "$NAME" "$AGENT_CLI" C-m
            sleep 2
            tmux send-keys -t "$NAME" "$PROMPT" C-m ;;
esac

echo "workstream '$NAME' started ($AGENT_CLI)"
echo "  transcript: ${LOG#$REPO/}"
echo "  join:       tmux attach -t $NAME"
echo "  observe:    tmux attach -rt $NAME"
