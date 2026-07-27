#!/bin/bash
# Publish window status to the repo so Ed can check it from a phone while the
# machine's screen is dark.
#
# WHY THIS EXISTS
#   Measurement windows run for hours with the display asleep and the operator
#   away. Until now the only way to learn a window had failed was to wake the
#   machine -- which is itself a measurement contaminant -- or to wait for the
#   session to report. On 2026-07-27 a window died five minutes after launch and
#   nobody knew for hours.
#
# PUSH DISCIPLINE -- THIS IS A SAFETY RULE, NOT A STYLE PREFERENCE
#   git push is network and CPU activity. It must NEVER run while a measurement
#   is in flight. Call this ONLY:
#     - before a window launches   (state: ready / blocked)
#     - after a window completes   (state: complete)
#     - after a window fails       (state: failed  -- the run has already stopped)
#     - between windows            (state: between)
#   Never during collection. The script refuses if a campaign process is running.
#
# USAGE
#   scripts/window_status.sh <state> "<headline>" ["<detail>"] ["<action needed>"]
#     state: ready | running | complete | failed | between | blocked | idle
#
#   Example:
#     scripts/window_status.sh failed "Window C died at member 7/40" \
#       "clock_anchor_unresolved; quarantined attempt3" \
#       "None -- diagnosing, will relaunch automatically"

set -euo pipefail

REPO=/Users/edr/code/JouleWise
STATUS_FILE="$REPO/WINDOW_STATUS.md"

STATE="${1:?state required: ready|running|complete|failed|between|blocked|idle}"
HEADLINE="${2:?headline required}"
DETAIL="${3:-}"
ACTION="${4:-None. Nothing needs your attention.}"

# Refuse to push while a measurement is live.
if ps aux | grep -E "run_campaign|window-chain" | grep -vq grep; then
  echo "REFUSING: a measurement process is running. Pushing now would contaminate it." >&2
  echo "Status not published. Call again between runs." >&2
  exit 1
fi

case "$STATE" in
  failed|blocked)  BANNER='# ⚠️ ATTENTION NEEDED' ;;
  complete)        BANNER='# ✅ RUN COMPLETE' ;;
  running)         BANNER='# ⏳ RUNNING — do not touch the machine' ;;
  ready|between)   BANNER='# 🟡 BETWEEN RUNS' ;;
  *)               BANNER='# 💤 IDLE' ;;
esac

NOW_LOCAL="$(date '+%Y-%m-%d %H:%M:%S %Z')"
NOW_UTC="$(TZ=UTC date '+%Y-%m-%dT%H:%M:%SZ')"

{
  echo "$BANNER"
  echo
  echo "**$HEADLINE**"
  echo
  echo "| | |"
  echo "|---|---|"
  echo "| State | \`$STATE\` |"
  echo "| Updated | $NOW_LOCAL ($NOW_UTC) |"
  echo
  echo "## Does anything need you?"
  echo
  echo "$ACTION"
  echo
  if [ -n "$DETAIL" ]; then
    echo "## Detail"
    echo
    echo "$DETAIL"
    echo
  fi
  echo "## How to read this"
  echo
  echo "This file is published from the measurement machine at defined moments only:"
  echo "before a window launches, after one completes or fails, and between runs."
  echo "It is **never** written while a measurement is in flight, because pushing"
  echo "is network and CPU activity that would contaminate the run."
  echo
  echo "**A stale timestamp during a run is normal and expected** — it means a"
  echo "window is still going. Compare the timestamp against the expected finish"
  echo "time in the detail section rather than treating silence as a fault."
  echo
  echo "If the timestamp is old **and** the detail says a run should already have"
  echo "finished, something went wrong in a way that stopped the session from"
  echo "reporting. That is the one case worth waking the machine for."
} > "$STATUS_FILE"

cd "$REPO"
git add WINDOW_STATUS.md
if git diff --cached --quiet; then
  echo "No status change; nothing to publish."
  exit 0
fi
git commit -q -m "status: $STATE — $HEADLINE"
git push -q origin HEAD 2>/dev/null || {
  echo "WARNING: push failed (offline?). Status committed locally only." >&2
  exit 0
}
echo "Published: $STATE — $HEADLINE"
