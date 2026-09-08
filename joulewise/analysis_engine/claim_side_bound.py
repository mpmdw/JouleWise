"""Copy-only claim widening provenance; see paper_claim_side_bound.md (D-178).

Raw JSON bytes are mandatory: a parsed float cannot retain a JSON numeral's
spelling. This module neither estimates bounds nor licenses paper rendering.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import hashlib
import json
import math


_SCHEMA = "joulewise.claim_side_bound.v2"
_ROW_KEYS = {"contrast_id", "source_cell_ids", "floor_artifact_id",
             "deterministic_widening_total", "unit", "estimator_id", "ratio_estimand",
             "deterministic_bounds", "metrology_aware_CI95", "decision_interval"}
_ANCHOR = "E_clock_anchor_shift_bound_j"


class ClaimSideBoundRefusal(ValueError):
    """A private producer/validator refusal, never an empirical outcome."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class _JsonNumber:
    token: str


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _non_json_constant(token):
    raise ValueError(f"non-JSON number: {token}")


def _parse(raw):
    if type(raw) is not bytes:
        raise ValueError("raw UTF-8 JSON bytes required")
    return json.loads(raw.decode("utf-8"), parse_int=_JsonNumber,
                      parse_float=_JsonNumber, parse_constant=_non_json_constant,
                      object_pairs_hook=_object)


def _encode(value):
    if isinstance(value, _JsonNumber):
        return value.token
    if isinstance(value, dict):
        return "{" + ",".join(json.dumps(key) + ":" + _encode(item)
                              for key, item in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ",".join(_encode(item) for item in value) + "]"
    return json.dumps(value, ensure_ascii=True, allow_nan=False)


def _number(value, *, nonnegative=False):
    return (isinstance(value, _JsonNumber) and math.isfinite(float(value.token))
            and (not nonnegative or Decimal(value.token) >= 0))


def _interval(value):
    if (not isinstance(value, dict) or set(value) != {"lower", "upper"}
        or not all(_number(item) for item in value.values())):
        return None
    lower, upper = float(value["lower"].token), float(value["upper"].token)
    return ((lower, upper) if Decimal(value["lower"].token) <= Decimal(value["upper"].token) else None)


def _project(claim_verdicts, finalized_manifest, floor_artifact):
    """Validate provenance shape and select source fields without arithmetic."""
    registered = [row["contrast_id"] for row in finalized_manifest["contrasts"]]
    floor_cells = {row["cell_id"] for row in floor_artifact["cells"]}
    floor_id = floor_artifact["artifact_id"]
    if (not registered or any(type(item) is not str or not item for item in registered)
        or len(set(registered)) != len(registered)
        or type(floor_id) is not str or not floor_id):
        raise ClaimSideBoundRefusal("paper_claim_side_bound_shape_invalid")
    contrasts = claim_verdicts["contrasts"]
    if not isinstance(contrasts, list) or not contrasts:
        raise ClaimSideBoundRefusal("paper_claim_side_bound_shape_invalid")
    rows, seen, joins = [], set(), set()
    for contrast in contrasts:
        subject = contrast["contrast_id"]
        if type(subject) is not str or subject in seen or subject not in registered:
            raise ClaimSideBoundRefusal("paper_claim_side_bound_contrast_mismatch")
        seen.add(subject)
        resolutions = contrast["floor"]["resolutions"]
        if not isinstance(resolutions, list) or not resolutions:
            raise ClaimSideBoundRefusal("paper_claim_side_bound_cell_mismatch")
        sources = []
        for resolution in resolutions:
            cells = resolution["source_cell_ids"]
            if (resolution["status"] not in {"exact", "transported"}
                or not isinstance(cells, list) or not cells
                or any(type(cell) is not str or cell not in floor_cells for cell in cells)
                or len(set(cells)) != len(cells)
                or (resolution["status"] == "exact" and len(cells) != 1)):
                raise ClaimSideBoundRefusal("paper_claim_side_bound_cell_mismatch")
            sources.extend(cells)
        # Repeated cells across resolutions are preserved, never deduplicated.
        if tuple(sources) in joins:
            raise ClaimSideBoundRefusal("paper_claim_side_bound_join_not_injective")
        joins.add(tuple(sources))
        metric, estimator = contrast["metric"], contrast["estimator"]
        unit, ratio = metric["unit"], metric["ratio_estimand"]
        if not ((unit == "J" and ratio is None) or
                (unit == "J/token" and ratio in {"mean_of_request_ratios", "ratio_of_totals"})):
            raise ClaimSideBoundRefusal("paper_claim_side_bound_unit_mismatch")
        if type(estimator["name"]) is not str or not estimator["name"]:
            raise ClaimSideBoundRefusal("paper_claim_side_bound_shape_invalid")
        deterministic = contrast["deterministic_bounds"]
        terms = deterministic["terms"]
        if (not isinstance(terms, list) or not terms
            or any(not isinstance(term, dict) or set(term) != {"name", "bound"}
                   or type(term["name"]) is not str or not term["name"]
                   or not _number(term["bound"], nonnegative=True) for term in terms)
            or len({term["name"] for term in terms}) != len(terms)
            or not _number(deterministic["total"], nonnegative=True)
            or _interval(estimator["metrology_aware_CI95"]) is None
            or _interval(deterministic["decision_interval"]) is None):
            raise ClaimSideBoundRefusal("paper_claim_side_bound_shape_invalid")
        if _ANCHOR not in {term["name"] for term in terms}:
            raise ClaimSideBoundRefusal("paper_claim_side_bound_anchor_missing")
        rows.append({"contrast_id": subject, "source_cell_ids": sources,
                     "floor_artifact_id": floor_id,
                     "deterministic_widening_total": deterministic["total"],
                     "unit": unit, "estimator_id": estimator["name"], "ratio_estimand": ratio,
                     "deterministic_bounds": terms,
                     "metrology_aware_CI95": estimator["metrology_aware_CI95"],
                     "decision_interval": deterministic["decision_interval"]})
    return rows


def produce_claim_side_bound(claim_verdicts_raw: bytes, *, finalized_manifest, floor_artifact) -> bytes:
    """Return deterministic UTF-8 sidecar bytes, or a structured refusal.

    Callers must authenticate and validate the verdicts and both parents before
    issuance. This copy operation alone grants no custody or claim authority.
    """
    try:
        contrasts = _project(_parse(claim_verdicts_raw), finalized_manifest, floor_artifact)
        value = {"schema_version": _SCHEMA,
                 "claim_verdicts_sha256": hashlib.sha256(claim_verdicts_raw).hexdigest(),
                 "contrasts": contrasts}
        return (_encode(value) + "\n").encode("utf-8")
    except ClaimSideBoundRefusal:
        raise
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ClaimSideBoundRefusal("paper_claim_side_bound_shape_invalid") from exc


def validate_claim_side_bound(value: bytes, *, claim_verdicts_raw: bytes,
                              finalized_manifest, floor_artifact) -> tuple[str, ...]:
    """Compare every copied numeral token exactly to the authenticated verdicts."""
    try:
        expected = _parse(produce_claim_side_bound(
            claim_verdicts_raw, finalized_manifest=finalized_manifest, floor_artifact=floor_artifact))
        actual = _parse(value)
        if (not isinstance(actual, dict) or set(actual) != set(expected)
            or actual["schema_version"] != _SCHEMA or not isinstance(actual["contrasts"], list)
            or any(not isinstance(row, dict) or set(row) != _ROW_KEYS for row in actual["contrasts"])):
            return ("paper_claim_side_bound_shape_invalid",)
        if actual["claim_verdicts_sha256"] != expected["claim_verdicts_sha256"]:
            return ("paper_claim_side_bound_reader_digest_mismatch",)
        if [row["contrast_id"] for row in actual["contrasts"]] != [row["contrast_id"] for row in expected["contrasts"]]:
            return ("paper_claim_side_bound_contrast_mismatch",)
        for row, source in zip(actual["contrasts"], expected["contrasts"]):
            if row["source_cell_ids"] != source["source_cell_ids"]:
                return ("paper_claim_side_bound_cell_mismatch",)
            if row["floor_artifact_id"] != source["floor_artifact_id"]:
                return ("paper_claim_side_bound_lineage_mismatch",)
            if any(row[key] != source[key] for key in ("unit", "estimator_id", "ratio_estimand")):
                return ("paper_claim_side_bound_unit_mismatch",)
            if row != source:
                return ("paper_claim_side_bound_copy_mismatch",)
        return ()
    except ClaimSideBoundRefusal as exc:
        return (exc.code,)
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError):
        return ("paper_claim_side_bound_shape_invalid",)


def claim_side_bound_diagnostics(value: bytes) -> tuple[str, ...]:
    """Optional arithmetic diagnostics; never used by validation or issuance."""
    codes = []
    try:
        for row in _parse(value)["contrasts"]:
            bound = float(row["deterministic_widening_total"].token)
            interval, decision = _interval(row["metrology_aware_CI95"]), _interval(row["decision_interval"])
            total = math.fsum(float(term["bound"].token) for term in row["deterministic_bounds"])
            if (interval is None or decision is None
                or not math.isclose(total, bound, rel_tol=1e-12, abs_tol=1e-12)
                or not math.isclose(decision[0], interval[0] - bound, rel_tol=1e-12, abs_tol=1e-12)
                or not math.isclose(decision[1], interval[1] + bound, rel_tol=1e-12, abs_tol=1e-12)):
                codes.append("paper_claim_side_bound_arithmetic_diagnostic")
    except (AttributeError, KeyError, TypeError, ValueError, OverflowError, RecursionError):
        codes.append("paper_claim_side_bound_shape_invalid")
    return tuple(codes)
