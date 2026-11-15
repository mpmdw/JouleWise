"""mobileassetd / mds / softwareupdated entry times by minute (leading date, time, process fields only; message text never kept).
Prints per-minute counts for the named processes between argv[2] and argv[3] (HH:MM, local). Gates nothing.
Usage: python3 -I -B maint_burst.py OUT HH:MM HH:MM"""
import re, sys
from collections import Counter
from pathlib import Path
ENTRY = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})\.\d+\s+\S+\s+([^\[\s]+)\[")
lo, hi = sys.argv[2], sys.argv[3]
c, first, last = Counter(), {}, {}
with (Path(sys.argv[1]) / "maintenance-log.txt").open(errors="replace") as fh:
    for line in fh:
        m = ENTRY.match(line)
        if not m: continue
        t, p = m.group(2), m.group(3)
        if p not in ("mobileassetd", "mds", "mds_stores", "softwareupdated") or not (lo <= t[:5] < hi): continue
        c[(t[:5], p)] += 1; first.setdefault(p, t); last[p] = t
for (mnt, p), n in sorted(c.items()): print(mnt, p, n)
print("first", first, "last", last)
