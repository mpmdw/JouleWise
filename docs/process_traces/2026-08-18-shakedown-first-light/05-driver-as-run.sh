#!/bin/bash
# D-139 SHAKEDOWN DRIVER — nonclaim instrument verification (2026-08-18)
# Authorized: Ed's explicit license 2026-08-18 ~02:10 PT ("yes you've got the
# license for all that makes sense in pursuit of a solid paper", following the
# stated plan: quiet-state baseline + calibration-only capture, D-127 clock
# vectors). The 2026-08-15 NOT-READY council gate continues to bind CLAIM
# windows; this run is diagnostic/nonclaim per the scout card
# (sol-shakedown-scout.md) and docs/contracts/powermetrics_fiducial.md:109-121.
# Ledger isolation: production validator runs inside a disposable clone at the
# transaction head; the canonical calibration ledger is never touched.
set -euo pipefail

STAMP=$(date '+%Y%m%dT%H%M%S')
CUST=/Users/edr/JouleWise-window-custody/shakedown-20260818
CLONE="$CUST/clone"
LOG="$CUST/driver-$STAMP.log"
mkdir -p "$CUST/quiet-state-baseline" "$CUST/runs" "$CUST/fences"
exec > >(/usr/bin/tee -a "$LOG") 2>&1
restore_clock() {
  /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on > "$CUST/fences/clock-restored.txt" 2>&1 || true
}
trap restore_clock EXIT

echo "== 0 fences: census (pre), power, thermal, display"
{ /usr/bin/pgrep -x caffeinate; echo "exit=$?"; } > "$CUST/fences/census-keepawake-pre.txt" 2>&1 || true
{ /usr/bin/pgrep -lf 'codex|claude|t3'; echo "exit=$?"; } > "$CUST/fences/census-agent-pre.txt" 2>&1 || true
{ /usr/bin/pgrep -lf 'powermetrics|window-chain|run_campaign|tail -f|watch'; echo "exit=$?"; } > "$CUST/fences/census-monitor-pre.txt" 2>&1 || true
pmset -g batt | head -2 > "$CUST/fences/power-state.txt"
pmset -g therm > "$CUST/fences/thermal-state.txt" 2>&1 || true

echo "== 1 clock: D-127 disable (hygiene, custodied; prior state = On per Ed's qualification clock-post-state.txt; the get vector is deliberately not NOPASSWD)"
echo "prior_state=On (operator qualification record ed-qual-20260817/clock-post-state.txt)" > "$CUST/fences/clock-prior-state.txt"
/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off >> "$CUST/fences/clock-prior-state.txt" 2>&1

if [ -s "$CUST/quiet-state-baseline/powermetrics_idle_baseline.plist" ]; then
  echo "== 2/3 SKIP: baseline already captured on a prior fenced run"
  SKIP_BASELINE=1
else
  SKIP_BASELINE=0
fi
echo "== 2 display to sleep (transient), then settle idle >=10 min"
/usr/bin/pmset displaysleepnow || true
if [ "$SKIP_BASELINE" -eq 1 ]; then
  sleep 300
else
  sleep 660
  echo "== 3 quiet-state baseline: 600 x 1s production-sampler idle capture"
  /usr/bin/sudo -n /usr/bin/powermetrics -b 0 -i 1000 -n 600 \
    --samplers cpu_power,gpu_power,ane_power,thermal --format plist \
    -o "$CUST/quiet-state-baseline/powermetrics_idle_baseline.plist"
  echo "baseline exit=$?"
fi

echo "== 4 three v3 calibration bundles (isolated clone ledger)"
cd "$CLONE"
for i in 1 2 3; do
  echo "-- bundle $i"
  "$CLONE/.venv/bin/python" "$CLONE/scripts/validate_powermetrics_fiducial.py" \
    --allow-live --power-policy ac_high_power \
    --output-root "$CUST/runs/instrument_validation"
  echo "bundle $i exit=$?"
  sleep 30
done

echo "== 5 clock restore + verify"
/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on > "$CUST/fences/clock-restored.txt" 2>&1
echo "restore exit=$?" >> "$CUST/fences/clock-restored.txt"

echo "== 6 census (post)"
{ /usr/bin/pgrep -lf 'powermetrics|window-chain|run_campaign|tail -f|watch'; echo "exit=$?"; } > "$CUST/fences/census-monitor-post.txt" 2>&1 || true
{ /usr/bin/pgrep -x powermetrics; echo "exit=$?"; } > "$CUST/fences/census-orphan-post.txt" 2>&1 || true

echo "SHAKEDOWN DRIVER: COMPLETE $(date '+%Y-%m-%dT%H:%M:%S%z')"
