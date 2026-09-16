# Staging exports for the REHEARSAL_STUB rehearsal-20260916 (activation 08ca8197). Sourced by every block.
set -euo pipefail
export STAGE_DIR=/tmp/magistrate-08ca8197/stage
export H="${H:-$(cat "$STAGE_DIR/H.txt")}"
export NIGHT_DATE=20260916
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export PLAN_ID="rehearsal-$NIGHT_DATE"
export MEASUREMENT_ROOT="/Users/edr/JouleWise-measurement-rehearsal-$NIGHT_DATE"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export WINDOW_MAX_S=900
export ARM_TO_T0_FLOOR_S=$((85*60))   # current floor: PLAN_LEAD_S 25 min + INSTALL_CLOSE_MARGIN_S 60 min (A210 will shorten)
