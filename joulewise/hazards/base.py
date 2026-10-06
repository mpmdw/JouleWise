"""Common shape of the hazard modules (gate-prune plan §2.1).

Each hazard module measures one physical quantity directly and exposes:

- ``measure(ctx) -> Measurement``: the raw values, the path and SHA-256 of
  every raw byte string the probe returned, and three timestamps taken when
  the probe started and when it finished;
- ``judge(measurement, thresholds) -> Verdict``: PASS, REFUSE or UNMEASURED
  with reasons.  UNMEASURED (the probe failed, timed out or returned bytes
  that do not parse) refuses at arm; in the window it becomes an
  ``<module>.unmeasured`` finding for the affected span;
- ``PROTECTS``: the inventory rows, keyed ``(file, function, code,
  occurrence)``, whose physical check this module now performs;
- ``SUPERSEDES``: the inventory rows that read a proxy for this module's
  quantity on a path block 5 no longer runs.

The three timestamps of a :class:`Stamp` are CLOCK_REALTIME (``wall_ns``),
``time.monotonic_ns()`` (the controller's stamp domain, mach absolute time on
macOS) and CLOCK_MONOTONIC_RAW (mach continuous time).  Every reading carries
all three so that a harvest can join it exactly to a member's sampler stream
(controller ``time.monotonic_ns``) and to the clock anchor (RAW).

This module imports nothing outside the standard library.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import signal
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

PASS = "PASS"
REFUSE = "REFUSE"
UNMEASURED = "UNMEASURED"
STATUSES = (PASS, REFUSE, UNMEASURED)

MEASUREMENT_SCHEMA = "joulewise.hazard_measurement.v1"
VERDICT_SCHEMA = "joulewise.hazard_verdict.v1"

# A probe child gets its own process group so a timeout can kill everything
# it started.  Every probe argv used by this package is read-only.
DEFAULT_PROBE_TIMEOUT_S = 10.0
C_LOCALE_ENV = {"LC_ALL": "C"}


# --------------------------------------------------------------------------
# Clocks


@dataclasses.dataclass(frozen=True)
class Stamp:
    """One instant read on the three clocks, in nanoseconds."""

    wall_ns: int
    monotonic_ns: int
    monotonic_raw_ns: int

    def to_json(self) -> dict[str, int]:
        return {"wall_ns": self.wall_ns, "monotonic_ns": self.monotonic_ns,
                "monotonic_raw_ns": self.monotonic_raw_ns}

    @classmethod
    def from_json(cls, value: Mapping[str, Any]) -> "Stamp":
        fields = ("wall_ns", "monotonic_ns", "monotonic_raw_ns")
        if not isinstance(value, Mapping) or set(value) != set(fields):
            raise ValueError("stamp must carry exactly wall_ns, monotonic_ns, monotonic_raw_ns")
        for name in fields:
            if type(value[name]) is not int:
                raise ValueError(f"stamp {name} must be an integer")
        return cls(value["wall_ns"], value["monotonic_ns"], value["monotonic_raw_ns"])


class SystemClocks:
    """The production clocks.  Tests replace this object, never the functions."""

    def realtime_ns(self) -> int:
        return time.clock_gettime_ns(time.CLOCK_REALTIME)

    def monotonic_ns(self) -> int:
        return time.monotonic_ns()

    def monotonic_raw_ns(self) -> int:
        return time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)

    def clock_gettime_ns(self, clock_id: int) -> int:
        return time.clock_gettime_ns(clock_id)

    def stamp(self) -> Stamp:
        raw = self.monotonic_raw_ns()
        monotonic = self.monotonic_ns()
        wall = self.realtime_ns()
        return Stamp(wall_ns=wall, monotonic_ns=monotonic, monotonic_raw_ns=raw)

    def sleep(self, seconds: float) -> None:
        if seconds > 0:
            time.sleep(seconds)


SYSTEM_CLOCKS = SystemClocks()


# --------------------------------------------------------------------------
# Probes


@dataclasses.dataclass(frozen=True)
class Completed:
    """The result of one probe child: exact stdout/stderr bytes."""

    argv: tuple[str, ...]
    returncode: int | None
    stdout: bytes
    stderr: bytes
    timed_out: bool = False
    error: str | None = None  # the child could not be spawned at all

    @property
    def ok(self) -> bool:
        return self.error is None and not self.timed_out and self.returncode == 0


Runner = Callable[[Sequence[str], float], Completed]


def run_probe(argv: Sequence[str], timeout_s: float = DEFAULT_PROBE_TIMEOUT_S) -> Completed:
    """Run one read-only probe in its own process group with a hard timeout.

    Never raises for a probe failure: a spawn error, a timeout or a nonzero
    exit is returned as data, and the module's ``judge`` turns it into
    UNMEASURED.
    """

    argv = tuple(str(item) for item in argv)
    env = {**os.environ, **C_LOCALE_ENV}
    try:
        process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, env=env, start_new_session=True)
    except OSError as exc:
        return Completed(argv, None, b"", b"", error=f"{type(exc).__name__}: {exc}")
    try:
        stdout, stderr = process.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        _kill_group(process.pid)
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            stdout, stderr = b"", b""
        return Completed(argv, process.returncode, stdout or b"", stderr or b"", timed_out=True)
    except BaseException:
        _kill_group(process.pid)
        process.wait()
        raise
    return Completed(argv, process.returncode, stdout, stderr)


def _kill_group(pgid: int) -> None:
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(pgid, sig)
        except (ProcessLookupError, PermissionError):
            return
        time.sleep(0.05)


# --------------------------------------------------------------------------
# Raw bytes


@dataclasses.dataclass(frozen=True)
class RawRef:
    """Where one raw byte string was kept, with its digest."""

    name: str
    sha256: str
    size: int
    path: str | None  # relative to the context's custody root when it has one

    def to_json(self) -> dict[str, Any]:
        return {"name": self.name, "sha256": self.sha256, "size": self.size, "path": self.path}


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_create_once(path: Path, data: bytes) -> None:
    """Create ``path`` exclusively, write ``data`` and fsync file and directory."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    fsync_directory(path.parent)


def fsync_directory(directory: Path) -> None:
    try:
        descriptor = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


# --------------------------------------------------------------------------
# Context, Measurement, Verdict


@dataclasses.dataclass
class Context:
    """Everything a ``measure`` call may touch.  Hardware seams are injectable.

    ``raw_dir``: where raw probe bytes are written create-once (``None`` keeps
    only their digests).  ``custody_root``: raw paths are recorded relative to
    it.  ``label``: a prefix that keeps raw file names unique within a run.
    Module inputs that are not hardware seams (the disk targets, the
    measurement tree) are passed as keyword arguments to ``measure``.
    """

    run: Runner = run_probe
    clocks: Any = SYSTEM_CLOCKS
    raw_dir: Path | None = None
    custody_root: Path | None = None
    label: str = ""
    probe_timeout_s: float = DEFAULT_PROBE_TIMEOUT_S

    def stamp(self) -> Stamp:
        return self.clocks.stamp()

    def keep_raw(self, name: str, data: bytes) -> RawRef:
        digest = sha256_hex(data)
        path_text: str | None = None
        if self.raw_dir is not None:
            prefix = f"{self.label}-" if self.label else ""
            target = Path(self.raw_dir) / f"{prefix}{name}"
            write_create_once(target, data)
            if self.custody_root is not None:
                try:
                    path_text = str(target.resolve().relative_to(Path(self.custody_root).resolve()))
                except ValueError:
                    path_text = str(target)
            else:
                path_text = str(target)
        return RawRef(name=name, sha256=digest, size=len(data), path=path_text)


@dataclasses.dataclass(frozen=True)
class Measurement:
    module: str
    kind: str  # "instant", or a module-specific series kind such as "dwell"
    values: Mapping[str, Any]
    raw: tuple[RawRef, ...]
    started: Stamp
    finished: Stamp
    error: str | None = None  # set when the probe failed: judge returns UNMEASURED

    def to_json(self) -> dict[str, Any]:
        return {"schema": MEASUREMENT_SCHEMA, "module": self.module, "kind": self.kind,
                "values": _jsonable(self.values), "raw": [item.to_json() for item in self.raw],
                "started": self.started.to_json(), "finished": self.finished.to_json(),
                "error": self.error}


@dataclasses.dataclass(frozen=True)
class Verdict:
    module: str
    status: str
    reasons: tuple[str, ...]
    thresholds: Mapping[str, Any]
    observed: Mapping[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"unknown verdict status {self.status!r}")
        if self.status != PASS and not self.reasons:
            raise ValueError("a REFUSE or UNMEASURED verdict needs a reason")

    @property
    def passed(self) -> bool:
        return self.status == PASS

    def to_json(self) -> dict[str, Any]:
        return {"schema": VERDICT_SCHEMA, "module": self.module, "status": self.status,
                "reasons": list(self.reasons), "thresholds": _jsonable(self.thresholds),
                "observed": _jsonable(self.observed)}


def unmeasured(module: str, measurement: Measurement | None, thresholds: Mapping[str, Any],
               reason: str) -> Verdict:
    return Verdict(module, UNMEASURED, (reason,), dict(thresholds))


def finding(code: str, *, span: Mapping[str, Any] | None, observed: Any, expected: Any,
            detail: str, evidence: Sequence[Mapping[str, Any]] = (),
            interval: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """One in-window physics finding.  The flag package wraps it as a flag;
    this package never imports flag code (plan §2.1)."""

    return {"code": code, "span": dict(span) if span is not None else None,
            "interval": dict(interval) if interval is not None else None,
            "observed": _jsonable(observed), "expected": _jsonable(expected),
            "detail": detail, "evidence": [dict(item) for item in evidence]}


def coverage_gap(points: Sequence[int], start: int, stop: int,
                 max_gap_ns: int) -> list[int] | None:
    """The first monotonic gap longer than ``max_gap_ns`` overlapping [start, stop].

    ``points`` are the monotonic stamps of good readings.  A span is covered
    when a good reading lies at most ``max_gap_ns`` before its start and after
    its stop and no two consecutive good readings across it are further apart
    than ``max_gap_ns``.  Returns ``[a, b]`` (the uncovered stretch) or None.
    """

    ordered = sorted(points)
    before = [p for p in ordered if p <= start]
    after = [p for p in ordered if p >= stop]
    if not before or start - before[-1] > max_gap_ns:
        return [before[-1] if before else start, min([p for p in ordered if p > start] or [stop])]
    if not after or after[0] - stop > max_gap_ns:
        return [max([p for p in ordered if p < stop] or [start]), after[0] if after else stop]
    inside = [before[-1], *[p for p in ordered if start < p < stop], after[0]]
    for a, b in zip(inside, inside[1:]):
        if b - a > max_gap_ns:
            return [a, b]
    return None


def require_thresholds(module: str, thresholds: Mapping[str, Any],
                       keys: Sequence[str]) -> dict[str, Any]:
    if not isinstance(thresholds, Mapping):
        raise ValueError(f"{module} thresholds must be a mapping")
    missing = [key for key in keys if key not in thresholds]
    if missing:
        raise ValueError(f"{module} thresholds missing {', '.join(missing)}")
    for key in keys:
        value = thresholds[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{module} threshold {key} must be a number")
    return dict(thresholds)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, Path):
        return str(value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        to_json = getattr(value, "to_json", None)
        return to_json() if callable(to_json) else _jsonable(dataclasses.asdict(value))
    return value


def row(file: str, function: str, code: str, occurrence: int = 1) -> tuple[str, str, str, int]:
    """One inventory row key (file, function, code, occurrence); see
    ``configs/gates/physics_rows.json``."""

    return (file, function, code, occurrence)


__all__ = [
    "C_LOCALE_ENV", "Completed", "Context", "DEFAULT_PROBE_TIMEOUT_S", "Measurement", "PASS",
    "REFUSE", "RawRef", "Runner", "STATUSES", "SYSTEM_CLOCKS", "Stamp", "SystemClocks",
    "UNMEASURED", "Verdict", "canonical_json", "coverage_gap", "finding", "fsync_directory", "require_thresholds",
    "row", "run_probe", "sha256_hex", "unmeasured", "write_create_once",
]
