"""Oracles for the desk-only partial-record enclosure."""

from __future__ import annotations

import hashlib
import io
import json
import math
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as ET

from joulewise.bundle_read import TracePoint, Window
from scripts.paper import partial_record_enclosure as enclosure


REPO_ROOT = Path(__file__).resolve().parent.parent
STRICT_SEED_BUNDLE = (
    REPO_ROOT / "tests/fixtures/d117_v2_production/strict_seed_bundle"
)


class PartialRecordEnclosureTests(unittest.TestCase):
    def test_synthetic_p1_entry_and_timing_corner_oracles(self) -> None:
        with mock.patch.object(enclosure, "derive_bundle") as authenticated:
            data = enclosure.derive_synthetic_p1()
        authenticated.assert_not_called()
        self.assertEqual(data["label"], "SYNTHETIC P1")
        self.assertFalse(data["claim_bearing"])
        self.assertEqual(data["inputs"]["window_s"], [0.55, 1.45])
        self.assertEqual(data["inputs"]["independent_edge_shift_s"], [-0.01, 0.01])
        self.assertEqual(len(data["inputs"]["records"]), 10)
        for i, record in enumerate(data["inputs"]["records"]):
            self.assertAlmostEqual(record["start_s"], 0.5 + i * 0.1)
            self.assertAlmostEqual(record["end_s"] - record["start_s"], 0.1)
            self.assertEqual(record["power_w"], 10)
        result = data["outputs"]
        self.assertEqual(result["scope"], "synthetic_p1_fixed_window.v1")
        for field, expected in (("point_j", 9), ("lower_j", 8), ("upper_j", 10)):
            self.assertAlmostEqual(result[field], expected)
        self.assertEqual(result["straddling_record_count"], 2)
        self.assertAlmostEqual(result["straddling_energy_j"], 2)
        for corner, expected in zip(result["timing_corners"], (9, 9.2, 8.8, 9)):
            self.assertAlmostEqual(corner["point_j"], expected)
        for actual, expected in zip(result["timing_envelope_j"], (8.8, 9.2)):
            self.assertAlmostEqual(actual, expected)

    def test_synthetic_figure_and_sidecar_reproduce_exactly(self) -> None:
        base = REPO_ROOT / "docs/paper/figures/figA_partial_record_enclosure"
        data = json.loads(base.with_suffix(".json").read_text())
        actual_svg = base.with_suffix(".svg").read_bytes()
        self.assertEqual(data["figure"]["sha256"], hashlib.sha256(actual_svg).hexdigest())
        with tempfile.TemporaryDirectory() as directory:
            svg, sidecar = Path(directory) / "figure.svg", Path(directory) / "figure.json"
            enclosure.write_synthetic_p1_figure(svg, sidecar)
            self.assertEqual(svg.read_bytes(), actual_svg)
            self.assertEqual(sidecar.read_bytes(), base.with_suffix(".json").read_bytes())
        root = ET.fromstring(actual_svg)
        ns = {"s": "http://www.w3.org/2000/svg"}
        self.assertIn("SYNTHETIC P1", root.find("s:title", ns).text)
        labels = [el.text for el in root.findall(".//s:text", ns)]
        self.assertTrue(set(f"R{i}" for i in range(1, 11)).issubset(labels))
        self.assertIn("Point 9.0 J", labels)
        self.assertIn("Timing [8.8, 9.2] J", labels)
        self.assertIn("Nonnegative [8, 10] J", labels)

    def assert_cli_refusal(self, bundle: Path, reason: str) -> None:
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            redirect_stdout(stdout),
            redirect_stderr(stderr),
            mock.patch.object(
                enclosure, "enclose_phase", wraps=enclosure.enclose_phase
            ) as derive_phase,
        ):
            self.assertEqual(enclosure.main([str(bundle)]), 2)
        self.assertEqual(stdout.getvalue(), "", "refusal must emit no enclosure")
        refusal = json.loads(stderr.getvalue())
        self.assertEqual(set(refusal), {"status", "reason", "detail"})
        self.assertEqual(refusal["status"], "refused")
        self.assertEqual(refusal["reason"], reason)
        derive_phase.assert_not_called()

    def test_registry_pins_current_script_bytes(self) -> None:
        registry = (REPO_ROOT / "docs/paper/results-fill-registry.md").read_text(
            encoding="utf-8"
        )
        rows = [line for line in registry.splitlines() if line.startswith("| PE-01 — ")]
        self.assertEqual(len(rows), 1)
        supplier = rows[0].split("|")[3].strip()
        pin = re.search(
            r"`scripts/paper/partial_record_enclosure\.py`, "
            r"SHA-256 `([0-9a-f]{64})`, ([0-9,]+) B",
            supplier,
        )
        self.assertIsNotNone(pin, "PE-01 must pin its producer in the supplier cell")
        assert pin is not None
        script = (REPO_ROOT / "scripts/paper/partial_record_enclosure.py").read_bytes()
        self.assertEqual(pin.group(1), hashlib.sha256(script).hexdigest())
        self.assertEqual(int(pin.group(2).replace(",", "")), len(script))

    def test_strict_validation_tamper_refuses_without_enclosure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            shutil.copytree(STRICT_SEED_BUNDLE, bundle)
            summary_path = bundle / "summary_metrics.json"
            summary = json.loads(summary_path.read_bytes())
            summary["phase_energy_j"]["decode"] += 1.0
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            self.assert_cli_refusal(bundle, "bundle_strict_validation_failed")

    def test_bundle_digest_drift_refuses_without_enclosure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle"
            shutil.copytree(STRICT_SEED_BUNDLE, bundle)
            census = enclosure._bundle_sha256_census

            def drift_before_census(path: Path) -> list[dict]:
                # Change real bytes after strict validation, preserving JSON
                # meaning so only the authentication digest can catch drift.
                summary_path = path / "summary_metrics.json"
                summary_path.write_bytes(summary_path.read_bytes() + b"\n")
                return census(path)

            with mock.patch.object(
                enclosure, "_bundle_sha256_census", side_effect=drift_before_census
            ):
                self.assert_cli_refusal(bundle, "v2_authentication_input_changed")

    def test_phase_summary_window_mismatch_refuses_without_enclosure(self) -> None:
        load_contributions = enclosure._load_contributions

        def omit_decode_window(reader):
            # Inject inconsistent window interpretation at the consumer seam;
            # the real strict validator still authenticates the clean fixture.
            contributions = load_contributions(reader)
            del contributions["decode"]
            return contributions

        with mock.patch.object(
            enclosure, "_load_contributions", side_effect=omit_decode_window
        ):
            self.assert_cli_refusal(STRICT_SEED_BUNDLE, "phase_summary_window_mismatch")

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
