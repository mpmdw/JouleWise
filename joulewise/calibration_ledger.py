"""Authenticated calibration-observation receipt ledger (D-109).

The ledger closes workflow omission, unregistered evidence, and rollback or
stale-head consumption.  It does not defend against a malicious trusted
writer or an authority that rewrites both Git and the complete ledger
history.  Version 1 is deliberately a single-authority, single-machine
protocol.

Each ordinary capture is represented by two immutable hash-chained receipts:
a reservation with disposition ``pending`` written before capture state
exists, then exactly one finalization.  Bracket sessions reserve both slots in
one capability and append an exclusive slot-claim before either writer creates
capture state.  Evaluation consumes one frozen snapshot whose physical head
must equal the repository-committed head pin.

Every new business append is preceded by an immutable in-ledger intent.  The
intent binds the ledger lineage and exact physical head, a stable operation
key, and the complete semantic target.  Recovery obtains the target only from
that intent.  Non-admitted tail bytes are never deleted: a following
abandonment control receipt authenticates their exact physical range before
the committed target is reconstructed.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import threading
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, BinaryIO

from joulewise.calibration_exits import (
    REFUSAL_BY_CODE,
    RefusalCode,
)
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS


LEDGER_SCHEMA = "joulewise.calibration_observation_ledger.v1"
RECEIPT_SCHEMA = "joulewise.calibration_observation_receipt.v1"
BRACKET_SESSION_SCHEMA = "joulewise.calibration_window_bracket_session.v1"
BRACKET_SESSION_OPEN_EVENT = "bracket-session-open"
BRACKET_SESSION_SLOT_CLAIM_EVENT = "bracket-session-slot-claim"
BRACKET_SESSION_FINALIZATION_EVENT = "bracket-session-slot-finalization"
BRACKET_SESSION_ABORT_EVENT = "bracket-session-abort"
BRACKET_SESSION_SLOTS = ("pre", "post")
CONTROL_SCHEMA = "joulewise.calibration_ledger_control.v1"
APPEND_INTENT_EVENT = "append-intent"
ABANDONMENT_EVENT = "abandon-tail"
APPEND_POLICY_REVISION = "d117-ledger-resident-v1"
CLAIM_POLICY_REVISION = "d117-stable-claim-v1"
# Every governed semantic append is represented by one durable intent followed
# by its committed target.  Consumers that model physical ledger cadence must
# derive it from this protocol constant instead of hard-coding row counts.
APPEND_RECORDS_PER_OPERATION = 2
HISTORICAL_IMPORT_TABLE_SCHEMA = (
    "joulewise.calibration_historical_import_table.v1"
)
HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA = (
    "joulewise.calibration_historical_import_custody_manifest.v1"
)
HISTORICAL_IMPORT_EVENT_PREFIX = "historical-import-v1"
HISTORICAL_IMPORT_RESERVATION_EVENT = (
    f"{HISTORICAL_IMPORT_EVENT_PREFIX}-reservation"
)
HISTORICAL_IMPORT_FINALIZATION_EVENT = (
    f"{HISTORICAL_IMPORT_EVENT_PREFIX}-finalization"
)
GENESIS_DIGEST = "0" * 64
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER_PATH = REPO_ROOT / "runs" / "calibration_observation_ledger.jsonl"
DEFAULT_HEAD_PIN_PATH = (
    REPO_ROOT / "configs" / "calibration" / "calibration_ledger_head.json"
)

IDENTITY_EPOCH_FIELDS = (
    "os_build",
    "hardware_model",
    "power_policy",
    "sampling_interval_ms",
    "estimator_revision",
    "pulse_protocol_id",
)
T1_FIELDS = tuple(V2_BINDING_FIELDS)
FINAL_DISPOSITIONS = frozenset(
    {"valid", "systematic-invalid", "ordinary-invalid", "abandoned"}
)
HISTORICAL_IMPORT_DISPOSITIONS = frozenset(
    {"valid", "systematic-invalid", "ordinary-invalid"}
)
ALL_DISPOSITIONS = FINAL_DISPOSITIONS | {"pending"}
CONTENT_ID_ARTIFACTS = (
    "instrument_evidence.json",
    "manifest.json",
)
GOVERNED_ARTIFACTS = (
    "raw/powermetrics.plist",
    "events.jsonl",
    "power_trace.csv",
    "instrument_evidence.json",
    "manifest.json",
)
MANIFEST_BOUND_ARTIFACTS = tuple(
    name for name in GOVERNED_ARTIFACTS if name != "manifest.json"
)
EVIDENCE_BOUND_ARTIFACTS = (
    "raw/powermetrics.plist",
    "events.jsonl",
    "power_trace.csv",
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

# Stable refusal taxonomy.  Consumers propagate these exact spellings into
# claim barriers; no malformed or unresolved history is silently omitted.
REFUSAL_TAXONOMY: Mapping[str, str] = MappingProxyType(
    {
        code.value: REFUSAL_BY_CODE[code].description
        for code in RefusalCode
        if code.value.startswith("calibration_ledger_")
        or code is RefusalCode.OBSERVATION_UNCLASSIFIABLE
    }
)


class CalibrationLedgerError(ValueError):
    """A writer-side ledger operation cannot preserve the D-109 contract."""

    def __init__(
        self,
        refusal: RefusalCode | str,
        *,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        # Historical import preparation is outside the unattended calibration
        # path and retains legacy prose until its own charter. Every D-117
        # operational site passes RefusalCode and therefore exposes ``code``.
        self.code = refusal if isinstance(refusal, RefusalCode) else None
        self.context = MappingProxyType(dict(context or {}))
        message = (
            f"{refusal.value}: {REFUSAL_BY_CODE[refusal].description}"
            if isinstance(refusal, RefusalCode)
            else refusal
        )
        if self.context:
            diagnostic = ", ".join(
                f"{key}={value!r}" for key, value in sorted(self.context.items())
            )
            message = f"{message} ({diagnostic})"
        super().__init__(message)


_REFUSAL_PRECEDENCE = (
    RefusalCode.LEDGER_RECOVERY_REQUIRED,
    RefusalCode.LEDGER_MALFORMED,
    RefusalCode.LEDGER_CHAIN_CONFLICT,
    RefusalCode.LEDGER_UNGOVERNED_BUSINESS,
    RefusalCode.LEDGER_OPERATION_CONFLICT,
    RefusalCode.LEDGER_CUSTODY_INVALID,
    RefusalCode.LEDGER_BRACKET_SESSION_CONFLICT,
    RefusalCode.LEDGER_ATTEMPT_CONFLICT,
    RefusalCode.LEDGER_CONTENT_CONFLICT,
    RefusalCode.LEDGER_PENDING,
    RefusalCode.LEDGER_BRACKET_SESSION_OPEN,
    RefusalCode.LEDGER_HEAD_UNCOMMITTED,
    RefusalCode.LEDGER_HEAD_MISMATCH,
    RefusalCode.LEDGER_ROLLBACK,
)


def _primary_refusal(reasons: Sequence[str]) -> RefusalCode:
    available = {RefusalCode(reason) for reason in reasons}
    return next(
        (code for code in _REFUSAL_PRECEDENCE if code in available),
        sorted(available, key=lambda code: code.value)[0],
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def stable_bracket_claim_id(
    *,
    session_id: str,
    slot: str,
    attempt_id: str,
    policy_revision: str = CLAIM_POLICY_REVISION,
) -> str:
    """Derive durable idempotency identity without process-local material."""

    return canonical_sha256(
        {
            "domain": "joulewise.calibration-bracket-claim-id.v1",
            "policy_revision": policy_revision,
            "session_id": session_id,
            "slot": slot,
            "attempt_id": attempt_id,
        }
    )


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


def _normalized_vector(
    value: Mapping[str, Any] | None,
    fields: Sequence[str],
) -> dict[str, Any]:
    source = value if isinstance(value, Mapping) else {}
    return {field: source.get(field) for field in fields}


def content_id_from_artifact_hashes(artifact_sha256: Mapping[str, Any]) -> str | None:
    """Return the path-independent identity of canonical primary bytes.

    The authenticated evidence document and its manifest are the canonical
    byte pair.  A copied custody tree therefore retains the same identity.
    Other receipt hashes remain custody checks but do not manufacture a new
    observation when a derived representation is regenerated.
    """

    identity = {
        name: artifact_sha256.get(name) for name in CONTENT_ID_ARTIFACTS
    }
    if any(not _is_sha256(value) for value in identity.values()):
        return None
    return canonical_sha256(identity)


def artifact_hashes(custody_dir: Path) -> dict[str, str]:
    """Hash every governed artifact present in one finalized custody tree."""

    root = Path(custody_dir)
    result: dict[str, str] = {}
    for relative in GOVERNED_ARTIFACTS:
        path = root / relative
        if path.is_file():
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def normalize_calibration_custody_path(path: Path | str) -> str:
    """Return the lexical absolute spelling used by reservation and capture.

    Custody identity is an exact ledger binding.  Resolving symlinks in only
    one writer would therefore change that identity even when both spellings
    name the same directory.
    """

    try:
        return str(Path(path).absolute())
    except (OSError, TypeError, ValueError) as exc:
        raise CalibrationLedgerError(
            "calibration custody path is malformed"
        ) from exc


def receipt_core(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in receipt.items() if key != "receipt_digest"}


def _receipt_digest(receipt: Mapping[str, Any]) -> str:
    return canonical_sha256(receipt_core(receipt))


@dataclass(frozen=True)
class LedgerObservation:
    sequence: int
    receipt_digest: str
    attempt_id: str
    content_id: str | None
    artifact_sha256: Mapping[str, str]
    identity_epoch: Mapping[str, Any]
    t1_bindings: Mapping[str, Any]
    capture_wall_time_s: str | None
    exact_bound_lexeme_s: str | None
    disposition: str
    custody_locator: str
    observation_kind: str = "live-capture"
    bracket_session_id: str | None = None
    bracket_slot: str | None = None
    bracket_window_id: str | None = None
    bracket_plan_id: str | None = None
    bracket_plan_sha256: str | None = None
    bracket_evidence_root_id: str | None = None
    bracket_runs_root: str | None = None

    @property
    def classification_disposition(self) -> str:
        """Map the writer terminal state onto the R2 observation schema."""

        return (
            "unresolved" if self.disposition == "abandoned" else self.disposition
        )

    @property
    def is_historical_import(self) -> bool:
        return self.observation_kind == "historical-import"


@dataclass(frozen=True)
class CalibrationLedgerSnapshot:
    """One immutable, fully checked view threaded through an evaluation."""

    ledger_schema: str
    ledger_path: Path
    head_sequence: int
    head_digest: str
    receipts: tuple[Mapping[str, Any], ...]
    observations: tuple[LedgerObservation, ...]
    refusal_reasons: tuple[str, ...]
    bracket_sessions: tuple["CalibrationBracketSession", ...] = ()
    baseline_sequence: int | None = None
    baseline_digest: str | None = None
    committed_head_sequence: int | None = None
    committed_head_digest: str | None = None

    @property
    def valid(self) -> bool:
        return not self.refusal_reasons

    @property
    def observation_by_attempt(self) -> Mapping[str, LedgerObservation]:
        return MappingProxyType(
            {observation.attempt_id: observation for observation in self.observations}
        )

    @property
    def bracket_session_by_id(self) -> Mapping[str, "CalibrationBracketSession"]:
        return MappingProxyType(
            {session.session_id: session for session in self.bracket_sessions}
        )

    @property
    def is_governed_open_bracket_extension(self) -> bool:
        """Whether the physical/pin gap is exactly one reserved open session."""

        allowed = {
            "calibration_ledger_bracket_session_open",
            "calibration_ledger_head_mismatch",
        }
        if (
            set(self.refusal_reasons) != allowed
            or self.committed_head_sequence is None
            or self.committed_head_digest is None
        ):
            return False
        open_sessions = [
            session for session in self.bracket_sessions if session.state == "open"
        ]
        if len(open_sessions) != 1:
            return False
        session = open_sessions[0]
        tail = self.receipts[self.committed_head_sequence :]
        business_tail = [
            row for row in tail if row.get("schema_version") != CONTROL_SCHEMA
        ]
        return bool(
            tail
            and business_tail
            and business_tail[0].get("event") == BRACKET_SESSION_OPEN_EVENT
            and business_tail[0].get("sequence") == session.capability_sequence
            and all(
                (
                    row.get("schema_version") == CONTROL_SCHEMA
                    and (
                        row.get("event") == ABANDONMENT_EVENT
                        or row.get("event") == APPEND_INTENT_EVENT
                        and row.get("target_core", {}).get("session_id")
                        == session.session_id
                    )
                )
                or row.get("session_id") == session.session_id
                for row in tail
            )
        )

    @property
    def observations_by_content(self) -> Mapping[str, tuple[LedgerObservation, ...]]:
        grouped: dict[str, list[LedgerObservation]] = {}
        for observation in self.observations:
            if observation.content_id is not None:
                grouped.setdefault(observation.content_id, []).append(observation)
        return MappingProxyType(
            {key: tuple(value) for key, value in sorted(grouped.items())}
        )

    def post_cutoff_live_observations(
        self, cutoff_sequence: int
    ) -> tuple[LedgerObservation, ...]:
        """Return only fresh live-capture observations after ``cutoff_sequence``.

        Historical bootstrap finalizations are deliberately excluded even
        when a caller compares them with the genesis sequence-zero cutoff.
        """

        if (
            isinstance(cutoff_sequence, bool)
            or not isinstance(cutoff_sequence, int)
            or cutoff_sequence < 0
        ):
            raise CalibrationLedgerError("cutoff_sequence must be nonnegative")
        return tuple(
            observation
            for observation in self.observations
            if observation.sequence > cutoff_sequence
            and not observation.is_historical_import
        )


@dataclass(frozen=True)
class CalibrationBracketSession:
    """Authenticated state of one prospectively reserved two-slot window."""

    session_id: str
    window_id: str
    plan_id: str
    plan_sha256: str
    evidence_root_id: str
    runs_root: str
    capability_receipt_digest: str
    capability_sequence: int
    slot_attempt_ids: Mapping[str, str]
    state: str
    finalized_slots: Mapping[str, LedgerObservation]
    abort_receipt_digest: str | None = None
    abort_reason: str | None = None


@dataclass(frozen=True)
class HistoricalImportPlan:
    """Deterministic, authenticated genesis bootstrap prepared in memory."""

    receipts: tuple[Mapping[str, Any], ...]
    final_sequence: int
    head_digest: str
    head_pin: Mapping[str, Any]
    disposition_table_sha256: str
    custody_manifest_sha256: str

    @property
    def ledger_bytes(self) -> bytes:
        return b"".join(canonical_json_bytes(row) + b"\n" for row in self.receipts)


class HistoricalImportDurabilityUncertain(CalibrationLedgerError):
    """The import committed, but its parent-directory fsync did not confirm."""

    outcome = "committed_durability_uncertain"

    def __init__(self, plan: HistoricalImportPlan) -> None:
        super().__init__(
            "historical import committed but parent-directory durability is uncertain"
        )
        self.plan = plan


@dataclass(frozen=True)
class CalibrationLedgerInspection:
    """Physical recovery state of one locked or immutable ledger view."""

    state: str
    ledger_id: str
    head_sequence: int
    head_digest: str
    valid_end_offset: int
    residue_start_offset: int
    residue_length: int
    residue_sha256: str
    active_operation_id: str | None
    active_operation_key: Mapping[str, Any] | None
    target_core_sha256: str | None
    legacy_journal_path: str | None = None
    legacy_journal_sha256: str | None = None


class PinRelation(str, Enum):
    EXACT = "exact"
    PHYSICAL_AHEAD = "physical_ahead"
    PHYSICAL_BEHIND = "physical_behind"
    DIVERGENT = "divergent"


@dataclass(frozen=True)
class CalibrationReadiness:
    phase: str
    status: str
    pin_relation: PinRelation
    refusal_code: RefusalCode | None
    session_id: str | None
    next_slot: str | None
    attempt_id: str | None
    custody_state: str | None
    claim_state: str | None
    needs_pin_commit: bool
    head_pin_candidate: Mapping[str, Any] | None
    enforcing_under_lease: bool

    def as_dict(self) -> dict[str, Any]:
        authorizes_arm = self.status == "ready" and self.enforcing_under_lease
        return {
            "phase": self.phase,
            "status": self.status,
            "pin_relation": self.pin_relation.value,
            "refusal_code": (
                self.refusal_code.value if self.refusal_code is not None else None
            ),
            "session_id": self.session_id,
            "next_slot": self.next_slot,
            "attempt_id": self.attempt_id,
            "custody_state": self.custody_state,
            "claim_state": self.claim_state,
            "needs_pin_commit": self.needs_pin_commit,
            "head_pin_candidate": (
                dict(self.head_pin_candidate)
                if self.head_pin_candidate is not None
                else None
            ),
            "enforcing_under_lease": self.enforcing_under_lease,
            "authorizes_arm": authorizes_arm,
            "terminal_result": "ready_to_arm" if authorizes_arm else None,
        }


@dataclass
class _PhysicalLedger:
    receipts: list[Mapping[str, Any]]
    offsets: list[int]
    valid_end_offset: int
    residue_start_offset: int
    residue: bytes
    active_intent: Mapping[str, Any] | None
    ledger_id: str
    reasons: set[str]


@dataclass(frozen=True)
class _HistoricalCandidate:
    attempt_id: str
    content_id: str
    artifact_sha256: Mapping[str, str]
    identity_epoch: Mapping[str, Any]
    t1_bindings: Mapping[str, Any]
    capture_wall_time_s: str | None
    exact_bound_lexeme_s: str | None
    custody_sort_key: str
    custody_locator: str


def _frozen_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    frozen: dict[str, Any] = {}
    for key, item in value.items():
        if isinstance(item, Mapping):
            frozen[key] = _frozen_mapping(item)
        elif isinstance(item, list):
            frozen[key] = tuple(
                _frozen_mapping(child) if isinstance(child, Mapping) else child
                for child in item
            )
        else:
            frozen[key] = item
    return MappingProxyType(frozen)


_RECEIPT_KEYS = frozenset(
    {
        "schema_version",
        "ledger_schema",
        "sequence",
        "predecessor_digest",
        "event",
        "attempt_id",
        "content_id",
        "artifact_sha256",
        "identity_epoch",
        "t1_bindings",
        "capture_wall_time_s",
        "exact_bound_lexeme_s",
        "disposition",
        "custody_locator",
        "receipt_digest",
    }
)
_HISTORICAL_IMPORT_INPUT_SHA256_KEY = "historical_import_input_sha256"
_HISTORICAL_IMPORT_INPUT_SHA256_KEYS = frozenset(
    {"disposition_table", "custody_manifest"}
)
_HISTORICAL_IMPORT_RESERVATION_KEYS = (
    _RECEIPT_KEYS | {_HISTORICAL_IMPORT_INPUT_SHA256_KEY}
)
_CHAIN_KEYS = frozenset(
    {
        "schema_version",
        "ledger_schema",
        "sequence",
        "predecessor_digest",
        "event",
        "receipt_digest",
    }
)
_INTENT_KEYS = _CHAIN_KEYS | {
    "ledger_id",
    "base_head",
    "operation_key",
    "target_schema_version",
    "target_event",
    "target_core",
    "target_core_sha256",
    "operation_id",
}
_ABANDONMENT_KEYS = _CHAIN_KEYS | {
    "abandoned_predecessor_sequence",
    "abandoned_predecessor_digest",
    "residue_start_offset",
    "residue_length",
    "residue_sha256",
    "receipt_offset",
    "reason_code",
    "known_operation_id",
    "known_target_core_sha256",
    "actor_type",
    "actor_identity",
    "policy_revision",
    "attestation_reason",
    "legacy_journal",
}
_OPERATION_KEY_KEYS = frozenset(
    {"event", "session_id", "slot", "attempt_id"}
)
_BASE_HEAD_KEYS = frozenset({"sequence", "digest", "byte_offset"})
_LEGACY_JOURNAL_KEYS = frozenset(
    {
        "path",
        "length",
        "sha256",
        "observed_tail_hex",
        "observed_tail_sha256",
    }
)
_SESSION_IDENTITY_KEYS = frozenset(
    {
        "session_id",
        "window_id",
        "plan_id",
        "plan_sha256",
        "evidence_root_id",
        "runs_root",
    }
)
_SESSION_OPEN_KEYS = _CHAIN_KEYS | _SESSION_IDENTITY_KEYS | {"slots"}
_SESSION_SLOT_CLAIM_KEYS = (
    _CHAIN_KEYS | _SESSION_IDENTITY_KEYS | {"slot", "attempt_id", "claim_id"}
)
_SESSION_FINALIZATION_KEYS = (
    _CHAIN_KEYS
    | _SESSION_IDENTITY_KEYS
    | {
        "slot",
        "attempt_id",
        "content_id",
        "artifact_sha256",
        "identity_epoch",
        "t1_bindings",
        "capture_wall_time_s",
        "exact_bound_lexeme_s",
        "disposition",
        "custody_locator",
    }
)
_SESSION_ABORT_KEYS = (
    _CHAIN_KEYS
    | _SESSION_IDENTITY_KEYS
    | {"finalized_slots", "unused_slots", "reason"}
)
_SESSION_SLOT_KEYS = frozenset(
    {
        "attempt_id",
        "custody_locator",
        "identity_epoch",
        "t1_bindings",
        "expected_time_role",
    }
)


def _valid_chain_fields(receipt: Mapping[str, Any], schema: str) -> bool:
    sequence = receipt.get("sequence")
    return (
        receipt.get("schema_version") == schema
        and receipt.get("ledger_schema") == LEDGER_SCHEMA
        and not isinstance(sequence, bool)
        and isinstance(sequence, int)
        and sequence >= 1
        and _is_sha256(receipt.get("predecessor_digest"))
        and _is_sha256(receipt.get("receipt_digest"))
        and receipt.get("receipt_digest") == _receipt_digest(receipt)
    )


def _valid_session_identity(receipt: Mapping[str, Any]) -> bool:
    return (
        all(
            isinstance(receipt.get(field), str) and bool(receipt.get(field))
            for field in (
                "session_id",
                "window_id",
                "plan_id",
                "evidence_root_id",
                "runs_root",
            )
        )
        and _is_sha256(receipt.get("plan_sha256"))
    )


def _valid_session_slot_reservation(slot: object, expected_role: str) -> bool:
    if not isinstance(slot, Mapping) or set(slot) != _SESSION_SLOT_KEYS:
        return False
    epoch = slot.get("identity_epoch")
    t1 = slot.get("t1_bindings")
    return (
        isinstance(slot.get("attempt_id"), str)
        and bool(slot.get("attempt_id"))
        and isinstance(slot.get("custody_locator"), str)
        and bool(slot.get("custody_locator"))
        and slot.get("expected_time_role") == expected_role
        and isinstance(epoch, Mapping)
        and set(epoch) == set(IDENTITY_EPOCH_FIELDS)
        and all(epoch.get(field) not in (None, "") for field in IDENTITY_EPOCH_FIELDS)
        and isinstance(t1, Mapping)
        and set(t1) == set(T1_FIELDS)
        and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
    )


def _valid_session_receipt_shape(receipt: Mapping[str, Any]) -> bool:
    event = receipt.get("event")
    expected_keys = {
        BRACKET_SESSION_OPEN_EVENT: _SESSION_OPEN_KEYS,
        BRACKET_SESSION_SLOT_CLAIM_EVENT: _SESSION_SLOT_CLAIM_KEYS,
        BRACKET_SESSION_FINALIZATION_EVENT: _SESSION_FINALIZATION_KEYS,
        BRACKET_SESSION_ABORT_EVENT: _SESSION_ABORT_KEYS,
    }.get(event)
    if (
        expected_keys is None
        or set(receipt) != expected_keys
        or not _valid_chain_fields(receipt, BRACKET_SESSION_SCHEMA)
        or not _valid_session_identity(receipt)
    ):
        return False
    if event == BRACKET_SESSION_OPEN_EVENT:
        slots = receipt.get("slots")
        return (
            isinstance(slots, Mapping)
            and set(slots) == set(BRACKET_SESSION_SLOTS)
            and all(
                _valid_session_slot_reservation(slots.get(role), role)
                for role in BRACKET_SESSION_SLOTS
            )
            and slots["pre"]["attempt_id"] != slots["post"]["attempt_id"]
        )
    if event == BRACKET_SESSION_SLOT_CLAIM_EVENT:
        return (
            receipt.get("slot") in BRACKET_SESSION_SLOTS
            and isinstance(receipt.get("attempt_id"), str)
            and bool(receipt.get("attempt_id"))
            and isinstance(receipt.get("claim_id"), str)
            and bool(receipt.get("claim_id"))
        )
    if event == BRACKET_SESSION_ABORT_EVENT:
        finalized = receipt.get("finalized_slots")
        unused = receipt.get("unused_slots")
        reason = receipt.get("reason")
        return (
            isinstance(finalized, Sequence)
            and not isinstance(finalized, (str, bytes))
            and isinstance(unused, Sequence)
            and not isinstance(unused, (str, bytes))
            and all(slot in BRACKET_SESSION_SLOTS for slot in (*finalized, *unused))
            and len(set((*finalized, *unused))) == len(finalized) + len(unused)
            and set((*finalized, *unused)) == set(BRACKET_SESSION_SLOTS)
            and isinstance(reason, str)
            and bool(reason)
        )
    disposition = receipt.get("disposition")
    artifacts = receipt.get("artifact_sha256")
    epoch = receipt.get("identity_epoch")
    t1 = receipt.get("t1_bindings")
    capture = receipt.get("capture_wall_time_s")
    bound = receipt.get("exact_bound_lexeme_s")
    content_id = receipt.get("content_id")
    if (
        receipt.get("slot") not in BRACKET_SESSION_SLOTS
        or not isinstance(receipt.get("attempt_id"), str)
        or not receipt.get("attempt_id")
        or disposition not in FINAL_DISPOSITIONS
        or not isinstance(receipt.get("custody_locator"), str)
        or not isinstance(artifacts, Mapping)
        or any(
            not isinstance(name, str) or not name or not _is_sha256(digest)
            for name, digest in artifacts.items()
        )
        or not isinstance(epoch, Mapping)
        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
        or not isinstance(t1, Mapping)
        or set(t1) != set(T1_FIELDS)
        or (capture is not None and not isinstance(capture, str))
        or (bound is not None and not isinstance(bound, str))
        or (content_id is not None and not _is_sha256(content_id))
    ):
        return False
    if disposition == "abandoned":
        return content_id == content_id_from_artifact_hashes(artifacts)
    return (
        content_id is not None
        and content_id_from_artifact_hashes(artifacts) == content_id
        and bool(receipt.get("custody_locator"))
        and all(epoch.get(field) not in (None, "") for field in IDENTITY_EPOCH_FIELDS)
        and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
        and capture is not None
    )


def _target_core(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Return semantic receipt content, excluding chain-placement fields."""

    return {
        key: _jsonable(value)
        for key, value in receipt.items()
        if key not in {"sequence", "predecessor_digest", "receipt_digest"}
    }


def _operation_key_for_core(target_core: Mapping[str, Any]) -> dict[str, Any]:
    event = target_core.get("event")
    schema = target_core.get("schema_version")
    session_id = target_core.get("session_id") if schema == BRACKET_SESSION_SCHEMA else None
    slot = target_core.get("slot") if schema == BRACKET_SESSION_SCHEMA else None
    attempt_id = target_core.get("attempt_id")
    if event == BRACKET_SESSION_OPEN_EVENT:
        attempt_id = None
    if event == BRACKET_SESSION_ABORT_EVENT:
        slot = None
        attempt_id = None
    return {
        "event": event,
        "session_id": session_id,
        "slot": slot,
        "attempt_id": attempt_id,
    }


def _valid_operation_key(value: object) -> bool:
    if not isinstance(value, Mapping) or set(value) != _OPERATION_KEY_KEYS:
        return False
    return (
        isinstance(value.get("event"), str)
        and bool(value.get("event"))
        and all(
            item is None or isinstance(item, str) and bool(item)
            for item in (
                value.get("session_id"),
                value.get("slot"),
                value.get("attempt_id"),
            )
        )
    )


def _valid_legacy_journal_metadata(value: object) -> bool:
    if not isinstance(value, Mapping) or set(value) != _LEGACY_JOURNAL_KEYS:
        return False
    try:
        observed_tail = bytes.fromhex(str(value.get("observed_tail_hex", "")))
    except ValueError:
        return False
    length = value.get("length")
    return (
        isinstance(value.get("path"), str)
        and bool(value["path"])
        and isinstance(length, int)
        and not isinstance(length, bool)
        and length >= len(observed_tail)
        and len(observed_tail) <= 64
        and _is_sha256(value.get("sha256"))
        and _is_sha256(value.get("observed_tail_sha256"))
        and hashlib.sha256(observed_tail).hexdigest()
        == value["observed_tail_sha256"]
    )


def _valid_control_receipt_shape(receipt: Mapping[str, Any]) -> bool:
    if not _valid_chain_fields(receipt, CONTROL_SCHEMA):
        return False
    event = receipt.get("event")
    if event == APPEND_INTENT_EVENT:
        base = receipt.get("base_head")
        operation_key = receipt.get("operation_key")
        target_core = receipt.get("target_core")
        if (
            set(receipt) != _INTENT_KEYS
            or not _is_sha256(receipt.get("ledger_id"))
            or not isinstance(base, Mapping)
            or set(base) != _BASE_HEAD_KEYS
            or isinstance(base.get("sequence"), bool)
            or not isinstance(base.get("sequence"), int)
            or int(base.get("sequence", -1)) < 0
            or not _is_sha256(base.get("digest"))
            or isinstance(base.get("byte_offset"), bool)
            or not isinstance(base.get("byte_offset"), int)
            or int(base.get("byte_offset", -1)) < 0
            or not _valid_operation_key(operation_key)
            or not isinstance(target_core, Mapping)
            or not isinstance(receipt.get("target_schema_version"), str)
            or not isinstance(receipt.get("target_event"), str)
            or not _is_sha256(receipt.get("target_core_sha256"))
            or not _is_sha256(receipt.get("operation_id"))
        ):
            return False
        return (
            target_core.get("schema_version") == receipt["target_schema_version"]
            and target_core.get("event") == receipt["target_event"]
            and _operation_key_for_core(target_core) == dict(operation_key)
            and canonical_sha256(target_core) == receipt["target_core_sha256"]
            and set(target_core).isdisjoint(
                {"sequence", "predecessor_digest", "receipt_digest"}
            )
            and receipt["operation_id"] == _operation_id(
                ledger_id=str(receipt["ledger_id"]),
                base_head=base,
                operation_key=operation_key,
                target_core_sha256=str(receipt["target_core_sha256"]),
            )
        )
    if event != ABANDONMENT_EVENT or set(receipt) != _ABANDONMENT_KEYS:
        return False
    legacy = receipt.get("legacy_journal")
    return (
        isinstance(receipt.get("abandoned_predecessor_sequence"), int)
        and not isinstance(receipt.get("abandoned_predecessor_sequence"), bool)
        and int(receipt["abandoned_predecessor_sequence"]) >= 0
        and _is_sha256(receipt.get("abandoned_predecessor_digest"))
        and isinstance(receipt.get("residue_start_offset"), int)
        and not isinstance(receipt.get("residue_start_offset"), bool)
        and int(receipt["residue_start_offset"]) >= 0
        and isinstance(receipt.get("residue_length"), int)
        and not isinstance(receipt.get("residue_length"), bool)
        and int(receipt["residue_length"]) >= 0
        and _is_sha256(receipt.get("residue_sha256"))
        and isinstance(receipt.get("receipt_offset"), int)
        and not isinstance(receipt.get("receipt_offset"), bool)
        and int(receipt["receipt_offset"]) >= 0
        and isinstance(receipt.get("reason_code"), str)
        and bool(receipt["reason_code"])
        and (
            receipt.get("known_operation_id") is None
            or _is_sha256(receipt.get("known_operation_id"))
        )
        and (
            receipt.get("known_target_core_sha256") is None
            or _is_sha256(receipt.get("known_target_core_sha256"))
        )
        and receipt.get("actor_type") in {"engine", "operator"}
        and isinstance(receipt.get("actor_identity"), str)
        and bool(receipt["actor_identity"])
        and receipt.get("policy_revision") == APPEND_POLICY_REVISION
        and isinstance(receipt.get("attestation_reason"), str)
        and bool(receipt["attestation_reason"])
        and (
            legacy is None
            or _valid_legacy_journal_metadata(legacy)
        )
    )


def _valid_receipt_shape(receipt: object) -> bool:
    if not isinstance(receipt, Mapping):
        return False
    if receipt.get("schema_version") == CONTROL_SCHEMA:
        return _valid_control_receipt_shape(receipt)
    if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
        return _valid_session_receipt_shape(receipt)
    sequence = receipt.get("sequence")
    event = receipt.get("event")
    expected_keys = (
        _HISTORICAL_IMPORT_RESERVATION_KEYS
        if event == HISTORICAL_IMPORT_RESERVATION_EVENT
        else _RECEIPT_KEYS
    )
    if set(receipt) != expected_keys:
        return False
    disposition = receipt.get("disposition")
    artifacts = receipt.get("artifact_sha256")
    epoch = receipt.get("identity_epoch")
    t1 = receipt.get("t1_bindings")
    capture = receipt.get("capture_wall_time_s")
    bound = receipt.get("exact_bound_lexeme_s")
    if (
        receipt.get("schema_version") != RECEIPT_SCHEMA
        or receipt.get("ledger_schema") != LEDGER_SCHEMA
        or isinstance(sequence, bool)
        or not isinstance(sequence, int)
        or sequence < 1
        or not _is_sha256(receipt.get("predecessor_digest"))
        or event
        not in {
            "reservation",
            "finalization",
            HISTORICAL_IMPORT_RESERVATION_EVENT,
            HISTORICAL_IMPORT_FINALIZATION_EVENT,
        }
        or not isinstance(receipt.get("attempt_id"), str)
        or not receipt.get("attempt_id")
        or disposition not in ALL_DISPOSITIONS
        or not isinstance(receipt.get("custody_locator"), str)
        or not isinstance(artifacts, Mapping)
        or any(
            not isinstance(name, str) or not name or not _is_sha256(digest)
            for name, digest in artifacts.items()
        )
        or not isinstance(epoch, Mapping)
        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
        or not isinstance(t1, Mapping)
        or set(t1) != set(T1_FIELDS)
        or (capture is not None and not isinstance(capture, str))
        or (bound is not None and not isinstance(bound, str))
        or not _is_sha256(receipt.get("receipt_digest"))
        or receipt.get("receipt_digest") != _receipt_digest(receipt)
    ):
        return False
    content_id = receipt.get("content_id")
    if content_id is not None and not _is_sha256(content_id):
        return False
    if event in {"reservation", HISTORICAL_IMPORT_RESERVATION_EVENT}:
        historical_input_sha256 = receipt.get(
            _HISTORICAL_IMPORT_INPUT_SHA256_KEY
        )
        return (
            disposition == "pending"
            and content_id is None
            and not artifacts
            and capture is None
            and bound is None
            and all(
                epoch.get(field) not in (None, "")
                for field in IDENTITY_EPOCH_FIELDS
            )
            and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
            and (
                event != HISTORICAL_IMPORT_RESERVATION_EVENT
                or isinstance(historical_input_sha256, Mapping)
                and set(historical_input_sha256)
                == _HISTORICAL_IMPORT_INPUT_SHA256_KEYS
                and all(
                    _is_sha256(historical_input_sha256.get(name))
                    for name in _HISTORICAL_IMPORT_INPUT_SHA256_KEYS
                )
            )
        )
    if disposition not in FINAL_DISPOSITIONS:
        return False
    if disposition == "abandoned":
        # R1 retains the terminal writer state as ``abandoned`` while R2
        # classifies it as unresolved.  When canonical primary bytes exist,
        # preserve their authentic content identity; a partial/no-content
        # attempt remains representable with a null content id.
        return content_id == content_id_from_artifact_hashes(artifacts)
    if (
        content_id is None
        or content_id_from_artifact_hashes(artifacts) != content_id
        or not receipt.get("custody_locator")
        or any(epoch.get(field) in (None, "") for field in IDENTITY_EPOCH_FIELDS)
        or any(t1.get(field) in (None, "") for field in T1_FIELDS)
        or capture is None
    ):
        return False
    return True


def _head_pin(value: object) -> tuple[int, str] | None:
    if not isinstance(value, Mapping) or set(value) != {
        "sequence",
        "head_digest",
        "ledger_schema",
    }:
        return None
    sequence = value.get("sequence")
    digest = value.get("head_digest")
    if (
        value.get("ledger_schema") != LEDGER_SCHEMA
        or isinstance(sequence, bool)
        or not isinstance(sequence, int)
        or sequence < 0
        or not _is_sha256(digest)
        or (sequence == 0 and digest != GENESIS_DIGEST)
    ):
        return None
    return sequence, str(digest)


def _committed_pin_bytes(path: Path, repo_root: Path) -> bytes | None:
    try:
        relative = Path(path).resolve().relative_to(Path(repo_root).resolve()).as_posix()
    except (OSError, ValueError):
        return None
    try:
        completed = subprocess.run(
            ["git", "show", f"HEAD:{relative}"],
            cwd=repo_root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout


def _legacy_append_journal_path(ledger_path: Path) -> Path:
    ledger = Path(ledger_path)
    return ledger.with_name(f"{ledger.name}.append-journal")


def _operation_id(
    *,
    ledger_id: str,
    base_head: Mapping[str, Any],
    operation_key: Mapping[str, Any],
    target_core_sha256: str,
) -> str:
    return canonical_sha256(
        {
            "ledger_id": ledger_id,
            "base_head": dict(base_head),
            "operation_key": dict(operation_key),
            "target_core_sha256": target_core_sha256,
        }
    )


def _derived_ledger_id(receipts: Sequence[Mapping[str, Any]]) -> str:
    for receipt in receipts:
        if receipt.get("event") == APPEND_INTENT_EVENT:
            return str(receipt["ledger_id"])
    anchor_sequence = 1 if receipts else 0
    anchor_digest = (
        str(receipts[0]["receipt_digest"]) if receipts else GENESIS_DIGEST
    )
    return canonical_sha256(
        {
            "ledger_schema": LEDGER_SCHEMA,
            "lineage_anchor_sequence": anchor_sequence,
            "lineage_anchor_digest": anchor_digest,
        }
    )


def _intent_target_receipt(
    intent: Mapping[str, Any], *, sequence: int, predecessor_digest: str
) -> dict[str, Any]:
    target = dict(intent["target_core"])
    target["sequence"] = sequence
    target["predecessor_digest"] = predecessor_digest
    target["receipt_digest"] = _receipt_digest(target)
    return target


def _known_intent_matches(
    abandonment: Mapping[str, Any], active_intent: Mapping[str, Any] | None
) -> bool:
    if active_intent is None:
        return (
            abandonment.get("known_operation_id") is None
            and abandonment.get("known_target_core_sha256") is None
        )
    return (
        abandonment.get("known_operation_id") == active_intent.get("operation_id")
        and abandonment.get("known_target_core_sha256")
        == active_intent.get("target_core_sha256")
    )


def _control_state_admits(
    value: Mapping[str, Any],
    *,
    receipts: Sequence[Mapping[str, Any]],
    offset: int,
    active_intent: Mapping[str, Any] | None,
    protocol_active: bool,
    expected_sequence: int,
    predecessor_digest: str,
) -> tuple[bool, Mapping[str, Any] | None]:
    event = value.get("event")
    if event == APPEND_INTENT_EVENT:
        base = value["base_head"]
        target = _intent_target_receipt(
            value,
            sequence=expected_sequence + 1,
            predecessor_digest=str(value["receipt_digest"]),
        )
        target_shape_valid = _valid_receipt_shape(target)
        valid = (
            active_intent is None
            and value["ledger_id"] == _derived_ledger_id(receipts)
            and base["sequence"] == expected_sequence - 1
            and base["digest"] == predecessor_digest
            and base["byte_offset"] == offset
            and not any(
                receipt.get("event") == APPEND_INTENT_EVENT
                and dict(receipt["operation_key"]) == dict(value["operation_key"])
                for receipt in receipts
            )
            # A hostile but internally authenticated intent may commit a
            # malformed target. Admit the intent as durable protocol state so
            # repair reaches the typed INTENT_TARGET_MALFORMED backstop rather
            # than degrading it to anonymous tail residue. Valid targets still
            # undergo the normal semantic-transition check.
            and (
                not target_shape_valid
                or _target_state_transition_is_valid(receipts, target)
            )
        )
        return valid, value if valid else active_intent
    if event == ABANDONMENT_EVENT:
        malformed_active_intent = False
        if active_intent is not None:
            active_target = _intent_target_receipt(
                active_intent,
                sequence=expected_sequence,
                predecessor_digest=predecessor_digest,
            )
            malformed_active_intent = not _valid_receipt_shape(active_target)
        valid = (
            value["abandoned_predecessor_sequence"] == expected_sequence - 1
            and value["abandoned_predecessor_digest"] == predecessor_digest
            and value["residue_length"] == 0
            and value["residue_start_offset"] == offset
            and value["receipt_offset"] == offset
            and value["residue_sha256"] == hashlib.sha256(b"").hexdigest()
            and _known_intent_matches(value, active_intent)
            and (
                value.get("legacy_journal") is not None
                or malformed_active_intent
            )
        )
        if valid and active_intent is not None:
            # An authenticated malformed-target intent is admitted only as
            # residue.  Its governed abandonment closes the quarantine; a
            # valid executable intent remains irrevocable.
            if malformed_active_intent:
                return True, None
        return valid, active_intent
    if active_intent is None:
        return not protocol_active, None
    target = _intent_target_receipt(
        active_intent,
        sequence=expected_sequence,
        predecessor_digest=predecessor_digest,
    )
    return value == target, None if value == target else active_intent


def _decode_line(raw: bytes, start: int, end: int) -> Mapping[str, Any] | None:
    try:
        value = json.loads(raw[start:end].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, Mapping) else None


def _matching_abandonment_bridge(
    raw: bytes,
    *,
    residue_start: int,
    expected_sequence: int,
    predecessor_digest: str,
    active_intent: Mapping[str, Any] | None,
) -> tuple[Mapping[str, Any], int, int] | None:
    candidate = raw.find(b"\n", residue_start)
    while candidate >= 0 and candidate + 1 < len(raw):
        receipt_offset = candidate + 1
        line_end = raw.find(b"\n", receipt_offset)
        if line_end < 0:
            return None
        value = _decode_line(raw, receipt_offset, line_end)
        if (
            value is not None
            and _valid_control_receipt_shape(value)
            and value.get("event") == ABANDONMENT_EVENT
            and value.get("sequence") == expected_sequence
            and value.get("predecessor_digest") == predecessor_digest
            and value.get("receipt_offset") == receipt_offset
            and value.get("residue_start_offset") == residue_start
            and value.get("abandoned_predecessor_sequence")
            == expected_sequence - 1
            and value.get("abandoned_predecessor_digest") == predecessor_digest
            and _known_intent_matches(value, active_intent)
        ):
            residue_end = residue_start + int(value["residue_length"])
            delimiter = raw[residue_end:receipt_offset]
            residue = raw[residue_start:residue_end]
            if (
                residue_end <= receipt_offset
                and delimiter in {b"", b"\n"}
                and hashlib.sha256(residue).hexdigest() == value["residue_sha256"]
            ):
                return value, receipt_offset, line_end + 1
        candidate = raw.find(b"\n", candidate + 1)
    return None


def _scan_physical_ledger(raw: bytes) -> _PhysicalLedger:
    receipts: list[Mapping[str, Any]] = []
    offsets: list[int] = []
    reasons: set[str] = set()
    offset = 0
    predecessor = GENESIS_DIGEST
    expected_sequence = 1
    active_intent: Mapping[str, Any] | None = None
    protocol_active = False
    seen_digests: set[str] = set()
    terminal_failure = "calibration_ledger_malformed"
    while offset < len(raw):
        line_end = raw.find(b"\n", offset)
        value = _decode_line(raw, offset, line_end) if line_end >= 0 else None
        shape_valid = value is not None and _valid_receipt_shape(value)
        chain_valid = bool(
            shape_valid
            and value["sequence"] == expected_sequence
            and value["predecessor_digest"] == predecessor
            and value["receipt_digest"] not in seen_digests
        )
        state_valid = False
        next_intent = active_intent
        if chain_valid:
            state_valid, next_intent = _control_state_admits(
                value,
                receipts=receipts,
                offset=offset,
                active_intent=active_intent,
                protocol_active=protocol_active,
                expected_sequence=expected_sequence,
                predecessor_digest=predecessor,
            )
        if chain_valid and state_valid:
            receipts.append(value)
            offsets.append(offset)
            predecessor = str(value["receipt_digest"])
            seen_digests.add(predecessor)
            expected_sequence += 1
            active_intent = next_intent
            protocol_active = (
                protocol_active or value.get("schema_version") == CONTROL_SCHEMA
            )
            offset = line_end + 1
            continue
        if shape_valid and not chain_valid:
            terminal_failure = "calibration_ledger_chain_conflict"
        elif chain_valid and not state_valid:
            terminal_failure = (
                "calibration_ledger_ungoverned_business"
                if protocol_active
                and active_intent is None
                and value.get("schema_version") != CONTROL_SCHEMA
                else "calibration_ledger_operation_conflict"
            )
        bridge = _matching_abandonment_bridge(
            raw,
            residue_start=offset,
            expected_sequence=expected_sequence,
            predecessor_digest=predecessor,
            active_intent=active_intent,
        )
        if bridge is None:
            break
        abandonment, receipt_offset, next_offset = bridge
        receipts.append(abandonment)
        offsets.append(receipt_offset)
        predecessor = str(abandonment["receipt_digest"])
        seen_digests.add(predecessor)
        expected_sequence += 1
        protocol_active = True
        offset = next_offset
        terminal_failure = "calibration_ledger_malformed"
    residue = raw[offset:]
    if residue:
        reasons.update({terminal_failure, "calibration_ledger_recovery_required"})
    elif active_intent is not None:
        reasons.add("calibration_ledger_recovery_required")
    return _PhysicalLedger(
        receipts=receipts,
        offsets=offsets,
        valid_end_offset=offset,
        residue_start_offset=offset,
        residue=residue,
        active_intent=active_intent,
        ledger_id=_derived_ledger_id(receipts),
        reasons=reasons,
    )


def _parse_ledger(raw: bytes) -> tuple[list[Mapping[str, Any]], set[str]]:
    physical = _scan_physical_ledger(raw)
    return physical.receipts, physical.reasons


def _observation_from_receipt(
    receipt: Mapping[str, Any],
    *,
    observation_kind: str,
    session: Mapping[str, Any] | None = None,
) -> LedgerObservation:
    content_id = receipt.get("content_id")
    return LedgerObservation(
        sequence=int(receipt["sequence"]),
        receipt_digest=str(receipt["receipt_digest"]),
        attempt_id=str(receipt["attempt_id"]),
        content_id=str(content_id) if isinstance(content_id, str) else None,
        artifact_sha256=MappingProxyType(dict(receipt["artifact_sha256"])),
        identity_epoch=MappingProxyType(dict(receipt["identity_epoch"])),
        t1_bindings=MappingProxyType(dict(receipt["t1_bindings"])),
        capture_wall_time_s=receipt.get("capture_wall_time_s"),
        exact_bound_lexeme_s=receipt.get("exact_bound_lexeme_s"),
        disposition=str(receipt["disposition"]),
        custody_locator=str(receipt["custody_locator"]),
        observation_kind=observation_kind,
        bracket_session_id=(str(session["session_id"]) if session else None),
        bracket_slot=(str(receipt["slot"]) if session else None),
        bracket_window_id=(str(session["window_id"]) if session else None),
        bracket_plan_id=(str(session["plan_id"]) if session else None),
        bracket_plan_sha256=(str(session["plan_sha256"]) if session else None),
        bracket_evidence_root_id=(
            str(session["evidence_root_id"]) if session else None
        ),
        bracket_runs_root=(str(session["runs_root"]) if session else None),
    )


def _session_identity_matches(
    receipt: Mapping[str, Any], open_receipt: Mapping[str, Any]
) -> bool:
    return all(receipt.get(field) == open_receipt.get(field) for field in _SESSION_IDENTITY_KEYS)


def _bracket_sessions_and_observations(
    receipts: Sequence[Mapping[str, Any]],
) -> tuple[list[CalibrationBracketSession], list[LedgerObservation], set[str]]:
    states: dict[str, dict[str, Any]] = {}
    claimed_attempts: set[str] = set()
    reasons: set[str] = set()
    for receipt in receipts:
        if receipt.get("schema_version") != BRACKET_SESSION_SCHEMA:
            continue
        event = receipt["event"]
        session_id = str(receipt["session_id"])
        if event == BRACKET_SESSION_OPEN_EVENT:
            slots = receipt["slots"]
            attempt_ids = {str(slots[role]["attempt_id"]) for role in BRACKET_SESSION_SLOTS}
            if session_id in states or attempt_ids & claimed_attempts:
                reasons.add("calibration_ledger_bracket_session_conflict")
                continue
            claimed_attempts.update(attempt_ids)
            states[session_id] = {
                "open": receipt,
                "claims": {},
                "finals": {},
                "abort": None,
            }
            continue
        state = states.get(session_id)
        if state is None:
            reasons.add("calibration_ledger_bracket_session_conflict")
            continue
        open_receipt = state["open"]
        if not _session_identity_matches(receipt, open_receipt):
            reasons.add("calibration_ledger_bracket_session_conflict")
            continue
        claims = state["claims"]
        finals = state["finals"]
        if event == BRACKET_SESSION_SLOT_CLAIM_EVENT:
            slot = str(receipt["slot"])
            expected_slot = (
                BRACKET_SESSION_SLOTS[len(finals)] if len(finals) < 2 else None
            )
            reserved = open_receipt["slots"].get(slot)
            if (
                state["abort"] is not None
                or slot != expected_slot
                or slot in claims
                or slot in finals
                or not isinstance(reserved, Mapping)
                or receipt["attempt_id"] != reserved["attempt_id"]
            ):
                reasons.add("calibration_ledger_bracket_session_conflict")
                continue
            claims[slot] = receipt
            continue
        if event == BRACKET_SESSION_FINALIZATION_EVENT:
            slot = str(receipt["slot"])
            expected_slot = BRACKET_SESSION_SLOTS[len(finals)] if len(finals) < 2 else None
            reserved = open_receipt["slots"].get(slot)
            if (
                state["abort"] is not None
                or slot != expected_slot
                or slot in finals
                or not isinstance(reserved, Mapping)
                or receipt["attempt_id"] != reserved["attempt_id"]
                or receipt["custody_locator"] != reserved["custody_locator"]
                or dict(receipt["identity_epoch"]) != dict(reserved["identity_epoch"])
                or dict(receipt["t1_bindings"]) != dict(reserved["t1_bindings"])
            ):
                reasons.add("calibration_ledger_bracket_session_conflict")
                continue
            finals[slot] = receipt
            continue
        finalized_slots = list(finals)
        unused_slots = [slot for slot in BRACKET_SESSION_SLOTS if slot not in finals]
        if (
            event != BRACKET_SESSION_ABORT_EVENT
            or state["abort"] is not None
            or len(finals) == 2
            or receipt["finalized_slots"] != finalized_slots
            or receipt["unused_slots"] != unused_slots
        ):
            reasons.add("calibration_ledger_bracket_session_conflict")
            continue
        state["abort"] = receipt

    sessions: list[CalibrationBracketSession] = []
    completed_observations: list[LedgerObservation] = []
    for session_id, state in sorted(
        states.items(), key=lambda item: int(item[1]["open"]["sequence"])
    ):
        open_receipt = state["open"]
        finals = state["finals"]
        abort = state["abort"]
        if abort is not None:
            session_state = "aborted"
        elif len(finals) == 2:
            session_state = "finalized"
        else:
            session_state = "open"
            reasons.add("calibration_ledger_bracket_session_open")
        finalized_observations = {
            slot: _observation_from_receipt(
                receipt,
                observation_kind=(
                    "bracket-session-finalized"
                    if session_state == "finalized"
                    else "bracket-session-aborted"
                ),
                session=open_receipt,
            )
            for slot, receipt in finals.items()
        }
        # R2's observation universe contains finalized evidence from every
        # terminal governed session, including a PRE whose session later
        # aborts.  An open session is intentionally withheld until its state
        # is governed-terminal; candidate discovery applies the narrower
        # finalized-session rule separately.
        if session_state in {"finalized", "aborted"}:
            completed_observations.extend(
                finalized_observations[slot]
                for slot in BRACKET_SESSION_SLOTS
                if slot in finalized_observations
            )
        sessions.append(
            CalibrationBracketSession(
                session_id=session_id,
                window_id=str(open_receipt["window_id"]),
                plan_id=str(open_receipt["plan_id"]),
                plan_sha256=str(open_receipt["plan_sha256"]),
                evidence_root_id=str(open_receipt["evidence_root_id"]),
                runs_root=str(open_receipt["runs_root"]),
                capability_receipt_digest=str(open_receipt["receipt_digest"]),
                capability_sequence=int(open_receipt["sequence"]),
                slot_attempt_ids=MappingProxyType(
                    {
                        slot: str(open_receipt["slots"][slot]["attempt_id"])
                        for slot in BRACKET_SESSION_SLOTS
                    }
                ),
                state=session_state,
                finalized_slots=MappingProxyType(finalized_observations),
                abort_receipt_digest=(
                    str(abort["receipt_digest"]) if abort is not None else None
                ),
                abort_reason=(str(abort["reason"]) if abort is not None else None),
            )
        )
    return sessions, completed_observations, reasons


def _attempts_and_observations(
    receipts: Sequence[Mapping[str, Any]],
) -> tuple[list[LedgerObservation], list[CalibrationBracketSession], set[str]]:
    pending: dict[str, Mapping[str, Any]] = {}
    finalized: dict[str, Mapping[str, Any]] = {}
    reasons: set[str] = set()
    for receipt in receipts:
        if receipt.get("schema_version") == CONTROL_SCHEMA:
            continue
        if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
            continue
        attempt_id = str(receipt["attempt_id"])
        if receipt["event"] in {
            "reservation",
            HISTORICAL_IMPORT_RESERVATION_EVENT,
        }:
            if attempt_id in pending or attempt_id in finalized:
                reasons.add("calibration_ledger_attempt_conflict")
            else:
                pending[attempt_id] = receipt
            continue
        reservation = pending.get(attempt_id)
        expected_final_event = (
            HISTORICAL_IMPORT_FINALIZATION_EVENT
            if reservation is not None
            and reservation["event"] == HISTORICAL_IMPORT_RESERVATION_EVENT
            else "finalization"
        )
        if (
            reservation is None
            or attempt_id in finalized
            or receipt["event"] != expected_final_event
        ):
            reasons.add("calibration_ledger_attempt_conflict")
        else:
            finalized[attempt_id] = receipt
    if set(pending) - set(finalized):
        reasons.add("calibration_ledger_pending")

    observations: list[LedgerObservation] = []
    content_classification: dict[str, tuple[str, tuple[tuple[str, Any], ...]]] = {}
    for attempt_id, receipt in sorted(
        finalized.items(), key=lambda item: int(item[1]["sequence"])
    ):
        content_id = receipt.get("content_id")
        epoch = dict(receipt["identity_epoch"])
        if isinstance(content_id, str):
            classification = (
                (
                    "unresolved"
                    if receipt["disposition"] == "abandoned"
                    else str(receipt["disposition"])
                ),
                tuple((field, epoch.get(field)) for field in IDENTITY_EPOCH_FIELDS),
            )
            previous = content_classification.get(content_id)
            if previous is not None and previous != classification:
                reasons.add("calibration_ledger_content_conflict")
            content_classification[content_id] = classification
        observations.append(
            _observation_from_receipt(
                receipt,
                observation_kind=(
                    "historical-import"
                    if receipt["event"] == HISTORICAL_IMPORT_FINALIZATION_EVENT
                    else "live-capture"
                ),
            )
        )
    sessions, session_observations, session_reasons = (
        _bracket_sessions_and_observations(receipts)
    )
    reasons.update(session_reasons)
    session_attempt_ids = {
        attempt_id
        for session in sessions
        for attempt_id in session.slot_attempt_ids.values()
    }
    if set(pending) & session_attempt_ids:
        reasons.add("calibration_ledger_bracket_session_conflict")
    observations.extend(session_observations)
    content_classification.clear()
    classification_observations = list(observations)
    visible_attempts = {observation.attempt_id for observation in observations}
    classification_observations.extend(
        observation
        for session in sessions
        for observation in session.finalized_slots.values()
        if observation.attempt_id not in visible_attempts
    )
    for observation in classification_observations:
        if observation.content_id is None:
            continue
        classification = (
            observation.classification_disposition,
            tuple(
                (field, observation.identity_epoch.get(field))
                for field in IDENTITY_EPOCH_FIELDS
            ),
        )
        previous = content_classification.get(observation.content_id)
        if previous is not None and previous != classification:
            reasons.add("calibration_ledger_content_conflict")
        content_classification[observation.content_id] = classification
    observations.sort(key=lambda observation: observation.sequence)
    return observations, sessions, reasons


def _target_state_transition_is_valid(
    receipts: Sequence[Mapping[str, Any]], target: Mapping[str, Any]
) -> bool:
    fatal = {
        "calibration_ledger_attempt_conflict",
        "calibration_ledger_bracket_session_conflict",
        "calibration_ledger_content_conflict",
    }
    _observations, _sessions, before = _attempts_and_observations(receipts)
    _observations, _sessions, after = _attempts_and_observations(
        [*receipts, target]
    )
    return not ((after & fatal) - (before & fatal))


def _custody_reasons(
    observations: Sequence[LedgerObservation], repo_root: Path
) -> set[str]:
    for observation in observations:
        if not observation.artifact_sha256:
            if observation.disposition == "abandoned":
                continue
            return {"calibration_ledger_custody_invalid"}
        root = Path(observation.custody_locator)
        if not root.is_absolute():
            root = Path(repo_root) / root
        for relative, expected in observation.artifact_sha256.items():
            path = root / relative
            try:
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                return {"calibration_ledger_custody_invalid"}
            if actual != expected:
                return {"calibration_ledger_custody_invalid"}
    return set()


def load_calibration_ledger_snapshot(
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
    *,
    baseline_sequence: int | None = None,
    baseline_digest: str | None = None,
    require_committed_pin: bool = True,
    verify_custody: bool = True,
    repo_root: Path = REPO_ROOT,
) -> CalibrationLedgerSnapshot:
    """Load, authenticate, and freeze exactly one ledger snapshot.

    A proper physical prefix of the pin is classified explicitly as rollback;
    any other physical/pinned disagreement is a stale-head mismatch.  The
    baseline must occur at its exact sequence in the same complete chain.
    This closes workflow omission, unregistered evidence, and rollback or
    stale-head consumption; it does not defend against a malicious trusted
    writer or a rewrite of both Git and the full ledger history.
    """

    ledger_path = Path(ledger_path)
    head_pin_path = Path(head_pin_path)
    reasons: set[str] = set()
    try:
        pin_raw = head_pin_path.read_bytes()
        pin_value = json.loads(pin_raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        pin_raw = b""
        pin_value = None
    pin = _head_pin(pin_value)
    if pin is None:
        reasons.add("calibration_ledger_malformed")
        pinned_sequence, pinned_digest = 0, GENESIS_DIGEST
    else:
        pinned_sequence, pinned_digest = pin
    try:
        raw = ledger_path.read_bytes()
    except OSError:
        raw = b""
        if pinned_sequence > 0:
            reasons.add("calibration_ledger_missing")
    genesis_development_bootstrap = (
        pinned_sequence == 0
        and pinned_digest == GENESIS_DIGEST
        and not raw
        and not ledger_path.exists()
    )
    if (
        require_committed_pin
        # The checked-in fixture starts at genesis.  Before its first commit,
        # an absent physical ledger cannot license a claim (there are no
        # endpoints); permitting this development-only empty view avoids a
        # circular "commit before tests" bootstrap. Any physical byte or any
        # non-genesis pin remains strictly commit-authenticated.
        and not genesis_development_bootstrap
        and _committed_pin_bytes(head_pin_path, repo_root) != pin_raw
    ):
        reasons.add("calibration_ledger_head_uncommitted")
    receipts, parse_reasons = _parse_ledger(raw)
    reasons.update(parse_reasons)
    physical_sequence = len(receipts)
    physical_digest = (
        str(receipts[-1]["receipt_digest"]) if receipts else GENESIS_DIGEST
    )
    if (physical_sequence, physical_digest) != (pinned_sequence, pinned_digest):
        if physical_sequence < pinned_sequence:
            reasons.add("calibration_ledger_rollback")
        else:
            reasons.add("calibration_ledger_head_mismatch")
    if baseline_sequence is not None or baseline_digest is not None:
        if (
            isinstance(baseline_sequence, bool)
            or not isinstance(baseline_sequence, int)
            or baseline_sequence < 0
            or not _is_sha256(baseline_digest)
        ):
            reasons.add("calibration_ledger_baseline_missing")
        else:
            in_chain = (
                baseline_digest == GENESIS_DIGEST
                if baseline_sequence == 0
                else baseline_sequence <= len(receipts)
                and receipts[baseline_sequence - 1]["receipt_digest"]
                == baseline_digest
            )
            if not in_chain or baseline_sequence > pinned_sequence:
                reasons.add("calibration_ledger_baseline_missing")
    observations, bracket_sessions, state_reasons = _attempts_and_observations(
        receipts
    )
    reasons.update(state_reasons)
    if verify_custody:
        custody_observations = list(observations)
        custody_attempt_ids = {observation.attempt_id for observation in observations}
        for session in bracket_sessions:
            custody_observations.extend(
                observation
                for observation in session.finalized_slots.values()
                if observation.attempt_id not in custody_attempt_ids
            )
        reasons.update(_custody_reasons(custody_observations, repo_root))
    return CalibrationLedgerSnapshot(
        ledger_schema=LEDGER_SCHEMA,
        ledger_path=ledger_path,
        head_sequence=physical_sequence,
        head_digest=physical_digest,
        receipts=tuple(_frozen_mapping(receipt) for receipt in receipts),
        observations=tuple(observations),
        refusal_reasons=tuple(sorted(reasons)),
        bracket_sessions=tuple(bracket_sessions),
        baseline_sequence=baseline_sequence,
        baseline_digest=baseline_digest,
        committed_head_sequence=pinned_sequence,
        committed_head_digest=pinned_digest,
    )


def _new_receipt(
    *,
    sequence: int,
    predecessor_digest: str,
    event: str,
    attempt_id: str,
    content_id: str | None,
    artifacts: Mapping[str, str],
    identity_epoch: Mapping[str, Any] | None,
    t1_bindings: Mapping[str, Any] | None,
    capture_wall_time_s: str | None,
    exact_bound_lexeme_s: str | None,
    disposition: str,
    custody_locator: str,
    historical_import_input_sha256: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "sequence": sequence,
        "predecessor_digest": predecessor_digest,
        "event": event,
        "attempt_id": attempt_id,
        "content_id": content_id,
        "artifact_sha256": dict(sorted(artifacts.items())),
        "identity_epoch": _normalized_vector(identity_epoch, IDENTITY_EPOCH_FIELDS),
        "t1_bindings": _normalized_vector(t1_bindings, T1_FIELDS),
        "capture_wall_time_s": capture_wall_time_s,
        "exact_bound_lexeme_s": exact_bound_lexeme_s,
        "disposition": disposition,
        "custody_locator": custody_locator,
    }
    if historical_import_input_sha256 is not None:
        receipt[_HISTORICAL_IMPORT_INPUT_SHA256_KEY] = dict(
            sorted(historical_import_input_sha256.items())
        )
    receipt["receipt_digest"] = _receipt_digest(receipt)
    return receipt


def _new_bracket_session_record(
    *,
    sequence: int,
    predecessor_digest: str,
    event: str,
    session_identity: Mapping[str, Any],
    fields: Mapping[str, Any],
) -> dict[str, Any]:
    receipt = {
        "schema_version": BRACKET_SESSION_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "sequence": sequence,
        "predecessor_digest": predecessor_digest,
        "event": event,
        **{field: session_identity.get(field) for field in _SESSION_IDENTITY_KEYS},
        **dict(fields),
    }
    receipt["receipt_digest"] = _receipt_digest(receipt)
    return receipt


def _json_object_from_bytes(raw: bytes, source: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CalibrationLedgerError(f"{source}: malformed JSON") from exc
    if not isinstance(value, Mapping):
        raise CalibrationLedgerError(f"{source}: expected a JSON object")
    return value


def _authenticated_json_object(
    raw: bytes,
    expected_sha256: str,
    *,
    label: str,
) -> Mapping[str, Any]:
    if not _is_sha256(expected_sha256):
        raise CalibrationLedgerError(f"expected {label} sha256 is malformed")
    observed = hashlib.sha256(raw).hexdigest()
    if observed != expected_sha256:
        raise CalibrationLedgerError(f"{label} sha256 mismatch")
    return _json_object_from_bytes(raw, Path(label))


def _number_lexemes(raw: bytes, source: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(raw, parse_float=str, parse_int=str)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CalibrationLedgerError(f"{source}: malformed JSON") from exc
    if not isinstance(value, Mapping):
        raise CalibrationLedgerError(f"{source}: expected a JSON object")
    return value


def _historical_import_table(
    value: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Mapping[str, Any]]]:
    if set(value) != {
        "schema_version",
        "ledger_schema",
        "identity_epoch",
        "members",
    }:
        raise CalibrationLedgerError("historical import table has invalid keys")
    if (
        value.get("schema_version") != HISTORICAL_IMPORT_TABLE_SCHEMA
        or value.get("ledger_schema") != LEDGER_SCHEMA
    ):
        raise CalibrationLedgerError("historical import table schema mismatch")
    epoch = value.get("identity_epoch")
    members = value.get("members")
    if (
        not isinstance(epoch, Mapping)
        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
        or any(epoch.get(field) in (None, "") for field in IDENTITY_EPOCH_FIELDS)
        or not isinstance(members, list)
        or not members
    ):
        raise CalibrationLedgerError("historical import table is incomplete")

    by_content: dict[str, Mapping[str, Any]] = {}
    attempt_ids: set[str] = set()
    for member in members:
        if not isinstance(member, Mapping) or set(member) != {
            "attempt_id",
            "content_id",
            "artifact_sha256",
            "disposition",
        }:
            raise CalibrationLedgerError("historical import member has invalid keys")
        attempt_id = member.get("attempt_id")
        content_id = member.get("content_id")
        artifacts = member.get("artifact_sha256")
        disposition = member.get("disposition")
        if (
            not isinstance(attempt_id, str)
            or not attempt_id
            or not _is_sha256(content_id)
            or not isinstance(artifacts, Mapping)
            or set(artifacts) != set(GOVERNED_ARTIFACTS)
            or any(not _is_sha256(item) for item in artifacts.values())
            or content_id_from_artifact_hashes(artifacts) != content_id
            or disposition not in HISTORICAL_IMPORT_DISPOSITIONS
        ):
            raise CalibrationLedgerError("historical import member is malformed")
        if attempt_id in attempt_ids:
            raise CalibrationLedgerError(
                "historical import attempt_id collision; content_id tiebreak is "
                "diagnostic only"
            )
        if str(content_id) in by_content:
            raise CalibrationLedgerError("historical import content_id is duplicated")
        attempt_ids.add(attempt_id)
        by_content[str(content_id)] = member
    return dict(epoch), by_content


def _historical_import_custody_manifest(
    value: Mapping[str, Any],
    *,
    expected_content_ids: set[str],
) -> dict[str, Path]:
    if set(value) != {"schema_version", "ledger_schema", "members"}:
        raise CalibrationLedgerError("custody manifest has invalid keys")
    if (
        value.get("schema_version") != HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA
        or value.get("ledger_schema") != LEDGER_SCHEMA
        or not isinstance(value.get("members"), Mapping)
    ):
        raise CalibrationLedgerError("custody manifest schema mismatch")
    members = value["members"]
    if set(members) != expected_content_ids:
        raise CalibrationLedgerError(
            "custody manifest content set differs from disposition table"
        )
    result: dict[str, Path] = {}
    for content_id, locator in members.items():
        if not _is_sha256(content_id) or not isinstance(locator, str) or not locator:
            raise CalibrationLedgerError("custody manifest member is malformed")
        path = Path(locator)
        if not path.is_absolute():
            raise CalibrationLedgerError("custody manifest locator is not absolute")
        result[str(content_id)] = path
    return result


def custody_manifest_bytes(value: Mapping[str, Any]) -> bytes:
    """Return the exact reviewable byte representation emitted by the CLI."""

    return (
        json.dumps(
            _jsonable(value),
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _historical_directories(roots: Sequence[Path]) -> tuple[Path, ...]:
    directories: set[Path] = set()
    if not roots:
        raise CalibrationLedgerError("at least one historical import root is required")
    for supplied in roots:
        try:
            root = Path(supplied).resolve(strict=True)
        except OSError as exc:
            raise CalibrationLedgerError(
                f"historical import root is unreadable: {supplied}"
            ) from exc
        if (root / "manifest.json").is_file():
            directories.add(root)
        directories.update(path.parent for path in root.glob("*/manifest.json"))
        directories.update(
            path.parent
            for path in root.glob("instrument_validation/*/manifest.json")
        )
    if not directories:
        raise CalibrationLedgerError("historical import roots contain no candidates")
    return tuple(sorted(directories, key=lambda path: path.as_posix()))


def _assert_absolute_nonsymlink_directory(directory: Path) -> Path:
    path = Path(directory)
    if not path.is_absolute():
        raise CalibrationLedgerError("custody locator is not absolute")
    current = Path(path.anchor)
    try:
        for component in path.parts[1:]:
            current /= component
            if stat.S_ISLNK(os.lstat(current).st_mode):
                raise CalibrationLedgerError(
                    f"custody locator resolves through a symlink: {path}"
                )
        if not stat.S_ISDIR(os.stat(path, follow_symlinks=False).st_mode):
            raise CalibrationLedgerError(f"custody locator is not a directory: {path}")
    except FileNotFoundError as exc:
        raise CalibrationLedgerError(f"custody locator is missing: {path}") from exc
    except OSError as exc:
        raise CalibrationLedgerError(f"custody locator is unreadable: {path}") from exc
    return path


def _read_contained_nofollow(directory: Path, relative: str) -> bytes:
    root = _assert_absolute_nonsymlink_directory(directory)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0) | nofollow
    descriptor = os.open(root, directory_flags)
    try:
        components = Path(relative).parts
        if not components or any(item in {"", ".", ".."} for item in components):
            raise CalibrationLedgerError("governed artifact path is not contained")
        parent = descriptor
        owned_parent = False
        try:
            for component in components[:-1]:
                child = os.open(component, directory_flags, dir_fd=parent)
                if owned_parent:
                    os.close(parent)
                parent = child
                owned_parent = True
            artifact = os.open(components[-1], flags | nofollow, dir_fd=parent)
            try:
                if not stat.S_ISREG(os.fstat(artifact).st_mode):
                    raise CalibrationLedgerError(
                        f"governed artifact is not a regular file: {root / relative}"
                    )
                chunks: list[bytes] = []
                while True:
                    chunk = os.read(artifact, 1024 * 1024)
                    if not chunk:
                        break
                    chunks.append(chunk)
                return b"".join(chunks)
            finally:
                os.close(artifact)
        finally:
            if owned_parent:
                os.close(parent)
    except CalibrationLedgerError:
        raise
    except OSError as exc:
        raise CalibrationLedgerError(
            f"governed artifact is unreadable without symlink traversal: {root / relative}"
        ) from exc
    finally:
        os.close(descriptor)


def _governed_raw_nofollow(directory: Path) -> dict[str, bytes]:
    return {
        relative: _read_contained_nofollow(directory, relative)
        for relative in GOVERNED_ARTIFACTS
    }


def _inspect_historical_candidate(
    directory: Path,
    *,
    checkout_root: Path | None,
    expected_epoch: Mapping[str, Any],
) -> tuple[str | None, _HistoricalCandidate | None, str | None]:
    manifest_path = directory / "manifest.json"
    evidence_path = directory / "instrument_evidence.json"
    try:
        manifest_raw = _read_contained_nofollow(directory, "manifest.json")
        evidence_raw = _read_contained_nofollow(
            directory, "instrument_evidence.json"
        )
        manifest = _json_object_from_bytes(manifest_raw, manifest_path)
        evidence = _json_object_from_bytes(evidence_raw, evidence_path)
    except (OSError, CalibrationLedgerError) as exc:
        return None, None, f"{directory}: primary evidence is unreadable: {exc}"

    bindings = evidence.get("bindings")
    if not isinstance(bindings, Mapping):
        return None, None, f"{directory}: evidence bindings are missing"
    epoch = _normalized_vector(bindings, IDENTITY_EPOCH_FIELDS)
    if epoch != dict(expected_epoch):
        return None, None, None

    primary_hashes = {
        "instrument_evidence.json": hashlib.sha256(evidence_raw).hexdigest(),
        "manifest.json": hashlib.sha256(manifest_raw).hexdigest(),
    }
    content_id = content_id_from_artifact_hashes(primary_hashes)
    if content_id is None:
        return None, None, f"{directory}: content identity is incomplete"

    try:
        resolved = _assert_absolute_nonsymlink_directory(directory)
        custody_sort_key = (
            resolved.relative_to(checkout_root).as_posix()
            if checkout_root is not None
            else resolved.as_posix()
        )
    except (OSError, ValueError, CalibrationLedgerError) as exc:
        return content_id, None, f"{directory}: custody is outside checkout root: {exc}"

    try:
        raw_by_name = _governed_raw_nofollow(directory)
    except CalibrationLedgerError as exc:
        return content_id, None, f"{directory}: hash-complete custody is missing: {exc}"
    hashes = {
        name: hashlib.sha256(raw_by_name[name]).hexdigest()
        for name in GOVERNED_ARTIFACTS
    }

    manifest_artifacts = manifest.get("artifacts")
    evidence_artifacts = evidence.get("artifact_sha256")
    if (
        not isinstance(manifest_artifacts, Mapping)
        or set(manifest_artifacts) != set(MANIFEST_BOUND_ARTIFACTS)
        or any(
            manifest_artifacts.get(name) != hashes[name]
            for name in MANIFEST_BOUND_ARTIFACTS
        )
    ):
        return content_id, None, f"{directory}: manifest artifact hash mismatch"
    if (
        not isinstance(evidence_artifacts, Mapping)
        or set(evidence_artifacts) != set(EVIDENCE_BOUND_ARTIFACTS)
        or any(
            evidence_artifacts.get(name) != hashes[name]
            for name in EVIDENCE_BOUND_ARTIFACTS
        )
    ):
        return content_id, None, f"{directory}: evidence artifact hash mismatch"

    attempt_id = evidence.get("validation_id")
    if (
        not isinstance(attempt_id, str)
        or not attempt_id
        or manifest.get("validation_id") != attempt_id
    ):
        return content_id, None, f"{directory}: attempt identity mismatch"
    t1_bindings = _normalized_vector(bindings, T1_FIELDS)
    if any(t1_bindings.get(field) in (None, "") for field in T1_FIELDS):
        return content_id, None, f"{directory}: full T1 binding is incomplete"
    try:
        lexemes = _number_lexemes(evidence_raw, evidence_path)
    except CalibrationLedgerError as exc:
        return content_id, None, str(exc)
    capture = lexemes.get("capture_wall_time_s")
    bound = lexemes.get("b_fiducial_s")
    if capture is not None and not isinstance(capture, str):
        return content_id, None, f"{directory}: capture time lexeme is invalid"
    if bound is not None and not isinstance(bound, str):
        return content_id, None, f"{directory}: bound lexeme is invalid"
    if capture is None:
        return content_id, None, f"{directory}: capture time is missing"
    return (
        content_id,
        _HistoricalCandidate(
            attempt_id=attempt_id,
            content_id=content_id,
            artifact_sha256=MappingProxyType(hashes),
            identity_epoch=MappingProxyType(epoch),
            t1_bindings=MappingProxyType(t1_bindings),
            capture_wall_time_s=capture,
            exact_bound_lexeme_s=bound,
            custody_sort_key=custody_sort_key,
            custody_locator=resolved.as_posix(),
        ),
        None,
    )


def _discover_historical_candidates(
    *,
    roots: Sequence[Path],
    checkout_root: Path,
    expected_epoch: Mapping[str, Any],
) -> tuple[dict[str, list[_HistoricalCandidate]], dict[str, list[str]]]:
    try:
        checkout = Path(checkout_root).resolve(strict=True)
    except OSError as exc:
        raise CalibrationLedgerError("checkout root is unreadable") from exc

    complete: dict[str, list[_HistoricalCandidate]] = {}
    incomplete: dict[str, list[str]] = {}
    unknown_errors: list[str] = []
    for directory in _historical_directories(roots):
        content_id, candidate, error = _inspect_historical_candidate(
            directory,
            checkout_root=checkout,
            expected_epoch=expected_epoch,
        )
        if candidate is not None:
            complete.setdefault(candidate.content_id, []).append(candidate)
        elif error is not None:
            if content_id is None:
                unknown_errors.append(error)
            else:
                incomplete.setdefault(content_id, []).append(error)
    if unknown_errors:
        raise CalibrationLedgerError(sorted(unknown_errors)[0])

    return complete, incomplete


def generate_historical_custody_manifest(
    *,
    roots: Sequence[Path],
    checkout_root: Path,
    disposition_table_raw: bytes,
    expected_disposition_table_sha256: str,
) -> Mapping[str, Any]:
    """Apply the lexicographic selection rule for a lead-reviewed manifest."""

    table = _authenticated_json_object(
        disposition_table_raw,
        expected_disposition_table_sha256,
        label="disposition table",
    )
    expected_epoch, table_by_content = _historical_import_table(table)
    complete, incomplete = _discover_historical_candidates(
        roots=roots,
        checkout_root=checkout_root,
        expected_epoch=expected_epoch,
    )
    expected_ids = set(table_by_content)
    extra_ids = sorted((set(complete) | set(incomplete)) - expected_ids)
    missing_ids = sorted(expected_ids - set(complete))
    if extra_ids:
        raise CalibrationLedgerError(
            f"historical import table omits authenticated content_id {extra_ids[0]}"
        )
    if missing_ids:
        detail = sorted(incomplete.get(missing_ids[0], []))
        if detail:
            raise CalibrationLedgerError(detail[0])
        raise CalibrationLedgerError(
            f"historical import content_id is missing: {missing_ids[0]}"
        )
    members: dict[str, str] = {}
    for content_id in sorted(expected_ids):
        candidate = min(
            complete[content_id], key=lambda item: item.custody_sort_key
        )
        member = table_by_content[content_id]
        if candidate.attempt_id != member["attempt_id"]:
            raise CalibrationLedgerError(
                f"{content_id}: attempt_id differs from disposition table"
            )
        if dict(candidate.artifact_sha256) != dict(member["artifact_sha256"]):
            raise CalibrationLedgerError(
                f"{content_id}: artifact hashes differ from disposition table"
            )
        members[content_id] = candidate.custody_locator
    return {
        "schema_version": HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "members": members,
    }


def prepare_historical_import(
    *,
    roots: Sequence[Path] = (),
    checkout_root: Path = REPO_ROOT,
    disposition_table_raw: bytes,
    expected_disposition_table_sha256: str,
    custody_manifest_raw: bytes,
    expected_custody_manifest_sha256: str,
) -> HistoricalImportPlan:
    """Authenticate reviewed inputs and prepare the canonical genesis chain."""

    disposition_table = _authenticated_json_object(
        disposition_table_raw,
        expected_disposition_table_sha256,
        label="disposition table",
    )
    expected_epoch, table_by_content = _historical_import_table(disposition_table)
    custody_manifest = _authenticated_json_object(
        custody_manifest_raw,
        expected_custody_manifest_sha256,
        label="custody manifest",
    )
    pinned = _historical_import_custody_manifest(
        custody_manifest,
        expected_content_ids=set(table_by_content),
    )

    selected_by_content: dict[str, _HistoricalCandidate] = {}
    for content_id, locator in pinned.items():
        observed_id, candidate, error = _inspect_historical_candidate(
            locator,
            checkout_root=None,
            expected_epoch=expected_epoch,
        )
        if candidate is None:
            raise CalibrationLedgerError(
                error or f"pinned custody is not authentic: {locator}"
            )
        if observed_id != content_id:
            raise CalibrationLedgerError(
                f"pinned custody content_id mismatch: {content_id}"
            )
        selected_by_content[content_id] = candidate

    if roots:
        complete, _incomplete = _discover_historical_candidates(
            roots=roots,
            checkout_root=checkout_root,
            expected_epoch=expected_epoch,
        )
        discovered_ids = set(complete)
        if discovered_ids != set(pinned):
            raise CalibrationLedgerError(
                "discovered hash-complete content set contradicts custody manifest"
            )
        discovered_locators = {
            candidate.custody_locator
            for candidates in complete.values()
            for candidate in candidates
        }
        absent = sorted(
            path.as_posix()
            for path in pinned.values()
            if path.as_posix() not in discovered_locators
        )
        if absent:
            raise CalibrationLedgerError(
                f"pinned custody locator is absent from root discovery: {absent[0]}"
            )

    selected: list[tuple[_HistoricalCandidate, Mapping[str, Any]]] = []
    for content_id, member in table_by_content.items():
        candidate = selected_by_content[content_id]
        if candidate.attempt_id != member["attempt_id"]:
            raise CalibrationLedgerError(
                f"{content_id}: attempt_id differs from disposition table"
            )
        if dict(candidate.artifact_sha256) != dict(member["artifact_sha256"]):
            raise CalibrationLedgerError(
                f"{content_id}: artifact hashes differ from disposition table"
            )
        selected.append((candidate, member))

    # Attempt ids are contractually unique. content_id is the deterministic
    # secondary key used before the duplicate-attempt refusal above.
    selected.sort(key=lambda item: (item[0].attempt_id, item[0].content_id))
    receipts: list[Mapping[str, Any]] = []
    predecessor = GENESIS_DIGEST
    for candidate, member in selected:
        reservation = _new_receipt(
            sequence=len(receipts) + 1,
            predecessor_digest=predecessor,
            event=HISTORICAL_IMPORT_RESERVATION_EVENT,
            attempt_id=candidate.attempt_id,
            content_id=None,
            artifacts={},
            identity_epoch=candidate.identity_epoch,
            t1_bindings=candidate.t1_bindings,
            capture_wall_time_s=None,
            exact_bound_lexeme_s=None,
            disposition="pending",
            custody_locator=candidate.custody_locator,
            historical_import_input_sha256={
                "disposition_table": expected_disposition_table_sha256,
                "custody_manifest": expected_custody_manifest_sha256,
            },
        )
        if not _valid_receipt_shape(reservation):
            raise CalibrationLedgerError("historical reservation is malformed")
        receipts.append(reservation)
        predecessor = str(reservation["receipt_digest"])
        finalization = _new_receipt(
            sequence=len(receipts) + 1,
            predecessor_digest=predecessor,
            event=HISTORICAL_IMPORT_FINALIZATION_EVENT,
            attempt_id=candidate.attempt_id,
            content_id=candidate.content_id,
            artifacts=candidate.artifact_sha256,
            identity_epoch=candidate.identity_epoch,
            t1_bindings=candidate.t1_bindings,
            capture_wall_time_s=candidate.capture_wall_time_s,
            exact_bound_lexeme_s=candidate.exact_bound_lexeme_s,
            disposition=str(member["disposition"]),
            custody_locator=candidate.custody_locator,
        )
        if not _valid_receipt_shape(finalization):
            raise CalibrationLedgerError("historical finalization is malformed")
        receipts.append(finalization)
        predecessor = str(finalization["receipt_digest"])

    observations, bracket_sessions, reasons = _attempts_and_observations(receipts)
    del bracket_sessions
    if reasons or len(observations) != len(selected):
        raise CalibrationLedgerError(
            ", ".join(sorted(reasons or {"historical import is incomplete"}))
        )
    final = receipts[-1]
    pin = head_pin_for_receipt(final)
    return HistoricalImportPlan(
        receipts=tuple(_frozen_mapping(row) for row in receipts),
        final_sequence=len(receipts),
        head_digest=str(final["receipt_digest"]),
        head_pin=_frozen_mapping(pin),
        disposition_table_sha256=expected_disposition_table_sha256,
        custody_manifest_sha256=expected_custody_manifest_sha256,
    )


def _require_genesis_bootstrap_state(
    ledger_path: Path,
    head_pin_path: Path,
    *,
    require_committed_pin: bool,
    repo_root: Path,
    expected_payload: bytes | None = None,
    allow_nonempty_pending_plan: bool = False,
) -> bool:
    try:
        pin_raw = Path(head_pin_path).read_bytes()
        pin_value = json.loads(pin_raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CalibrationLedgerError("head pin is unreadable") from exc
    if _head_pin(pin_value) != (0, GENESIS_DIGEST):
        raise CalibrationLedgerError("historical import requires the genesis head pin")
    if (
        require_committed_pin
        and _committed_pin_bytes(Path(head_pin_path), Path(repo_root)) != pin_raw
    ):
        raise CalibrationLedgerError("head pin is not committed at Git HEAD")
    path = Path(ledger_path)
    try:
        raw = path.read_bytes() if path.exists() else b""
    except OSError as exc:
        raise CalibrationLedgerError("physical ledger is unreadable") from exc
    if raw:
        if expected_payload is not None and raw == expected_payload:
            return True
        if allow_nonempty_pending_plan:
            return False
        raise CalibrationLedgerError("historical import requires an empty ledger")
    return False


def _ledger_lock_path(ledger_path: Path) -> Path:
    ledger = Path(ledger_path).resolve(strict=False)
    return ledger.with_name(f"{ledger.name}.lock")


_LOCAL_FILESYSTEM_TYPES = frozenset(
    {
        "apfs",
        "btrfs",
        "devfs",
        "ext2",
        "ext3",
        "ext4",
        "hfs",
        "hfsplus",
        "overlay",
        "tmpfs",
        "ufs",
        "xfs",
        "zfs",
    }
)
_REMOTE_FILESYSTEM_TYPES = frozenset(
    {
        "9p",
        "afs",
        "cifs",
        "fuse.sshfs",
        "nfs",
        "nfs4",
        "smbfs",
        "webdav",
    }
)


def _filesystem_type(path: Path) -> str | None:
    """Return a platform-confirmed filesystem type for the canonical parent."""

    if sys.platform == "darwin":
        try:
            completed = subprocess.run(
                ["/sbin/mount"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (OSError, subprocess.CalledProcessError):
            return None
        resolved = str(Path(path).resolve(strict=True))
        candidates: list[tuple[int, str]] = []
        for line in completed.stdout.splitlines():
            match = re.match(r"^.+ on (.+) \(([^,]+), (.+)\)$", line)
            if match is None:
                continue
            mount_point, fs_type, raw_options = match.groups()
            options = {option.strip() for option in raw_options.split(",")}
            if "local" not in options:
                continue
            if resolved == mount_point or resolved.startswith(mount_point.rstrip("/") + "/"):
                candidates.append((len(mount_point), fs_type.lower()))
        return max(candidates, default=(0, ""))[1] or None
    mountinfo = Path("/proc/self/mountinfo")
    if sys.platform.startswith("linux") and mountinfo.is_file():
        resolved = str(Path(path).resolve(strict=True))
        candidates: list[tuple[int, str]] = []
        try:
            lines = mountinfo.read_text(encoding="utf-8").splitlines()
        except OSError:
            return None
        for line in lines:
            fields = line.split()
            try:
                separator = fields.index("-")
                mount_point = fields[4].replace("\\040", " ")
                fs_type = fields[separator + 1].lower()
            except (ValueError, IndexError):
                continue
            if resolved == mount_point or resolved.startswith(mount_point.rstrip("/") + "/"):
                candidates.append((len(mount_point), fs_type))
        return max(candidates, default=(0, ""))[1] or None
    return None


def _affirm_local_filesystem(path: Path) -> None:
    fs_type = _filesystem_type(path)
    if fs_type in _LOCAL_FILESYSTEM_TYPES:
        return
    reason = "remote_filesystem" if fs_type in _REMOTE_FILESYSTEM_TYPES else "filesystem_capability_indeterminate"
    raise CalibrationLedgerError(
        RefusalCode.UNSAFE_LOCK_INODE,
        context={"reason": reason, "filesystem_type": fs_type},
    )


@dataclass(frozen=True)
class LedgerLeaseIdentity:
    canonical_path: Path
    canonical_parent: Path
    canonical_basename: str
    parent_descriptor: int
    slot_key: tuple[int, int, str]
    object_key: tuple[int, int] | None
    object_descriptor: int | None


def resolve_ledger_lease_identity(ledger_path: Path) -> LedgerLeaseIdentity:
    """Resolve one canonical pathname slot and optional regular ledger object."""

    canonical_path = Path(ledger_path).resolve(strict=False)
    canonical_parent = canonical_path.parent.resolve(strict=True)
    canonical_basename = canonical_path.name
    if not canonical_basename or canonical_basename in {".", ".."}:
        raise CalibrationLedgerError(
            RefusalCode.UNSAFE_LOCK_INODE,
            context={"reason": "invalid_canonical_basename"},
        )
    _affirm_local_filesystem(canonical_parent)
    try:
        parent_descriptor = os.open(
            canonical_parent,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
        )
    except OSError as exc:
        raise CalibrationLedgerError(
            RefusalCode.UNSAFE_LOCK_INODE,
            context={"reason": "canonical_parent_open_failed"},
        ) from exc
    object_descriptor: int | None = None
    try:
        parent_stat = os.fstat(parent_descriptor)
        slot_key = (parent_stat.st_dev, parent_stat.st_ino, canonical_basename)
        try:
            object_descriptor = os.open(
                canonical_basename,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=parent_descriptor,
            )
        except FileNotFoundError:
            object_key = None
        except OSError as exc:
            raise CalibrationLedgerError(
                RefusalCode.PHYSICAL_LEDGER_UNREADABLE,
                context={"reason": "identity_unreadable"},
            ) from exc
        else:
            object_stat = os.fstat(object_descriptor)
            if not stat.S_ISREG(object_stat.st_mode):
                raise CalibrationLedgerError(
                    RefusalCode.UNSAFE_LOCK_INODE,
                    context={"reason": "ledger_not_regular"},
                )
            object_key = (object_stat.st_dev, object_stat.st_ino)
        return LedgerLeaseIdentity(
            canonical_path=canonical_path,
            canonical_parent=canonical_parent,
            canonical_basename=canonical_basename,
            parent_descriptor=parent_descriptor,
            slot_key=slot_key,
            object_key=object_key,
            object_descriptor=object_descriptor,
        )
    except Exception:
        if object_descriptor is not None:
            os.close(object_descriptor)
        os.close(parent_descriptor)
        raise


def _open_slot_sidecar(identity: LedgerLeaseIdentity) -> int:
    try:
        descriptor = os.open(
            f"{identity.canonical_basename}.lock",
            os.O_NOFOLLOW | os.O_CREAT | os.O_RDWR,
            0o600,
            dir_fd=identity.parent_descriptor,
        )
    except OSError as exc:
        raise CalibrationLedgerError(
            RefusalCode.UNSAFE_LOCK_INODE,
            context={"reason": "open_failed"},
        ) from exc
    try:
        lock_stat = os.fstat(descriptor)
        if not stat.S_ISREG(lock_stat.st_mode) or lock_stat.st_nlink != 1:
            raise CalibrationLedgerError(
                RefusalCode.UNSAFE_LOCK_INODE,
                context={"reason": "not_dedicated_regular_file"},
            )
        if identity.object_key == (lock_stat.st_dev, lock_stat.st_ino):
            raise CalibrationLedgerError(
                RefusalCode.UNSAFE_LOCK_INODE,
                context={"reason": "aliases_ledger"},
            )
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _open_ledger_lock(ledger_path: Path) -> int:
    """Compatibility helper returning the canonical permanent slot sidecar."""

    identity = resolve_ledger_lease_identity(Path(ledger_path))
    try:
        return _open_slot_sidecar(identity)
    finally:
        if identity.object_descriptor is not None:
            os.close(identity.object_descriptor)
        os.close(identity.parent_descriptor)


_LeaseRegistryKey = tuple[str, int, int] | tuple[str, int, int, str]
_ACTIVE_WRITER_LEASES: dict[_LeaseRegistryKey, "CalibrationWriterLease"] = {}
_ACTIVE_WRITER_LEASES_GUARD = threading.Lock()


class _LedgerPublicationDurabilityUncertain(OSError):
    """The ledger name is published and locked, but directory fsync failed."""


def _registry_keys(identity: LedgerLeaseIdentity) -> tuple[_LeaseRegistryKey, ...]:
    slot = ("slot", *identity.slot_key)
    if identity.object_key is None:
        return (slot,)
    return (slot, ("object", *identity.object_key))


def _close_identity(identity: LedgerLeaseIdentity) -> None:
    if identity.object_descriptor is not None:
        os.close(identity.object_descriptor)
    os.close(identity.parent_descriptor)


def _current_writer_lease(ledger_path: Path) -> "CalibrationWriterLease | None":
    identity = resolve_ledger_lease_identity(Path(ledger_path))
    try:
        with _ACTIVE_WRITER_LEASES_GUARD:
            held = {
                _ACTIVE_WRITER_LEASES[key]
                for key in _registry_keys(identity)
                if key in _ACTIVE_WRITER_LEASES
            }
        if len(held) != 1:
            return None
        lease = next(iter(held))
        return lease if lease._owner_thread == threading.get_ident() else None
    finally:
        _close_identity(identity)


class CalibrationWriterLease:
    """One nonblocking kernel lease held across the complete writer lifetime.

    The dedicated lock inode is permanent. Diagnostic metadata may become
    stale, but only kernel ``flock`` ownership determines liveness.
    """

    def __init__(self, ledger_path: Path = DEFAULT_LEDGER_PATH) -> None:
        self.ledger_path = Path(ledger_path)
        self.identity: LedgerLeaseIdentity | None = None
        self.slot_descriptor: int | None = None
        self._owner_thread: int | None = None

    @property
    def held(self) -> bool:
        return self.slot_descriptor is not None

    @property
    def descriptor(self) -> int | None:
        """Backward-compatible diagnostic name for the slot descriptor."""

        return self.slot_descriptor

    def acquire(self, *, nonblocking: bool = True) -> "CalibrationWriterLease":
        if self.held:
            return self
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        identity = resolve_ledger_lease_identity(self.ledger_path)
        keys = _registry_keys(identity)
        with _ACTIVE_WRITER_LEASES_GUARD:
            if any(key in _ACTIVE_WRITER_LEASES for key in keys):
                _close_identity(identity)
                raise CalibrationLedgerError(RefusalCode.LIVE_WRITER_CONTENTION)
        slot_descriptor = _open_slot_sidecar(identity)
        flags = fcntl.LOCK_EX | (fcntl.LOCK_NB if nonblocking else 0)
        try:
            fcntl.flock(slot_descriptor, flags)
        except BlockingIOError as exc:
            os.close(slot_descriptor)
            _close_identity(identity)
            raise CalibrationLedgerError(RefusalCode.LIVE_WRITER_CONTENTION) from exc
        try:
            if identity.object_descriptor is not None:
                fcntl.flock(identity.object_descriptor, flags)
        except BlockingIOError as exc:
            fcntl.flock(slot_descriptor, fcntl.LOCK_UN)
            os.close(slot_descriptor)
            _close_identity(identity)
            raise CalibrationLedgerError(RefusalCode.LIVE_WRITER_CONTENTION) from exc
        owner = threading.get_ident()
        with _ACTIVE_WRITER_LEASES_GUARD:
            if any(key in _ACTIVE_WRITER_LEASES for key in keys):
                if identity.object_descriptor is not None:
                    fcntl.flock(identity.object_descriptor, fcntl.LOCK_UN)
                fcntl.flock(slot_descriptor, fcntl.LOCK_UN)
                os.close(slot_descriptor)
                _close_identity(identity)
                raise CalibrationLedgerError(RefusalCode.LIVE_WRITER_CONTENTION)
            for key in keys:
                _ACTIVE_WRITER_LEASES[key] = self
        self.identity = identity
        self.slot_descriptor = slot_descriptor
        self._owner_thread = owner
        return self

    def _verify_current_path(self) -> None:
        identity = self.identity
        if identity is None or identity.object_key is None:
            return
        try:
            current = os.stat(
                identity.canonical_basename,
                dir_fd=identity.parent_descriptor,
                follow_symlinks=False,
            )
        except OSError as exc:
            raise CalibrationLedgerError(
                RefusalCode.UNSAFE_LOCK_INODE,
                context={"reason": "leased_path_replaced"},
            ) from exc
        if not stat.S_ISREG(current.st_mode) or (
            current.st_dev,
            current.st_ino,
        ) != identity.object_key:
            raise CalibrationLedgerError(
                RefusalCode.UNSAFE_LOCK_INODE,
                context={"reason": "leased_path_replaced"},
            )

    def _adopt_object(self, descriptor: int) -> None:
        identity = self.identity
        if identity is None:
            raise AssertionError("cannot adopt an object without a held slot")
        status = os.fstat(descriptor)
        object_key = (status.st_dev, status.st_ino)
        new_key: _LeaseRegistryKey = ("object", *object_key)
        old_key = (
            ("object", *identity.object_key)
            if identity.object_key is not None
            else None
        )
        with _ACTIVE_WRITER_LEASES_GUARD:
            conflict = _ACTIVE_WRITER_LEASES.get(new_key)
            if conflict is not None and conflict is not self:
                raise CalibrationLedgerError(RefusalCode.LIVE_WRITER_CONTENTION)
            if old_key is not None and _ACTIVE_WRITER_LEASES.get(old_key) is self:
                del _ACTIVE_WRITER_LEASES[old_key]
            _ACTIVE_WRITER_LEASES[new_key] = self
        old_descriptor = identity.object_descriptor
        self.identity = replace(
            identity,
            object_key=object_key,
            object_descriptor=descriptor,
        )
        if old_descriptor is not None:
            try:
                fcntl.flock(old_descriptor, fcntl.LOCK_UN)
            finally:
                os.close(old_descriptor)

    def _publish_locked_inode(self, descriptor: int, staging_path: Path) -> None:
        identity = self.identity
        if identity is None:
            raise AssertionError("cannot publish without a held slot")
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if identity.object_key is None:
            try:
                os.link(staging_path, identity.canonical_path)
            except FileExistsError as exc:
                raise CalibrationLedgerError(
                    RefusalCode.UNSAFE_LOCK_INODE,
                    context={"reason": "genesis_path_appeared"},
                ) from exc
            staging_path.unlink()
        else:
            self._verify_current_path()
            os.replace(staging_path, identity.canonical_path)
        self._adopt_object(descriptor)
        try:
            _fsync_parent_directory(identity.canonical_parent)
        except OSError as exc:
            raise _LedgerPublicationDurabilityUncertain from exc

    def publish_genesis_payload(self, payload: bytes) -> None:
        identity = self.identity
        if identity is None:
            raise AssertionError("cannot publish without a held lease")
        descriptor, staging_name = tempfile.mkstemp(
            prefix=f".{identity.canonical_basename}.genesis-",
            dir=identity.canonical_parent,
        )
        staging_path = Path(staging_name)
        adopted = False
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(os.dup(descriptor), "wb") as handle:
                _write_bootstrap_payload(handle, payload)
                handle.flush()
                os.fsync(handle.fileno())
            self._publish_locked_inode(descriptor, staging_path)
            adopted = True
        finally:
            if (
                self.identity is not None
                and self.identity.object_descriptor == descriptor
            ):
                adopted = True
            if staging_path.exists():
                staging_path.unlink()
            if not adopted:
                os.close(descriptor)

    def open_append_descriptor(self) -> int:
        identity = self.identity
        if identity is None:
            raise AssertionError("append requires a held lease")
        if identity.object_descriptor is None:
            self.publish_genesis_payload(b"")
            identity = self.identity
            assert identity is not None
        self._verify_current_path()
        assert identity.object_descriptor is not None
        try:
            descriptor = os.open(
                identity.canonical_basename,
                os.O_RDWR | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=identity.parent_descriptor,
            )
        except OSError:
            raise
        status = os.fstat(descriptor)
        if (status.st_dev, status.st_ino) != identity.object_key:
            os.close(descriptor)
            raise CalibrationLedgerError(
                RefusalCode.UNSAFE_LOCK_INODE,
                context={"reason": "leased_path_replaced"},
            )
        return descriptor

    def release(self) -> None:
        slot_descriptor = self.slot_descriptor
        identity = self.identity
        if slot_descriptor is None or identity is None:
            return
        keys = _registry_keys(identity)
        with _ACTIVE_WRITER_LEASES_GUARD:
            for key in keys:
                if _ACTIVE_WRITER_LEASES.get(key) is self:
                    del _ACTIVE_WRITER_LEASES[key]
        try:
            if identity.object_descriptor is not None:
                try:
                    fcntl.flock(identity.object_descriptor, fcntl.LOCK_UN)
                finally:
                    os.close(identity.object_descriptor)
            fcntl.flock(slot_descriptor, fcntl.LOCK_UN)
        finally:
            os.close(slot_descriptor)
            os.close(identity.parent_descriptor)
            self.identity = None
            self.slot_descriptor = None
            self._owner_thread = None

    def __enter__(self) -> "CalibrationWriterLease":
        return self.acquire()

    def __exit__(self, *_exc: object) -> None:
        self.release()


@contextmanager
def _ledger_lock(ledger_path: Path, *, nonblocking: bool = False):
    """Reuse the current thread's held writer lease or acquire a short lock."""

    existing = _current_writer_lease(ledger_path)
    if existing is not None:
        yield existing.descriptor
        return
    lease = CalibrationWriterLease(ledger_path)
    try:
        lease.acquire(nonblocking=nonblocking)
        yield lease.descriptor
    finally:
        lease.release()


def writer_lease_is_live(ledger_path: Path = DEFAULT_LEDGER_PATH) -> bool:
    """Return a diagnostic liveness snapshot; never use it to authorize ARM."""

    if _current_writer_lease(ledger_path) is not None:
        return False
    lease = CalibrationWriterLease(Path(ledger_path))
    try:
        try:
            lease.acquire(nonblocking=True)
        except CalibrationLedgerError as exc:
            if exc.code != RefusalCode.LIVE_WRITER_CONTENTION:
                raise
            return True
        return False
    finally:
        lease.release()


def _open_ledger_append_descriptor(ledger_path: Path) -> int:
    lease = _current_writer_lease(Path(ledger_path))
    if lease is None:
        raise AssertionError("ledger append attempted without the current writer lease")
    return lease.open_append_descriptor()


def _verify_current_writer_lease_for_handle(handle: BinaryIO) -> None:
    try:
        status = os.fstat(handle.fileno())
    except (AttributeError, OSError):
        return
    key: _LeaseRegistryKey = ("object", status.st_dev, status.st_ino)
    with _ACTIVE_WRITER_LEASES_GUARD:
        lease = _ACTIVE_WRITER_LEASES.get(key)
    if lease is not None and lease._owner_thread == threading.get_ident():
        lease._verify_current_path()


def _fsync_parent_directory(path: Path) -> None:
    """Confirm a directory entry, retrying the complete fsync operation once."""

    failure: OSError | None = None
    for _attempt in range(2):
        descriptor = -1
        try:
            descriptor = os.open(
                Path(path),
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
            )
            os.fsync(descriptor)
            return
        except OSError as exc:
            failure = exc
        finally:
            if descriptor >= 0:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
    assert failure is not None
    raise failure


def _write_bootstrap_payload(handle: BinaryIO, payload: bytes) -> None:
    written = handle.write(payload)
    if written != len(payload):
        raise OSError("short historical import write")


def _reauthenticate_historical_import_plan(plan: HistoricalImportPlan) -> None:
    """Re-open every planned artifact without following links and hash it."""

    finalizations = [
        receipt
        for receipt in plan.receipts
        if receipt.get("event") == HISTORICAL_IMPORT_FINALIZATION_EVENT
    ]
    for receipt in finalizations:
        locator = Path(str(receipt["custody_locator"]))
        raw = _governed_raw_nofollow(locator)
        observed = {
            name: hashlib.sha256(value).hexdigest() for name, value in raw.items()
        }
        if observed != dict(receipt["artifact_sha256"]):
            raise CalibrationLedgerError(
                f"execute-time custody reauthentication failed: {locator}"
            )


def bootstrap_historical_import(
    ledger_path: Path,
    *,
    head_pin_path: Path,
    roots: Sequence[Path] = (),
    checkout_root: Path = REPO_ROOT,
    disposition_table_raw: bytes,
    expected_disposition_table_sha256: str,
    custody_manifest_raw: bytes,
    expected_custody_manifest_sha256: str,
    execute: bool = False,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> HistoricalImportPlan:
    """Prepare, and only when requested atomically append, the genesis import.

    Dry-run is the default and creates no path. Execution stages and fsyncs the
    complete chain outside the reader-visible ledger path, then atomically
    replaces the empty ledger. The head pin is never written.
    """

    ledger = Path(ledger_path)
    pin = Path(head_pin_path)
    _require_genesis_bootstrap_state(
        ledger,
        pin,
        require_committed_pin=require_committed_pin,
        repo_root=Path(repo_root),
        allow_nonempty_pending_plan=execute,
    )
    plan = prepare_historical_import(
        roots=roots,
        checkout_root=checkout_root,
        disposition_table_raw=disposition_table_raw,
        expected_disposition_table_sha256=expected_disposition_table_sha256,
        custody_manifest_raw=custody_manifest_raw,
        expected_custody_manifest_sha256=expected_custody_manifest_sha256,
    )
    if not execute:
        return plan

    payload = plan.ledger_bytes
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with CalibrationWriterLease(ledger) as lease:
        already_committed = _require_genesis_bootstrap_state(
            ledger,
            pin,
            require_committed_pin=require_committed_pin,
            repo_root=Path(repo_root),
            expected_payload=payload,
        )
        _reauthenticate_historical_import_plan(plan)
        if already_committed:
            try:
                _fsync_parent_directory(ledger.parent)
            except OSError as exc:
                raise HistoricalImportDurabilityUncertain(plan) from exc
            return plan

        try:
            lease.publish_genesis_payload(payload)
        except _LedgerPublicationDurabilityUncertain as exc:
            raise HistoricalImportDurabilityUncertain(plan) from exc
        except Exception as exc:
            raise CalibrationLedgerError(
                "historical import append failed atomically"
            ) from exc
        try:
            _fsync_parent_directory(ledger.parent)
        except OSError as exc:
            raise HistoricalImportDurabilityUncertain(plan) from exc
    return plan


def _write_ledger_append_payload(handle: BinaryIO, payload: bytes) -> None:
    """Single injectable physical append boundary used by crash regressions."""

    written = handle.write(payload)
    if written != len(payload):
        raise OSError("short ledger append")


def _after_ledger_fsync(stage: str) -> None:
    """Injectable post-fsync crash boundary; intentionally a no-op."""

    del stage


def _append_and_fsync(
    handle: BinaryIO,
    payload: bytes,
    *,
    stage: str,
    boundary: Any | None = None,
) -> None:
    _verify_current_writer_lease_for_handle(handle)
    handle.seek(0, os.SEEK_END)
    if boundary is not None:
        boundary(f"{stage}-write")
    _write_ledger_append_payload(handle, payload)
    handle.flush()
    os.fsync(handle.fileno())
    _after_ledger_fsync(stage)
    if boundary is not None:
        boundary(f"{stage}-fsynced")


def _new_append_intent(
    *,
    receipts: Sequence[Mapping[str, Any]],
    byte_offset: int,
    target_core: Mapping[str, Any],
    operation_key: Mapping[str, Any],
) -> dict[str, Any]:
    predecessor = (
        str(receipts[-1]["receipt_digest"]) if receipts else GENESIS_DIGEST
    )
    base_head = {
        "sequence": len(receipts),
        "digest": predecessor,
        "byte_offset": byte_offset,
    }
    target_commitment = canonical_sha256(target_core)
    ledger_id = _derived_ledger_id(receipts)
    receipt: dict[str, Any] = {
        "schema_version": CONTROL_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "sequence": len(receipts) + 1,
        "predecessor_digest": predecessor,
        "event": APPEND_INTENT_EVENT,
        "ledger_id": ledger_id,
        "base_head": base_head,
        "operation_key": dict(operation_key),
        "target_schema_version": target_core["schema_version"],
        "target_event": target_core["event"],
        "target_core": _jsonable(target_core),
        "target_core_sha256": target_commitment,
        "operation_id": _operation_id(
            ledger_id=ledger_id,
            base_head=base_head,
            operation_key=operation_key,
            target_core_sha256=target_commitment,
        ),
    }
    receipt["receipt_digest"] = _receipt_digest(receipt)
    return receipt


def _legacy_journal_metadata(path: Path) -> Mapping[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CalibrationLedgerError(RefusalCode.LEGACY_JOURNAL_UNREADABLE) from exc
    tail = raw[-64:]
    return {
        "path": str(path),
        "length": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "observed_tail_hex": tail.hex(),
        "observed_tail_sha256": hashlib.sha256(tail).hexdigest(),
    }


def _new_abandonment_receipt(
    *,
    receipts: Sequence[Mapping[str, Any]],
    residue_start_offset: int,
    residue: bytes,
    receipt_offset: int,
    reason_code: str,
    active_intent: Mapping[str, Any] | None,
    actor_type: str,
    actor_identity: str,
    attestation_reason: str,
    legacy_journal: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    predecessor = (
        str(receipts[-1]["receipt_digest"]) if receipts else GENESIS_DIGEST
    )
    receipt: dict[str, Any] = {
        "schema_version": CONTROL_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "sequence": len(receipts) + 1,
        "predecessor_digest": predecessor,
        "event": ABANDONMENT_EVENT,
        "abandoned_predecessor_sequence": len(receipts),
        "abandoned_predecessor_digest": predecessor,
        "residue_start_offset": residue_start_offset,
        "residue_length": len(residue),
        "residue_sha256": hashlib.sha256(residue).hexdigest(),
        "receipt_offset": receipt_offset,
        "reason_code": reason_code,
        "known_operation_id": (
            active_intent.get("operation_id") if active_intent else None
        ),
        "known_target_core_sha256": (
            active_intent.get("target_core_sha256") if active_intent else None
        ),
        "actor_type": actor_type,
        "actor_identity": actor_identity,
        "policy_revision": APPEND_POLICY_REVISION,
        "attestation_reason": attestation_reason,
        "legacy_journal": (
            dict(legacy_journal) if legacy_journal is not None else None
        ),
    }
    receipt["receipt_digest"] = _receipt_digest(receipt)
    return receipt


def _append_abandonment(
    handle: BinaryIO,
    raw: bytes,
    physical: _PhysicalLedger,
    *,
    reason_code: str,
    actor_type: str,
    actor_identity: str,
    attestation_reason: str,
    legacy_journal: Mapping[str, Any] | None = None,
) -> bytes:
    residue = physical.residue
    separator = b"" if not residue or residue.endswith(b"\n") else b"\n"
    receipt_offset = len(raw) + len(separator)
    receipt = _new_abandonment_receipt(
        receipts=physical.receipts,
        residue_start_offset=physical.residue_start_offset,
        residue=residue,
        receipt_offset=receipt_offset,
        reason_code=reason_code,
        active_intent=physical.active_intent,
        actor_type=actor_type,
        actor_identity=actor_identity,
        attestation_reason=attestation_reason,
        legacy_journal=legacy_journal,
    )
    payload = separator + canonical_json_bytes(receipt) + b"\n"
    _append_and_fsync(handle, payload, stage="abandonment")
    return raw + payload


def _migrate_legacy_journal(
    ledger_path: Path,
    handle: BinaryIO,
    raw: bytes,
    physical: _PhysicalLedger,
) -> tuple[bytes, _PhysicalLedger]:
    path = _legacy_append_journal_path(ledger_path)
    if not path.exists():
        return raw, physical
    metadata = _legacy_journal_metadata(path)
    already_recorded = any(
        receipt.get("event") == ABANDONMENT_EVENT
        and isinstance(receipt.get("legacy_journal"), Mapping)
        and receipt["legacy_journal"].get("sha256") == metadata["sha256"]
        and receipt["legacy_journal"].get("path") == metadata["path"]
        for receipt in physical.receipts
    )
    if already_recorded:
        _archive_legacy_journal(path, str(metadata["sha256"]))
        return raw, physical
    if physical.residue:
        return raw, physical
    archive = path.with_name(
        f"{path.name}.archived-{str(metadata['sha256'])[:16]}"
    )
    if archive.exists():
        raise CalibrationLedgerError(RefusalCode.LEGACY_JOURNAL_ARCHIVE_CONFLICT)
    try:
        parent_mode = path.parent.stat().st_mode
    except OSError as exc:
        raise CalibrationLedgerError(
            RefusalCode.LEGACY_JOURNAL_ARCHIVE_FAILED
        ) from exc
    if parent_mode & 0o222 == 0:
        raise CalibrationLedgerError(RefusalCode.LEGACY_JOURNAL_ARCHIVE_FAILED)
    raw = _append_abandonment(
        handle,
        raw,
        physical,
        reason_code="legacy-journal-observed-never-replayed",
        actor_type="engine",
        actor_identity="joulewise.calibration_ledger",
        attestation_reason=(
            "legacy sidecar bytes were hashed and preserved without payload replay"
        ),
        legacy_journal=metadata,
    )
    _archive_legacy_journal(path, str(metadata["sha256"]))
    return raw, _scan_physical_ledger(raw)


def _archive_legacy_journal(path: Path, digest: str) -> Path:
    archive = path.with_name(f"{path.name}.archived-{digest[:16]}")
    if archive.exists():
        raise CalibrationLedgerError(RefusalCode.LEGACY_JOURNAL_ARCHIVE_CONFLICT)
    try:
        os.replace(path, archive)
        _fsync_parent_directory(path.parent)
    except OSError as exc:
        raise CalibrationLedgerError(RefusalCode.LEGACY_JOURNAL_ARCHIVE_FAILED) from exc
    return archive


def _repair_locked(
    ledger_path: Path,
    handle: BinaryIO,
    raw: bytes,
    *,
    engine_identity: str,
    attestation_reason: str,
) -> tuple[bytes, _PhysicalLedger]:
    for _step in range(8):
        physical = _scan_physical_ledger(raw)
        raw, physical = _migrate_legacy_journal(
            ledger_path, handle, raw, physical
        )
        if physical.residue:
            if physical.active_intent is not None:
                target = _intent_target_receipt(
                    physical.active_intent,
                    sequence=len(physical.receipts) + 1,
                    predecessor_digest=str(
                        physical.receipts[-1]["receipt_digest"]
                    ),
                )
                target_payload = canonical_json_bytes(target) + b"\n"
                if target_payload.startswith(physical.residue):
                    missing = target_payload[len(physical.residue) :]
                    if missing:
                        _append_and_fsync(handle, missing, stage="target")
                        raw += missing
                    continue
                raw = _append_abandonment(
                    handle,
                    raw,
                    physical,
                    reason_code="intent-target-mismatch",
                    actor_type="engine",
                    actor_identity=engine_identity,
                    attestation_reason=attestation_reason,
                )
                continue
            if not raw.endswith(b"\n"):
                raw = _append_abandonment(
                    handle,
                    raw,
                    physical,
                    reason_code="torn-uncommitted-record",
                    actor_type="engine",
                    actor_identity=engine_identity,
                    attestation_reason=attestation_reason,
                )
                continue
            raise CalibrationLedgerError(RefusalCode.TAIL_REQUIRES_ABANDON)
        if physical.active_intent is not None:
            predecessor = str(physical.receipts[-1]["receipt_digest"])
            target = _intent_target_receipt(
                physical.active_intent,
                sequence=len(physical.receipts) + 1,
                predecessor_digest=predecessor,
            )
            if (
                target.get("schema_version") == CONTROL_SCHEMA
                and target.get("event") == APPEND_INTENT_EVENT
            ):
                # A durable intent whose committed target is another intent
                # cannot reduce to one business operation. This shape is not
                # emitted by any writer, but hostile authenticated bytes must
                # still reach the typed nonconvergence backstop.
                raise CalibrationLedgerError(RefusalCode.RECOVERY_NONCONVERGENT)
            if not _valid_receipt_shape(target):
                raise CalibrationLedgerError(RefusalCode.INTENT_TARGET_MALFORMED)
            payload = canonical_json_bytes(target) + b"\n"
            _append_and_fsync(handle, payload, stage="target")
            raw += payload
            continue
        return raw, physical
    raise CalibrationLedgerError(RefusalCode.RECOVERY_NONCONVERGENT)


def _completed_operation(
    receipts: Sequence[Mapping[str, Any]], operation_selector: Any
) -> tuple[Mapping[str, Any], Mapping[str, Any]] | None:
    for index, receipt in enumerate(receipts):
        if (
            receipt.get("event") == APPEND_INTENT_EVENT
            and operation_selector(receipt["operation_key"])
        ):
            for candidate in receipts[index + 1 :]:
                if candidate.get("schema_version") == CONTROL_SCHEMA:
                    continue
                if _target_core(candidate) == dict(receipt["target_core"]):
                    return receipt, candidate
                break
    return None


def _inspection_from_physical(
    physical: _PhysicalLedger,
    *,
    legacy_path: Path | None = None,
) -> CalibrationLedgerInspection:
    active = physical.active_intent
    if physical.residue:
        state = "residue"
    elif active is not None:
        state = "intent"
    else:
        state = "clean"
    legacy_sha: str | None = None
    if legacy_path is not None and legacy_path.exists():
        legacy_sha = str(_legacy_journal_metadata(legacy_path)["sha256"])
    return CalibrationLedgerInspection(
        state=state,
        ledger_id=physical.ledger_id,
        head_sequence=len(physical.receipts),
        head_digest=(
            str(physical.receipts[-1]["receipt_digest"])
            if physical.receipts
            else GENESIS_DIGEST
        ),
        valid_end_offset=physical.valid_end_offset,
        residue_start_offset=physical.residue_start_offset,
        residue_length=len(physical.residue),
        residue_sha256=hashlib.sha256(physical.residue).hexdigest(),
        active_operation_id=(
            str(active["operation_id"]) if active is not None else None
        ),
        active_operation_key=(
            _frozen_mapping(active["operation_key"])
            if active is not None
            else None
        ),
        target_core_sha256=(
            str(active["target_core_sha256"]) if active is not None else None
        ),
        legacy_journal_path=(
            str(legacy_path)
            if legacy_path is not None and legacy_path.exists()
            else None
        ),
        legacy_journal_sha256=legacy_sha,
    )


def inspect_calibration_ledger(
    ledger_path: Path = DEFAULT_LEDGER_PATH,
) -> CalibrationLedgerInspection:
    """Inspect physical recovery state without changing any byte."""

    ledger = Path(ledger_path)
    try:
        raw = ledger.read_bytes() if ledger.exists() else b""
    except OSError as exc:
        raise CalibrationLedgerError(RefusalCode.PHYSICAL_LEDGER_UNREADABLE) from exc
    return _inspection_from_physical(
        _scan_physical_ledger(raw),
        legacy_path=_legacy_append_journal_path(ledger),
    )


def repair_calibration_ledger(
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    *,
    engine_identity: str = "joulewise.recovery-engine",
    attestation_reason: str = "deterministic ledger-only recovery",
) -> CalibrationLedgerInspection:
    """Converge every mechanically recoverable state under the ledger lock."""

    if not engine_identity or not attestation_reason:
        raise CalibrationLedgerError(RefusalCode.RECOVERY_CREDENTIALS_INVALID)
    ledger = Path(ledger_path)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with _ledger_lock(ledger):
        descriptor = _open_ledger_append_descriptor(ledger)
        try:
            with os.fdopen(descriptor, "r+b", closefd=False) as handle:
                raw = handle.read()
                raw, physical = _repair_locked(
                    ledger,
                    handle,
                    raw,
                    engine_identity=engine_identity,
                    attestation_reason=attestation_reason,
                )
                return _inspection_from_physical(
                    physical,
                    legacy_path=_legacy_append_journal_path(ledger),
                )
        finally:
            os.close(descriptor)


def _physical_chain_contains_pin(
    receipts: Sequence[Mapping[str, Any]], pin: tuple[int, str]
) -> bool:
    sequence, digest = pin
    if sequence == 0:
        return digest == GENESIS_DIGEST
    return (
        len(receipts) >= sequence
        and receipts[sequence - 1].get("sequence") == sequence
        and receipts[sequence - 1].get("receipt_digest") == digest
    )


def abandon_calibration_ledger_tail(
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    *,
    operator_identity: str,
    attestation_reason: str,
    reason_code: str = "operator-attested-tail-abandonment",
    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> CalibrationLedgerInspection:
    """Authenticate only the residue after the maximal valid chain."""

    if not operator_identity or not attestation_reason or not reason_code:
        raise CalibrationLedgerError(RefusalCode.ABANDON_CREDENTIALS_INVALID)
    pin = _authenticated_head_pin(
        Path(head_pin_path),
        require_committed_pin=require_committed_pin,
        repo_root=Path(repo_root),
    )
    ledger = Path(ledger_path)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with _ledger_lock(ledger):
        try:
            descriptor = _open_ledger_append_descriptor(ledger)
        except OSError as exc:
            raise CalibrationLedgerError(RefusalCode.ABANDON_NOT_CLEAN) from exc
        try:
            with os.fdopen(descriptor, "r+b", closefd=False) as handle:
                raw = handle.read()
                physical = _scan_physical_ledger(raw)
                if not _physical_chain_contains_pin(physical.receipts, pin):
                    raise CalibrationLedgerError(RefusalCode.ABANDON_PIN_MISMATCH)
                malformed_intent = False
                if physical.active_intent is not None:
                    target = _intent_target_receipt(
                        physical.active_intent,
                        sequence=len(physical.receipts) + 1,
                        predecessor_digest=str(
                            physical.receipts[-1]["receipt_digest"]
                        ),
                    )
                    malformed_intent = not _valid_receipt_shape(target)
                if physical.active_intent is not None and not malformed_intent:
                    raise CalibrationLedgerError(RefusalCode.ABANDON_ACTIVE_INTENT)
                if not physical.residue and not malformed_intent:
                    return _inspection_from_physical(physical)
                raw = _append_abandonment(
                    handle,
                    raw,
                    physical,
                    reason_code=(
                        "admitted-malformed-intent-quarantine"
                        if malformed_intent
                        else reason_code
                    ),
                    actor_type="operator",
                    actor_identity=operator_identity,
                    attestation_reason=attestation_reason,
                )
                final = _scan_physical_ledger(raw)
                if final.residue or final.active_intent is not None:
                    raise CalibrationLedgerError(RefusalCode.ABANDON_NOT_CLEAN)
                return _inspection_from_physical(final)
        except OSError as exc:
            raise CalibrationLedgerError(RefusalCode.ABANDON_NOT_CLEAN) from exc
        finally:
            os.close(descriptor)


def _locked_append(
    ledger_path: Path,
    build: Any,
    *,
    operation_key: Mapping[str, Any] | None,
    completed_matches: Any,
    operation_selector: Any | None = None,
    nonblocking: bool = False,
    stage_boundary: Any | None = None,
    conflict_code: RefusalCode = RefusalCode.LEDGER_OPERATION_CONFLICT,
) -> Mapping[str, Any]:
    ledger_path = Path(ledger_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with _ledger_lock(ledger_path, nonblocking=nonblocking):
        descriptor = _open_ledger_append_descriptor(ledger_path)
        try:
            with os.fdopen(descriptor, "r+b", closefd=False) as handle:
                handle.seek(0)
                raw = handle.read()
                raw, physical = _repair_locked(
                    ledger_path,
                    handle,
                    raw,
                    engine_identity="joulewise.calibration_ledger",
                    attestation_reason="automatic deterministic append recovery",
                )
                selector = operation_selector or (
                    lambda key: dict(key) == dict(operation_key or {})
                )
                completed = _completed_operation(physical.receipts, selector)
                if completed is not None:
                    intent, target = completed
                    if not completed_matches(intent["target_core"]):
                        raise CalibrationLedgerError(conflict_code)
                    return _frozen_mapping(target)
                receipt = build(physical.receipts)
                if not _valid_receipt_shape(receipt) or receipt.get(
                    "schema_version"
                ) == CONTROL_SCHEMA:
                    raise CalibrationLedgerError(RefusalCode.LEDGER_MALFORMED)
                target_core = _target_core(receipt)
                actual_operation_key = _operation_key_for_core(target_core)
                if operation_key is not None and actual_operation_key != dict(operation_key):
                    raise CalibrationLedgerError(conflict_code)
                intent = _new_append_intent(
                    receipts=physical.receipts,
                    byte_offset=len(raw),
                    target_core=target_core,
                    operation_key=actual_operation_key,
                )
                intent_payload = canonical_json_bytes(intent) + b"\n"
                _append_and_fsync(
                    handle,
                    intent_payload,
                    stage="intent",
                    boundary=stage_boundary,
                )
                raw += intent_payload
                target = _intent_target_receipt(
                    intent,
                    sequence=len(physical.receipts) + 2,
                    predecessor_digest=str(intent["receipt_digest"]),
                )
                target_payload = canonical_json_bytes(target) + b"\n"
                _append_and_fsync(
                    handle,
                    target_payload,
                    stage="target",
                    boundary=stage_boundary,
                )
                raw += target_payload
                final = _scan_physical_ledger(raw)
                if final.reasons or final.active_intent is not None:
                    raise CalibrationLedgerError(RefusalCode.RECOVERY_NONCONVERGENT)
                return _frozen_mapping(target)
        finally:
            os.close(descriptor)


def _authenticated_head_pin(
    head_pin_path: Path,
    *,
    require_committed_pin: bool,
    repo_root: Path,
) -> tuple[int, str]:
    pin_path = Path(head_pin_path)
    try:
        pin_raw = pin_path.read_bytes()
        pin_value = json.loads(pin_raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CalibrationLedgerError(RefusalCode.HEAD_PIN_UNREADABLE) from exc
    pin = _head_pin(pin_value)
    if pin is None:
        raise CalibrationLedgerError(RefusalCode.HEAD_PIN_MALFORMED)
    if require_committed_pin and _committed_pin_bytes(pin_path, repo_root) != pin_raw:
        raise CalibrationLedgerError(RefusalCode.HEAD_PIN_NOT_COMMITTED)
    return pin


def validate_bracket_session_reservation_inputs(
    *,
    session_id: str,
    window_id: str,
    plan_id: str,
    plan_sha256: str,
    evidence_root_id: str,
    runs_root: Path | str,
    slots: Mapping[str, Mapping[str, Any]],
) -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
    """Apply the exact same capability-input validation for dry-run/execute."""

    try:
        normalized_runs_root = normalize_calibration_custody_path(runs_root)
    except CalibrationLedgerError as exc:
        raise CalibrationLedgerError(RefusalCode.RESERVATION_INPUT_INVALID) from exc
    session_identity = {
        "session_id": session_id,
        "window_id": window_id,
        "plan_id": plan_id,
        "plan_sha256": plan_sha256,
        "evidence_root_id": evidence_root_id,
        "runs_root": normalized_runs_root,
    }
    normalized_slots: dict[str, dict[str, Any]] = {}
    if not isinstance(slots, Mapping) or set(slots) != set(BRACKET_SESSION_SLOTS):
        raise CalibrationLedgerError(RefusalCode.RESERVATION_INPUT_INVALID)
    validation_root = Path(normalized_runs_root) / "instrument_validation"
    for role in BRACKET_SESSION_SLOTS:
        source = slots.get(role)
        if not isinstance(source, Mapping):
            raise CalibrationLedgerError(
                RefusalCode.RESERVATION_INPUT_INVALID,
                context={"slot": role},
            )
        custody_value = source.get("custody_locator")
        try:
            custody = Path(normalize_calibration_custody_path(custody_value))
            custody.relative_to(validation_root)
        except (CalibrationLedgerError, OSError, TypeError, ValueError) as exc:
            raise CalibrationLedgerError(
                RefusalCode.RESERVATION_INPUT_INVALID,
                context={"slot": role, "reason": "custody_outside_runs_root"},
            ) from exc
        normalized_slots[role] = {
            "attempt_id": source.get("attempt_id"),
            "custody_locator": str(custody),
            "identity_epoch": _normalized_vector(
                source.get("identity_epoch"), IDENTITY_EPOCH_FIELDS
            ),
            "t1_bindings": _normalized_vector(source.get("t1_bindings"), T1_FIELDS),
            "expected_time_role": role,
        }
    if not _valid_session_identity(session_identity) or any(
        not _valid_session_slot_reservation(normalized_slots[role], role)
        for role in BRACKET_SESSION_SLOTS
    ):
        raise CalibrationLedgerError(RefusalCode.RESERVATION_INPUT_INVALID)
    if normalized_slots["pre"]["attempt_id"] == normalized_slots["post"]["attempt_id"]:
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_INPUT_INVALID,
            context={"reason": "slot_attempts_not_distinct"},
        )
    return _frozen_mapping(session_identity), _frozen_mapping(normalized_slots)


def append_bracket_session_receipt(
    ledger_path: Path,
    *,
    session_id: str,
    window_id: str,
    plan_id: str,
    plan_sha256: str,
    evidence_root_id: str,
    runs_root: Path | str,
    slots: Mapping[str, Mapping[str, Any]],
    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
    _stage_boundary: Any | None = None,
) -> Mapping[str, Any]:
    """Atomically reserve exactly one immutable pre/post bracket capability.

    Physical-head equality with the committed pin is checked here, at open,
    and deliberately not checked again while either already-reserved slot is
    finalized. Claim evaluation remains impossible until the terminal head
    pin is emitted, reviewed, and committed.
    """

    session_identity, normalized_slots = validate_bracket_session_reservation_inputs(
        session_id=session_id,
        window_id=window_id,
        plan_id=plan_id,
        plan_sha256=plan_sha256,
        evidence_root_id=evidence_root_id,
        runs_root=runs_root,
        slots=slots,
    )
    pin = _authenticated_head_pin(
        Path(head_pin_path),
        require_committed_pin=require_committed_pin,
        repo_root=Path(repo_root),
    )

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        if (len(receipts), predecessor) != pin:
            raise CalibrationLedgerError(RefusalCode.RESERVATION_HEAD_MISMATCH)
        observations, sessions, reasons = _attempts_and_observations(receipts)
        del observations
        if reasons:
            raise CalibrationLedgerError(_primary_refusal(reasons))
        reserved_attempts = {
            attempt_id
            for session in sessions
            for attempt_id in session.slot_attempt_ids.values()
        }
        ordinary_attempts = {
            str(receipt["attempt_id"])
            for receipt in receipts
            if receipt.get("schema_version") == RECEIPT_SCHEMA
        }
        proposed_attempts = {
            normalized_slots[role]["attempt_id"] for role in BRACKET_SESSION_SLOTS
        }
        if (
            any(session.session_id == session_id for session in sessions)
            or proposed_attempts & (reserved_attempts | ordinary_attempts)
        ):
            raise CalibrationLedgerError(RefusalCode.RESERVATION_IDENTITY_CONFLICT)
        return _new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event=BRACKET_SESSION_OPEN_EVENT,
            session_identity=session_identity,
            fields={"slots": normalized_slots},
        )

    expected_core = _target_core(
        _new_bracket_session_record(
            sequence=1,
            predecessor_digest=GENESIS_DIGEST,
            event=BRACKET_SESSION_OPEN_EVENT,
            session_identity=session_identity,
            fields={"slots": normalized_slots},
        )
    )
    operation_key = _operation_key_for_core(expected_core)
    return _locked_append(
        Path(ledger_path),
        build,
        operation_key=operation_key,
        completed_matches=lambda core: dict(core) == expected_core,
        stage_boundary=_stage_boundary,
        conflict_code=RefusalCode.RESERVATION_IDENTITY_CONFLICT,
    )


def claim_bracket_session_slot(
    ledger_path: Path,
    *,
    session_id: str,
    slot: str,
    attempt_id: str,
    claim_id: str | None = None,
    _stage_boundary: Any | None = None,
) -> Mapping[str, Any]:
    """Append one deterministic claim while liveness is owned by the lease."""

    if slot not in BRACKET_SESSION_SLOTS:
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_INPUT_INVALID,
            context={"slot": slot},
        )
    expected_claim_id = stable_bracket_claim_id(
        session_id=session_id,
        slot=slot,
        attempt_id=attempt_id,
    )
    if claim_id is not None and claim_id != expected_claim_id:
        raise CalibrationLedgerError(RefusalCode.CLAIM_ID_INVALID)
    claim_id = expected_claim_id

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        observations, sessions, reasons = _attempts_and_observations(receipts)
        del observations
        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
        if non_open_reasons:
            raise CalibrationLedgerError(_primary_refusal(non_open_reasons))
        session = next(
            (item for item in sessions if item.session_id == session_id), None
        )
        if session is None or session.state != "open":
            raise CalibrationLedgerError(RefusalCode.SESSION_NOT_OPEN)
        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
        if slot != expected_slot or session.slot_attempt_ids.get(slot) != attempt_id:
            raise CalibrationLedgerError(
                RefusalCode.SLOT_ORDER_CONFLICT,
                context={
                    "detail": f"expected {expected_slot}",
                    "expected_slot": expected_slot,
                    "slot": slot,
                },
            )
        existing = [
            receipt
            for receipt in receipts
            if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
            and receipt.get("event") == BRACKET_SESSION_SLOT_CLAIM_EVENT
            and receipt.get("session_id") == session_id
            and receipt.get("slot") == slot
        ]
        if existing:
            raise CalibrationLedgerError(RefusalCode.LEDGER_BRACKET_SLOT_CLAIMED)
        open_receipt = next(
            receipt
            for receipt in receipts
            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
            and receipt.get("session_id") == session_id
        )
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        return _new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event=BRACKET_SESSION_SLOT_CLAIM_EVENT,
            session_identity={
                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
            },
            fields={
                "slot": slot,
                "attempt_id": attempt_id,
                "claim_id": claim_id,
            },
        )

    operation_key = {
        "event": BRACKET_SESSION_SLOT_CLAIM_EVENT,
        "session_id": session_id,
        "slot": slot,
        "attempt_id": attempt_id,
    }
    return _locked_append(
        Path(ledger_path),
        build,
        operation_key=operation_key,
        completed_matches=lambda core: (
            core.get("event") == BRACKET_SESSION_SLOT_CLAIM_EVENT
            and core.get("session_id") == session_id
            and core.get("slot") == slot
            and core.get("attempt_id") == attempt_id
            and core.get("claim_id") == claim_id
        ),
        stage_boundary=_stage_boundary,
        conflict_code=RefusalCode.CLAIM_ID_INVALID,
    )


def finalize_bracket_session_slot(
    ledger_path: Path,
    *,
    session_id: str,
    slot: str,
    disposition: str,
    custody_locator: str,
    artifact_sha256: Mapping[str, str] | None = None,
    identity_epoch: Mapping[str, Any] | None = None,
    t1_bindings: Mapping[str, Any] | None = None,
    capture_wall_time_s: str | None = None,
    exact_bound_lexeme_s: str | None = None,
    _stage_boundary: Any | None = None,
) -> Mapping[str, Any]:
    """Fill exactly one reserved session slot in mandatory pre/post order."""

    if slot not in BRACKET_SESSION_SLOTS:
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_INPUT_INVALID,
            context={"slot": slot},
        )
    if disposition not in FINAL_DISPOSITIONS:
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_INPUT_INVALID,
            context={"disposition": disposition},
        )
    artifacts = dict(artifact_sha256 or {})
    content_id = content_id_from_artifact_hashes(artifacts)
    normalized_epoch = _normalized_vector(identity_epoch, IDENTITY_EPOCH_FIELDS)
    normalized_t1 = _normalized_vector(t1_bindings, T1_FIELDS)

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        observations, sessions, reasons = _attempts_and_observations(receipts)
        del observations
        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
        if non_open_reasons:
            raise CalibrationLedgerError(_primary_refusal(non_open_reasons))
        by_id = {session.session_id: session for session in sessions}
        session = by_id.get(session_id)
        if session is None or session.state != "open":
            raise CalibrationLedgerError(RefusalCode.SESSION_NOT_OPEN)
        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
        if slot != expected_slot or slot in session.finalized_slots:
            raise CalibrationLedgerError(
                RefusalCode.SLOT_ORDER_CONFLICT,
                context={
                    "detail": f"expected {expected_slot}",
                    "expected_slot": expected_slot,
                    "slot": slot,
                },
            )
        open_receipt = next(
            receipt
            for receipt in receipts
            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
            and receipt.get("session_id") == session_id
        )
        reserved = open_receipt["slots"][slot]
        if (
            reserved["custody_locator"] != custody_locator
            or dict(reserved["identity_epoch"]) != normalized_epoch
            or dict(reserved["t1_bindings"]) != normalized_t1
        ):
            raise CalibrationLedgerError(RefusalCode.FINALIZATION_BINDING_CONFLICT)
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        return _new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event=BRACKET_SESSION_FINALIZATION_EVENT,
            session_identity={
                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
            },
            fields={
                "slot": slot,
                "attempt_id": reserved["attempt_id"],
                "content_id": content_id,
                "artifact_sha256": dict(sorted(artifacts.items())),
                "identity_epoch": normalized_epoch,
                "t1_bindings": normalized_t1,
                "capture_wall_time_s": capture_wall_time_s,
                "exact_bound_lexeme_s": exact_bound_lexeme_s,
                "disposition": disposition,
                "custody_locator": custody_locator,
            },
        )

    return _locked_append(
        Path(ledger_path),
        build,
        operation_key=None,
        operation_selector=lambda key: (
            key.get("event") == BRACKET_SESSION_FINALIZATION_EVENT
            and key.get("session_id") == session_id
            and key.get("slot") == slot
        ),
        completed_matches=lambda core: (
            core.get("event") == BRACKET_SESSION_FINALIZATION_EVENT
            and core.get("session_id") == session_id
            and core.get("slot") == slot
            and core.get("disposition") == disposition
            and core.get("custody_locator") == custody_locator
            and dict(core.get("artifact_sha256", {})) == dict(sorted(artifacts.items()))
            and dict(core.get("identity_epoch", {})) == normalized_epoch
            and dict(core.get("t1_bindings", {})) == normalized_t1
            and core.get("capture_wall_time_s") == capture_wall_time_s
            and core.get("exact_bound_lexeme_s") == exact_bound_lexeme_s
        ),
        stage_boundary=_stage_boundary,
        conflict_code=RefusalCode.FINALIZATION_BINDING_CONFLICT,
    )


def abort_bracket_session(
    ledger_path: Path,
    *,
    session_id: str,
    reason: str,
) -> Mapping[str, Any]:
    """Append a governed terminal closure without deleting partial receipts."""

    if not isinstance(reason, str) or not reason:
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_INPUT_INVALID,
            context={"reason": "empty_abort_reason"},
        )

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        observations, sessions, reasons = _attempts_and_observations(receipts)
        del observations
        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
        if non_open_reasons:
            raise CalibrationLedgerError(_primary_refusal(non_open_reasons))
        session = next(
            (item for item in sessions if item.session_id == session_id), None
        )
        if session is None or session.state != "open":
            raise CalibrationLedgerError(RefusalCode.SESSION_NOT_OPEN)
        open_receipt = next(
            receipt
            for receipt in receipts
            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
            and receipt.get("session_id") == session_id
        )
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        finalized_slots = list(session.finalized_slots)
        return _new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event=BRACKET_SESSION_ABORT_EVENT,
            session_identity={
                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
            },
            fields={
                "finalized_slots": finalized_slots,
                "unused_slots": [
                    role for role in BRACKET_SESSION_SLOTS if role not in finalized_slots
                ],
                "reason": reason,
            },
        )

    operation_key = {
        "event": BRACKET_SESSION_ABORT_EVENT,
        "session_id": session_id,
        "slot": None,
        "attempt_id": None,
    }
    return _locked_append(
        Path(ledger_path),
        build,
        operation_key=operation_key,
        completed_matches=lambda core: (
            core.get("event") == BRACKET_SESSION_ABORT_EVENT
            and core.get("session_id") == session_id
            and core.get("reason") == reason
        ),
        nonblocking=True,
    )


def terminal_head_pin_for_session(
    ledger_path: Path,
    *,
    session_id: str,
) -> dict[str, Any]:
    """Return the sole terminal pin candidate after post or governed abort."""

    try:
        raw = Path(ledger_path).read_bytes()
    except OSError as exc:
        raise CalibrationLedgerError(RefusalCode.PHYSICAL_LEDGER_UNREADABLE) from exc
    receipts, parse_reasons = _parse_ledger(raw)
    observations, sessions, state_reasons = _attempts_and_observations(receipts)
    del observations
    reasons = (parse_reasons | state_reasons) - {
        RefusalCode.LEDGER_BRACKET_SESSION_OPEN.value,
    }
    if reasons:
        raise CalibrationLedgerError(_primary_refusal(reasons))
    session = next((item for item in sessions if item.session_id == session_id), None)
    if session is None or session.state == "open":
        raise CalibrationLedgerError(RefusalCode.SESSION_NOT_TERMINAL)
    terminal_digest = (
        session.finalized_slots["post"].receipt_digest
        if session.state == "finalized"
        else session.abort_receipt_digest
    )
    terminal_index = next(
        (
            index
            for index, receipt in enumerate(receipts)
            if receipt.get("receipt_digest") == terminal_digest
        ),
        None,
    )
    if terminal_index is None or any(
        receipt.get("schema_version") != CONTROL_SCHEMA
        for receipt in receipts[terminal_index + 1 :]
    ):
        raise CalibrationLedgerError(RefusalCode.SESSION_TERMINAL_NOT_HEAD)
    final = receipts[-1]
    return _head_pin_for_valid_receipt(final)


def _pin_relation(snapshot: CalibrationLedgerSnapshot) -> PinRelation:
    pinned = (
        int(snapshot.committed_head_sequence or 0),
        str(snapshot.committed_head_digest or GENESIS_DIGEST),
    )
    physical = (snapshot.head_sequence, snapshot.head_digest)
    if physical == pinned:
        return PinRelation.EXACT
    if _physical_chain_contains_pin(snapshot.receipts, pinned):
        return PinRelation.PHYSICAL_AHEAD
    if (
        snapshot.head_sequence < pinned[0]
        and _physical_chain_contains_pin(snapshot.receipts, physical)
    ):
        return PinRelation.PHYSICAL_BEHIND
    return PinRelation.DIVERGENT


def _session_open_receipt(
    snapshot: CalibrationLedgerSnapshot, session_id: str
) -> Mapping[str, Any] | None:
    return next(
        (
            receipt
            for receipt in snapshot.receipts
            if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
            and receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
            and receipt.get("session_id") == session_id
        ),
        None,
    )


def validate_frozen_reservation_plan(
    plan_path: Path, *, expected_sha256: str, expected_plan_id: str
) -> Mapping[str, Any]:
    try:
        raw = Path(plan_path).read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CalibrationLedgerError(RefusalCode.PLAN_UNREADABLE) from exc
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise CalibrationLedgerError(RefusalCode.PLAN_HASH_MISMATCH)
    if not isinstance(value, Mapping) or value.get("plan_id") != expected_plan_id:
        raise CalibrationLedgerError(RefusalCode.PLAN_HASH_MISMATCH)
    return _frozen_mapping(value)


def _custody_state(path: Path) -> str:
    try:
        if not path.exists():
            return "absent"
        if not path.is_dir():
            return "unreadable"
        present = {name for name in GOVERNED_ARTIFACTS if (path / name).is_file()}
    except OSError:
        return "unreadable"
    if not present:
        return "empty"
    if present == set(GOVERNED_ARTIFACTS):
        try:
            raw_by_name = _governed_raw_nofollow(path)
            manifest = json.loads(raw_by_name["manifest.json"])
            evidence = json.loads(raw_by_name["instrument_evidence.json"])
        except (CalibrationLedgerError, UnicodeDecodeError, json.JSONDecodeError):
            return "unreadable"
        if not isinstance(manifest, Mapping) or not isinstance(evidence, Mapping):
            return "unreadable"
        return "complete"
    return "partial"


def calibration_session_status(
    ledger_path: Path,
    head_pin_path: Path,
    *,
    session_id: str,
    plan_path: Path | None = None,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Derive session progress solely from durable ledger/plan/custody state."""

    inspection = inspect_calibration_ledger(ledger_path)
    snapshot = load_calibration_ledger_snapshot(
        ledger_path,
        head_pin_path,
        require_committed_pin=require_committed_pin,
        verify_custody=False,
        repo_root=repo_root,
    )
    session = snapshot.bracket_session_by_id.get(session_id)
    if session is None:
        raise CalibrationLedgerError(RefusalCode.SESSION_NOT_FOUND)
    if plan_path is not None:
        validate_frozen_reservation_plan(
            plan_path,
            expected_sha256=session.plan_sha256,
            expected_plan_id=session.plan_id,
        )
    open_receipt = _session_open_receipt(snapshot, session_id)
    slots: dict[str, Any] = {}
    for slot in BRACKET_SESSION_SLOTS:
        reserved = (
            open_receipt.get("slots", {}).get(slot)
            if isinstance(open_receipt, Mapping)
            and isinstance(open_receipt.get("slots"), Mapping)
            else None
        )
        locator = (
            Path(str(reserved.get("custody_locator")))
            if isinstance(reserved, Mapping)
            else None
        )
        slots[slot] = {
            "attempt_id": session.slot_attempt_ids.get(slot),
            "custody_locator": str(locator) if locator is not None else None,
            "custody_state": _custody_state(locator) if locator is not None else None,
            "finalized": slot in session.finalized_slots,
        }
    next_slot = (
        BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
        if session.state == "open" and len(session.finalized_slots) < len(BRACKET_SESSION_SLOTS)
        else None
    )
    live_writer = writer_lease_is_live(ledger_path)
    actionable: RefusalCode | None = None
    unexpected = set(snapshot.refusal_reasons) - {
        RefusalCode.LEDGER_BRACKET_SESSION_OPEN.value,
        RefusalCode.LEDGER_HEAD_MISMATCH.value,
    }
    if unexpected:
        actionable = RefusalCode(_primary_refusal(unexpected))
    elif inspection.state != "clean" or inspection.legacy_journal_path is not None:
        actionable = RefusalCode.LEDGER_RECOVERY_REQUIRED
    elif live_writer:
        actionable = RefusalCode.LIVE_WRITER_CONTENTION
    elif next_slot is not None and slots[next_slot]["custody_state"] == "complete":
        actionable = RefusalCode.CUSTODY_COMPLETE_USE_RESUME
    elif next_slot is not None and slots[next_slot]["custody_state"] in {
        "empty",
        "partial",
        "unreadable",
    }:
        actionable = (
            RefusalCode.CUSTODY_UNREADABLE
            if slots[next_slot]["custody_state"] == "unreadable"
            else RefusalCode.CUSTODY_PARTIAL
        )
    elif session.state != "open" and _pin_relation(snapshot) is PinRelation.PHYSICAL_AHEAD:
        actionable = RefusalCode.LEDGER_HEAD_MISMATCH
    route = REFUSAL_BY_CODE.get(actionable) if actionable is not None else None
    return {
        "status": "session_status",
        "session_id": session.session_id,
        "session_state": session.state,
        "abort_reason": session.abort_reason,
        "plan_id": session.plan_id,
        "plan_sha256": session.plan_sha256,
        "inspection_state": inspection.state,
        "legacy_journal_path": inspection.legacy_journal_path,
        "pin_relation": _pin_relation(snapshot).value,
        "next_slot": next_slot,
        "slots": slots,
        "live_writer": live_writer,
        "refusal_code": actionable.value if actionable is not None else None,
        "exit_id": route.exit_id if route is not None else None,
        "next_command": route.command if route is not None else None,
        "arm_blocked": route.arm_blocked if route is not None else False,
        "terminal_head_pin_candidate": (
            terminal_head_pin_for_session(ledger_path, session_id=session_id)
            if session.state != "open" and inspection.state == "clean"
            else None
        ),
    }


def calibration_readiness(
    ledger_path: Path,
    head_pin_path: Path,
    *,
    phase: str,
    session_id: str | None = None,
    slot: str | None = None,
    attempt_id: str | None = None,
    enforcing_under_lease: bool = False,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> CalibrationReadiness:
    """Evaluate the D-117 composite readiness predicate for one exact phase."""

    if phase not in {"pre-reserve", "pre-slot", "terminal"}:
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_INPUT_INVALID,
            context={"phase": phase},
        )
    if enforcing_under_lease and _current_writer_lease(ledger_path) is None:
        raise CalibrationLedgerError(RefusalCode.PRE_SLOT_NOT_READY)
    inspection = inspect_calibration_ledger(ledger_path)
    snapshot = load_calibration_ledger_snapshot(
        ledger_path,
        head_pin_path,
        require_committed_pin=require_committed_pin,
        # The enforcing gate authenticates every finalized observation in the
        # snapshot, not merely the custody path for the upcoming slot.
        verify_custody=enforcing_under_lease,
        repo_root=repo_root,
    )
    relation = _pin_relation(snapshot)
    common_blocked = inspection.state != "clean" or inspection.legacy_journal_path is not None
    live_writer = (
        False
        if enforcing_under_lease
        else writer_lease_is_live(ledger_path)
    )
    refusal: RefusalCode | None = None
    next_slot: str | None = None
    expected_attempt: str | None = None
    custody_state: str | None = None
    claim_state: str | None = None
    candidate: Mapping[str, Any] | None = None

    if phase == "pre-reserve":
        open_sessions = [item for item in snapshot.bracket_sessions if item.state == "open"]
        unexpected = set(snapshot.refusal_reasons) - {
            RefusalCode.LEDGER_HEAD_MISMATCH.value,
            RefusalCode.LEDGER_BRACKET_SESSION_OPEN.value,
        }
        if unexpected:
            refusal = RefusalCode(_primary_refusal(unexpected))
        elif common_blocked:
            refusal = RefusalCode.LEDGER_RECOVERY_REQUIRED
        elif live_writer:
            refusal = RefusalCode.LIVE_WRITER_CONTENTION
        elif open_sessions:
            refusal = RefusalCode.PRE_RESERVE_NOT_READY
        elif relation is not PinRelation.EXACT:
            refusal = RefusalCode.RESERVATION_HEAD_MISMATCH
    elif phase == "pre-slot":
        session = snapshot.bracket_session_by_id.get(str(session_id))
        open_receipt = (
            _session_open_receipt(snapshot, str(session_id)) if session is not None else None
        )
        if session is not None and session.state == "open":
            next_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
            expected_attempt = session.slot_attempt_ids.get(next_slot)
            reserved = (
                open_receipt.get("slots", {}).get(next_slot)
                if isinstance(open_receipt, Mapping)
                and isinstance(open_receipt.get("slots"), Mapping)
                else None
            )
            if isinstance(reserved, Mapping):
                custody_state = _custody_state(Path(str(reserved["custody_locator"])))
            claims = [
                receipt
                for receipt in snapshot.receipts
                if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
                and receipt.get("event") == BRACKET_SESSION_SLOT_CLAIM_EVENT
                and receipt.get("session_id") == str(session_id)
                and receipt.get("slot") == next_slot
            ]
            if not claims:
                claim_state = "absent"
            elif len(claims) == 1 and claims[0].get("claim_id") == stable_bracket_claim_id(
                session_id=str(session_id),
                slot=str(next_slot),
                attempt_id=str(expected_attempt),
            ):
                claim_state = "exact_completed"
            else:
                claim_state = "conflict"
        unexpected = set(snapshot.refusal_reasons) - {
            RefusalCode.LEDGER_BRACKET_SESSION_OPEN.value,
            RefusalCode.LEDGER_HEAD_MISMATCH.value,
        }
        if unexpected:
            refusal = RefusalCode(_primary_refusal(unexpected))
        elif common_blocked:
            refusal = RefusalCode.LEDGER_RECOVERY_REQUIRED
        elif live_writer:
            refusal = RefusalCode.LIVE_WRITER_CONTENTION
        elif relation is not PinRelation.PHYSICAL_AHEAD:
            refusal = (
                RefusalCode.LEDGER_ROLLBACK
                if relation is PinRelation.PHYSICAL_BEHIND
                else RefusalCode.LEDGER_HEAD_MISMATCH
            )
        elif custody_state == "complete":
            refusal = RefusalCode.CUSTODY_COMPLETE_USE_RESUME
        elif custody_state in {"empty", "partial", "unreadable"}:
            refusal = (
                RefusalCode.CUSTODY_UNREADABLE
                if custody_state == "unreadable"
                else RefusalCode.CUSTODY_PARTIAL
            )
        elif claim_state == "conflict":
            refusal = RefusalCode.CLAIM_ID_INVALID
        elif (
            session is None
            or session.state != "open"
            or slot != next_slot
            or attempt_id != expected_attempt
            or not snapshot.is_governed_open_bracket_extension
        ):
            refusal = RefusalCode.PRE_SLOT_NOT_READY
    else:
        session = snapshot.bracket_session_by_id.get(str(session_id))
        if session is not None and session.state != "open" and not common_blocked:
            try:
                candidate = terminal_head_pin_for_session(
                    ledger_path, session_id=str(session_id)
                )
            except CalibrationLedgerError:
                candidate = None
        unexpected = set(snapshot.refusal_reasons) - {
            RefusalCode.LEDGER_HEAD_MISMATCH.value,
        }
        if unexpected:
            refusal = RefusalCode(_primary_refusal(unexpected))
        elif common_blocked:
            refusal = RefusalCode.LEDGER_RECOVERY_REQUIRED
        elif live_writer:
            refusal = RefusalCode.LIVE_WRITER_CONTENTION
        elif relation not in {PinRelation.EXACT, PinRelation.PHYSICAL_AHEAD}:
            refusal = (
                RefusalCode.LEDGER_ROLLBACK
                if relation is PinRelation.PHYSICAL_BEHIND
                else RefusalCode.LEDGER_HEAD_MISMATCH
            )
        elif (
            session is None
            or session.state == "open"
            or candidate is None
        ):
            refusal = RefusalCode.TERMINAL_NOT_READY

    return CalibrationReadiness(
        phase=phase,
        status="ready" if refusal is None else "blocked",
        pin_relation=relation,
        refusal_code=refusal,
        session_id=session_id,
        next_slot=next_slot,
        attempt_id=expected_attempt,
        custody_state=custody_state,
        claim_state=claim_state,
        needs_pin_commit=relation is PinRelation.PHYSICAL_AHEAD,
        head_pin_candidate=candidate,
        enforcing_under_lease=enforcing_under_lease,
    )


def advance_calibration_head_pin(
    ledger_path: Path,
    head_pin_path: Path,
    *,
    session_id: str | None,
    expected_sequence: int,
    expected_digest: str,
    operator_identity: str,
    attestation_reason: str,
    execute: bool = False,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> Mapping[str, Any]:
    """Guarded desk-only advancement to an authenticated terminal head."""

    if not operator_identity or not attestation_reason:
        raise CalibrationLedgerError(RefusalCode.ABANDON_CREDENTIALS_INVALID)
    with CalibrationWriterLease(ledger_path):
        current_pin = _authenticated_head_pin(
            Path(head_pin_path),
            require_committed_pin=require_committed_pin,
            repo_root=Path(repo_root),
        )
        inspection = inspect_calibration_ledger(ledger_path)
        if inspection.state != "clean" or inspection.legacy_journal_path is not None:
            raise CalibrationLedgerError(RefusalCode.PIN_ADVANCEMENT_UNSAFE)
        snapshot = load_calibration_ledger_snapshot(
            ledger_path,
            head_pin_path,
            require_committed_pin=require_committed_pin,
            verify_custody=True,
            repo_root=repo_root,
        )
        if _pin_relation(snapshot) is not PinRelation.PHYSICAL_AHEAD:
            raise CalibrationLedgerError(RefusalCode.PIN_ADVANCEMENT_NOT_NEEDED)
        if not _physical_chain_contains_pin(snapshot.receipts, current_pin):
            raise CalibrationLedgerError(RefusalCode.PIN_ADVANCEMENT_UNSAFE)
        if session_id is None:
            # Sessionless advancement is only for a clean recovery-shaped
            # control tail.  Ordinary pending/open/refusal state is never a
            # candidate merely because its bytes authenticate.
            allowed_reasons = {RefusalCode.LEDGER_HEAD_MISMATCH.value}
            terminal = snapshot.receipts[-1] if snapshot.receipts else None
            if (
                set(snapshot.refusal_reasons) - allowed_reasons
                or any(session.state == "open" for session in snapshot.bracket_sessions)
                or not isinstance(terminal, Mapping)
                or terminal.get("schema_version") != CONTROL_SCHEMA
                or terminal.get("event") != ABANDONMENT_EVENT
            ):
                raise CalibrationLedgerError(RefusalCode.PIN_ADVANCEMENT_UNSAFE)
            candidate = {
                "sequence": inspection.head_sequence,
                "head_digest": inspection.head_digest,
                "ledger_schema": LEDGER_SCHEMA,
            }
        else:
            candidate = terminal_head_pin_for_session(
                ledger_path, session_id=session_id
            )
        if (
            candidate["sequence"] != expected_sequence
            or candidate["head_digest"] != expected_digest
        ):
            raise CalibrationLedgerError(RefusalCode.PIN_CANDIDATE_MISMATCH)
        result = {
            **candidate,
            "operator_identity": operator_identity,
            "attestation_reason": attestation_reason,
            "previous_sequence": current_pin[0],
            "previous_head_digest": current_pin[1],
            "executed": execute,
        }
        if execute:
            payload = json.dumps(candidate, indent=2, sort_keys=False).encode("utf-8") + b"\n"
            pin_path = Path(head_pin_path)
            pin_path.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{pin_path.name}.advance-", dir=pin_path.parent
            )
            temporary = Path(temporary_name)
            try:
                with os.fdopen(descriptor, "wb") as handle:
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, pin_path)
                _fsync_parent_directory(pin_path.parent)
            finally:
                if temporary.exists():
                    temporary.unlink()
        return _frozen_mapping(result)


def resume_finalize_bracket_session(
    ledger_path: Path,
    head_pin_path: Path,
    *,
    session_id: str,
    slot: str,
    plan_path: Path,
    systematic_screen_s: Decimal,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> Mapping[str, Any]:
    """Finalize authenticated complete custody from a fresh process."""

    with CalibrationWriterLease(ledger_path):
        repair_calibration_ledger(
            ledger_path,
            engine_identity="recover_calibration_ledger.resume-finalize",
            attestation_reason="fresh-process deterministic finalization",
        )
        snapshot = load_calibration_ledger_snapshot(
            ledger_path,
            head_pin_path,
            require_committed_pin=require_committed_pin,
            verify_custody=False,
            repo_root=repo_root,
        )
        session = snapshot.bracket_session_by_id.get(session_id)
        if session is None:
            raise CalibrationLedgerError(RefusalCode.SESSION_NOT_FOUND)
        validate_frozen_reservation_plan(
            plan_path,
            expected_sha256=session.plan_sha256,
            expected_plan_id=session.plan_id,
        )
        if session.state != "open":
            raise CalibrationLedgerError(RefusalCode.SESSION_NOT_OPEN)
        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
        if slot != expected_slot:
            raise CalibrationLedgerError(
                RefusalCode.SLOT_ORDER_CONFLICT,
                context={"expected_slot": expected_slot, "slot": slot},
            )
        open_receipt = _session_open_receipt(snapshot, session_id)
        assert open_receipt is not None
        reserved = open_receipt["slots"][slot]
        custody = Path(str(reserved["custody_locator"]))
        state = _custody_state(custody)
        if state != "complete":
            raise CalibrationLedgerError(
                RefusalCode.CUSTODY_PARTIAL
                if state in {"absent", "empty", "partial"}
                else RefusalCode.CUSTODY_UNREADABLE
            )
        try:
            raw_by_name = _governed_raw_nofollow(custody)
            manifest = json.loads(raw_by_name["manifest.json"])
            evidence = json.loads(raw_by_name["instrument_evidence.json"])
        except (CalibrationLedgerError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CalibrationLedgerError(RefusalCode.CUSTODY_UNREADABLE) from exc
        if not isinstance(manifest, Mapping) or not isinstance(evidence, Mapping):
            raise CalibrationLedgerError(RefusalCode.CUSTODY_UNREADABLE)
        hashes = {
            name: hashlib.sha256(raw).hexdigest()
            for name, raw in raw_by_name.items()
        }
        manifest_hashes = manifest.get("artifacts")
        evidence_hashes = evidence.get("artifact_sha256")
        if (
            not isinstance(manifest_hashes, Mapping)
            or any(manifest_hashes.get(name) != hashes[name] for name in MANIFEST_BOUND_ARTIFACTS)
            or not isinstance(evidence_hashes, Mapping)
            or any(evidence_hashes.get(name) != hashes[name] for name in EVIDENCE_BOUND_ARTIFACTS)
            or evidence.get("validation_id") != reserved["attempt_id"]
            or manifest.get("validation_id") != reserved["attempt_id"]
        ):
            raise CalibrationLedgerError(RefusalCode.CUSTODY_UNREADABLE)
        if (
            _normalized_vector(evidence.get("bindings"), T1_FIELDS)
            != dict(reserved["t1_bindings"])
        ):
            # The manifest authenticates the evidence bytes and the evidence
            # authenticates the governed artifacts.  A mismatch against the
            # reserved binding is therefore a finalization conflict, not
            # structurally unreadable custody.  This refusal precedes claim.
            raise CalibrationLedgerError(
                RefusalCode.FINALIZATION_BINDING_CONFLICT
            )
        try:
            lexemes = _number_lexemes(
                raw_by_name["instrument_evidence.json"],
                custody / "instrument_evidence.json",
            )
            capture_wall_time_s = lexemes.get("capture_wall_time_s")
            exact_bound_lexeme_s = lexemes.get("b_fiducial_s")
            if not isinstance(capture_wall_time_s, str):
                raise ValueError("capture time missing")
            bound = (
                Decimal(exact_bound_lexeme_s)
                if isinstance(exact_bound_lexeme_s, str)
                else None
            )
        except (CalibrationLedgerError, InvalidOperation, ValueError) as exc:
            raise CalibrationLedgerError(RefusalCode.CUSTODY_UNREADABLE) from exc
        status = evidence.get("status")
        if status not in {"valid", "invalid"}:
            raise CalibrationLedgerError(RefusalCode.CUSTODY_UNREADABLE)
        disposition = "ordinary-invalid"
        if status == "valid":
            disposition = (
                "systematic-invalid"
                if bound is not None and bound > systematic_screen_s
                else "valid"
            )
        claim_bracket_session_slot(
            ledger_path,
            session_id=session_id,
            slot=slot,
            attempt_id=str(reserved["attempt_id"]),
        )
        receipt = finalize_bracket_session_slot(
            ledger_path,
            session_id=session_id,
            slot=slot,
            disposition=disposition,
            custody_locator=str(custody),
            artifact_sha256=hashes,
            identity_epoch=reserved["identity_epoch"],
            t1_bindings=reserved["t1_bindings"],
            capture_wall_time_s=capture_wall_time_s,
            exact_bound_lexeme_s=exact_bound_lexeme_s,
        )
        terminal_result = "operation_completed"
        if slot == "pre" and disposition != "valid":
            receipt = abort_bracket_session(
                ledger_path,
                session_id=session_id,
                reason=f"pre_capture_{disposition}",
            )
            terminal_result = "session_aborted"
        candidate = (
            None
            if slot == "pre" and disposition == "valid"
            else terminal_head_pin_for_session(ledger_path, session_id=session_id)
        )
        return _frozen_mapping(
            {
                "status": "finalized",
                "terminal_result": terminal_result,
                "session_id": session_id,
                "slot": slot,
                "disposition": disposition,
                "receipt": receipt,
                "head_pin_candidate": candidate,
                "needs_pin_commit": candidate is not None,
            }
        )


def abort_calibration_session(
    ledger_path: Path,
    head_pin_path: Path,
    *,
    session_id: str,
    reason: str,
    plan_path: Path,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> Mapping[str, Any]:
    """Abort an open session under the writer lease without deleting custody."""

    with CalibrationWriterLease(ledger_path):
        repair_calibration_ledger(
            ledger_path,
            engine_identity="recover_calibration_ledger.abort-session",
            attestation_reason="fresh-process governed session abort",
        )
        status = calibration_session_status(
            ledger_path,
            head_pin_path,
            session_id=session_id,
            plan_path=plan_path,
            require_committed_pin=require_committed_pin,
            repo_root=repo_root,
        )
        if status["session_state"] != "open":
            terminal_result = (
                "session_aborted"
                if status["session_state"] == "aborted"
                else "operation_completed"
            )
            return _frozen_mapping(
                {
                    "status": status["session_state"],
                    "terminal_result": terminal_result,
                    "session_id": session_id,
                    "receipt": None,
                    "head_pin_candidate": status["terminal_head_pin_candidate"],
                    "custody_preserved": True,
                    "needs_pin_commit": status["pin_relation"] == "physical_ahead",
                    "idempotent": True,
                }
            )
        next_slot = status["next_slot"]
        if next_slot is not None:
            custody_state = status["slots"][next_slot]["custody_state"]
            if custody_state == "complete":
                raise CalibrationLedgerError(RefusalCode.CUSTODY_COMPLETE_USE_RESUME)
        receipt = abort_bracket_session(
            ledger_path,
            session_id=session_id,
            reason=reason,
        )
        return _frozen_mapping(
            {
                "status": "aborted",
                "terminal_result": "session_aborted",
                "session_id": session_id,
                "receipt": receipt,
                "head_pin_candidate": terminal_head_pin_for_session(
                    ledger_path, session_id=session_id
                ),
                "custody_preserved": True,
                "needs_pin_commit": True,
            }
        )


def append_pending_receipt(
    ledger_path: Path,
    *,
    attempt_id: str,
    custody_locator: str,
    identity_epoch: Mapping[str, Any] | None = None,
    t1_bindings: Mapping[str, Any] | None = None,
    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> Mapping[str, Any]:
    """Reserve an attempt before any capture directory or sampler exists.

    This closes workflow omission, unregistered evidence, and rollback or
    stale-head consumption; it does not defend against a malicious trusted
    writer or a rewrite of both Git and the full ledger history.
    """

    if not isinstance(attempt_id, str) or not attempt_id:
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_INPUT_INVALID,
            context={"reason": "attempt_id_empty"},
        )
    pin_path = Path(head_pin_path)
    try:
        pin_raw = pin_path.read_bytes()
        pin_value = json.loads(pin_raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CalibrationLedgerError(RefusalCode.HEAD_PIN_UNREADABLE) from exc
    pin = _head_pin(pin_value)
    if pin is None:
        raise CalibrationLedgerError(RefusalCode.HEAD_PIN_MALFORMED)
    if require_committed_pin and _committed_pin_bytes(pin_path, repo_root) != pin_raw:
        raise CalibrationLedgerError(RefusalCode.HEAD_PIN_NOT_COMMITTED)

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        sequence = len(receipts) + 1
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        if (len(receipts), predecessor) != pin:
            raise CalibrationLedgerError(RefusalCode.RESERVATION_HEAD_MISMATCH)
        observations, bracket_sessions, reasons = _attempts_and_observations(receipts)
        del observations
        del bracket_sessions
        if reasons or any(
            row.get("attempt_id") == attempt_id
            or any(
                isinstance(slot, Mapping) and slot.get("attempt_id") == attempt_id
                for slot in (
                    row.get("slots", {}).values()
                    if isinstance(row.get("slots"), Mapping)
                    else ()
                )
            )
            for row in receipts
        ):
            raise CalibrationLedgerError(
                _primary_refusal(
                    reasons or {"calibration_ledger_attempt_conflict"}
                )
            )
        return _new_receipt(
            sequence=sequence,
            predecessor_digest=str(predecessor),
            event="reservation",
            attempt_id=attempt_id,
            content_id=None,
            artifacts={},
            identity_epoch=identity_epoch,
            t1_bindings=t1_bindings,
            capture_wall_time_s=None,
            exact_bound_lexeme_s=None,
            disposition="pending",
            custody_locator=custody_locator,
        )

    expected_core = _target_core(
        _new_receipt(
            sequence=1,
            predecessor_digest=GENESIS_DIGEST,
            event="reservation",
            attempt_id=attempt_id,
            content_id=None,
            artifacts={},
            identity_epoch=identity_epoch,
            t1_bindings=t1_bindings,
            capture_wall_time_s=None,
            exact_bound_lexeme_s=None,
            disposition="pending",
            custody_locator=custody_locator,
        )
    )
    operation_key = _operation_key_for_core(expected_core)
    return _locked_append(
        Path(ledger_path),
        build,
        operation_key=operation_key,
        completed_matches=lambda core: dict(core) == expected_core,
    )


def finalize_attempt_receipt(
    ledger_path: Path,
    *,
    attempt_id: str,
    disposition: str,
    custody_locator: str,
    artifact_sha256: Mapping[str, str] | None = None,
    identity_epoch: Mapping[str, Any] | None = None,
    t1_bindings: Mapping[str, Any] | None = None,
    capture_wall_time_s: str | None = None,
    exact_bound_lexeme_s: str | None = None,
) -> Mapping[str, Any]:
    """Append the sole final state for a previously reserved attempt."""

    if disposition not in FINAL_DISPOSITIONS:
        raise CalibrationLedgerError(
            RefusalCode.RESERVATION_INPUT_INVALID,
            context={"disposition": disposition},
        )
    artifacts = dict(artifact_sha256 or {})
    content_id = content_id_from_artifact_hashes(artifacts)

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        observations, bracket_sessions, reasons = _attempts_and_observations(
            receipts
        )
        del observations, bracket_sessions
        unexpected_reasons = reasons - {"calibration_ledger_pending"}
        if unexpected_reasons:
            raise CalibrationLedgerError(_primary_refusal(unexpected_reasons))
        reservations = [
            row
            for row in receipts
            if row.get("attempt_id") == attempt_id and row["event"] == "reservation"
        ]
        finals = [
            row
            for row in receipts
            if row.get("attempt_id") == attempt_id and row["event"] == "finalization"
        ]
        if len(reservations) != 1 or finals:
            raise CalibrationLedgerError(RefusalCode.LEDGER_ATTEMPT_CONFLICT)
        reservation = reservations[0]
        normalized_epoch = _normalized_vector(
            identity_epoch, IDENTITY_EPOCH_FIELDS
        )
        normalized_t1 = _normalized_vector(t1_bindings, T1_FIELDS)
        if (
            dict(reservation["identity_epoch"]) != normalized_epoch
            or dict(reservation["t1_bindings"]) != normalized_t1
            or reservation["custody_locator"] != custody_locator
        ):
            raise CalibrationLedgerError(RefusalCode.FINALIZATION_BINDING_CONFLICT)
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        return _new_receipt(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event="finalization",
            attempt_id=attempt_id,
            content_id=content_id,
            artifacts=artifacts,
            identity_epoch=identity_epoch,
            t1_bindings=t1_bindings,
            capture_wall_time_s=capture_wall_time_s,
            exact_bound_lexeme_s=exact_bound_lexeme_s,
            disposition=disposition,
            custody_locator=custody_locator,
        )

    expected_core = _target_core(
        _new_receipt(
            sequence=1,
            predecessor_digest=GENESIS_DIGEST,
            event="finalization",
            attempt_id=attempt_id,
            content_id=content_id,
            artifacts=artifacts,
            identity_epoch=identity_epoch,
            t1_bindings=t1_bindings,
            capture_wall_time_s=capture_wall_time_s,
            exact_bound_lexeme_s=exact_bound_lexeme_s,
            disposition=disposition,
            custody_locator=custody_locator,
        )
    )
    operation_key = _operation_key_for_core(expected_core)
    return _locked_append(
        Path(ledger_path),
        build,
        operation_key=operation_key,
        completed_matches=lambda core: dict(core) == expected_core,
    )


def _head_pin_for_valid_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not _valid_receipt_shape(receipt):
        raise CalibrationLedgerError(RefusalCode.LEDGER_MALFORMED)
    return {
        "sequence": int(receipt["sequence"]),
        "head_digest": str(receipt["receipt_digest"]),
        "ledger_schema": LEDGER_SCHEMA,
    }


def head_pin_for_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Emit a pin for an ordinary receipt, never a mid-session receipt."""

    if receipt.get("event") == APPEND_INTENT_EVENT:
        raise CalibrationLedgerError(RefusalCode.LEDGER_RECOVERY_REQUIRED)
    if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
        raise CalibrationLedgerError(RefusalCode.SESSION_NOT_TERMINAL)
    return _head_pin_for_valid_receipt(receipt)


__all__ = [
    "ABANDONMENT_EVENT",
    "ALL_DISPOSITIONS",
    "APPEND_INTENT_EVENT",
    "APPEND_POLICY_REVISION",
    "CLAIM_POLICY_REVISION",
    "APPEND_RECORDS_PER_OPERATION",
    "BRACKET_SESSION_ABORT_EVENT",
    "BRACKET_SESSION_FINALIZATION_EVENT",
    "BRACKET_SESSION_OPEN_EVENT",
    "BRACKET_SESSION_SLOT_CLAIM_EVENT",
    "BRACKET_SESSION_SCHEMA",
    "BRACKET_SESSION_SLOTS",
    "CONTENT_ID_ARTIFACTS",
    "CONTROL_SCHEMA",
    "DEFAULT_HEAD_PIN_PATH",
    "DEFAULT_LEDGER_PATH",
    "FINAL_DISPOSITIONS",
    "GENESIS_DIGEST",
    "GOVERNED_ARTIFACTS",
    "HISTORICAL_IMPORT_EVENT_PREFIX",
    "HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA",
    "HISTORICAL_IMPORT_FINALIZATION_EVENT",
    "HISTORICAL_IMPORT_RESERVATION_EVENT",
    "HISTORICAL_IMPORT_TABLE_SCHEMA",
    "IDENTITY_EPOCH_FIELDS",
    "LEDGER_SCHEMA",
    "RECEIPT_SCHEMA",
    "REFUSAL_TAXONOMY",
    "CalibrationLedgerError",
    "CalibrationLedgerInspection",
    "CalibrationReadiness",
    "CalibrationWriterLease",
    "CalibrationBracketSession",
    "CalibrationLedgerSnapshot",
    "HistoricalImportDurabilityUncertain",
    "HistoricalImportPlan",
    "LedgerObservation",
    "PinRelation",
    "abort_calibration_session",
    "append_pending_receipt",
    "abandon_calibration_ledger_tail",
    "append_bracket_session_receipt",
    "advance_calibration_head_pin",
    "calibration_readiness",
    "calibration_session_status",
    "canonical_json_bytes",
    "claim_bracket_session_slot",
    "abort_bracket_session",
    "artifact_hashes",
    "bootstrap_historical_import",
    "custody_manifest_bytes",
    "canonical_sha256",
    "content_id_from_artifact_hashes",
    "finalize_attempt_receipt",
    "finalize_bracket_session_slot",
    "generate_historical_custody_manifest",
    "head_pin_for_receipt",
    "inspect_calibration_ledger",
    "load_calibration_ledger_snapshot",
    "normalize_calibration_custody_path",
    "prepare_historical_import",
    "repair_calibration_ledger",
    "resume_finalize_bracket_session",
    "stable_bracket_claim_id",
    "terminal_head_pin_for_session",
    "validate_bracket_session_reservation_inputs",
    "validate_frozen_reservation_plan",
    "writer_lease_is_live",
]
