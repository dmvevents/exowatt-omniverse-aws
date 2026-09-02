#!/usr/bin/env bash
# SessionStart hook — orient a fresh agent to the live state of the standup.
#
# Surfaces where the standup stands (quota, host, Omniverse, first scene) so an
# agent the operator just started knows what it can run before being asked.
# Never blocks, never fails the turn (always exits 0). Output is added to the
# session's opening context.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO" || exit 0

echo "[Exowatt Omniverse standup] Read AGENTS.md for how to drive this from a conversation."

# Print the offline harness plan headline if it imports cleanly. Guarded so a
# broken import or missing dep never taints the session start.
python3 - <<'PY' 2>/dev/null || true
import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "harness"))
try:
    import quota_check
    r = quota_check.build_quota_report(region="us-east-1", live=False)
    blocker = "BLOCKER: On-Demand G/VT vCPU quota = 0 (increase submitted; JC monitoring)" \
        if r.get("blocker") else "no known quota blocker"
    print(f"[standup] region={r.get('region')} | {blocker}")
    print("[standup] next: invoke 'omniverse-g6e-standup' — quota-check -> provision g6e -> install Kit -> first scene. Dry-run first; live RunInstances is a human checkpoint.")
except Exception:
    pass
PY

exit 0
