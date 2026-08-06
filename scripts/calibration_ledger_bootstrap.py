#!/usr/bin/env python3
"""Prepare or execute the deterministic calibration-ledger genesis import.

Dry-run is the default. It authenticates the reviewed disposition table and
per-member custody manifest, then prints the complete canonical receipt chain
plus the exact candidate head pin without writing either file. ``--execute``
atomically writes only the ledger; the lead must review and commit the printed
head pin separately.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, BinaryIO, Mapping

sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_ledger import (  # noqa: E402
    DEFAULT_HEAD_PIN_PATH,
    DEFAULT_LEDGER_PATH,
    HISTORICAL_IMPORT_FINALIZATION_EVENT,
    HISTORICAL_IMPORT_RESERVATION_EVENT,
    LEDGER_SCHEMA,
    CalibrationLedgerError,
    HistoricalImportDurabilityUncertain,
    bootstrap_historical_import,
    canonical_json_bytes,
    custody_manifest_bytes,
    generate_historical_custody_manifest,
    prepare_historical_import,
)
from joulewise.calibration_bracketing import (  # noqa: E402
    ACCEPTANCE_BOUND_SCHEMA,
    DEFAULT_ACCEPTANCE_BOUND_PATH,
    ISSUED_ACCEPTANCE_BOUND_SHA256,
    _acceptance_bound_from_authenticated_bytes,
    _authenticated_explicit_acceptance_bound,
    _canonical_sha256,
    _valid_acceptance_bound,
)


OUTPUT_SCHEMA = "joulewise.calibration_historical_import_dry_run.v1"
ISSUED_ARTIFACT_OUTPUT_SCHEMA = (
    "joulewise.calibration_acceptance_issuance_dry_run.v1"
)
DURABILITY_UNCERTAIN_EXIT = 3
_D079_ISSUANCE_SEQUENCE = 76
_D079_ISSUANCE_HEAD_DIGEST = (
    "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7"
)
_D079_ISSUANCE_INVENTORY = {
    "ordinary-invalid": 6,
    "systematic-invalid": 2,
    "valid": 30,
}


@dataclass(frozen=True)
class PreparedIssuedAcceptanceArtifact:
    """Immutable, fully serialized issued-artifact reporting payload."""

    artifact_file_bytes: bytes
    artifact_file_sha256: str
    derivation_sha256: str
    output_record_bytes: bytes
    summary_fields: tuple[tuple[str, str], ...]


def _json_object_bytes(path: Path) -> tuple[bytes, Mapping[str, Any]]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, Mapping):
        raise ValueError(f"{path}: expected a JSON object")
    return raw, value


def _pin_content(pin: Mapping[str, Any]) -> str:
    ordered = {
        "sequence": pin["sequence"],
        "head_digest": pin["head_digest"],
        "ledger_schema": pin["ledger_schema"],
    }
    return json.dumps(ordered, indent=2, ensure_ascii=False) + "\n"


def _issued_artifact_bytes(artifact: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            dict(artifact),
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ": "),
        )
        + "\n"
    ).encode("utf-8")


def _write_issued_artifact_payload(handle: BinaryIO, payload: bytes) -> None:
    written = handle.write(payload)
    if written != len(payload):
        raise OSError("short issued-artifact write")


def _atomic_emit_issued_artifact(path: Path, payload: bytes) -> None:
    """Fsync a sibling stage before atomically replacing the claim anchor."""

    destination = Path(path)
    staging_descriptor = -1
    staging_path: Path | None = None
    try:
        staging_descriptor, staging_name = tempfile.mkstemp(
            prefix=f".{destination.name}.issued-",
            dir=destination.parent,
        )
        staging_path = Path(staging_name)
        staging = os.fdopen(staging_descriptor, "wb")
        staging_descriptor = -1
        with staging:
            _write_issued_artifact_payload(staging, payload)
            staging.flush()
            os.fsync(staging.fileno())
        os.replace(staging_path, destination)
        staging_path = None
    finally:
        if staging_descriptor >= 0:
            os.close(staging_descriptor)
        if staging_path is not None:
            try:
                staging_path.unlink()
            except FileNotFoundError:
                pass


def _issued_acceptance_artifact(
    plan: Any,
    source_artifact: Mapping[str, Any],
    *,
    source_artifact_raw: bytes | None = None,
) -> dict[str, Any]:
    """Build the D-079 issued artifact only from the prepared ledger prefix."""

    if source_artifact_raw is None:
        authenticated_source = _authenticated_explicit_acceptance_bound(
            source_artifact
        )
    else:
        authenticated_source = _acceptance_bound_from_authenticated_bytes(
            source_artifact_raw
        )
        if (
            authenticated_source is not None
            and dict(source_artifact) != authenticated_source
        ):
            authenticated_source = None
    if authenticated_source is None:
        raise ValueError(
            "acceptance artifact source does not match its role-indexed byte pin"
        )
    if (
        plan.final_sequence != _D079_ISSUANCE_SEQUENCE
        or plan.head_digest != _D079_ISSUANCE_HEAD_DIGEST
        or len(plan.receipts) != _D079_ISSUANCE_SEQUENCE
    ):
        raise ValueError("ledger plan is not the ruled D-079 issuance cutoff")
    if any(
        receipt.get("event")
        not in {
            HISTORICAL_IMPORT_RESERVATION_EVENT,
            HISTORICAL_IMPORT_FINALIZATION_EVENT,
        }
        for receipt in plan.receipts
    ):
        raise ValueError("issued prior set requires an import-only ledger prefix")

    # Clone the authenticated source, not the caller's mapping. This preserves
    # the reviewed schema-field order that defines the issued file pin and
    # makes output independent of caller key insertion order.
    artifact = json.loads(
        json.dumps(dict(authenticated_source), allow_nan=False)
    )
    epoch_catalog = artifact["prior_observation_set"]["epoch_catalog"]
    observations: list[dict[str, Any]] = []
    for receipt in plan.receipts:
        if receipt["event"] != HISTORICAL_IMPORT_FINALIZATION_EVENT:
            continue
        epoch_ids = [
            epoch_id
            for epoch_id, epoch in epoch_catalog.items()
            if dict(epoch) == dict(receipt["identity_epoch"])
        ]
        if len(epoch_ids) != 1:
            raise ValueError("ledger observation does not map to one artifact epoch")
        observations.append(
            {
                "content_id": receipt["content_id"],
                "epoch_id": epoch_ids[0],
                "disposition": receipt["disposition"],
                "attempt_id": receipt["attempt_id"],
            }
        )
    disposition_counts = {
        disposition: sum(
            observation["disposition"] == disposition
            for observation in observations
        )
        for disposition in sorted(_D079_ISSUANCE_INVENTORY)
    }
    if (
        len(observations) != 38
        or disposition_counts != _D079_ISSUANCE_INVENTORY
        or len({row["content_id"] for row in observations}) != len(observations)
        or len({row["attempt_id"] for row in observations}) != len(observations)
    ):
        raise ValueError("ledger prefix does not have the ruled 30/2/6 inventory")

    cutoff = {
        "sequence": plan.final_sequence,
        "head_digest": plan.head_digest,
        "ledger_schema": LEDGER_SCHEMA,
    }
    artifact["schema_version"] = ACCEPTANCE_BOUND_SCHEMA
    artifact["artifact_role"] = "issued"
    artifact["issuance"] = {
        "status": "issued",
        "claim_eligible": True,
        "reason": (
            "D-109 R2 raw-physics and artifact-hash verification is bound "
            "by the authenticated historical-import cutoff"
        ),
    }
    artifact["ledger_cutoff"] = {
        **cutoff,
        "role": "issued_acceptance_baseline",
    }
    artifact["prior_observation_set"]["cutoff"] = cutoff
    artifact["prior_observation_set"]["observations"] = observations
    artifact["backfill_candidate"].update(
        {
            "status": "issued",
            "candidate_inventory": disposition_counts,
            "production_issuance_blocked": False,
            "required_verification": (
                "complete: lead-owned raw-physics and artifact-hash verification"
            ),
        }
    )
    artifact["derivation_sha256"] = _canonical_sha256(
        {
            key: value
            for key, value in artifact.items()
            if key != "derivation_sha256"
        }
    )
    if not _valid_acceptance_bound(artifact):
        raise ValueError("deterministically emitted acceptance artifact is invalid")
    return artifact


def _prepare_issued_acceptance_artifact(
    plan: Any,
    source_artifact: Mapping[str, Any],
    *,
    source_artifact_raw: bytes | None = None,
) -> PreparedIssuedAcceptanceArtifact:
    """Build and fully validate the exact artifact bytes before any commit."""

    artifact = _issued_acceptance_artifact(
        plan,
        source_artifact,
        source_artifact_raw=source_artifact_raw,
    )
    expected_cutoff = {
        "sequence": plan.final_sequence,
        "head_digest": plan.head_digest,
        "ledger_schema": LEDGER_SCHEMA,
    }
    expected_observations = []
    epoch_catalog = artifact["prior_observation_set"]["epoch_catalog"]
    for receipt in plan.receipts:
        if receipt["event"] != HISTORICAL_IMPORT_FINALIZATION_EVENT:
            continue
        epoch_ids = [
            epoch_id
            for epoch_id, epoch in epoch_catalog.items()
            if dict(epoch) == dict(receipt["identity_epoch"])
        ]
        if len(epoch_ids) != 1:
            raise ValueError("ledger observation does not map to one artifact epoch")
        expected_observations.append(
            {
                "content_id": receipt["content_id"],
                "epoch_id": epoch_ids[0],
                "disposition": receipt["disposition"],
                "attempt_id": receipt["attempt_id"],
            }
        )
    core = {
        key: value
        for key, value in artifact.items()
        if key != "derivation_sha256"
    }
    if artifact["derivation_sha256"] != _canonical_sha256(core):
        raise ValueError("issued artifact whole-core digest is invalid")
    if artifact["ledger_cutoff"] != {
        **expected_cutoff,
        "role": "issued_acceptance_baseline",
    }:
        raise ValueError("issued artifact cutoff does not match the import plan")
    if artifact["prior_observation_set"]["cutoff"] != expected_cutoff:
        raise ValueError("issued prior-set cutoff does not match the import plan")
    if (
        artifact["prior_observation_set"]["observations"]
        != expected_observations
    ):
        raise ValueError("issued prior set is not the complete import prefix")
    raw = _issued_artifact_bytes(artifact)
    artifact_file_sha256 = hashlib.sha256(raw).hexdigest()
    if artifact_file_sha256 != ISSUED_ACCEPTANCE_BOUND_SHA256:
        raise ValueError("issued artifact bytes do not match the reviewed byte pin")
    derivation_sha256 = artifact["derivation_sha256"]
    output_record = {
        "schema_version": ISSUED_ARTIFACT_OUTPUT_SCHEMA,
        "record": "issued-acceptance-artifact",
        "artifact": artifact,
        "derivation_sha256": derivation_sha256,
        "artifact_file_sha256": artifact_file_sha256,
        "artifact_file_content": raw.decode("utf-8"),
    }
    return PreparedIssuedAcceptanceArtifact(
        artifact_file_bytes=raw,
        artifact_file_sha256=artifact_file_sha256,
        derivation_sha256=derivation_sha256,
        output_record_bytes=canonical_json_bytes(output_record) + b"\n",
        summary_fields=(
            ("issued_artifact_derivation_sha256", derivation_sha256),
            ("issued_artifact_file_sha256", artifact_file_sha256),
        ),
    )


def _emit(
    plan: Any,
    *,
    executed: bool,
    outcome: str,
    prepared_issued_artifact: PreparedIssuedAcceptanceArtifact | None = None,
) -> None:
    for receipt in plan.receipts:
        sys.stdout.buffer.write(
            canonical_json_bytes({"record": "receipt", "receipt": receipt}) + b"\n"
        )
    if prepared_issued_artifact is not None:
        sys.stdout.buffer.write(prepared_issued_artifact.output_record_bytes)
    summary = {
        "schema_version": OUTPUT_SCHEMA,
        "record": "bootstrap-summary",
        "executed": executed,
        "outcome": outcome,
        "receipt_count": len(plan.receipts),
        "final_sequence": plan.final_sequence,
        "head_digest": plan.head_digest,
        "disposition_table_sha256": plan.disposition_table_sha256,
        "custody_manifest_sha256": plan.custody_manifest_sha256,
        "head_pin": plan.head_pin,
        "head_pin_content": _pin_content(plan.head_pin),
    }
    if prepared_issued_artifact is not None:
        summary.update(dict(prepared_issued_artifact.summary_fields))
    sys.stdout.buffer.write(canonical_json_bytes(summary) + b"\n")
    sys.stdout.buffer.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="*",
        type=Path,
        help="optional strict cross-check roots; required in manifest-emission mode",
    )
    parser.add_argument(
        "--disposition-table",
        required=True,
        type=Path,
        help="explicit ruled historical-import table",
    )
    parser.add_argument(
        "--expected-table-sha256",
        required=True,
        help="required SHA-256 of the disposition table's exact raw bytes",
    )
    parser.add_argument(
        "--custody-manifest",
        type=Path,
        help="reviewed content_id-to-absolute-locator custody manifest",
    )
    parser.add_argument(
        "--expected-custody-manifest-sha256",
        help="required SHA-256 of the custody manifest's exact raw bytes",
    )
    parser.add_argument(
        "--emit-custody-manifest",
        action="store_true",
        help="print a lexicographically selected manifest and write nothing",
    )
    parser.add_argument(
        "--checkout-root",
        type=Path,
        default=REPO_ROOT,
        help="root against which deterministic custody locators are stored",
    )
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="atomically write the ledger (the head pin is still never written)",
    )
    parser.add_argument(
        "--acceptance-artifact",
        type=Path,
        default=DEFAULT_ACCEPTANCE_BOUND_PATH,
        help="current D-079 fixture or already-issued artifact used as the template",
    )
    parser.add_argument(
        "--prepare-issued-artifact",
        action="store_true",
        help="print the deterministic issued artifact and digests without writing it",
    )
    parser.add_argument(
        "--emit-issued-artifact",
        nargs="?",
        const=DEFAULT_ACCEPTANCE_BOUND_PATH,
        type=Path,
        metavar="PATH",
        help=(
            "explicitly write the deterministic issued artifact (default: the "
            "checked-in acceptance-artifact path); it is also printed"
        ),
    )
    args = parser.parse_args()
    prepared_issued_artifact: PreparedIssuedAcceptanceArtifact | None = None
    try:
        table_raw = args.disposition_table.read_bytes()
        if args.emit_custody_manifest:
            if args.execute:
                raise ValueError("--emit-custody-manifest cannot execute")
            if args.prepare_issued_artifact or args.emit_issued_artifact is not None:
                raise ValueError(
                    "--emit-custody-manifest cannot prepare an issued artifact"
                )
            if not args.roots:
                raise ValueError("--emit-custody-manifest requires custody roots")
            manifest = generate_historical_custody_manifest(
                roots=args.roots,
                checkout_root=args.checkout_root,
                disposition_table_raw=table_raw,
                expected_disposition_table_sha256=args.expected_table_sha256,
            )
            raw = custody_manifest_bytes(manifest)
            sys.stdout.buffer.write(raw)
            sys.stdout.buffer.flush()
            print(
                f"custody-manifest-sha256={hashlib.sha256(raw).hexdigest()}",
                file=sys.stderr,
            )
            return 0
        if args.custody_manifest is None:
            raise ValueError("--custody-manifest is required")
        if args.expected_custody_manifest_sha256 is None:
            raise ValueError("--expected-custody-manifest-sha256 is required")
        custody_manifest_raw = args.custody_manifest.read_bytes()
        import_inputs = {
            "roots": args.roots,
            "checkout_root": args.checkout_root,
            "disposition_table_raw": table_raw,
            "expected_disposition_table_sha256": args.expected_table_sha256,
            "custody_manifest_raw": custody_manifest_raw,
            "expected_custody_manifest_sha256": (
                args.expected_custody_manifest_sha256
            ),
        }
        artifact_requested = (
            args.prepare_issued_artifact
            or args.emit_issued_artifact is not None
        )
        if artifact_requested:
            # Artifact construction and emission are deliberately completed
            # before the only irreversible ledger call below.
            plan = prepare_historical_import(**import_inputs)
            source_raw, source_artifact = _json_object_bytes(
                args.acceptance_artifact
            )
            prepared_issued_artifact = _prepare_issued_acceptance_artifact(
                plan,
                source_artifact,
                source_artifact_raw=source_raw,
            )
            if args.emit_issued_artifact is not None:
                _atomic_emit_issued_artifact(
                    args.emit_issued_artifact,
                    prepared_issued_artifact.artifact_file_bytes,
                )
        if args.execute:
            # Keep this as the final state-changing operation. Nothing in the
            # durability-uncertain path performs artifact preparation/write.
            plan = bootstrap_historical_import(
                args.ledger,
                head_pin_path=args.head_pin,
                **import_inputs,
                execute=True,
                repo_root=REPO_ROOT,
            )
        else:
            plan = bootstrap_historical_import(
                args.ledger,
                head_pin_path=args.head_pin,
                **import_inputs,
                execute=False,
                repo_root=REPO_ROOT,
            )
    except HistoricalImportDurabilityUncertain as exc:
        _emit(
            exc.plan,
            executed=True,
            outcome=exc.outcome,
            prepared_issued_artifact=prepared_issued_artifact,
        )
        print(
            "committed: parent-directory durability remains uncertain after "
            "one retry; rerun the identical --execute invocation to confirm "
            "durability before updating the head pin",
            file=sys.stderr,
        )
        return DURABILITY_UNCERTAIN_EXIT
    except (CalibrationLedgerError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    _emit(
        plan,
        executed=args.execute,
        outcome="committed" if args.execute else "planned",
        prepared_issued_artifact=prepared_issued_artifact,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
