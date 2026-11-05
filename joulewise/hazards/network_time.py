"""Bounded OFF command, immutable receipt, and same-boot settle admission."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import subprocess
import time

OFF_ARGV = ("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "off")
BOOT_ARGV = ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid")
SCHEMA = "joulewise.network_time_off.v1"
EXPECTED_STDOUT = "setUsingNetworkTime: Off\n"
"""The wording macOS prints when the setter switches network time from On to Off."""
# What the receipt must prove is the end state: network time is Off.  macOS
# words that two ways, depending on the state before the call, and both are
# the required end state.  C1 (2026-09-30, plan ...-c1-20261001T0137Z) was
# refused at t0 because only the first wording was admitted while the Mac was
# already Off, which is its standing state between windows.  The comparison is
# on normalised text (case, whitespace, trailing period), against a closed set
# of end-state statements; anything else, including an "On" statement and the
# "You need administrator access ... exiting!" text that systemsetup prints
# with exit status 0, is still refused.
ADMITTED_OFF_STATEMENTS = frozenset({
    "setusingnetworktime: off",      # was On, now Off
    "network time is already off",  # was already Off
})


def off_stdout_admitted(stdout):
    """True when the setter's stdout states that network time ends Off."""
    if not isinstance(stdout, str):
        return False
    statement = " ".join(stdout.split()).casefold().rstrip(".").rstrip()
    return statement in ADMITTED_OFF_STATEMENTS
RECEIPT_BASENAME = "network_time_off.json"


def _run(argv, *, timeout):
    return subprocess.run(argv, capture_output=True, timeout=timeout, check=False)


def _text(value):
    return value.decode("utf-8", "surrogateescape") if isinstance(value, bytes) else value


def boot_id(runner=_run):
    result = runner(BOOT_ARGV, timeout=10)
    value = _text(result.stdout).strip().lower()
    if result.returncode != 0 or not value:
        raise ValueError("boot identity unavailable")
    return value


def _clock():
    return {"epoch_s": time.time(), "monotonic_s": time.monotonic()}


def admit(receipt):
    if (not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA
            or receipt.get("argv") != list(OFF_ARGV)
            or type(receipt.get("exit_code")) is not int or receipt["exit_code"] != 0
            or not off_stdout_admitted(receipt.get("stdout"))
            or not isinstance(receipt.get("stderr"), str)
            or any(not isinstance(receipt.get(name), str) or not receipt[name]
                   for name in ("boot_id", "plan_id", "window_id"))):
        raise ValueError("network time OFF receipt not admitted")
    for name in ("epoch_s", "monotonic_s"):
        value = receipt.get(name)
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("invalid OFF receipt clock")
    return receipt


def read_receipt(path, *, plan_id=None, window_id=None):
    path = Path(path)
    if path.is_symlink():
        raise ValueError("OFF receipt is a symlink")
    receipt = admit(json.loads(path.read_bytes()))
    if ((plan_id is not None and receipt["plan_id"] != plan_id)
            or (window_id is not None and receipt["window_id"] != window_id)):
        raise ValueError("OFF receipt window/plan mismatch")
    return receipt


def set_network_time_off(path, plan_id, window_id, *, runner=_run,
                         clock=_clock, boot_probe=None):
    """Save failed attempts too; no command on an existing receipt path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        error = None
        try:
            result = runner(OFF_ARGV, timeout=30)
            code, stdout, stderr = result.returncode, _text(result.stdout), _text(result.stderr)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            code, stdout, stderr = None, _text(getattr(exc, "stdout", None)) or "", _text(getattr(exc, "stderr", None)) or ""
            error = f"{type(exc).__name__}: {exc}"
        stamp = clock()
        try:
            boot = boot_probe() if boot_probe is not None else boot_id(runner)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            boot, error = None, f"{type(exc).__name__}: {exc}"
        receipt = {"schema": SCHEMA, "argv": list(OFF_ARGV), "exit_code": code,
                   "stdout": stdout, "stderr": stderr, "error": error, **stamp,
                   "boot_id": boot, "plan_id": plan_id, "window_id": window_id}
        stream.write(json.dumps(receipt, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    return admit(receipt)


def seconds_since_receipt(receipt, now):
    """Minimum elapsed on both clocks; refuse until both prove 600 seconds."""
    admit(receipt)
    # The receipt stores the boot session UUID lowercased; callers may pass the
    # raw sysctl value, which macOS prints in upper case.
    current = now.get("boot_id") if isinstance(now, dict) else None
    if not isinstance(current, str) or current.strip().lower() != receipt["boot_id"]:
        raise ValueError("OFF receipt belongs to a different boot")
    elapsed = []
    for name in ("epoch_s", "monotonic_s"):
        value = now.get(name)
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("invalid admission clock")
        elapsed.append(value - receipt[name])
    if min(elapsed) < 600:
        raise ValueError("OFF receipt has not settled for 600 seconds on both clocks")
    return min(elapsed)
