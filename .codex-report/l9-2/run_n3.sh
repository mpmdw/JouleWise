#!/usr/bin/env bash
# Short modules at this head, then the N3 per-site fault injection alone.
here=$(cd "$(dirname "$0")" && pwd); src=$(cd "$here/../.." && pwd); out=$1
# Resumable: short modules run once; N3 keeps reported children and restarts its parent.
[ -f "$out/short/ALL_DONE" ] || "$here/run_short.sh" "$out/short"
rm -rf "${out:?}/n3/tmp"; mkdir -p "$out/n3/tmp"
cd "$src"
echo "head=$(git rev-parse HEAD) start=$(date -u +%FT%TZ)" > "$out/n3/meta"
"$here/host_sampler.sh" "$out/n3/host.log" 60 & sampler=$!
TMPDIR="$out/n3/tmp" PYTHONPATH="$src" JW_B5_SYNTHETIC_ONLY=1 JW_B5_S10_REAL_PROGRAMS=1 PYTHONDONTWRITEBYTECODE=1 \
  python3.13 "$here/fault_injection.py" "$out/n3" "$here/fault_injection_plan.json" > "$out/n3/run.log" 2>&1
echo $? > "$out/n3/exit"
kill $sampler
python3.13 "$here/fault_injection_check.py" "$out/n3" > "$out/n3/verdicts.md" 2>&1
touch "$out/ALL_DONE"
