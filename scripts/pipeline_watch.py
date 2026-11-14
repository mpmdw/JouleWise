#!/usr/bin/env python3
"""Non-agent pipeline watcher for the Air (RL-127 terms 6-8; RL-128 probe disabled).

    pipeline_watch.py once [--dry-run] [--offline] [--run-state FILE] [--now EPOCH]
    pipeline_watch.py status
    pipeline_watch.py queue add --name N [--expected-end ISO] | queue done --name N | queue list
    pipeline_watch.py notify-test

`once` is what the launchd agent runs every 120 s. It reads origin/main
RUN_STATE.md (git fetch into a private ref), the directive-notice issues and
in-progress CI runs (gh), the armed plan's results ref (ls-remote), the timing
ledger, the MBP queue file and the local process table; runs the detectors in
`joulewise.pipeline_time.detect`; profiles over-budget local jobs; and alarms
by macOS notification, /Volumes/JW-EXT/ledger/alarms.jsonl and a
`pipeline-alarm` GitHub issue (deduplicated; see `alarms.py`). It needs no
Claude session, never opens SSH and signals no process.

`--dry-run` prints the state and the alarms it would raise. It sends nothing,
saves no alarm state and takes no profile; it still fetches origin main into the
private ref and creates the state directory and its lock file. `queue` edits the MBP queue file that the
idle detector reads (jobs the lead starts on the unarmed MBP).
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
from pathlib import Path
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.pipeline_time import alarms, detect, runstate, sources  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
LEDGER_DIR = sources.LEDGER_DIR
STATE_DIR = Path.home() / "Library/Application Support/JouleWise/pipeline-watch"
REPO_CONFIG = REPO / "scripts/air/pipeline_watch_config.json"


def load_config(paths) -> dict:
    config = dict(detect.DEFAULT_CONFIG)
    for path in paths:
        try:
            data = json.loads(Path(path).read_text())
        except (OSError, ValueError):
            continue
        if isinstance(data, dict):
            config.update({k: v for k, v in data.items() if not k.startswith("_")})
    return config


@contextlib.contextmanager
def single_instance(lock_path: Path):
    import fcntl
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            yield False
            return
        yield True


def write_heartbeat(path: Path, now: float, status: list[str], active: list[str]) -> None:
    try:
        if not path.parent.is_dir():
            return
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"ts": round(now, 3), "pid": os.getpid(), "status": status,
                                   "active_alarms": active}, indent=1) + "\n")
        os.replace(tmp, path)
    except OSError:
        pass


def try_save(path: Path, state: dict) -> bool:
    try:
        alarms.save_state(path, state)
        return True
    except (OSError, TypeError, ValueError):
        return False


CRASH_REPEAT_S = 3600


def crash_alarm(state_dir: Path, ledger_dir: Path, exc: BaseException, now: float | None = None,
                runner=None) -> bool:
    """F5: one local PIPELINE_WATCH_CRASH alarm per hour (notification and alarms.jsonl), never an issue."""
    now = time.time() if now is None else now
    runner = runner or alarms.default_runner
    stamp = Path(state_dir) / "crash.stamp"
    try:
        last = float(stamp.read_text().strip())
    except (OSError, ValueError):
        last = None
    name = type(exc).__name__
    when = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    if last is not None and now - last < CRASH_REPEAT_S:
        print(f"{when} INFO PIPELINE_WATCH_CRASH_SUPPRESSED {name}")
        return False
    line = f"ALARM PIPELINE_WATCH_CRASH {name}: the poll raised; see the watcher log"
    ok = alarms.notify(line, runner=runner)
    wrote = alarms.append_jsonl(Path(ledger_dir) / "alarms.jsonl",
                                {"ts": round(now, 3), "event": "raise", "key": "watch_crash",
                                 "code": "PIPELINE_WATCH_CRASH", "severity": "alarm",
                                 "summary": f"{name}: {str(exc)[:200]}"})
    try:
        Path(state_dir).mkdir(parents=True, exist_ok=True)
        stamp.write_text(f"{now}\n")
    except OSError:
        pass
    print(f"{when} NOTIFY {'ok' if ok else 'failed'} jsonl {'ok' if wrote else 'failed'} PIPELINE_WATCH_CRASH {name}")
    return True


def once(args, config, runner=alarms.default_runner) -> int:
    now = time.time() if args.now is None else float(args.now)
    state_path = Path(args.state_dir) / "state.json"
    ledger_dir = Path(args.ledger_dir)
    with single_instance(Path(args.state_dir) / "watch.lock") as got:
        if not got:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} INFO another watcher instance holds the lock")
            return 0
        state = alarms.load_state(state_path)
        text = Path(args.run_state).read_text() if args.run_state else None
        snap = sources.gather(REPO, config, state, now=now, runner=runner,
                              ledger_file=ledger_dir / "timing.jsonl", queue_file=ledger_dir / "mbp-queue.json",
                              run_state_text=text, offline=args.offline)
        found = detect.run_all(snap, config)
        status = detect.status_lines(snap, config)
        probe = sources.rl128_probe(state, now)
        status.append(f"RL-128 probe: {probe['reason']}")
        if args.dry_run:
            print("\n".join(status))
            print(f"--- {len(found)} alarm(s) this poll (dry run: nothing sent, nothing saved)")
            for alarm in found:
                print(f"{alarm.line()}  [key {alarm.key}]")
                if alarm.profile_pid:
                    print(f"    would profile pid {alarm.profile_pid}")
            return 0
        actions = alarms.plan(found, state, now, repeat_s=config.get("repeat_s"),
                              issue_repeat_s=config.get("issue_repeat_s", alarms.ISSUE_REPEAT_S),
                              hold=detect.held_prefixes(snap))
        # F2: record the plan before any channel fires. If the state cannot be saved, the next
        # poll would re-plan the same posts, so the public issue channel is skipped this poll.
        saved = try_save(state_path, state)
        profile_cfg = config.get("profile") or {}
        for action in actions:
            alarm = action.alarm
            if action.kind == "raise" and alarm and alarm.profile_pid and not action.record.get("profile") \
                    and snap.processes is not None:
                path = sources.capture_profile(
                    alarm.profile_pid, alarm.stage, ledger_dir / "profiles", snap.processes, runner=runner,
                    samples=int(profile_cfg.get("samples", 3)), interval_s=float(profile_cfg.get("interval_s", 10)),
                    use_sample=bool(profile_cfg.get("use_sample", True)), sample_s=int(profile_cfg.get("sample_s", 3)),
                    window_s=float(profile_cfg.get("recent_window_s", 300)))
                if path:
                    action.record["profile"] = path
                    alarm.detail = (alarm.detail + "\n" if alarm.detail else "") + f"profile: {path}"
                    # L3: the public issue names the profile by its JW-EXT-relative name only.
                    alarm.public = (alarm.public or "") + f"; profile {ledger_dir.name}/profiles/{Path(path).name}"
        issues = alarms.IssueChannel(config["repo"], runner=runner) if saved else None
        log = alarms.deliver(actions, now, ledger_dir / "alarms.jsonl", config.get("channels") or {},
                             issues=issues, runner=runner, host=snap.host)
        if not saved:
            log.append("issue skipped: state not saved (F2)")
        try_save(state_path, state)
        active = sorted(key for key, rec in state["alarms"].items() if rec.get("active"))
        write_heartbeat(ledger_dir / "watch-heartbeat.json", now, status, active)
        stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
        print(f"{stamp} POLL alarms={len(found)} active={len(active)} sent={len(log)}")
        for line in log:
            print(f"{stamp} {line}")
    return 0


def queue(args) -> int:
    path = Path(args.ledger_dir) / "mbp-queue.json"
    jobs = sources.read_queue(path)
    now = time.time()
    if args.queue_mode == "add":
        end = runstate.parse_time(args.expected_end) if args.expected_end else None
        if args.expected_end and end is None:
            print("expected end must be ISO 8601 with an offset", file=sys.stderr)
            return 2
        jobs = [job for job in jobs if job.get("name") != args.name]
        jobs.append({"name": args.name, "started_epoch_s": round(now, 3), "expected_end_epoch_s": end})
    elif args.queue_mode == "done":
        jobs = [job for job in jobs if job.get("name") != args.name]
    if args.queue_mode in ("add", "done"):
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"jobs": jobs}, indent=1, sort_keys=True) + "\n")
        os.replace(tmp, path)
    for job in jobs:
        print(f"{job.get('name')}: started {detect.fmt(job.get('started_epoch_s'))}, "
              f"expected end {detect.fmt(job.get('expected_end_epoch_s'))}")
    return 0


def parse(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--state-dir", default=str(STATE_DIR))
    parser.add_argument("--ledger-dir", default=str(LEDGER_DIR))
    parser.add_argument("--config", action="append", default=[],
                        help="extra JSON config merged over the repo config (repeatable)")
    sub = parser.add_subparsers(dest="mode", required=True)
    one = sub.add_parser("once")
    one.add_argument("--dry-run", action="store_true")
    one.add_argument("--offline", action="store_true", help="no git or gh calls (use with --run-state)")
    one.add_argument("--run-state", help="read this RUN_STATE file instead of origin/main")
    one.add_argument("--now", type=float)
    sub.add_parser("status")
    q = sub.add_parser("queue")
    q.add_argument("queue_mode", choices=("add", "done", "list"))
    q.add_argument("--name")
    q.add_argument("--expected-end")
    sub.add_parser("notify-test")
    args = parser.parse_args(argv)
    if args.mode == "queue" and args.queue_mode in ("add", "done") and not args.name:
        parser.error("queue add/done needs --name")
    return args


def main(argv=None, runner=None) -> int:
    args = parse(sys.argv[1:] if argv is None else argv)
    if args.mode == "once":
        # F5: a persistent exception (a bad config override, a hand-edited queue file) must not
        # leave the watcher silently dead: one rate-limited local crash alarm, one log line, exit 0.
        try:
            config = load_config([REPO_CONFIG, Path(args.ledger_dir) / "watch-config.json", *args.config])
            return once(args, config, runner=runner or alarms.default_runner)
        except Exception as exc:  # noqa: BLE001 - the guard is the point
            import traceback
            traceback.print_exc(limit=3)
            crash_alarm(Path(args.state_dir), Path(args.ledger_dir), exc, runner=runner)
            return 0
    config = load_config([REPO_CONFIG, Path(args.ledger_dir) / "watch-config.json", *args.config])
    if args.mode == "status":
        args.dry_run, args.offline, args.run_state, args.now = True, False, None, None
        return once(args, config)
    if args.mode == "queue":
        return queue(args)
    ok = alarms.notify("ALARM INSTALL_TEST pipeline watcher notification test")
    ledger_dir = Path(args.ledger_dir)
    wrote = alarms.append_jsonl(ledger_dir / "alarms.jsonl", {"ts": round(time.time(), 3), "event": "test",
                                                               "key": "install-test", "code": "INSTALL_TEST",
                                                               "severity": "warn", "summary": "notify-test"})
    print(f"notification {'ok' if ok else 'failed'}; alarms.jsonl {'ok' if wrote else 'failed'}")
    return 0 if ok and wrote else 1


if __name__ == "__main__":
    sys.exit(main())
