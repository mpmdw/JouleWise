"""WO-CENSUS-SEMANTICS: resident daemons veto only above the shared CPU bar."""
import math
import re

CPU_LIMIT_PERCENT = 5.0
CONTAMINANTS = "XProtect|mds_stores|mdworker|mdbulkimport|backupd|photoanalysisd|softwareupdated|Spotlight|mediaanalysisd"
PS_ARGV = ("/bin/ps", "-Ao", "pid=,pcpu=,args=")


def busy_contaminants(stdout):
    if not stdout.strip():
        raise ValueError("empty process census")
    busy = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        fields = line.split(None, 2)
        if len(fields) != 3 or not fields[0].isdigit():
            raise ValueError("invalid process census row")
        cpu = float(fields[1])
        if not math.isfinite(cpu) or cpu < 0:
            raise ValueError("invalid process CPU")
        if re.search(CONTAMINANTS, fields[2], re.I) and cpu > CPU_LIMIT_PERCENT:
            busy.append((int(fields[0]), cpu, fields[2]))
    return busy


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--shell"]:
        print(f"CPU_LIMIT={CPU_LIMIT_PERCENT}; CONTAMINANTS='{CONTAMINANTS}'")
    elif sys.argv[1:] == ["--check"]:
        for pid, cpu, args in busy_contaminants(sys.stdin.read()):
            print(f"{pid} {args}({cpu:.1f}%)")
    else:
        raise SystemExit(2)
