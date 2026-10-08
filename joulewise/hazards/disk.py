"""Disk hazard: not enough free space for the window's bytes.

Measured directly with ``os.statvfs`` (free bytes available to an unprivileged
writer, ``f_bavail x f_frsize``) on the runs-root volume and on each backup
destination.  Targets on the same volume (same ``st_dev``) share its free
space, so their planned copies are added.

Arm (plan §2.3): on every volume, free >= planned bytes x the copies planned
on that volume + 20 GiB headroom.  ALPHA: about 182 MiB per bundle (block 3
measured) x 119 members = 21.2 GiB, so about 41 GiB on the runs volume.  264
GiB were free on 10-05.  A target that does not exist or cannot be read is
UNMEASURED and refuses.

In the window the monitor reads every 60 s.  Below 10 GiB on any target it
journals ``disk.low`` and creates the marker file ``monitor/disk.low``; the
driver stops the chain on that marker, because a write failure is imminent.

Ported from ``prewindow.t0_check`` (``shutil.disk_usage`` free >= 20 GiB) and
the backup-destination logic of ``arm_readiness_evidence_t0.py:2058-2070``
(each destination >= 20 GiB free).
"""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from joulewise.hazards.base import (
    PASS, REFUSE, UNMEASURED, Context, Measurement, Verdict, require_thresholds, row,
)

MODULE = "disk"
GIB = 1024 ** 3

DEFAULT_THRESHOLDS: dict[str, Any] = {
    "planned_bytes": int(round(182 * 1024 ** 2 * 119)),  # ALPHA estimate; the plan supplies its own
    "headroom_bytes": 20 * GIB,
    "low_bytes": 10 * GIB,
}
ARM_THRESHOLD_KEYS = ("planned_bytes", "headroom_bytes")

Statvfs = Callable[[str], Any]
Stat = Callable[[str], Any]


def measure(ctx: Context, *, targets: Sequence[Mapping[str, Any]],
            statvfs: Statvfs = os.statvfs, stat: Stat = os.stat) -> Measurement:
    """``targets``: ``[{"path": str, "copies": int}, ...]`` (runs root first).

    ``copies`` is how many copies of the window's planned bytes land on that
    path (1 for the runs root; 1 for a backup destination; 0 for a path that
    only needs headroom).
    """

    started = ctx.stamp()
    rows = []
    error = None
    for target in targets:
        path = str(target["path"])
        copies = int(target.get("copies", 1))
        entry: dict[str, Any] = {"path": path, "copies": copies}
        try:
            result = statvfs(path)
            entry.update(device=int(stat(path).st_dev), free_bytes=int(result.f_bavail) * int(result.f_frsize),
                         total_bytes=int(result.f_blocks) * int(result.f_frsize),
                         f_bavail=int(result.f_bavail), f_frsize=int(result.f_frsize))
        except OSError as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
            error = error or f"statvfs {path}: {entry['error']}"
        rows.append(entry)
    if not rows:
        error = "no disk target given"
    finished = ctx.stamp()
    return Measurement(MODULE, "instant", {"targets": rows}, (), started, finished, error)


def volumes(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Group target rows by device; the volume's free space is read once per device."""

    grouped: dict[int, dict[str, Any]] = {}
    for item in rows:
        volume = grouped.setdefault(item["device"], {"device": item["device"], "paths": [],
                                                     "copies": 0,
                                                     "free_bytes": item["free_bytes"]})
        volume["paths"].append(item["path"])
        volume["copies"] += item["copies"]
        volume["free_bytes"] = min(volume["free_bytes"], item["free_bytes"])
    return list(grouped.values())


def judge(measurement: Measurement, thresholds: Mapping[str, Any]) -> Verdict:
    limits = require_thresholds(MODULE, thresholds, ARM_THRESHOLD_KEYS)
    if measurement.module != MODULE:
        raise ValueError("disk.judge received another module's measurement")
    if measurement.error:
        return Verdict(MODULE, UNMEASURED, (measurement.error,), limits)
    reasons = []
    observed = []
    for volume in volumes(measurement.values["targets"]):
        required = limits["planned_bytes"] * volume["copies"] + limits["headroom_bytes"]
        observed.append({**volume, "required_bytes": required})
        if volume["free_bytes"] < required:
            reasons.append(f"{', '.join(volume['paths'])}: {volume['free_bytes'] / GIB:.1f} GiB free "
                           f"< {required / GIB:.1f} GiB required "
                           f"({volume['copies']} planned copies + headroom)")
    return Verdict(MODULE, REFUSE if reasons else PASS, tuple(reasons), limits,
                   {"volumes": observed})


def low(measurement: Measurement, low_bytes: int) -> list[dict[str, Any]]:
    """In-window: the targets below ``low_bytes`` (``disk.low``).  An unreadable
    target is the measurement's ``error``, journaled as unmeasured, not low."""

    out = []
    for item in measurement.values.get("targets", []):
        if "error" not in item and item["free_bytes"] < low_bytes:
            out.append({"path": item["path"], "free_bytes": item["free_bytes"],
                        "low_bytes": low_bytes})
    return out


def planned_target(path: str | Path, copies: int = 1) -> dict[str, Any]:
    return {"path": str(path), "copies": int(copies)}


# Inventory rows (configs/gates/physics_rows.json) whose physical check this
# module performs.  tests/hazards/test_physics_coverage.py keeps the two in step.
PROTECTS: tuple[tuple[str, str, str, int], ...] = (
    # base line 94: shutil.disk_usage free >= 20 GiB.
    row("joulewise/prewindow.py", "t0_check",
        "BLOCK only N GB free", 1),
    # base line 98: disk_usage ran.
    row("joulewise/prewindow.py", "t0_check",
        "BLOCK disk headroom probe failed", 1),
    # base line 154: df -g free space >= 20 GB (a df failure counts as 0 and blocks).
    row("scripts/prewindow_check.sh", "check_once",
        "BLOCK only N GB free", 1),
)

# Proxy rows on paths block 5 no longer runs that this module's direct
# measurement replaces (configs/gates/physics_rows.json, "retired_proxy").
SUPERSEDES: tuple[tuple[str, str, str, int], ...] = (
    # base line 1148: The claim and bound backup destinations exist, are distinct and writable, and eac...
    row("joulewise/arm_readiness.py", "<module>",
        "predicate t0.storage_backup_capacity.v1", 1),
    # base line 7168: The BACKUP_PREFLIGHT receipt says the backup destinations exist, are distinct, ar...
    row("joulewise/arm_readiness.py", "_evaluate_rows",
        "readiness_backup_preflight_refused (row t0.storage_backup_capacity)", 1),
    # base line 2070: Disk: either backup destination has under 20 GiB free (statvfs).
    row("joulewise/arm_readiness_evidence_t0.py", "_derive_backup",
        "evidence_author_t0_backup_preflight_underivable", 1),
)
