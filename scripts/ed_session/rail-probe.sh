#!/bin/bash
# ED-QUALIFICATION step 3: keyboard-backlight ABBA rail probe.

set -euo pipefail

ORIGINAL_ARGS=("$@")
DRY_RUN=0
NO_SUDO=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --no-sudo) NO_SUDO=1 ;;
    *) echo "usage: $0 [--dry-run] [--no-sudo]" >&2; exit 2 ;;
  esac
  shift
done

if [ "$NO_SUDO" -eq 1 ] && [ "$DRY_RUN" -ne 1 ]; then
  echo "REFUSE: --no-sudo is a dry-run inspection aid only; the live rail probe requires sudo -n." >&2
  exit 2
fi

SESSION_ROOT=/tmp/ed-session
mkdir -p "$SESSION_ROOT"
STAMP="${ED_SESSION_STAMP:-$(date -u '+%Y%m%dT%H%M%SZ')}"
RUN_ROOT="$SESSION_ROOT/rail-probe-$STAMP"
mkdir -p "$RUN_ROOT"
LOG="$RUN_ROOT/rail-probe.log"
RESULT="$RUN_ROOT/rail-probe-results.json"
if [ "${ED_SESSION_TEE_ACTIVE:-0}" -ne 1 ]; then
  set +e
  ED_SESSION_TEE_ACTIVE=1 ED_SESSION_STAMP="$STAMP" \
    /bin/bash "$0" "${ORIGINAL_ARGS[@]}" 2>&1 | /usr/bin/tee -a "$LOG"
  status="${PIPESTATUS[0]}"
  exit "$status"
fi

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd -P)"
PYTHON="$REPO_ROOT/.venv/bin/python"
[ -x "$PYTHON" ] || PYTHON=python3
SAMPLERS=battery,cpu_power,gpu_power,ane_power,thermal
ARMS=(max-1 off-1 off-2 max-2)

require_empty_sampler_census() {
  local output rc
  set +e
  output="$(/usr/bin/pgrep -fl '[p]owermetrics' 2>&1)"
  rc=$?
  set -e
  case "$rc" in
    0) echo "$output"; echo "REFUSE: a powermetrics process already exists." >&2; return 1 ;;
    1) echo "PASS: no powermetrics process found."; return 0 ;;
    *) echo "REFUSE: powermetrics census is unavailable: $output" >&2; return 1 ;;
  esac
}

echo "ED-QUALIFICATION keyboard-backlight rail probe"
echo "evidence_root=$RUN_ROOT"
echo "log=$LOG"

echo "1. Review the fixed ABBA order and capture contract."
echo "arms=max-1,off-1,off-2,max-2"
echo "capture_seconds_per_arm=30 samplers=$SAMPLERS format=plist"
echo "Keep every non-keyboard-backlight condition unchanged across all four arms."

echo "2. Confirm non-interactive sudo before any live sampler starts."
if [ "$DRY_RUN" -eq 1 ]; then
  echo "DRY-RUN: sudo probe skipped."
else
  if [ ! -x /usr/bin/sudo ]; then
    echo "REFUSE: /usr/bin/sudo is missing; install/restore sudo before qualification." >&2
    exit 1
  fi
  if ! /usr/bin/sudo -n /usr/bin/true; then
    echo "REFUSE: sudo -n is unavailable. Fix the governed passwordless powermetrics sudoers entry; do not enter a password inside this script." >&2
    exit 1
  fi
  echo "PASS: sudo -n authorization is available."
fi

echo "3. Require an empty sampler census before the ABBA sequence."
if ! require_empty_sampler_census; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY-RUN: census refusal recorded without starting a sampler."
  else
    echo "Stop and identify the sampler owner or restore the process census before retrying." >&2
    exit 1
  fi
fi

echo "4. Capture the four 30-second ABBA arms."
for arm in "${ARMS[@]}"; do
  capture="$RUN_ROOT/$arm.plist"
  case "$arm" in
    max-*) instruction="Set keyboard backlight to maximum." ;;
    off-*) instruction="Set keyboard backlight to zero/off." ;;
  esac
  echo "4.${arm}: $instruction"
  echo "command=/usr/bin/sudo -n /usr/bin/powermetrics -b 0 -i 1000 -n 30 --samplers $SAMPLERS --format plist -o $capture"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY-RUN: prompt and 30-second capture skipped for $arm."
    continue
  fi
  printf "Press Return only after the requested backlight level is visually stable: "
  IFS= read -r _confirmation
  /usr/bin/sudo -n /usr/bin/powermetrics \
    -b 0 -i 1000 -n 30 \
    --samplers "$SAMPLERS" \
    --format plist \
    -o "$capture"
  if ! require_empty_sampler_census; then
    echo "REFUSE: sampler teardown after arm $arm is not proven." >&2
    exit 1
  fi
  echo "PASS: arm $arm captured and sampler exited."
done

echo "5. Parse rail energy and compare max-versus-off deltas."
if [ "$DRY_RUN" -eq 1 ]; then
  echo "DRY-RUN: parser skipped; expected inputs are $RUN_ROOT/{max-1,off-1,off-2,max-2}.plist."
else
  cd "$REPO_ROOT"
  "$PYTHON" - "$RUN_ROOT" "$RESULT" <<'PY'
import json
import statistics
import sys
from pathlib import Path

from joulewise.adapters.powermetrics import parse_powermetrics_records

run_root = Path(sys.argv[1])
result_path = Path(sys.argv[2])
arms = ("max-1", "off-1", "off-2", "max-2")
rails = ("cpu_power", "gpu_power", "ane_power")
results = {}
for arm in arms:
    records = parse_powermetrics_records((run_root / f"{arm}.plist").read_bytes())
    if len(records) < 20:
        raise SystemExit(
            f"REFUSE: {arm} has only {len(records)} complete records; expected at least 20"
        )
    duration_s = sum(record.elapsed_ns for record in records) / 1_000_000_000
    mean_power_w = {
        rail: statistics.fmean(record.rail_power_w[rail] for record in records)
        for rail in rails
    }
    energy_j = {
        rail: sum(
            record.rail_power_w[rail] * record.elapsed_ns / 1_000_000_000
            for record in records
        )
        for rail in rails
    }
    results[arm] = {
        "records": len(records),
        "duration_s": duration_s,
        "mean_power_w": mean_power_w,
        "consumed_rail_energy_j": energy_j,
        "consumed_rail_total_energy_j": sum(energy_j.values()),
    }

def deltas(max_arm, off_arm):
    return {
        rail: results[max_arm]["consumed_rail_energy_j"][rail]
        - results[off_arm]["consumed_rail_energy_j"][rail]
        for rail in rails
    }

pair_deltas = {
    "max-1_minus_off-1": deltas("max-1", "off-1"),
    "max-2_minus_off-2": deltas("max-2", "off-2"),
}
aggregate_delta = {
    rail: statistics.fmean(
        results[arm]["consumed_rail_energy_j"][rail]
        for arm in ("max-1", "max-2")
    )
    - statistics.fmean(
        results[arm]["consumed_rail_energy_j"][rail]
        for arm in ("off-1", "off-2")
    )
    for rail in rails
}
document = {
    "schema_version": "joulewise.ed_qualification_keyboard_backlight_rail_probe.v1",
    "arm_order": list(arms),
    "samplers": "battery,cpu_power,gpu_power,ane_power,thermal",
    "capture_seconds_per_arm": 30,
    "arms": results,
    "pair_consumed_rail_energy_delta_j": pair_deltas,
    "aggregate_max_minus_off_consumed_rail_energy_delta_j": aggregate_delta,
}
result_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
for arm in arms:
    row = results[arm]
    print(
        f"arm={arm} records={row['records']} duration_s={row['duration_s']:.6f} "
        f"consumed_rail_total_energy_j={row['consumed_rail_total_energy_j']:.9f}"
    )
for pair, values in pair_deltas.items():
    print("pair=" + pair + " " + " ".join(f"{rail}_delta_j={values[rail]:.9f}" for rail in rails))
print(
    "aggregate=max_minus_off "
    + " ".join(f"{rail}_delta_j={aggregate_delta[rail]:.9f}" for rail in rails)
)
print(f"result_json={result_path}")
PY
fi

echo "6. Perform the final orphan census and preserve the evidence paths."
if ! require_empty_sampler_census; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY-RUN: final census refusal recorded without starting a sampler."
  else
    echo "REFUSE: final teardown is not qualified until an empty census is observed." >&2
    exit 1
  fi
fi
if [ "$DRY_RUN" -eq 1 ]; then
  echo "DRY-RUN COMPLETE: ABBA order, prompts, sampler argv, and parser are staged."
else
  echo "PASS: ABBA rail probe complete; preserve $RUN_ROOT."
fi
