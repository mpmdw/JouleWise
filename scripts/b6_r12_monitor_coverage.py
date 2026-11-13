"""Read interval coverage from original monitor records, not row-start span."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

from b6_r12_verify import archive_pin, child, rows, sha

CONTENTION = "sources/night-custody/hazards/monitor/contention.jsonl"
LOADED_SHA = sha(Path(__file__))


def interval_coverage(data):
    bounds = []
    for row in rows(data):
        if row.get("kind") != "interval":
            continue
        value = (row.get("values") or {}).get("interval", {}).get("monotonic_ns")
        if (not isinstance(value, list) or len(value) != 2
                or any(type(n) is not int for n in value) or value[1] <= value[0]):
            raise ValueError("original contention interval bounds required")
        if bounds and value[0] < bounds[-1][0]:
            raise ValueError("contention intervals out of order")
        bounds.append(value)
    if not bounds:
        raise ValueError("original contention intervals missing")
    left, right = bounds[0]
    covered = gaps = 0
    for a, b in bounds[1:]:
        if a > right:
            covered += right - left
            gaps += 1
            left, right = a, b
        else:
            right = max(right, b)
    covered += right - left
    return {"coverage_s": covered / 1e9,
            "coverage_span_s": (right - bounds[0][0]) / 1e9,
            "coverage_gap_count": gaps, "interval_rows": len(bounds)}


def session_interval_coverage(root, session_id):
    """Authenticate the original bytes; add no interval or source judgment."""
    from joulewise.b6_analysis_inputs import AuthenticatedInputs
    if sha(Path(__file__)) != LOADED_SHA:
        raise ValueError("reload changed monitor coverage reader")
    metadata = json.loads((root / "sessions" / session_id / "session.json").read_bytes())
    archive = child(root, metadata["paths"]["archive"])
    reader = AuthenticatedInputs(archive, archive_pin(root, archive, metadata))
    raw = reader.read(archive / CONTENTION)
    return {**interval_coverage(raw), "source_sha256": hashlib.sha256(raw).hexdigest(),
            "helper_sha256": LOADED_SHA}
