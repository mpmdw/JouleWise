#!/usr/bin/env python3
"""Fail-closed detection-floor extraction CLI (2026-07-19 audit T0.4/T0.6).

Runs :mod:`joulewise.floor_extraction` over one runs root and one extraction
spec, writing a ``joulewise.detection_floor_extraction.v1`` report.

Exit codes:

* ``0`` — every cell extracted under all governed gates;
* ``1`` — the report was written but at least one cell refused (fail-closed
  evidence refusals are recorded per member/cell, never silently dropped);
* ``2`` — process-input error (bad spec, bad paths); no report is written.

Per D-078, corpora recorded before the trace-time-anchor fix refuse
mechanically (their wires cannot carry anchor-shift envelopes); this tool
never publishes a claim-bearing floor from them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.floor_extraction import FloorExtractionError, _block5_runs_root, extract_cells  # noqa: E402
from joulewise.whole_window import (  # noqa: E402
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    MINTED_CONSUMPTION_SEMANTICS_ID,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
    canonical_sha256,
    NEG8_HARVEST_ALLOWANCE_RECORD,
)


def _stored_bundle_containing(path: Path) -> Path | None:
    """Return the finalized bundle ancestor of a prospective output path."""

    resolved = path.resolve(strict=False)
    for parent in resolved.parents:
        if (parent / "summary_metrics.json").is_file():
            return parent
    return None


def extract_indexed_pack(window_index: Path | None, pack: str | None, *, hash_bundles: bool = False,
                         runs_root: Path | None = None, spec=None, manifest_id=None,
                         evaluation_basis_sha256=None, consumption_semantics_id=None,
                         mode="issuing",
                         seal_pins=None, pack_table=None,
                         test_only_allow_synthetic_binding: bool = False,
                         repo_root: Path = REPO_ROOT) -> dict:
    """Compose the sealed readers; no caller-selected scientific input on the CLI."""
    from joulewise.b5_analysis.windows import (
        AnalysisRefusal, SealPins, load_window_index, select_analysed_attempts,
        sealed_pack_table,
    )
    from joulewise.b5_analysis.archive import open_attempt_record, open_archive
    from joulewise.b5_analysis.kept_units import load_kept_units, _strict_json
    from joulewise.b5_analysis.bracket import evaluate_window_bracket
    from joulewise.b5_analysis.context import build_context

    if window_index is None:
        return extract_cells(runs_root, spec, manifest_id=manifest_id,
            evaluation_basis_sha256=evaluation_basis_sha256,
            consumption_semantics_id=consumption_semantics_id,
            mode=mode, hash_bundles=hash_bundles)
    if pack not in ("alpha", "beta"):
        raise AnalysisRefusal("floor_pack_required")
    pins = seal_pins or SealPins.load()
    table = sealed_pack_table(seal_pins=pins) if pack_table is None else pack_table
    index = load_window_index(window_index, seal_pins=pins, pack_table=table)
    records = tuple(open_attempt_record(entry, seal_pins=pins, pack_table=table) for entry in index.entries)
    window = select_analysed_attempts(index, records, seal_pins=pins)[pack]
    pack_prefix = f"sources/repo/configs/campaigns/{window.pack_id}/"
    synthetic_digest = None
    if test_only_allow_synthetic_binding is True:
        # Explicit fixture binding; production authenticates the sealed plan tree.
        synthetic_digest = hashlib.sha256((window.archive_root / (pack_prefix + "plan_tree.json")).read_bytes()).hexdigest()
    archive = open_archive(window, seal_pins=pins, pack_table=table,
                           synthetic_plan_tree_sha256=synthetic_digest)
    local_spec = (Path(repo_root) / "configs/campaigns" / window.pack_id / "extraction_spec.json").read_bytes()
    if local_spec != archive.source_bytes(pack_prefix + "extraction_spec.json"):
        raise AnalysisRefusal("extraction_spec_differs_from_archive")
    spec = _strict_json(local_spec, "extraction_spec_invalid")
    planned = {}
    for cell in spec["cells"]:
        strata = planned.setdefault(cell["condition_family_id"], {})
        stratum = "repeat" if cell["kind"] == "absolute" else "quad"
        units = ({m["bundle_id"]: (m["bundle_id"],) for m in cell["members"]}
                 if stratum == "repeat" else
                 {b["block_id"]: tuple(b["members"][p] for p in ("A1", "B1", "B2", "A2")) for b in cell["blocks"]})
        strata[stratum] = units
    kept = load_kept_units(archive, sealed_catalog_sha256=pins.sealed["catalog_sha256"], planned_units=planned)
    bracket = evaluate_window_bracket(archive, repo_root=Path(repo_root))
    allowance = _strict_json(archive.output_bytes(NEG8_HARVEST_ALLOWANCE_RECORD), "neg8_allowance_record_invalid")
    claim_prefix = ("night-custody/" + window.claim_runs_root.relative_to(window.custody_root).as_posix() + "/"
                    if window.claim_runs_root.is_relative_to(window.custody_root) else "claim-runs/")
    row = _strict_json(archive.source_bytes("sources/" + claim_prefix + allowance["verdict"]["path"]),
                       "whole_window_verdict_provenance_invalid")
    if (canonical_sha256(row) != allowance["verdict"]["row_sha256"]
            or row["evaluation_basis"]["sha256"] != allowance["verdict"]["evaluation_basis_sha256"]):
        raise AnalysisRefusal("whole_window_verdict_provenance_invalid")
    context = build_context(archive, kept, bracket, row,
                           test_only_allow_synthetic_binding=test_only_allow_synthetic_binding)
    from joulewise.b5_analysis.steps import require_primary_context
    require_primary_context(context)
    return extract_cells(window.claim_runs_root, spec, kept_units=kept, archive_context=context,
        evaluation_basis_sha256=row["evaluation_basis"]["sha256"],
        consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        mode=mode, hash_bundles=hash_bundles)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs-root",
        type=Path,
        help="corpus root containing the member bundles and campaign_manifests/",
    )
    parser.add_argument(
        "--spec",
        type=Path,
        help="joulewise.detection_floor_extraction_spec.v1 JSON document",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="path for the extraction report JSON",
    )
    parser.add_argument(
        "--manifest-id",
        default=None,
        help=(
            "analysis manifest id the campaign manifests are bound to; omit for "
            "calibration campaigns recorded with analysis_manifest_id null"
        ),
    )
    parser.add_argument(
        "--evaluation-basis-sha256",
        default=None,
        help=(
            "sha256 of the authenticated whole-window evaluation basis that "
            "governs this extraction subset"
        ),
    )
    parser.add_argument(
        "--consumption-semantics-id",
        default=None,
        choices=(
            MINTED_CONSUMPTION_SEMANTICS_ID,
            MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
            SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
        ),
        help="exact whole-window verdict consumption semantics",
    )
    parser.add_argument(
        "--hash-bundles",
        action="store_true",
        help="record complete-bundle and config sha256 pins per member",
    )
    parser.add_argument("--window-index", type=Path, default=None)
    parser.add_argument("--pack", default=None)
    args = parser.parse_args(argv)
    if args.window_index is not None:
        if any(value is not None for value in (args.runs_root, args.spec, args.manifest_id,
                args.evaluation_basis_sha256, args.consumption_semantics_id)):
            print("error: window_index_conflicting_arguments", file=sys.stderr)
            return 2
        if args.pack not in ("alpha", "beta"):
            print("error: floor_pack_required", file=sys.stderr)
            return 2
    else:
        try:
            block5 = args.runs_root is not None and _block5_runs_root(args.runs_root)
        except FloorExtractionError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if block5:
            print("error: window_index_required", file=sys.stderr)
            return 2
        if args.runs_root is None or args.spec is None or args.pack is not None:
            print("error: runs_root_and_spec_required", file=sys.stderr)
            return 2

    if (args.evaluation_basis_sha256 is None) != (
        args.consumption_semantics_id is None
    ):
        parser.error(
            "--evaluation-basis-sha256 and --consumption-semantics-id are required together"
        )
    if args.evaluation_basis_sha256 is not None and not (
        len(args.evaluation_basis_sha256) == 64
        and all(
            character in "0123456789abcdef"
            for character in args.evaluation_basis_sha256
        )
    ):
        parser.error("--evaluation-basis-sha256 must be 64 lowercase hex")

    if args.window_index is None:
        try:
            spec = json.loads(args.spec.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"error: cannot read extraction spec: {exc}", file=sys.stderr)
            return 2
        if not args.runs_root.is_dir():
            print(f"error: runs root is not a directory: {args.runs_root}", file=sys.stderr)
            return 2
    if args.out.exists():
        print(
            f"error: refusing to overwrite existing extraction artifact: {args.out}",
            file=sys.stderr,
        )
        return 2
    bundle_ancestor = _stored_bundle_containing(args.out)
    if bundle_ancestor is not None:
        print(
            "error: extraction output must be outside the immutable stored "
            f"run bundle: {bundle_ancestor}",
            file=sys.stderr,
        )
        return 2

    from joulewise.b5_analysis.windows import AnalysisRefusal
    try:
        report = extract_indexed_pack(args.window_index, args.pack,
            runs_root=args.runs_root, spec=spec if args.window_index is None else None,
            manifest_id=args.manifest_id, evaluation_basis_sha256=args.evaluation_basis_sha256,
            consumption_semantics_id=args.consumption_semantics_id,
            hash_bundles=args.hash_bundles, mode="read_replay")
    except (FloorExtractionError, AnalysisRefusal) as exc:
        code = exc.code if isinstance(exc, AnalysisRefusal) else str(exc)
        if (args.window_index is not None and not isinstance(exc, AnalysisRefusal)
                and re.fullmatch(r"[a-z][a-z0-9_]*", code) is None):
            code = "floor_extraction_input_invalid"
        print(f"error: {code}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        if args.window_index is None:
            raise
        print("error: extraction_input_invalid", file=sys.stderr)
        return 2

    try:
        args.out.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        print("error: extraction_output_unwritable", file=sys.stderr)
        return 2
    try:
        with args.out.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    except FileExistsError:
        print(
            f"error: refusing to overwrite existing extraction artifact: {args.out}",
            file=sys.stderr,
        )
        return 2
    except OSError:
        print("error: extraction_output_unwritable", file=sys.stderr)
        return 2
    refused = [
        cell["cell_id"] for cell in report["cells"] if not cell["extractable"]
    ]
    omitted = [
        row["bundle_id"] for row in report.get("spec_membership_refusals", [])
    ]
    if refused or omitted:
        if refused:
            print(
                "refused cells (fail-closed): " + ", ".join(sorted(refused)),
                file=sys.stderr,
            )
        if omitted:
            print(
                "campaign members omitted from spec (fail-closed): "
                + ", ".join(sorted(omitted)),
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
