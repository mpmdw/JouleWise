#!/usr/bin/env python3
"""Desk-only BYTES analysis; never launches a model or collector."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from joulewise import bytes_analysis as ba


def _write(out, name, payload):
    path = out / (name + ".json")
    if path.exists():
        raise ba.AnalysisError(f"output already exists: {path.name}")
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n")


def _reduce(source, manifest, stage):
    records = ba.load_records(source, manifest, stage=stage)
    passes = ba.reduce_models(records, manifest) + ba.reduce_models(records, manifest, inclusive=True)
    return passes, ba.combine_passes(passes)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--export", type=Path, help="Block-6 export directory; manifest must locate matching archives")
    source.add_argument("--records", type=Path, nargs="+", help="harvest archive or withheld/member-assessments.json")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--stage", required=True, choices=("fit", "heldout", "all"))
    parser.add_argument("--predictions", type=Path, help="fit-stage predictions.json, with predictions.sha256 beside it")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = ba.validate_manifest(ba.read_json(args.manifest))
        source = args.export or args.records
        if args.stage == "heldout" and args.predictions is None:
            raise ba.AnalysisError("heldout requires --predictions and its SHA-256 sidecar")
        if args.stage == "all" and manifest.get("synthetic") is not True:
            raise ba.AnalysisError("all is synthetic-only; real inputs require separately committed fit predictions")
        if args.stage != "heldout":
            fit_passes, fit_points = _reduce(source, manifest, "fit")
            frozen = ba.frozen_predictions(fit_points, manifest)
            sha = ba.write_predictions(args.out, frozen)
            _write(args.out, "fit_pass_estimates", fit_passes)
            if args.stage == "fit":
                print(json.dumps({"stage": "fit", "predictions_sha256": sha, "out": str(args.out)}))
                return 0
        else:
            # Validate the commitment before opening any held-out archive.
            frozen, sha = ba.read_predictions(args.predictions, manifest)
            fit_points = frozen["fit_points"]
            if ba.frozen_predictions(fit_points, manifest) != frozen:
                raise ba.AnalysisError("frozen line/fit-point mismatch")
        held_passes, held_points = _reduce(source, manifest, "heldout")
        points = fit_points + held_points
        result = ba.evaluate(points, frozen)
        args.out.mkdir(parents=True, exist_ok=True)
        _write(args.out, "heldout_pass_estimates", held_passes)
        _write(args.out, "model_estimates", points)
        for name, rows in result.items():
            _write(args.out, name, rows)
        _write(args.out, "analysis_record", {"stage": args.stage, "predictions_sha256": sha,
                "manifest_sha256": ba.digest(manifest), "H1_checks": ba.H1_CHECKS,
                "H2_intervals": ba.H2_INTERVALS, "output_label": ba.OUTPUT_LABEL,
                "note": frozen["note"], "synthetic": manifest.get("synthetic", False)})
        print(json.dumps({"stage": args.stage, "predictions_sha256": sha, "out": str(args.out)}))
        return 0
    except (ba.AnalysisError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"BYTES analysis refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
