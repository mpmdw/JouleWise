#!/bin/zsh
set -euo pipefail
# Lead fills ONLY these two values before use; NIGHT_DATE is t0's local date.
export NIGHT_DATE='20260920'
export T0_EPOCH_S='1789890000'
export H='cd10ce9d12f291070a0be77bc8c7768aa5e58ace'
export TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
[[ ${#NIGHT_DATE} -eq 8 && "$NIGHT_DATE" == <-> && "$T0_EPOCH_S" == <-> ]] || {
  print -u2 -- 'REFUSED: fill NIGHT_DATE and T0_EPOCH_S in arm-env.zsh'; exit 3
}
[[ "$(date -r "$T0_EPOCH_S" +%Y%m%d)" == "$NIGHT_DATE" ]] || exit 3
(( T0_EPOCH_S % 60 == 0 )) || exit 3
export PLAN_ID="qpe01-pilot-n1-$NIGHT_DATE"
export MEASUREMENT_ROOT="/Users/edr/JouleWise-measurement-$NIGHT_DATE-qpe01-pilot-n1"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json" PLAN="$NIGHT_ROOT/night_plan.json"
export WINDOW_MAX_S=9000
export INSTALL_CLOSE_EPOCH_S=$(( T0_EPOCH_S - 600 ))
export REQUEST_EPOCH_S=$(( T0_EPOCH_S - 480 ))
export TERM_EPOCH_S=$(( T0_EPOCH_S - 360 )) KILL_EPOCH_S=$(( T0_EPOCH_S - 300 ))
export ACQUISITION_END_EPOCH_S=$(( T0_EPOCH_S + WINDOW_MAX_S ))
export COURIER_EPOCH_S=$(( ACQUISITION_END_EPOCH_S + 300 ))
export DEADMAN_EPOCH_S=$(( (COURIER_EPOCH_S + 3600 + 59) / 60 * 60 ))
export PATH="$MEASUREMENT_ROOT/.venv/bin:$PATH"
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export ARM_ATTEMPT=1 ATTEMPT_DIR="$STAGE/arm-attempts/000001"
# The evidence chain reads neither SESSION_ID nor EVIDENCE_ROOT_ID.
