#!/usr/bin/env python3
"""Replay one bundle's prefill/decode allocation over its shared boundary.

This is a desk-analysis producer, not a claim-path reducer.  It reads the
current-wire boundary bound from both stored phase envelopes, requires the two
copies to agree, and re-integrates the retained interval-support power curve.
The JSON result seals the three source files used for the calculation.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.bundle_read import BundleReadError, BundleReader
from joulewise.phase_share import PhaseBoundaryError, phase_boundary_envelope
from joulewise.reduce import ANCHOR_SHIFT_METHOD


SCHEMA_VERSION = "joulewise.phase_share_diagnostic.v1"
REFUSAL_EXIT_CODE = 2


class PhaseShareAnalysisRefused(RuntimeError):
    """The bundle does not carry the evidence required by this diagnostic."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _phase_envelope(summary: dict[str, Any], phase: str) -> dict[str, Any]:
    envelopes = summary.get("energy_anchor_shift_envelopes")
    candidate = (
        envelopes.get(f"/phase_energy_j/{phase}")
        if isinstance(envelopes, dict)
        else None
    )
    if not isinstance(candidate, dict):
        raise PhaseShareAnalysisRefused(f"{phase} phase envelope is absent")
    if candidate.get("method") != ANCHOR_SHIFT_METHOD:
        raise PhaseShareAnalysisRefused(
            f"{phase} phase envelope is not a current-wire corner envelope"
        )
    bound = candidate.get("anchor_bound_s")
    if (
        isinstance(bound, bool)
        or not isinstance(bound, (int, float))
        or not math.isfinite(float(bound))
        or float(bound) < 0.0
    ):
        raise PhaseShareAnalysisRefused(f"{phase} phase boundary bound is invalid")
    return candidate


def analyze_bundle(bundle: Path) -> dict[str, Any]:
    """Return a provenance-bearing phase-boundary diagnostic for ``bundle``."""

    reader = BundleReader(bundle)
    resolved = reader.path
    summary = reader.raw_summary()
    if not isinstance(summary, dict):
        raise PhaseShareAnalysisRefused("summary_metrics.json is absent or unreadable")
    if summary.get("status") != "succeeded":
        raise PhaseShareAnalysisRefused("only a succeeded bundle can be analyzed")

    prefill_envelope = _phase_envelope(summary, "prefill")
    decode_envelope = _phase_envelope(summary, "decode")
    prefill_bound = float(prefill_envelope["anchor_bound_s"])
    decode_bound = float(decode_envelope["anchor_bound_s"])
    if prefill_bound != decode_bound:
        raise PhaseShareAnalysisRefused(
            "prefill and decode phase envelopes do not carry one boundary bound"
        )

    windows = reader.phase_windows()
    prefill_windows = windows.get("prefill")
    decode_windows = windows.get("decode")
    if (
        not isinstance(prefill_windows, list)
        or len(prefill_windows) != 1
        or not isinstance(decode_windows, list)
        or len(decode_windows) != 1
    ):
        raise PhaseShareAnalysisRefused(
            "exactly one prefill and one decode phase window are required"
        )

    result = phase_boundary_envelope(
        reader.summed_curve(),
        prefill_windows[0],
        decode_windows[0],
        prefill_bound,
    )
    source_names = (
        "power_trace.csv",
        "events.jsonl",
        "metadata.json",
        "summary_metrics.json",
    )
    try:
        source_sha256 = {name: _sha256(resolved / name) for name in source_names}
    except OSError as exc:
        raise PhaseShareAnalysisRefused(f"source evidence cannot be read: {exc}") from exc

    joint_share_width = (
        result.joint_prefill_share.upper - result.joint_prefill_share.lower
    )
    box_share_width = (
        result.independent_box_prefill_share.upper
        - result.independent_box_prefill_share.lower
    )
    joint_asymmetry_width = (
        result.joint_normalized_decode_minus_prefill.upper
        - result.joint_normalized_decode_minus_prefill.lower
    )
    box_asymmetry_width = (
        result.independent_box_normalized_decode_minus_prefill.upper
        - result.independent_box_normalized_decode_minus_prefill.lower
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "claim_status": "diagnostic_non_claim_bearing",
        "bundle_id": resolved.name,
        "source_sha256": source_sha256,
        "source_phase_envelope_method": ANCHOR_SHIFT_METHOD,
        "source_boundary_bound_s": prefill_bound,
        "nominal_phase_marker_gap_s": (
            decode_windows[0].start_s - prefill_windows[0].end_s
        ),
        "envelope": asdict(result),
        "comparison": {
            "joint_prefill_share_width": joint_share_width,
            "independent_box_prefill_share_width": box_share_width,
            "joint_to_box_prefill_share_width_ratio": (
                joint_share_width / box_share_width if box_share_width else None
            ),
            "joint_normalized_asymmetry_width": joint_asymmetry_width,
            "independent_box_normalized_asymmetry_width": box_asymmetry_width,
            "joint_to_box_normalized_asymmetry_width_ratio": (
                joint_asymmetry_width / box_asymmetry_width
                if box_asymmetry_width
                else None
            ),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="retained bundle directory")
    args = parser.parse_args(argv)
    try:
        payload = analyze_bundle(args.bundle)
    except (BundleReadError, PhaseBoundaryError, PhaseShareAnalysisRefused) as exc:
        print(
            json.dumps(
                {"status": "refused", "detail": str(exc)},
                sort_keys=True,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return REFUSAL_EXIT_CODE
    print(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
