"""Build-keyed hold on claim authority."""

from __future__ import annotations

import subprocess


CLAIM_HELD_OS_BUILDS: dict[str, str] = {
    "25G83": "H1-25G83-CAP-CADENCE (SCI-25G83-CANDIDATE-01-A1 §5.3)",
}
UNKNOWN_BUILD_HOLD = "UNKNOWN-OS-BUILD (a build that cannot be read is treated as held)"


def claim_hold_for_os_build(os_build: object) -> str | None:
    """The name of the hold on this build, or None if claims are allowed."""
    if not isinstance(os_build, str) or not os_build:
        return UNKNOWN_BUILD_HOLD
    return CLAIM_HELD_OS_BUILDS.get(os_build)


def machine_os_build() -> str | None:
    """`/usr/sbin/sysctl -n kern.osversion`, stripped; None on any failure."""
    try:
        completed = subprocess.run(
            ["/usr/sbin/sysctl", "-n", "kern.osversion"],
            capture_output=True, text=True, check=True,
        )
        return completed.stdout.strip() or None
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return None
