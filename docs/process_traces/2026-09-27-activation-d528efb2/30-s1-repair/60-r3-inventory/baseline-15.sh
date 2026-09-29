#!/bin/zsh
# Baseline for S1-REPAIR-ROUTE-01 stop condition 5: the 15 R3-1 failing modules
# run on 5283d7d0 merged with main (the pre-gate-fix tree), per-test IDs.
set -u
WT=/Users/edr/code/JouleWise-wt-s1-base-d528efb2
OUT=/tmp/s1-base15-d528efb2
H=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair
if [ ! -d "$WT" ]; then
  git -C /Users/edr/code/JouleWise-wt-bk-77b1bee2 worktree add -q --detach "$WT" 5283d7d0 || exit 2
  git -C "$WT" -c user.name="Ed R" merge -q --no-edit origin/main || exit 3
fi
rm -rf "$OUT"; mkdir -p "$OUT/mod" "$OUT/tmp"
export TMPDIR="$OUT/tmp/"
cd "$WT" || exit 4
git rev-parse HEAD > "$OUT/head.txt"
printf '%s\n' tests.test_arm_readiness_lifecycle tests.test_bfgs_window_consumers tests.test_analysis_integration \
  tests.test_floor_mint_estimator tests.test_floor_extraction tests.test_mint_floor_artifact \
  tests.test_mint_floor_artifact_generalized tests.test_night_gate tests.test_paper_custody \
  tests.test_paper_rendering tests.test_paper_reported_energy tests.test_launch_window \
  tests.test_run_campaign tests.test_window_duration_margins tests.test_whole_window > "$OUT/modules.txt"
: > "$OUT/rc.txt"
xargs -n 1 -P 6 "$H/one_module.sh" "$OUT" /opt/homebrew/bin/python3 "$H/run_module_ids.py" < "$OUT/modules.txt"
/opt/homebrew/bin/python3 -B - "$OUT" /tmp/s1-r3inv-d528efb2 <<'PY'
import json, os, sys
base, r3 = sys.argv[1:3]
def bad(root):
    out = set()
    for f in os.listdir(os.path.join(root, "mod")):
        if f.endswith(".json"):
            d = json.load(open(os.path.join(root, "mod", f)))
            out |= {k for k, v in d["outcomes"].items() if v in ("fail", "error")}
    return out
mods = [m.strip() for m in open(os.path.join(base, "modules.txt"))]
b = bad(base)
r = {x for x in bad(r3) if any(x.startswith(m + ".") for m in mods)}
turned = sorted(r - b)
open(os.path.join(base, "turned_by_gate_fix.txt"), "w").write("".join(t + "\n" for t in turned))
print(f"baseline_bad={len(b)} r3_bad={len(r)} turned_by_gate_fix={len(turned)} cured_between={len(b - r)}")
PY
