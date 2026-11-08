"""Own-capture refits and exact session calibration arithmetic."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Any, Mapping, Sequence

from joulewise.b6.registration import decimal_s
from joulewise.b6.capture_screen import operative_bound_stop_s


@dataclass(frozen=True)
class Capture:
    value_s: Decimal | None
    status: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


def read_own_capture(directory: Path | str) -> Capture:
    """Refit the capture's raw bytes; preserve the exact stored time lexeme."""
    from joulewise.powermetrics_fiducial import verify_stored_evidence_physics

    root = Path(directory)
    try:
        raw = (root / "instrument_evidence.json").read_bytes()
    except (FileNotFoundError, NotADirectoryError):
        return Capture(None, "absent")
    try:
        exact = json.loads(raw, parse_float=Decimal)
        stored = decimal_s(exact["b_fiducial_s"])
        evidence = json.loads(raw)
        refit = decimal_s(verify_stored_evidence_physics(
            evidence, (root / "raw/powermetrics.plist").read_bytes(),
            (root / "events.jsonl").read_bytes()))
        return Capture(max(stored, refit), "valid", {
            key: evidence.get(key) for key in
            ("protocol_id", "protocol_sha256", "estimator_sha256")})
    except (OSError, ValueError, TypeError, KeyError, ArithmeticError):
        return Capture(None, "refit_failed")


def evaluate(pre: Capture, post: Capture, reg: Mapping,
             other_rows: Sequence[Mapping], own_session_ids: Sequence[str],
             estimator_changed: bool, *, pack_id: str | None = None) -> dict[str, Any]:
    """Times only; other sessions cannot contribute to the operative bound."""
    cal = reg.get("calibration", reg)
    reference = decimal_s(cal["alignment_reference_s"])
    corpus = [decimal_s(item) for item in cal["acceptance_corpus"]]
    flags: list[dict[str, Any]] = []
    excluding: list[str] = []

    def flag(code: str, **observed: Any) -> None:
        flags.append({"code": code, **observed})

    for slot, capture in (("pre", pre), ("post", post)):
        if capture.value_s is not None and capture.status == "valid":
            if capture.value_s > reference:
                flag("calibration.alignment_above_reference", slot=slot)
            if corpus and not min(corpus) <= capture.value_s <= max(corpus):
                flag("calibration.capture_outside_acceptance_range", slot=slot)
    if estimator_changed:
        flag("calibration.estimator_code_changed")
    others = [row for row in other_rows if row.get("session_id") not in own_session_ids]
    systematic = [row.get("seq") for row in others if row.get("disposition") == "systematic-invalid"]
    if systematic:
        flag("calibration.other_session_systematic", sequences=systematic)
    valid = [row for row in others if row.get("disposition") == "valid"]
    expanded = []
    for row in valid:
        try:
            value = decimal_s(row["value_s"])
        except (ValueError, TypeError, KeyError, ArithmeticError):
            continue
        if corpus and not min(corpus) <= value <= max(corpus):
            expanded.append(row.get("seq"))
    if expanded:
        flag("calibration.other_session_range_expansion", sequences=expanded)
    threshold = 2 * len(corpus)
    # Count valid observations in the list, including own-session observations;
    # the corpus is the registered initial sample, not added a second time.
    count = sum(row.get("disposition") == "valid" for row in other_rows)
    if threshold and count >= threshold:
        flag("calibration.corpus_doubling_reached", count=count, threshold=threshold)
    stop = operative_bound_stop_s(reg, pack_id)
    if stop is None:
        flag("calibration.stop_line_unsized", pack_id=pack_id or reg.get("pack_id"))
    drift = allowance = bound = None
    if any(c.value_s is None or c.status != "valid" for c in (pre, post)):
        excluding.append("calibration.bracket_incomplete")
    else:
        with localcontext() as ctx:
            ctx.prec = max(50, len(pre.value_s.as_tuple().digits) + len(post.value_s.as_tuple().digits) + 10)
            drift = abs(pre.value_s - post.value_s)
            allowance = max(drift, decimal_s(cal["bracket_screen_s"]))
            bound = max(pre.value_s, post.value_s) + allowance
        if drift > decimal_s(cal["max_budgetable_drift_s"]):
            flag("calibration.drift_above_budget")
        if stop is not None and bound > decimal_s(stop):
            excluding.append("calibration.operative_bound_above_stop")
    return {"pre_s": None if pre.value_s is None else str(pre.value_s),
            "post_s": None if post.value_s is None else str(post.value_s),
            "drift_s": None if drift is None else str(drift),
            "allowance_s": None if allowance is None else str(allowance),
            "operative_bound_s": None if bound is None else str(bound),
            "flags": flags, "excluding": excluding}
