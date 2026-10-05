#!/usr/bin/env python3
"""Outcome-blind prospective-to-finalized analysis-manifest transition."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.analysis_manifest_v3 import (  # noqa: E402
    AnalysisManifestFinalizationError,
    FINALIZED_BASENAME_SUFFIX,
    finalize_prospective_analysis_manifest_v3,
    _path_under_root,
    _strict_json_bytes,
    _write_append_only,
)
from joulewise.authentication_io import read_authentication_input_nofollow  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Authenticate postcollection custody and derive an immutable "
            "finalized-v3 manifest without inspecting an effect estimate"
        )
    )
    parser.add_argument("--prospective-manifest", required=True, type=Path)
    parser.add_argument("--plan-tree", required=True, type=Path)
    parser.add_argument("--custody-root", required=True, type=Path)
    parser.add_argument("--runs-root", required=True, type=Path)
    parser.add_argument("--whole-window-verdict", required=True, type=Path)
    parser.add_argument("--bracket-binding", required=True, type=Path)
    parser.add_argument("--calibration-ledger", required=True, type=Path)
    parser.add_argument("--aggregate-floor-artifact", required=True, type=Path)
    parser.add_argument(
        "--dominance-replay-sidecar", type=Path,
        help="D-165 mint replay sidecar; copied unchanged into custody when external",
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser


def stage_dominance_replay_sidecar(source: Path, custody_root: Path) -> Path:
    """Keep exact mint bytes in append-only, content-addressed finalize custody."""
    try:
        raw = read_authentication_input_nofollow(
            source.parent, source.name, grammar="json", label="dominance replay sidecar"
        )
    except OSError as exc:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_input_unreadable", f"dominance replay sidecar: {exc}"
        ) from exc
    value = _strict_json_bytes(raw, "dominance replay sidecar")
    from joulewise.dominance_closeout import REPLAY_SCHEMA_VERSION

    if (value.get("schema_version") != REPLAY_SCHEMA_VERSION
            or not isinstance(value.get("sidecar_id"), str)
            or not value["sidecar_id"]):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            "dominance replay sidecar schema/identity is invalid",
        )
    custody = Path(custody_root).absolute()
    if source.absolute().is_relative_to(custody):
        path, _relative = _path_under_root(source, custody, "dominance replay sidecar")
        return path
    digest = hashlib.sha256(raw).hexdigest()
    path = custody / f"dominance-replay-{digest}.json"
    _write_append_only(path, raw)
    return path


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        sidecar_path = (
            stage_dominance_replay_sidecar(args.dominance_replay_sidecar, args.custody_root)
            if args.dominance_replay_sidecar is not None else None
        )
        manifest = finalize_prospective_analysis_manifest_v3(
            args.prospective_manifest,
            plan_tree_path=args.plan_tree,
            custody_root=args.custody_root,
            runs_root=args.runs_root,
            whole_window_verdict_path=args.whole_window_verdict,
            bracket_binding_path=args.bracket_binding,
            calibration_ledger_path=args.calibration_ledger,
            aggregate_floor_artifact_path=args.aggregate_floor_artifact,
            output_dir=args.output_dir,
            dominance_replay_sidecar_path=sidecar_path,
        )
    except AnalysisManifestFinalizationError as exc:
        print(
            json.dumps(
                {
                    "status": "REFUSE",
                    "reason": exc.reason_code,
                    "detail": exc.detail,
                },
                sort_keys=True,
            )
        )
        return 2
    output = (
        Path(args.output_dir)
        / f"{manifest['lineage']['prospective_manifest_id']}"
        f"{FINALIZED_BASENAME_SUFFIX}"
    )
    print(
        json.dumps(
            {
                "status": "FINALIZED",
                "manifest_id": manifest["manifest_id"],
                "output": str(output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
