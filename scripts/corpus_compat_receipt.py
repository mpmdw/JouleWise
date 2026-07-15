#!/usr/bin/env python3
"""Emit deterministic WO-003 compatibility gates for every bundle in a corpus."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.analysis_engine.inputs import (  # noqa: E402
    BundleEvidence,
    token_provenance,
)
from joulewise.analysis_engine.ratio import ratio_evidence_reasons  # noqa: E402
from joulewise.bundle_read import BundleReader  # noqa: E402
from joulewise.cli import validate_bundle  # noqa: E402
from joulewise.provenance import FIXED_BUDGET_EXACT  # noqa: E402


SCHEMA_VERSION = "joulewise.corpus_compat_receipt.v1"
GATE_NAMES = ("strict_readable", "exact", "replay", "ratio")


def _is_int(value: object, *, positive: bool = False) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and (value > 0 if positive else value >= 0)
    )


def _realized_items(provenance: Mapping[str, Any]) -> Sequence[Mapping[str, Any]] | None:
    policy = provenance.get("output_policy")
    items = policy.get("realized_items") if isinstance(policy, Mapping) else None
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)) or not items:
        return None
    if not all(isinstance(item, Mapping) for item in items):
        return None
    return items


def _exact_revocation_reasons(provenance: Mapping[str, Any]) -> list[str]:
    policy = provenance.get("output_policy")
    if not isinstance(policy, Mapping):
        return ["output_policy_required"]

    reasons: list[str] = []
    items = _realized_items(provenance)
    if items is not None:
        for item in items:
            if item.get("record_marker_agreement") is not True:
                reasons.append("suite_item_record_marker_conflict")
            if item.get("output_policy") != FIXED_BUDGET_EXACT:
                reasons.append("fixed_budget_exact_required")
            if item.get("status") != "succeeded":
                reasons.append("realized_status_not_succeeded")
            requested = item.get("requested_tokens")
            emitted = item.get("emitted_tokens")
            if not _is_int(requested, positive=True) or emitted != requested:
                reasons.append("requested_emitted_mismatch")
            if item.get("stop_reason") != "requested_tokens_emitted":
                reasons.append("exact_stop_reason_required")
            if item.get("token_evidence_count") != emitted:
                reasons.append("token_evidence_count_mismatch")
        return sorted(set(reasons))

    requested = policy.get("requested_tokens")
    emitted = policy.get("emitted_tokens")
    if policy.get("name") != FIXED_BUDGET_EXACT:
        reasons.append("fixed_budget_exact_required")
    if not _is_int(requested, positive=True) or emitted != requested:
        reasons.append("requested_emitted_mismatch")
    if provenance.get("output_tokens") != emitted:
        reasons.append("observed_emitted_mismatch")
    if provenance.get("stop_reason") != "requested_tokens_emitted":
        reasons.append("exact_stop_reason_required")
    return sorted(set(reasons))


def _replay_revocation_reasons(
    provenance: Mapping[str, Any], metadata: Mapping[str, Any] | None
) -> list[str]:
    reasons = _exact_revocation_reasons(provenance)
    items = _realized_items(provenance)
    if items is not None:
        for item in items:
            emitted = item.get("emitted_tokens")
            if item.get("emitted_token_ids_count") != emitted:
                reasons.append("emitted_token_ids_missing_or_inconsistent")
    else:
        workload = (
            metadata.get("workload_provenance")
            if isinstance(metadata, Mapping)
            else None
        )
        response = workload.get("response") if isinstance(workload, Mapping) else None
        emitted_ids = response.get("emitted_token_ids") if isinstance(response, Mapping) else None
        policy = provenance.get("output_policy")
        emitted = policy.get("emitted_tokens") if isinstance(policy, Mapping) else None
        if not isinstance(emitted_ids, list) or len(emitted_ids) != emitted:
            reasons.append("emitted_token_ids_missing_or_inconsistent")
    return sorted(set(reasons))


def _ratio_revocation_reasons(provenance: Mapping[str, Any]) -> list[str]:
    reasons = list(ratio_evidence_reasons(provenance, provenance))
    items = _realized_items(provenance)
    if items is not None and any(
        item.get("record_marker_agreement") is not True for item in items
    ):
        reasons.append("suite_item_record_marker_conflict")
    return sorted(set(reasons))


def _gate(reasons: Sequence[str]) -> dict[str, Any]:
    stable = sorted(set(reasons))
    return {"eligible": not stable, "revocation_reasons": stable}


def _artifact_directory_paths(root: Path) -> list[Path]:
    candidates: set[Path] = set()
    for artifact in ("config.json", "metadata.json", "summary_metrics.json"):
        candidates.update(path.parent for path in root.rglob(artifact))
    return sorted(candidates, key=lambda path: path.relative_to(root).as_posix())


def _bundle_paths(root: Path) -> list[Path]:
    """Return only D-011-complete bundle directories in stable path order."""

    return [
        path
        for path in _artifact_directory_paths(root)
        if BundleReader(path).is_complete()
    ]


def evaluate_bundle(path: Path, corpus_root: Path) -> dict[str, Any]:
    reader = BundleReader(path)
    summary = reader.raw_summary()
    metadata = reader.raw_metadata()
    relative_path = path.relative_to(corpus_root).as_posix()
    evidence = BundleEvidence(
        entry={},
        bundle_id=path.name,
        relative_path=relative_path,
        path=path,
        summary=summary,
        metadata=metadata,
        raw_config=reader.raw_config(),
        strict_problems=(),
        base_reason_codes=(),
        config_sha256=None,
        summary_sha256=None,
        replacement_classification="registered",
        inclusion_status="included",
    )
    provenance = token_provenance(evidence)
    strict_problems = validate_bundle(path, strict=True)
    exact_reasons = _exact_revocation_reasons(provenance)
    replay_reasons = _replay_revocation_reasons(provenance, metadata)
    ratio_reasons = _ratio_revocation_reasons(provenance)
    run_id = metadata.get("run_id") if isinstance(metadata, Mapping) else None
    return {
        "bundle_id": run_id if isinstance(run_id, str) and run_id else path.name,
        "relative_path": relative_path,
        "gates": {
            "strict_readable": _gate(
                [] if not strict_problems else ["strict_validation_failed"]
            ),
            "exact": _gate(exact_reasons),
            "replay": _gate(replay_reasons),
            "ratio": _gate(ratio_reasons),
        },
    }


def build_receipt(corpus_root: Path) -> dict[str, Any]:
    root = Path(corpus_root).resolve()
    if not root.is_dir():
        raise ValueError(f"corpus root is not a directory: {root}")
    bundles = [evaluate_bundle(path, root) for path in _bundle_paths(root)]
    summary: dict[str, dict[str, int]] = {}
    for gate_name in GATE_NAMES:
        eligible = sum(
            1 for bundle in bundles if bundle["gates"][gate_name]["eligible"]
        )
        summary[gate_name] = {
            "eligible": eligible,
            "revoked": len(bundles) - eligible,
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "corpus_root": "runs",
        "bundle_count": len(bundles),
        "bundles": bundles,
        "summary": summary,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus_root", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        help="write the receipt to this path instead of stdout",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        receipt = build_receipt(args.corpus_root)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
