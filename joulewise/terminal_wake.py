"""Advisory launchd edge, never evidence of termination or launch authority."""

import json
import math
import os
from pathlib import Path
import stat
import subprocess
import sys
import time
import uuid

MARKER = "terminal-wake.json"
SCHEMA = "joulewise.terminal_wake.v1"
DESTINATION_ENV = "JOULEWISE_TERMINAL_WAKE_ROOT"


def notify_after_exit(root, plan_id, receipt_class):
    """Start a short-lived exit observer only after terminal reporting.

    It inherits no driver locks or input. It cannot publish while the
    driver PID exists (including a zombie or a reused PID). No window work or
    arm authority is delegated to this helper.
    """
    return subprocess.Popen(
        [sys.executable, "-B", "-m", "joulewise.terminal_wake",
         "--wait-pid", str(os.getpid()), "--root", str(root),
         "--plan-id", plan_id, "--receipt-class", receipt_class],
        cwd=Path(__file__).resolve().parents[1], stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL, close_fds=True, start_new_session=True,
    )


def publish_after_exit(root, plan_id, receipt_class, pid, *, timeout_s=60):
    """Publish only after ESRCH proves driver absence; uncertainty falls back.

    The timeout bounds the helper, not a release rule. A timeout, permission
    error, helper loss or failed publication retains the 300 s watchdog tick.
    """
    if type(pid) is not int or pid <= 1 or pid == os.getpid():
        raise ValueError("invalid terminal driver PID")
    if not math.isfinite(timeout_s) or timeout_s <= 0:
        raise ValueError("invalid terminal exit timeout")
    deadline = time.monotonic() + timeout_s
    while True:
        try:
            os.kill(pid, 0)  # observation only; never signal the driver
        except ProcessLookupError:
            return publish(root, plan_id, receipt_class)
        except OSError:
            return None
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        time.sleep(min(0.1, remaining))


def publish(root, plan_id, receipt_class, *, now=None):
    root = Path(root)
    if not root.is_absolute() or any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError("terminal wake destination must be absolute and unsymlinked")
    # The watchdog installer owns this directory; a driver cannot create it.
    if not root.is_dir():
        raise ValueError("terminal wake destination is not installed")
    epoch = time.time() if now is None else now
    if type(epoch) not in (int, float) or not math.isfinite(epoch):
        raise ValueError("invalid terminal wake time")
    payload = json.dumps({"schema": SCHEMA, "plan_id": plan_id,
                          "receipt_class": receipt_class, "issued_epoch_s": epoch,
                          "nonce": uuid.uuid4().hex}, sort_keys=True).encode() + b"\n"
    temporary = root / (".terminal-wake-" + uuid.uuid4().hex)
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, root / MARKER)
        fd = os.open(root, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        temporary.unlink(missing_ok=True)
    return root / MARKER


def read_event(path):
    """Bounded regular-file read; malformed or unavailable edges are harmless."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                return None
            raw = stream.read(4097)
        event = json.loads(raw) if len(raw) <= 4096 else None
        if (not isinstance(event, dict) or event.get("schema") != SCHEMA
                or type(event.get("issued_epoch_s")) not in (int, float)
                or not math.isfinite(event["issued_epoch_s"])):
            return None
        return raw, event
    except (OSError, ValueError):
        return None


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wait-pid", type=int, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--plan-id", required=True)
    parser.add_argument("--receipt-class", required=True)
    args = parser.parse_args(argv)
    try:
        if publish_after_exit(args.root, args.plan_id, args.receipt_class, args.wait_pid):
            return 0
    except (OSError, ValueError) as exc:
        print("terminal wake: {}".format(exc), file=sys.stderr)
    print("terminal wake unavailable; retaining 300 s watchdog fallback", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
