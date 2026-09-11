#!/bin/zsh
set -euo pipefail
: "${H_PRIME:?Set H_PRIME to the full committed handback hash from the notice}"
: "${DRIVER_SOURCE:?the arming activation's authorized linked worktree}"
export H_PRIME DRIVER_SOURCE
export STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260912-checkout
export NIGHT_CUSTODY=/Users/edr/night-custody/rehearsal-20260912
export STAGE=/private/tmp/joulewise-rehearsal-20260912-staging
export SCRATCH=/private/tmp/joulewise-rehearsal-20260912-validate
export PYTHONDONTWRITEBYTECODE=1
test "$DRIVER_SOURCE" != /Users/edr/code/JouleWise
for p in "$STAGE" "$SCRATCH" "$STUB_CHECKOUT" "$NIGHT_CUSTODY"; do
  test ! -e "$p"
  test ! -L "$p"
done
mkdir "$STAGE" "$SCRATCH"
# Capture foreground output, including failures; a missing final rc=0 is not success.
exec > >(tee "$STAGE/arm-blockA-output.txt") 2>&1
cat > "$STAGE/preconditions.py" <<'PY'
import json, os, subprocess, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

zone = ZoneInfo("America/Los_Angeles")
now = time.time()
print("arm clock:", now, datetime.fromtimestamp(now, zone).isoformat(), flush=True)
# C-5: install on 2026-09-11 local, after 07:00 PDT, and after the chosen
# hour:minute (00:30) has already passed that day -- trivially true for hour 0.
assert now > datetime(2026, 9, 11, 7, 0, tzinfo=zone).timestamp(), "before 07:00 PDT 09-11"
assert now < 1789196700, "at or beyond the 00:05 PDT 09-12 exit boundary"
assert datetime.fromtimestamp(1789198200).strftime('%Y-%m-%d %H:%M') == '2026-09-12 00:30', 'system local time differs from the pinned launchd time'
local = datetime.fromtimestamp(now, zone)
second = local.hour * 3600 + local.minute * 60 + local.second
assert not (2*3600 + 45*60 <= second < 3*3600 + 30*60), "inside the 02:45-03:30 fixed fence"
assert not (7*3600 <= second < 7*3600 + 60), "inside the 07:00 fixed fence"
parent = Path('/Users/edr/night-custody')
stop = parent/'magistrate/standdown.request'
assert not stop.exists() and not stop.is_symlink(), "standdown requested"
assert not list(parent.glob('*/night_plan.json')), "existing plan"
services = subprocess.run(['launchctl', 'list'], capture_output=True, text=True, check=True)
matches = [line for line in services.stdout.splitlines() if 'joulewise' in line]
print('launchctl list | grep joulewise:', *matches, sep='\n', flush=True)
assert [line.split()[-1] for line in matches] == ['com.joulewise.magistrate']
# Own = the arming activation's root PID and its currently attached descendants.
# Default: the magistrate lock's PID. ARM_OWNER_PID overrides it ONLY when this
# session is not the lock's owner; the override and its reason go in the record.
override = os.environ.get('ARM_OWNER_PID')
me = int(override) if override else json.loads((parent/'magistrate/magistrate.lock').read_text())['pid']
print('own root pid:', me, '(override)' if override else '(magistrate.lock)', flush=True)
raw = subprocess.run(['ps', '-axo', 'pid=,ppid=,command='], capture_output=True, text=True, check=True).stdout
rows = {int(a): (int(b), c) for line in raw.splitlines() if line.strip()
        for a, b, c in [line.strip().split(None, 2)]}
def ancestors(pid):
    seen = set()
    while pid in rows and pid != 1 and pid not in seen:
        seen.add(pid)
        yield pid
        pid = rows[pid][0]
assert me in set(ancestors(os.getpid())), 'own root PID is not this census ancestor'
probe = subprocess.run(['/usr/bin/pgrep', '-lf', 'codex|claude|t3'], capture_output=True, text=True)
print('pgrep -lf "codex|claude|t3" rc=', probe.returncode, flush=True)
print(probe.stdout, end='', flush=True)
print(probe.stderr, end='', flush=True)
assert probe.returncode in (0, 1), 'census failed'
hits = [int(line.split(None, 1)[0]) for line in probe.stdout.splitlines() if line.strip()]
foreign = [pid for pid in hits if me not in set(ancestors(pid))]
for pid in hits:
    print('census ancestry:', pid, list(ancestors(pid)), rows.get(pid), flush=True)
print('foreign agent matches:', foreign, flush=True)
assert not foreign, 'foreign or unclassifiable process; preserve it and abort'
# Record 01 F2: the orphan tree must be gone before any arm (ruling 06 C-3).
orphans = [pid for pid in (83102, 83155, 83180, 83195, 83220, 83308, 83319) if pid in rows]
print('record-01 F2 orphan pids still present:', orphans, flush=True)
assert not orphans, 'the 83102 orphan tree is alive; Ed must clear it before arming'
PY
python3 -B "$STAGE/preconditions.py"

git -C "$DRIVER_SOURCE" fetch origin main
git -C "$DRIVER_SOURCE" cat-file -e "$H_PRIME^{commit}"
test "$(git -C "$DRIVER_SOURCE" rev-parse "$H_PRIME^{commit}")" = "$H_PRIME"
remote_main="$(git -C "$DRIVER_SOURCE" ls-remote --exit-code origin refs/heads/main)"
remote_main_head="${remote_main%%$'\t'*}"
git -C "$DRIVER_SOURCE" merge-base --is-ancestor "$H_PRIME" "$remote_main_head"
git -C "$DRIVER_SOURCE" ls-remote --exit-code origin refs/heads/night-results/20260912 && {
  print 'ABORT: night-results/20260912 already exists' >&2; exit 1
} || true
git -C "$DRIVER_SOURCE" show "$H_PRIME:docs/process/NIGHT_HANDBACK.md"
# Inspect the displayed handback against the sent notice before continuing.

git -C "$DRIVER_SOURCE" worktree add --detach "$STUB_CHECKOUT" "$H_PRIME"
test "$(git -C "$STUB_CHECKOUT" rev-parse HEAD)" = "$H_PRIME"
test -z "$(git -C "$STUB_CHECKOUT" status --short)"

cd "$STUB_CHECKOUT"
/opt/homebrew/bin/python3.13 --version
/opt/homebrew/bin/python3.13 -m venv .venv
export PY="$STUB_CHECKOUT/.venv/bin/python"
test -x "$PY"
"$PY" -c 'import sys; print(sys.executable, sys.version); assert sys.version_info[:2] >= (3, 11)'
# .venv/ is gitignored (.gitignore:6), so the tree stays clean:
test -z "$(git -C "$STUB_CHECKOUT" status --short)"
python3 -m unittest tests.test_install_night_agent tests.test_run_night

cd "$STUB_CHECKOUT"
PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'
import hashlib, os, time
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from joulewise.night_gate import NightPlan, D166_REGISTRATION_PATH, D166_REGISTRATION_SHA256
from joulewise.night_plan_writer import write_night_plan

root = Path(os.environ['NIGHT_CUSTODY'])
stage = Path(os.environ['STAGE'])
scratch = Path(os.environ['SCRATCH'])
t0 = datetime(2026, 9, 12, 0, 30, tzinfo=ZoneInfo('America/Los_Angeles')).timestamp()
assert t0 == 1789198200
assert 1789196400 <= t0 <= 1789200000, 'outside cold-gate 06 C-4 window'
now = time.time()
assert now < t0 - 25 * 60, 'past the exit boundary'
assert 0 <= t0 - now <= 36 * 3600, 'authored_epoch_s must be within 36 h of t0'
# Step 0c: C1 hashes this file and refuses anything else.
registration = D166_REGISTRATION_PATH
digest = hashlib.sha256(Path(registration).read_bytes()).hexdigest()
assert digest == D166_REGISTRATION_SHA256, (registration, digest, D166_REGISTRATION_SHA256)
print('registration_path:', registration, digest)
plan = NightPlan(plan_id='rehearsal-20260912', receipt_class='REHEARSAL_STUB',
    t0_epoch_s=t0, window_max_s=900, authored_epoch_s=now,
    repo_head=os.environ['H_PRIME'], measurement_head=os.environ['H_PRIME'],
    measurement_root=os.environ['STUB_CHECKOUT'], custody_root=str(root),
    chain_path=str(root/'chain.zsh'), chain_sha256_path=str(root/'chain.zsh.sha256'),
    registration_path=registration)
twin_root = scratch/'custody'
twin = replace(plan, custody_root=str(twin_root), chain_path=str(twin_root/'chain.zsh'),
               chain_sha256_path=str(twin_root/'chain.zsh.sha256'))
print(write_night_plan(stage/'night_plan.json', plan))
print(write_night_plan(scratch/'night_plan.json', twin))
PY

cd "$STUB_CHECKOUT"
scripts/install_night_agent.sh --plan "$SCRATCH/night_plan.json" --hour 0 --minute 30 --render-only "$SCRATCH/render"
/usr/bin/plutil -lint "$SCRATCH/render/com.joulewise.night.plist"
/usr/bin/plutil -lint "$SCRATCH/render/com.joulewise.night.deadman.plist"
python3 -B - <<'PY'
import json, os, plistlib
from pathlib import Path
render = Path(os.environ['SCRATCH'])/'render'
py = os.environ['PY']
for label, mode, hour, minute in [('com.joulewise.night', 'run', 0, 30),
                                  ('com.joulewise.night.deadman', 'dead-man', 7, 0)]:
    data = plistlib.loads((render/(label+'.plist')).read_bytes())
    print(label, 'calendar=', data['StartCalendarInterval'],
          'ProgramArguments=', data['ProgramArguments'], flush=True)
    assert data['StartCalendarInterval'] == {'Hour': hour, 'Minute': minute}
    assert data['RunAtLoad'] is False
    argv = data['ProgramArguments']
    # Ruling 06 C-2: the cured shape.
    assert argv[0] == py, (argv[0], py)
    assert argv[0].startswith('/')
    assert '/usr/bin/env' not in argv and 'python3' not in argv
    assert argv[1] == str(Path(os.environ['STUB_CHECKOUT'])/'scripts/run_night.py')
    assert argv[2] == mode
PY
python3 -B - <<'PY'
import json, os
from pathlib import Path
real = json.loads((Path(os.environ['STAGE'])/'night_plan.json').read_bytes())
twin = json.loads((Path(os.environ['SCRATCH'])/'night_plan.json').read_bytes())
diff = {k for k in real.keys() | twin.keys() if real.get(k) != twin.get(k)}
print('plan differing fields:', sorted(diff))
assert diff == {'custody_root', 'chain_path', 'chain_sha256_path'}
assert real['schema'] == 'joulewise.night_plan.v2' and real['schema_version'] == 2
assert not Path(os.environ['NIGHT_CUSTODY']).exists()
PY
print 'block A rc=0'
