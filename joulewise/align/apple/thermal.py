"""ALIGN in-process SMC sidecar, config slots and coverage.

Sensor names do not establish die/heatsink identity. R0 proposals remain
PROVISIONAL until checked on the measurement machine. No admission thresholds
or scientific eligibility rules are installed by this diagnostic sidecar.
"""
from __future__ import annotations

import math
import json
import os
import re
import threading
from collections import deque
from pathlib import Path
from collections.abc import Mapping, Sequence
from typing import Any

NS = 1_000_000_000


def validate_policy(value: Any) -> dict[str, Any]:
    fields = {"s_fast", "s_slow", "fan_keys", "r0_sha256"}
    if not isinstance(value, Mapping) or set(value) != fields:
        raise ValueError("smc_temperature must have s_fast, s_slow, fan_keys, r0_sha256")
    for role in ("s_fast", "s_slow"):
        if not isinstance(value[role], str) or not re.fullmatch(r"T[!-~]{3}", value[role]):
            raise ValueError(f"smc_temperature.{role} must be a four-character temperature key")
    if value["s_fast"] == value["s_slow"]:
        raise ValueError("smc_temperature fast and slow keys must differ")
    fans = value["fan_keys"]
    if (not isinstance(fans, list) or any(not isinstance(k, str) or not re.fullmatch(r"F[!-~]Ac", k)
                                          for k in fans) or len(set(fans)) != len(fans)):
        raise ValueError("smc_temperature.fan_keys must be distinct F?Ac keys (empty for fanless hosts)")
    if not isinstance(value["r0_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", value["r0_sha256"]):
        raise ValueError("smc_temperature.r0_sha256 must pin the R0 JSON bytes")
    return {**value, "fan_keys": list(fans)}


def keys(policy: Mapping[str, Any]) -> tuple[str, ...]:
    return (policy["s_fast"], policy["s_slow"], *policy["fan_keys"])


def valid_value(key: str, value: Any) -> bool:
    return (type(value) in (int, float) and math.isfinite(value)
            and (-40 <= value <= 150 if key.startswith("T") else value >= 0))


def sample(reader: Any, selected: Sequence[str]) -> dict[str, Any]:
    """Failed/implausible keys are null with a reason; zero RPM is valid."""
    try:
        result = reader.read(selected) if reader is not None else {"errors": {}}
        values, errors = result.get("values", {}), dict(result.get("errors", {}))
    except Exception as exc:
        result = {}
        values, errors = {}, {k: f"{type(exc).__name__}: {exc}" for k in selected}
    clean = {}
    for key in selected:
        value = values.get(key)
        if key not in errors and valid_value(key, value):
            clean[key] = value
        else:
            clean[key] = None
            errors.setdefault(key, "missing, non-finite or implausible SMC value")
    return {"source": "smc", "sensors": clean,
            "units": {k: "degC" if k.startswith("T") else "rpm" if k.endswith("Ac") else "raw" for k in selected},
            "errors": {k: errors[k] for k in selected if k in errors},
            "readings": {k: {**result.get("raw", {}).get(k, {}), "value": clean[k],
                              "error": errors.get(k)} for k in selected}}


class Sidecar:
    """One reader/thread, from adapter prepare to teardown, bundle-local only.

    Gate/hold logic is supplied by the gate lane. It can inspect ``readings``
    and record phase boundaries with ``event``; this collector invents no gate.
    ``tick`` and ``start(background=False)`` are deterministic test seams.
    """
    def __init__(self, outputs_dir: Path, config: Mapping[str, Any], *, reader=None, ctx=None):
        from joulewise.hazards.base import Context
        from joulewise.align.apple.smc_reader import Reader
        self.config = validate_policy(config)
        self.selected = keys(self.config)
        self.path = Path(outputs_dir) / "align_thermal.jsonl"
        self.reader = reader if reader is not None else Reader()
        self.ctx = ctx if ctx is not None else Context()
        self.readings = deque(maxlen=3600)
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread = None
        self._file = None
        self._error = None
        self._seq = 0

    def _write(self, kind, values, started=None, finished=None):
        with self._lock:
            started = started or self.ctx.stamp()
            finished = finished or started
            self._seq += 1
            row = {"schema": "joulewise.align_thermal.v1", "module": "temperature", "kind": kind,
                   "session": self.session, "seq": self._seq, "started": started.to_json(),
                   "finished": finished.to_json(), "values": values, "raw": [],
                   "error": "; ".join(values.get("errors", {}).values()) or None}
            self._file.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
            self._file.flush()
            if finished.monotonic_ns - self._synced_ns >= 5 * NS:
                os.fsync(self._file.fileno())
                self._synced_ns = finished.monotonic_ns
            return row

    def start(self, *, background=True):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("x", encoding="utf-8")
        stamp = self.ctx.stamp()
        self.session = f"align-{stamp.monotonic_ns}"
        self._synced_ns = stamp.monotonic_ns
        self.counter = Coverage(stamp.monotonic_ns, self.selected)
        self._write("session_start", {"thermal": self.config}, stamp)
        if background:
            self._thread = threading.Thread(target=self._loop, name="align-thermal", daemon=True)
            self._thread.start()

    def tick(self):
        with self._lock:
            started = self.ctx.stamp()
            values = sample(self.reader, self.selected)
            finished = self.ctx.stamp()
            self.counter.observe(started.monotonic_ns, finished.monotonic_ns, values)
            row = self._write("reading", values, started, finished)
            self.readings.append(row)
            return row

    def _loop(self):
        due = self.ctx.clocks.monotonic_ns()
        try:
            while not self._stop.is_set():
                delay = (due - self.ctx.clocks.monotonic_ns()) / NS
                if delay > 0 and self._stop.wait(delay):
                    return
                self.tick()
                due += NS
                now = self.ctx.clocks.monotonic_ns()
                if due <= now:
                    due += ((now - due) // NS + 1) * NS
        except Exception as exc:
            self._error = exc
            self._stop.set()

    def event(self, kind: str, values: Mapping[str, Any]):
        if kind not in ("align_thermal_gate", "align_thermal_hold"):
            raise ValueError("unknown ALIGN thermal phase event")
        return self._write(kind, dict(values))

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join()
            self._thread = None
        try:
            if self._file is not None:
                self._write("session_end", {"coverage": self.counter.report(self.ctx.clocks.monotonic_ns()),
                                            "collector_error": str(self._error) if self._error else None})
                os.fsync(self._file.fileno())
        finally:
            if self._file is not None:
                self._file.close()
                self._file = None
            self.reader.close()
        if self._error is not None:
            raise RuntimeError(f"ALIGN thermal collector failed: {self._error}") from self._error


class Coverage:
    """Unique successful slots / ceil(span seconds); never interpolate.

    Slots are [start+i seconds, start+(i+1) seconds). A read belongs to the
    slot where it started, provided it finished inside that same slot. Late
    and duplicate reads cannot repair missed slots. Constant valid readings
    count: unlike battery publications, a constant temperature is legitimate.
    """

    def __init__(self, start_ns: int, selected: Sequence[str]):
        self.start_ns = start_ns
        self.slots: dict[str, set[int]] = {k: set() for k in selected}

    def observe(self, started_ns: int, finished_ns: int, values: Mapping[str, Any]) -> None:
        slot = (started_ns - self.start_ns) // NS
        if slot < 0 or finished_ns < started_ns or (finished_ns - self.start_ns) // NS != slot:
            return
        for key in self.slots:
            if key not in values.get("errors", {}) and valid_value(key, values.get("sensors", {}).get(key)):
                self.slots[key].add(slot)

    def report(self, end_ns: int) -> dict[str, Any]:
        if end_ns < self.start_ns:
            raise ValueError("temperature span ends before it starts")
        expected = (end_ns - self.start_ns + NS - 1) // NS

        def stats(good):
            good = {i for i in good if 0 <= i < expected}
            gaps = []
            for slot in range(expected):
                if slot in good:
                    continue
                lo, hi = self.start_ns + slot * NS, min(end_ns, self.start_ns + (slot + 1) * NS)
                if gaps and gaps[-1][1] == lo:
                    gaps[-1][1] = hi
                else:
                    gaps.append([lo, hi])
            return {"expected_samples": expected, "valid_samples": len(good),
                    "sample_fraction": len(good) / expected if expected else None,
                    "gaps_ns": gaps}

        common = set.intersection(*self.slots.values()) if self.slots else set()
        return {"clock": "monotonic_ns", "period_ns": NS, "span_ns": [self.start_ns, end_ns],
                "all_keys": stats(common), "per_key": {k: stats(v) for k, v in self.slots.items()}}


def coverage(lines: Sequence[Mapping[str, Any]], start_ns: int, end_ns: int,
             selected: Sequence[str]) -> dict[str, Any]:
    """Desk-side recomputation over any span, including monitor restarts."""
    counter = Coverage(start_ns, selected)
    for row in lines:
        if row.get("module") == "temperature" and row.get("kind") == "reading":
            started, finished = row["started"]["monotonic_ns"], row["finished"]["monotonic_ns"]
            if start_ns <= started < end_ns and finished <= end_ns:
                counter.observe(started, finished, row["values"])
    return counter.report(end_ns)
