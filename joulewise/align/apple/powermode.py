"""Read-only observation of the host's AC-profile ``powermode`` (council ruling 7).

``pmset -g custom`` prints one block per power source. Only the ``AC Power:``
block is read, and only an exact ``powermode`` key: ``lowpowermode`` and the
battery profile never match. Observation never changes the setting.
"""
from __future__ import annotations

import os
import re
import subprocess

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


def admit_ac_powermode(expected, *, marker=None, runner=None):
    """Admit only if the AC-profile powermode equals ``expected`` (0 or 2).

    The High Power ``marker`` means "this host may be at powermode 2 by our
    doing; an Automatic restore is owed when a night expects 0". With
    ``expected`` 0 and the marker present, Automatic is restored first with the
    narrow sudo rule and the mode is read again; the marker is removed only
    after a successful restore. With ``expected`` 2 (a W1 night under an
    adopted High Power, lead ruling R5-6) a W1 session's marker
    (``W1_MARKER_TAG``) is the owed restore of that night's own close, so it is
    kept and no restore runs; any other marker (an R1 crash) still restores
    first, and the night then refuses on the mode. Returns the
    record a caller stores in its arm or admission evidence; ``admitted`` is
    False with a ``reason`` otherwise.
    """
    runner = runner or _run
    record = {"expected": expected, "source": SOURCE, "marker": None if marker is None else str(marker),
              "marker_present": False, "restore": None, "observations": []}

    def refuse(reason):
        record.update(admitted=False, reason=reason)
        return record

    if type(expected) is not int or expected not in ADMISSIBLE:
        record["observed"] = None
        return refuse(f"expected AC powermode must be 0 or 2, not {expected!r}")
    first = read_ac_powermode(runner)
    record["observations"].append({"point": "admission", **first})
    if marker is not None and os.path.lexists(marker) and expected == 2 and w1_marker(marker):
        record["marker_present"] = True
        record["marker_kept"] = "expected 2: the restore is owed at this night's close"
        final = first
    elif marker is not None and os.path.lexists(marker):
        record["marker_present"] = True
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
        os.unlink(marker)
        second = read_ac_powermode(runner)
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


def enter_high_power(marker, *, runner=None):
    """W1 under an adopted High Power (lead ruling R5-6): set AC powermode 2
    through the narrow sudo rule. The marker is written first, so a crash at
    any later instruction leaves a durable restore obligation; the mode is
    read back. On any failure Automatic is restored (marker removed only after
    a verified restore). Returns the record; ``ok`` is False with a reason."""
    runner = runner or _run
    record = {"marker": str(marker), "set": None, "observed": None, "prior_marker_restore": None}
    marker = os.fspath(marker)
    if os.path.lexists(marker) and not w1_marker(marker):
        # An R1 crash marker: honour the owed restore before taking ownership.
        prior = restore_automatic(marker, runner=runner)
        record["prior_marker_restore"] = prior
        if not prior["ok"]:
            record.update(ok=False, reason="an earlier High Power marker's Automatic restore failed")
            return record
    os.makedirs(os.path.dirname(marker) or ".", exist_ok=True)
    with open(marker, "w", encoding="utf-8") as handle:
        handle.write(W1_MARKER_TAG + "\n")
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
