#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
cd "$MEASUREMENT_ROOT" || exit 3
print -- "CHECK: clone HEAD still equals reviewed H and the tree is clean"
test "$(git rev-parse HEAD)" = "$H"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
print -- "CHECK: amended Revision 5, frozen calibration plan and both PR-L templates have their exact arm-time digests"
"$PY" -B - <<'PY'
import hashlib, os, re
from pathlib import Path
e = os.environ
paths = {
    "PREREG_SHA256": Path("configs/calibration/preregistration_d079_epoch_25g83_rev1.md"),
    "FROZEN_PLAN_SHA256": Path(os.environ["FROZEN_PLAN_REL"]),
    "NIGHT_TEMPLATE_SHA256": Path("configs/launchd/com.joulewise.night.plist.template"),
    "PROBE_TEMPLATE_SHA256": Path("configs/launchd/com.joulewise.night-probe.plist.template"),
}
for key, path in paths.items():
    observed = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"CHECK: sha256({path}) == {key}: {observed}", flush=True)
    assert observed == e[key]
registration = paths["PREREG_SHA256"].read_text()
count = len(re.findall(r"<PR-L-MERGE-SHA>|<TEMPLATE-SHA256:[^>]+>", registration))
print(f"CHECK: sealed launch-context placeholder count == 0: {count}", flush=True)
assert count == 0
heading = "# Revision 5 — Amendment A-R5b (2026-09-25): battery float (directive #421)"
heading_count = registration.splitlines().count(heading)
print(f"CHECK: A-R5b heading occurs exactly once: {heading_count}", flush=True)
assert heading_count == 1
print("CHECK: Revision 5 names the PR-L merge commit and both template digests", flush=True)
assert all(value in registration for value in (e["PR_L_COMMIT"], e["NIGHT_TEMPLATE_SHA256"], e["PROBE_TEMPLATE_SHA256"]))
PY
echo "== epoch checks"
# check() compares active r7 acceptance + ledger T1 against the machine.
# Revision 5 seals prospective issuance; it does not replace active r7.
# Thus both calls return 3 for 25F84 -> 25G83 plus the old sampler/MLX
# comparison; --preregistration also requires a matching registered sampler.
set +e
check_output="$("$PY" scripts/issue_calibration_acceptance_generation.py check 2>&1)"; check_rc=$?
prereg_output="$("$PY" scripts/issue_calibration_acceptance_generation.py check --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md 2>&1)"; prereg_rc=$?
set -e
print -r -- "$check_output" "$prereg_output"
echo "check_rc=$check_rc prereg_rc=$prereg_rc"
print -r -- 'CHECK: test "$check_rc" -eq 3; test "$prereg_rc" -eq 3'
test "$check_rc" -eq 3; test "$prereg_rc" -eq 3
print -- "CHECK: both reports have exactly the old os_build and sampler mismatches, no ledger error; preregistered sampler matches"
print -r -- "$check_output" | grep -Eq '^os_build[[:space:]]+25F84[[:space:]]+25G83[[:space:]]+MISMATCH$'
print -r -- "$prereg_output" | grep -Eq '^os_build[[:space:]]+25F84[[:space:]]+25G83[[:space:]]+MISMATCH$'
print -r -- "$check_output" | grep -Fxq 'mismatched fields: os_build, powermetrics_sha256'
print -r -- "$prereg_output" | grep -Fxq 'mismatched fields: os_build, powermetrics_sha256'
! print -r -- "$check_output" "$prereg_output" | grep -q '^ledger:'
print -r -- "$prereg_output" | grep -Eq '^pre-registered powermetrics sha256 [0-9a-f]{64}: match$'
shasum -a 256 scripts/night_chains/calibration_derivation_only.zsh configs/calibration/preregistration_d079_epoch_25g83_rev1.md
git rev-parse "${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
mkdir -p "$NIGHT_ROOT" "$STAGE"
print -r -- 'CHECK: test "$(stat -f %d "$NIGHT_ROOT")" = "$(stat -f %d "$STAGE")"'
test "$(stat -f %d "$NIGHT_ROOT")" = "$(stat -f %d "$STAGE")"
print -- "CHECK: frozen calibration plan source is the reviewed committed plan choice"
test -f "$FROZEN_PLAN_REL"
cp "$FROZEN_PLAN_REL" "$CALIBRATION_PLAN"
print -- "CHECK: byte equality" "$FROZEN_PLAN_REL" "$CALIBRATION_PLAN"
cmp "$FROZEN_PLAN_REL" "$CALIBRATION_PLAN"
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
"$PY" -B - <<'PY'
import hashlib, json, os, plistlib
from pathlib import Path
directory = Path(os.environ["STAGE"]) / "rendered-agents"
paths = sorted(directory.glob("*.plist"))
print("CHECK: render-only emitted exactly night and dead-man plists", flush=True)
assert {p.name for p in paths} == {"com.joulewise.night.plist", "com.joulewise.night.deadman.plist"}
evidence = {}
for path in paths:
    raw = path.read_bytes()
    plist = plistlib.loads(raw)
    print(f"CHECK: {path.name} ProcessType == Interactive", flush=True)
    assert plist["ProcessType"] == "Interactive"
    evidence[plist["Label"]] = {"ProcessType": plist["ProcessType"],
                                  "rendered_plist_sha256": hashlib.sha256(raw).hexdigest(),
                                  "path": str(path)}
target = Path(os.environ["STAGE"]) / "render-context.json"
target.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
print(f"render evidence: {target}", flush=True)
PY
"$PY" -B scripts/run_night.py schedule --plan "$STAGED_PLAN" > "$STAGE/schedule.json"
cat "$STAGE/schedule.json"
ls -la "$NIGHT_ROOT" "$STAGE"
echo "STEP2 OK"
