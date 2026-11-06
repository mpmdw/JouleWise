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
# The one restore command the narrow sudo rule allows (the R1 chain's rule).
RESTORE_AUTOMATIC = ("sudo", "-n", "/usr/bin/pmset", "-c", "powermode", "0")
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

    If the R1 High Power ``marker`` exists, Automatic is restored first with
    the narrow sudo rule and the mode is read again; the marker is removed only
    after a successful restore. Returns the record a caller stores in its arm
    or admission evidence; ``admitted`` is False with a ``reason`` otherwise.
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
    if marker is not None and os.path.lexists(marker):
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
