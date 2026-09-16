# Staging/arm exports for the REHEARSAL_STUB rehearsal-20260916c (activation 83d93f5a), re-plan of the lapsed rehearsal-20260916 candidate.
set -euo pipefail
export STAGE_DIR=/tmp/magistrate-83d93f5a/stage
export H="${H:-$(cat "$STAGE_DIR/H.txt")}"
export NIGHT_DATE=20260916
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export PLAN_ID="rehearsal-${NIGHT_DATE}c"
export MEASUREMENT_ROOT="/Users/edr/JouleWise-measurement-rehearsal-${NIGHT_DATE}c"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export WINDOW_MAX_S=900
export T0_EPOCH_S=1789554300   # 2026-09-16 03:25:00 PDT, fixed in the handback commit H
