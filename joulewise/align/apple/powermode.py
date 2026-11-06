"""Read-only observation of the host's AC-profile ``powermode`` (council ruling 7).

``pmset -g custom`` prints one block per power source. Only the ``AC Power:``
block is read, and only an exact ``powermode`` key: ``lowpowermode`` and the
battery profile never match. Observation never changes the setting.
"""
from __future__ import annotations

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
