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
from joulewise.phase_share import (
    Interval,
    PhaseBoundaryError,
    phase_boundary_envelope,
)


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
        self.independent_prefill = Interval(15.0, 40.0)
        self.independent_decode = Interval(35.0, 60.0)

    def test_one_boundary_transfers_energy_and_rejects_impossible_box_totals(self) -> None:
        """Deleting the joint sweep restores the impossible 50--100 J box."""

        result = phase_boundary_envelope(
            self.curve,
            self.prefill,
            self.decode,
            boundary_bound_s=0.5,
            independent_prefill_energy_j=self.independent_prefill,
            independent_decode_energy_j=self.independent_decode,
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
            independent_prefill_energy_j=self.independent_prefill,
            independent_decode_energy_j=self.independent_decode,
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
            independent_prefill_energy_j=self.independent_prefill,
            independent_decode_energy_j=self.independent_decode,
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
                independent_prefill_energy_j=self.independent_prefill,
                independent_decode_energy_j=self.independent_decode,
            )

    def test_sweep_that_can_collapse_a_phase_is_refused(self) -> None:
        with self.assertRaisesRegex(PhaseBoundaryError, "collapse"):
            phase_boundary_envelope(
                self.curve,
                Window(0.9, 1.0),
                self.decode,
                boundary_bound_s=0.5,
                independent_prefill_energy_j=self.independent_prefill,
                independent_decode_energy_j=self.independent_decode,
            )

    def _write_bundle(
        self,
        parent: Path,
        *,
        status: str = "succeeded",
        prefill_bound: float = 0.5,
        decode_bound: float = 0.5,
        prefill_method: str | None = None,
        decode_method: str | None = None,
        prefill_energy: tuple[float, float, float] = (15.0, 25.0, 40.0),
        decode_energy: tuple[float, float, float] = (35.0, 50.0, 60.0),
        event_rows: list[tuple[float, str, str]] | None = None,
        metadata_bytes: bytes = b'{"device":{"rail_manifest":["total"]}}',
    ) -> Path:
        bundle = parent / "bundle-1"
        bundle.mkdir()
        (bundle / "metadata.json").write_bytes(metadata_bytes)
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
        if event_rows is None:
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

        def envelope(
            method: str | None,
            bound: float,
            energy: tuple[float, float, float],
        ) -> dict[str, float | str]:
            return {
                "method": method or ANALYZER.ANCHOR_SHIFT_METHOD,
                "anchor_bound_s": bound,
                "lower_j": energy[0],
                "point_j": energy[1],
                "upper_j": energy[2],
            }

        (bundle / "summary_metrics.json").write_text(
            json.dumps(
                {
                    "status": status,
                    "energy_anchor_shift_envelopes": {
                        "/phase_energy_j/prefill": envelope(
                            prefill_method, prefill_bound, prefill_energy
                        ),
                        "/phase_energy_j/decode": envelope(
                            decode_method, decode_bound, decode_energy
                        ),
                    },
                }
            ),
            encoding="utf-8",
        )
        return bundle

    def test_bundle_producer_seals_sources_and_reports_fixture_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            bundle = self._write_bundle(Path(temporary_directory))
            payload = ANALYZER.analyze_bundle(bundle)

        self.assertEqual(payload["claim_status"], "diagnostic_non_claim_bearing")
        self.assertEqual(
            payload["joint_sweep_bound_interpretation"],
            ANALYZER.BOUND_INTERPRETATION,
        )
        self.assertEqual(payload["independent_box_basis"], ANALYZER.BOX_BASIS)
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

    def test_retained_r01_current_wire_marginals_define_the_box(self) -> None:
        """The refuter's r01 box makes the former asserted 1.0 ratio fail."""

        prefill = (0.8540576948934585, 1.5869922431521415, 2.3199267914108246)
        decode = (49.08387764734075, 50.04031113792181, 50.99674462850287)
        with tempfile.TemporaryDirectory() as temporary_directory:
            bundle = self._write_bundle(
                Path(temporary_directory),
                prefill_energy=prefill,
                decode_energy=decode,
            )
            payload = ANALYZER.analyze_bundle(bundle)

        box = payload["envelope"]["independent_box_prefill_share"]
        self.assertAlmostEqual(box["lower"], 0.016471446084221675, places=15)
        self.assertAlmostEqual(box["upper"], 0.045131422017120414, places=15)
        retained_joint_width = 0.043838296558722796 - 0.017640500094209376
        self.assertAlmostEqual(
            retained_joint_width / (box["upper"] - box["lower"]),
            0.9140899673415641,
            places=15,
        )
        self.assertNotEqual(
            payload["comparison"]["joint_to_box_prefill_share_width_ratio"],
            1.0,
        )

    def test_changed_source_bytes_change_a_pinned_sha256_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            bundle = self._write_bundle(Path(temporary_directory))
            original = ANALYZER.analyze_bundle(bundle)
            self.assertEqual(
                original["source_sha256"]["metadata.json"],
                "7386959d73d0de47c1c551b3de49d2281241f0c82caff18439cfac5ba6ce36c9",
            )

            (bundle / "metadata.json").write_bytes(
                b'{"device": {"rail_manifest": ["total"]}}\n'
            )
            changed = ANALYZER.analyze_bundle(bundle)

        self.assertEqual(
            changed["source_sha256"]["metadata.json"],
            "f49d278b4a17e97784b62daa05afe24da8e3ce64c387baae3f8a3ee57dc12aa8",
        )
        self.assertNotEqual(
            original["source_sha256"]["metadata.json"],
            changed["source_sha256"]["metadata.json"],
        )

    def test_unequal_prefill_and_decode_bounds_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            bundle = self._write_bundle(
                Path(temporary_directory), decode_bound=0.25
            )
            with self.assertRaisesRegex(
                ANALYZER.PhaseShareAnalysisRefused, "one boundary bound"
            ):
                ANALYZER.analyze_bundle(bundle)

    def test_non_v3_phase_envelope_method_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            bundle = self._write_bundle(
                Path(temporary_directory),
                prefill_method="common_trace_shift_plus_independent_edge_span_v2",
            )
            with self.assertRaisesRegex(
                ANALYZER.PhaseShareAnalysisRefused, "current-wire corner envelope"
            ):
                ANALYZER.analyze_bundle(bundle)

    def test_invalid_current_wire_energy_interval_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            bundle = self._write_bundle(
                Path(temporary_directory), prefill_energy=(15.0, 25.0, 20.0)
            )
            with self.assertRaisesRegex(
                ANALYZER.PhaseShareAnalysisRefused, "energy envelope is invalid"
            ):
                ANALYZER.analyze_bundle(bundle)

    def test_failed_summary_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            bundle = self._write_bundle(Path(temporary_directory), status="failed")
            with self.assertRaisesRegex(
                ANALYZER.PhaseShareAnalysisRefused, "succeeded bundle"
            ):
                ANALYZER.analyze_bundle(bundle)

    def test_duplicate_phase_windows_are_refused(self) -> None:
        duplicate_prefill_rows = [
            (-0.9, "phase_start", "prefill"),
            (-0.8, "phase_end", "prefill"),
            (-0.5, "phase_start", "prefill"),
            (1.0, "phase_end", "prefill"),
            (1.0, "phase_start", "decode"),
            (2.5, "phase_end", "decode"),
        ]
        with tempfile.TemporaryDirectory() as temporary_directory:
            bundle = self._write_bundle(
                Path(temporary_directory), event_rows=duplicate_prefill_rows
            )
            with self.assertRaisesRegex(
                ANALYZER.PhaseShareAnalysisRefused,
                "exactly one prefill and one decode",
            ):
                ANALYZER.analyze_bundle(bundle)


if __name__ == "__main__":
    unittest.main()
