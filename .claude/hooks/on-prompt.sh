#!/usr/bin/env bash
# UserPromptSubmit hook — route the operator's words toward the right skill.
#
# The operator talks to this session in plain language. This hook reads their
# prompt and, when it detects a provisioning or scene intent, injects a short
# reminder pointing the agent at the correct skill. It NEVER blocks and NEVER
# fails the turn (always exits 0); the reminder is additive context only.
#
# Claude Code passes the hook a JSON object on stdin with a "prompt" field.
# Anything we print on stdout is added to the model's context for this turn.
set -euo pipefail

PROMPT="$(python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    print((d.get("prompt") or "").lower())
except Exception:
    print("")
' 2>/dev/null || echo "")"

[ -z "$PROMPT" ] && exit 0

emit() { printf '%s\n' "$1"; }

# Quota / provisioning intent -> omniverse-g6e-standup skill.
case "$PROMPT" in
  *quota*|*provision*|*"spin up"*|*"stand up"*|*standup*|*launch*|*runinstances*|*g6e*|*g7e*|*g6.*|*"spot fleet"*|*instance*|*vcpu*)
    emit "[hint] This looks like a GPU-host provisioning request. Invoke the 'omniverse-g6e-standup' skill — it runs quota-check -> provision g6e (or Spot g6.24xlarge fallback) -> install Omniverse Kit headless -> launch the first scene. Dry-run the plan first; the first live RunInstances call is a human checkpoint. Remember the On-Demand G/VT quota-0 blocker."
    exit 0
    ;;
esac

# Scene / render intent -> first-scene-hello-omniverse or physx-render-bridge.
case "$PROMPT" in
  *"first scene"*|*"hello omniverse"*|*usd*|*render*|*scene*|*viewport*|*stage*)
    emit "[hint] This looks like a scene/render request. For the initial proof invoke 'first-scene-hello-omniverse'. To render Exowatt's own Titan physics output (we do NOT own the physics sim), invoke 'physx-render-bridge'. Keep runs as evidence: cite the written USD path, never claim a frame you did not render."
    exit 0
    ;;
esac

# Data-upload intent (CAD / CFD / Python) -> data-onboarding skill.
case "$PROMPT" in
  *upload*|*"here is"*|*"here's a"*|*ingest*|*.cad*|*.step*|*.stp*|*.stl*|*.obj*|*.usd*|*.py*|*cfd*|*cad*|*mesh*|*geometry*)
    emit "[hint] The customer may be providing input files (Python / CFD / CAD). If so, invoke the 'data-onboarding' skill — it maps any input into a USD-ready asset for the Omniverse render layer, reports coverage/gaps, and keeps customer files in scratch/ (gitignored)."
    exit 0
    ;;
esac

exit 0
