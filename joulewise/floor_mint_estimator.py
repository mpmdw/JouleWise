"""Spec-authoritative comparative-estimator support for the v2 floor mint.

The committed extraction spec is the only estimator authority.  Registration
data authorizes an internal arithmetic path; it is never projected into an
extraction report, floor artifact, or artifact provenance record.
"""

from __future__ import annotations

import inspect
import math
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence

from joulewise import detection_floor, floor_extraction
from joulewise.authentication_io import active_v2_authentication_session
from joulewise.whole_window import (
    AuthenticatedConsumptionSession,
    whole_window_refusal_reasons,
)


__all__ = [
    "selection_from_authenticated_spec",
    "recompute_comparative_estimate",
    "bind_v2_floor_artifact_evidence",
]


_DEFAULT_PATH = "default"
_COMMON_MODE_PATH = "common_mode"
_ABBA_POSITIONS = ("A1", "B1", "B2", "A2")
_BRACKET_SCREEN = Decimal("0.010818")
_ALLOWANCE_RULE = "max(observed_drift_s,0.010818)"
_COMPONENT_COMPOSITION = "componentwise_max_never_sum.v1"
_ACCEPTANCE_SELECTION = "issued_d116_artifact_only"
_PENDING_STATUS = "candidate_pending_floor_commonmode_01"
_CANONICAL_COMMON_MODE_PARAMETER_SHA256 = (
    "dd61d38811ddadb2aecb8df4a533b715c8ca74bb031896d09688c9b76b69ed38"
)
_BLOCK_INPUT_BUILDER_SIGNATURE = (
    "(members: 'Sequence[MemberReport]', *, runs_root: 'Path', metric: 'str', "
    "shared_edge_bound_s: 'float') -> '_CommonModeBlockInputs'"
)
_FLOOR_FROM_BLOCK_INPUTS_SIGNATURE = (
    "(block_deltas_j: 'Sequence[float]', "
    "block_inputs: 'Sequence[_CommonModeBlockInputs]', *, "
    "calibration_bracket: 'object', shared_edge_bound_s: 'float') "
    "-> 'FloorEstimate'"
)


class _MintEstimatorError(ValueError):
    """A spec-selected estimator cannot be authenticated or recomputed."""


@dataclass(frozen=True)
class _EvidenceMember:
    bundle_id: str
    position: str


@dataclass(frozen=True)
class _ComparativeRecomputation:
    estimator_path: str
    comparative_blocks: tuple[Mapping[str, Any], ...]
    estimate: Any
    exact_widths_j: tuple[float, ...]
    comparative_record: Mapping[str, Any]


def _assert_common_mode_contract() -> None:
    if (
        detection_floor.COMMON_MODE_PARAMETER_SHA256
        != _CANONICAL_COMMON_MODE_PARAMETER_SHA256
    ):
        raise _MintEstimatorError(
            "common-mode parameter sha256 differs from the mint-reviewed pin"
        )
    registration = detection_floor.two_shared_edge_common_mode_registration()
    if registration.get("parameter_sha256") != (
        _CANONICAL_COMMON_MODE_PARAMETER_SHA256
    ):
        raise _MintEstimatorError(
            "canonical common-mode registration does not carry the pinned parameter sha256"
        )
    signatures = (
        (
            floor_extraction._common_mode_block_inputs_from_evidence,
            _BLOCK_INPUT_BUILDER_SIGNATURE,
        ),
        (
            floor_extraction._common_mode_floor_from_block_inputs,
            _FLOOR_FROM_BLOCK_INPUTS_SIGNATURE,
        ),
    )
    for helper, expected in signatures:
        if str(inspect.signature(helper)) != expected:
            raise _MintEstimatorError(
                f"common-mode helper signature changed: {helper.__name__}"
            )


def _decimal(value: object, label: str) -> Decimal:
    if isinstance(value, bool):
        raise _MintEstimatorError(f"{label} must be a finite decimal value")
    try:
        converted = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise _MintEstimatorError(
            f"{label} must be a finite decimal value"
        ) from exc
    if not converted.is_finite():
        raise _MintEstimatorError(f"{label} must be a finite decimal value")
    return converted


def _validate_calibration_basis(
    basis: object,
    *,
    calibration_acceptance: Mapping[str, Any] | None,
    calibration_acceptance_sha256: str | None,
    calibration_allowance_projection: Mapping[str, Any] | None,
    declared_calibration_scope: str | None,
) -> None:
    if not isinstance(basis, Mapping):
        raise _MintEstimatorError(
            "authenticated spec calibration_basis must be a complete object"
        )
    if (
        not isinstance(calibration_acceptance, Mapping)
        or not isinstance(calibration_acceptance_sha256, str)
        or not isinstance(calibration_allowance_projection, Mapping)
        or not isinstance(declared_calibration_scope, str)
    ):
        raise _MintEstimatorError(
            "authenticated producer acceptance context is required for calibration_basis"
        )
    issued = basis.get("issued_acceptance")
    if not isinstance(issued, Mapping):
        raise _MintEstimatorError(
            "authenticated spec calibration_basis issued_acceptance is malformed"
        )
    expected_issued = {
        "acceptance_id": calibration_acceptance.get("acceptance_id"),
        "artifact_sha256": calibration_acceptance_sha256,
        "derivation_sha256": calibration_acceptance.get("derivation_sha256"),
        "schema_version": calibration_acceptance.get("schema_version"),
    }
    if any(
        not isinstance(value, str) or not value
        for value in expected_issued.values()
    ) or any(issued.get(field) != value for field, value in expected_issued.items()):
        raise _MintEstimatorError(
            "authenticated spec calibration_basis differs from the producer acceptance"
        )
    if (
        basis.get("calibration_scope") != declared_calibration_scope
        or basis.get("acceptance_selection") != _ACCEPTANCE_SELECTION
        or basis.get("allowance_rule") != _ALLOWANCE_RULE
        or isinstance(basis.get("allowance_embedding_count"), bool)
        or basis.get("allowance_embedding_count") != 1
        or basis.get("component_composition") != _COMPONENT_COMPOSITION
    ):
        raise _MintEstimatorError(
            "authenticated spec calibration_basis policy literals are not canonical"
        )
    try:
        observed = _decimal(
            calibration_allowance_projection.get("observed_drift_s"),
            "authenticated observed drift",
        )
        screen = _decimal(
            calibration_allowance_projection.get("bracket_screen_s"),
            "authenticated bracket screen",
        )
        applied = _decimal(
            calibration_allowance_projection.get("applied_allowance_s"),
            "authenticated applied allowance",
        )
    except AttributeError as exc:
        raise _MintEstimatorError(
            "authenticated producer allowance projection is malformed"
        ) from exc
    if (
        screen != _BRACKET_SCREEN
        or applied != max(observed, _BRACKET_SCREEN)
        or calibration_allowance_projection.get("allowance_rule")
        != _ALLOWANCE_RULE
        or isinstance(
            calibration_allowance_projection.get("allowance_embedding_count"),
            bool,
        )
        or calibration_allowance_projection.get("allowance_embedding_count")
        != 1
    ):
        raise _MintEstimatorError(
            "authenticated producer allowance does not implement max(observed_drift_s,0.010818) exactly once"
        )


def selection_from_authenticated_spec(
    spec_cell: Mapping[str, Any],
    *,
    calibration_acceptance: Mapping[str, Any] | None = None,
    calibration_acceptance_sha256: str | None = None,
    calibration_allowance_projection: Mapping[str, Any] | None = None,
    declared_calibration_scope: str | None = None,
) -> str:
    """Select from the authenticated target spec cell, never report data."""

    if not isinstance(spec_cell, Mapping):
        raise _MintEstimatorError("authenticated comparative spec cell is malformed")
    estimator_present = "estimator" in spec_cell
    estimator = spec_cell.get("estimator")
    registration_present = "estimator_registration" in spec_cell
    registration = spec_cell.get("estimator_registration")
    basis_present = "calibration_basis" in spec_cell

    if basis_present:
        _validate_calibration_basis(
            spec_cell.get("calibration_basis"),
            calibration_acceptance=calibration_acceptance,
            calibration_acceptance_sha256=calibration_acceptance_sha256,
            calibration_allowance_projection=calibration_allowance_projection,
            declared_calibration_scope=declared_calibration_scope,
        )

    if not estimator_present or estimator == detection_floor.METHOD_ID:
        if registration_present:
            raise _MintEstimatorError(
                "common-mode registration cannot authorize the default estimator path"
            )
        return _DEFAULT_PATH

    if estimator != detection_floor.COMMON_MODE_ESTIMATOR_ID:
        raise _MintEstimatorError(
            f"unsupported authenticated spec estimator: {estimator!r}"
        )
    if (
        isinstance(registration, Mapping)
        and registration.get("estimator_id")
        == detection_floor.COMMON_MODE_ESTIMATOR_ID
        and registration.get("status") == _PENDING_STATUS
    ):
        raise _MintEstimatorError(
            "pending common-mode estimator registration is not mint-authorized"
        )
    _assert_common_mode_contract()
    if not detection_floor.validate_common_mode_estimator_registration(
        registration
    ):
        raise _MintEstimatorError(
            "authenticated spec common-mode registration is not canonical"
        )
    if not basis_present:
        raise _MintEstimatorError(
            "authenticated spec common-mode calibration_basis is required"
        )
    return _COMMON_MODE_PATH


def _full_spec_member_ids(spec: Mapping[str, Any]) -> tuple[str, ...]:
    result: list[str] = []
    cells = spec.get("cells")
    if not isinstance(cells, list) or not cells:
        raise _MintEstimatorError("authenticated extraction spec has no cells")
    for cell in cells:
        if not isinstance(cell, Mapping):
            raise _MintEstimatorError("authenticated extraction spec cell is malformed")
        members = cell.get("members")
        if isinstance(members, list):
            for member in members:
                bundle_id = member.get("bundle_id") if isinstance(member, Mapping) else None
                if not isinstance(bundle_id, str) or not bundle_id:
                    raise _MintEstimatorError(
                        "authenticated extraction spec member is malformed"
                    )
                result.append(bundle_id)
        blocks = cell.get("blocks")
        if isinstance(blocks, list):
            for block in blocks:
                block_members = block.get("members") if isinstance(block, Mapping) else None
                if not isinstance(block_members, Mapping) or set(block_members) != set(
                    _ABBA_POSITIONS
                ):
                    raise _MintEstimatorError(
                        "authenticated extraction spec ABBA block is malformed"
                    )
                for position in _ABBA_POSITIONS:
                    bundle_id = block_members.get(position)
                    if not isinstance(bundle_id, str) or not bundle_id:
                        raise _MintEstimatorError(
                            "authenticated extraction spec ABBA member is malformed"
                        )
                    result.append(bundle_id)
    if not result:
        raise _MintEstimatorError("authenticated extraction spec has no members")
    return tuple(result)


def _comparative_layout(component: Any, core: Any) -> tuple[
    tuple[Mapping[str, Any], ...], tuple[float, ...]
]:
    blocks = component.spec_cell.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise _MintEstimatorError("authenticated comparative spec has no ABBA blocks")
    flattened: list[str] = []
    for block in blocks:
        members = block.get("members") if isinstance(block, Mapping) else None
        if not isinstance(members, Mapping) or set(members) != set(_ABBA_POSITIONS):
            raise _MintEstimatorError("authenticated comparative ABBA block is malformed")
        flattened.extend(members[position] for position in _ABBA_POSITIONS)
    authenticated_order = [member.bundle_id for member in component.members]
    if flattened != authenticated_order or len(set(flattened)) != len(flattened):
        raise _MintEstimatorError(
            "authenticated comparative spec blocks do not flatten to the authenticated member sequence"
        )
    try:
        comparative_blocks, deltas = core._comparative_blocks(component)
    except (KeyError, TypeError, ValueError) as exc:
        raise _MintEstimatorError(
            "authenticated comparative ABBA values are not derivable"
        ) from exc
    return tuple(comparative_blocks), tuple(deltas)


def _authenticated_common_mode_session(
    component: Any,
    *,
    runs_root: Path,
    calibration_ledger_snapshot: Any,
    calibration_bracket_binding: Mapping[str, Any],
) -> AuthenticatedConsumptionSession:
    if active_v2_authentication_session() is None:
        raise _MintEstimatorError(
            "common-mode mint recomputation requires an active v2 authentication read session"
        )
    member_ids = _full_spec_member_ids(component.spec)
    referenced = set(member_ids)
    session = AuthenticatedConsumptionSession(
        Path(runs_root),
        referenced,
        evaluation_basis_sha256=(
            component.whole_window_evaluation_basis_sha256
        ),
        consumption_semantics_id=component.consumption_semantics_id,
        calibration_ledger_snapshot=calibration_ledger_snapshot,
        calibration_bracket_binding=calibration_bracket_binding,
    )
    reasons = whole_window_refusal_reasons(
        Path(runs_root),
        referenced,
        evaluation_basis_sha256=(
            component.whole_window_evaluation_basis_sha256
        ),
        consumption_session=session,
        consumption_semantics_id=component.consumption_semantics_id,
    )
    if reasons or not session.ready:
        reason = reasons[0] if reasons else (
            session.refusal_reasons[0]
            if session.refusal_reasons
            else "common_mode_authenticated_bracket_required"
        )
        raise _MintEstimatorError(
            f"authenticated common-mode consumption refused: {reason}"
        )
    if not isinstance(session.calibration_bracket, Mapping):
        raise _MintEstimatorError(
            "authenticated common-mode consumption did not rederive a full calibration bracket"
        )
    if any(session.summary_for(bundle_id) is None for bundle_id in referenced):
        raise _MintEstimatorError(
            "authenticated common-mode consumption omitted extraction-spec members"
        )
    return session


def recompute_comparative_estimate(
    *,
    core: Any,
    comparative_component: Any,
    runs_root: Path,
    calibration_acceptance: Mapping[str, Any],
    calibration_acceptance_sha256: str,
    calibration_allowance_projection: Mapping[str, Any],
    declared_calibration_scope: str,
    calibration_ledger_snapshot: Any,
    calibration_bracket_binding: Mapping[str, Any],
) -> _ComparativeRecomputation:
    """Recompute one comparative cell from authenticated members and bytes."""

    path = selection_from_authenticated_spec(
        comparative_component.spec_cell,
        calibration_acceptance=calibration_acceptance,
        calibration_acceptance_sha256=calibration_acceptance_sha256,
        calibration_allowance_projection=calibration_allowance_projection,
        declared_calibration_scope=declared_calibration_scope,
    )
    comparative_blocks, deltas = _comparative_layout(comparative_component, core)
    if path == _DEFAULT_PATH:
        estimate = core.comparative_false_effect_floor(
            deltas,
            admissible_half_widths_j=comparative_component.widths_j,
        )
    else:
        _assert_common_mode_contract()
        session = _authenticated_common_mode_session(
            comparative_component,
            runs_root=Path(runs_root),
            calibration_ledger_snapshot=calibration_ledger_snapshot,
            calibration_bracket_binding=calibration_bracket_binding,
        )
        bracket = session.calibration_bracket
        assert isinstance(bracket, Mapping)
        shared_edge_bound_s = (
            detection_floor.registered_common_mode_operative_bound(bracket)
        )
        session_bound = session.operative_fiducial_bound_s
        if (
            isinstance(session_bound, bool)
            or not isinstance(session_bound, int | float)
            or not math.isfinite(float(session_bound))
            or not math.isclose(
                float(session_bound),
                shared_edge_bound_s,
                rel_tol=0.0,
                abs_tol=1e-12,
            )
        ):
            raise _MintEstimatorError(
                "authenticated common-mode once-widened bound is inconsistent"
            )
        member_by_id = {
            member.bundle_id: member for member in comparative_component.members
        }
        block_inputs = []
        for spec_block in comparative_component.spec_cell["blocks"]:
            ids = spec_block["members"]
            block_members = [
                _EvidenceMember(
                    bundle_id=member_by_id[ids[position]].bundle_id,
                    position=position,
                )
                for position in _ABBA_POSITIONS
            ]
            block_inputs.append(
                floor_extraction._common_mode_block_inputs_from_evidence(
                    block_members,
                    runs_root=Path(runs_root),
                    metric=comparative_component.spec_cell["metric"],
                    shared_edge_bound_s=shared_edge_bound_s,
                )
            )
        estimate = floor_extraction._common_mode_floor_from_block_inputs(
            deltas,
            block_inputs,
            calibration_bracket=bracket,
            shared_edge_bound_s=shared_edge_bound_s,
        )
    widths = tuple(estimate.admissible_half_widths_j)
    comparative_record = core.build_comparative_record(
        estimate,
        comparative_blocks,
        consumption_semantics_id=comparative_component.consumption_semantics_id,
        whole_window_drift_allowance=(
            comparative_component.whole_window_drift_allowance
        ),
    )
    return _ComparativeRecomputation(
        estimator_path=path,
        comparative_blocks=comparative_blocks,
        estimate=estimate,
        exact_widths_j=widths,
        comparative_record=comparative_record,
    )


def _stored_comparative_widths(artifact: Mapping[str, Any]) -> Sequence[object]:
    cells = artifact.get("cells")
    if not isinstance(cells, list) or len(cells) != 1:
        raise _MintEstimatorError(
            "v2 estimator-aware binder requires one isolated cell artifact"
        )
    comparative = cells[0].get("comparative") if isinstance(cells[0], Mapping) else None
    widths = (
        comparative.get("admissible_half_widths_j")
        if isinstance(comparative, Mapping)
        else None
    )
    if not isinstance(widths, list):
        raise _MintEstimatorError(
            "v2 comparative artifact has no admissible widths"
        )
    return widths


def _binding_result_from_provenance(
    artifact: Mapping[str, Any],
) -> Mapping[str, tuple[str, ...]]:
    cells = artifact.get("cells")
    if not isinstance(cells, list) or len(cells) != 1 or not isinstance(
        cells[0], Mapping
    ):
        return {}
    provenance = cells[0].get("provenance")
    if not isinstance(provenance, Mapping):
        return {}
    result: dict[str, tuple[str, ...]] = {}
    for component_name in ("absolute", "comparative"):
        component = provenance.get(component_name)
        hashes = component.get("bundle_sha256s") if isinstance(component, Mapping) else None
        if isinstance(hashes, list) and all(isinstance(value, str) for value in hashes):
            result[component_name] = tuple(hashes)
    return result


def bind_v2_floor_artifact_evidence(
    *,
    core: Any,
    artifact: Mapping[str, Any],
    floor_path: Path,
    evidence_roots: Mapping[str, Path],
    strict_validator: Any,
    comparative_component: Any,
    runs_root: Path,
    calibration_acceptance: Mapping[str, Any],
    calibration_acceptance_sha256: str,
    calibration_allowance_projection: Mapping[str, Any],
    declared_calibration_scope: str,
    calibration_ledger_snapshot: Any,
    calibration_bracket_binding: Mapping[str, Any],
) -> Mapping[str, tuple[str, ...]]:
    """Preserve the pinned binder and add exact spec-selected v2 widths."""

    path = selection_from_authenticated_spec(
        comparative_component.spec_cell,
        calibration_acceptance=calibration_acceptance,
        calibration_acceptance_sha256=calibration_acceptance_sha256,
        calibration_allowance_projection=calibration_allowance_projection,
        declared_calibration_scope=declared_calibration_scope,
    )
    legacy_result: Mapping[str, tuple[str, ...]] | None = None
    try:
        legacy_result = core.bind_floor_artifact_evidence(
            artifact,
            floor_path,
            evidence_roots,
            strict_validator=strict_validator,
            calibration_ledger_snapshot=calibration_ledger_snapshot,
            calibration_bracket_binding=calibration_bracket_binding,
        )
    except core.MintError as exc:
        if path != _COMMON_MODE_PATH or not str(exc).endswith(
            "artifact widths differ from authenticated source bytes"
        ):
            raise
        # For one isolated common-mode cell the pinned binder reaches this
        # exact message only after plan, campaign, bundle, config, stack,
        # semantics, and member-order checks have all passed.  Its sole
        # remaining default-only assumption is replaced below.

    if path == _DEFAULT_PATH:
        assert legacy_result is not None
        return legacy_result

    recomputation = recompute_comparative_estimate(
        core=core,
        comparative_component=comparative_component,
        runs_root=Path(runs_root),
        calibration_acceptance=calibration_acceptance,
        calibration_acceptance_sha256=calibration_acceptance_sha256,
        calibration_allowance_projection=calibration_allowance_projection,
        declared_calibration_scope=declared_calibration_scope,
        calibration_ledger_snapshot=calibration_ledger_snapshot,
        calibration_bracket_binding=calibration_bracket_binding,
    )
    stored = _stored_comparative_widths(artifact)
    if len(stored) != len(recomputation.exact_widths_j):
        raise _MintEstimatorError(
            "artifact common-mode widths differ from authenticated source bytes"
        )
    try:
        exact = all(
            _decimal(observed, "artifact common-mode width")
            == Decimal(str(expected))
            and _decimal(observed, "artifact common-mode width") >= 0
            for observed, expected in zip(
                stored, recomputation.exact_widths_j, strict=True
            )
        )
    except (InvalidOperation, ValueError) as exc:
        raise _MintEstimatorError(
            "artifact common-mode widths differ from authenticated source bytes"
        ) from exc
    if not exact:
        raise _MintEstimatorError(
            "artifact common-mode widths differ from authenticated source bytes"
        )
    return legacy_result or _binding_result_from_provenance(artifact)
