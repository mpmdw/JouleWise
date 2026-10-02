#!/bin/zsh
set -euo pipefail
export BENCH=/Users/edr/night-plan-staging/r6-bench
# ---- values substituted by the fill command in section 3 ----
export H='f0e211cbb5b6715cd9c67c3d56dd2fa8c0e4e67a'                       # 40 hex: remote main after the seal merge (and after the prior window's harvest PR for C2/C3)
export T0_EPOCH_S='1790835420'             # section 1
export WINDOW_LABEL='c1'        # c1 | c2 | c3
export PREREG_SHA256='d0034003a7e61683696b88662825d909dc4bb8ad23678edad6bbc8dfd4877b78'      # sha256 of the sealed registration file at H
export PRIOR_SESSION_ID=''       # empty for C1
export PRIOR_HARVEST_JSON=''     # empty for C1
export PRIOR_STARTED_EPOCH_S=''  # empty for C1
export PRIOR_TERMINAL_EPOCH_S='' # empty for C1
export LEDGER_SOURCE='/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/runs/calibration_observation_ledger.jsonl'
export LEDGER_SOURCE_EXPECTED_SHA256='23f72c37cb2483faa1b31a603996b86d6b7b390ce9460f490699501cfc971c7d'
# ---- fixed ----
export TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
export CANON=/Users/edr/code/JouleWise
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export REG_PATH='configs/calibration/preregistration_d079_epoch_25g83_rev1.md'
export T0_UTC="$(TZ=UTC date -r "$T0_EPOCH_S" +%Y%m%dT%H%MZ)"
export NIGHT_DATE="$T0_UTC"
export SESSION_ID="d079-epoch-25g83-r6-$T0_UTC"
export PLAN_ID="d079-epoch-25g83-r6-derivation-$WINDOW_LABEL-$T0_UTC"
export EVIDENCE_ROOT_ID="evidence-$PLAN_ID"
export MEASUREMENT_ROOT="/Users/edr/night-custody/measurement/JouleWise-measurement-$T0_UTC-r6-$WINDOW_LABEL"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export PLAN="$NIGHT_ROOT/night_plan.json"
export CALIBRATION_PLAN="$NIGHT_ROOT/calibration_plan.json"
export FROZEN_PLAN_REL="configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json"
export FROZEN_PLAN_SHA256=9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json"
export PATH="$MEASUREMENT_ROOT/.venv/bin:$PATH"
export ARM_ATTEMPT=1 ATTEMPT_DIR="$STAGE/arm-attempts/000001"
export FIRST_WINDOW_REASON='C1 is the first session of Revision 6; no earlier Revision 6 session exists, so start conditions (a) and (b) have nothing to test (Revision 6 section 6.2).'
if [[ -n "$PRIOR_SESSION_ID" ]]; then
  MANIFEST_FLAGS=(--prior-revision6-session "$PRIOR_SESSION_ID" --prior-harvest-json "$PRIOR_HARVEST_JSON"
                  --prior-started-epoch-s "$PRIOR_STARTED_EPOCH_S" --prior-terminal-epoch-s "$PRIOR_TERMINAL_EPOCH_S")
else
  MANIFEST_FLAGS=(--first-revision6-window-reason "$FIRST_WINDOW_REASON")
fi
source "$BENCH/battery-gate.zsh"
