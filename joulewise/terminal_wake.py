"""Advisory launchd edge, never evidence of termination or launch authority."""

import json
import math
import os
from pathlib import Path
import stat
import time
import uuid

MARKER = "terminal-wake.json"
SCHEMA = "joulewise.terminal_wake.v1"
DESTINATION_ENV = "JOULEWISE_TERMINAL_WAKE_ROOT"


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
