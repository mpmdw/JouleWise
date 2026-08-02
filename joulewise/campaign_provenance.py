"""Shared campaign-provenance schema and authentication primitives.

The v2 attestation is an anti-malformation discriminator: it proves that the
campaign writer emitted a particular raw manifest snapshot.  It is not an
anti-tamper signature; a coordinated rewrite of both the manifest and its
external log can recreate the evidence.  Claim-path tamper resistance remains
the separately rechecked source-manifest hashes carried by verdict provenance.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


CAMPAIGN_PROVENANCE_SCHEMA_V1 = "joulewise.campaign_provenance.v1"
CAMPAIGN_PROVENANCE_SCHEMA_V2 = "joulewise.campaign_provenance.v2"
CAMPAIGN_PROVENANCE_SCHEMAS = frozenset(
    {CAMPAIGN_PROVENANCE_SCHEMA_V1, CAMPAIGN_PROVENANCE_SCHEMA_V2}
)
CAMPAIGN_PROVENANCE_OUTCOMES = frozenset(
    {"usable", "failed", "incomplete", "waived"}
)
CAMPAIGN_PROVENANCE_ATTESTATION_SCHEMA = (
    "joulewise.campaign_provenance_attestation.v1"
)
CAMPAIGN_PROVENANCE_ATTESTATION_RECORD_TYPE = (
    "campaign_provenance_attestation"
)


@dataclass(frozen=True)
class AuthenticatedCampaignManifest:
    """One shape-valid, and for v2 externally authenticated, manifest."""

    path: Path
    raw_bytes: bytes
    value: Mapping[str, Any]


def campaign_manifest_member_shape_valid(
    member: object, schema_version: object
) -> bool:
    """Validate the execution/outcome wire shared by every catalog reader."""

    if not isinstance(member, Mapping):
        return False
    execution = member.get("execution")
    bundle_ids = member.get("bundle_ids")
    if (
        schema_version not in CAMPAIGN_PROVENANCE_SCHEMAS
        or execution not in {"invoked", "existing", "blocked_before_invoke"}
        or not isinstance(member.get("run_id"), str)
        or not member["run_id"]
        or not isinstance(bundle_ids, list)
        or not bundle_ids
        or any(
            not isinstance(bundle_id, str) or not bundle_id
            for bundle_id in bundle_ids
        )
    ):
        return False
    if execution == "existing":
        config = member.get("config")
        if not isinstance(config, str) or not config:
            return False
        if schema_version == CAMPAIGN_PROVENANCE_SCHEMA_V2:
            return member.get("outcome") in CAMPAIGN_PROVENANCE_OUTCOMES
        return "outcome" not in member
    return "outcome" not in member


def load_campaign_log_rows(log_path: Path) -> list[Mapping[str, Any]] | None:
    """Read an object-only JSONL campaign log; corruption fails closed."""

    try:
        lines = Path(log_path).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    except (OSError, UnicodeDecodeError):
        return None
    rows: list[Mapping[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            return None
        if not isinstance(value, Mapping):
            return None
        rows.append(value)
    return rows


def campaign_provenance_attestation(
    *,
    manifest_path: Path,
    raw_manifest_bytes: bytes,
    manifest: Mapping[str, Any],
    timestamp: str,
) -> dict[str, Any]:
    """Bind writer-emitted raw v2 bytes outside the manifest itself."""

    if manifest.get("schema_version") != CAMPAIGN_PROVENANCE_SCHEMA_V2:
        raise ValueError("campaign provenance attestations require a v2 manifest")
    session_id = manifest.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("campaign provenance v2 manifest lacks a session_id")
    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("campaign provenance attestation requires a timestamp")
    return {
        "schema_version": CAMPAIGN_PROVENANCE_ATTESTATION_SCHEMA,
        "record_type": CAMPAIGN_PROVENANCE_ATTESTATION_RECORD_TYPE,
        "timestamp": timestamp,
        "campaign_provenance_manifest": (
            f"campaign_manifests/{manifest_path.name}"
        ),
        "campaign_provenance_manifest_sha256": hashlib.sha256(
            raw_manifest_bytes
        ).hexdigest(),
        "campaign_provenance_schema_version": CAMPAIGN_PROVENANCE_SCHEMA_V2,
        "campaign_provenance_session_id": session_id,
    }


def _recognizable_attestation(row: Mapping[str, Any]) -> bool:
    return bool(
        row.get("schema_version") == CAMPAIGN_PROVENANCE_ATTESTATION_SCHEMA
        or row.get("record_type") == CAMPAIGN_PROVENANCE_ATTESTATION_RECORD_TYPE
    )


def _attestation_shape_valid(row: Mapping[str, Any]) -> bool:
    path_text = row.get("campaign_provenance_manifest")
    path_name = PurePosixPath(path_text).name if isinstance(path_text, str) else ""
    canonical_path = (
        f"campaign_manifests/{path_name}"
        if path_name and path_name != ".json" and "\\" not in path_name
        else None
    )
    digest = row.get("campaign_provenance_manifest_sha256")
    return bool(
        row.get("schema_version") == CAMPAIGN_PROVENANCE_ATTESTATION_SCHEMA
        and row.get("record_type")
        == CAMPAIGN_PROVENANCE_ATTESTATION_RECORD_TYPE
        and isinstance(row.get("timestamp"), str)
        and row["timestamp"]
        and path_text == canonical_path
        and path_name.endswith(".json")
        and re.fullmatch(r"[0-9a-f]{64}", digest or "") is not None
        and row.get("campaign_provenance_schema_version")
        == CAMPAIGN_PROVENANCE_SCHEMA_V2
        and isinstance(row.get("campaign_provenance_session_id"), str)
        and row["campaign_provenance_session_id"]
    )


def matching_campaign_provenance_attestations(
    rows: Sequence[Mapping[str, Any]],
    *,
    manifest_path: Path,
    raw_manifest_bytes: bytes,
    manifest: Mapping[str, Any],
) -> tuple[Mapping[str, Any], ...]:
    """Return shape-valid attestations for one exact current v2 snapshot."""

    expected_path = f"campaign_manifests/{Path(manifest_path).name}"
    expected_sha = hashlib.sha256(raw_manifest_bytes).hexdigest()
    session_id = manifest.get("session_id")
    return tuple(
        row
        for row in rows
        if _attestation_shape_valid(row)
        and row.get("campaign_provenance_manifest") == expected_path
        and row.get("campaign_provenance_manifest_sha256") == expected_sha
        and row.get("campaign_provenance_schema_version")
        == CAMPAIGN_PROVENANCE_SCHEMA_V2
        and row.get("campaign_provenance_session_id") == session_id
    )


def _load_campaign_manifest(path: Path) -> AuthenticatedCampaignManifest | None:
    try:
        raw_bytes = Path(path).read_bytes()
        raw = json.loads(raw_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(raw, Mapping):
        return None
    schema_version = raw.get("schema_version")
    members = raw.get("members")
    if (
        schema_version not in CAMPAIGN_PROVENANCE_SCHEMAS
        or not isinstance(members, list)
        or any(
            not campaign_manifest_member_shape_valid(member, schema_version)
            for member in members
        )
    ):
        return None
    return AuthenticatedCampaignManifest(
        path=Path(path),
        raw_bytes=raw_bytes,
        value=raw,
    )


def _shape_valid_attestations(
    rows: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]] | None:
    attestations: list[Mapping[str, Any]] = []
    for row in rows:
        if not _recognizable_attestation(row):
            continue
        if not _attestation_shape_valid(row):
            return None
        attestations.append(row)
    return attestations


def load_authenticated_campaign_manifest(
    runs_root: Path,
    manifest_path: Path,
    log_path: Path | None = None,
) -> AuthenticatedCampaignManifest | None:
    """Load one source manifest under the shared v1/v2 acceptance rules.

    Legacy v1 descriptors retain their existing relocatable path behavior.
    A v2 descriptor is accepted only at its canonical catalog location and
    only when the external campaign log has exactly one attestation for its
    current raw bytes.
    """

    record = _load_campaign_manifest(Path(manifest_path))
    if record is None:
        return None
    if record.value.get("schema_version") == CAMPAIGN_PROVENANCE_SCHEMA_V1:
        return record
    root = Path(runs_root)
    try:
        expected_path = (root / "campaign_manifests" / record.path.name).resolve()
        actual_path = record.path.resolve()
    except (OSError, RuntimeError):
        return None
    if actual_path != expected_path:
        return None
    rows = load_campaign_log_rows(log_path or root / "campaign_log.jsonl")
    if rows is None:
        return None
    attestations = _shape_valid_attestations(rows)
    if attestations is None:
        return None
    matches = matching_campaign_provenance_attestations(
        attestations,
        manifest_path=record.path,
        raw_manifest_bytes=record.raw_bytes,
        manifest=record.value,
    )
    return record if len(matches) == 1 else None


def load_authenticated_campaign_catalog(
    runs_root: Path, log_path: Path | None = None
) -> list[AuthenticatedCampaignManifest] | None:
    """Load the all-or-nothing v1/v2 campaign-provenance catalog.

    Every manifest must use a known schema and satisfy its member wire.  Each
    current v2 raw snapshot must have exactly one matching writer attestation
    in the selected external campaign log.  Stale valid snapshot attestations
    may coexist, while malformed recognizable rows and duplicate attestations
    for current bytes refuse the entire catalog.
    """

    root = Path(runs_root)
    manifest_dir = root / "campaign_manifests"
    if not manifest_dir.is_dir():
        return []
    catalog: list[AuthenticatedCampaignManifest] = []
    for path in sorted(manifest_dir.glob("*.json"), key=lambda item: item.name):
        record = _load_campaign_manifest(path)
        if record is None:
            return None
        catalog.append(record)

    v2_manifests = [
        record
        for record in catalog
        if record.value.get("schema_version") == CAMPAIGN_PROVENANCE_SCHEMA_V2
    ]
    if not v2_manifests:
        return catalog
    rows = load_campaign_log_rows(log_path or root / "campaign_log.jsonl")
    if rows is None:
        return None
    attestations = _shape_valid_attestations(rows)
    if attestations is None:
        return None
    for record in v2_manifests:
        session_id = record.value.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            return None
        matches = matching_campaign_provenance_attestations(
            attestations,
            manifest_path=record.path,
            raw_manifest_bytes=record.raw_bytes,
            manifest=record.value,
        )
        if len(matches) != 1:
            return None
    return catalog


def campaign_log_manifest_matches(value: object, manifest_name: str) -> bool:
    """Match a relocatable manifest reference without basename-only aliasing."""

    if not isinstance(value, str) or not value:
        return False
    parts = PurePosixPath(value).parts
    return len(parts) >= 2 and parts[-2:] == ("campaign_manifests", manifest_name)


def _legacy_log_member_classification(value: object) -> str | None:
    if not isinstance(value, Mapping):
        return None
    classification = value.get("collection_classification")
    if classification not in {"usable", "failed", "waived"}:
        return None
    flags = value.get("collection_integrity_flags")
    if not isinstance(flags, list) or any(not isinstance(flag, str) for flag in flags):
        return None
    if classification == "usable" and not (
        value.get("status") == "succeeded"
        and value.get("strict_valid") is True
        and not flags
    ):
        return None
    if classification == "waived" and not isinstance(value.get("waiver"), Mapping):
        return None
    strict_valid = value.get("strict_valid")
    if classification == "failed":
        if strict_valid is not True and strict_valid is not False:
            return None
        if value.get("status") == "succeeded" and strict_valid is True and not flags:
            return None
    return classification


def legacy_existing_outcome(
    *,
    manifest_name: str,
    member: Mapping[str, Any],
    log_rows: Sequence[Mapping[str, Any]],
) -> tuple[str, int] | None:
    """Bind one v1 existing row to its exact outcome and log-row identity."""

    run_id = member.get("run_id")
    config = member.get("config")
    bundle_ids = member.get("bundle_ids")
    if (
        not isinstance(run_id, str)
        or not run_id
        or not isinstance(config, str)
        or not config
        or not isinstance(bundle_ids, list)
        or not bundle_ids
        or any(not isinstance(bundle_id, str) or not bundle_id for bundle_id in bundle_ids)
    ):
        return None
    candidates: list[tuple[int, Mapping[str, Any]]] = []
    for row_index, row in enumerate(log_rows):
        if not campaign_log_manifest_matches(
            row.get("campaign_provenance_manifest"), manifest_name
        ):
            continue
        log_config = row.get("config")
        if (
            row.get("run_id") != run_id
            or not isinstance(log_config, str)
            or Path(log_config).name != config
        ):
            continue
        candidates.append((row_index, row))
    if len(candidates) != 1:
        return None
    row_index, candidate = candidates[0]
    members = candidate.get("members")
    if not isinstance(members, list):
        return None
    logged_bundle_ids = [
        value.get("bundle_id") if isinstance(value, Mapping) else None
        for value in members
    ]
    if logged_bundle_ids != bundle_ids:
        return None
    classifications = [_legacy_log_member_classification(value) for value in members]
    if any(value is None for value in classifications):
        return None
    status = candidate.get("status")
    if status == "skipped" and set(classifications) == {"usable"}:
        return "usable", row_index
    if (
        status == "waived"
        and "waived" in classifications
        and set(classifications) <= {"usable", "waived"}
    ):
        return "waived", row_index
    if status == "failed":
        return "failed", row_index
    if status == "incomplete_existing":
        return "incomplete", row_index
    return None
