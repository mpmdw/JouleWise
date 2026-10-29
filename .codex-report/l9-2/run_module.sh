#!/usr/bin/env bash
# Detached durable runner: one module, fresh TMPDIR, log/exit/timing files.
# usage: run_module.sh <run-dir> <module> [observed]
set -u
run=$1; module=$2; mode=${3:-plain}
src=$(cd "$(dirname "$0")/../.." && pwd)
mkdir -p "$run"
tmp="$run/tmp/${module//./_}"; rm -rf "$tmp"; mkdir -p "$tmp"
log="$run/${module//./_}.log"
export TMPDIR="$tmp" PYTHONPATH="$src" JW_B5_SYNTHETIC_ONLY=1 JW_B5_S10_REAL_PROGRAMS=1 PYTHONDONTWRITEBYTECODE=1
cd "$src"
echo "head=$(git rev-parse HEAD) module=$module mode=$mode start=$(date -u +%FT%T.%NZ) nproc=$(nproc)" > "$run/${module//./_}.meta"
free -b >> "$run/${module//./_}.meta"
start=$(date +%s.%N)
if [ "$mode" = observed ]; then
  L9_2_SAMPLE_LOG="$run/${module//./_}.samples.jsonl" python3.13 .codex-report/l9-2/observed_unittest.py -v "$module" > "$log" 2>&1
else
  python3.13 -m unittest -v "$module" > "$log" 2>&1
fi
code=$?
end=$(date +%s.%N)
echo "$code" > "$run/${module//./_}.exit"
python3.13 - "$start" "$end" "$code" "$log" "$run/${module//./_}.result.json" "$module" <<'EOF'
import sys, json, hashlib, re
start, end, code, log, out, module = sys.argv[1:]
text = open(log, errors='replace').read()
m = re.search(r'^Ran (\d+) tests? in', text, re.M)
f = re.search(r'^FAILED \((.*)\)$', text, re.M)
counts = dict(failures=0, errors=0, skipped=0)
if f:
    for part in f.group(1).split(','):
        k, v = part.strip().split('='); counts[k] = int(v)
s = re.search(r'^OK \(skipped=(\d+)\)', text, re.M)
if s: counts['skipped'] = int(s.group(1))
json.dump(dict(module=module, tests=int(m.group(1)) if m else None, **counts, exit=int(code),
               wall_s=round(float(end) - float(start), 3),
               log_sha256=hashlib.sha256(open(log, 'rb').read()).hexdigest()), open(out, 'w'))
EOF
