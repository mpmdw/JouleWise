"""Non-issuing sidecar validation scaffold; the producer/contract is pending.

This closed candidate wire binds the reader digest, registered contrast cells,
floor identity and the arithmetic of the expanded decision interval. It cannot
register the paper claim gate or serve as a producer acceptance artifact.
"""
from __future__ import annotations

import math
import re


_SCHEMA = "joulewise.claim_side_bound.v1"
_ROW_KEYS = {"contrast_id", "source_cell_ids", "floor_artifact_id", "claim_side_bound_j",
             "metrology_aware_CI95", "decision_interval"}


def _interval(value: object) -> tuple[float, float] | None:
    if not isinstance(value, dict) or set(value) != {"lower", "upper"}:
        return None
    numbers = (value["lower"], value["upper"])
    if any(type(item) not in {int, float} or not math.isfinite(item) for item in numbers):
        return None
    return numbers if numbers[0] <= numbers[1] else None


def validate_claim_side_bound(value, *, claim_verdicts_sha256, finalized_manifest, floor_artifact) -> tuple[str, ...]:
    """Return private diagnostics; passing this candidate never authorizes prose."""
    if (not isinstance(value, dict) or set(value) != {"schema_version", "claim_verdicts_sha256", "contrasts"}
        or value.get("schema_version") != _SCHEMA or not isinstance(value.get("contrasts"), list)
        or not value["contrasts"]):
        return ("claim_side_bound_shape_invalid",)
    if (not isinstance(claim_verdicts_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", claim_verdicts_sha256) is None
        or value.get("claim_verdicts_sha256") != claim_verdicts_sha256):
        return ("claim_side_bound_reader_digest_mismatch",)
    try:
        registered = {row["contrast_id"]: row for row in finalized_manifest["contrasts"]}
        floor_cells = {row["cell_id"] for row in floor_artifact["cells"]}
        seen = set()
        for row in value["contrasts"]:
            if not isinstance(row, dict) or set(row) != _ROW_KEYS:
                return ("claim_side_bound_shape_invalid",)
            subject = row["contrast_id"]
            if subject in seen or subject not in registered:
                return ("claim_side_bound_contrast_mismatch",)
            seen.add(subject)
            sources = row["source_cell_ids"]
            # No transport guess: the pending producer must explicitly register
            # the source-cell join. Missing registration remains non-issuing.
            expected = registered[subject].get("source_cell_ids")
            if (not isinstance(sources, list) or not sources or sources != expected
                or len(set(sources)) != len(sources) or not set(sources) <= floor_cells):
                return ("claim_side_bound_cell_mismatch",)
            if row["floor_artifact_id"] != floor_artifact["artifact_id"]:
                return ("claim_side_bound_lineage_mismatch",)
            bound = row["claim_side_bound_j"]
            interval = _interval(row["metrology_aware_CI95"])
            decision = _interval(row["decision_interval"])
            if (type(bound) not in {int, float} or not math.isfinite(bound) or bound < 0
                or interval is None or decision is None
                or not math.isclose(decision[0], interval[0] - bound, rel_tol=1e-12, abs_tol=1e-12)
                or not math.isclose(decision[1], interval[1] + bound, rel_tol=1e-12, abs_tol=1e-12)):
                return ("claim_side_bound_arithmetic_mismatch",)
    except (KeyError, TypeError, ValueError):
        return ("claim_side_bound_shape_invalid",)
    return ()
