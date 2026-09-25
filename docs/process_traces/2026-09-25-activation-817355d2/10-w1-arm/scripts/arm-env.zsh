#!/bin/zsh
set -euo pipefail
export H='__H__' T0_EPOCH_S='__T0__'
export TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
export WINDOW_ID=w1
export NIGHT_DATE="$(date -r "$T0_EPOCH_S" +%Y%m%d)"
export MEASUREMENT_ROOT="/Users/edr/night-custody/measurement/JouleWise-measurement-$NIGHT_DATE-derivation-$WINDOW_ID"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export PLAN_ID="d079-epoch-25g83-derivation-$WINDOW_ID-$NIGHT_DATE"
export SESSION_ID="$PLAN_ID" EVIDENCE_ROOT_ID="evidence-$PLAN_ID"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export PLAN="$NIGHT_ROOT/night_plan.json"
export CALIBRATION_PLAN="$NIGHT_ROOT/calibration_plan.json"
export FROZEN_PLAN_REL="configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json"
export PR_L_COMMIT=9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87
export SEALED_REGISTRATION_SHA256=497847c4adcae3d8a9bfef99148c602579cca2b4adec1893c1980e7b366fd191
export NIGHT_TEMPLATE_SHA256=e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8
export PROBE_TEMPLATE_SHA256=1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json"
export PATH="$MEASUREMENT_ROOT/.venv/bin:$PATH"
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export LEDGER_SOURCE=/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl
export ARM_ATTEMPT=1 ATTEMPT_DIR="$STAGE/arm-attempts/000001"

# Read-only battery observation. The caller retains stdout with a timestamp.
battery_gate() {
  local raw
  print -- 'CHECK: ioreg -r -c AppleSmartBattery supplies ExternalConnected, IsCharging and InstantAmperage'
  raw="$(/usr/sbin/ioreg -r -c AppleSmartBattery)" || return 3
  print -- "CHECK: battery gate observed at $(TZ=UTC date '+%Y-%m-%dT%H:%M:%SZ')"
  print -r -- "$raw" | python3 -B -c '
import re, sys
text = sys.stdin.read()
def field(name):
    matches = re.findall(r"\"" + re.escape(name) + r"\"\s*=\s*(Yes|No|True|False|[+-]?\d+)", text)
    print(f"CHECK: exactly one {name} field; raw={matches}", flush=True)
    if len(matches) != 1:
        raise SystemExit(3)
    return matches[0]
external = field("ExternalConnected")
charging = field("IsCharging")
amperage_raw = field("InstantAmperage")
raw_number = int(amperage_raw)
print(f"CHECK: raw ExternalConnected={external} IsCharging={charging} InstantAmperage={amperage_raw} mA", flush=True)
print("CHECK: InstantAmperage is a signed integer or unsigned 64-bit two\047s complement", flush=True)
if raw_number >= 2**64 or raw_number < -(2**63):
    raise SystemExit(3)
signed = raw_number - 2**64 if raw_number >= 2**63 else raw_number
print(f"CHECK: signed InstantAmperage={signed} mA (unsigned64 conversion={raw_number >= 2**63})", flush=True)
print("CHECK: ExternalConnected=Yes, IsCharging=No, abs(signed InstantAmperage)<=200 mA", flush=True)
if external != "Yes" or charging != "No" or abs(signed) > 200:
    raise SystemExit(3)
print("BATTERY GATE PASS", flush=True)
'
}
