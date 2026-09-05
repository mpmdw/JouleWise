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
from typing import Callable, Literal, overload

from joulewise.authentication_io import (
    V2AuthenticationInputError,
    V2AuthenticationReadSession,
    V2_AUTHENTICATION_INPUT_CHANGED,
    V2_AUTHENTICATION_INPUT_DIGEST_MISMATCH,
)
from joulewise.identity_pins import IdentityPinProjectionError, _mint_git_anchor


_SUPPLY_MAP_PATH = "configs/paper_supply/supply_map.json"
_SUPPLY_MAP_SCHEMA = "joulewise.paper_supply_map.v1"
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
        "paper_custody_receipt_unissued",
        "paper_custody_blocked_pending_receipt",
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
        "evidence",
        "_payload",
    }
)


def _capability_getattribute(value: object, name: str) -> object:
    if name in _CAPABILITY_FIELDS:
        _require_custody_capability(value)
    return object.__getattribute__(value, name)


def _make_custody_capability_mint() -> tuple[Callable[..., object], ...]:
    """Keep the construction token inside the seam's private closures."""

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
        if output_type not in {
            VerifiedReportedEnergyParents,
            VerifiedD165Closeout,
            VerifiedWholeWindowVerdict,
            VerifiedClaimEvidence,
            VerifiedTransferProjection,
        } or type(payload) is not _FrozenObject:
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
class VerifiedReportedEnergyParents:
    evidence: CustodyEvidence
    _payload: _FrozenObject
    _custody_token: object = field(repr=False, compare=False)

    __init__ = _refuse_verified_construction
    __getattribute__ = _capability_getattribute


@dataclass(frozen=True, init=False, slots=True)
class VerifiedD165Closeout:
    evidence: CustodyEvidence
    _payload: _FrozenObject
    _custody_token: object = field(repr=False, compare=False)

    __init__ = _refuse_verified_construction
    __getattribute__ = _capability_getattribute


@dataclass(frozen=True, init=False, slots=True)
class VerifiedWholeWindowVerdict:
    evidence: CustodyEvidence
    _payload: _FrozenObject
    _custody_token: object = field(repr=False, compare=False)

    __init__ = _refuse_verified_construction
    __getattribute__ = _capability_getattribute


@dataclass(frozen=True, init=False, slots=True)
class VerifiedClaimEvidence:
    evidence: CustodyEvidence
    _payload: _FrozenObject
    _custody_token: object = field(repr=False, compare=False)

    __init__ = _refuse_verified_construction
    __getattribute__ = _capability_getattribute


@dataclass(frozen=True, init=False, slots=True)
class VerifiedTransferProjection:
    evidence: CustodyEvidence
    _payload: _FrozenObject
    _custody_token: object = field(repr=False, compare=False)

    __init__ = _refuse_verified_construction
    __getattribute__ = _capability_getattribute


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
    output_type: type


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


@dataclass(frozen=True)
class _ReplayState:
    family: str
    repository: Path
    runs_root: Path
    bindings: tuple[_BoundFile, ...]


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
) -> tuple[tuple[str, Callable[..., object]], ...]:
    """Return the closed dispatcher-plus-owner source census for one family."""

    common: tuple[tuple[str, Callable[..., object]], ...] = (
        ("paper_custody._replay_family", _replay_family),
        ("paper_custody._validate_fixture_documents", _validate_fixture_documents),
        (
            "paper_custody._validate_production_documents",
            _validate_production_documents,
        ),
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
        from joulewise.analysis_engine.artifact import validate_claim_verdicts

        owners = (
            ("analysis_engine.artifact.validate_claim_verdicts", validate_claim_verdicts),
        )
    elif family == "transfer_projection":
        owners = ()
    else:
        raise ValueError("unknown paper custody family")
    return (*common, *owners)


def _validator_source_sha256(family: str) -> str:
    digest = hashlib.sha256()
    digest.update(family.encode("utf-8") + b"\0")
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
    code: str,
    *,
    role: InputRole | None = None,
    validator_codes: tuple[str, ...] = (),
    session: V2AuthenticationReadSession | None = None,
    repository: Path | None = None,
    runs_root: Path | None = None,
    bindings: tuple[_BoundFile, ...] = (),
) -> None:
    records = (
        _record_tuple(session, repository, runs_root, bindings)
        if session is not None and repository is not None and runs_root is not None
        else ()
    )
    raise PaperCustodyRefusal(
        code,
        input_role=role,
        validator_codes=validator_codes,
        records=records,
    )


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
    if set(value) != {"roles", "schema_version"} or value.get(
        "schema_version"
    ) != _SUPPLY_MAP_SCHEMA:
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
    }:
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
    if not isinstance(rows, list) or len(rows) != len(spec.roles):
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
    if tuple(binding.role for binding in sources) != spec.roles:
        raise PaperCustodyRefusal("paper_custody_supply_map_invalid")
    bindings = (inventory, *sources, receipt_file)
    identities = [
        (binding.base, _relative_path(binding)) for binding in bindings
    ]
    if len(set(identities)) != len(identities) or len(
        {binding.role for binding in bindings}
    ) != len(bindings):
        raise PaperCustodyRefusal("paper_custody_evidence_ambiguous")
    return _ResolvedSupply(
        inventory=inventory,
        sources=tuple(sources),
        receipt=_ReceiptRef(file=receipt_file, validator=validator),
        supply_map_sha256=_sha256(raw),
    )


def _read_once(
    session: V2AuthenticationReadSession,
    repository: Path,
    runs_root: Path,
    binding: _BoundFile,
    *,
    bindings: tuple[_BoundFile, ...],
) -> bytes:
    relative = _relative_path(binding)
    root = _binding_root(binding, repository, runs_root)
    grammar: Literal["json", "jsonl", "raw"] = (
        "jsonl" if relative.endswith(".jsonl") else "json"
    )
    try:
        return session.read_nofollow_pinned(
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
            repository=repository,
            runs_root=runs_root,
            bindings=bindings,
        )
    except OSError as exc:
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
                repository=repository,
                runs_root=runs_root,
                bindings=bindings,
            )
        except PaperCustodyRefusal as refusal:
            raise refusal from exc
    raise AssertionError("unreachable paper custody read")


def _validate_inventory(
    raw: bytes,
    *,
    family: str,
    expected: tuple[_BoundFile, ...],
) -> tuple[
    Literal["production", "test_fixture_non_issuing"],
    dict[InputRole, dict[str, str]],
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
            or row.get("authority") not in {"git_blob", "generated"}
            or not isinstance(row.get("path"), str)
            or not isinstance(row.get("sha256"), str)
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
        key=lambda row: row["role"],
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


def _validate_production_documents(
    family: str,
    repository: Path,
    runs_root: Path,
    sources: tuple[_BoundFile, ...],
    raws: dict[InputRole, bytes],
) -> tuple[str, ...]:
    """Replay every available owning validator; absent producers stay blocked."""

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
        from joulewise.dominance_closeout import validate_d165_paper_sources

        manifest_binding = next(
            binding
            for binding in sources
            if binding.role is InputRole.FINALIZED_MANIFEST
        )
        return validate_d165_paper_sources(
            closeout=parsed[InputRole.D165_CLOSEOUT],
            finalized_manifest_bytes=raws[InputRole.FINALIZED_MANIFEST],
            finalized_manifest_path=(
                _binding_root(manifest_binding, repository, runs_root)
                / _relative_path(manifest_binding)
            ),
            custody_root=runs_root,
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
        referenced = (
            {value for value in bundle_ids if isinstance(value, str)}
            if isinstance(bundle_ids, list)
            else set()
        )
        validation = validate_whole_window_verdict_row(row, runs_root, referenced)
        return () if validation.authentic else validation.reasons
    return ()


def _replay_family(
    family: str,
    mode: Literal["production", "test_fixture_non_issuing"],
    repository: Path,
    runs_root: Path,
    sources: tuple[_BoundFile, ...],
    raws: dict[InputRole, bytes],
) -> tuple[str, ...]:
    if mode == "test_fixture_non_issuing":
        return _validate_fixture_documents(family, sources, raws)
    try:
        return _validate_production_documents(
            family, repository, runs_root, sources, raws
        )
    except (KeyError, TypeError, ValueError) as exc:
        return (type(exc).__name__,)


def _after_validator_replay(state: _ReplayState) -> None:
    """Deliberately empty seam used to prove replay-to-reopen detection."""

    if not isinstance(state, _ReplayState):
        raise TypeError("invalid paper custody replay state")


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
) -> _VerifiedFamily:
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
        bindings = (supply.inventory, *sources, receipt_binding)

        inventory_raw = _read_once(
            session,
            repository,
            runs_root,
            supply.inventory,
            bindings=bindings,
        )
        mode, _inventory = _validate_inventory(
            inventory_raw,
            family=spec.family,
            expected=(*sources, receipt_binding),
        )
        raws: dict[InputRole, bytes] = {}
        all_first_raws: dict[InputRole, bytes] = {
            InputRole.CUSTODY_INVENTORY: inventory_raw
        }
        for binding in (*sources, receipt_binding):
            raw = _read_once(
                session,
                repository,
                runs_root,
                binding,
                bindings=bindings,
            )
            all_first_raws[binding.role] = raw
            if binding.role is not InputRole.VALIDATOR_RECEIPT:
                raws[binding.role] = raw

        receipt_value = _validate_receipt(
            all_first_raws[InputRole.VALIDATOR_RECEIPT],
            supply.receipt,
            family=spec.family,
            sources=sources,
        )
        validator_codes = _replay_family(
            spec.family, mode, repository, runs_root, sources, raws
        )
        if validator_codes:
            _raise(
                "paper_custody_validator_refused",
                validator_codes=validator_codes,
                session=session,
                repository=repository,
                runs_root=runs_root,
                bindings=bindings,
            )
        if receipt_value["replay_codes"] != list(validator_codes):
            _raise(
                "paper_custody_receipt_binding_mismatch",
                role=InputRole.VALIDATOR_RECEIPT,
                session=session,
                repository=repository,
                runs_root=runs_root,
                bindings=bindings,
            )

        _after_validator_replay(
            _ReplayState(spec.family, repository, runs_root, bindings)
        )
        for binding in bindings:
            try:
                reopened = _read_once(
                    session,
                    repository,
                    runs_root,
                    binding,
                    bindings=bindings,
                )
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
                        repository=repository,
                        runs_root=runs_root,
                        bindings=bindings,
                    )
                raise
            if reopened != all_first_raws[binding.role]:
                _raise(
                    "paper_custody_input_changed",
                    role=binding.role,
                    session=session,
                    repository=repository,
                    runs_root=runs_root,
                    bindings=bindings,
                )

        records = _record_tuple(session, repository, runs_root, bindings)
        evidence = _construct_custody_evidence(
            _custody_token,
            family=spec.family,
            inputs=records,
            receipt_sha256=_sha256(
                all_first_raws[InputRole.VALIDATOR_RECEIPT]
            ),
            validator_source_sha256=_validator_source_sha256(spec.family),
            anchor_head=head,
            supply_map_sha256=supply.supply_map_sha256,
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
        return _construct_verified(
            _custody_token, spec.output_type, evidence, payload
        )


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
    "VerifiedD165Closeout",
    "VerifiedDigest",
    "VerifiedReportedEnergyParents",
    "VerifiedTransferProjection",
    "VerifiedWholeWindowVerdict",
    "WholeWindowVerdictRef",
    "open_paper_input",
]
