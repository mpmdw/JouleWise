#!/bin/bash
# SPACING PROBE — Long/Short settle discriminating experiment (nonclaim).
# Design per the repeatability diagnosis (custodied): alternate
# Long(15-min settle) -> Short(60s) -> Long -> Short -> Long -> Short,
# same v3 protocol, 165k budget, full fences, pristine ledger per bundle.
set -euo pipefail
STAMP=$(date '+%Y%m%dT%H%M%S')
CUST=/Users/edr/JouleWise-window-custody/shakedown-20260818
CLONE="$CUST/clone"
LOG="$CUST/spacing-probe-$STAMP.log"
mkdir -p "$CUST/fences"
exec > >(/usr/bin/tee -a "$LOG") 2>&1
restore_clock() {
  /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on > "$CUST/fences/clock-restored.txt" 2>&1 || true
}
trap restore_clock EXIT

echo "== fences + clock off + display sleep"
pmset -g batt | head -2 > "$CUST/fences/spacing-probe-power.txt"
pmset -g therm > "$CUST/fences/spacing-probe-thermal.txt" 2>&1 || true
/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off > /dev/null 2>&1
/usr/bin/pmset displaysleepnow || true

ARMS=(LONG SHORT LONG SHORT LONG SHORT)
for i in 0 1 2 3 4 5; do
  arm="${ARMS[$i]}"
  n=$((i+1))
  if [ "$arm" = "LONG" ]; then settle=900; else settle=60; fi
  echo "-- probe bundle $n arm=$arm settle=${settle}s start=$(date '+%H:%M:%S')"
  sleep "$settle"
  cp "$CUST/pristine-ledger.jsonl" "$CLONE/runs/calibration_observation_ledger.jsonl"
  git -C "$CLONE" checkout -- configs/calibration/calibration_ledger_head.json
  git -C "$CLONE" add -A
  git -C "$CLONE" -c user.name="spacing-probe" -c user.email="probe@local" commit -q -m "probe: pristine reset before bundle $n ($arm)" || true
  cd "$CLONE"
  set +e
  "$CLONE/.venv/bin/python" "$CLONE/scripts/validate_powermetrics_fiducial.py" \
    --allow-live --power-policy ac_high_power \
    --output-root "$CUST/runs/spacing_probe"
  echo "probe bundle $n ($arm) exit=$?"
  set -e
done

echo "SPACING PROBE: COMPLETE $(date '+%Y-%m-%dT%H:%M:%S%z')"
