"""Issuing-family paper renderers. Every public body has a runtime boundary."""
from __future__ import annotations

from functools import wraps
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN, localcontext

from joulewise.paper_custody import (
    PaperCustodyRefusal, VerifiedClaimEvidence, VerifiedD165Closeout,
    VerifiedReportedEnergyParents, VerifiedTransferProjection, VerifiedWholeWindowVerdict,
    _FAMILY_SPECS, _FrozenArray, _FrozenObject, _RenderGrant,
    _require_custody_capability, _validate_grants,
)


def _issued_renderer(expected_type, required_grant):
    """Refuse before body/payload access; type hints alone confer no authority."""
    def decorate(body):
        @wraps(body)
        def guarded(value):
            if type(value) is not expected_type:
                raise PaperCustodyRefusal("paper_custody_not_issuable")
            _require_custody_capability(value)
            evidence = value.evidence
            _require_custody_capability(evidence)
            spec = next(item for item in _FAMILY_SPECS.values() if item.issuing_type is expected_type)
            if evidence.family != spec.family or evidence.mode != "production":
                raise PaperCustodyRefusal("paper_custody_not_issuable")
            _validate_grants(spec.family, evidence.subjects, evidence.grants)
            if any(_RenderGrant(required_grant, subject) not in evidence.grants for subject in evidence.subjects):
                raise PaperCustodyRefusal("paper_custody_not_issuable")
            return body(value)
        guarded._issuing_boundary = (expected_type, required_grant)
        return guarded
    return decorate


_MISSING = object()


def _field(value: _FrozenObject, name: str, default=_MISSING):
    if type(value) is not _FrozenObject:
        return default
    return next((child for key, child in value.fields if key == name), default)


_PRECISION = (
    "Display precision: 3 decimals in J; 6 decimals in J/token; estimates "
    "round-half-even; interval endpoints rounded outward (lower down, upper up)."
)


def _thaw(value):
    if type(value) is _FrozenObject:
        return {key: _thaw(child) for key, child in value.fields}
    if type(value) is _FrozenArray:
        return [_thaw(child) for child in value.items]
    return value


def _number(value, unit="J", rounding=ROUND_HALF_EVEN):
    if type(value) not in (int, float):
        raise ValueError("missing or invalid numeric projection")
    number = Decimal(str(value))
    if not number.is_finite():
        raise ValueError("nonfinite numeric projection")
    places = 6 if unit == "J/token" else 3
    with localcontext() as context:
        context.prec = max(28, number.adjusted() + places + 2)
        rounded = number.quantize(Decimal(1).scaleb(-places), rounding=rounding)
    # A small negative estimate can round to zero; never print negative zero.
    return format(abs(rounded) if rounded == 0 else rounded, f".{places}f")


def _interval(value, unit):
    if value is None:
        return "unavailable"
    if not isinstance(value, dict) or set(value) != {"lower", "upper"}:
        raise ValueError("missing or invalid interval projection")
    lower = _number(value["lower"], unit, ROUND_FLOOR)
    upper = _number(value["upper"], unit, ROUND_CEILING)
    if value["lower"] > value["upper"]:
        raise ValueError("reversed interval projection")
    return f"[{lower}, {upper}] {unit}"


def _selected_rows(rows, subjects, key):
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("invalid row projection")
    selected = [row for row in rows if row.get(key) in subjects]
    if len(selected) != len(subjects) or {row[key] for row in selected} != set(subjects):
        raise ValueError("selected subject projection is missing or duplicated")
    return selected


def _count(value):
    if type(value) is not int or value < 0:
        raise ValueError("invalid count projection")
    return str(value)


@_issued_renderer(VerifiedReportedEnergyParents, "cell")
def render_reported_energy(value: VerifiedReportedEnergyParents) -> str:
    from joulewise.paper_reported_energy import PaperReportedEnergyRefusal
    projection = value.reported_energy_projection
    if projection is None:
        raise PaperReportedEnergyRefusal("paper_reported_energy_projection_absent")
    cells = _field(projection, "cells")
    if type(cells) is not _FrozenArray:
        raise PaperReportedEnergyRefusal("paper_reported_energy_projection_mismatch")
    try:
        lines = []
        for cell in _selected_rows(_thaw(cells), value.evidence.subjects, "cell_id"):
            token = cell["per_token"]
            if token["status"] == "computed":
                per_token = _number(token["j_per_token"], "J/token")
            elif token["status"] == "refused" and isinstance(token["reason"], str):
                per_token = f'unavailable ({token["reason"]})'
            else:
                raise ValueError("invalid per-token projection")
            interval = _interval({"lower": cell["lower_j"], "upper": cell["upper_j"]}, "J")
            lines.append(
                f'{cell["cell_id"]}: estimate = {_number(cell["mean_j"])} J; '
                f'95% reported-mean interval = {interval}; J/token = {per_token}; '
                f'n = {_count(cell["n_bundles"])} bundles '
                f'({_count(cell["independence_units"])} independence units); '
                "decision interval = unavailable (reported mean)."
            )
        return "\n".join((*lines, _PRECISION))
    except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
        raise PaperReportedEnergyRefusal("paper_reported_energy_projection_mismatch") from exc


@_issued_renderer(VerifiedD165Closeout, "outcome")
def render_d165(value: VerifiedD165Closeout) -> str:
    from joulewise.dominance_closeout import D165_OR01_REASON_SENTENCES
    closeout = _thaw(_field(value._payload, "d165_closeout"))
    try:
        branch = closeout["branch"]
        if branch == "A":
            return "D-165 branch A: every required attribution-dominance ratio passes."
        labels = []
        for key, common in (("independent_ratios", False), ("comparative_common_mode_ratios", True)):
            for row in closeout.get(key, []):
                if row.get("passes") is False or row.get("status") == "refused":
                    component = "comparative common-mode" if common else row["component"]
                    labels.append(f'{row["cell_id"]} {component}')
        affected = ", ".join(labels) or "none recorded"
        if branch == "B":
            return f"D-165 branch B: required ratios below the twofold threshold: {affected}."
        if branch is None:
            reason = D165_OR01_REASON_SENTENCES[closeout["refusal_reason"]]
            return f"at close-out: {reason}; affected: {affected}"
        raise ValueError("unknown D-165 branch")
    except (KeyError, TypeError, ValueError) as exc:
        raise PaperCustodyRefusal("paper_custody_not_issuable") from exc


@_issued_renderer(VerifiedWholeWindowVerdict, "positive")
def render_whole_window(value: VerifiedWholeWindowVerdict) -> str:
    return "admitted"


@_issued_renderer(VerifiedClaimEvidence, "outcome")
def render_claim(value: VerifiedClaimEvidence) -> str:
    contrasts = _field(_field(value._payload, "claim_verdicts"), "contrasts")
    try:
        lines = []
        for row in _selected_rows(_thaw(contrasts), value.evidence.subjects, "contrast_id"):
            estimator, evaluation = row["estimator"], row["claim_evaluation"]
            unit = row["metric"]["unit"]
            if unit not in {"J", "J/token"}:
                raise ValueError("unsupported claim unit")
            estimate = ("unavailable" if estimator["estimate"] is None
                        else f'{_number(estimator["estimate"], unit)} {unit}')
            # A J-valued contrast has no token estimand. Never divide by a
            # configured length or borrow another contrast's denominator.
            per_token = (_number(estimator["estimate"], unit)
                         if unit == "J/token" and estimator["estimate"] is not None
                         else "unavailable (no issued token contrast)" if unit == "J"
                         else "unavailable (not estimable)")
            reasons = ", ".join(evaluation["reason_codes"]) or "none"
            lines.append(
                f'{row["contrast_id"]}: outcome = {evaluation["outcome"]}; '
                f'estimate = {estimate}; 95% metrology interval = '
                f'{_interval(estimator["metrology_aware_CI95"], unit)}; '
                f'decision interval = {_interval(row["deterministic_bounds"]["decision_interval"], unit)}; '
                f'J/token = {per_token}; n = {_count(estimator["n"])} blocks; '
                f'direction = {evaluation["direction"] or "unavailable"}; '
                f'claim ceiling = {evaluation["claim_level_ceiling"]}; '
                f'claim ready = {str(evaluation["claim_ready_for_l2_l3"]).lower()}; reasons = {reasons}.'
            )
        return "\n".join((*lines, _PRECISION))
    except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
        raise PaperCustodyRefusal("paper_custody_not_issuable") from exc


@_issued_renderer(VerifiedTransferProjection, "diagnostic")
def render_transfer(value: VerifiedTransferProjection) -> str:
    return "diagnostic projection"


_RENDERERS = {
    "render_reported_energy": (VerifiedReportedEnergyParents, "cell"),
    "render_d165": (VerifiedD165Closeout, "outcome"),
    "render_whole_window": (VerifiedWholeWindowVerdict, "positive"),
    "render_claim": (VerifiedClaimEvidence, "outcome"),
    "render_transfer": (VerifiedTransferProjection, "diagnostic"),
}
__all__ = list(_RENDERERS)
