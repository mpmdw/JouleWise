"""Authenticated, validator-replayed ingress for paper-supplier evidence.

Callers can name only a closed supply role and a runs root.  The fixed clean
repository selected by :func:`identity_pins._mint_git_anchor` supplies the
Git-tracked role map; paths, digests, validators, inventory, and receipt
locators are all resolved behind this module's public boundary.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import inspect
import json
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Callable, Literal, overload

from joulewise.authentication_io import (
    V2AuthenticationInputError,
    V2AuthenticationReadSession,
    V2_AUTHENTICATION_INPUT_CHANGED,
    V2_AUTHENTICATION_INPUT_DIGEST_MISMATCH,
)
from joulewise.identity_pins import IdentityPinProjectionError, _mint_git_anchor


_SUPPLY_MAP_PATH = "configs/paper_supply/supply_map.json"
_SUPPLY_MAP_SCHEMA = "joulewise.paper_supply_map.v2"
_INVENTORY_SCHEMA = "joulewise.paper_custody_inventory.v1"
_RECEIPT_SCHEMA = "joulewise.paper_custody_receipt.v1"
_FIXTURE_SCHEMA = "joulewise.paper_custody_fixture.v1"
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_SUPPLY_ROLE_RE = re.compile(r"[a-z0-9][a-z0-9_.-]*")


PAPER_CUSTODY_REFUSAL_CODES = frozenset(
    {
        "paper_custody_request_invalid",
        "paper_custody_anchor_unavailable",
        "paper_custody_anchor_mismatch",
        "paper_custody_supply_map_invalid",
        "paper_custody_role_unregistered",
        "paper_custody_path_refused",
        "paper_custody_input_unreadable",
        "paper_custody_digest_mismatch",
        "paper_custody_parse_invalid",
        "paper_custody_issuance_gate_unregistered",
        "paper_custody_not_issuable",
        "paper_custody_binding_mismatch",
        "paper_custody_issuance_prerequisite_missing",
        "paper_custody_receipt_invalid",
        "paper_custody_receipt_binding_mismatch",
        "paper_custody_validator_refused",
        "paper_custody_evidence_ambiguous",
        "paper_custody_input_changed",
    }
)


class InputRole(str, Enum):
    """Closed paper-input role vocabulary."""

    CUSTODY_INVENTORY = "custody_inventory"
    VALIDATOR_RECEIPT = "validator_receipt"
    EXTRACTION_SPEC = "extraction_spec"
    EXTRACTION_REPORT = "extraction_report"
    WHOLE_WINDOW_BASIS = "whole_window_basis"
    G2A_SELECTION = "g2a_selection"
    PROMPT_PIN = "prompt_pin"
    D165_CLOSEOUT = "d165_closeout"
    FINALIZED_MANIFEST = "finalized_manifest"
    FLOOR_ARTIFACT = "floor_artifact"
    FLOOR_ACCEPTANCE = "floor_acceptance"
    AUTHENTICATED_SOURCE = "authenticated_source"
    REPLAY_SIDECAR = "replay_sidecar"
    CAMPAIGN_LOG = "campaign_log"
    STANDALONE_VERDICT = "standalone_verdict"
    PROSPECTIVE_MANIFEST = "prospective_manifest"
    PLAN = "plan"
    CLAIM_VERDICTS = "claim_verdicts"
    CLAIM_SIDE_BOUND = "claim_side_bound"
    TRANSFER_RESULT = "transfer_result"
    REVIEWED_CAPTURE = "reviewed_capture"
    PRE_DATA_RECEIPT = "pre_data_receipt"
    PULSE_BOUND_SOURCE = "pulse_bound_source"
    BUNDLE_INVENTORY = "bundle_inventory"


@dataclass(frozen=True)
class ReportedEnergyParentsRef:
    role: str
    runs_root: Path


@dataclass(frozen=True)
class D165CloseoutRef:
    role: str
    runs_root: Path


@dataclass(frozen=True)
class WholeWindowVerdictRef:
    role: str
    runs_root: Path


@dataclass(frozen=True)
class ClaimEvidenceRef:
    role: str
    runs_root: Path


@dataclass(frozen=True)
class TransferProjectionRef:
    role: str
    runs_root: Path


@dataclass(frozen=True)
class VerifiedDigest:
    role: InputRole
    relative_path: str
    sha256: str
    read_count: int
    strict_parse_succeeded: bool


def _refuse_verified_construction(*_args: object, **_kwargs: object) -> None:
    raise PaperCustodyRefusal("paper_custody_request_invalid")


_CAPABILITY_FIELDS = frozenset(
    {
        "family",
        "inputs",
        "receipt_sha256",
        "validator_source_sha256",
        "anchor_head",
        "supply_map_sha256",
        "mode",
        "issuance_authorized",
        "grants",
        "subjects",
        "evidence",
        "_payload",
    }
)


def _capability_getattribute(value: object, name: str) -> object:
    if name in _CAPABILITY_FIELDS:
        _require_custody_capability(value)
    return object.__getattribute__(value, name)


def _make_custody_capability_mint() -> tuple[Callable[..., object], ...]:
    """Create a guard token; ordinary attributes and closure cells expose it."""

    token = object()

    def require(value: object) -> None:
        try:
            presented = object.__getattribute__(value, "_custody_token")
        except AttributeError as exc:
            raise PaperCustodyRefusal("paper_custody_request_invalid") from exc
        if presented is not token:
            raise PaperCustodyRefusal("paper_custody_request_invalid")

    def construct_evidence(presented: object, **values: object) -> object:
        if presented is not token:
            raise PaperCustodyRefusal("paper_custody_request_invalid")
        evidence = object.__new__(CustodyEvidence)
        for name, child in values.items():
            object.__setattr__(evidence, name, child)
        object.__setattr__(evidence, "_custody_token", token)
        return evidence

    def construct_verified(
        presented: object,
        output_type: type,
        evidence: object,
        payload: object,
    ) -> object:
        if presented is not token:
            raise PaperCustodyRefusal("paper_custody_request_invalid")
        require(evidence)
        spec = next((item for item in _FAMILY_SPECS.values()
                     if item.family == evidence.family), None)
        if spec is None or type(payload) is not _FrozenObject:
            raise PaperCustodyRefusal("paper_custody_request_invalid")
        if evidence.mode == "test_fixture_non_issuing":
            if output_type is not spec.fixture_type or evidence.grants or evidence.subjects:
                raise PaperCustodyRefusal("paper_custody_not_issuable")
        elif evidence.mode == "production":
            if output_type is not spec.issuing_type or not evidence.issuance_authorized:
                raise PaperCustodyRefusal("paper_custody_not_issuable")
            _validate_grants(spec.family, evidence.subjects, evidence.grants)
        else:
            raise PaperCustodyRefusal("paper_custody_request_invalid")
        result = object.__new__(output_type)
        object.__setattr__(result, "evidence", evidence)
        object.__setattr__(result, "_payload", payload)
        object.__setattr__(result, "_custody_token", token)
        return result

    def open_with_token(ref: object) -> object:
        return _open_paper_input_impl(ref, _custody_token=token)

    return construct_evidence, construct_verified, require, open_with_token


@dataclass(frozen=True, init=False, slots=True)
class CustodyEvidence:
    family: str
    inputs: tuple[VerifiedDigest, ...]
    receipt_sha256: str
    validator_source_sha256: str
    anchor_head: str
    supply_map_sha256: str
    mode: Literal["production", "test_fixture_non_issuing"]
    issuance_authorized: bool
    subjects: tuple[str, ...]
    grants: tuple[_RenderGrant, ...]
    _custody_token: object = field(repr=False, compare=False)

    __init__ = _refuse_verified_construction
    __getattribute__ = _capability_getattribute


@dataclass(frozen=True)
class _FrozenObject:
    fields: tuple[tuple[str, object], ...]


@dataclass(frozen=True)
class _FrozenArray:
    items: tuple[object, ...]


@dataclass(frozen=True, init=False, slots=True)
class _CustodyResult:
    evidence: CustodyEvidence
    _payload: _FrozenObject
    _custody_token: object = field(repr=False, compare=False)

    __init__ = _refuse_verified_construction
    __getattribute__ = _capability_getattribute


@dataclass(frozen=True, init=False, slots=True)
class VerifiedReportedEnergyParents(_CustodyResult):
    pass


@dataclass(frozen=True, init=False, slots=True)
class VerifiedD165Closeout(_CustodyResult):
    pass


@dataclass(frozen=True, init=False, slots=True)
class VerifiedWholeWindowVerdict(_CustodyResult):
    pass


@dataclass(frozen=True, init=False, slots=True)
class VerifiedClaimEvidence(_CustodyResult):
    pass


@dataclass(frozen=True, init=False, slots=True)
class VerifiedTransferProjection(_CustodyResult):
    pass


@dataclass(frozen=True, init=False, slots=True)
class FixtureReportedEnergyParents(_CustodyResult):
    pass


@dataclass(frozen=True, init=False, slots=True)
class FixtureD165Closeout(_CustodyResult):
    pass


@dataclass(frozen=True, init=False, slots=True)
class FixtureWholeWindowVerdict(_CustodyResult):
    pass


@dataclass(frozen=True, init=False, slots=True)
class FixtureClaimEvidence(_CustodyResult):
    pass


@dataclass(frozen=True, init=False, slots=True)
class FixtureTransferProjection(_CustodyResult):
    pass


(
    _construct_custody_evidence,
    _construct_verified,
    _require_custody_capability,
    _open_paper_input,
) = _make_custody_capability_mint()


class PaperCustodyRefusal(RuntimeError):
    """Out-of-band refusal whose diagnostics are never rendered as paper."""

    def __init__(
        self,
        code: str,
        *,
        input_role: InputRole | None = None,
        scope: Literal["artifact", "cell", "token"] = "artifact",
        validator_codes: tuple[str, ...] = (),
        records: tuple[VerifiedDigest, ...] = (),
    ) -> None:
        if code not in PAPER_CUSTODY_REFUSAL_CODES:
            code = "paper_custody_request_invalid"
        self.code = code
        self.input_role = input_role if isinstance(input_role, InputRole) else None
        self.scope = scope
        self.validator_codes = tuple(validator_codes)
        self.records = tuple(records)
        self.rendered_output: tuple[()] = ()
        suffix = (
            f":{self.input_role.value}" if self.input_role is not None else ""
        )
        super().__init__(f"{code}{suffix}")


_FamilyRef = (
    ReportedEnergyParentsRef
    | D165CloseoutRef
    | WholeWindowVerdictRef
    | ClaimEvidenceRef
    | TransferProjectionRef
)
_VerifiedFamily = (
    VerifiedReportedEnergyParents
    | VerifiedD165Closeout
    | VerifiedWholeWindowVerdict
    | VerifiedClaimEvidence
    | VerifiedTransferProjection
)


@dataclass(frozen=True)
class _FamilySpec:
    family: str
    roles: tuple[InputRole, ...]
    issuing_type: type
    fixture_type: type

    def roles_for(self, mode: str) -> tuple[InputRole, ...]:
        if mode == "production" and self.family in {"d165_closeout", "claim_evidence"}:
            return (*self.roles, InputRole.FLOOR_ACCEPTANCE)
        return self.roles


_FAMILY_SPECS: dict[type, _FamilySpec] = {
    ReportedEnergyParentsRef: _FamilySpec(
        "reported_energy_parents",
        (
            InputRole.EXTRACTION_SPEC,
            InputRole.EXTRACTION_REPORT,
            InputRole.WHOLE_WINDOW_BASIS,
            InputRole.G2A_SELECTION,
            InputRole.PROMPT_PIN,
        ),
        VerifiedReportedEnergyParents,
        FixtureReportedEnergyParents,
    ),
    D165CloseoutRef: _FamilySpec(
        "d165_closeout",
        (
            InputRole.D165_CLOSEOUT,
            InputRole.FINALIZED_MANIFEST,
            InputRole.FLOOR_ARTIFACT,
            InputRole.REPLAY_SIDECAR,
        ),
        VerifiedD165Closeout,
        FixtureD165Closeout,
    ),
    WholeWindowVerdictRef: _FamilySpec(
        "whole_window_verdict",
        (
            InputRole.CAMPAIGN_LOG,
            InputRole.STANDALONE_VERDICT,
            InputRole.PROSPECTIVE_MANIFEST,
            InputRole.PLAN,
        ),
        VerifiedWholeWindowVerdict,
        FixtureWholeWindowVerdict,
    ),
    ClaimEvidenceRef: _FamilySpec(
        "claim_evidence",
        (
            InputRole.CLAIM_VERDICTS,
            InputRole.CLAIM_SIDE_BOUND,
            InputRole.FINALIZED_MANIFEST,
            InputRole.FLOOR_ARTIFACT,
        ),
        VerifiedClaimEvidence,
        FixtureClaimEvidence,
    ),
    TransferProjectionRef: _FamilySpec(
        "transfer_projection",
        (
            InputRole.TRANSFER_RESULT,
            InputRole.REVIEWED_CAPTURE,
            InputRole.PLAN,
            InputRole.PRE_DATA_RECEIPT,
            InputRole.PULSE_BOUND_SOURCE,
            InputRole.BUNDLE_INVENTORY,
        ),
        VerifiedTransferProjection,
        FixtureTransferProjection,
    ),
}


@dataclass(frozen=True)
class _BoundFile:
    base: Literal["repository", "runs_root"]
    path: Path
    expected_sha256: str
    role: InputRole
    authority: Literal["git_blob", "generated"]


@dataclass(frozen=True)
class _ReceiptRef:
    file: _BoundFile
    validator: str


@dataclass(frozen=True)
class _ResolvedSupply:
    inventory: _BoundFile
    sources: tuple[_BoundFile, ...]
    receipt: _ReceiptRef
    supply_map_sha256: str
    mode: Literal["production", "test_fixture_non_issuing"]
    issuance_gate_id: str | None
    subjects: tuple[str, ...]
    source_census: tuple[_BoundFile, ...]


@dataclass(frozen=True)
class _ReplayState:
    family: str
    repository: Path
    runs_root: Path
    bindings: tuple[_BoundFile, ...]


@dataclass(frozen=True, slots=True)
class _RenderGrant:
    kind: str
    subject_id: str


@dataclass(frozen=True, slots=True)
class _FamilyReplay:
    authentic: bool
    admitted: bool
    grants: tuple[_RenderGrant, ...]
    validator_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _GateContext:
    family: str
    supply_role: str
    mode: str
    issuance_gate_id: str | None
    subjects: tuple[str, ...]
    repository: Path
    runs_root: Path
    head: str
    sources: tuple[_BoundFile, ...]
    source_census: tuple[_BoundFile, ...]
    raws: dict[InputRole, bytes]
    session: V2AuthenticationReadSession


_GRANT_KINDS = {
    "reported_energy_parents": ("cell",),
    "d165_closeout": ("outcome", "dominance_sentence", "subtitle"),
    "whole_window_verdict": ("positive",),  # F6 not installed.
    "claim_evidence": ("outcome", "l2"),
    "transfer_projection": ("diagnostic",),
}
_FLOOR_ACCEPTANCE_SCHEMA = "joulewise.paper_floor_acceptance.v1"


def _validate_grants(family: str, subjects: tuple[str, ...], grants: tuple[_RenderGrant, ...]) -> None:
    if (type(subjects) is not tuple or not subjects or len(set(subjects)) != len(subjects)
        or any(type(subject) is not str or not subject for subject in subjects)
        or type(grants) is not tuple or not grants
        or any(type(grant) is not _RenderGrant or grant.kind not in _GRANT_KINDS[family]
               for grant in grants) or len(set(grants)) != len(grants)):
        raise PaperCustodyRefusal("paper_custody_not_issuable")
    if {grant.subject_id for grant in grants} != set(subjects):
        raise PaperCustodyRefusal("paper_custody_binding_mismatch")
    required = _GRANT_KINDS[family][0]
    if any(_RenderGrant(required, subject) not in grants for subject in subjects):
        raise PaperCustodyRefusal("paper_custody_not_issuable")


def _floor_binder_source_sha256() -> str:
    from joulewise.floor_mint_estimator import bind_v2_floor_artifact_evidence

    return _sha256(inspect.getsource(bind_v2_floor_artifact_evidence).encode("utf-8"))


def _validate_floor_acceptance(ctx: _GateContext) -> None:
    raw = ctx.raws.get(InputRole.FLOOR_ACCEPTANCE)
    if raw is None or not ctx.source_census:
        raise PaperCustodyRefusal("paper_custody_issuance_prerequisite_missing",
                                  input_role=InputRole.FLOOR_ACCEPTANCE)
    value = _json_object(raw)
    expected_sources = sorted(
        ({"path": f"{binding.base}/{binding.path.as_posix()}", "sha256": binding.expected_sha256}
         for binding in ctx.source_census), key=lambda row: row["path"])
    anchor = value.get("anchor_head")
    if (set(value) != {"schema_version", "floor_sha256", "sources", "binder_source_sha256",
                       "anchor_head", "status"}
        or value.get("schema_version") != _FLOOR_ACCEPTANCE_SCHEMA
        or value.get("status") != "PASS"
        or value.get("floor_sha256") != _sha256(ctx.raws[InputRole.FLOOR_ARTIFACT])
        or value.get("sources") != expected_sources
        or len({row["path"] for row in expected_sources}) != len(expected_sources)
        or value.get("binder_source_sha256") != _floor_binder_source_sha256()
        or not isinstance(anchor, str) or re.fullmatch(r"[0-9a-f]{40}", anchor) is None):
        raise PaperCustodyRefusal("paper_custody_issuance_prerequisite_missing",
                                  input_role=InputRole.FLOOR_ACCEPTANCE)
    # Acceptance is produced before the map commit that pins it; require ancestry,
    # not the impossible self-referential equality with that later map commit.
    result = subprocess.run(["git", "-C", str(ctx.repository), "merge-base", "--is-ancestor",
                             anchor, ctx.head], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        raise PaperCustodyRefusal("paper_custody_issuance_prerequisite_missing",
                                  input_role=InputRole.FLOOR_ACCEPTANCE)


def _d165_issuance_gate(ctx: _GateContext) -> _FamilyReplay:
    from joulewise.dominance_closeout import validate_d165_paper_sources, _expected_global_fields

    manifest = next(binding for binding in ctx.sources if binding.role is InputRole.FINALIZED_MANIFEST)
    closeout = _json_object(ctx.raws[InputRole.D165_CLOSEOUT])
    codes = validate_d165_paper_sources(
        closeout=closeout, finalized_manifest_bytes=ctx.raws[InputRole.FINALIZED_MANIFEST],
        finalized_manifest_path=_binding_root(manifest, ctx.repository, ctx.runs_root) / manifest.path,
        custody_root=ctx.runs_root, floor_artifact_bytes=ctx.raws[InputRole.FLOOR_ARTIFACT],
        replay_sidecar_bytes=ctx.raws[InputRole.REPLAY_SIDECAR],
    )
    if codes:
        return _FamilyReplay(False, False, (), tuple(codes))
    _validate_floor_acceptance(ctx)
    if ctx.subjects != (ctx.supply_role,):
        raise PaperCustodyRefusal("paper_custody_binding_mismatch")
    # The owner authenticates/recomputes each ratio and the v5 census. Its global
    # reducer recomputes the branch; source/structural null remains non-issuing.
    expected = _expected_global_fields(closeout["independent_ratios"],
                                       closeout["comparative_common_mode_ratios"], ())
    if closeout.get("refusal_reason") is not None or closeout.get("branch") is None:
        return _FamilyReplay(True, False, (), ())
    if any(closeout.get(key) != child for key, child in expected.items()):
        return _FamilyReplay(False, False, (), ("d165_gate_recomputed_fields_mismatch",))
    if expected["branch"] not in {"A", "B"}:
        return _FamilyReplay(True, False, (), ())
    grants = [_RenderGrant("outcome", ctx.supply_role)]
    if expected["branch"] == "A":
        for kind in ("dominance_sentence", "subtitle"):
            if expected[f"{kind}_licensed"] is True:
                grants.append(_RenderGrant(kind, ctx.supply_role))
    return _FamilyReplay(True, True, tuple(grants), ())


def _claim_issuance_gate(ctx: _GateContext) -> _FamilyReplay:
    """Candidate only: no registry entry until sidecar contract/producer lands."""
    from joulewise.analysis_engine.artifact import validate_claim_verdicts
    from joulewise.analysis_engine.claim_side_bound import validate_claim_side_bound
    from joulewise.analysis_engine.claims import evaluate_claim
    from joulewise.analysis_manifest_v3 import validate_finalized_analysis_manifest_v3

    manifest_binding = next(binding for binding in ctx.sources if binding.role is InputRole.FINALIZED_MANIFEST)
    manifest = _json_object(ctx.raws[InputRole.FINALIZED_MANIFEST])
    artifact = _json_object(ctx.raws[InputRole.CLAIM_VERDICTS])
    floor = _json_object(ctx.raws[InputRole.FLOOR_ARTIFACT])
    sidecar = _json_object(ctx.raws[InputRole.CLAIM_SIDE_BOUND])
    codes = list(validate_finalized_analysis_manifest_v3(
        manifest, manifest_path=_binding_root(manifest_binding, ctx.repository, ctx.runs_root) / manifest_binding.path,
        custody_root=ctx.runs_root))
    codes.extend(validate_claim_verdicts(artifact, frozen_manifest=manifest))
    codes.extend(validate_claim_side_bound(sidecar, claim_verdicts_sha256=_sha256(ctx.raws[InputRole.CLAIM_VERDICTS]),
                                           finalized_manifest=manifest, floor_artifact=floor))
    embedded = artifact.get("inputs", {}).get("floor_artifact", {}).get("embedded_bytes_base64")
    try:
        embedded_floor = base64.b64decode(embedded, validate=True) if isinstance(embedded, str) else None
    except (binascii.Error, ValueError):
        embedded_floor = None
    if embedded_floor != ctx.raws[InputRole.FLOOR_ARTIFACT]:
        codes.append("claim_floor_anchor_mismatch")
    if codes:
        return _FamilyReplay(False, False, (), tuple(codes))
    _validate_floor_acceptance(ctx)
    contrasts = {row["contrast_id"]: row for row in artifact["contrasts"]}
    bounds = {row["contrast_id"]: row for row in sidecar["contrasts"]}
    if not ctx.subjects or any(subject not in contrasts or subject not in bounds for subject in ctx.subjects):
        raise PaperCustodyRefusal("paper_custody_binding_mismatch")
    grants = []
    for subject in ctx.subjects:
        contrast = contrasts[subject]
        deterministic = contrast["deterministic_bounds"]
        if (bounds[subject]["claim_side_bound_j"] != deterministic["total"]
            or bounds[subject]["decision_interval"] != deterministic["decision_interval"]
            or bounds[subject]["metrology_aware_CI95"] != contrast["estimator"]["metrology_aware_CI95"]):
            raise PaperCustodyRefusal("paper_custody_binding_mismatch")
        if artifact["evidence_class"] != "current" or contrast["sampling"]["confirmatory_status"] != "confirmatory":
            continue
        floor_metadata_keys = {"floor_limit_class", "floor_source", "point_floor_diagnostics", "single_count_discipline"}
        floor_values = contrast["floor"]
        evaluated = evaluate_claim(
            estimate=contrast["estimator"]["estimate"],
            metrology_aware_ci95=contrast["estimator"]["metrology_aware_CI95"],
            decision_interval=deterministic["decision_interval"], floor_gate_j=floor_values["active_floor_j"],
            adjusted_rejected=contrast["multiplicity"]["rejected"] is True,
            base_reason_codes=contrast["claim_evaluation"]["reason_codes"], equivalence=contrast.get("equivalence"),
            claim_role=contrast["claim_role"], confirmatory_status=contrast["sampling"]["confirmatory_status"],
            evidence_class=artifact["evidence_class"],
            floor_metadata=({key: floor_values[key] for key in floor_metadata_keys}
                            if floor_metadata_keys <= set(floor_values) else None),
            hypothesized_direction=contrast.get("hypothesized_direction"),
        )
        grants.append(_RenderGrant("outcome", subject))
        if evaluated["claim_ready_for_l2_l3"] is True and evaluated["claim_level_ceiling"] in {"L2", "L3"}:
            grants.append(_RenderGrant("l2", subject))
    admitted = all(_RenderGrant("outcome", subject) in grants for subject in ctx.subjects)
    return _FamilyReplay(True, admitted, tuple(grants), ())


# Register only completed gate implementations. Maps still contain no production
# roles. Energy joins, claim sidecar producer, F6, and transfer remain absent.
_ISSUANCE_GATES: dict[tuple[str, str], Callable[[_GateContext], _FamilyReplay]] = {
    ("d165_closeout", "d165-closeout.v1"): _d165_issuance_gate,
}


def _run_issuance_gate(ctx: _GateContext) -> _FamilyReplay:
    if ctx.mode != "production":
        raise PaperCustodyRefusal("paper_custody_not_issuable")
    gate = _ISSUANCE_GATES.get((ctx.family, ctx.issuance_gate_id))
    if gate is None:
        raise PaperCustodyRefusal("paper_custody_issuance_gate_unregistered")
    replay = gate(ctx)
    if (type(replay) is not _FamilyReplay or type(replay.authentic) is not bool
        or type(replay.admitted) is not bool or type(replay.validator_codes) is not tuple
        or any(type(code) is not str for code in replay.validator_codes)
        or (replay.admitted and not replay.authentic)):
        raise PaperCustodyRefusal("paper_custody_not_issuable")
    if replay.admitted:
        _validate_grants(ctx.family, ctx.subjects, replay.grants)
    elif replay.grants:
        raise PaperCustodyRefusal("paper_custody_not_issuable")
    return replay


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _freeze_json(value: object) -> object:
    if isinstance(value, dict):
        return _FrozenObject(
            tuple((key, _freeze_json(child)) for key, child in sorted(value.items()))
        )
    if isinstance(value, list):
        return _FrozenArray(tuple(_freeze_json(child) for child in value))
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError("paper custody can freeze only strict JSON values")


def _json_object(raw: bytes) -> dict[str, object]:
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("paper custody input must be one JSON object")
    return value


def _validator_source_census(
    family: str,
) -> tuple[tuple[str, Callable[..., object] | ModuleType], ...]:
    """Return the closed dispatcher-plus-owner source census for one family."""

    common: tuple[tuple[str, Callable[..., object]], ...] = tuple(
        (f"paper_custody.{member.__name__}", member) for member in (
            _replay_family, _validate_fixture_documents, _validate_production_documents,
            _run_issuance_gate, _validate_grants, _validate_floor_acceptance,
            _floor_binder_source_sha256, _d165_issuance_gate, _claim_issuance_gate,
            _make_custody_capability_mint, _FamilySpec, _load_supply_entry,
            _read_once, _open_paper_input_impl,
        )
    )
    if family == "reported_energy_parents":
        from joulewise.floor_extraction import (
            validate_d117_mint_consumption_report,
            validate_extraction_spec,
        )

        owners = (
            ("floor_extraction.validate_extraction_spec", validate_extraction_spec),
            (
                "floor_extraction.validate_d117_mint_consumption_report",
                validate_d117_mint_consumption_report,
            ),
        )
    elif family == "d165_closeout":
        from joulewise.analysis_engine.inputs import authenticate_floor_artifact_bytes
        from joulewise.analysis_manifest_v3 import (
            validate_finalized_analysis_manifest_v3,
        )
        from joulewise.dominance_closeout import (
            validate_d165_closeout,
            validate_d165_paper_sources,
            validate_d165_replay_sidecar,
            _expected_global_fields,
        )

        owners = (
            (
                "dominance_closeout.validate_d165_paper_sources",
                validate_d165_paper_sources,
            ),
            (
                "analysis_manifest_v3.validate_finalized_analysis_manifest_v3",
                validate_finalized_analysis_manifest_v3,
            ),
            (
                "analysis_engine.inputs.authenticate_floor_artifact_bytes",
                authenticate_floor_artifact_bytes,
            ),
            (
                "dominance_closeout.validate_d165_replay_sidecar",
                validate_d165_replay_sidecar,
            ),
            ("dominance_closeout.validate_d165_closeout", validate_d165_closeout),
            ("dominance_closeout._expected_global_fields", _expected_global_fields),
        )
    elif family == "whole_window_verdict":
        from joulewise.whole_window import validate_whole_window_verdict_row

        owners = (
            (
                "whole_window.validate_whole_window_verdict_row",
                validate_whole_window_verdict_row,
            ),
        )
    elif family == "claim_evidence":
        from joulewise.analysis_engine.artifact import validate_claim_verdicts, _validate_cross_field_claim_semantics
        from joulewise.analysis_engine.claims import evaluate_claim
        from joulewise.analysis_engine.claim_side_bound import validate_claim_side_bound, _interval
        from joulewise.analysis_manifest_v3 import validate_finalized_analysis_manifest_v3

        owners = (
            ("analysis_engine.claims.evaluate_claim", evaluate_claim),
            ("analysis_engine.artifact._validate_cross_field_claim_semantics", _validate_cross_field_claim_semantics),
            ("analysis_engine.claim_side_bound.validate_claim_side_bound", validate_claim_side_bound),
            ("analysis_engine.claim_side_bound._interval", _interval),
            ("analysis_manifest_v3.validate_finalized_analysis_manifest_v3", validate_finalized_analysis_manifest_v3),
            ("analysis_engine.artifact.validate_claim_verdicts", validate_claim_verdicts),
        )
    elif family == "transfer_projection":
        owners = ()
    else:
        raise ValueError("unknown paper custody family")
    from joulewise.floor_mint_estimator import bind_v2_floor_artifact_evidence
    members = (*common, *owners, ("floor_mint_estimator.bind_v2_floor_artifact_evidence", bind_v2_floor_artifact_evidence))
    # Pin each owner's complete module too: helper implementations and policy
    # constants must invalidate a receipt just as the named entry point does.
    modules = {module.__name__: module for _, member in members
               if (module := inspect.getmodule(member)) is not None}
    return (*members, *((f"module:{name}", module) for name, module in sorted(modules.items())))


def _validator_source_sha256(family: str) -> str:
    digest = hashlib.sha256()
    digest.update(family.encode("utf-8") + b"\0")
    from joulewise.analysis_engine import claim_side_bound
    policy = {"grant_kinds": _GRANT_KINDS, "registered_gates": sorted(_ISSUANCE_GATES),
              "floor_acceptance_schema": _FLOOR_ACCEPTANCE_SCHEMA,
              "side_bound_schema": claim_side_bound._SCHEMA,
              "side_bound_row_keys": sorted(claim_side_bound._ROW_KEYS)}
    digest.update(_canonical_json_bytes(policy) + b"\0")
    for member_id, member in _validator_source_census(family):
        digest.update(member_id.encode("utf-8") + b"\0")
        digest.update(inspect.getsource(member).encode("utf-8") + b"\0")
    return digest.hexdigest()


def _relative_path(binding: _BoundFile) -> str:
    if type(binding) is not _BoundFile:
        raise PaperCustodyRefusal("paper_custody_request_invalid")
    if not isinstance(binding.path, Path):
        raise PaperCustodyRefusal(
            "paper_custody_request_invalid", input_role=binding.role
        )
    text = binding.path.as_posix()
    pure = PurePosixPath(text)
    if (
        pure.is_absolute()
        or not pure.parts
        or any(part in {"", ".", ".."} for part in pure.parts)
        or "\\" in text
    ):
        raise PaperCustodyRefusal(
            "paper_custody_path_refused", input_role=binding.role
        )
    if (
        not isinstance(binding.role, InputRole)
        or not isinstance(binding.expected_sha256, str)
        or _SHA256_RE.fullmatch(binding.expected_sha256) is None
        or binding.base not in {"repository", "runs_root"}
        or binding.authority not in {"git_blob", "generated"}
        or (binding.authority == "git_blob" and binding.base != "repository")
    ):
        raise PaperCustodyRefusal(
            "paper_custody_supply_map_invalid", input_role=binding.role
        )
    return text


def _binding_root(
    binding: _BoundFile, repository: Path, runs_root: Path
) -> Path:
    return repository if binding.base == "repository" else runs_root


def _record_tuple(
    session: V2AuthenticationReadSession,
    repository: Path,
    runs_root: Path,
    bindings: tuple[_BoundFile, ...],
) -> tuple[VerifiedDigest, ...]:
    records = session.records
    result: list[VerifiedDigest] = []
    for binding in bindings:
        relative = _relative_path(binding)
        root = _binding_root(binding, repository, runs_root)
        identity = str((root / relative).resolve(strict=False))
        record = records.get(identity)
        if record is None:
            continue
        result.append(
            VerifiedDigest(
                role=binding.role,
                relative_path=relative,
                sha256=record.sha256,
                read_count=record.read_count,
                strict_parse_succeeded=record.strict_parse_succeeded,
            )
        )
    return tuple(result)


def _raise(
    refusal: PaperCustodyRefusal,
    *,
    session: V2AuthenticationReadSession | None = None,
    repository: Path | None = None,
    runs_root: Path | None = None,
    bindings: tuple[_BoundFile, ...] = (),
) -> None:
    if session is not None and repository is not None and runs_root is not None:
        refusal.records = _record_tuple(session, repository, runs_root, bindings)
    raise refusal


def _git_blob(
    repository: Path, head: str, relative: str, role: InputRole | None = None
) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repository), "show", f"{head}:{relative}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PaperCustodyRefusal(
            "paper_custody_anchor_unavailable", input_role=role
        ) from exc
    return completed.stdout


def _map_binding(
    value: object,
    *,
    role: InputRole,
    include_authority: bool,
) -> _BoundFile:
    expected_keys = {"base", "expected_sha256", "path"}
    if include_authority:
        expected_keys.add("authority")
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise PaperCustodyRefusal(
            "paper_custody_supply_map_invalid", input_role=role
        )
    base = value.get("base")
    path = value.get("path")
    digest = value.get("expected_sha256")
    authority = value.get("authority", "generated")
    if (
        base not in {"repository", "runs_root"}
        or not isinstance(path, str)
        or not isinstance(digest, str)
        or not isinstance(authority, str)
    ):
        raise PaperCustodyRefusal(
            "paper_custody_supply_map_invalid", input_role=role
        )
    binding = _BoundFile(
        base=base,
        path=Path(path),
        expected_sha256=digest,
        role=role,
        authority=authority,
    )
    _relative_path(binding)
    return binding


def _load_supply_entry(
    session: V2AuthenticationReadSession,
    repository: Path,
    head: str,
    supply_role: str,
    spec: _FamilySpec,
) -> _ResolvedSupply:
    raw = _git_blob(repository, head, _SUPPLY_MAP_PATH)
    try:
        raw = session.ingest(
            f"git:{head}:{_SUPPLY_MAP_PATH}",
            raw,
            grammar="json",
            label="paper supply map",
        )
        value = _json_object(raw)
    except (UnicodeError, json.JSONDecodeError, V2AuthenticationInputError, ValueError) as exc:
        raise PaperCustodyRefusal("paper_custody_supply_map_invalid") from exc
    if set(value) != {"roles", "pending_roles", "schema_version"} or value.get(
        "schema_version"
    ) != _SUPPLY_MAP_SCHEMA:
        raise PaperCustodyRefusal("paper_custody_supply_map_invalid")
    pending_roles = value.get("pending_roles")
    if not isinstance(pending_roles, dict) or any(
        not isinstance(key, str)
        or _SUPPLY_ROLE_RE.fullmatch(key) is None
        or not isinstance(pending, dict)
        or set(pending) != {"status", "family", "input_role", "base", "authority", "path"}
        or pending.get("status") != "pending_desk_day"
        for key, pending in pending_roles.items()
    ):
        raise PaperCustodyRefusal("paper_custody_supply_map_invalid")
    roles = value.get("roles")
    if not isinstance(roles, dict) or any(
        not isinstance(key, str) or _SUPPLY_ROLE_RE.fullmatch(key) is None
        for key in roles
    ):
        raise PaperCustodyRefusal("paper_custody_supply_map_invalid")
    entry = roles.get(supply_role)
    if entry is None:
        raise PaperCustodyRefusal("paper_custody_role_unregistered")
    if not isinstance(entry, dict) or set(entry) != {
        "family",
        "inputs",
        "inventory",
        "receipt",
        "validator",
        "mode",
        "issuance_gate_id",
        "subjects",
        "source_census",
    }:
        raise PaperCustodyRefusal("paper_custody_supply_map_invalid")
    mode = entry.get("mode")
    gate_id = entry.get("issuance_gate_id")
    subjects = entry.get("subjects")
    if (mode not in {"production", "test_fixture_non_issuing"}
        or (gate_id is not None and (not isinstance(gate_id, str) or not gate_id))
        or not isinstance(subjects, list)
        or any(not isinstance(item, str) or not item for item in subjects)
        or len(set(subjects)) != len(subjects)
        or (mode == "test_fixture_non_issuing" and (gate_id is not None or subjects))):
        raise PaperCustodyRefusal("paper_custody_supply_map_invalid")
    validator = entry.get("validator")
    if (
        entry.get("family") != spec.family
        or validator != f"joulewise.paper_custody.{spec.family}.v1"
    ):
        raise PaperCustodyRefusal("paper_custody_supply_map_invalid")
    inventory = _map_binding(
        entry.get("inventory"),
        role=InputRole.CUSTODY_INVENTORY,
        include_authority=False,
    )
    receipt_file = _map_binding(
        entry.get("receipt"),
        role=InputRole.VALIDATOR_RECEIPT,
        include_authority=False,
    )
    rows = entry.get("inputs")
    if not isinstance(rows, list) or len(rows) != len(spec.roles_for(mode)):
        raise PaperCustodyRefusal("paper_custody_supply_map_invalid")
    sources: list[_BoundFile] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("role"), str):
            raise PaperCustodyRefusal("paper_custody_supply_map_invalid")
        try:
            role = InputRole(row["role"])
        except (TypeError, ValueError) as exc:
            raise PaperCustodyRefusal("paper_custody_supply_map_invalid") from exc
        without_role = {key: child for key, child in row.items() if key != "role"}
        sources.append(
            _map_binding(without_role, role=role, include_authority=True)
        )
    if tuple(binding.role for binding in sources) != spec.roles_for(mode):
        raise PaperCustodyRefusal("paper_custody_supply_map_invalid")
    census = entry.get("source_census")
    if not isinstance(census, list):
        raise PaperCustodyRefusal("paper_custody_supply_map_invalid")
    source_census = tuple(_map_binding(row, role=InputRole.AUTHENTICATED_SOURCE,
                                      include_authority=True) for row in census)
    bindings = (inventory, *sources, *source_census, receipt_file)
    identities = [
        (binding.base, _relative_path(binding)) for binding in bindings
    ]
    if len(set(identities)) != len(identities):
        raise PaperCustodyRefusal("paper_custody_evidence_ambiguous")
    return _ResolvedSupply(
        inventory=inventory,
        sources=tuple(sources),
        receipt=_ReceiptRef(file=receipt_file, validator=validator),
        supply_map_sha256=_sha256(raw),
        mode=mode,
        issuance_gate_id=gate_id,
        subjects=tuple(subjects),
        source_census=source_census,
    )


def _read_once(
    session: V2AuthenticationReadSession,
    repository: Path,
    runs_root: Path,
    binding: _BoundFile,
    *,
    head: str,
    bindings: tuple[_BoundFile, ...],
) -> bytes:
    relative = _relative_path(binding)
    root = _binding_root(binding, repository, runs_root)
    grammar: Literal["json", "jsonl", "raw"] = (
        "raw" if binding.role is InputRole.AUTHENTICATED_SOURCE
        else "jsonl" if relative.endswith(".jsonl") else "json"
    )
    try:
        if binding.authority == "git_blob":
            blob = _git_blob(repository, head, relative, binding.role)
            if _sha256(blob) != binding.expected_sha256:
                raise PaperCustodyRefusal("paper_custody_digest_mismatch", input_role=binding.role)
            session.ingest(f"git:{head}:{relative}", blob, grammar=grammar,
                           label=f"paper custody {binding.role.value} Git blob")
        return session.read_nofollow_pinned(
            root, relative, expected_sha256=binding.expected_sha256,
            grammar=grammar, label=f"paper custody {binding.role.value}",
        )
    except V2AuthenticationInputError as exc:
        if exc.reason == V2_AUTHENTICATION_INPUT_CHANGED:
            refusal = PaperCustodyRefusal("paper_custody_input_changed", input_role=binding.role)
        elif exc.reason == V2_AUTHENTICATION_INPUT_DIGEST_MISMATCH:
            refusal = PaperCustodyRefusal("paper_custody_digest_mismatch", input_role=binding.role)
        else:
            refusal = PaperCustodyRefusal("paper_custody_parse_invalid", input_role=binding.role)
        _raise(refusal, session=session, repository=repository, runs_root=runs_root, bindings=bindings)
    except OSError as exc:
        if isinstance(exc, FileNotFoundError):
            refusal = PaperCustodyRefusal("paper_custody_input_unreadable", input_role=binding.role)
        else:
            refusal = PaperCustodyRefusal("paper_custody_path_refused", input_role=binding.role)
        _raise(refusal, session=session, repository=repository, runs_root=runs_root, bindings=bindings)
    raise AssertionError("unreachable paper custody read")


def _validate_inventory(
    raw: bytes,
    *,
    family: str,
    expected: tuple[_BoundFile, ...],
    expected_mode: str,
) -> tuple[
    Literal["production", "test_fixture_non_issuing"],
    dict[tuple[InputRole, str], dict[str, str]],
]:
    try:
        value = _json_object(raw)
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise PaperCustodyRefusal(
            "paper_custody_parse_invalid", input_role=InputRole.CUSTODY_INVENTORY
        ) from exc
    if set(value) != {
        "family",
        "files",
        "inventory_id",
        "mode",
        "schema_version",
    } or value.get("schema_version") != _INVENTORY_SCHEMA or value.get(
        "family"
    ) != family or not isinstance(value.get("inventory_id"), str):
        raise PaperCustodyRefusal(
            "paper_custody_receipt_invalid", input_role=InputRole.CUSTODY_INVENTORY
        )
    mode = value.get("mode")
    if mode != expected_mode:
        raise PaperCustodyRefusal(
            "paper_custody_receipt_invalid", input_role=InputRole.CUSTODY_INVENTORY
        )
    rows = value.get("files")
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise PaperCustodyRefusal(
            "paper_custody_evidence_ambiguous", input_role=InputRole.CUSTODY_INVENTORY
        )
    indexed: dict[tuple[InputRole, str], dict[str, str]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "authority",
            "path",
            "role",
            "sha256",
        }:
            raise PaperCustodyRefusal(
                "paper_custody_receipt_invalid",
                input_role=InputRole.CUSTODY_INVENTORY,
            )
        try:
            role = InputRole(row["role"])
        except (TypeError, ValueError) as exc:
            raise PaperCustodyRefusal(
                "paper_custody_receipt_invalid",
                input_role=InputRole.CUSTODY_INVENTORY,
            ) from exc
        if (
            (role, row.get("path")) in indexed
            or row.get("authority") not in {"git_blob", "generated"}
            or not isinstance(row.get("path"), str)
            or not isinstance(row.get("sha256"), str)
            or _SHA256_RE.fullmatch(row["sha256"]) is None
        ):
            raise PaperCustodyRefusal(
                "paper_custody_evidence_ambiguous",
                input_role=InputRole.CUSTODY_INVENTORY,
            )
        indexed[(role, row["path"])] = row
    expected_by_role = {(binding.role, _relative_path(binding)): binding for binding in expected}
    if len(expected_by_role) != len(expected) or set(indexed) != set(expected_by_role):
        raise PaperCustodyRefusal(
            "paper_custody_evidence_ambiguous", input_role=InputRole.CUSTODY_INVENTORY
        )
    for key, binding in expected_by_role.items():
        role = binding.role
        row = indexed[key]
        if (
            row["path"] != _relative_path(binding)
            or row["sha256"] != binding.expected_sha256
            or row["authority"] != binding.authority
        ):
            raise PaperCustodyRefusal(
                "paper_custody_anchor_mismatch", input_role=role
            )
    return mode, indexed


def _validate_receipt(
    raw: bytes,
    ref: _ReceiptRef,
    *,
    family: str,
    sources: tuple[_BoundFile, ...],
) -> dict[str, object]:
    if (
        type(ref) is not _ReceiptRef
        or ref.file.role is not InputRole.VALIDATOR_RECEIPT
        or ref.validator != f"joulewise.paper_custody.{family}.v1"
    ):
        raise PaperCustodyRefusal(
            "paper_custody_supply_map_invalid",
            input_role=InputRole.VALIDATOR_RECEIPT,
        )
    try:
        value = _json_object(raw)
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise PaperCustodyRefusal(
            "paper_custody_receipt_invalid", input_role=InputRole.VALIDATOR_RECEIPT
        ) from exc
    if _canonical_json_bytes(value) != raw or set(value) != {
        "family",
        "inputs",
        "replay_codes",
        "schema_version",
        "status",
        "validator",
        "validator_source_sha256",
    }:
        raise PaperCustodyRefusal(
            "paper_custody_receipt_invalid", input_role=InputRole.VALIDATOR_RECEIPT
        )
    expected_inputs = sorted(
        (
            {
                "path": _relative_path(binding),
                "role": binding.role.value,
                "sha256": binding.expected_sha256,
            }
            for binding in sources
        ),
        key=lambda row: (row["role"], row["path"]),
    )
    expected_source = _validator_source_sha256(family)
    if (
        value.get("schema_version") != _RECEIPT_SCHEMA
        or value.get("family") != family
        or value.get("status") != "PASS"
        or value.get("validator") != ref.validator
        or value.get("validator_source_sha256") != expected_source
        or value.get("inputs") != expected_inputs
        or not isinstance(value.get("replay_codes"), list)
        or any(not isinstance(code, str) for code in value["replay_codes"])
    ):
        raise PaperCustodyRefusal(
            "paper_custody_receipt_binding_mismatch",
            input_role=InputRole.VALIDATOR_RECEIPT,
        )
    return value


def _validate_fixture_documents(
    family: str,
    sources: tuple[_BoundFile, ...],
    raws: dict[InputRole, bytes],
) -> tuple[str, ...]:
    errors: list[str] = []
    for binding in sources:
        try:
            value = _json_object(raws[binding.role])
        except (UnicodeError, json.JSONDecodeError, ValueError):
            errors.append(f"{binding.role.value}_invalid")
            continue
        if value != {
            "family": family,
            "marker": "synthetic-no-measurement-value",
            "role": binding.role.value,
            "schema_version": _FIXTURE_SCHEMA,
        }:
            errors.append(f"{binding.role.value}_invalid")
    return tuple(errors)


def _validate_production_documents(ctx: _GateContext) -> _FamilyReplay:
    return _run_issuance_gate(ctx)


def _replay_family(ctx: _GateContext) -> _FamilyReplay:
    if ctx.mode == "test_fixture_non_issuing":
        codes = _validate_fixture_documents(ctx.family, ctx.sources, ctx.raws)
        return _FamilyReplay(not codes, False, (), codes)
    try:
        return _validate_production_documents(ctx)
    except PaperCustodyRefusal:
        raise
    except Exception as exc:
        return _FamilyReplay(False, False, (), (type(exc).__name__,))


def _after_validator_replay(state: _ReplayState) -> None:
    """Deliberately empty seam used to prove replay-to-reopen detection."""

    if not isinstance(state, _ReplayState):
        raise TypeError("invalid paper custody replay state")


@overload
def open_paper_input(ref: ReportedEnergyParentsRef) -> VerifiedReportedEnergyParents | FixtureReportedEnergyParents: ...


@overload
def open_paper_input(ref: D165CloseoutRef) -> VerifiedD165Closeout | FixtureD165Closeout: ...


@overload
def open_paper_input(ref: WholeWindowVerdictRef) -> VerifiedWholeWindowVerdict | FixtureWholeWindowVerdict: ...


@overload
def open_paper_input(ref: ClaimEvidenceRef) -> VerifiedClaimEvidence | FixtureClaimEvidence: ...


@overload
def open_paper_input(ref: TransferProjectionRef) -> VerifiedTransferProjection | FixtureTransferProjection: ...


def open_paper_input(ref: _FamilyRef) -> _CustodyResult:
    """Open one closed paper-input role from a caller-named runs root."""

    try:
        return _open_paper_input(ref)
    except PaperCustodyRefusal:
        raise
    except Exception as exc:
        raise PaperCustodyRefusal("paper_custody_request_invalid") from exc


def _open_paper_input_impl(
    ref: _FamilyRef,
    *,
    _custody_token: object,
) -> _CustodyResult:
    spec = _FAMILY_SPECS.get(type(ref))
    if spec is None:
        raise PaperCustodyRefusal("paper_custody_request_invalid")
    if (
        not isinstance(ref.role, str)
        or _SUPPLY_ROLE_RE.fullmatch(ref.role) is None
        or not isinstance(ref.runs_root, Path)
    ):
        raise PaperCustodyRefusal("paper_custody_request_invalid")
    try:
        runs_root = ref.runs_root.resolve(strict=True)
    except OSError as exc:
        raise PaperCustodyRefusal("paper_custody_input_unreadable") from exc
    if not runs_root.is_dir():
        raise PaperCustodyRefusal("paper_custody_path_refused")
    try:
        repository, head = _mint_git_anchor(require_origin_main=True)
    except IdentityPinProjectionError as exc:
        raise PaperCustodyRefusal("paper_custody_anchor_unavailable") from exc

    with V2AuthenticationReadSession() as session:
        supply = _load_supply_entry(
            session, repository, head, ref.role, spec
        )
        sources = supply.sources
        receipt_binding = supply.receipt.file
        consumed = (*sources, *supply.source_census)
        bindings = (supply.inventory, *consumed, receipt_binding)
        identities = [str((_binding_root(item, repository, runs_root) / item.path).resolve())
                      for item in bindings]
        if len(set(identities)) != len(identities):
            raise PaperCustodyRefusal("paper_custody_evidence_ambiguous")
        inventory_raw = _read_once(session, repository, runs_root, supply.inventory,
                                   head=head, bindings=bindings)
        mode, _inventory = _validate_inventory(
            inventory_raw, family=spec.family, expected=(*consumed, receipt_binding),
            expected_mode=supply.mode,
        )
        first = {supply.inventory: inventory_raw}
        for binding in (*consumed, receipt_binding):
            first[binding] = _read_once(session, repository, runs_root, binding,
                                        head=head, bindings=bindings)
        raws = {binding.role: first[binding] for binding in sources}
        ctx = _GateContext(spec.family, ref.role, mode, supply.issuance_gate_id,
                           supply.subjects, repository, runs_root, head, sources,
                           supply.source_census, raws, session)
        replay = _replay_family(ctx)
        if type(replay) is not _FamilyReplay:
            raise PaperCustodyRefusal("paper_custody_not_issuable")
        if not replay.authentic or replay.validator_codes:
            _raise(PaperCustodyRefusal("paper_custody_validator_refused",
                                      validator_codes=replay.validator_codes),
                   session=session, repository=repository, runs_root=runs_root, bindings=bindings)
        # Owners may read transitively only within the prospectively mapped census.
        allowed = {str((_binding_root(item, repository, runs_root) / item.path).resolve())
                   for item in bindings}
        allowed_git = {f"git:{head}:{_SUPPLY_MAP_PATH}",
                       *(f"git:{head}:{item.path.as_posix()}" for item in bindings if item.authority == "git_blob")}
        if any(identity not in allowed and identity not in allowed_git
               for identity in session.records):
            raise PaperCustodyRefusal("paper_custody_binding_mismatch")
        receipt_value = _validate_receipt(first[receipt_binding], supply.receipt,
                                          family=spec.family, sources=consumed)
        if receipt_value["replay_codes"] != list(replay.validator_codes):
            raise PaperCustodyRefusal("paper_custody_receipt_binding_mismatch",
                                      input_role=InputRole.VALIDATOR_RECEIPT)
        _after_validator_replay(_ReplayState(spec.family, repository, runs_root, bindings))
        for binding in bindings:
            try:
                reopened = _read_once(session, repository, runs_root, binding,
                                      head=head, bindings=bindings)
            except PaperCustodyRefusal as exc:
                if exc.code in {"paper_custody_digest_mismatch", "paper_custody_parse_invalid",
                                "paper_custody_path_refused", "paper_custody_input_unreadable"}:
                    _raise(PaperCustodyRefusal("paper_custody_input_changed", input_role=binding.role),
                           session=session, repository=repository, runs_root=runs_root, bindings=bindings)
                raise
            if reopened != first[binding]:
                _raise(PaperCustodyRefusal("paper_custody_input_changed", input_role=binding.role),
                       session=session, repository=repository, runs_root=runs_root, bindings=bindings)
        if mode == "production":
            if not replay.admitted:
                raise PaperCustodyRefusal("paper_custody_not_issuable")
            _validate_grants(spec.family, supply.subjects, replay.grants)
        elif replay.admitted or replay.grants:
            raise PaperCustodyRefusal("paper_custody_not_issuable")
        evidence = _construct_custody_evidence(
            _custody_token, family=spec.family,
            inputs=_record_tuple(session, repository, runs_root, bindings),
            receipt_sha256=_sha256(first[receipt_binding]),
            validator_source_sha256=_validator_source_sha256(spec.family),
            anchor_head=head, supply_map_sha256=supply.supply_map_sha256,
            mode=mode, issuance_authorized=mode == "production" and replay.admitted,
            subjects=supply.subjects, grants=replay.grants,
        )
        payload = _FrozenObject(tuple((binding.role.value, _freeze_json(_json_object(raws[binding.role])))
                                      for binding in sources))
        output_type = spec.issuing_type if mode == "production" else spec.fixture_type
        return _construct_verified(_custody_token, output_type, evidence, payload)


__all__ = [
    "ClaimEvidenceRef",
    "CustodyEvidence",
    "D165CloseoutRef",
    "InputRole",
    "PAPER_CUSTODY_REFUSAL_CODES",
    "PaperCustodyRefusal",
    "ReportedEnergyParentsRef",
    "TransferProjectionRef",
    "VerifiedClaimEvidence",
    "FixtureClaimEvidence",
    "VerifiedD165Closeout",
    "FixtureD165Closeout",
    "VerifiedDigest",
    "VerifiedReportedEnergyParents",
    "FixtureReportedEnergyParents",
    "VerifiedTransferProjection",
    "FixtureTransferProjection",
    "VerifiedWholeWindowVerdict",
    "FixtureWholeWindowVerdict",
    "WholeWindowVerdictRef",
    "open_paper_input",
]
