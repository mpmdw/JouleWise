"""Synthetic floor arithmetic, boundary, and provenance regressions."""

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise import detection_floor as floor
from tests.test_detection_floor import (
    MINT1_PINSET_PATH, make_artifact, make_cell, make_regime, write_pinset,
)


class FloorArithmeticTests(unittest.TestCase):
    def test_shared_bound_cannot_embed_allowance_twice(self):
        """A shared operative bound contains one allowance. Kills M01010."""
        # All terms are dyadic: the recorded allowance is 1/64 s, but
        # the applied field is 1/32 s and the operative bound is 1/16 s.
        # Thus endpoint 1/32 + 2 * recorded allowance embeds it twice.
        # The recorded/applied disagreement is gross (100%), not roundoff.
        bracket = {
            "status": "passed", "endpoint_max_b_fiducial_s": 0.03125,
            "calibration_drift_allowance_s": 0.03125,
            "b_fiducial_s": 0.0625, "operative_b_fiducial_s": 0.0625,
            "acceptance": {"allowance": {
                "rule": "max(observed_drift_s,bracket_screen_s)",
                "value_s": "0.015625", "embedding_count": 1,
                "embedded_in": "b_fiducial_s",
            }},
        }
        with self.assertRaises(floor.CommonModeEstimatorRefusal) as caught:
            floor.registered_common_mode_operative_bound(bracket)
        self.assertEqual(caught.exception.reason, "common_mode_allowance_application_invalid")

    def test_transport_gate_uses_largest_nonfirst_cell(self):
        """Transport composition takes the worst gate, regardless of order. Kills M00378."""
        small = {"floor_abs_j": 2.0, "floor_cmp_j": 4.0, "floor_gate_j": 4.0,
                 "source_regime": make_regime()}
        large = {"floor_abs_j": 8.0, "floor_cmp_j": 1.0, "floor_gate_j": 8.0,
                 "source_regime": make_regime()}
        for cells in ([small, large], [large, small]):
            # Exact binary integers: the largest source gate is 8 J.
            self.assertEqual(floor.compose_transport_group(cells)["composed_floor_gate_j"], 8.0)

    def test_nine_member_residual_corner_floor(self):
        """One uncertain member moves its residual by eight ninths of its width. Kills M00860."""
        estimate = floor.absolute_false_effect_floor(
            [18.0] + [9.0] * 8, admissible_half_widths_j=[0.5] + [0.0] * 8,
        )
        # The extreme corner is [18.5,9,...,9]: mean=90.5/9,
        # largest residual=18.5-90.5/9=76/9. The prediction is smaller:
        # t_8 * (9.5/3) * sqrt(10/9) < 76/9. The n=9 guard is sqrt(9/8).
        expected = (76.0 / 9.0) * math.sqrt(9.0 / 8.0)
        # Bar: 1e-6 relative (COMMON fallback; no printed half-width).
        # Mutant adds sqrt(9/8)/9 = 0.11785 J, over 13,000 bars.
        self.assertAlmostEqual(estimate.corner_widened_guarded_floor_j,
                               expected, delta=expected * 1e-6)

    def test_exactly_sixteen_nonzero_widths_are_admitted(self):
        """The exact-corner cap admits sixteen uncertain members. Kills M00074."""
        estimate = floor.absolute_false_effect_floor(
            [100.0] * 16, admissible_half_widths_j=[0.5] * 16,
        )
        self.assertEqual(estimate.n, 16)
        self.assertIsNotNone(estimate.guarded_floor_j)

    def test_negative_mean_zero_width_corner_helper(self):
        """The helper includes the magnitude of a negative mean. Kills M00589.

        No public floor can change: comparative_false_effect_floor separately
        computes the correct point floor and takes its maximum with this
        helper. With zero widths these floors coincide, masking this mutant.
        """
        # Mean=-3, sample variance=10/4=2.5; t_4=2.776 and the prediction
        # includes |mean|, giving 3 + 2.776*sqrt(3), which exceeds max|x|=5.
        expected = 3.0 + 2.776 * math.sqrt(3.0)
        actual = floor._corner_maximized_unguarded_floor(
            [-5.0, -3.0, -2.0, -1.0, -4.0], [0.0] * 5, kind="comparative",
        )
        # Bar: 1e-6 relative (COMMON fallback; no printed half-width).
        # Mutant returns 5 J, a loss of 2.808 J (>350,000 bars).
        self.assertAlmostEqual(actual, expected, delta=expected * 1e-6)


class FloorWireTests(unittest.TestCase):
    def test_one_is_a_positive_member_count_on_the_pinset_wire(self):
        """A one-member count is schema-valid on the pinset wire. Kills M00684."""
        # Counts describe their own source sets, independently of the floor
        # sample size. Exercise the public reader's closed-schema path.
        pinset = json.loads(MINT1_PINSET_PATH.read_bytes())
        for component in ("absolute", "comparative"):
            for field in ("evaluation_basis_members", "extraction_spec_members", "expected_n"):
                pinset[component][field] = 1
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = write_pinset(Path(tmp), pinset)
            self.assertEqual(floor.validate_floor_artifact(
                make_artifact(), pinset_path=path, expected_pinset_sha256=digest,
            ), [])

    def test_config_projection_must_match_the_registered_family(self):
        """Matching config-set provenance passes and a mismatch refuses. Kills M00443."""
        artifact = make_artifact([make_cell("synthetic")])
        provenance = artifact["provenance"]
        plan = provenance["calibration_plan"]
        identity = (provenance["mint_tool_version"], plan["plan_id"], plan["sha256"])
        expected = copy.deepcopy(provenance.get("producer_config_sets", []))
        projection = SimpleNamespace(
            family_identities={identity}, config_sets_by_identity={identity: expected},
            evidence_root_ids=frozenset({"a10", "window_c"}),
        )
        with patch.object(floor, "_repository_floor_mint_pinsets", return_value=([projection], None)):
            self.assertEqual(floor.validate_floor_artifact(artifact), [])
            attacked = copy.deepcopy(artifact)
            attacked["provenance"]["producer_config_sets"] = [{"synthetic_mismatch": True}]
            errors = floor.validate_floor_artifact(attacked)
        self.assertIn(
            "artifact.pinset: producer config-set provenance does not match registered per-cell pins",
            errors,
        )
