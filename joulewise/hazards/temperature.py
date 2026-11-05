"""Optional ALIGN SMC journal policy and one-second slot coverage.

Sensor names do not establish die/heatsink identity. R0 proposals remain
PROVISIONAL until checked on the measurement machine. No admission thresholds
or scientific eligibility rules are installed by this diagnostic sidecar.
"""
from __future__ import annotations

import math
import re
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
            "units": {k: "degC" if k.startswith("T") else "rpm" for k in selected},
            "errors": {k: errors[k] for k in selected if k in errors}}


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
