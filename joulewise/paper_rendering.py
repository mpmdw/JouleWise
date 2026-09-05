"""Issuing-family paper renderers. Every public body has a runtime boundary."""
from __future__ import annotations

from functools import wraps

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


def _field(value: _FrozenObject, name: str):
    return next(child for key, child in value.fields if key == name)


@_issued_renderer(VerifiedReportedEnergyParents, "cell")
def render_reported_energy(value: VerifiedReportedEnergyParents) -> str:
    cells = _field(_field(value._payload, "extraction_report"), "reported_energy_cells")
    assert type(cells) is _FrozenArray
    selected = {subject for subject in value.evidence.subjects}
    return "\n".join(f'{_field(cell, "cell_id")}: {_field(cell, "mean_j")}'
                     for cell in cells.items if _field(cell, "cell_id") in selected)


@_issued_renderer(VerifiedD165Closeout, "outcome")
def render_d165(value: VerifiedD165Closeout) -> str:
    return _field(_field(value._payload, "d165_closeout"), "branch")


@_issued_renderer(VerifiedWholeWindowVerdict, "positive")
def render_whole_window(value: VerifiedWholeWindowVerdict) -> str:
    return "admitted"


@_issued_renderer(VerifiedClaimEvidence, "outcome")
def render_claim(value: VerifiedClaimEvidence) -> str:
    contrasts = _field(_field(value._payload, "claim_verdicts"), "contrasts")
    assert type(contrasts) is _FrozenArray
    selected = set(value.evidence.subjects)
    return "\n".join(f'{_field(row, "contrast_id")}: {_field(_field(row, "claim_evaluation"), "outcome")}'
                     for row in contrasts.items if _field(row, "contrast_id") in selected)


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
