#!/bin/zsh
set -euo pipefail
source "$(dirname "$0")/arm-env.zsh"
cd "$MEASUREMENT_ROOT" || exit 3
launchctl print "gui/$(id -u)/com.joulewise.night"
launchctl print "gui/$(id -u)/com.joulewise.night.deadman"
plutil -p /Users/edr/Library/LaunchAgents/com.joulewise.night.plist
plutil -p /Users/edr/Library/LaunchAgents/com.joulewise.night.deadman.plist
"$PY" -B scripts/run_night.py schedule --plan "$PLAN"
print -- "CHECK: byte equality" "$PLAN" "$ATTEMPT_DIR/plan.json"
cmp "$PLAN" "$ATTEMPT_DIR/plan.json"
"$PY" -B - <<'PY'
import json, os, plistlib, subprocess
from pathlib import Path
from joulewise.night_gate import NightPlan
from scripts.run_night import schedule
labels = {line.split()[-1] for line in subprocess.check_output(['launchctl', 'list'], text=True).splitlines() if line.split()}
print("CHECK: {'com.joulewise.night', 'com.joulewise.night.deadman'} <= labels", flush=True)
assert {'com.joulewise.night', 'com.joulewise.night.deadman'} <= labels
plan = NightPlan.from_mapping(json.loads(Path(os.environ['PLAN']).read_text()))
expected = schedule(plan)
for label, key in (('com.joulewise.night', 'night_calendar'), ('com.joulewise.night.deadman', 'deadman_calendar')):
    plist = plistlib.loads((Path.home() / 'Library' / 'LaunchAgents' / f'{label}.plist').read_bytes())
    print(f"CHECK: {label} plist Label matches loaded label", flush=True)
    assert plist['Label'] == label
    print("CHECK: plist['StartCalendarInterval'] == expected[key], (label, plist['StartCalendarInterval'])", flush=True)
    assert plist['StartCalendarInterval'] == expected[key], (label, plist['StartCalendarInterval'])
    print("CHECK: os.environ['PLAN'] in plist['ProgramArguments'], plist['ProgramArguments']", flush=True)
    assert os.environ['PLAN'] in plist['ProgramArguments'], plist['ProgramArguments']
    rendered = plistlib.loads((Path(os.environ['STAGE']) / 'rendered-agents' / f'{label}.plist').read_bytes())
    print("CHECK: plist['ProgramArguments'] == rendered['ProgramArguments'], (label, plist['ProgramArguments'])", flush=True)
    assert plist['ProgramArguments'] == rendered['ProgramArguments'], (label, plist['ProgramArguments'])
    print("CHECK: plist['ProgramArguments'][0] == os.environ['PY']", flush=True)
    assert plist['ProgramArguments'][0] == os.environ['PY']
    print("CHECK: plist['WorkingDirectory'] == os.environ['MEASUREMENT_ROOT']", flush=True)
    assert plist['WorkingDirectory'] == os.environ['MEASUREMENT_ROOT']
    assert plist['RunAtLoad'] is False
print('installed calendars match plan')
night = Path(os.environ['NIGHT_ROOT']) / 'night'
entries = sorted(night.iterdir()) if night.is_dir() else []
print('post-install night/ baseline:', json.dumps([{'name': p.name, 'size': p.lstat().st_size, 'mtime_ns': p.lstat().st_mtime_ns} for p in entries]))
PY
shasum -a 256 "$PLAN" "$NIGHT_ROOT/chain.zsh" "$NIGHT_ROOT/night_probe_receipt.json"
echo "ARMED $(date '+%Y-%m-%dT%H:%M:%S%z')"
( cd "$NIGHT_ROOT" && shasum -a 256 -c chain.zsh.sha256 )
# This prints the deadline; it does not terminate the magistrate or its children.
print -- "EXIT RULE: magistrate, all owned agents, MCP children and helpers must exit strictly BEFORE epoch $REQUEST_EPOCH_S ($(date -r "$REQUEST_EPOCH_S" '+%Y-%m-%d %H:%M:%S %Z'))."
print -- 'Keep the machine untouched and agent apps closed through courier completion; longer if still active. Announcing exit does not terminate a process.'
