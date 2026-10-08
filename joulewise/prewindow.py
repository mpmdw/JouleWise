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



# T-0 has its own dwell: the Revision-6 shell script remains sealed.
MIN_CLEAN_DWELL_S = 600
INTERVAL_S = 30
DEFAULT_TIMEOUT_S = 45 * 60
STALE_RUNS_PREFIXES = {
    'alpha': 'runs_d117_floor_qwen25_1p5b_v2',
    'beta': 'runs_d117_floor_qwen25_7b_v2',
    'gamma': 'runs_d117_contrast_qwen25_1p5b_vs_7b_v2',
}


def t0_check(repository, window, *, emit=print):
    """Read the shell gate's readiness domains, with CPU census and report-only load."""
    import shutil
    import subprocess

    def probe(argv):
        return subprocess.run(argv, check=True, capture_output=True, text=True,
                              timeout=15).stdout

    blocked = False

    def block(message):
        nonlocal blocked
        blocked = True
        emit('  BLOCK ' + message)

    try:
        busy = busy_contaminants(probe(('ps', *PS_ARGV[1:])))
        if busy:
            block('background daemon active: ' + ' '.join(
                f'{pid} {args}({cpu:.1f}%)' for pid, cpu, args in busy))
        else:
            emit(f'  OK no contaminating daemon above {CPU_LIMIT_PERCENT}% CPU')
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        block(f'maintenance CPU probe failed: {exc}')
    try:
        uptime = probe(('uptime',))
        match = re.search(r'load averages?:\s*([0-9.]+)', uptime)
        load = match.group(1) if match else 'unavailable'
    except (OSError, subprocess.SubprocessError):
        load = 'unavailable'
    emit(f'  REPORT 1-minute load average {load}; limit 2.0; T-0 production CPU-idle admission governs')
    try:
        if 'AC Power' not in probe(('pmset', '-g', 'batt')).splitlines()[0]:
            block('not on AC power')
        else:
            emit('  OK on AC power')
    except (OSError, subprocess.SubprocessError, IndexError) as exc:
        block(f'power probe failed: {exc}')
    emit('  NOTE network-time state is handled by interactive E-4 plus exact E-5 enforcement')
    for literal in ('level=0', 'automatic_adjust=false', 'inactivity=never',
                    'verification=operator_visual'):
        emit('  NOTE keyboard_backlight.' + literal)
    if window:
        try:
            hits = [str(path) for path in repository.glob(STALE_RUNS_PREFIXES[window] + '*')
                    if not path.is_dir() or next(path.iterdir(), None) is not None]
            if hits:
                block(f'stale runs roots already exist for window {window}: ' + ' '.join(hits))
        except OSError as exc:
            block(f'stale runs root probe failed: {exc}')
    try:
        free = shutil.disk_usage(repository).free // 1024**3
        if free < 20:
            block(f'only {free} GB free; a window needs several GB with headroom')
        else:
            emit(f'  OK {free} GB free')
    except OSError as exc:
        block(f'disk headroom probe failed: {exc}')
    try:
        names = probe(('ps', '-A', '-o', 'comm='))
        agents = sum(bool(re.match(
            r'^(codex|claude|mcp-server|run_campaign|window-chain)([-_.\s].*)?$',
            name.strip().rsplit('/', 1)[-1], re.I)) for name in names.splitlines())
        if agents:
            block(f'{agents} agent/measurement process(es) already running')
        else:
            emit('  OK no agent or measurement process running')
    except (OSError, subprocess.SubprocessError) as exc:
        block(f'agent process probe failed: {exc}')
    return not blocked


def t0_wait(repository, window, timeout_s=DEFAULT_TIMEOUT_S, *,
            check=None, monotonic=None, sleep=None, emit=print):
    """Require a complete clean sample followed by 600 continuous clean seconds."""
    import time
    monotonic = monotonic or time.monotonic
    sleep = sleep or time.sleep
    check = check or (lambda: t0_check(repository, window, emit=emit))
    started = monotonic()
    deadline = started + timeout_s
    clean_since = None
    checks = 0
    while monotonic() < deadline:
        if check():
            now = monotonic()
            if now >= deadline:
                break
            if clean_since is None:
                clean_since = now
            checks += 1
            elapsed = int(now - clean_since)
            emit(f'  continuous clean dwell {elapsed}/{MIN_CLEAN_DWELL_S}s (check {checks})')
            if now - clean_since >= MIN_CLEAN_DWELL_S:
                emit(f'READY after {int((now - started) / 60)} min.')
                return 0
        else:
            clean_since = None
            checks = 0
            emit(f'  not ready; re-checking in {INTERVAL_S}s')
        remaining = deadline - monotonic()
        if remaining <= 0:
            break
        sleep(min(INTERVAL_S, remaining))
    emit(f'TIMED OUT after {timeout_s}s without {MIN_CLEAN_DWELL_S}s continuous clean time.')
    return 1


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--shell"]:
        print(f"CPU_LIMIT={CPU_LIMIT_PERCENT}; CONTAMINANTS='{CONTAMINANTS}'")
    elif sys.argv[1:] == ["--check"]:
        for pid, cpu, args in busy_contaminants(sys.stdin.read()):
            print(f"{pid} {args}({cpu:.1f}%)")
    else:
        import argparse
        from pathlib import Path
        parser = argparse.ArgumentParser(description="T-0 CPU-based clean dwell")
        parser.add_argument("--t0-wait", action="store_true", required=True)
        parser.add_argument("--timeout-min", type=int, default=45)
        parser.add_argument("--timeout-s", type=int)
        parser.add_argument("--window", choices=tuple(STALE_RUNS_PREFIXES), default="")
        args = parser.parse_args()
        timeout = args.timeout_min * 60 if args.timeout_s is None else args.timeout_s
        if timeout <= 0 or timeout > DEFAULT_TIMEOUT_S:
            parser.error("T-0 timeout must be positive and at most 2700 seconds")
        raise SystemExit(t0_wait(Path(__file__).resolve().parents[1], args.window, timeout))
