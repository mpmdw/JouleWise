#!/bin/zsh
# Full suite with per-test outcome IDs (S1-REGRESSION-01 §7.3 check 8 / §7.4 record).
# Usage: fullsuite_ids.sh <worktree> <outdir>. Runs every tests/test_*.py module in its own
# process, 6 at a time, verbose; writes per-module logs, skipped/failed/errored ID lists and a summary.
set -u
WT=$1; OUT=$2; PY=/opt/homebrew/bin/python3
mkdir -p "$OUT/mod" "$OUT/tmp"
cd "$WT" || exit 2
export TMPDIR="$OUT/tmp/"
HEAD=$(git rev-parse HEAD)
ls tests/test_*.py | sed 's#/#.#; s#\.py$##' | sort > "$OUT/modules.txt"
xargs -P 6 -I{} sh -c "$PY -B -m unittest -v {} > '$OUT/mod/{}.log' 2>&1; echo \"{} rc=\$?\" >> '$OUT/rc.txt'" < "$OUT/modules.txt"
cat "$OUT"/mod/*.log | grep -E '^(test\S+) \(([^)]+)\).* \.\.\. skipped' | sed -E 's/^(test\S+) \(([^)]+)\).*/\2.\1/' | sort > "$OUT/skipped_ids.txt"
cat "$OUT"/mod/*.log | grep -E '^(FAIL|ERROR): ' | sort > "$OUT/fail_error_lines.txt"
ran=$(cat "$OUT"/mod/*.log | awk '/^Ran [0-9]+ test/{s+=$2} END{print s+0}')
nf=$(grep -c '^FAIL: ' "$OUT/fail_error_lines.txt"); ne=$(grep -c '^ERROR: ' "$OUT/fail_error_lines.txt")
nonzero=$(grep -vc ' rc=0$' "$OUT/rc.txt")
{ echo "head=$HEAD"; echo "cmd=fullsuite_ids.sh (per-module unittest -v, 6-way, $PY -B)"; echo "TMPDIR=$TMPDIR";
  echo "modules=$(wc -l < "$OUT/modules.txt" | tr -d ' ') tests=$ran failures=$nf errors=$ne skipped=$(wc -l < "$OUT/skipped_ids.txt" | tr -d ' ') nonzero_modules=$nonzero"; } > "$OUT/summary.txt"
cat "$OUT/summary.txt"
