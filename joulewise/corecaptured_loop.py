"""Parse launchd's corecaptured spawn reports from a syslog-style log read."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re


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


def count_spawns(log_text: str, now_epoch_s: float, *, after_epoch_s: float | None = None) -> SpawnObservation:
    """Count spawn reports within ten minutes, optionally strictly after a cure.

    Raises ValueError for a missing header or a malformed timestamped record;
    callers decide whether an unavailable observation is a refusal.
    """
    lines = log_text.splitlines()
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
                and now_epoch_s - 600 <= epoch <= now_epoch_s
                and (after_epoch_s is None or epoch > after_epoch_s)):
            matched.append(match.group("timestamp"))
    return SpawnObservation(len(matched), matched[0] if matched else None,
                            matched[-1] if matched else None)
