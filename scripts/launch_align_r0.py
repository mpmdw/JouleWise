#!/usr/bin/env python3
"""Hand R0 to a one-shot LaunchAgent; never run a measurement in an agent tree."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import math
import os
from pathlib import Path
import plistlib
import signal
import stat
import subprocess
import sys
import time
import uuid


FENCE_NAME = "desk_fence.json"
# R0 is planned at ~3-6.5 h. The deadline bounds both the runner and the
# watchdog fence; a cap stops a unit slip (ms for s) or a typo from fencing
# the magistrate for days if the job hangs or its PID is reused.
MAX_DESK_SECONDS = 12 * 3600


def positive_seconds(value: str) -> float:
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("seconds must be positive and finite")
    return seconds


@contextlib.contextmanager
def fence_lock(root: Path, *, dry_run: bool = False):
    """Serialize stale removal, publication, ownership transfer and cleanup.

    This is separate from watchdog.lock, which a resident holds for its life.
    Callers that publish a new fence must create the custody directory first.
    """
    if dry_run:
        yield
        return
    fd = os.open(root / ".desk-fence.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def read_fence(root: Path) -> dict | None:
    path = root / FENCE_NAME
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    with os.fdopen(fd, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ValueError("desk fence must be a regular file")
        raw = handle.read(4097)
        if len(raw) > 4096:
            raise ValueError("desk fence exceeds 4096 bytes")
        record = json.loads(raw)
    if (not isinstance(record, dict) or set(record) != {"purpose", "pid", "deadline"}
            or not isinstance(record["purpose"], str) or not record["purpose"].strip()
            or type(record["pid"]) is not int or record["pid"] <= 1
            or type(record["deadline"]) not in (int, float)
            or not math.isfinite(record["deadline"]) or record["deadline"] <= 0):
        raise ValueError("invalid desk fence: expected purpose, positive pid and finite epoch deadline")
    return record


def write_fence(root: Path, record: dict) -> None:
    temporary = root / f".{FENCE_NAME}.{uuid.uuid4().hex}.tmp"
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(record, handle, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, root / FENCE_NAME)
        sync_directory(root)
    finally:
        temporary.unlink(missing_ok=True)


def sync_directory(root: Path) -> None:
    fd = os.open(root, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def clear_owned(root: Path, purpose: str, pid: int | None = None) -> None:
    with fence_lock(root):
        current = read_fence(root)
        if current and current["purpose"] == purpose and (pid is None or current["pid"] == pid):
            (root / FENCE_NAME).unlink()
            sync_directory(root)


def handoff(args) -> None:
    root = args.custody_root
    with fence_lock(root):
        current = read_fence(root)
        expected = {"purpose": args.purpose, "pid": args.magistrate_pid, "deadline": args.deadline}
        if current != expected or time.time() >= args.deadline:
            raise ValueError("desk fence changed or expired before LaunchAgent handoff")
        write_fence(root, {**current, "pid": args.pid})
    # The magistrate must end its session. QuietGuard still performs its full
    # independent agent, custody and installed-night-agent census afterwards.
    until = min(args.deadline, time.time() + args.exit_wait_seconds)
    while pid_alive(args.magistrate_pid):
        if time.time() >= until:
            raise TimeoutError("magistrate did not exit before the handoff timeout")
        time.sleep(0.1)


def preflight(args) -> None:
    import shutil

    result = subprocess.run([args.pmset_bin, "-g", "batt"], check=True,
                            capture_output=True, text=True, timeout=15,
                            env={**os.environ, "LC_ALL": "C"})
    if "Now drawing from 'AC Power'" not in result.stdout.splitlines():
        raise ValueError("R0 requires AC power (pmset -g batt)")
    free = shutil.disk_usage(args.disk_path).free
    # ALIGN v4 ruling 6: the >=80 GB bar belongs to W1, not this engineering desk.
    print(json.dumps({"ac_power": True, "free_bytes": free, "disk_check": "report_only"}), flush=True)


def run_until_deadline(args) -> int:
    """Bound the runner by the same deadline that releases the watchdog fence."""
    # Leave time to terminate a stuck runner and resume Spotlight before the
    # watchdog's deadline fallback permits another activation.
    remaining = args.deadline - time.time() - 10
    if remaining <= 0:
        raise TimeoutError("R0 desk deadline already passed")
    child = None

    def interrupted(signum, _frame):
        raise SystemExit(128 + signum)

    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(signum, interrupted)
    try:
        runner = json.loads(args.runner_spec.read_text())
        child = subprocess.Popen(runner)
        return child.wait(timeout=remaining)
    finally:
        # launchd and the shell may both deliver TERM. Finish reaping before
        # the shell resumes Spotlight and releases its fence.
        for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            signal.signal(signum, signal.SIG_IGN)
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


def launch(args) -> None:
    if (args.magistrate_pid <= 1 or not pid_alive(args.magistrate_pid)
            or not math.isfinite(args.deadline) or args.deadline <= time.time()):
        raise ValueError("live magistrate PID and future finite epoch deadline required")
    if args.deadline > time.time() + MAX_DESK_SECONDS:
        raise ValueError(f"desk deadline is more than {MAX_DESK_SECONDS} s ahead")
    if args.output.exists():
        raise ValueError("R0 output must be a new record directory")
    runner = args.repo / "scripts/align_r0_checks.py"
    if not runner.is_file() or not args.config.is_file() or not os.access(args.python_bin, os.X_OK):
        raise ValueError("measurement checkout runner, config and executable interpreter required")
    root = args.custody_root
    root.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    purpose = f"align-r0:{token}"
    label = f"com.joulewise.align-r0.{token}"
    domain = f"gui/{os.getuid()}"
    job = root / "r0-launches" / token
    job.mkdir(parents=True)
    plist = job / f"{label}.plist"
    wrapper = Path(__file__).with_name("run_align_r0_launchagent.sh").resolve()
    runner_spec = job / "runner.json"
    runner_spec.write_text(json.dumps([str(args.python_bin), str(runner),
                                      "--config", str(args.config), "--output", str(args.output)]) + "\n")
    # Keep the measurement entry-point name out of the launcher ancestors'
    # argv: QuietGuard correctly refuses a second align_r0_checks process.
    arguments = ["/bin/bash", str(wrapper), str(Path(__file__).resolve()),
                 str(args.python_bin), str(root), purpose, str(args.magistrate_pid),
                 str(args.deadline), str(args.exit_wait_seconds), args.pmset_bin,
                 str(args.disk_path), args.pgrep_bin, args.kill_bin, str(runner_spec),
                 args.launchctl_bin, f"{domain}/{label}"]
    plist.write_bytes(plistlib.dumps({
        "Label": label, "ProgramArguments": arguments, "RunAtLoad": True,
        "WorkingDirectory": str(args.repo),
        "EnvironmentVariables": {"PATH": "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin", "LC_ALL": "C"},
        "StandardOutPath": str(job / "stdout.log"), "StandardErrorPath": str(job / "stderr.log"),
    }))
    with fence_lock(root):
        current = read_fence(root)
        if current and current["deadline"] > time.time() and pid_alive(current["pid"]):
            raise ValueError("an active desk fence already exists")
        write_fence(root, {"purpose": purpose, "pid": args.magistrate_pid, "deadline": args.deadline})
    try:
        subprocess.run([args.launchctl_bin, "bootstrap", domain, str(plist)], check=True, timeout=30)
        until = time.monotonic() + args.start_wait_seconds
        while time.monotonic() < until:
            with fence_lock(root):
                current = read_fence(root)
            if (current and current["purpose"] == purpose and current["pid"] != args.magistrate_pid
                    and pid_alive(current["pid"])):
                print(json.dumps({"label": label, "plist": str(plist), "fence": current,
                                  "next": "exit the magistrate session now"}), flush=True)
                return
            time.sleep(0.1)
        raise TimeoutError("LaunchAgent did not claim the desk fence")
    except BaseException:
        # Do not release the fence until launchd has stopped this job. If
        # bootout is indeterminate, the dead-PID/deadline rule remains the fallback.
        stopped = subprocess.run([args.launchctl_bin, "bootout", f"{domain}/{label}"],
                                 capture_output=True, timeout=30)
        if stopped.returncode == 0 or (stopped.returncode == 113 and
                                       b"could not find service" in stopped.stderr.lower()):
            clear_owned(root, purpose)
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("launch", help="magistrate: publish fence, bootstrap once, then exit session")
    start.add_argument("--repo", type=Path, required=True)
    start.add_argument("--config", type=Path, required=True)
    start.add_argument("--output", type=Path, required=True)
    start.add_argument("--python-bin", type=Path, required=True)
    start.add_argument("--disk-path", type=Path, required=True)
    start.add_argument("--launchctl-bin", default="/bin/launchctl")
    start.add_argument("--pmset-bin", default="/usr/bin/pmset")
    start.add_argument("--pgrep-bin", default="/usr/bin/pgrep")
    start.add_argument("--kill-bin", default="/bin/kill")
    start.add_argument("--start-wait-seconds", type=positive_seconds, default=30)
    start.add_argument("--exit-wait-seconds", type=positive_seconds, default=180)
    take = sub.add_parser("handoff")
    take.add_argument("--magistrate-pid", type=int, required=True)
    take.add_argument("--exit-wait-seconds", type=positive_seconds, required=True)
    for command in (start, take):
        if command is start:
            command.add_argument("--magistrate-pid", type=int, required=True)
        command.add_argument("--deadline", type=float, required=True)
    clear = sub.add_parser("clear")
    for command in (take, clear):
        command.add_argument("--purpose", required=True)
        command.add_argument("--pid", type=int, required=True)
    for command in (start, take, clear):
        command.add_argument("--custody-root", type=Path, required=True)
    check = sub.add_parser("preflight")
    check.add_argument("--pmset-bin", default="/usr/bin/pmset")
    check.add_argument("--disk-path", type=Path, required=True)
    run = sub.add_parser("run")
    run.add_argument("--deadline", type=float, required=True)
    run.add_argument("--runner-spec", type=Path, required=True)
    args = parser.parse_args(argv)
    for name in ("repo", "config", "output", "python_bin", "disk_path", "custody_root"):
        if hasattr(args, name):
            setattr(args, name, getattr(args, name).expanduser().resolve())
    try:
        if args.command == "launch":
            launch(args)
        elif args.command == "handoff":
            handoff(args)
        elif args.command == "clear":
            clear_owned(args.custody_root, args.purpose, args.pid)
        elif args.command == "preflight":
            preflight(args)
        else:
            return run_until_deadline(args)
        return 0
    except (OSError, ValueError, subprocess.SubprocessError, TimeoutError) as exc:
        print(f"R0 launch refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
