"""Authenticated, replayed ingress for values consumed by paper suppliers.

The module deliberately exposes one read operation.  Locator objects carry
caller pins, but those pins never authorize bytes: Git blobs authorize
governed files and a Git-authorized custody inventory authorizes generated
files.  A validator receipt is checked only after a fresh validator replay.
"""

from __future__ import annotations

import dataclasses
import base64
import binascii
import hashlib
import inspect
import json
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Literal, overload

from joulewise.authentication_io import (
    AuthenticationInputRecord,
    V2AuthenticationInputError,
    V2AuthenticationReadSession,
    V2_AUTHENTICATION_INPUT_CHANGED,
    V2_AUTHENTICATION_INPUT_DIGEST_MISMATCH,
)


_INVENTORY_SCHEMA = "joulewise.paper_custody_inventory.v1"
_RECEIPT_SCHEMA = "joulewise.paper_custody_receipt.v1"
_FIXTURE_SCHEMA = "joulewise.paper_custody_fixture.v1"
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


PAPER_CUSTODY_REFUSAL_CODES = frozenset(
    {
        "paper_custody_request_invalid",
        "paper_custody_anchor_unavailable",
        "paper_custody_anchor_mismatch",
        "paper_custody_path_refused",
        "paper_custody_input_unreadable",
        "paper_custody_digest_mismatch",
        "paper_custody_parse_invalid",
        "paper_custody_receipt_unissued",
        "paper_custody_blocked_pending_receipt",
        "paper_custody_receipt_invalid",
        "paper_custody_receipt_binding_mismatch",
        "paper_custody_validator_refused",
        "paper_custody_derivation_mismatch",
        "paper_custody_evidence_ambiguous",
        "paper_custody_identity_not_v5",
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
class BoundFile:
    """A locator and caller pin; never an authorization by itself."""

    path: Path
    expected_sha256: str
    role: InputRole


@dataclass(frozen=True)
class ReceiptRef:
    """Closed locator for the corroborating validator receipt."""

    file: BoundFile
    schema: str
    validator: str
    validator_source_sha256: str


@dataclass(frozen=True)
class ReportedEnergyParentsRef:
    root: Path
    inventory: BoundFile
    extraction_spec: BoundFile
    extraction_report: BoundFile
    whole_window_basis: BoundFile
    g2a_selection: BoundFile
    prompt_pin: BoundFile
    receipt: ReceiptRef


@dataclass(frozen=True)
class D165CloseoutRef:
    root: Path
    inventory: BoundFile
    closeout: BoundFile
    finalized_manifest: BoundFile
    floor_artifact: BoundFile
    replay_sidecar: BoundFile
    receipt: ReceiptRef


@dataclass(frozen=True)
class WholeWindowVerdictRef:
    root: Path
    inventory: BoundFile
    campaign_log: BoundFile
    standalone_verdict: BoundFile
    prospective_manifest: BoundFile
    plan: BoundFile
    receipt: ReceiptRef


@dataclass(frozen=True)
class ClaimEvidenceRef:
    root: Path
    inventory: BoundFile
    claim_verdicts: BoundFile
    claim_side_bound: BoundFile
    finalized_manifest: BoundFile
    floor_artifact: BoundFile
    receipt: ReceiptRef


@dataclass(frozen=True)
class TransferProjectionRef:
    root: Path
    inventory: BoundFile
    result_projection: BoundFile
    reviewed_capture: BoundFile
    plan: BoundFile
    pre_data_receipt: BoundFile
    pulse_bound_source: BoundFile
    bundle_inventory: BoundFile
    receipt: ReceiptRef


@dataclass(frozen=True)
class VerifiedDigest:
    role: InputRole
    relative_path: str
    sha256: str
    read_count: int
    strict_parse_succeeded: bool


@dataclass(frozen=True)
class CustodyEvidence:
    family: str
    inputs: tuple[VerifiedDigest, ...]
    receipt_sha256: str
    validator_source_sha256: str
    mode: Literal["production", "test_fixture_non_issuing"]
    issuance_authorized: bool


@dataclass(frozen=True)
class _FrozenObject:
    fields: tuple[tuple[str, object], ...]


@dataclass(frozen=True)
class _FrozenArray:
    items: tuple[object, ...]


@dataclass(frozen=True, init=False)
class VerifiedReportedEnergyParents:
    evidence: CustodyEvidence
    _payload: _FrozenObject


@dataclass(frozen=True, init=False)
class VerifiedD165Closeout:
    evidence: CustodyEvidence
    _payload: _FrozenObject


@dataclass(frozen=True, init=False)
class VerifiedWholeWindowVerdict:
    evidence: CustodyEvidence
    _payload: _FrozenObject


@dataclass(frozen=True, init=False)
class VerifiedClaimEvidence:
    evidence: CustodyEvidence
    _payload: _FrozenObject


@dataclass(frozen=True, init=False)
class VerifiedTransferProjection:
    evidence: CustodyEvidence
    _payload: _FrozenObject


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
    fields: tuple[tuple[str, InputRole], ...]
    output_type: type


_FAMILY_SPECS: dict[type, _FamilySpec] = {
    ReportedEnergyParentsRef: _FamilySpec(
        "reported_energy_parents",
        (
            ("extraction_spec", InputRole.EXTRACTION_SPEC),
            ("extraction_report", InputRole.EXTRACTION_REPORT),
            ("whole_window_basis", InputRole.WHOLE_WINDOW_BASIS),
            ("g2a_selection", InputRole.G2A_SELECTION),
            ("prompt_pin", InputRole.PROMPT_PIN),
        ),
        VerifiedReportedEnergyParents,
    ),
    D165CloseoutRef: _FamilySpec(
        "d165_closeout",
        (
            ("closeout", InputRole.D165_CLOSEOUT),
            ("finalized_manifest", InputRole.FINALIZED_MANIFEST),
            ("floor_artifact", InputRole.FLOOR_ARTIFACT),
            ("replay_sidecar", InputRole.REPLAY_SIDECAR),
        ),
        VerifiedD165Closeout,
    ),
    WholeWindowVerdictRef: _FamilySpec(
        "whole_window_verdict",
        (
            ("campaign_log", InputRole.CAMPAIGN_LOG),
            ("standalone_verdict", InputRole.STANDALONE_VERDICT),
            ("prospective_manifest", InputRole.PROSPECTIVE_MANIFEST),
            ("plan", InputRole.PLAN),
        ),
        VerifiedWholeWindowVerdict,
    ),
    ClaimEvidenceRef: _FamilySpec(
        "claim_evidence",
        (
            ("claim_verdicts", InputRole.CLAIM_VERDICTS),
            ("claim_side_bound", InputRole.CLAIM_SIDE_BOUND),
            ("finalized_manifest", InputRole.FINALIZED_MANIFEST),
            ("floor_artifact", InputRole.FLOOR_ARTIFACT),
        ),
        VerifiedClaimEvidence,
    ),
    TransferProjectionRef: _FamilySpec(
        "transfer_projection",
        (
            ("result_projection", InputRole.TRANSFER_RESULT),
            ("reviewed_capture", InputRole.REVIEWED_CAPTURE),
            ("plan", InputRole.PLAN),
            ("pre_data_receipt", InputRole.PRE_DATA_RECEIPT),
            ("pulse_bound_source", InputRole.PULSE_BOUND_SOURCE),
            ("bundle_inventory", InputRole.BUNDLE_INVENTORY),
        ),
        VerifiedTransferProjection,
    ),
}


@dataclass(frozen=True)
class _ReplayState:
    family: str
    root: Path
    bindings: tuple[BoundFile, ...]


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


def _validator_source_sha256(family: str) -> str:
    if family not in {spec.family for spec in _FAMILY_SPECS.values()}:
        raise ValueError("unknown paper custody family")
    source = inspect.getsource(_replay_family).encode("utf-8")
    return _sha256(family.encode("utf-8") + b"\0" + source)


def _relative_path(binding: BoundFile) -> str:
    if type(binding) is not BoundFile:
        raise PaperCustodyRefusal(
            "paper_custody_request_invalid", input_role=getattr(binding, "role", None)
        )
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
    if not isinstance(binding.role, InputRole) or _SHA256_RE.fullmatch(
        binding.expected_sha256
    ) is None:
        raise PaperCustodyRefusal(
            "paper_custody_request_invalid", input_role=binding.role
        )
    return text


def _record_tuple(
    session: V2AuthenticationReadSession,
    root: Path,
    bindings: tuple[BoundFile, ...],
) -> tuple[VerifiedDigest, ...]:
    records = session.records
    result: list[VerifiedDigest] = []
    for binding in bindings:
        relative = _relative_path(binding)
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
    code: str,
    *,
    role: InputRole | None = None,
    validator_codes: tuple[str, ...] = (),
    session: V2AuthenticationReadSession | None = None,
    root: Path | None = None,
    bindings: tuple[BoundFile, ...] = (),
) -> None:
    records = (
        _record_tuple(session, root, bindings)
        if session is not None and root is not None
        else ()
    )
    raise PaperCustodyRefusal(
        code,
        input_role=role,
        validator_codes=validator_codes,
        records=records,
    )


def _git_root(root: Path) -> Path:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PaperCustodyRefusal("paper_custody_anchor_unavailable") from exc
    discovered = Path(completed.stdout.strip()).resolve(strict=True)
    if discovered != root:
        raise PaperCustodyRefusal("paper_custody_anchor_mismatch")
    return discovered


def _git_blob(root: Path, relative: str, role: InputRole) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "show", f"HEAD:{relative}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PaperCustodyRefusal(
            "paper_custody_anchor_unavailable", input_role=role
        ) from exc
    return completed.stdout


def _read_once(
    session: V2AuthenticationReadSession,
    root: Path,
    binding: BoundFile,
    *,
    bindings: tuple[BoundFile, ...],
) -> bytes:
    relative = _relative_path(binding)
    grammar: Literal["json", "jsonl", "raw"] = (
        "jsonl" if relative.endswith(".jsonl") else "json"
    )
    try:
        raw = session.read_nofollow_pinned(
            root,
            relative,
            expected_sha256=binding.expected_sha256,
            grammar=grammar,
            label=f"paper custody {binding.role.value}",
        )
    except V2AuthenticationInputError as exc:
        if exc.reason == V2_AUTHENTICATION_INPUT_CHANGED:
            code = "paper_custody_input_changed"
        elif exc.reason == V2_AUTHENTICATION_INPUT_DIGEST_MISMATCH:
            code = "paper_custody_digest_mismatch"
        else:
            code = "paper_custody_parse_invalid"
        _raise(
            code,
            role=binding.role,
            session=session,
            root=root,
            bindings=bindings,
        )
    except (OSError, ValueError) as exc:
        code = (
            "paper_custody_input_unreadable"
            if isinstance(exc, FileNotFoundError)
            else "paper_custody_path_refused"
        )
        try:
            _raise(
                code,
                role=binding.role,
                session=session,
                root=root,
                bindings=bindings,
            )
        except PaperCustodyRefusal as refusal:
            raise refusal from exc
    return raw


def _validate_inventory(
    raw: bytes,
    *,
    family: str,
    expected: tuple[BoundFile, ...],
) -> tuple[Literal["production", "test_fixture_non_issuing"], dict[InputRole, dict[str, str]]]:
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
    if mode not in {"production", "test_fixture_non_issuing"}:
        raise PaperCustodyRefusal(
            "paper_custody_receipt_invalid", input_role=InputRole.CUSTODY_INVENTORY
        )
    rows = value.get("files")
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise PaperCustodyRefusal(
            "paper_custody_evidence_ambiguous", input_role=InputRole.CUSTODY_INVENTORY
        )
    indexed: dict[InputRole, dict[str, str]] = {}
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
            role in indexed
            or not isinstance(row["authority"], str)
            or row["authority"] not in {"git_blob", "generated"}
            or not isinstance(row["path"], str)
            or not isinstance(row["sha256"], str)
            or _SHA256_RE.fullmatch(row["sha256"]) is None
        ):
            raise PaperCustodyRefusal(
                "paper_custody_evidence_ambiguous",
                input_role=InputRole.CUSTODY_INVENTORY,
            )
        indexed[role] = row
    expected_by_role = {binding.role: binding for binding in expected}
    if len(expected_by_role) != len(expected) or set(indexed) != set(expected_by_role):
        raise PaperCustodyRefusal(
            "paper_custody_evidence_ambiguous", input_role=InputRole.CUSTODY_INVENTORY
        )
    for role, binding in expected_by_role.items():
        row = indexed[role]
        if row["path"] != _relative_path(binding):
            raise PaperCustodyRefusal(
                "paper_custody_anchor_mismatch", input_role=role
            )
    return mode, indexed


def _validate_receipt(
    raw: bytes,
    ref: ReceiptRef,
    *,
    family: str,
    sources: tuple[BoundFile, ...],
) -> dict[str, object]:
    if (
        type(ref) is not ReceiptRef
        or ref.file.role is not InputRole.VALIDATOR_RECEIPT
        or ref.schema != _RECEIPT_SCHEMA
        or ref.validator != f"joulewise.paper_custody.{family}.v1"
        or not isinstance(ref.validator_source_sha256, str)
        or _SHA256_RE.fullmatch(ref.validator_source_sha256) is None
    ):
        raise PaperCustodyRefusal(
            "paper_custody_request_invalid", input_role=InputRole.VALIDATOR_RECEIPT
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
        key=lambda row: row["role"],
    )
    expected_source = _validator_source_sha256(family)
    if (
        value.get("schema_version") != ref.schema
        or value.get("family") != family
        or value.get("status") != "PASS"
        or value.get("validator") != ref.validator
        or value.get("validator_source_sha256") != expected_source
        or ref.validator_source_sha256 != expected_source
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
    sources: tuple[BoundFile, ...],
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


def _validate_production_documents(
    family: str,
    root: Path,
    sources: tuple[BoundFile, ...],
    raws: dict[InputRole, bytes],
) -> tuple[str, ...]:
    """Replay available owning validators; no absent producer is invented."""

    parsed = {role: _json_object(raw) for role, raw in raws.items()}
    if family == "reported_energy_parents":
        from joulewise.floor_extraction import (
            validate_d117_mint_consumption_report,
            validate_extraction_spec,
        )

        return tuple(
            [
                *validate_extraction_spec(parsed[InputRole.EXTRACTION_SPEC]),
                *validate_d117_mint_consumption_report(
                    parsed[InputRole.EXTRACTION_REPORT]
                ),
            ]
        )
    if family == "d165_closeout":
        from joulewise.d165_dominance_closeout import validate_d165_paper_sources

        return validate_d165_paper_sources(
            closeout=parsed[InputRole.D165_CLOSEOUT],
            finalized_manifest_bytes=raws[InputRole.FINALIZED_MANIFEST],
            finalized_manifest_path=(
                root
                / _relative_path(
                    next(
                        binding
                        for binding in sources
                        if binding.role is InputRole.FINALIZED_MANIFEST
                    )
                )
            ),
            custody_root=root,
            floor_artifact_bytes=raws[InputRole.FLOOR_ARTIFACT],
            replay_sidecar_bytes=raws[InputRole.REPLAY_SIDECAR],
        )
    if family == "claim_evidence":
        from joulewise.analysis_engine.artifact import validate_claim_verdicts

        errors = list(
            validate_claim_verdicts(
                parsed[InputRole.CLAIM_VERDICTS],
                frozen_manifest=parsed[InputRole.FINALIZED_MANIFEST],
            )
        )
        inputs = parsed[InputRole.CLAIM_VERDICTS].get("inputs")
        floor_link = (
            inputs.get("floor_artifact") if isinstance(inputs, dict) else None
        )
        embedded = (
            floor_link.get("embedded_bytes_base64")
            if isinstance(floor_link, dict)
            else None
        )
        try:
            embedded_floor = (
                base64.b64decode(embedded, validate=True)
                if isinstance(embedded, str)
                else None
            )
        except (binascii.Error, ValueError):
            embedded_floor = None
        if embedded_floor != raws[InputRole.FLOOR_ARTIFACT]:
            errors.append("claim_floor_anchor_mismatch")
        return tuple(errors)
    if family == "whole_window_verdict":
        from joulewise.whole_window import validate_whole_window_verdict_row

        row = parsed[InputRole.STANDALONE_VERDICT]
        bundle_ids = row.get("bundle_ids")
        referenced = {
            value for value in bundle_ids if isinstance(value, str)
        } if isinstance(bundle_ids, list) else set()
        validation = validate_whole_window_verdict_row(row, root, referenced)
        return () if validation.authentic else validation.reasons
    # The whole-window and transfer producer gates are intentionally absent.
    return ()


def _replay_family(
    family: str,
    mode: Literal["production", "test_fixture_non_issuing"],
    root: Path,
    sources: tuple[BoundFile, ...],
    raws: dict[InputRole, bytes],
) -> tuple[str, ...]:
    if mode == "test_fixture_non_issuing":
        return _validate_fixture_documents(family, sources, raws)
    try:
        return _validate_production_documents(family, root, sources, raws)
    except (KeyError, TypeError, ValueError) as exc:
        return (type(exc).__name__,)


def _after_validator_replay(state: _ReplayState) -> None:
    """Deliberately empty seam used to prove replay-to-reopen detection."""

    if not isinstance(state, _ReplayState):
        raise TypeError("invalid paper custody replay state")


def _construct_verified(
    output_type: type,
    evidence: CustodyEvidence,
    payload: _FrozenObject,
) -> _VerifiedFamily:
    value = object.__new__(output_type)
    object.__setattr__(value, "evidence", evidence)
    object.__setattr__(value, "_payload", payload)
    return value


@overload
def open_paper_input(ref: ReportedEnergyParentsRef) -> VerifiedReportedEnergyParents: ...


@overload
def open_paper_input(ref: D165CloseoutRef) -> VerifiedD165Closeout: ...


@overload
def open_paper_input(ref: WholeWindowVerdictRef) -> VerifiedWholeWindowVerdict: ...


@overload
def open_paper_input(ref: ClaimEvidenceRef) -> VerifiedClaimEvidence: ...


@overload
def open_paper_input(ref: TransferProjectionRef) -> VerifiedTransferProjection: ...


def open_paper_input(ref: _FamilyRef) -> _VerifiedFamily:
    """Open one of the five closed paper-input families or refuse it."""

    spec = _FAMILY_SPECS.get(type(ref))
    if spec is None or not dataclasses.is_dataclass(ref):
        raise PaperCustodyRefusal("paper_custody_request_invalid")
    if not isinstance(ref.root, Path):
        raise PaperCustodyRefusal("paper_custody_request_invalid")
    try:
        root = ref.root.resolve(strict=True)
    except OSError as exc:
        raise PaperCustodyRefusal("paper_custody_anchor_unavailable") from exc
    _git_root(root)
    if type(ref.inventory) is not BoundFile:
        raise PaperCustodyRefusal("paper_custody_request_invalid")
    if ref.inventory.role is not InputRole.CUSTODY_INVENTORY:
        raise PaperCustodyRefusal(
            "paper_custody_request_invalid", input_role=ref.inventory.role
        )
    sources = tuple(getattr(ref, field) for field, _role in spec.fields)
    for (field, role), binding in zip(spec.fields, sources, strict=True):
        if type(binding) is not BoundFile or binding.role is not role:
            raise PaperCustodyRefusal(
                "paper_custody_request_invalid",
                input_role=getattr(binding, "role", None),
            )
    if type(ref.receipt) is not ReceiptRef or type(ref.receipt.file) is not BoundFile:
        raise PaperCustodyRefusal("paper_custody_request_invalid")
    receipt_binding = ref.receipt.file
    bindings = (ref.inventory, *sources, receipt_binding)
    paths = [_relative_path(binding) for binding in bindings]
    roles = [binding.role for binding in bindings]
    if len(set(paths)) != len(paths) or len(set(roles)) != len(roles):
        raise PaperCustodyRefusal("paper_custody_evidence_ambiguous")

    with V2AuthenticationReadSession() as session:
        inventory_raw = _read_once(
            session, root, ref.inventory, bindings=bindings
        )
        inventory_relative = _relative_path(ref.inventory)
        if _git_blob(root, inventory_relative, ref.inventory.role) != inventory_raw:
            _raise(
                "paper_custody_anchor_mismatch",
                role=ref.inventory.role,
                session=session,
                root=root,
                bindings=bindings,
            )
        mode, inventory = _validate_inventory(
            inventory_raw,
            family=spec.family,
            expected=(*sources, receipt_binding),
        )
        raws: dict[InputRole, bytes] = {}
        all_first_raws: dict[InputRole, bytes] = {
            InputRole.CUSTODY_INVENTORY: inventory_raw
        }
        for binding in (*sources, receipt_binding):
            raw = _read_once(session, root, binding, bindings=bindings)
            row = inventory[binding.role]
            if row["sha256"] != _sha256(raw):
                _raise(
                    "paper_custody_anchor_mismatch",
                    role=binding.role,
                    session=session,
                    root=root,
                    bindings=bindings,
                )
            if row["authority"] == "git_blob" and _git_blob(
                root, _relative_path(binding), binding.role
            ) != raw:
                _raise(
                    "paper_custody_anchor_mismatch",
                    role=binding.role,
                    session=session,
                    root=root,
                    bindings=bindings,
                )
            all_first_raws[binding.role] = raw
            if binding.role is not InputRole.VALIDATOR_RECEIPT:
                raws[binding.role] = raw

        receipt_value = _validate_receipt(
            all_first_raws[InputRole.VALIDATOR_RECEIPT],
            ref.receipt,
            family=spec.family,
            sources=sources,
        )
        validator_codes = _replay_family(spec.family, mode, root, sources, raws)
        if validator_codes:
            _raise(
                "paper_custody_validator_refused",
                validator_codes=validator_codes,
                session=session,
                root=root,
                bindings=bindings,
            )
        if receipt_value["replay_codes"] != list(validator_codes):
            _raise(
                "paper_custody_receipt_binding_mismatch",
                role=InputRole.VALIDATOR_RECEIPT,
                session=session,
                root=root,
                bindings=bindings,
            )

        _after_validator_replay(_ReplayState(spec.family, root, bindings))
        for binding in bindings:
            try:
                reopened = _read_once(session, root, binding, bindings=bindings)
            except PaperCustodyRefusal as exc:
                if exc.code in {
                    "paper_custody_digest_mismatch",
                    "paper_custody_parse_invalid",
                    "paper_custody_path_refused",
                    "paper_custody_input_unreadable",
                }:
                    _raise(
                        "paper_custody_input_changed",
                        role=binding.role,
                        session=session,
                        root=root,
                        bindings=bindings,
                    )
                raise
            if reopened != all_first_raws[binding.role]:
                _raise(
                    "paper_custody_input_changed",
                    role=binding.role,
                    session=session,
                    root=root,
                    bindings=bindings,
                )

        records = _record_tuple(session, root, bindings)
        evidence = CustodyEvidence(
            family=spec.family,
            inputs=records,
            receipt_sha256=_sha256(
                all_first_raws[InputRole.VALIDATOR_RECEIPT]
            ),
            validator_source_sha256=_validator_source_sha256(spec.family),
            mode=mode,
            issuance_authorized=mode == "production",
        )
        if type(ref) is WholeWindowVerdictRef:
            raise PaperCustodyRefusal(
                "paper_custody_blocked_pending_receipt",
                input_role=InputRole.VALIDATOR_RECEIPT,
                records=records,
            )
        if mode == "production":
            # No production custody inventory is registered in this fixture-only
            # landing.  Producers register prospectively in their own missions.
            raise PaperCustodyRefusal(
                "paper_custody_receipt_unissued",
                input_role=InputRole.CUSTODY_INVENTORY,
                records=records,
            )
        payload = _FrozenObject(
            tuple(
                (binding.role.value, _freeze_json(_json_object(raws[binding.role])))
                for binding in sources
            )
        )
        return _construct_verified(spec.output_type, evidence, payload)


__all__ = [
    "BoundFile",
    "ClaimEvidenceRef",
    "CustodyEvidence",
    "D165CloseoutRef",
    "InputRole",
    "PAPER_CUSTODY_REFUSAL_CODES",
    "PaperCustodyRefusal",
    "ReceiptRef",
    "ReportedEnergyParentsRef",
    "TransferProjectionRef",
    "VerifiedClaimEvidence",
    "VerifiedD165Closeout",
    "VerifiedDigest",
    "VerifiedReportedEnergyParents",
    "VerifiedTransferProjection",
    "VerifiedWholeWindowVerdict",
    "WholeWindowVerdictRef",
    "open_paper_input",
]
