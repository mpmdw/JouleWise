export H='92c178f863ccc9a9742f080108433a5afd148b2e' T0_EPOCH_S='1789684200'
export TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
export NIGHT_DATE="$(date -r "$T0_EPOCH_S" +%Y%m%d)"
export MEASUREMENT_ROOT="/Users/edr/JouleWise-measurement-$NIGHT_DATE-derivation"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export PLAN_ID="d079-epoch-25g83-derivation-n1-$NIGHT_DATE"
export SESSION_ID="$PLAN_ID" EVIDENCE_ROOT_ID="evidence-$PLAN_ID"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export PLAN="$NIGHT_ROOT/night_plan.json"
export CALIBRATION_PLAN="$NIGHT_ROOT/calibration_plan.json"
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json"
export PATH="$MEASUREMENT_ROOT/.venv/bin:$PATH"
