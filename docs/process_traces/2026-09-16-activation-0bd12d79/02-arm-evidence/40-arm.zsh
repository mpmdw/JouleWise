#!/bin/zsh
# The arm itself (runbook §1.4 block): 83d93f5a's 40-arm.zsh with the derivation night's wrapper --verify, class and window assertions and the D-166 pin assert.
# Preconditions (operator, just before): notice sent; $ATTEMPT_DIR/notice-evidence.txt + notice.json written; directives/thread/standdown.request/STOP re-read.
source /tmp/magistrate-0bd12d79/arm/exports.zsh
: "${H:?}" "${PY:?}" "${MEASUREMENT_ROOT:?}" "${NIGHT_ROOT:?}" "${STAGE:?}" "${STAGED_PLAN:?}" "${SESSION_ID:?}" "${EVIDENCE_ROOT_ID:?}" "${CALIBRATION_PLAN:?}"
export ARM_ATTEMPT="${ARM_ATTEMPT:-1}"
export ATTEMPT_DIR="$STAGE/arm-attempts/$(printf '%06d' "$ARM_ATTEMPT")"
exec > >(tee -a "$ATTEMPT_DIR/arm-block-output.txt") 2>&1
echo "ARM BLOCK START $(date '+%Y-%m-%dT%H:%M:%S%z')"
cd "$MEASUREMENT_ROOT"
echo "=== 0. stop files"
for name in standdown.request STOP; do test ! -e "/Users/edr/night-custody/magistrate/$name"; test ! -L "/Users/edr/night-custody/magistrate/$name"; done
echo "=== 1. pins + notice evidence"
test -s "$ATTEMPT_DIR/notice-evidence.txt"
test -s "$ATTEMPT_DIR/notice.json"
test "$(git rev-parse HEAD)" = "$H"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
git fetch -q origin main
git merge-base --is-ancestor "$H" origin/main
echo "=== 2. wrapper still re-derives to the installed bytes (§1.1b step 4)"
"$PY" -B scripts/gen_derivation_night.py --plan "$STAGED_PLAN" \
  --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" \
  --calibration-plan "$CALIBRATION_PLAN" \
  --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" \
  --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" \
  --verify
echo "=== 3. staged plan checks"
cmp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
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
assert plan.window_max_s == int(os.environ['WINDOW_MAX_S']) == 9000
assert plan.t0_epoch_s == int(os.environ['T0_EPOCH_S'])
assert plan.chain_path == os.environ['NIGHT_ROOT'] + '/chain.zsh'
assert plan.chain_sha256_path == plan.chain_path + '.sha256'
assert plan.registration_path == night_gate.D166_REGISTRATION_PATH
d = hashlib.sha256((Path(os.environ['MEASUREMENT_ROOT']) / night_gate.D166_REGISTRATION_PATH).read_bytes()).hexdigest()
assert d == night_gate.D166_REGISTRATION_SHA256, ('D166 registration sha256 MISMATCH', d)
assert 0 <= time.time() - plan.authored_epoch_s <= 36 * 3600
assert 0 <= plan.t0_epoch_s - plan.authored_epoch_s <= 36 * 3600
assert time.time() < install_close_epoch(plan), 'install close passed'
assert Path(os.environ['STAGE']).stat().st_dev == Path(os.environ['NIGHT_ROOT']).stat().st_dev
print('staged plan checks PASS; seconds to install close:', int(install_close_epoch(plan) - time.time()))
PY
echo "=== 4. --render-only again from the pinned checkout"
rm -rf "$STAGE/rendered-agents"
scripts/install_night_agent.sh --render-only "$STAGE/rendered-agents" --plan "$STAGED_PLAN" --python "$PY"
echo "=== 5. final arm-time census immediately before publication (real class: any foreign process aborts)"
launchctl list | grep joulewise
test "$(launchctl list | grep joulewise | awk '{print $3}')" = "com.joulewise.magistrate"
test -z "$(print -rl -- /Users/edr/night-custody/*/night_plan.json(N))"
if "$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" 2>&1 | tee "$ATTEMPT_DIR/arm-census-final.txt"; then :; else rc=$?; print -u2 "arm census exit $rc; stop publication"; exit "$rc"; fi
echo "=== 6. publication (retry_allowed, then os.replace)"
"$PY" -B - <<'PY'
import json, os, time
from pathlib import Path
from joulewise.arm_retry import retry_allowed
from joulewise.night_gate import NightPlan, PLAN_MAX_AGE_S
from scripts.run_night import install_close_epoch
attempt_dir = Path(os.environ['ATTEMPT_DIR'])
raw = Path(os.environ['STAGED_PLAN']).read_bytes()
plan = NightPlan.from_mapping(json.loads(raw))
attempts = json.loads((attempt_dir / 'attempts.json').read_text())
notice = json.loads((attempt_dir / 'notice.json').read_text())
now = time.time()
if notice['attempt'] != int(os.environ['ARM_ATTEMPT']):
    raise SystemExit('notice belongs to a different attempt')
context = dict(plan_bytes=raw, saved_plan_bytes=(attempt_dir / 'plan.json').read_bytes(),
               reviewed_head=os.environ['H'], install_close_epoch_s=install_close_epoch(plan),
               plan_max_age_s=PLAN_MAX_AGE_S)
decision = retry_allowed(now, context, attempts, notice)
print('retry_allowed:', decision)
if not decision.allowed:
    raise SystemExit('arm refused: ' + decision.reason)
target = Path(os.environ['NIGHT_ROOT']) / 'night_plan.json'
if target.exists() or target.is_symlink():
    raise SystemExit('publication target already exists')
os.replace(os.environ['STAGED_PLAN'], target)
print('PUBLISHED', target, 'at', time.time())
PY
echo "=== 7. install both agents FROM the clone"
set +e
scripts/install_night_agent.sh --plan "$NIGHT_ROOT/night_plan.json" --python "$PY" 2>&1 | tee "$ATTEMPT_DIR/install-output.txt"
irc=${pipestatus[1]}
set -e
echo "install rc=$irc"
test "$irc" = 0
echo "=== 8. inspect"
launchctl list | grep joulewise
"$PY" -B - <<'PY'
import json, os, plistlib, subprocess
from pathlib import Path
from joulewise.night_gate import NightPlan
from scripts.run_night import schedule
labels = {line.split()[-1] for line in subprocess.check_output(['launchctl', 'list'], text=True).splitlines() if line.split()}
assert {'com.joulewise.night', 'com.joulewise.night.deadman'} <= labels
plan = NightPlan.from_mapping(json.loads((Path(os.environ['NIGHT_ROOT']) / 'night_plan.json').read_text()))
expected = schedule(plan)
for label, key in (('com.joulewise.night', 'night_calendar'), ('com.joulewise.night.deadman', 'deadman_calendar')):
    plist = plistlib.loads((Path.home() / 'Library' / 'LaunchAgents' / f'{label}.plist').read_bytes())
    assert plist['StartCalendarInterval'] == expected[key], (label, plist['StartCalendarInterval'])
print('installed calendars match plan')
night = Path(os.environ['NIGHT_ROOT']) / 'night'
entries = sorted(night.iterdir()) if night.is_dir() else []
print('post-install night/ baseline:', json.dumps([{'name': p.name, 'size': p.lstat().st_size, 'mtime_ns': p.lstat().st_mtime_ns} for p in entries]))
PY
plutil -p ~/Library/LaunchAgents/com.joulewise.night.plist | tee "$ATTEMPT_DIR/plist-night.txt"
plutil -p ~/Library/LaunchAgents/com.joulewise.night.deadman.plist | tee "$ATTEMPT_DIR/plist-deadman.txt"
cmp "$NIGHT_ROOT/night_plan.json" "$ATTEMPT_DIR/plan.json"
shasum -a 256 "$NIGHT_ROOT/night_plan.json" "$NIGHT_ROOT/chain.zsh"
pmset -g batt | head -2; pmset -g | grep -E 'powermode|lowpowermode| sleep ' || true
echo "ARMED $(date '+%H:%M:%S') plan=$NIGHT_ROOT/night_plan.json"
