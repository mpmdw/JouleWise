#!/usr/bin/env python3
"""Re-plan the n1-20260916 handback to a new t0. Usage: replan.py NEW_T0_EPOCH  (run from the hb worktree; edits NIGHT_HANDBACK.md + inventory note; prints the derived boundaries). Commit/push/H.txt are done by the caller."""
import math, re, sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
Z = ZoneInfo("America/Los_Angeles")
T0 = int(sys.argv[1]); assert T0 % 60 == 0
OLD = dict(t0=1789562400, close=1789561800, req=1789561920, term=1789562040, kill=1789562100, wend=1789571400, comp=1789571700, dead=1789575300)
NEW = dict(t0=T0, close=T0-600, req=T0-480, term=T0-360, kill=T0-300, wend=T0+9000, comp=T0+9300)
NEW['dead'] = int(math.ceil((NEW['comp']+3600)/60)*60)
def loc(e): return datetime.fromtimestamp(e, Z).strftime('%H:%M:%S')
def hm(e): return datetime.fromtimestamp(e, Z).strftime('%H:%M')
def utc(e): return datetime.fromtimestamp(e, timezone.utc).strftime('%H:%M:%S')
assert datetime.fromtimestamp(T0, Z).strftime('%Y-%m-%d') == '2026-09-16', 'same-day plan only'
p = Path('docs/process/NIGHT_HANDBACK.md'); s = p.read_text()
a = s.index('## Purpose of this night'); b = s.index('**Standing rules** <!-- F11 -->')
region = s[a:b]
pairs = []
for k in OLD:
    pairs.append((str(OLD[k]), str(NEW[k])))
    pairs.append((loc(OLD[k]), loc(NEW[k])))
pairs.append((utc(OLD['t0'])+' UTC', utc(NEW['t0'])+' UTC'))
pairs.append(('for 05:40 PDT', 'for '+hm(NEW['t0'])+' PDT'))
pairs.append(('(09:15 is after it)', '('+hm(NEW['dead'])+' is after it)'))
# longest first to avoid partial overlaps; HH:MM:SS strings are distinct per boundary
for old, new in sorted(pairs, key=lambda x: -len(x[0])):
    region = region.replace(old, new)
census_old_start = region.index('**Census.**'); census_old_end = region.index('**Timeline.**')
census_new = ('**Census.** This is a real night: the t0 census has no idle-interactive\n'
 'exemption (that exemption is stub-only, ARM-CENSUS-IDLE-INTERACTIVE-01), and\n'
 'the arm-time census classifies every `codex|claude|t3` match by ancestry and\n'
 'aborts on any foreign process. The first candidate for this plan id (t0\n'
 '05:40:00 PDT, H `82ea3eef`) was never published: Ed\'s interactive session\n'
 '(pid 7066) stayed alive past its own 04:14 exit announcement because its\n'
 'terminal was never closed, and the candidate lapsed at its 05:30 install\n'
 'close (its staged plan and night root preserved unpublished under record 02\'s\n'
 'evidence). This commit re-plans the same id to the t0 above, chosen at the\n'
 'moment the census cleared plus the arm-to-t0 floor and a margin; nothing is\n'
 'published while any foreign agent process lives.\n\n')
region = region[:census_old_start] + census_new + region[census_old_end:]
s = s[:a] + region + s[b:]
p.write_text(s)
inv = Path('configs/production_custody_inventory.json'); t = inv.read_text()
old = 're-planned by activation 0bd12d79 for t0 2026-09-16 05:40 PDT'
assert t.count(old) == 1
inv.write_text(t.replace(old, 're-planned by activation 0bd12d79 for t0 2026-09-16 %s PDT (the 05:40 candidate lapsed unpublished)' % hm(NEW['t0'])))
for k in ('close','req','term','kill','t0','wend','comp','dead'):
    print(f"{k:5s} {NEW[k]} {loc(NEW[k])} PDT")
print('T0_UTC', utc(NEW['t0']))
