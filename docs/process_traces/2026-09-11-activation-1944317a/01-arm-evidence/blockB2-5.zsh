#!/bin/zsh
set -euo pipefail
: "${H_PRIME:?}"
: "${DRIVER_SOURCE:?}"
export STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260912-checkout
export NIGHT_CUSTODY=/Users/edr/night-custody/rehearsal-20260912
export STAGE=/private/tmp/joulewise-rehearsal-20260912-staging
export SCRATCH=/private/tmp/joulewise-rehearsal-20260912-validate
export PY="$STUB_CHECKOUT/.venv/bin/python"
export PYTHONDONTWRITEBYTECODE=1
exec >> >(tee -a "$STAGE/arm-blockB-output.txt") 2>&1
test -s "$STAGE/notice-evidence.txt"
cat "$STAGE/notice-evidence.txt"

python3 -B "$STAGE/preconditions.py"

cd "$STUB_CHECKOUT"
mkdir -p "$NIGHT_CUSTODY"
python3 -c 'import os,sys; os.replace(sys.argv[1], sys.argv[2]); print("moved", sys.argv[2])' "$STAGE/night_plan.json" "$NIGHT_CUSTODY/night_plan.json"
cp "$NIGHT_CUSTODY/night_plan.json" "$STAGE/arm-night_plan.json"
date '+install-start epoch=%s local=%Y-%m-%dT%H:%M:%S%z'
if ! scripts/install_night_agent.sh --plan "$NIGHT_CUSTODY/night_plan.json" --hour 0 --minute 30; then
  print 'ABORT: install failed after publication; preserve this transcript'
  scripts/install_night_agent.sh --plan "$NIGHT_CUSTODY/night_plan.json" --hour 0 --minute 30 --uninstall
  cp "$NIGHT_CUSTODY/night_plan.json" "$STAGE/failed-night_plan.json"
  rm "$NIGHT_CUSTODY/night_plan.json"
  exit 1
fi
date '+install-end epoch=%s local=%Y-%m-%dT%H:%M:%S%z'

launchctl list | grep joulewise
python3 -B - <<'PY'
import json, os, plistlib, subprocess, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
root = Path(os.environ['STUB_CHECKOUT'])
plan = str(Path(os.environ['NIGHT_CUSTODY'])/'night_plan.json')
py = os.environ['PY']
rows = subprocess.run(['launchctl', 'list'], capture_output=True, text=True, check=True).stdout
labels = {line.split()[-1] for line in rows.splitlines() if line.split()}
assert {'com.joulewise.night', 'com.joulewise.night.deadman'} <= labels
for label, mode, hour, minute, stem in [
        ('com.joulewise.night', 'run', 0, 30, 'launchd.night'),
        ('com.joulewise.night.deadman', 'dead-man', 7, 0, 'launchd.deadman')]:
    p = Path('/Users/edr/Library/LaunchAgents')/(label+'.plist')
    data = plistlib.loads(p.read_bytes())
    print(label, 'calendar=', data['StartCalendarInterval'], 'program=', data['ProgramArguments'],
          'cwd=', data['WorkingDirectory'], flush=True)
    assert data['StartCalendarInterval'] == {'Hour': hour, 'Minute': minute}
    assert data['WorkingDirectory'] == str(root)
    argv = data['ProgramArguments']
    assert argv[0] == py and argv[0].startswith('/')
    assert '/usr/bin/env' not in argv and 'python3' not in argv
    assert argv[1:5] == [str(root/'scripts/run_night.py'), mode, '--plan', plan]
    assert data['RunAtLoad'] is False
    assert data['StandardOutPath'] == str(Path(os.environ['NIGHT_CUSTODY'])/'night'/(stem+'.out'))
    assert data['StandardErrorPath'] == str(Path(os.environ['NIGHT_CUSTODY'])/'night'/(stem+'.err'))
now = time.time()
assert now < 1789196700, 'past the 00:05 PDT exit boundary'
print('install verified epoch=', now, datetime.fromtimestamp(now, ZoneInfo('America/Los_Angeles')).isoformat(), flush=True)
print('expected: night t0=1789198200 (2026-09-12 00:30 PDT); window close=1789199100; '
      'courier deadline=1789199400 (00:50 PDT); plan span opens=1789196700 (00:05 PDT); '
      'dead-man would be 1789221600 (09-12 07:00) but the agents are removed first', flush=True)
PY
cp /Users/edr/Library/LaunchAgents/com.joulewise.night.plist "$STAGE/arm-com.joulewise.night.plist"
cp /Users/edr/Library/LaunchAgents/com.joulewise.night.deadman.plist "$STAGE/arm-com.joulewise.night.deadman.plist"
cmp "$NIGHT_CUSTODY/night_plan.json" "$STAGE/arm-night_plan.json"
python3 -B - <<'PY'
import json, os
from pathlib import Path
root = Path(os.environ['NIGHT_CUSTODY'])/'night'
print('post-install night/ baseline:', json.dumps([
    {'name': p.name, 'size': p.lstat().st_size, 'mtime_ns': p.lstat().st_mtime_ns}
    for p in sorted(root.iterdir())], indent=2))
PY
print 'block B rc=0'
