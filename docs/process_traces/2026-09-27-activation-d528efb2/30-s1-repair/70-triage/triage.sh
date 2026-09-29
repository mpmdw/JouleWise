#!/bin/zsh
# S1-REPAIR-ROUTE-01 §5.1 / step R3-2: the lead's triage by script.
# Runs each failing module of the round-3 inventory on MAIN's tree under the recorder,
# then classifies every failing candidate test id (T1..T6 proposal; the lead confirms).
set -u
HERE=${0:A:h}
MAIN_WT=/Users/edr/code/JouleWise-wt-s1-ref-d528efb2      # main e7c8bcc6 (code-identical to 9eab16f8)
INV=/tmp/s1-r3inv-d528efb2                                 # round-3 inventory (candidate tree 0c469057)
OUT=/tmp/s1-triage-d528efb2
rm -rf "$OUT"; mkdir -p "$OUT/log" "$OUT/tmp"
export TMPDIR="$OUT/tmp/"
grep -v ' rc=0$' "$INV/rc.txt" | sed 's/ rc=.*//' | sort > "$OUT/modules.txt"
cd "$MAIN_WT" || exit 2
run_one() {
  m=$1
  TRIAGE_LOG="$OUT/log/$m.jsonl" PYTHONPATH="$HERE/recorder" /opt/homebrew/bin/python3 -B -m unittest "$m" < /dev/null > "$OUT/log/$m.out" 2>&1
  echo "$m rc=$?" >> "$OUT/rc.txt"
}
: > "$OUT/rc.txt"
for m in $(cat "$OUT/modules.txt"); do
  while [ $(jobs -r | wc -l) -ge 6 ]; do sleep 2; done
  run_one "$m" &
done
wait
/opt/homebrew/bin/python3 -B "$HERE/classify.py" "$OUT" "$INV" /tmp/s1-ref-d528efb2 > "$OUT/table.md"
tail -20 "$OUT/table.md"
