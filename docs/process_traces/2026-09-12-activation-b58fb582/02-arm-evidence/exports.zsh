# Sourced by every later block. H is filled by 10-commit-H.zsh.
set -euo pipefail
export BOOKKEEPING_ROOT=/Users/edr/code/JouleWise-wt-bk-b58fb582
export H="${H:-$(cat /tmp/magistrate-b58fb582/H.txt)}"
export NIGHT_DATE=20260913
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export MEASUREMENT_ROOT="/Users/edr/JouleWise-measurement-$NIGHT_DATE-derivation"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
export PLAN_ID="d079-epoch-25g83-derivation-n1-$NIGHT_DATE"
export SESSION_ID="d079-epoch-25g83-derivation-n1-$NIGHT_DATE"
export EVIDENCE_ROOT_ID="evidence-d079-epoch-25g83-derivation-n1-$NIGHT_DATE"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export CALIBRATION_PLAN="$NIGHT_ROOT/calibration_plan.json"
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json"
export FROZEN_PLAN_SOURCE_REL=configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json
export T0_EPOCH_S=1789293360   # 2026-09-13T02:56:00-07:00
export WINDOW_MAX_S=9000
export NIGHT_HOUR=2 NIGHT_MINUTE=56
export TRACE_DIR="$BOOKKEEPING_ROOT/docs/process_traces/2026-09-12-activation-b58fb582"
export EVIDENCE_DIR="$TRACE_DIR/02-arm-evidence"
