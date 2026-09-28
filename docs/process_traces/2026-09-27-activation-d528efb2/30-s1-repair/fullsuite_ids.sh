#!/bin/zsh
# Full suite with per-test outcome IDs (S1-REGRESSION-01 §7.3 check 8 / §7.4 record).
# Usage: fullsuite_ids.sh <worktree> <outdir>. Runs every tests/test_*.py module in its own
# process (run_module_ids.py), 6 at a time, stdin closed; writes per-module JSON + logs,
# the skipped / failed / errored ID lists and a summary.
set -u
HERE=${0:A:h}
WT=$1; OUT=$2; PY=/opt/homebrew/bin/python3
mkdir -p "$OUT/mod" "$OUT/tmp"
cd "$WT" || exit 2
export TMPDIR="$OUT/tmp/"
HEAD=$(git rev-parse HEAD)
ls tests/test_*.py | sed 's#/#.#; s#\.py$##' | sort > "$OUT/modules.txt"
: > "$OUT/rc.txt"
xargs -n 1 -P 6 "$HERE/one_module.sh" "$OUT" "$PY" "$HERE/run_module_ids.py" < "$OUT/modules.txt"
$PY -B - "$OUT" "$HEAD" "$PY" <<'PYEOF'
import json, os, sys
out, head, py = sys.argv[1:4]
mods = [m.strip() for m in open(os.path.join(out, "modules.txt")) if m.strip()]
ids = {"skip": [], "fail": [], "error": []}
tests = 0; missing = []
for m in mods:
    p = os.path.join(out, "mod", m + ".json")
    if not os.path.exists(p):
        missing.append(m); continue
    d = json.load(open(p)); tests += d["tests_run"]
    for tid, o in d["outcomes"].items():
        if o in ids: ids[o].append(tid)
for k, v in ids.items():
    open(os.path.join(out, f"{k}_ids.txt"), "w").write("".join(sorted(x + "\n" for x in v)))
open(os.path.join(out, "missing_modules.txt"), "w").write("".join(x + "\n" for x in missing))
rc_all = open(os.path.join(out, "rc.txt")).read().splitlines()
nonzero = [l for l in rc_all if not l.endswith("rc=0")]
summary = (f"head={head}\ncmd=fullsuite_ids.sh (run_module_ids.py per module, 6-way, {py} -B, stdin closed)\n"
           f"TMPDIR={os.environ.get('TMPDIR')}\nmodules={len(mods)} rc_lines={len(rc_all)} "
           f"missing_json={len(missing)} tests={tests} failures={len(ids['fail'])} errors={len(ids['error'])} "
           f"skipped={len(ids['skip'])} nonzero_modules={len(nonzero)}\n")
open(os.path.join(out, "summary.txt"), "w").write(summary)
print(summary, end="")
PYEOF
