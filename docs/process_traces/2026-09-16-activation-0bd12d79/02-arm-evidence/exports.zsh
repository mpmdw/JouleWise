# Staging/arm exports for the equivalence night d079-epoch-25g83-derivation-n1-20260916 (activation 0bd12d79).
set -euo pipefail
export STAGE_DIR=/tmp/magistrate-0bd12d79/arm
export H="${H:-$(cat "$STAGE_DIR/H.txt")}"
export NIGHT_DATE=20260916
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export MEASUREMENT_ROOT="/Users/edr/JouleWise-measurement-$NIGHT_DATE-derivation"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
export PLAN_ID="d079-epoch-25g83-derivation-n1-$NIGHT_DATE"
export SESSION_ID="$PLAN_ID"
export EVIDENCE_ROOT_ID="evidence-$PLAN_ID"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export CALIBRATION_PLAN="$NIGHT_ROOT/calibration_plan.json"
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_SOURCE=/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl
export FROZEN_PLAN_SOURCE_REL=configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json
export T0_EPOCH_S=1789562400   # 2026-09-16 05:40:00 PDT, fixed in the handback commit H
export WINDOW_MAX_S=9000
