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
