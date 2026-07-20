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
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.floor_extraction import FloorExtractionError, extract_cells  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs-root",
        required=True,
        type=Path,
        help="corpus root containing the member bundles and campaign_manifests/",
    )
    parser.add_argument(
        "--spec",
        required=True,
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
        "--hash-bundles",
        action="store_true",
        help="record complete-bundle and config sha256 pins per member",
    )
    args = parser.parse_args(argv)

    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"error: cannot read extraction spec: {exc}", file=sys.stderr)
        return 2
    if not args.runs_root.is_dir():
        print(f"error: runs root is not a directory: {args.runs_root}", file=sys.stderr)
        return 2

    try:
        report = extract_cells(
            args.runs_root,
            spec,
            manifest_id=args.manifest_id,
            hash_bundles=args.hash_bundles,
        )
    except FloorExtractionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    refused = [
        cell["cell_id"] for cell in report["cells"] if not cell["extractable"]
    ]
    if refused:
        print(
            "refused cells (fail-closed): " + ", ".join(sorted(refused)),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
