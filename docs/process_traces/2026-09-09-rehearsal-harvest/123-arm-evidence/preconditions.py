import json, os, subprocess, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

zone = ZoneInfo("America/Los_Angeles")
now = time.time()
start = datetime(2026, 9, 10, 3, 0, tzinfo=zone).timestamp()
end = datetime(2026, 9, 10, 6, 30, tzinfo=zone).timestamp()
print("arm clock:", now, datetime.fromtimestamp(now, zone).isoformat(), flush=True)
assert start <= now < end, "outside 03:00–06:30 PDT install window"
assert datetime.fromtimestamp(1789120560).strftime('%Y-%m-%d %H:%M') == '2026-09-11 02:56', 'system local time differs from the pinned launchd time'
parent = Path('/Users/edr/night-custody')
stop = parent/'magistrate/standdown.request'
assert not stop.exists() and not stop.is_symlink(), "standdown requested"
assert not list(parent.glob('*/night_plan.json')), "existing plan"
services = subprocess.run(['launchctl', 'list'], capture_output=True, text=True, check=True)
matches = [line for line in services.stdout.splitlines() if 'joulewise' in line]
print('launchctl list | grep joulewise:', *matches, sep='\n', flush=True)
assert [line.split()[-1] for line in matches] == ['com.joulewise.magistrate']
me = json.loads((parent/'magistrate/magistrate.lock').read_text())['pid']
raw = subprocess.run(['ps', '-axo', 'pid=,ppid=,command='], capture_output=True, text=True, check=True).stdout
rows = {int(a): (int(b), c) for line in raw.splitlines() if line.strip()
        for a, b, c in [line.strip().split(None, 2)]}
def ancestors(pid):
    seen = set()
    while pid in rows and pid != 1 and pid not in seen:
        seen.add(pid)
        yield pid
        pid = rows[pid][0]
assert me in set(ancestors(os.getpid())), 'lock PID is not this census ancestor'
probe = subprocess.run(['pgrep', '-fl', 'codex|claude|t3'], capture_output=True, text=True)
print('pgrep -fl "codex|claude|t3" rc=', probe.returncode, flush=True)
print(probe.stdout, end='', flush=True)
print(probe.stderr, end='', flush=True)
assert probe.returncode in (0, 1), 'census failed'
hits = [int(line.split(None, 1)[0]) for line in probe.stdout.splitlines() if line.strip()]
foreign = [pid for pid in hits if me not in set(ancestors(pid))]
for pid in hits:
    print('census ancestry:', pid, list(ancestors(pid)), rows.get(pid), flush=True)
print('foreign agent matches:', foreign, flush=True)
assert not foreign, 'foreign or unclassifiable process; preserve it and abort'
