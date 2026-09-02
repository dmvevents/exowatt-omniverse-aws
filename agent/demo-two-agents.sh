#!/usr/bin/env bash
# agent/demo-two-agents.sh — one demo, two agents, one operating pattern.
#
# For customer success: show that the SAME agent pattern stands up the whole
# Omniverse host as two cooperating roles —
#   * a PROVISIONING agent (quota-check -> the g6e / Spot launch plan), and
#   * a RENDER agent (headless Omniverse Kit install -> the first USD scene).
# The point the room takes away: plain-language goal in, deterministic audited
# plan out; the model orchestrates, it never invents the numbers; every run
# leaves a kept trail; runs as a named tmux session per agent.
#
# It runs fully OFFLINE / read-only: no AWS call, no GPU, no cost. The live
# steps are gated TODOs inside the harness.
#
# Usage:
#   agent/demo-two-agents.sh            # full narrated two-part demo
#   agent/demo-two-agents.sh provision  # just the provisioning half
#   agent/demo-two-agents.sh render     # just the render half
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PART="${1:-both}"

hr()  { printf '%s\n' "------------------------------------------------------------------------"; }
say() { printf '\n\033[1;36m%s\033[0m\n' "$1"; }
note(){ printf '\033[2m%s\033[0m\n' "$1"; }

provision_half() {
    say "PART 1 — the PROVISIONING agent (get a GPU host, honestly)"
    note "Plain-language goal -> a deterministic, audited launch plan. The agent"
    note "reads the real quota state first; it does not pretend capacity exists."
    hr
    ( cd "$REPO" && python3 harness/quota_check.py --dry-run )
    echo
    ( cd "$REPO" && python3 harness/provision_g6e.py --dry-run )
    ( cd "$REPO" && python3 harness/provision_g6e.py --strategy spot --dry-run )
    hr
    note "Blocker surfaced: On-Demand G/VT vCPU quota = 0. Plan falls back to Spot."
    note "The first live RunInstances is a human checkpoint (agent/AUTOPILOT.md)."
}

render_half() {
    say "PART 2 — the RENDER agent (stand up Omniverse, draw the first scene)"
    note "Same operating pattern, a different role: install headless Kit on the"
    note "host, then author the 'hello Omniverse' USD scene as the POC proof."
    hr
    ( cd "$REPO" && python3 harness/omniverse_setup.py --plan )
    echo
    ( cd "$REPO" && python3 harness/first_scene.py --dry-run )
    hr
    note "Render layer only: Omniverse renders Exowatt's own Titan physics output."
    note "We do not own or size the physics sim (docs/ARCHITECTURE.md)."
}

closing() {
    say "THE THROUGH-LINE (what to say to the room)"
    cat <<'TXT'
  Two agents — one that provisions the GPU host, one that renders the first
  scene — one operating pattern:
    * plain-language goal in, deterministic plan out
    * the model orchestrates; it does not invent the numbers (quota=0 is real)
    * every run leaves a kept, auditable trail
    * runs as a named tmux session per agent (agent/loop.sh)
    * live steps (launch, install, render) are gated human checkpoints, never
      fabricated
  Next real step: clear the G/VT quota, then run the provisioning plan for real.
TXT
}

case "$PART" in
    provision) provision_half ;;
    render)    render_half ;;
    both)      provision_half; render_half; closing ;;
    *) echo "usage: $0 [both|provision|render]" >&2; exit 2 ;;
esac
