#!/bin/zsh
# Runbook §1.4 "The arm itself, in one foreground block" (revision 7), unchanged except:
#  - census step 4 is the runbook 68 preconditions.py classification (own vs foreign), aborting on foreign;
#  - output tee'd to $STAGE/arm-block-output.txt for the arm evidence.
source /tmp/magistrate-b58fb582/exports.zsh
set -euo pipefail
: "${H:?}" "${PY:?}" "${MEASUREMENT_ROOT:?}" "${NIGHT_ROOT:?}" "${STAGE:?}" "${STAGED_PLAN:?}"
: "${SESSION_ID:?}" "${EVIDENCE_ROOT_ID:?}" "${CALIBRATION_PLAN:?}" "${NIGHT_HOUR:?}" "${NIGHT_MINUTE:?}"
exec > >(tee -a "$STAGE/arm-block-output.txt") 2>&1
echo "ARM BLOCK START $(date '+%Y-%m-%dT%H:%M:%S%z')"
cd "$MEASUREMENT_ROOT"

# 0. Install span, stand-down request, STOP, directives were checked by the operator just before; re-assert the mechanical ones.
python3 -B - <<'PY'
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
zone = ZoneInfo("America/Los_Angeles"); now = time.time()
start = datetime(2026, 9, 12, 3, 0, tzinfo=zone).timestamp(); end = datetime(2026, 9, 12, 6, 30, tzinfo=zone).timestamp()
print("arm clock:", now, datetime.fromtimestamp(now, zone).isoformat())
assert start <= now < end, "outside 03:00-06:30 PDT install span"
assert datetime.fromtimestamp(1789293360).strftime('%Y-%m-%d %H:%M') == '2026-09-13 02:56', 'system local time differs from the pinned launchd time'
assert 1789293360 + 9000 + 300 < 1789308000
m = Path('/Users/edr/night-custody/magistrate')
for name in ('standdown.request', 'STOP'):
    assert not (m/name).exists() and not (m/name).is_symlink(), name
print("span/stop checks PASS")
PY

# 1. The pins still hold, and the notice really went out.
test -s "$STAGE/notice-evidence.txt"
test "$(git rev-parse HEAD)" = "$H"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
git fetch origin main
git merge-base --is-ancestor "$H" origin/main

# 2. The wrapper still re-derives to the installed bytes (§1.1b step 4).
"$PY" -B scripts/gen_derivation_night.py --plan "$STAGED_PLAN" \
  --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" \
  --calibration-plan "$CALIBRATION_PLAN" \
  --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" \
  --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" \
  --verify

# 3. The staged plan says what this night is, and the move is possible.
cp "$STAGED_PLAN" "$STAGE/arm-night_plan.json"
"$PY" -B - <<'PY'
import hashlib, json, os, time
from pathlib import Path
from joulewise import night_gate
from joulewise.night_gate import NightPlan
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
assert time.time() < plan.t0_epoch_s - 1500
assert Path(os.environ['STAGE']).stat().st_dev == Path(os.environ['NIGHT_ROOT']).stat().st_dev
print('staged plan checks PASS')
PY

# 4. The final raw census, immediately before publication (§0.6), classified by ancestry (runbook 68 preconditions).
ps -axo pid,ppid,command | grep -E 'claude (daemon run|bg-spare|bg-pty-host)|--resume' || true
python3 -B - <<'PY'
import json, os, subprocess
from pathlib import Path
parent = Path('/Users/edr/night-custody')
services = subprocess.run(['launchctl', 'list'], capture_output=True, text=True, check=True)
matches = [l for l in services.stdout.splitlines() if 'joulewise' in l]
print('launchctl list | grep joulewise:', *matches, sep='\n')
assert [l.split()[-1] for l in matches] == ['com.joulewise.magistrate'], matches
assert not list(parent.glob('*/night_plan.json')), "existing plan"
me = json.loads((parent/'magistrate/magistrate.lock').read_text())['pid']
raw = subprocess.run(['ps', '-axo', 'pid=,ppid=,command='], capture_output=True, text=True, check=True).stdout
rows = {int(a): (int(b), c) for line in raw.splitlines() if line.strip() for a, b, c in [line.strip().split(None, 2)]}
def ancestors(pid):
    seen = set()
    while pid in rows and pid != 1 and pid not in seen:
        seen.add(pid); yield pid; pid = rows[pid][0]
assert me in set(ancestors(os.getpid())), 'lock PID is not this census ancestor'
probe = subprocess.run(['pgrep', '-fl', 'codex|claude|t3'], capture_output=True, text=True)
print('pgrep -fl "codex|claude|t3" rc=', probe.returncode); print(probe.stdout, end='')
assert probe.returncode in (0, 1)
hits = [int(l.split(None, 1)[0]) for l in probe.stdout.splitlines() if l.strip()]
foreign = [pid for pid in hits if me not in set(ancestors(pid))]
for pid in hits: print('census ancestry:', pid, list(ancestors(pid)), rows.get(pid))
print('foreign agent matches:', foreign)
assert not foreign, 'foreign or unclassifiable process; preserve it and abort'
PY

# 5. Publication: the one irreversible instant.
"$PY" -B - <<'PY'
import os
from pathlib import Path
target = Path(os.environ['NIGHT_ROOT']) / 'night_plan.json'
assert not target.exists() and not target.is_symlink()
os.replace(os.environ['STAGED_PLAN'], target)
print('PUBLISHED', target)
PY

# 6. Install both agents FROM the clone.
scripts/install_night_agent.sh --plan "$NIGHT_ROOT/night_plan.json" \
  --hour "$NIGHT_HOUR" --minute "$NIGHT_MINUTE" --python "$PY"

# 7. Inspect what was actually installed, and baseline the night directory.
launchctl list | grep joulewise
"$PY" -B - <<'PY'
import json, os, subprocess
from pathlib import Path
labels = {line.split()[-1] for line in subprocess.check_output(['launchctl', 'list'], text=True).splitlines() if line.split()}
assert {'com.joulewise.night', 'com.joulewise.night.deadman'} <= labels
night = Path(os.environ['NIGHT_ROOT']) / 'night'
entries = sorted(night.iterdir()) if night.is_dir() else []
print('post-install night/ baseline:', json.dumps([{'name': p.name, 'size': p.lstat().st_size, 'mtime_ns': p.lstat().st_mtime_ns} for p in entries], indent=2))
PY
plutil -p ~/Library/LaunchAgents/com.joulewise.night.plist
plutil -p ~/Library/LaunchAgents/com.joulewise.night.deadman.plist
cmp "$NIGHT_ROOT/night_plan.json" "$STAGE/arm-night_plan.json"
shasum -a 256 "$NIGHT_ROOT/night_plan.json"
pmset -g batt | head -2; pmset -g | grep -E 'powermode|lowpowermode' || true
echo "ARM BLOCK DONE $(date '+%Y-%m-%dT%H:%M:%S%z')"
