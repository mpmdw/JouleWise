"""Parse launchd's corecaptured spawn reports from a syslog-style log read."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re


# Thresholds and waits shared by the t0 gate and the arm check (cold ruling 16
# Q2/Q3, 2026-09-23). One home, so the two sides cannot drift apart.
WINDOW_S = 600
SPAWNS_MAX = 2                  # more than this in WINDOW_S is a respawn loop
WIFI_OFF_S = 8                  # radio off time in the one licensed cycle
POST_TOGGLE_WAIT_S = 180        # observation after the cycle
POST_TOGGLE_SPAWNS_MIN = 1      # this many new spawns after the cycle = persisting

LOG_ARGV = ("/usr/bin/log", "show", "--last", "10m", "--style", "syslog",
            "--predicate", 'process == "launchd" AND eventMessage CONTAINS "corecaptured"')
SPAWN_LINE = re.compile(
    r"^launchd\[1\]: \[system/com\.apple\.corecaptured \[(?P<pid>[0-9]+)\]:\] "
    r"Successfully spawned corecaptured\[(?P=pid)\](?: because .*)?$"
)
TIMESTAMPED_LINE = re.compile(
    r"^(?P<timestamp>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+[+-]\d{4})\s+"
    r"\S+\s+(?P<message>.*)$"
)


@dataclass(frozen=True)
class SpawnObservation:
    count: int
    first: str | None
    last: str | None


def count_spawns(log_text: str, now_epoch_s: float, *, after_epoch_s: float | None = None,
                 until_epoch_s: float | None = None) -> SpawnObservation:
    """Count spawns from ten minutes before a read through its completion.

    ``now_epoch_s`` is the clock immediately before the log command. A caller
    may supply its clock after the command as ``until_epoch_s``. Raises
    ValueError for a missing header or a malformed nonblank record;
    callers decide whether an unavailable observation is a refusal.
    """
    if until_epoch_s is not None and until_epoch_s < now_epoch_s:
        # A wall clock stepped backward during the read would shrink the
        # window and could report a false zero; the read is not measured.
        raise ValueError("clock moved backward during the corecaptured log read")
    lines = [line for line in log_text.splitlines() if line.strip()]
    if not lines or not lines[0].startswith("Timestamp "):
        raise ValueError("corecaptured log has no syslog header")
    matched: list[str] = []
    for line in lines[1:]:
        match = TIMESTAMPED_LINE.fullmatch(line)
        if match is None:
            raise ValueError("corecaptured log has an unparseable line")
        try:
            epoch = datetime.fromisoformat(match.group("timestamp")).timestamp()
        except ValueError as exc:
            raise ValueError("corecaptured log has an invalid timestamp") from exc
        if (SPAWN_LINE.fullmatch(match.group("message"))
                and now_epoch_s - WINDOW_S <= epoch <= (now_epoch_s if until_epoch_s is None else until_epoch_s)
                and (after_epoch_s is None or epoch > after_epoch_s)):
            matched.append(match.group("timestamp"))
    return SpawnObservation(len(matched), matched[0] if matched else None,
                            matched[-1] if matched else None)
