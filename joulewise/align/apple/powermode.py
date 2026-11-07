"""Read-only observation of the host's AC-profile ``powermode`` (council ruling 7).

``pmset -g custom`` prints one block per power source. Only the ``AC Power:``
block is read, and only an exact ``powermode`` key: ``lowpowermode`` and the
battery profile never match. Observation never changes the setting.
"""
from __future__ import annotations

import errno
import json
import os
import re
import subprocess
import time

QUERY = ("/usr/bin/pmset", "-g", "custom")
SOURCE = "pmset -g custom (AC Power block, exact powermode key)"


def parse_ac_powermode(stdout):
    """Return the AC-profile ``powermode`` integer, or ``None`` if absent."""
    in_ac = False
    for line in (stdout or "").splitlines():
        if re.match(r"^\S.*:\s*$", line):
            in_ac = line.strip().rstrip(":").strip() == "AC Power"
            continue
        if in_ac:
            match = re.match(r"^\s*powermode\s+([0-9]+)\s*$", line)
            if match:
                return int(match.group(1))
    return None


def _run(argv):
    return subprocess.run(argv, text=True, capture_output=True, check=False, timeout=10)


def observe_ac_powermode(runner=None):
    """Observe the AC powermode; raises ``ValueError`` if pmset fails."""
    result = (runner or _run)(QUERY)
    if result.returncode:
        raise ValueError(f"pmset -g custom failed: exit {result.returncode}")
    return parse_ac_powermode(result.stdout)


# --- Host-level admission (executing review HIGH-3, council ruling 7) -------

# The R1 driver writes this marker under MEASUREMENT_ROOT before it sets High
# Power and removes it only after a successful Automatic restore, so a marker
# that survives means a crash, SIGKILL or power loss left the AC profile at 2.
R1_HIGH_POWER_MARKER = ".align-r1-high-power"
# The two commands the narrow sudo rule allows (the R1 chain's rule).
RESTORE_AUTOMATIC = ("sudo", "-n", "/usr/bin/pmset", "-c", "powermode", "0")
SET_HIGH_POWER = ("sudo", "-n", "/usr/bin/pmset", "-c", "powermode", "2")
# The W1 session's marker text (lead ruling R5-6). Any other marker content is
# an R1 crash marker: a restore owed, never a W1 night's own obligation.
W1_MARKER_TAG = "ALIGN v4 W1 high-power restoration required"


def w1_marker(marker):
    """True when ``marker`` is a W1 session's own High Power marker."""
    try:
        with open(marker, encoding="utf-8") as handle:
            return handle.read(256).startswith(W1_MARKER_TAG)
    except (OSError, UnicodeError):
        return False


# --- Host-level High Power state (lead ruling R6-7) ------------------------
#
# The marker that says "an Automatic restore is owed" lives at one HOST-level
# path that every session, night and the watchdog see, outside any per-session
# measurement view (which later sessions never share). Beside it, the night
# lock: a measuring night (a W1 night admitted under High Power, the R1
# driver) holds an exclusive flock on it for as long as it measures, and the
# kernel drops the lock when that process dies (SIGKILL, power loss), so a
# lock never outlives its night. No restore ever runs while another process
# holds the lock, so a late launchd fire (or an operator's session start)
# cannot change the mode under a measuring night.
HOST_STATE_ENV = "JOULEWISE_HOST_STATE_DIR"
HOST_STATE_DEFAULT = "/Users/Shared/JouleWise/host-power"
HOST_MARKER_NAME = "high-power.marker"
NIGHT_LOCK_NAME = "night.lock"
# A night admitted under High Power waits this long for the lock (a session
# install holds it through the installer's 180 s budget plus two pmset calls).
NIGHT_LOCK_WAIT_S = 240.0
R1_MARKER_TEXT = "high-power restoration required"


def host_state_dir():
    """The host-level directory (``$JOULEWISE_HOST_STATE_DIR`` overrides; tests
    and synthetic harnesses always set it)."""
    return os.environ.get(HOST_STATE_ENV) or HOST_STATE_DEFAULT


def host_marker_path():
    return os.path.join(host_state_dir(), HOST_MARKER_NAME)


def night_lock_path():
    return os.path.join(host_state_dir(), NIGHT_LOCK_NAME)


def _owner_key(value):
    return None if value in (None, "") else os.path.realpath(os.fspath(value))


def write_host_marker(marker, *, tag, owner=None):
    """Write the marker (tag line, then the owner as JSON) before any mode
    change; ``owner`` names the session that owes the restore."""
    marker = os.fspath(marker)
    os.makedirs(os.path.dirname(marker) or ".", mode=0o700, exist_ok=True)
    body = dict(owner or {})
    for key in ("custody_root", "plan_path"):
        if body.get(key) is not None:
            body[key] = _owner_key(body[key])
    body.setdefault("pid", os.getpid())
    body.setdefault("written_epoch_s", time.time())
    temporary = f"{marker}.{os.getpid()}.tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        handle.write(tag + "\n" + json.dumps(body, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, marker)


def marker_owner(marker):
    """The owner record of a marker (``{}`` when it carries none)."""
    try:
        with open(marker, encoding="utf-8") as handle:
            lines = handle.read(4096).splitlines()
        owner = json.loads(lines[1]) if len(lines) > 1 else {}
        return owner if isinstance(owner, dict) else {}
    except (OSError, UnicodeError, ValueError):
        return {}


def owned_by(marker, *, custody_root=None, plan_path=None):
    """True when ``marker`` is a W1 marker whose owner is this night (same
    custody root, or, when the plan could not be parsed, the same plan path)."""
    if not w1_marker(marker):
        return False
    owner = marker_owner(marker)
    custody, plan = _owner_key(custody_root), _owner_key(plan_path)
    return bool((custody is not None and owner.get("custody_root") == custody)
                or (plan is not None and owner.get("plan_path") == plan))


class HostLock:
    """The host night lock: an exclusive ``flock`` on ``night.lock``.

    Locks are per open file description, so one holder object per process
    and role; ``held`` says whether this object holds it."""

    def __init__(self, path=None, *, role="night"):
        self.path = os.fspath(path) if path is not None else night_lock_path()
        self.role = role
        self.fd = None

    @property
    def held(self):
        return self.fd is not None

    def acquire(self, *, wait_s=0.0, poll_s=0.5, sleep=time.sleep, monotonic=time.monotonic):
        """Take the lock, waiting up to ``wait_s``; False if another process
        still holds it. Raises OSError only when the lock file cannot be made."""
        import fcntl
        if self.fd is not None:
            return True
        os.makedirs(os.path.dirname(self.path) or ".", mode=0o700, exist_ok=True)
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        deadline = monotonic() + max(0.0, float(wait_s))
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as error:
                if error.errno not in (errno.EWOULDBLOCK, errno.EAGAIN, errno.EACCES):
                    os.close(fd)
                    raise
                if monotonic() >= deadline:
                    os.close(fd)
                    return False
                sleep(poll_s)
        self.fd = fd
        try:
            os.ftruncate(fd, 0)
            os.write(fd, (json.dumps({"pid": os.getpid(), "role": self.role, "epoch_s": time.time()},
                                     sort_keys=True) + "\n").encode())
        except OSError:
            pass  # the holder note is diagnostic only
        return True

    def release(self):
        import fcntl
        fd, self.fd = self.fd, None
        if fd is None:
            return
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def restore_owed(markers, *, runner=None, lock=None, owner=None, reason):
    """Restore Automatic for a host-level marker on a non-measuring path
    (lead ruling R6-7). Never raises; returns the record.

    ``owner`` (a dict with ``custody_root``/``plan_path``) limits the restore
    to a W1 marker that this night owns, so a late fire of another plan never
    changes the mode an armed session set; ``owner`` None restores any
    marker (session start). ``lock`` is the caller's HostLock: when the
    caller does not already hold it, it is taken without waiting, and a lock
    another process holds (a measuring night) defers the restore."""
    record = {"reason": reason, "action": "none", "markers": [os.fspath(m) for m in markers]}
    try:
        present = [os.fspath(m) for m in markers if os.path.lexists(m)]
        record["present"] = present
        if not present:
            return record
        if owner is not None and not any(owned_by(m, **owner) for m in present):
            record["action"] = "not_owner"
            return record
        lock = lock if lock is not None else HostLock()
        taken = False
        if not lock.held:
            if not lock.acquire():
                record["action"] = "deferred_measuring_night"
                return record
            taken = True
        try:
            restored = restore_automatic(present[0], runner=runner)
            if restored["ok"]:
                for marker in present[1:]:
                    if os.path.lexists(marker):
                        os.unlink(marker)
            record.update(action="restored" if restored["ok"] else "restore_failed", restore=restored)
        finally:
            if taken:
                lock.release()
    except BaseException as error:  # noqa: BLE001 - a restore attempt never masks the caller's exit
        record.update(action="error", error=f"{type(error).__name__}: {error}")
    return record


ADMISSIBLE = (0, 2)
READ_RETRIES = 1


def _completed(result):
    """(returncode, stdout, stderr) from a CompletedProcess or a ProbeResult."""
    code = getattr(result, "returncode", None)
    if code is None:
        code = getattr(result, "exit_code")
    return code, getattr(result, "stdout", "") or "", getattr(result, "stderr", "") or ""


def read_ac_powermode(runner=None, *, retries=READ_RETRIES):
    """One ``pmset -g custom`` observation, retried once on a failed read.

    Returns ``{value, pmset_text, attempts, error}``. A failed or unparsable
    read leaves ``value`` None; callers treat None as a refusal, never as 0.
    """
    runner = runner or _run
    attempts = []
    for _ in range(1 + retries):
        try:
            code, stdout, stderr = _completed(runner(QUERY))
        except Exception as exc:  # noqa: BLE001 - a failed read is evidence, not a crash
            attempts.append({"exit_code": None, "error": f"{type(exc).__name__}: {exc}"})
            continue
        attempts.append({"exit_code": code, "error": stderr.strip() or None if code else None})
        if code == 0:
            return {"value": parse_ac_powermode(stdout), "pmset_text": stdout, "source": SOURCE,
                    "attempts": attempts, "error": None}
    return {"value": None, "pmset_text": None, "source": SOURCE, "attempts": attempts,
            "error": attempts[-1].get("error") or f"exit {attempts[-1].get('exit_code')}"}


def admit_ac_powermode(expected, *, marker=None, runner=None, markers=(), lock=None, owner=None):
    """Admit only if the AC-profile powermode equals ``expected`` (0 or 2).

    A High Power marker (``marker`` and ``markers``: the host-level marker of
    lead ruling R6-7 and the R1 chain's ``$MEASUREMENT_ROOT`` marker) means
    "this host may be at powermode 2 by our doing; an Automatic restore is
    owed". With ``expected`` 0 and a marker present, Automatic is restored
    first with the narrow sudo rule and the mode is read again; the markers
    are removed only after a successful restore. With ``expected`` 2 (a W1
    night under an adopted High Power, lead ruling R5-6) W1 session markers
    (``W1_MARKER_TAG``) are the owed restore of that night's own close, so
    they are kept and no restore runs; any other marker (an R1 crash) still
    restores first, and the night then refuses on the mode. A restore never
    runs while another process holds the host night lock (``lock`` is the
    caller's HostLock; if it does not hold it, it is taken without waiting
    for the restore and released after): that refuses instead. With
    ``owner`` (the admitted night's ``custody_root``/``plan_path``), only W1
    markers that night owns are kept under 2; another session's W1 marker is
    a restore owed first (round-6 Sol critique). Markers are removed only
    after the restore reads back 0. Returns the
    record a caller stores in its arm or admission evidence; ``admitted`` is
    False with a ``reason`` otherwise.
    """
    runner = runner or _run
    candidates = [os.fspath(m) for m in ([marker] if marker is not None else []) + list(markers or ())]
    record = {"expected": expected, "source": SOURCE, "marker": candidates[0] if candidates else None,
              "markers": candidates, "marker_present": False, "restore": None, "observations": []}

    def refuse(reason):
        record.update(admitted=False, reason=reason)
        return record

    if type(expected) is not int or expected not in ADMISSIBLE:
        record["observed"] = None
        return refuse(f"expected AC powermode must be 0 or 2, not {expected!r}")
    first = read_ac_powermode(runner)
    record["observations"].append({"point": "admission", **first})
    present = [m for m in candidates if os.path.lexists(m)]
    record["markers_present"] = present
    if present and expected == 2 and all(w1_marker(m) and (owner is None or owned_by(m, **owner))
                                         for m in present):
        record["marker_present"] = True
        record["marker_kept"] = "expected 2: the restore is owed at this night's close"
        final = first
    elif present:
        record["marker_present"] = True
        lock = lock if lock is not None else HostLock()
        taken = False
        if not lock.held:
            try:
                taken = lock.acquire()
            except OSError as error:
                record["observed"] = first["value"]
                return refuse(f"High Power marker present and the host night lock is unavailable: {error}")
            if not taken:
                record["observed"] = first["value"]
                return refuse("High Power marker present but a measuring night holds the host night lock; "
                              "no restore under a measuring night")
        try:
            try:
                code, stdout, stderr = _completed(runner(RESTORE_AUTOMATIC))
            except Exception as exc:  # noqa: BLE001
                code, stdout, stderr = None, "", f"{type(exc).__name__}: {exc}"
            record["restore"] = {"argv": list(RESTORE_AUTOMATIC), "exit_code": code,
                                 "stdout": stdout, "stderr": stderr}
            if code != 0:
                record["observed"] = first["value"]
                return refuse("R1 High Power marker present and the Automatic restore failed "
                              f"(exit {code}): {stderr.strip()}")
            second = read_ac_powermode(runner)
            if second["value"] == 0:
                # Round-6 Sol critique: the obligation is cleared only once the
                # restore reads back Automatic.
                for path in present:
                    if os.path.lexists(path):
                        os.unlink(path)
        finally:
            if taken:
                lock.release()
        record["observations"].append({"point": "after_marker_restore", **second})
        final = second
    else:
        final = first
    record["observed"] = final["value"]
    record["pmset_text"] = final["pmset_text"]
    if final["value"] is None:
        return refuse("AC powermode unobserved: " + str(final["error"] or "no AC Power powermode key"))
    if final["value"] != expected:
        return refuse(f"AC powermode {final['value']} != expected {expected}")
    record.update(admitted=True, reason=None)
    return record


def enter_high_power(marker, *, runner=None, owner=None, prior_markers=()):
    """W1 under an adopted High Power (lead ruling R5-6): set AC powermode 2
    through the narrow sudo rule. The marker (host-level, lead ruling R6-7,
    naming ``owner``) is written first, so a crash at any later instruction
    leaves a durable restore obligation every later session sees; the mode
    is read back. On any failure Automatic is restored (marker removed only
    after a verified restore). An earlier non-W1 marker (``marker`` or any of
    ``prior_markers``) is an R1 crash: its restore is honoured first. Returns
    the record; ``ok`` is False with a reason."""
    runner = runner or _run
    record = {"marker": str(marker), "set": None, "observed": None, "prior_marker_restore": None}
    marker = os.fspath(marker)
    crashed = [os.fspath(m) for m in (marker, *prior_markers) if os.path.lexists(m) and not w1_marker(m)]
    if crashed:
        # An R1 crash marker: honour the owed restore before taking ownership.
        prior = restore_automatic(crashed[0], runner=runner)
        if prior["ok"]:
            for path in crashed[1:]:
                if os.path.lexists(path):
                    os.unlink(path)
        record["prior_marker_restore"] = prior
        if not prior["ok"]:
            record.update(ok=False, reason="an earlier High Power marker's Automatic restore failed")
            return record
    write_host_marker(marker, tag=W1_MARKER_TAG, owner=owner)
    try:
        code, stdout, stderr = _completed(runner(SET_HIGH_POWER))
    except Exception as exc:  # noqa: BLE001
        code, stdout, stderr = None, "", f"{type(exc).__name__}: {exc}"
    record["set"] = {"argv": list(SET_HIGH_POWER), "exit_code": code, "stderr": stderr}
    read = read_ac_powermode(runner)
    record["observed"], record["read"] = read["value"], read
    if code == 0 and read["value"] == 2:
        record.update(ok=True, reason=None)
        return record
    record.update(ok=False, reason=f"set High Power failed (exit {code}, observed {read['value']}): {stderr.strip()}",
                  restore=restore_automatic(marker, runner=runner))
    return record


def restore_automatic(marker=None, *, runner=None):
    """Restore AC powermode 0 with the narrow sudo rule and read it back; the
    marker is removed only once the read-back is 0 (the close of a W1 night
    under High Power, lead ruling R5-6). Never raises."""
    runner = runner or _run
    try:
        code, stdout, stderr = _completed(runner(RESTORE_AUTOMATIC))
    except Exception as exc:  # noqa: BLE001
        code, stdout, stderr = None, "", f"{type(exc).__name__}: {exc}"
    read = read_ac_powermode(runner)
    ok = code == 0 and read["value"] == 0
    if ok and marker is not None and os.path.lexists(marker):
        os.unlink(marker)
    return {"argv": list(RESTORE_AUTOMATIC), "exit_code": code, "stderr": stderr, "observed": read["value"],
            "ok": ok, "marker": None if marker is None else str(marker),
            "marker_removed": bool(ok and marker is not None)}
