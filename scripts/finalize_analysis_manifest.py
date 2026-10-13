#!/usr/bin/env python3
"""Outcome-blind prospective-to-finalized analysis-manifest transition."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.analysis_manifest_v3 import (  # noqa: E402
    AnalysisManifestFinalizationError,
    FINALIZED_BASENAME_SUFFIX,
    finalize_prospective_analysis_manifest_v3,
    _authenticate_floor_dependencies,
    _derive_arms_and_entries,
    _directory_under_root,
    _dominance_floor_identity_enabled,
    _path_under_root,
    _read_strict_object,
    _strict_json_bytes,
    _verify_basis_members,
    _write_append_only,
)
from joulewise.authentication_io import read_authentication_input_nofollow  # noqa: E402
from joulewise.analysis_engine.inputs import AnalysisInputError, block5_claim_gate_inputs  # noqa: E402
from joulewise.b5_analysis.windows import AnalysisRefusal  # noqa: E402


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
    parser.add_argument("--window-index", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser


def stage_dominance_replay_sidecar(
    source: Path, custody_root: Path, aggregate_floor_artifact: Path
) -> Path:
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
    from joulewise.dominance_closeout import (
        _floor_member_census_error,
        _sidecar_floor_alignment_errors,
        validate_d165_replay_sidecar,
    )

    errors = validate_d165_replay_sidecar(value)
    floor_path, _relative = _path_under_root(
        aggregate_floor_artifact, custody_root, "aggregate floor artifact"
    )
    floor, _raw = _read_strict_object(floor_path, "aggregate floor artifact")
    if not errors and value["sidecar_id"] != floor["artifact_id"] + "::d165-replay":
        errors.append("dominance replay sidecar identity does not match aggregate floor")
    if not errors:
        errors.extend(_sidecar_floor_alignment_errors(floor, value))
    if not errors:
        census_error = _floor_member_census_error(floor, value)
        if census_error is not None:
            errors.append(census_error)
    if errors:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            "dominance replay sidecar is invalid: " + "; ".join(errors),
        )
    custody = Path(custody_root).absolute()
    if source.absolute().is_relative_to(custody):
        path, _relative = _path_under_root(source, custody, "dominance replay sidecar")
        return path
    digest = hashlib.sha256(raw).hexdigest()
    path = custody / f"dominance-replay-{digest}.json"
    _write_append_only(path, raw)
    return path


def _finalize(args: argparse.Namespace, sidecar_path: Path | None, *,
              block5_inputs: Mapping[str, Any] | None = None) -> dict:
    return finalize_prospective_analysis_manifest_v3(
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
        window_index=getattr(args, "window_index", None),
        **({"_block5_inputs": block5_inputs} if block5_inputs is not None else {}),
    )


def _preflight_other_inputs(args: argparse.Namespace, *,
                            block5_inputs: Mapping[str, Any] | None = None) -> None:
    """Reach the required-sidecar checkpoint without writing custody bytes.

    The library authenticates every other attachment before this checkpoint.
    Reuse that path, then validate the realized arms normally derived after
    the sidecar read. Only the exact missing-sidecar refusal permits staging.
    """
    prospective_path, _relative = _path_under_root(
        args.prospective_manifest, args.custody_root, "prospective manifest"
    )
    prospective, _raw = _read_strict_object(prospective_path, "prospective analysis manifest")
    if not _dominance_floor_identity_enabled(prospective):
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            "legacy prospective manifest may not attach a dominance replay sidecar",
        )
    if getattr(args, "window_index", None) is not None and block5_inputs is None:
        block5_inputs = block5_claim_gate_inputs(args.window_index, prospective_path, args.runs_root)
    try:
        _finalize(args, None, block5_inputs=block5_inputs)
    except AnalysisManifestFinalizationError as exc:
        if (exc.reason_code != "analysis_finalization_attachment_missing"
                or exc.detail != "dominance-enabled prospective manifest requires a dominance replay sidecar"):
            raise
    else:
        raise AnalysisManifestFinalizationError(
            "analysis_finalization_attachment_invalid",
            "dominance-enabled finalization did not require its replay sidecar",
        )
    verdict, _raw = _read_strict_object(args.whole_window_verdict, "whole-window verdict")
    runs_root = _directory_under_root(args.runs_root, args.custody_root, "runs root")
    removed_run_ids = frozenset()
    kept_run_ids = None
    if block5_inputs is not None:
        units = block5_inputs["kept_units"]
        removed_run_ids = units.removed_run_ids()
        kept_run_ids = frozenset(run for cid in units.cells for run in units.kept_run_ids(cid))
    _basis, bundle_paths = _verify_basis_members(
        prospective, verdict, manifest_dir=prospective_path.parent, runs_root=runs_root,
        **({"kept_run_ids": kept_run_ids} if kept_run_ids is not None else {}),
    )
    floor, _raw = _read_strict_object(args.aggregate_floor_artifact, "aggregate floor artifact")
    bindings = _authenticate_floor_dependencies(prospective, floor, bundle_paths=bundle_paths)
    _derive_arms_and_entries(
        prospective, manifest_dir=prospective_path.parent, runs_root=runs_root,
        bundle_paths=bundle_paths, floor_arm_bindings=bindings,
        **({"removed_run_ids": removed_run_ids} if kept_run_ids is not None else {}),
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        sidecar_path = None
        block5_inputs = (block5_claim_gate_inputs(args.window_index, args.prospective_manifest, args.runs_root)
                         if args.window_index is not None else None)
        if args.dominance_replay_sidecar is not None:
            _preflight_other_inputs(args, block5_inputs=block5_inputs)
            sidecar_path = stage_dominance_replay_sidecar(
                args.dominance_replay_sidecar, args.custody_root, args.aggregate_floor_artifact
            )
        manifest = _finalize(args, sidecar_path, block5_inputs=block5_inputs)
    except (AnalysisManifestFinalizationError, AnalysisRefusal, AnalysisInputError) as exc:
        print(
            json.dumps(
                {
                    "status": "REFUSE",
                    "reason": getattr(exc, "reason_code", str(exc).split(":", 1)[0]),
                    "detail": getattr(exc, "detail", str(exc)),
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
