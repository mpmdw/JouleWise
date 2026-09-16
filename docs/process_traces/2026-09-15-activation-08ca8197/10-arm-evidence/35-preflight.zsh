#!/bin/zsh
# Pre-notice block: attempt dir (§1.4a step 4-5), schedule + boundaries (§1.3), --render-only validation (§1.4), arm census (§0.6 step 3b).
source /tmp/magistrate-08ca8197/stage/exports.zsh
: "${H:?}" "${PY:?}" "${STAGED_PLAN:?}" "${STAGE:?}"
export ARM_ATTEMPT="${ARM_ATTEMPT:-1}"
ATTEMPT_DIR="$STAGE/arm-attempts/$(printf '%06d' "$ARM_ATTEMPT")"
export ATTEMPT_DIR
mkdir -p "$STAGE/arm-attempts"
mkdir "$ATTEMPT_DIR"                 # existing attempt evidence is a stop
cp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
print -r -- '[]' > "$ATTEMPT_DIR/attempts.json"
echo "ATTEMPT_DIR=$ATTEMPT_DIR"
shasum -a 256 "$ATTEMPT_DIR/plan.json"
cd "$MEASUREMENT_ROOT"
test "$(git rev-parse HEAD)" = "$H"
echo "=== §1.3 schedule"
"$PY" -B scripts/run_night.py schedule --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/schedule.json"
"$PY" -B - "$STAGED_PLAN" "$(date +%Y-%m-%d)" <<'PY' | tee "$ATTEMPT_DIR/boundaries.txt"
import json, sys
from datetime import date, datetime
from pathlib import Path
from joulewise.night_gate import NightPlan
from scripts.run_night import (COURIER_DEADLINE_S, deadman_epoch, install_close_epoch, install_spans_for_day)
from scripts.magistrate_watchdog import PLAN_LEAD_S
plan = NightPlan.from_mapping(json.loads(Path(sys.argv[1]).read_text()))
def show(label, epoch):
    print(label, datetime.fromtimestamp(epoch).astimezone().isoformat(), epoch)
for i, (start, end) in enumerate(install_spans_for_day(date.fromisoformat(sys.argv[2])), 1):
    show(f"install span {i} open", start)
    show(f"install span {i} close (excluded)", end)
show("install close (excluded)", install_close_epoch(plan))
show("plan span / exit boundary", plan.t0_epoch_s - PLAN_LEAD_S)
show("t0", plan.t0_epoch_s)
show("completion / courier deadline", plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S)
show("dead-man", deadman_epoch(plan))
PY
echo "=== §1.4 --render-only validation of the STAGED plan (no launchctl)"
rm -rf "$STAGE/rendered-agents"
scripts/install_night_agent.sh --render-only "$STAGE/rendered-agents" --plan "$STAGED_PLAN" --python "$PY"; echo "render-only rc=$?"
ls -la "$STAGE/rendered-agents"
echo "=== §0.6 step 3b arm census (stub: idle interactive sessions not foreign; workloads block)"
set +e
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" 2>&1 | tee "$ATTEMPT_DIR/arm-census-preflight.txt"
rc=${pipestatus[1]}
set -e
echo "arm census rc=$rc"
echo "PREFLIGHT DONE $(date '+%H:%M:%S') census_rc=$rc"
exit $rc
