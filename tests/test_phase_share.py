"""Counterfactual tests for the shared prefill/decode boundary sweep."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

from joulewise.bundle_read import TracePoint, Window
from joulewise.phase_share import PhaseBoundaryError, phase_boundary_envelope


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "analyze_phase_share.py"
SPEC = importlib.util.spec_from_file_location("analyze_phase_share", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
ANALYZER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ANALYZER
SPEC.loader.exec_module(ANALYZER)


def _point(power_w: float, start_s: float, end_s: float) -> TracePoint:
    return TracePoint(
        t=end_s,
        power_w=power_w,
        support_start_s=start_s,
        support_end_s=end_s,
    )


class PhaseBoundaryEnvelopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.curve = [
            _point(10.0, -1.0, 0.0),
            _point(20.0, 0.0, 1.0),
            _point(30.0, 1.0, 2.0),
            _point(40.0, 2.0, 3.0),
        ]
        self.prefill = Window(-0.5, 1.0)
        self.decode = Window(1.0, 2.5)

    def test_one_boundary_transfers_energy_and_rejects_impossible_box_totals(self) -> None:
        """Deleting the joint sweep restores the impossible 50--100 J box."""

        result = phase_boundary_envelope(
            self.curve,
            self.prefill,
            self.decode,
            boundary_bound_s=0.5,
        )

        self.assertEqual(result.prefill_energy_j.lower, 15.0)
        self.assertEqual(result.prefill_energy_j.upper, 40.0)
        self.assertEqual(result.decode_energy_j.lower, 35.0)
        self.assertEqual(result.decode_energy_j.upper, 60.0)
        self.assertEqual(result.joint_total_phase_energy_j.lower, 75.0)
        self.assertEqual(result.joint_total_phase_energy_j.upper, 75.0)
        self.assertEqual(result.independent_box_total_phase_energy_j.lower, 50.0)
        self.assertEqual(result.independent_box_total_phase_energy_j.upper, 100.0)
        for point in result.curve:
            self.assertEqual(point.total_phase_energy_j, 75.0)

    def test_scalar_share_and_normalized_asymmetry_keep_the_box_endpoints(self) -> None:
        """The row's proposed scalar gain is zero for pure boundary transfer."""

        result = phase_boundary_envelope(
            self.curve,
            self.prefill,
            self.decode,
            boundary_bound_s=0.5,
        )

        self.assertEqual(
            result.joint_prefill_share,
            result.independent_box_prefill_share,
        )
        self.assertEqual(
            result.joint_normalized_decode_minus_prefill,
            result.independent_box_normalized_decode_minus_prefill,
        )
        self.assertTrue(
            math.isclose(result.joint_prefill_share.lower, 0.2, abs_tol=1e-15)
        )
        self.assertTrue(
            math.isclose(
                result.joint_prefill_share.upper,
                8.0 / 15.0,
                abs_tol=1e-15,
            )
        )

    def test_every_measured_support_crossing_is_on_the_curve(self) -> None:
        curve = [
            _point(10.0, -1.0, 0.0),
            _point(20.0, 0.0, 1.2),
            _point(40.0, 1.2, 3.0),
        ]
        result = phase_boundary_envelope(
            curve,
            self.prefill,
            self.decode,
            boundary_bound_s=0.5,
        )

        self.assertIn(
            0.2,
            [round(point.boundary_shift_s, 12) for point in result.curve],
        )

    def test_unmeasured_point_interpolation_is_refused(self) -> None:
        with self.assertRaisesRegex(PhaseBoundaryError, "interval support"):
            phase_boundary_envelope(
                [TracePoint(t=0.0, power_w=10.0)],
                self.prefill,
                self.decode,
                boundary_bound_s=0.5,
            )

    def test_sweep_that_can_collapse_a_phase_is_refused(self) -> None:
        with self.assertRaisesRegex(PhaseBoundaryError, "collapse"):
            phase_boundary_envelope(
                self.curve,
                Window(0.9, 1.0),
                self.decode,
                boundary_bound_s=0.5,
            )

    def test_bundle_producer_seals_sources_and_reports_the_scalar_null_gain(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            bundle = Path(temporary_directory) / "bundle-1"
            bundle.mkdir()
            (bundle / "metadata.json").write_text(
                json.dumps({"device": {"rail_manifest": ["total"]}}),
                encoding="utf-8",
            )
            with (bundle / "power_trace.csv").open(
                "w", encoding="utf-8", newline=""
            ) as handle:
                writer = csv.writer(handle, lineterminator="\n")
                writer.writerow(
                    [
                        "timestamp_s",
                        "power_w",
                        "source",
                        "rail",
                        "interval_start_s",
                        "interval_end_s",
                    ]
                )
                for point in self.curve:
                    writer.writerow(
                        [
                            point.t,
                            point.power_w,
                            "fixture",
                            "total",
                            point.support_start_s,
                            point.support_end_s,
                        ]
                    )
            event_rows = [
                (-0.5, "phase_start", "prefill"),
                (1.0, "phase_end", "prefill"),
                (1.0, "phase_start", "decode"),
                (2.5, "phase_end", "decode"),
            ]
            (bundle / "events.jsonl").write_text(
                "".join(
                    json.dumps(
                        {
                            "timestamp_s": timestamp,
                            "event_type": event_type,
                            "phase": phase,
                            "message": "fixture",
                            "metadata": {},
                        }
                    )
                    + "\n"
                    for timestamp, event_type, phase in event_rows
                ),
                encoding="utf-8",
            )
            envelope = {
                "method": ANALYZER.ANCHOR_SHIFT_METHOD,
                "anchor_bound_s": 0.5,
            }
            (bundle / "summary_metrics.json").write_text(
                json.dumps(
                    {
                        "status": "succeeded",
                        "energy_anchor_shift_envelopes": {
                            "/phase_energy_j/prefill": envelope,
                            "/phase_energy_j/decode": envelope,
                        },
                    }
                ),
                encoding="utf-8",
            )

            payload = ANALYZER.analyze_bundle(bundle)

        self.assertEqual(payload["claim_status"], "diagnostic_non_claim_bearing")
        self.assertEqual(
            set(payload["source_sha256"]),
            {
                "power_trace.csv",
                "events.jsonl",
                "metadata.json",
                "summary_metrics.json",
            },
        )
        self.assertEqual(
            payload["comparison"]["joint_to_box_prefill_share_width_ratio"],
            1.0,
        )
        self.assertEqual(
            payload["comparison"][
                "joint_to_box_normalized_asymmetry_width_ratio"
            ],
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
