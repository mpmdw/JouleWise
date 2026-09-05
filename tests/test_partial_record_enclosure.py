"""Oracles for the desk-only partial-record enclosure."""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

from joulewise.bundle_read import TracePoint, Window
from scripts.paper import partial_record_enclosure as enclosure


REPO_ROOT = Path(__file__).resolve().parent.parent


class PartialRecordEnclosureTests(unittest.TestCase):
    @staticmethod
    def interval_curve(
        *, start_s: float, count: int, power_w: float
    ) -> list[TracePoint]:
        return [
            TracePoint(
                t=start_s + (index + 1) / 10,
                power_w=power_w,
                support_start_s=start_s + index / 10,
                support_end_s=start_s + (index + 1) / 10,
            )
            for index in range(count)
        ]

    def test_p1_oracle_and_half_record_mutation_kill(self) -> None:
        curve = self.interval_curve(start_s=0.5, count=10, power_w=10.0)

        result = enclosure.enclose_phase(
            "decode", [(curve, [Window(0.55, 1.45)])]
        )

        self.assertAlmostEqual(result["point_j"], 9.0, places=9)
        self.assertAlmostEqual(result["lower_j"], 8.0, places=9)
        self.assertAlmostEqual(result["upper_j"], 10.0, places=9)
        self.assertEqual(result["straddling_record_count"], 2)
        self.assertAlmostEqual(result["straddling_energy_j"], 2.0, places=9)
        self.assertEqual(result["basis"], enclosure.BASIS)

        # The killed mutation replaces each straddler's [0,Q] by [Q/2,Q/2].
        mutated_endpoint = result["lower_j"] + result["straddling_energy_j"] / 2
        self.assertAlmostEqual(mutated_endpoint, 9.0, places=9)
        self.assertNotEqual(mutated_endpoint, result["lower_j"])
        self.assertNotEqual(mutated_endpoint, result["upper_j"])

    def test_01_f1_oracle(self) -> None:
        curve = self.interval_curve(start_s=0.0, count=6, power_w=50.0)

        result = enclosure.enclose_phase(
            "prefill", [(curve, [Window(0.05, 0.45)])]
        )

        self.assertAlmostEqual(result["point_j"], 20.0, places=9)
        self.assertAlmostEqual(result["lower_j"], 15.0, places=9)
        self.assertAlmostEqual(result["upper_j"], 25.0, places=9)
        self.assertEqual(result["straddling_record_count"], 2)

    def test_record_aligned_edges_collapse_to_point(self) -> None:
        curve = self.interval_curve(start_s=0.0, count=6, power_w=50.0)

        result = enclosure.enclose_phase(
            "prefill", [(curve, [Window(0.1, 0.5)])]
        )

        self.assertAlmostEqual(result["point_j"], 20.0, places=9)
        self.assertAlmostEqual(result["lower_j"], result["point_j"], places=9)
        self.assertAlmostEqual(result["upper_j"], result["point_j"], places=9)
        self.assertEqual(result["straddling_record_count"], 0)
        self.assertEqual(result["straddling_energy_j"], 0.0)

    def test_negative_power_refuses_with_named_reason(self) -> None:
        curve = self.interval_curve(start_s=0.0, count=6, power_w=50.0)
        curve[2] = TracePoint(
            t=curve[2].t,
            power_w=-1.0,
            support_start_s=curve[2].support_start_s,
            support_end_s=curve[2].support_end_s,
        )

        with self.assertRaises(enclosure.EnclosureRefusal) as caught:
            enclosure.enclose_phase("prefill", [(curve, [Window(0.05, 0.45)])])

        self.assertEqual(caught.exception.reason, "negative_reported_power")

    def test_window_wholly_inside_one_record_is_zero_to_q(self) -> None:
        curve = [
            TracePoint(
                t=1.0,
                power_w=10.0,
                support_start_s=0.0,
                support_end_s=1.0,
            )
        ]

        result = enclosure.enclose_phase(
            "decode", [(curve, [Window(0.25, 0.75)])]
        )

        self.assertEqual(result["point_j"], 5.0)
        self.assertEqual(result["lower_j"], 0.0)
        self.assertEqual(result["upper_j"], 10.0)
        self.assertEqual(result["straddling_record_count"], 1)
        self.assertEqual(result["straddling_energy_j"], 10.0)

    def test_point_supported_records_refuse_with_named_reason(self) -> None:
        curve = [TracePoint(t=0.0, power_w=1.0)]

        with self.assertRaises(enclosure.EnclosureRefusal) as caught:
            enclosure.enclose_phase("decode", [(curve, [Window(0.0, 1.0)])])

        self.assertEqual(
            caught.exception.reason, "point_supported_records_unsupported"
        )

    def test_nonfinite_power_refuses_with_named_reason(self) -> None:
        for power_w in (math.nan, math.inf, -math.inf):
            with self.subTest(power_w=power_w):
                curve = [
                    TracePoint(
                        t=1.0,
                        power_w=power_w,
                        support_start_s=0.0,
                        support_end_s=1.0,
                    )
                ]
                with self.assertRaises(enclosure.EnclosureRefusal) as caught:
                    enclosure.enclose_phase(
                        "decode", [(curve, [Window(0.0, 1.0)])]
                    )
                self.assertEqual(
                    caught.exception.reason, "nonfinite_reported_power"
                )

    def test_tracked_bundle_derivation_leaves_summary_byte_identical(self) -> None:
        bundle = (
            REPO_ROOT
            / "tests"
            / "fixtures"
            / "d117_v2_production"
            / "strict_seed_bundle"
        )
        summary_path = bundle / "summary_metrics.json"
        before = summary_path.read_bytes()
        stored_phase_points = json.loads(before)["phase_energy_j"]

        result = enclosure.derive_bundle(bundle)

        self.assertEqual(summary_path.read_bytes(), before)
        self.assertEqual(set(result), set(stored_phase_points))
        for phase, point_j in stored_phase_points.items():
            self.assertAlmostEqual(result[phase]["point_j"], point_j, places=9)
            self.assertEqual(result[phase]["scope"], enclosure.FIXED_WINDOW_SCOPE)
        census = result["decode"]["inputs"]["bundle_sha256_census"]
        self.assertIn("summary_metrics.json", {row["path"] for row in census})


if __name__ == "__main__":
    unittest.main()
