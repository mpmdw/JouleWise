#!/usr/bin/env python3
"""Emit UNRATIFIED D-109 calibration-ledger backfill candidates.

This tool never appends the authoritative ledger and never issues an
acceptance artifact.  It derives path-independent candidate identities from
stored manifest/evidence bytes; the lead must still verify raw physics,
hashes, and every disposition before an authenticated import transaction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_ledger import (  # noqa: E402
    IDENTITY_EPOCH_FIELDS,
    LEDGER_SCHEMA,
    T1_FIELDS,
    artifact_hashes,
    canonical_sha256,
    content_id_from_artifact_hashes,
)


BACKFILL_SCHEMA = "joulewise.calibration_ledger_backfill_candidates.v1"


def _json_object(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def _candidate(directory: Path) -> dict[str, Any]:
    manifest_path = directory / "manifest.json"
    evidence_path = directory / "instrument_evidence.json"
    manifest = _json_object(manifest_path)
    evidence = _json_object(evidence_path)
    hashes = artifact_hashes(directory)
    manifest_artifacts = manifest.get("artifacts")
    if not isinstance(manifest_artifacts, Mapping):
        raise ValueError(f"{directory}: manifest artifact table is missing")
    for relative, expected in manifest_artifacts.items():
        if not isinstance(relative, str) or hashes.get(relative) != expected:
            raise ValueError(f"{directory}: manifest hash mismatch for {relative!r}")
    content_id = content_id_from_artifact_hashes(hashes)
    bindings = evidence.get("bindings")
    if content_id is None or not isinstance(bindings, Mapping):
        raise ValueError(f"{directory}: candidate identity/bindings are incomplete")
    proposed = (
        "valid"
        if evidence.get("status") == "valid"
        else "ordinary-invalid"
        if evidence.get("status") == "invalid"
        else "unclassifiable"
    )
    return {
        "attempt_id": str(evidence.get("validation_id") or directory.name),
        "content_id": content_id,
        "artifact_sha256": hashes,
        "identity_epoch": {
            field: bindings.get(field) for field in IDENTITY_EPOCH_FIELDS
        },
        "t1_bindings": {field: bindings.get(field) for field in T1_FIELDS},
        "capture_wall_time_s": (
            str(evidence["capture_wall_time_s"])
            if evidence.get("capture_wall_time_s") is not None
            else None
        ),
        "exact_bound_lexeme_s": (
            str(evidence["b_fiducial_s"])
            if evidence.get("b_fiducial_s") is not None
            else None
        ),
        "custody_locator": str(directory.resolve()),
        "candidate_disposition": "UNRATIFIED",
        "stored_status_proposal": proposed,
        "required_verification": "lead-owned raw-physics and hash verification",
    }


def build_candidate_set(roots: list[Path]) -> dict[str, Any]:
    directories: set[Path] = set()
    for root in roots:
        root = Path(root).resolve(strict=True)
        directories.update(path.parent for path in root.glob("*/manifest.json"))
        directories.update(
            path.parent
            for path in root.glob("instrument_validation/*/manifest.json")
        )
    candidates = [_candidate(path) for path in sorted(directories)]
    duplicate_content = sorted(
        content_id
        for content_id in {row["content_id"] for row in candidates}
        if sum(row["content_id"] == content_id for row in candidates) > 1
    )
    payload: dict[str, Any] = {
        "schema_version": BACKFILL_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "status": "UNRATIFIED_CANDIDATE_SET",
        "authoritative": False,
        "production_issuance_blocked": True,
        "candidate_count": len(candidates),
        "content_distinct_count": len({row["content_id"] for row in candidates}),
        "duplicate_content_ids": duplicate_content,
        "candidates": candidates,
    }
    payload["candidate_set_sha256"] = canonical_sha256(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        payload = build_candidate_set(args.roots)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": payload["status"],
                "candidate_count": payload["candidate_count"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
