#!/usr/bin/env python3
"""Build and optionally publish one deterministic D-102 successor artifact.

Dry-run is the default. Issuance publishes immutable artifact bytes first and
switches the committed registry last; it never writes the ledger head pin.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_bracketing import (  # noqa: E402
    ACCEPTANCE_IDENTITY_FIELDS,
    ACCEPTANCE_REGISTRY_SCHEMA,
    ACCEPTANCE_REGISTRY_AUTHORITY,
    ACCEPTANCE_SUCCESSOR_SCHEMA,
    DEFAULT_ACCEPTANCE_REGISTRY_PATH,
    POST_SUCCESSOR_POLICY,
    SUCCESSOR_CORPUS_SELECTION,
    SUCCESSOR_COUNT_BOUNDARY_RULE,
    SUCCESSOR_DECISION_IDS,
    SUCCESSOR_PUBLICATION_POLICY,
    SUCCESSOR_QUANTILE_METHOD,
    _active_registry_entry,
    _artifact_count_boundary,
    _canonical_sha256,
    _group_probe_observations,
    _observation_custody_authentic,
    _probe_observation_universe,
    _valid_acceptance_bound,
    _valid_registry,
    derive_successor_decimal_derivation,
    load_calibration_acceptance_registry,
    probe_calibration_acceptance_trigger,
)
from joulewise.calibration_ledger import (  # noqa: E402
    BRACKET_SESSION_ABORT_EVENT,
    DEFAULT_HEAD_PIN_PATH,
    DEFAULT_LEDGER_PATH,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
    LedgerObservation,
    load_calibration_ledger_snapshot,
)
from joulewise.powermetrics_fiducial import PROTOCOL_ID, protocol_sha256  # noqa: E402


BUILD_OUTPUT_SCHEMA = "joulewise.calibration_acceptance_successor_build.v1"
CONTENT_IDENTITY_METHOD = (
    "sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))"
)


@dataclass(frozen=True)
class SuccessorBuild:
    artifact: Mapping[str, Any]
    artifact_bytes: bytes
    artifact_sha256: str
    registry: Mapping[str, Any]
    registry_bytes: bytes
    registry_sha256: str
    artifact_path: str
    head_pin: Mapping[str, Any]
    parent_probe: Mapping[str, Any]
    successor_probe: Mapping[str, Any]

    def output_record(self) -> dict[str, Any]:
        return {
            "schema_version": BUILD_OUTPUT_SCHEMA,
            "publication_policy": SUCCESSOR_PUBLICATION_POLICY,
            "artifact_path": self.artifact_path,
            "artifact_sha256": self.artifact_sha256,
            "derivation_sha256": self.artifact["derivation_sha256"],
            "artifact_file_content": self.artifact_bytes.decode("utf-8"),
            "registry_sha256": self.registry_sha256,
            "registry_file_content": self.registry_bytes.decode("utf-8"),
            "proposed_registry_entry": next(
                entry
                for entry in self.registry["entries"]
                if entry["active"] is True
            ),
            "proposed_head_pin": dict(self.head_pin),
            "parent_probe": dict(self.parent_probe),
            "successor_probe": dict(self.successor_probe),
        }


class SuccessorDurabilityUncertain(RuntimeError):
    """Registry authority switched, but its directory sync failed."""


def _pretty_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            dict(value),
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
        )
        + "\n"
    ).encode("utf-8")


def _epoch_id(epoch: Mapping[str, Any], active: Mapping[str, Any]) -> str:
    if dict(epoch) == dict(active):
        return "active_epoch"
    raw = json.dumps(
        dict(epoch),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return f"epoch_{hashlib.sha256(raw).hexdigest()[:16]}"


def _attempt_row(observation: LedgerObservation) -> dict[str, Any]:
    return {
        "attempt_id": observation.attempt_id,
        "finalization_sequence": observation.sequence,
        "receipt_digest": observation.receipt_digest,
        "observation_kind": observation.observation_kind,
        "custody_locator": observation.custody_locator,
        "exact_bound_lexeme_s": observation.exact_bound_lexeme_s,
        "manifest_sha256": observation.artifact_sha256.get("manifest.json"),
        "instrument_evidence_sha256": observation.artifact_sha256.get(
            "instrument_evidence.json"
        ),
    }


def _governed_unused_slots(
    snapshot: CalibrationLedgerSnapshot,
) -> list[dict[str, Any]]:
    """Record only unused U1 slots whose terminal abort proves no capture."""

    rows: list[dict[str, Any]] = []
    receipts_by_session: dict[str, list[Mapping[str, Any]]] = {}
    for receipt in snapshot.receipts:
        session_id = receipt.get("session_id")
        if isinstance(session_id, str):
            receipts_by_session.setdefault(session_id, []).append(receipt)
    for session in snapshot.bracket_sessions:
        if session.state != "aborted":
            continue
        receipts = receipts_by_session.get(session.session_id, [])
        opens = [receipt for receipt in receipts if receipt.get("event") == "bracket-session-open"]
        aborts = [
            receipt
            for receipt in receipts
            if receipt.get("event") == BRACKET_SESSION_ABORT_EVENT
        ]
        if len(opens) != 1 or len(aborts) != 1:
            raise ValueError("aborted bracket session lacks one authenticated closure")
        opened = opens[0]
        aborted = aborts[0]
        for slot in aborted["unused_slots"]:
            reservation = opened["slots"][slot]
            rows.append(
                {
                    "attempt_id": reservation["attempt_id"],
                    "closure_sequence": aborted["sequence"],
                    "receipt_digest": aborted["receipt_digest"],
                    "disposition": "governed-unused-slot",
                    "custody_locator": reservation["custody_locator"],
                }
            )
    return rows


def _noncontent_rows(
    noncontent: Sequence[LedgerObservation],
    snapshot: CalibrationLedgerSnapshot,
) -> list[dict[str, Any]]:
    if noncontent:
        # A terminal `abandoned` receipt can still conceal already-created
        # classifiable bytes. Q6 requires a ruling before automatic issuance.
        raise ValueError("noncontent observation blocks automatic successor issuance")
    return sorted(
        _governed_unused_slots(snapshot),
        key=lambda row: (row["closure_sequence"], row["attempt_id"]),
    )


def _load_parent_artifact(
    registry: Mapping[str, Any], repo_root: Path
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    active = _active_registry_entry(registry)
    if active is None:
        raise ValueError("acceptance registry does not have one active entry")
    path = repo_root / str(active["artifact_path"])
    try:
        raw = path.read_bytes()
        artifact = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("active acceptance artifact is unreadable") from exc
    if (
        hashlib.sha256(raw).hexdigest() != active["artifact_sha256"]
        or not _valid_acceptance_bound(artifact)
    ):
        raise ValueError("active acceptance artifact is not registry-authenticated")
    return active, artifact


def _assert_terminal_committed_snapshot(snapshot: CalibrationLedgerSnapshot) -> None:
    if (
        not snapshot.valid
        or snapshot.head_sequence < 1
        or snapshot.head_sequence != len(snapshot.receipts)
        or snapshot.committed_head_sequence != snapshot.head_sequence
        or snapshot.committed_head_digest != snapshot.head_digest
        or snapshot.receipts[-1].get("receipt_digest") != snapshot.head_digest
        or snapshot.receipts[-1].get("event")
        in {"reservation", "bracket-session-open", "bracket-session-slot-claim"}
    ):
        raise ValueError("successor issuance requires a committed terminal ledger head")


def build_calibration_acceptance_successor(
    ledger_snapshot: CalibrationLedgerSnapshot,
    *,
    observed_identity_epoch: Mapping[str, Any],
    registry_path: Path = DEFAULT_ACCEPTANCE_REGISTRY_PATH,
    repo_root: Path = REPO_ROOT,
    require_committed_registry: bool = True,
    verify_custody: bool = True,
) -> SuccessorBuild:
    """Build deterministic artifact and registry buffers without writing."""

    repo_root = Path(repo_root).resolve()
    _assert_terminal_committed_snapshot(ledger_snapshot)
    registry = load_calibration_acceptance_registry(
        registry_path,
        repo_root=repo_root,
        require_committed=require_committed_registry,
    )
    if registry is None:
        raise ValueError("acceptance registry is invalid or uncommitted")
    parent_entry, parent = _load_parent_artifact(registry, repo_root)
    parent_probe = probe_calibration_acceptance_trigger(
        ledger_snapshot,
        observed_identity_epoch=observed_identity_epoch,
        registry_path=registry_path,
        repo_root=repo_root,
        require_committed_registry=require_committed_registry,
        verify_custody=verify_custody,
    )
    if parent_probe["outcome"] != "successor_required":
        raise ValueError(
            f"active artifact does not require a successor: {parent_probe['outcome']}"
        )

    grouped_result = _group_probe_observations(
        _probe_observation_universe(ledger_snapshot)
    )
    if grouped_result is None:
        raise ValueError("content identity has conflicting classifications or bytes")
    grouped, noncontent = grouped_result
    noncontent_rows = _noncontent_rows(noncontent, ledger_snapshot)
    active_epoch = dict(parent["identity_epoch"])
    if dict(observed_identity_epoch) != active_epoch:
        raise ValueError("observed identity epoch differs from the parent artifact")

    epoch_values: dict[str, dict[str, Any]] = {"active_epoch": active_epoch}
    prior_rows: list[dict[str, Any]] = []
    corpus_members: list[dict[str, Any]] = []
    for content_id, aliases in grouped.items():
        representative = aliases[0]
        epoch_id = _epoch_id(representative.identity_epoch, active_epoch)
        epoch_values.setdefault(epoch_id, dict(representative.identity_epoch))
        prior_rows.append(
            {
                "content_id": content_id,
                "epoch_id": epoch_id,
                "disposition": representative.classification_disposition,
                "representative_attempt_id": representative.attempt_id,
                "attempts": [_attempt_row(alias) for alias in aliases],
            }
        )
        if (
            representative.classification_disposition != "valid"
            or epoch_id != "active_epoch"
        ):
            continue
        if verify_custody and any(
            not _observation_custody_authentic(alias) for alias in aliases
        ):
            raise ValueError("selected corpus member fails custody reauthentication")
        bound = representative.exact_bound_lexeme_s
        if not isinstance(bound, str):
            raise ValueError("selected corpus member lacks an exact bound lexeme")
        corpus_members.append(
            {
                "content_id": content_id,
                "attempt_id": representative.attempt_id,
                "finalization_sequence": representative.sequence,
                "receipt_digest": representative.receipt_digest,
                "custody_locator": representative.custody_locator,
                "b_fiducial_s": bound,
                "manifest_sha256": representative.artifact_sha256.get(
                    "manifest.json"
                ),
                "instrument_evidence_sha256": representative.artifact_sha256.get(
                    "instrument_evidence.json"
                ),
            }
        )
    prior_rows.sort(key=lambda row: row["content_id"])
    corpus_members.sort(key=lambda member: member["content_id"])
    if len(corpus_members) < 2:
        raise ValueError("successor corpus has fewer than two valid same-epoch members")

    derivation = derive_successor_decimal_derivation(corpus_members)
    parent_boundary = _artifact_count_boundary(parent)
    count = len(corpus_members)
    next_boundary = parent_boundary if count < parent_boundary else 2 * count
    cutoff_core = {
        "sequence": ledger_snapshot.head_sequence,
        "head_digest": ledger_snapshot.head_digest,
        "ledger_schema": LEDGER_SCHEMA,
    }
    acceptance_id = (
        f"d079_calibration_acceptance_v3_s{ledger_snapshot.head_sequence}_"
        f"{ledger_snapshot.head_digest[:16]}"
    )
    artifact_path = (
        "configs/calibration/"
        f"calibration_acceptance_v3_s{ledger_snapshot.head_sequence}_"
        f"{ledger_snapshot.head_digest[:16]}.json"
    )
    root_acceptance_id = (
        parent["lineage"]["root_acceptance_id"]
        if parent.get("schema_version") == ACCEPTANCE_SUCCESSOR_SCHEMA
        else parent["acceptance_id"]
    )
    parent_cutoff = {
        key: parent["ledger_cutoff"][key]
        for key in ("sequence", "head_digest", "ledger_schema")
    }
    artifact: dict[str, Any] = {
        "schema_version": ACCEPTANCE_SUCCESSOR_SCHEMA,
        "acceptance_id": acceptance_id,
        "decision_ids": list(SUCCESSOR_DECISION_IDS),
        "artifact_role": "issued",
        "issuance": {
            "status": "issued",
            "claim_eligible": True,
            "reason": (
                "authenticated live-prefix trigger judged under the parent "
                "artifact and rederived under D-102/D-109/D-117"
            ),
        },
        "lineage": {
            "generation": int(parent_entry["generation"]) + 1,
            "root_acceptance_id": root_acceptance_id,
            "parent_acceptance_id": parent["acceptance_id"],
            "parent_artifact_sha256": parent_entry["artifact_sha256"],
            "parent_derivation_sha256": parent["derivation_sha256"],
            "parent_ledger_cutoff": parent_cutoff,
            "trigger_judgment": {
                "judged_under_acceptance_id": parent["acceptance_id"],
                "judged_under_artifact_sha256": parent_entry["artifact_sha256"],
                "result": "successor_required",
                "new_content_ids": list(parent_probe["new_content_ids"]),
                "triggers": list(parent_probe["observed_triggers"]),
            },
        },
        "ledger_cutoff": {**cutoff_core, "role": "issued_acceptance_baseline"},
        "identity_epoch": active_epoch,
        "prospective_rederivation": {
            "calendar_expiry": None,
            "trigger_observation_rule": "judge_under_prior_artifact_never_self_fit",
            "triggers": [
                "identity_field_change",
                "protocol_or_estimator_byte_change",
                "new_valid_same_identity_capture_expands_observed_range",
                "content_distinct_valid_same_epoch_count_boundary",
                "new_systematic_failure_challenges_preflight_screen",
            ],
            "protocol_sha256": protocol_sha256(PROTOCOL_ID),
            "estimator_code_sha256": parent["prospective_rederivation"][
                "estimator_code_sha256"
            ],
            "count_trigger": {
                "source_corpus_count": count,
                "next_boundary": next_boundary,
                "rule": SUCCESSOR_COUNT_BOUNDARY_RULE,
            },
        },
        "derivation_corpus": {
            "selection": SUCCESSOR_CORPUS_SELECTION,
            "n": count,
            "members": corpus_members,
        },
        "prior_observation_set": {
            "cutoff": cutoff_core,
            "content_identity_method": CONTENT_IDENTITY_METHOD,
            "epoch_catalog": dict(sorted(epoch_values.items())),
            "observations": prior_rows,
            "noncontent_attempts": noncontent_rows,
        },
        "decimal_derivation": derivation,
    }
    artifact["derivation_sha256"] = _canonical_sha256(artifact)
    if not _valid_acceptance_bound(artifact):
        raise ValueError("constructed successor fails the production loader")
    artifact_bytes = _pretty_json_bytes(artifact)
    artifact_sha256 = hashlib.sha256(artifact_bytes).hexdigest()

    registry_entries = []
    for entry in registry["entries"]:
        registry_entries.append({**entry, "active": False})
    registry_entries.append(
        {
            "acceptance_id": acceptance_id,
            "artifact_path": artifact_path,
            "artifact_sha256": artifact_sha256,
            "derivation_sha256": artifact["derivation_sha256"],
            "artifact_schema": ACCEPTANCE_SUCCESSOR_SCHEMA,
            "generation": int(parent_entry["generation"]) + 1,
            "active": True,
            "parent_acceptance_id": parent["acceptance_id"],
            "parent_artifact_sha256": parent_entry["artifact_sha256"],
            "ledger_cutoff": cutoff_core,
        }
    )
    proposed_registry = {
        "schema_version": ACCEPTANCE_REGISTRY_SCHEMA,
        "authority": ACCEPTANCE_REGISTRY_AUTHORITY,
        "entries": registry_entries,
    }
    if not _valid_registry(proposed_registry):
        raise ValueError("constructed registry fails ancestry validation")
    registry_bytes = _pretty_json_bytes(proposed_registry)

    # Step 16's self-fit guard is explicit: every parent-new content ID is now
    # in the successor prior set, while the next count boundary is above n.
    successor_prior_ids = {row["content_id"] for row in prior_rows}
    if not set(parent_probe["new_content_ids"]).issubset(successor_prior_ids):
        raise ValueError("successor omits a parent-judged trigger observation")
    successor_probe = {
        "outcome": "accepted_under_active_artifact",
        "active_acceptance_id": acceptance_id,
        "new_content_ids": [],
        "observed_triggers": [],
        "parent_judgment_policy": POST_SUCCESSOR_POLICY,
    }
    return SuccessorBuild(
        artifact=artifact,
        artifact_bytes=artifact_bytes,
        artifact_sha256=artifact_sha256,
        registry=proposed_registry,
        registry_bytes=registry_bytes,
        registry_sha256=hashlib.sha256(registry_bytes).hexdigest(),
        artifact_path=artifact_path,
        head_pin=cutoff_core,
        parent_probe=parent_probe,
        successor_probe=successor_probe,
    )


def _stage_bytes(destination: Path, payload: bytes) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".stage", dir=destination.parent
    )
    staged = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        staged.unlink(missing_ok=True)
        raise
    return staged


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def publish_successor(
    build: SuccessorBuild,
    *,
    artifact_destination: Path,
    registry_destination: Path,
    expected_registry_bytes: bytes,
    repo_root: Path = REPO_ROOT,
) -> None:
    """Publish validated buffers with the registry as the commit point."""

    repo_root = Path(repo_root).resolve()
    artifact_destination = Path(artifact_destination)
    registry_destination = Path(registry_destination)
    expected_artifact = repo_root / build.artifact_path
    expected_registry = (
        repo_root / "configs/calibration/calibration_acceptance_registry.json"
    )
    if (
        artifact_destination.resolve(strict=False)
        != expected_artifact.resolve(strict=False)
        or registry_destination.resolve(strict=False)
        != expected_registry.resolve(strict=False)
        or artifact_destination.is_symlink()
        or registry_destination.is_symlink()
    ):
        raise ValueError("issuance destinations changed or are substituted")
    try:
        registry_stat = registry_destination.stat()
    except OSError as exc:
        raise ValueError("registry destination is absent") from exc
    if not stat.S_ISREG(registry_stat.st_mode) or registry_stat.st_nlink != 1:
        raise ValueError("registry destination is not one regular unaliased file")
    lock_path = registry_destination.with_name(f"{registry_destination.name}.lock")
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    try:
        lock_descriptor = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        raise ValueError("registry lock is unavailable or substituted") from exc
    try:
        lock_stat = os.fstat(lock_descriptor)
        if not stat.S_ISREG(lock_stat.st_mode) or lock_stat.st_nlink != 1:
            raise ValueError("registry lock is not one regular unaliased file")
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
        if registry_destination.read_bytes() != expected_registry_bytes:
            raise ValueError("registry changed since the successor was built")
        artifact_already_published = artifact_destination.exists()
        if (
            artifact_already_published
            and artifact_destination.read_bytes() != build.artifact_bytes
        ):
            raise ValueError("immutable successor artifact path is occupied")
        artifact_stage = (
            None
            if artifact_already_published
            else _stage_bytes(artifact_destination, build.artifact_bytes)
        )
        registry_stage = _stage_bytes(registry_destination, build.registry_bytes)
        try:
            # An interruption after this replace leaves only an inert
            # unregistered immutable artifact. Authority changes only at the
            # registry replace; an exact orphan is an idempotent retry state.
            if artifact_stage is not None:
                os.replace(artifact_stage, artifact_destination)
                _fsync_directory(artifact_destination.parent)
            os.replace(registry_stage, registry_destination)
            try:
                _fsync_directory(registry_destination.parent)
            except OSError as exc:
                raise SuccessorDurabilityUncertain(
                    "registry committed with directory durability uncertain"
                ) from exc
        finally:
            if artifact_stage is not None:
                artifact_stage.unlink(missing_ok=True)
            registry_stage.unlink(missing_ok=True)
    finally:
        os.close(lock_descriptor)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH)
    parser.add_argument(
        "--registry", type=Path, default=DEFAULT_ACCEPTANCE_REGISTRY_PATH
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--observed-identity", type=Path, required=True)
    parser.add_argument("--issue", action="store_true")
    parser.add_argument("--artifact-out", type=Path)
    parser.add_argument("--registry-out", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        registry_raw = args.registry.read_bytes()
        registry = load_calibration_acceptance_registry(
            args.registry,
            repo_root=args.repo_root,
            require_committed=True,
        )
        if registry is None:
            raise ValueError("registry is not committed or authenticated")
        _, parent = _load_parent_artifact(registry, Path(args.repo_root).resolve())
        cutoff = parent["ledger_cutoff"]
        snapshot = load_calibration_ledger_snapshot(
            args.ledger,
            args.head_pin,
            baseline_sequence=cutoff["sequence"],
            baseline_digest=cutoff["head_digest"],
            require_committed_pin=True,
            verify_custody=True,
            repo_root=args.repo_root,
        )
        observed_identity = json.loads(args.observed_identity.read_bytes())
        if not isinstance(observed_identity, Mapping):
            raise ValueError("observed identity must be a JSON object")
        build = build_calibration_acceptance_successor(
            snapshot,
            observed_identity_epoch=observed_identity,
            registry_path=args.registry,
            repo_root=args.repo_root,
            require_committed_registry=True,
            verify_custody=True,
        )
        if args.issue:
            if args.artifact_out is None or args.registry_out is None:
                raise ValueError("--issue requires --artifact-out and --registry-out")
            publish_successor(
                build,
                artifact_destination=args.artifact_out,
                registry_destination=args.registry_out,
                expected_registry_bytes=registry_raw,
                repo_root=args.repo_root,
            )
        elif args.artifact_out is not None or args.registry_out is not None:
            raise ValueError("dry-run forbids output destinations")
        sys.stdout.buffer.write(_pretty_json_bytes(build.output_record()))
        return 0
    except SuccessorDurabilityUncertain as exc:
        print(f"committed_durability_uncertain: {exc}", file=sys.stderr)
        return 3
    except (OSError, TypeError, ValueError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
