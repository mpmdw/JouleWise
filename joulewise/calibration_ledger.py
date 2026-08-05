"""Authenticated calibration-observation receipt ledger (D-109).

The ledger closes workflow omission, unregistered evidence, and rollback or
stale-head consumption.  It does not defend against a malicious trusted
writer or an authority that rewrites both Git and the complete ledger
history.  Version 1 is deliberately a single-authority, single-machine
protocol.

Each capture is represented by two immutable hash-chained receipts: a
reservation with disposition ``pending`` written before capture state exists,
then exactly one finalization.  Evaluation consumes one frozen snapshot whose
physical head must equal the repository-committed head pin.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS


LEDGER_SCHEMA = "joulewise.calibration_observation_ledger.v1"
RECEIPT_SCHEMA = "joulewise.calibration_observation_receipt.v1"
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
ALL_DISPOSITIONS = FINAL_DISPOSITIONS | {"pending"}
CONTENT_ID_ARTIFACTS = (
    "instrument_evidence.json",
    "manifest.json",
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

# Stable refusal taxonomy.  Consumers propagate these exact spellings into
# claim barriers; no malformed or unresolved history is silently omitted.
REFUSAL_TAXONOMY: Mapping[str, str] = MappingProxyType(
    {
        "calibration_ledger_missing": "the pinned non-genesis ledger is absent",
        "calibration_ledger_malformed": "ledger, receipt, or head-pin schema is malformed",
        "calibration_ledger_chain_conflict": "sequence or predecessor linkage is not one linear chain",
        "calibration_ledger_attempt_conflict": "an attempt has duplicate or conflicting state transitions",
        "calibration_ledger_content_conflict": "one content identity has conflicting authenticated classifications",
        "calibration_ledger_pending": "at least one reservation is unresolved",
        "calibration_ledger_head_uncommitted": "the head pin differs from the Git HEAD bytes",
        "calibration_ledger_head_mismatch": "the physical head differs from the committed pin",
        "calibration_ledger_rollback": "the physical ledger is a proper prefix of the pinned head",
        "calibration_ledger_baseline_missing": "the acceptance cutoff is not in the current chain",
        "calibration_ledger_custody_invalid": "receipt-bound evidence bytes are absent or hash-invalid",
        "calibration_ledger_snapshot_required": "claim evaluation did not receive one immutable snapshot",
        "calibration_ledger_off_ledger_artifact": "a calibration artifact is not registered in the snapshot",
        "calibration_observation_unclassifiable": "a governed observation has no ruled disposition",
    }
)


class CalibrationLedgerError(ValueError):
    """A writer-side ledger operation cannot preserve the D-109 contract."""


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
    for relative in (
        "raw/powermetrics.plist",
        "events.jsonl",
        "power_trace.csv",
        "instrument_evidence.json",
        "manifest.json",
    ):
        path = root / relative
        if path.is_file():
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


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

    @property
    def classification_disposition(self) -> str:
        """Map the writer terminal state onto the R2 observation schema."""

        return (
            "unresolved" if self.disposition == "abandoned" else self.disposition
        )


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
    baseline_sequence: int | None = None
    baseline_digest: str | None = None

    @property
    def valid(self) -> bool:
        return not self.refusal_reasons

    @property
    def observation_by_attempt(self) -> Mapping[str, LedgerObservation]:
        return MappingProxyType(
            {observation.attempt_id: observation for observation in self.observations}
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


def _valid_receipt_shape(receipt: object) -> bool:
    if not isinstance(receipt, Mapping) or set(receipt) != _RECEIPT_KEYS:
        return False
    sequence = receipt.get("sequence")
    event = receipt.get("event")
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
        or event not in {"reservation", "finalization"}
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
    if event == "reservation":
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


def _parse_ledger(raw: bytes) -> tuple[list[Mapping[str, Any]], set[str]]:
    receipts: list[Mapping[str, Any]] = []
    reasons: set[str] = set()
    if not raw:
        return receipts, reasons
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return receipts, {"calibration_ledger_malformed"}
    if not text.endswith("\n"):
        reasons.add("calibration_ledger_malformed")
    predecessor = GENESIS_DIGEST
    expected_sequence = 1
    seen_digests: set[str] = set()
    for line in text.splitlines():
        if not line.strip():
            reasons.add("calibration_ledger_malformed")
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            reasons.add("calibration_ledger_malformed")
            continue
        if not _valid_receipt_shape(value):
            reasons.add("calibration_ledger_malformed")
            continue
        if (
            value["sequence"] != expected_sequence
            or value["predecessor_digest"] != predecessor
            or value["receipt_digest"] in seen_digests
        ):
            reasons.add("calibration_ledger_chain_conflict")
        expected_sequence += 1
        predecessor = value["receipt_digest"]
        seen_digests.add(predecessor)
        receipts.append(value)
    return receipts, reasons


def _attempts_and_observations(
    receipts: Sequence[Mapping[str, Any]],
) -> tuple[list[LedgerObservation], set[str]]:
    pending: dict[str, Mapping[str, Any]] = {}
    finalized: dict[str, Mapping[str, Any]] = {}
    reasons: set[str] = set()
    for receipt in receipts:
        attempt_id = str(receipt["attempt_id"])
        if receipt["event"] == "reservation":
            if attempt_id in pending or attempt_id in finalized:
                reasons.add("calibration_ledger_attempt_conflict")
            else:
                pending[attempt_id] = receipt
            continue
        if attempt_id not in pending or attempt_id in finalized:
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
            LedgerObservation(
                sequence=int(receipt["sequence"]),
                receipt_digest=str(receipt["receipt_digest"]),
                attempt_id=attempt_id,
                content_id=str(content_id) if isinstance(content_id, str) else None,
                artifact_sha256=MappingProxyType(dict(receipt["artifact_sha256"])),
                identity_epoch=MappingProxyType(epoch),
                t1_bindings=MappingProxyType(dict(receipt["t1_bindings"])),
                capture_wall_time_s=receipt.get("capture_wall_time_s"),
                exact_bound_lexeme_s=receipt.get("exact_bound_lexeme_s"),
                disposition=str(receipt["disposition"]),
                custody_locator=str(receipt["custody_locator"]),
            )
        )
    return observations, reasons


def _custody_reasons(observations: Sequence[LedgerObservation]) -> set[str]:
    for observation in observations:
        if not observation.artifact_sha256:
            if observation.disposition == "abandoned":
                continue
            return {"calibration_ledger_custody_invalid"}
        root = Path(observation.custody_locator)
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
    observations, state_reasons = _attempts_and_observations(receipts)
    reasons.update(state_reasons)
    if verify_custody:
        reasons.update(_custody_reasons(observations))
    return CalibrationLedgerSnapshot(
        ledger_schema=LEDGER_SCHEMA,
        ledger_path=ledger_path,
        head_sequence=physical_sequence,
        head_digest=physical_digest,
        receipts=tuple(_frozen_mapping(receipt) for receipt in receipts),
        observations=tuple(observations),
        refusal_reasons=tuple(sorted(reasons)),
        baseline_sequence=baseline_sequence,
        baseline_digest=baseline_digest,
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
    receipt["receipt_digest"] = _receipt_digest(receipt)
    return receipt


def _locked_append(
    ledger_path: Path,
    build: Any,
) -> Mapping[str, Any]:
    ledger_path = Path(ledger_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(ledger_path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        with os.fdopen(descriptor, "r+b", closefd=False) as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            handle.seek(0)
            raw = handle.read()
            receipts, reasons = _parse_ledger(raw)
            if reasons:
                raise CalibrationLedgerError(", ".join(sorted(reasons)))
            receipt = build(receipts)
            if not _valid_receipt_shape(receipt):
                raise CalibrationLedgerError("writer constructed a malformed receipt")
            payload = canonical_json_bytes(receipt) + b"\n"
            handle.seek(0, os.SEEK_END)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
            return _frozen_mapping(receipt)
    finally:
        os.close(descriptor)


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
        raise CalibrationLedgerError("attempt_id must be nonempty")
    pin_path = Path(head_pin_path)
    try:
        pin_raw = pin_path.read_bytes()
        pin_value = json.loads(pin_raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CalibrationLedgerError("head pin is unreadable") from exc
    pin = _head_pin(pin_value)
    if pin is None:
        raise CalibrationLedgerError("head pin is malformed")
    if require_committed_pin and _committed_pin_bytes(pin_path, repo_root) != pin_raw:
        raise CalibrationLedgerError("head pin is not committed at Git HEAD")

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        sequence = len(receipts) + 1
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        if (len(receipts), predecessor) != pin:
            raise CalibrationLedgerError(
                "physical ledger head differs from the committed pin"
            )
        observations, reasons = _attempts_and_observations(receipts)
        del observations
        if reasons or any(row["attempt_id"] == attempt_id for row in receipts):
            raise CalibrationLedgerError(
                ", ".join(sorted(reasons or {"calibration_ledger_attempt_conflict"}))
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

    return _locked_append(Path(ledger_path), build)


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
        raise CalibrationLedgerError(f"invalid final disposition: {disposition!r}")
    artifacts = dict(artifact_sha256 or {})
    content_id = content_id_from_artifact_hashes(artifacts)

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        reservations = [
            row
            for row in receipts
            if row["attempt_id"] == attempt_id and row["event"] == "reservation"
        ]
        finals = [
            row
            for row in receipts
            if row["attempt_id"] == attempt_id and row["event"] == "finalization"
        ]
        if len(reservations) != 1 or finals:
            raise CalibrationLedgerError("attempt is not uniquely pending")
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
            raise CalibrationLedgerError(
                "finalization conflicts with the reserved attempt binding"
            )
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

    return _locked_append(Path(ledger_path), build)


def head_pin_for_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Emit the exact candidate pin that must be reviewed and committed."""

    if not _valid_receipt_shape(receipt):
        raise CalibrationLedgerError("cannot pin a malformed receipt")
    return {
        "sequence": int(receipt["sequence"]),
        "head_digest": str(receipt["receipt_digest"]),
        "ledger_schema": LEDGER_SCHEMA,
    }


__all__ = [
    "ALL_DISPOSITIONS",
    "CONTENT_ID_ARTIFACTS",
    "DEFAULT_HEAD_PIN_PATH",
    "DEFAULT_LEDGER_PATH",
    "FINAL_DISPOSITIONS",
    "GENESIS_DIGEST",
    "IDENTITY_EPOCH_FIELDS",
    "LEDGER_SCHEMA",
    "RECEIPT_SCHEMA",
    "REFUSAL_TAXONOMY",
    "CalibrationLedgerError",
    "CalibrationLedgerSnapshot",
    "LedgerObservation",
    "append_pending_receipt",
    "artifact_hashes",
    "canonical_sha256",
    "content_id_from_artifact_hashes",
    "finalize_attempt_receipt",
    "head_pin_for_receipt",
    "load_calibration_ledger_snapshot",
]
