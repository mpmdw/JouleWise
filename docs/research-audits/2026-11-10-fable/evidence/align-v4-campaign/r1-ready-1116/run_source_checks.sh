#!/bin/zsh
# Off measurement host only. Synthetic tests; never install or arm.
set -euo pipefail
[[ $# == 2 ]] || { print -u2 'usage: run_source_checks.sh SOURCE_WORKTREE NEW_LOG_DIRECTORY'; exit 1; }
SOURCE=${1:A}
LOG=${2:A}
HERE=${0:A:h}
PY=${R1_TEST_PYTHON:-python3.13}
mkdir "$LOG"
cd "$SOURCE"
"$PY" -B "$HERE/verify_sources.py" "$SOURCE" > "$LOG/source-check.json"
export JW_B5_SYNTHETIC_ONLY=1
export PYTHONPATH="$SOURCE:$SOURCE/tests"
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR=$(mktemp -d /tmp/jw-r1-checks.XXXXXX)
trap 'rmdir "$TMPDIR" 2>/dev/null || true' EXIT
check_modules=(tests.align.test_rl145_gate_hashes tests.align.test_w1_rl122_kit
 tests.align.test_rl149_typical_case tests.align.test_rl149_blackout
 tests.align.test_rl145_night_confirmation tests.align.test_rl145_part_c
 tests.align.test_v4_kit tests.align.test_r1_arm)
for module in $check_modules; do
  "$PY" -B -m unittest "$module" > "$LOG/$module.log" 2>&1
  tail -4 "$LOG/$module.log"
done
"$PY" -B "$SOURCE/scripts/arm_align_r1.py" size --t0 1795075200 > "$LOG/size-thu0000.json"
date '+%Y-%m-%d %H:%M:%S %Z' > "$LOG/finished.txt"
print -r -- "OFF-HOST SOURCE CHECKS PASSED; no native READY claim. Logs $LOG"
