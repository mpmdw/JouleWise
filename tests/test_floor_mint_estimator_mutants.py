"""Synthetic mint-consumer guards that need unequal allowances and bounds."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from joulewise import detection_floor, floor_mint_estimator as estimator
from joulewise.authentication_io import V2AuthenticationReadSession
from tests.test_floor_mint_estimator import (
    ACCEPTANCE, ACCEPTANCE_SHA256, ALLOWANCE, calibration_basis,
    recompute_kwargs, registered_component,
)


class MintConsumerTests(unittest.TestCase):
    def test_projection_cannot_substitute_screen_for_larger_drift(self):
        """A screen-only allowance cannot understate observed drift. Kills M01780."""
        projection = {**ALLOWANCE, "observed_drift_s": "0.01175",
                      "applied_allowance_s": "0.010818"}
        # Drift remains below this generation's 0.012093... s budget.
        # The missing 0.000932 s (>8%) is gross, not a tolerance-boundary probe.
        with self.assertRaisesRegex(ValueError, r"does not implement max\(observed_drift_s"):
            estimator.selection_from_authenticated_spec(
                {"calibration_basis": calibration_basis()},
                calibration_acceptance=ACCEPTANCE,
                calibration_acceptance_sha256=ACCEPTANCE_SHA256,
                calibration_allowance_projection=projection,
                declared_calibration_scope="production_window",
            )

    def test_inconsistent_authenticated_session_bound_refuses(self):
        """A grossly inconsistent session bound refuses. Kills M01801 and M01803."""
        bracket = {
            "status": "passed", "endpoint_max_b_fiducial_s": 0.02,
            "calibration_drift_allowance_s": 0.010818,
            "b_fiducial_s": 0.030818, "operative_b_fiducial_s": 0.030818,
            "acceptance": {"allowance": {
                "rule": "max(observed_drift_s,bracket_screen_s)",
                "value_s": "0.010818", "embedding_count": 1,
                "embedded_in": "b_fiducial_s",
            }},
        }
        # 0.1 s differs by 0.069182 s (>200%); nowhere near the tolerance.
        session = SimpleNamespace(ready=True, refusal_reasons=(),
                                  calibration_bracket=bracket,
                                  operative_fiducial_bound_s=0.1)
        with (
            V2AuthenticationReadSession(),
            patch.object(estimator, "_assert_common_mode_contract", return_value=None),
            patch.object(estimator, "_authenticated_common_mode_session", return_value=session),
            patch.object(estimator.floor_extraction, "_common_mode_block_inputs_from_evidence",
                         side_effect=lambda members, **kw: tuple(m.position for m in members)),
            patch.object(estimator.floor_extraction, "_common_mode_floor_from_block_inputs",
                         side_effect=lambda deltas, inputs, **kw:
                         detection_floor.comparative_false_effect_floor(
                             deltas, admissible_half_widths_j=[0.125] * len(deltas))),
        ):
            with self.assertRaisesRegex(
                ValueError, "authenticated common-mode once-widened bound is inconsistent",
            ):
                estimator.recompute_comparative_estimate(**recompute_kwargs(registered_component()))
