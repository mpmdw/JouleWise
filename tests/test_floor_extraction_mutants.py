"""Synthetic extraction regressions with independent numeric and gate oracles."""

import math
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise import floor_extraction as extraction
from tests.test_floor_extraction import make_summary, write_bundle


def synthetic_member(index, value=10.0, width=0.0, lineage=None, comparative=False):
    return extraction.MemberReport(
        slot=f"s{index}", bundle_id=f"b{index}",
        block_id=f"g{index // 4}" if comparative else None,
        position=("A1", "B1", "B2", "A2")[index % 4] if comparative else None,
        value_j=value, cooldown_result="recovered", cooldown_verified=True,
        cap_hit=False, excluded=False, reasons=(), anchor_shift_bound_j=width,
        operative_anchor_envelope={"half_width_j": width}, consumption_provenance={},
        summary_sha256="a" * 64, bundle_sha256="b" * 64, config_sha256="c" * 64,
        launch_lineage=lineage,
    )


def absolute_row(members):
    by_id = {member.bundle_id: member for member in members}
    with patch.object(extraction, "_evaluate_member",
                      side_effect=lambda **kw: by_id[kw["bundle_id"]]):
        return extraction.extract_absolute_cell(
            cell_id="synthetic", metric="gross_energy_j", window_class="request",
            members=[{"slot": member.slot, "bundle_id": member.bundle_id} for member in members],
            runs_root=Path("/synthetic"), cooldowns={},
        ).as_row()


class MemberEnvelopeTests(unittest.TestCase):
    def member_row(self, value):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_bundle(root, "synthetic", make_summary(
                value, anchor_bound=1.0, interpolation_bound=0.25,
            ))
            identity = SimpleNamespace(custody_bound_config=False, triangle_agrees=True,
                                       mock_config=False)
            with (
                patch.object(extraction, "custody_telemetry_identity", return_value=identity),
                patch.object(extraction, "_cpu_admission_bundle_reasons", return_value=()),
                patch.object(extraction, "authenticate_bundle_launch_lineage", return_value=None),
            ):
                row = extraction.extract_absolute_cell(
                    cell_id="synthetic", metric="gross_energy_j", window_class="request",
                    members=[{"slot": "s", "bundle_id": "synthetic"}], runs_root=root,
                    cooldowns={"synthetic": {"verified": True, "result": "recovered"}},
                    hash_bundles=False, strict_validator=lambda path, strict: (),
                ).as_row()
        return row["members"][0]

    def test_interpolation_adds_to_member_envelope(self):
        """The member width adds anchor and joint interpolation terms. Kills M01678."""
        member = self.member_row(16.0)
        # Exact dyadic arithmetic: 1 + 1/4 = 5/4 J, not 3/4 J.
        self.assertEqual(member["anchor_shift_bound_j"], 1.25)

    def test_quarter_metric_boundary_is_admitted(self):
        """A width exactly one quarter of the metric is admitted. Kills M01714."""
        member = self.member_row(5.0)
        # All arithmetic is exact in binary64: (1 + 1/4) / 5 = 1/4.
        self.assertEqual(member["reasons"], [])

    def test_zero_metric_with_nonzero_envelope_has_typed_refusal(self):
        """Zero energy with uncertainty refuses without dividing by zero. Kills M01710."""
        member = self.member_row(0.0)
        self.assertIn("anchor_energy_envelope_exceeds_quarter_metric", member["reasons"])


class CellProjectionTests(unittest.TestCase):
    def test_exactly_two_launch_lineages_refuse(self):
        """Two distinct launch lineages cannot form one absolute cell. Kills M01411."""
        members = [synthetic_member(i, lineage={"synthetic_id": str(i % 2)})
                   for i in range(5)]
        row = absolute_row(members)
        self.assertEqual(row["refusal_reasons"], ["launch_lineage_conflict"])
        self.assertEqual(row["n_admitted"], 0)

    def test_uncertainty_dominated_cell_keeps_its_label(self):
        """A widened constant-energy cell carries the attribution condition. Kills M01508."""
        row = absolute_row([synthetic_member(i, width=0.125) for i in range(5)])
        # Identical points have exactly zero scatter; nonzero admitted widths
        # create a positive floor, so the attribution condition must survive.
        self.assertEqual(row["floor_conditions"],
                         ["admissible_set_uncertainty_dominates_point_floor"])
        self.assertTrue(row["extractable"])

    def test_serialized_point_diagnostic_keeps_dominating_prediction(self):
        """The serialized diagnostic uses the larger prediction term. Kills M01218 and M01220."""
        values = [100.0, 100.0, 100.0, 100.0, 110.0]
        row = absolute_row([synthetic_member(i, value=value, width=8.0)
                            for i, value in enumerate(values)])
        # Mean=102; residuals=(-2,-2,-2,-2,8); sample variance=80/4=20.
        # Widths of 8 J admit a 20.8 J residual, so this cell is labelled.
        # Prediction=2.776*sqrt(20)*sqrt(6/5)=2.776*sqrt(24) > max|r|=8.
        # n=5 guard=sqrt(9/4)=1.5, giving 20.39935058 J.
        expected = 1.5 * 2.776 * math.sqrt(24.0)
        # Bar: 1e-6 relative (COMMON fallback; no printed half-width).
        # Both mutants emit 12 J, a loss of 8.399 J (>410,000 bars).
        self.assertAlmostEqual(row["point_floor_diagnostic"]["guarded_floor_j"],
                               expected, delta=expected * 1e-6)

    def test_comparative_anchor_maximum_includes_nonfirst_members(self):
        """Comparative anchor diagnostics retain the largest member width. Kills M01539."""
        members = [synthetic_member(i, value=16.0, width=(i + 1) / 8.0, comparative=True)
                   for i in range(8)]
        by_id = {member.bundle_id: member for member in members}
        blocks = [{"block_id": f"g{i}", "members": dict(zip(
            ("A1", "B1", "B2", "A2"), [f"b{i * 4 + j}" for j in range(4)],
        ))} for i in range(2)]
        with patch.object(extraction, "_evaluate_member",
                          side_effect=lambda **kw: by_id[kw["bundle_id"]]):
            row = extraction.extract_comparative_cell(
                cell_id="synthetic", metric="gross_energy_j", window_class="request",
                blocks=blocks, runs_root=Path("/synthetic"), cooldowns={},
            ).as_row()
        # Widths are exactly representable eighths, from 1/8 through 8/8 J.
        self.assertEqual(row["anchor_shift_bound_max_j"], 1.0)


class ReaderThroughputTests(unittest.TestCase):
    def test_subunit_and_zero_throughput_are_valid(self):
        """Finite nonnegative reader throughput includes zero and a half. Kills M01488."""
        for value in (0.0, 0.5):
            with self.subTest(value=value):
                # Both values are exact in binary64; legacy throughput must
                # not replace the governed reader-facing value.
                self.assertEqual(extraction.reader_throughput_tokens_s({
                    extraction.READER_THROUGHPUT_FIELD: value,
                    extraction.LEGACY_THROUGHPUT_FIELD: 99.0,
                }), value)
