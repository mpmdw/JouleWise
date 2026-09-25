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
export FROZEN_PLAN_SHA256=9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072
export PR_L_COMMIT=9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87
export PREREG_SHA256='__PREREG__'
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
  local raw now_epoch_s
  print -- 'CHECK: ioreg -r -c AppleSmartBattery supplies one fresh, top-level battery observation'
  raw="$(/usr/sbin/ioreg -r -c AppleSmartBattery)" || return 3
  now_epoch_s="$(date +%s)" || return 3
  print -- "CHECK: battery gate observed at $(TZ=UTC date '+%Y-%m-%dT%H:%M:%SZ')"
  print -r -- "$raw" | BATTERY_WALL_EPOCH_S="$now_epoch_s" python3 -B -c '
import os, re, sys
raw = sys.stdin.read()
objects = re.findall(r"^\+-o AppleSmartBattery\b", raw, re.M)
print(f"CHECK: exactly one AppleSmartBattery object; count={len(objects)}", flush=True)
if len(objects) != 1:
    raise SystemExit(3)
closes = re.findall(r"^    \}\s*$", raw, re.M)
print(f"CHECK: exactly one complete top-level object; close_count={len(closes)}", flush=True)
if len(closes) != 1:
    raise SystemExit(3)
def field(name, kind="integer"):
    # ioreg top-level properties have six spaces; quoted keys prevent aliases.
    matches = re.findall(r"^      \"" + re.escape(name) + r"\" = (\S+)\s*$", raw, re.M)
    print(f"CHECK: exactly one top-level quoted {name}; raw={matches}", flush=True)
    if len(matches) != 1 or not re.fullmatch(
        r"Yes|No" if kind == "boolean" else r"[+-]?\d+", matches[0]):
        raise SystemExit(3)
    return matches[0]
external = field("ExternalConnected", "boolean")
charging = field("IsCharging", "boolean")
amperage_raw = field("InstantAmperage")
update_raw = field("UpdateTime")
for name, kind in (("AppleRawCurrentCapacity", "integer"),
                   ("AppleRawMaxCapacity", "integer"),
                   ("Amperage", "integer"),
                   ("Voltage", "integer"), ("Temperature", "integer"),
                   ("FullyCharged", "boolean"), ("CurrentCapacity", "integer")):
    field(name, kind)
number = int(amperage_raw)
print("CHECK: InstantAmperage is signed or unsigned 64-bit two-s complement", flush=True)
if number >= 2**64 or number < -(2**63):
    raise SystemExit(3)
signed = number - 2**64 if number >= 2**63 else number
print(f"CHECK: InstantAmperage raw={amperage_raw} signed={signed} mA; unsigned64_conversion={number >= 2**63}", flush=True)
now = int(os.environ["BATTERY_WALL_EPOCH_S"])
age = now - int(update_raw)
print(f"CHECK: UpdateTime raw={update_raw} wall_epoch_s={now} age_s={age}; 0 <= age <= 180", flush=True)
if not 0 <= age <= 180:
    raise SystemExit(3)
print("CHECK: ExternalConnected=Yes, IsCharging=No, abs(signed InstantAmperage)<=200 mA", flush=True)
if external != "Yes" or charging != "No" or abs(signed) > 200:
    raise SystemExit(3)
print("BATTERY GATE PASS", flush=True)
'
}
