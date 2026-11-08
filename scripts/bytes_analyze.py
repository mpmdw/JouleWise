#!/usr/bin/env python3
"""Desk-only BYTES analysis; never launches a model or collector."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from joulewise import bytes_analysis as ba
from joulewise.desk_restore import StorageStop


def _write(out, name, payload):
    path = out / (name + ".json")
    if path.exists():
        raise ba.AnalysisError(f"output already exists: {path.name}")
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n")


def _reduce(source, manifest, stage, key_dir=None, stage1_commit=None):
    records = ba.load_records(source, manifest, stage=stage, key_dir=key_dir, stage1_commit=stage1_commit)
    boundaries = ("rails",) if stage == "blinded" else ba.BOUNDARIES
    passes = ba.reduce_models(records, manifest, boundaries=boundaries) + ba.reduce_models(
        records, manifest, inclusive=True, boundaries=boundaries)
    points = ba.combine_passes(passes)
    labels = {tuple(p[k] for k in ("model", "boundary", "basis", "selection")): p for p in points}
    for row in passes:
        point = labels[tuple(row[k] for k in ("model", "boundary", "basis", "selection"))]
        row.update(pass_status=point["pass_status"], n_passes=point["n_passes"])
    return passes, points


def _missing_labels(points):
    """Disclose pass flags on survivors and label models with no point."""
    for point in points:
        flags = set(point.get("flags", [])) | {
            flag for row in point.get("passes", []) for flag in row.get("flags", [])}
        if "bytes.withheld_missing" in flags:
            point["flags"] = sorted(flags)
            if point.get("status") == "unavailable":
                point.update(status="missing", reason="withheld rows missing")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--export", type=Path, nargs="+", help="Block-6 export directories read in place; manifest must locate matching archives")
    source.add_argument("--records", type=Path, nargs="+", help="harvest archive or withheld/member-assessments.json")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--stage", required=True, choices=("blinded", "fit", "heldout", "all"))
    parser.add_argument("--key-dir", type=Path, help="directory of released pack/config keys (read only)")
    parser.add_argument("--stage1-commit", help="recorded stage-1 commit; permits blinded held-out agreement")
    parser.add_argument("--predictions", type=Path, help="fit-stage predictions.json, with predictions.sha256 beside it")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = ba.validate_manifest(ba.read_json(args.manifest))
        source = args.export or args.records
        if args.stage == "heldout" and args.predictions is None:
            raise ba.AnalysisError("heldout requires --predictions and its SHA-256 sidecar")
        if args.stage1_commit and not re.fullmatch(r"[0-9a-fA-F]{40}(?:[0-9a-fA-F]{24})?", args.stage1_commit):
            raise ba.AnalysisError("stage-1 commit must be a Git commit hash")
        if args.stage == "blinded":
            if args.export is None:
                raise ba.AnalysisError("blinded stage requires --export")
            passes, points = _reduce(source, manifest, "blinded", stage1_commit=args.stage1_commit)
            frozen = ba.frozen_predictions([p for p in points if p["role"] == "fit"], manifest)
            # Pre-commit grouped exports contain only fit configurations. Their
            # estimates and NEG-8 inputs remain reviewable without H1/H2 words.
            _missing_labels(points)
            result = ba.evaluate(points, frozen) if any(p["role"] == "heldout" for p in points) else {
                name: [] for name in ("h1", "moe", "h2", "unavailable")}
            args.out.mkdir(parents=True, exist_ok=True)
            _write(args.out, "blinded_pass_estimates", passes)
            _write(args.out, "model_estimates", points)
            for name, rows in result.items():
                _write(args.out, name, rows)
            _write(args.out, "analysis_record", {"stage": "blinded", "boundaries": ["rails"],
                "manifest_sha256": ba.digest(manifest), "non_claim": True})
            return 0
        if args.stage == "all" and manifest.get("synthetic") is not True:
            raise ba.AnalysisError("all is synthetic-only; real inputs require separately committed fit predictions")
        if args.stage != "heldout":
            fit_passes, fit_points = _reduce(source, manifest, "fit", args.key_dir)
            refs = {r["session_id"]: r["neg8_inputs"] for r in fit_passes if "neg8_inputs" in r}
            frozen = ba.frozen_predictions(fit_points, manifest, refs)
            sha = ba.write_predictions(args.out, frozen)
            digest = frozen["bytes_analysis_sha256"]
            commitment = {"bytes_analysis_sha256": {"committed": digest, "evaluating": digest},
                          "flags": [], "fields_not_rebuilt": []}
            _write(args.out, "fit_pass_estimates", fit_passes)
            if args.stage == "fit":
                print(json.dumps({"stage": "fit", "predictions_sha256": sha, "out": str(args.out)}))
                return 0
        else:
            # Validate the commitment before opening any held-out archive.
            frozen, sha = ba.read_predictions(args.predictions, manifest)
            fit_points = frozen["fit_points"]
            rebuilt = ba.frozen_predictions(fit_points, manifest, frozen["neg8_inputs"])
            # The committed content (fit points, rival lines, NEG-8 inputs, tier inputs,
            # sizes, manifest digest) is data; the module digest is provenance. Under the
            # committing module the content must rebuild exactly. Under a module changed
            # after the commitment (registration section 11, held-out agreement) the
            # rebuild is reported and flagged, and the committed content is evaluated as
            # committed; the corrected lines live in the second commitment.
            module = {"committed": frozen["bytes_analysis_sha256"], "evaluating": rebuilt["bytes_analysis_sha256"]}
            not_rebuilt = sorted(k for k in set(frozen) | set(rebuilt)
                                 if k != "bytes_analysis_sha256" and frozen.get(k) != rebuilt.get(k))
            if module["committed"] == module["evaluating"] and not_rebuilt:
                raise ba.AnalysisError("frozen line/fit-point mismatch")
            flags = [] if module["committed"] == module["evaluating"] else (
                ["bytes.module_changed_after_commitment"] + (["bytes.commitment_not_rebuilt"] if not_rebuilt else []))
            commitment = {"bytes_analysis_sha256": module, "flags": flags, "fields_not_rebuilt": not_rebuilt}
        held_passes, held_points = _reduce(source, manifest, "heldout", args.key_dir)
        points = fit_points + held_points
        _missing_labels(points)
        result = ba.evaluate(points, frozen)
        args.out.mkdir(parents=True, exist_ok=True)
        _write(args.out, "heldout_pass_estimates", held_passes)
        _write(args.out, "model_estimates", points)
        for name, rows in result.items():
            _write(args.out, name, rows)
        _write(args.out, "analysis_record", {"stage": args.stage, "predictions_sha256": sha,
                **commitment,
                "manifest_sha256": ba.digest(manifest), "H1_checks": frozen["H1_checks"],
                "H2_intervals": [{k: row[k] for k in ("selection", "basis", "boundary", "n", "k")}
                                 for row in result["h2"] if not row["description_only"]],
                "output_label": ba.OUTPUT_LABEL,
                "note": frozen["note"], "synthetic": manifest.get("synthetic", False)})
        print(json.dumps({"stage": args.stage, "predictions_sha256": sha, "out": str(args.out)}))
        return 0
    except StorageStop as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 1
    except (ba.AnalysisError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"BYTES analysis refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
