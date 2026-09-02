#!/usr/bin/env bash
# agent/laptop-connect.sh — the laptop's bridge to the EC2 standup agent.
#
# Two agents, one workflow:
#   * EC2 agent  — Claude Code on Bedrock, runs the Omniverse standup. The backbone.
#   * Laptop agent — a general coding agent (Claude Code / Cursor / Codex / etc.)
#     the operator talks to. It shells out to THIS script to reach the EC2.
#
# A human can run it directly; a laptop coding agent can call it verbatim. It
# never opens a public port — everything rides SSH.
#
# Configure once (env vars, or ~/.exowatt-remote which this sources):
#   EXOWATT_HOST   EC2 host or IP           (required)
#   EXOWATT_USER   SSH user                 (default: ubuntu)
#   EXOWATT_KEY    path to SSH private key  (optional; else your SSH agent/config)
#   EXOWATT_REPO   repo path on the EC2     (default: /home/ubuntu/exowatt-omniverse-aws)
#   EXOWATT_TMUX   tmux session name        (default: standup)
#
# Usage:
#   agent/laptop-connect.sh status                 # is the host reachable + session up?
#   agent/laptop-connect.sh attach                 # interactive: attach the live agent session
#   agent/laptop-connect.sh run "<make target>"    # run one make target remotely (e.g. verify, quota)
#   agent/laptop-connect.sh ask "<instruction>"    # hand a natural-language instruction to the EC2 agent
#   agent/laptop-connect.sh upload <local-file>    # copy an input file into the EC2 scratch/uploads/
#
# Examples:
#   agent/laptop-connect.sh run "verify"
#   agent/laptop-connect.sh run "quota"
#   agent/laptop-connect.sh ask "check the G/VT quota and plan the g6e launch"
set -euo pipefail

# --- usage (works without any config, so read it first) --------------------
CMD="${1:-help}"
if [ "$CMD" = "help" ] || [ "$CMD" = "-h" ] || [ "$CMD" = "--help" ]; then
    sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
fi

# --- config -----------------------------------------------------------------
[ -f "${HOME}/.exowatt-remote" ] && . "${HOME}/.exowatt-remote"
HOST="${EXOWATT_HOST:-}"
USER_="${EXOWATT_USER:-ubuntu}"
KEY="${EXOWATT_KEY:-}"
REPO="${EXOWATT_REPO:-/home/ubuntu/exowatt-omniverse-aws}"
SESSION="${EXOWATT_TMUX:-standup}"

if [ -z "$HOST" ]; then
    echo "ERROR: EXOWATT_HOST is not set. Export it or put it in ~/.exowatt-remote:" >&2
    echo "  echo 'EXOWATT_HOST=1.2.3.4' >> ~/.exowatt-remote" >&2
    exit 2
fi

SSH_OPTS=(-o StrictHostKeyChecking=accept-new -o ConnectTimeout=10)
[ -n "$KEY" ] && SSH_OPTS+=(-i "$KEY")
TARGET="${USER_}@${HOST}"

# All remote commands run from the repo so CLAUDE.md/AGENTS.md load as context.
remote() { ssh "${SSH_OPTS[@]}" "$TARGET" "cd '$REPO' && $1"; }

shift || true

case "$CMD" in
  status)
    echo "-> host $TARGET, repo $REPO, tmux '$SESSION'"
    if remote "true" 2>/dev/null; then
        echo "OK  SSH reachable"
    else
        echo "XX  SSH failed — check EXOWATT_HOST/USER/KEY and the security group (port 22)"; exit 1
    fi
    if remote "tmux has-session -t '$SESSION' 2>/dev/null"; then
        echo "OK  agent session '$SESSION' is live (attach with: $0 attach)"
    else
        echo "..  no '$SESSION' session yet — start one on the host: agent/loop.sh $SESSION"
    fi
    # Show the offline quota headline the harness sees.
    remote "make -s quota 2>/dev/null" || true
    ;;

  attach)
    # Interactive: join the live Claude-on-Bedrock session (or start it).
    exec ssh -t "${SSH_OPTS[@]}" "$TARGET" \
        "cd '$REPO' && (tmux attach -t '$SESSION' || tmux new -s '$SESSION')"
    ;;

  run)
    # Run one make target remotely and stream its output back.
    [ $# -ge 1 ] || { echo "usage: $0 run \"<make target>\"" >&2; exit 2; }
    remote "make $*"
    ;;

  ask)
    # Hand a natural-language instruction to the EC2 Claude agent, headless,
    # and stream its answer back.
    [ $# -ge 1 ] || { echo "usage: $0 ask \"<instruction>\"" >&2; exit 2; }
    PROMPT="$*"
    ESCAPED="${PROMPT//\'/\'\\\'\'}"
    remote "claude --dangerously-skip-permissions -p '$ESCAPED'"
    ;;

  upload)
    # Copy a local input file into the EC2 scratch/uploads/ (gitignored).
    [ $# -ge 1 ] || { echo "usage: $0 upload <local-file>" >&2; exit 2; }
    SRC="$1"
    [ -f "$SRC" ] || { echo "no such file: $SRC" >&2; exit 2; }
    remote "mkdir -p '$REPO/scratch/uploads'"
    SCP_OPTS=(-o StrictHostKeyChecking=accept-new)
    [ -n "$KEY" ] && SCP_OPTS+=(-i "$KEY")
    scp "${SCP_OPTS[@]}" "$SRC" "$TARGET:$REPO/scratch/uploads/"
    echo "OK  uploaded $(basename "$SRC") -> $REPO/scratch/uploads/ (tell the agent to onboard it)"
    ;;

  *)
    echo "unknown command: $CMD" >&2
    sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
    exit 2
    ;;
esac
