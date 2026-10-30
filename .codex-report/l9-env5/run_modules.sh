#!/usr/bin/env bash
# usage: run_modules.sh MODULE_LIST_FILE OUT_DIR JOBS  (run from the checkout root)
set -u
list=$1; out=$2; jobs=$3
mkdir -p "$out"
export TMPDIR=/tmp/lnine-env5/tmp JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
xargs -P "$jobs" -I{} sh -c 'python3.13 -m unittest {} > "$0/{}.log" 2>&1; true' "$out" < "$list"
for m in $(cat "$list"); do
  f="$out/$m.log"
  printf '%s | %s | %s\n' "$m" "$(grep -E '^Ran ' "$f" | tail -n 1)" "$(tail -n 1 "$f")"
done
