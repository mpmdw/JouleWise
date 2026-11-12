"""LaunchAgent entry point for the Air: results watcher plus main-CI check.

`run` starts `night_results_watch.py --loop --keep-going` as a child and runs
`main_ci_watch` every `--ci-interval` seconds while the child lives. When the
child exits, `run` exits with its status and launchd (KeepAlive) restarts it.
`notify <event line>` is the watcher's --notify-cmd: NOTICE and ALARM lines
become a macOS notification with structural fields only (level, code, subject)
and are appended to the log. Notification failure is logged, never fatal.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.air import main_ci_watch  # noqa: E402

HERE = Path(__file__).resolve().parent
DEFAULT_LOG = Path.home() / "Library/Logs/JouleWise/air-watch.log"
TITLE = "JouleWise Air watch"
REPO = HERE.parents[1]
EXIT_NOTIFY_S = 3600
OK_STATUSES = {0, 10, 20}


def watcher_exit(status, state_path, log, now=None, notifier=None):
    """Post one ALARM WATCHER_EXIT per status per hour, from this process (no repo file needed)."""
    now = time.time() if now is None else now
    try:
        seen = json.loads(state_path.read_text())
        if not isinstance(seen, dict):
            seen = {}
    except (OSError, ValueError):
        seen = {}
    key = str(status)
    last = seen.get(key)
    if isinstance(last, (int, float)) and now - last < EXIT_NOTIFY_S:
        append_log(log, f"INFO WATCHER_EXIT_SUPPRESSED agent status={status}")
        return False
    stamp = dt.datetime.fromtimestamp(now, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    (notifier or notify)(f"{stamp} ALARM WATCHER_EXIT agent status={status}", log)
    seen[key] = now
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(seen, sort_keys=True))
    except OSError:
        pass
    return True


def structural_text(line):
    """`YYYY-MM-DD HH:MM:SS LEVEL CODE subject ...` -> (level, 'LEVEL CODE subject')."""
    parts = line.split()
    if len(parts) < 5:
        return None, None
    level, code, subject = parts[2], parts[3], parts[4]
    clean = [re.sub(r"[^A-Za-z0-9_:./-]", "", p)[:80] for p in (level, code, subject)]
    return clean[0], " ".join(clean)


def append_log(log, text):
    log.parent.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open(log, "a", encoding="utf-8") as stream:
        stream.write(f"{stamp} {text}\n")


def notify(line, log, osascript="/usr/bin/osascript"):
    level, text = structural_text(line)
    if level not in {"NOTICE", "ALARM"}:
        return False
    script = f'display notification "{text}" with title "{TITLE}"'
    try:
        done = subprocess.run([osascript, "-e", script], stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              timeout=10, check=False)
        status = "ok" if done.returncode == 0 else "failed"
    except (OSError, subprocess.SubprocessError):
        status = "failed"
    append_log(log, f"NOTIFY {status} {text}")
    return status == "ok"


def watcher_argv(python, log, interval, hours, extra=()):
    return [python, str(HERE / "night_results_watch.py"), "--loop", "--keep-going",
            "--interval", str(interval), "--hours", str(hours), "--current-from-origin", *extra,
            "--notify-cmd", python, str(Path(__file__).resolve()), "notify", "--log", str(log)]


def run(args, popen=subprocess.Popen, sleep=time.sleep, clock=time.monotonic):
    try:
        child = popen(watcher_argv(args.python, args.log, args.interval, args.hours, args.watch_arg),
                      stdin=subprocess.DEVNULL)
    except OSError:
        watcher_exit("spawn", args.exit_state, args.log)
        return 2
    next_ci = clock()
    while True:
        status = child.poll()
        if status is not None:
            if status not in OK_STATUSES:
                watcher_exit(status, args.exit_state, args.log)
            return status
        if args.ci_interval > 0 and clock() >= next_ci:
            try:
                main_ci_watch.run_once(args.ci_state, notify=lambda l: notify(l, args.log),
                                       gh=args.gh, repo=args.repo, cwd=str(REPO))
            except Exception:  # never let an odd gh reply kill the supervisor
                append_log(args.log, "INFO MAIN_CI_WATCH_ERROR main")
            next_ci = clock() + args.ci_interval
        sleep(5)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--python", default=sys.executable)
    r.add_argument("--log", type=Path, default=DEFAULT_LOG)
    r.add_argument("--interval", type=float, default=120)
    r.add_argument("--hours", type=float, default=24)
    r.add_argument("--ci-interval", type=float, default=900)
    r.add_argument("--ci-state", type=Path, default=main_ci_watch.DEFAULT_STATE)
    r.add_argument("--exit-state", type=Path, default=main_ci_watch.DEFAULT_STATE.with_name("agent-exit.json"))
    r.add_argument("--gh", default="gh")
    r.add_argument("--repo", default=None)
    r.add_argument("--watch-arg", action="append", default=[],
                   help="extra watcher argument (repeat), e.g. --watch-arg=--min-expected-s --watch-arg=3600")
    n = sub.add_parser("notify")
    n.add_argument("--log", type=Path, default=DEFAULT_LOG)
    n.add_argument("--osascript", default="/usr/bin/osascript")
    n.add_argument("line")
    args = parser.parse_args(argv)
    if args.cmd == "notify":
        try:
            notify(args.line, args.log, args.osascript)
        except OSError:
            pass
        return 0
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
