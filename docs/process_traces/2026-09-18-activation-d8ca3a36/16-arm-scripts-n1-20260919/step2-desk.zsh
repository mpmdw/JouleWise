#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
cd "$MEASUREMENT_ROOT" || exit 3
echo "== discovery (informational; watchdog fences active spans only):"; setopt BARE_GLOB_QUAL; print -rl -- /Users/edr/night-custody/*/night_plan.json(N) || true
echo "== epoch checks"
# rc 3 is the explained os_build 25F84 -> 25G83 mismatch (and the
# corresponding sampler replacement), not general permission to ignore errors.
# The magistrate must read both reports and stop on any unexplained error.
set +e
"$PY" scripts/issue_calibration_acceptance_generation.py check; check_rc=$?
"$PY" scripts/issue_calibration_acceptance_generation.py check --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md; prereg_rc=$?
set -e
echo "check_rc=$check_rc prereg_rc=$prereg_rc"
print -r -- 'CHECK: test "$check_rc" -eq 3; test "$prereg_rc" -eq 3'
test "$check_rc" -eq 3; test "$prereg_rc" -eq 3
shasum -a 256 scripts/night_chains/calibration_derivation_only.zsh configs/calibration/preregistration_d079_epoch_25g83_rev1.md
git rev-parse "${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
mkdir -p "$NIGHT_ROOT" "$STAGE"
print -r -- 'CHECK: test "$(stat -f %d "$NIGHT_ROOT")" = "$(stat -f %d "$STAGE")"'
test "$(stat -f %d "$NIGHT_ROOT")" = "$(stat -f %d "$STAGE")"
cp configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json "$CALIBRATION_PLAN"
print -- "CHECK: byte equality" configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json "$CALIBRATION_PLAN"
cmp configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json "$CALIBRATION_PLAN"
"$PY" scripts/write_derivation_night_inputs.py --out-dir "$NIGHT_ROOT"
"$PY" -B - <<'PY'
import hashlib, os, time
from pathlib import Path
from joulewise.night_gate import NightPlan,D166_REGISTRATION_PATH,D166_REGISTRATION_SHA256
from joulewise.night_plan_writer import write_night_plan
e=os.environ
a=int(time.time()); t=int(e["T0_EPOCH_S"])
print('CHECK: t%60==0 and 0<=t-a<=129600 and a<t-600, (t,a)', flush=True)
assert t%60==0 and 0<=t-a<=129600 and a<t-600, (t,a)
print('CHECK: hashlib.sha256((Path(e["MEASUREMENT_ROOT"])/D166_REGISTRATION_PATH).read_bytes()).hexdigest()==D166_REGISTRATION_SHA256', flush=True)
assert hashlib.sha256((Path(e["MEASUREMENT_ROOT"])/D166_REGISTRATION_PATH).read_bytes()).hexdigest()==D166_REGISTRATION_SHA256
p=NightPlan.from_mapping({
 "schema":"joulewise.night_plan.v2","schema_version":2,
 "plan_id":e["PLAN_ID"],"receipt_class":"DIAGNOSTIC_NO_PACK",
 "t0_epoch_s":t,"window_max_s":9000,"authored_epoch_s":a,
 "repo_head":e["H"],"measurement_root":e["MEASUREMENT_ROOT"],
 "measurement_head":e["H"],"chain_path":e["NIGHT_ROOT"]+"/chain.zsh",
 "chain_sha256_path":e["NIGHT_ROOT"]+"/chain.zsh.sha256",
 "custody_root":e["NIGHT_ROOT"],"registration_path":D166_REGISTRATION_PATH})
target=Path(e["STAGED_PLAN"])
print('CHECK: not target.exists() and not target.is_symlink()', flush=True)
assert not target.exists() and not target.is_symlink()
print(write_night_plan(target,p))
PY
gen() { "$PY" -B scripts/gen_derivation_night.py --plan "$1" --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" --calibration-plan "$CALIBRATION_PLAN" --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" "${@:2}"; }
"$PY" -B scripts/gen_derivation_night.py --check
gen "$STAGED_PLAN"
gen "$STAGED_PLAN" --verify
/bin/zsh -n "$NIGHT_ROOT/chain.zsh"
python3 scripts/run_night.py preflight --plan "$STAGED_PLAN"
scripts/install_night_agent.sh --plan "$STAGED_PLAN" --python "$PY" --render-only "$STAGE/rendered-agents"
"$PY" -B scripts/run_night.py schedule --plan "$STAGED_PLAN" > "$STAGE/schedule.json"
cat "$STAGE/schedule.json"
ls -la "$NIGHT_ROOT" "$STAGE"
echo "STEP2 OK"
