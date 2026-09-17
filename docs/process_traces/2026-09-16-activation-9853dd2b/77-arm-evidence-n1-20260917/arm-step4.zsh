#!/bin/zsh
set -euo pipefail
source /tmp/magistrate-9853dd2b/arm-env.zsh
export ARM_ATTEMPT=1 ATTEMPT_DIR="$STAGE/arm-attempts/000001"
cd "$MEASUREMENT_ROOT"
echo "== pre-publication observations $(date '+%Y-%m-%dT%H:%M:%S%z')"
test ! -e /Users/edr/night-custody/magistrate/standdown.request; echo "standdown.request: absent"
test ! -e /Users/edr/night-custody/magistrate/STOP; echo "STOP: absent"
gh issue list --repo mpmdw/JouleWise --label directive --state open --author mpmdw --json number,title,author > "$ATTEMPT_DIR/directives-prepub.json"; cat "$ATTEMPT_DIR/directives-prepub.json"
test -s "$ATTEMPT_DIR/notice-evidence.txt"
test "$(git rev-parse HEAD)" = "$H"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
git fetch origin main
git merge-base --is-ancestor "$H" origin/main
cmp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
"$PY" -B scripts/gen_derivation_night.py --plan "$STAGED_PLAN" --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" --calibration-plan "$CALIBRATION_PLAN" --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" --verify
"$PY" -B - <<'PY'
import hashlib, json, os, time
from pathlib import Path
from joulewise import night_gate
from joulewise.night_gate import NightPlan
from scripts.run_night import install_close_epoch
plan = NightPlan.from_mapping(json.loads(Path(os.environ['STAGED_PLAN']).read_text()))
assert plan.repo_head == plan.measurement_head == os.environ['H']
assert plan.measurement_root == os.environ['MEASUREMENT_ROOT']
assert plan.custody_root == os.environ['NIGHT_ROOT']
assert plan.receipt_class == 'DIAGNOSTIC_NO_PACK'
assert plan.window_max_s == 9000
assert plan.chain_path == os.environ['NIGHT_ROOT'] + '/chain.zsh'
assert plan.chain_sha256_path == plan.chain_path + '.sha256'
assert plan.registration_path == night_gate.D166_REGISTRATION_PATH
assert hashlib.sha256((Path(os.environ['MEASUREMENT_ROOT']) / night_gate.D166_REGISTRATION_PATH).read_bytes()).hexdigest() == night_gate.D166_REGISTRATION_SHA256
assert 0 <= time.time() - plan.authored_epoch_s <= 36 * 3600
assert 0 <= plan.t0_epoch_s - plan.authored_epoch_s <= 36 * 3600
assert time.time() < install_close_epoch(plan)
assert Path(os.environ['STAGE']).stat().st_dev == Path(os.environ['NIGHT_ROOT']).stat().st_dev
print('staged plan checks PASS')
PY
scripts/install_night_agent.sh --render-only "$STAGE/rendered-agents" --plan "$STAGED_PLAN" --python "$PY"
echo "== final arm census"
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/arm-census-final.json"
echo "== publication"
"$PY" -B - <<'PY'
import json,os,time
from pathlib import Path
from joulewise.arm_retry import retry_allowed
from joulewise.night_gate import NightPlan,PLAN_MAX_AGE_S
from scripts.run_night import install_close_epoch
e=os.environ; d=Path(e["ATTEMPT_DIR"]); raw=Path(e["STAGED_PLAN"]).read_bytes()
p=NightPlan.from_mapping(json.loads(raw))
n=json.loads((d/"notice.json").read_text())
assert n["attempt"]==int(e["ARM_ATTEMPT"])
r=retry_allowed(time.time(),dict(plan_bytes=raw,saved_plan_bytes=(d/"plan.json").read_bytes(),reviewed_head=e["H"],install_close_epoch_s=install_close_epoch(p),plan_max_age_s=PLAN_MAX_AGE_S),json.loads((d/"attempts.json").read_text()),n)
print("retry_allowed:", r)
assert r.allowed, r.reason
target=Path(e["PLAN"])
assert not target.exists() and not target.is_symlink()
os.replace(e["STAGED_PLAN"],target)
print("PUBLISHED", target, time.time())
PY
"$PY" -B scripts/gen_derivation_night.py --plan "$PLAN" --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" --calibration-plan "$CALIBRATION_PLAN" --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" --verify
echo "== launchd probe $(date '+%H:%M:%S')"
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY" --launchd-probe
echo "== probe receipt $(date '+%H:%M:%S')"
cat "$NIGHT_ROOT/night_probe_receipt.json"
"$PY" -B - <<'PY'
import json,os
from pathlib import Path
r=json.loads((Path(os.environ["NIGHT_ROOT"])/"night_probe_receipt.json").read_text())
print(json.dumps({k:r[k] for k in ("custody_elapsed_s","observations","custody_passes","outcome","custody_budget_s") if k in r},sort_keys=True))
assert r["outcome"]=="ok"
assert r["custody_elapsed_s"]*3*1.5<=r["custody_budget_s"], (r["custody_elapsed_s"], r["custody_budget_s"])
print("PROBE ADMITS")
PY
echo "== install $(date '+%H:%M:%S')"
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY"
echo "== verify"
launchctl list | grep joulewise
launchctl print "gui/$(id -u)/com.joulewise.night" | head -30
launchctl print "gui/$(id -u)/com.joulewise.night.deadman" | head -20
plutil -p /Users/edr/Library/LaunchAgents/com.joulewise.night.plist
plutil -p /Users/edr/Library/LaunchAgents/com.joulewise.night.deadman.plist
"$PY" -B scripts/run_night.py schedule --plan "$PLAN"
cmp "$PLAN" "$ATTEMPT_DIR/plan.json"
"$PY" -B - <<'PY'
import json, os, plistlib, subprocess
from pathlib import Path
from joulewise.night_gate import NightPlan
from scripts.run_night import schedule
labels = {line.split()[-1] for line in subprocess.check_output(['launchctl', 'list'], text=True).splitlines() if line.split()}
assert {'com.joulewise.night', 'com.joulewise.night.deadman'} <= labels
plan = NightPlan.from_mapping(json.loads(Path(os.environ['PLAN']).read_text()))
expected = schedule(plan)
for label, key in (('com.joulewise.night', 'night_calendar'), ('com.joulewise.night.deadman', 'deadman_calendar')):
    plist = plistlib.loads((Path.home() / 'Library' / 'LaunchAgents' / f'{label}.plist').read_bytes())
    assert plist['StartCalendarInterval'] == expected[key], (label, plist['StartCalendarInterval'])
    assert os.environ['PLAN'] in plist['ProgramArguments'], plist['ProgramArguments']
print('installed calendars match plan')
night = Path(os.environ['NIGHT_ROOT']) / 'night'
entries = sorted(night.iterdir()) if night.is_dir() else []
print('post-install night/ baseline:', json.dumps([{'name': p.name, 'size': p.lstat().st_size, 'mtime_ns': p.lstat().st_mtime_ns} for p in entries]))
PY
shasum -a 256 "$PLAN" "$NIGHT_ROOT/chain.zsh" "$NIGHT_ROOT/night_probe_receipt.json"
echo "ARMED $(date '+%Y-%m-%dT%H:%M:%S%z')"
