#!/bin/zsh
set -euo pipefail
export H='__H__' T0_EPOCH_S='1789819200'
export TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
export NIGHT_DATE="$(date -r "$T0_EPOCH_S" +%Y%m%d)"
export WINDOW_ID=n2
export MEASUREMENT_ROOT="/Users/edr/JouleWise-measurement-$NIGHT_DATE-derivation-$WINDOW_ID"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export PLAN_ID="d079-epoch-25g83-derivation-$WINDOW_ID-$NIGHT_DATE"
export SESSION_ID="$PLAN_ID" EVIDENCE_ROOT_ID="evidence-$PLAN_ID"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export PLAN="$NIGHT_ROOT/night_plan.json"
export CALIBRATION_PLAN="$NIGHT_ROOT/calibration_plan.json"
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json"
export PATH="$MEASUREMENT_ROOT/.venv/bin:$PATH"
export REMOTE_URL=https://github.com/mpmdw/JouleWise
# Night one appended 50 rows; the authenticated 126-record ledger lives in the
# night-one clone (head pin 126 / ffd12051 committed at H). The canonical root's
# copy is stale at 76 records and is NOT touched by this activation.
export LEDGER_SOURCE=/Users/edr/JouleWise-measurement-20260919-derivation/runs/calibration_observation_ledger.jsonl
export LEDGER_SOURCE_EXPECTED_SHA256=c004eee59b1bf837ff00ff94be19d3e3debb2e8bd9736bcc187931dc620193c5
export ARM_ATTEMPT=1 ATTEMPT_DIR="$STAGE/arm-attempts/000001"
