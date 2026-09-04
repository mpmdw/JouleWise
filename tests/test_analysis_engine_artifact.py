import copy
import unittest

from joulewise.analysis_engine.artifact import (
    SCHEMA_VERSION_V1,
    SCHEMA_VERSION_V2,
    calculate_claim_verdicts_id,
    validate_claim_verdicts,
    validate_claim_verdicts_for_claim_index,
)
from tests.test_analysis_claims import minimal_artifact
from tests.test_analysis_integration import _v3_fixture_artifact


class ClaimVerdictsV2Tests(unittest.TestCase):
    def test_v1_remains_closed_and_valid(self) -> None:
        artifact = minimal_artifact()
        self.assertEqual(artifact["schema_version"], SCHEMA_VERSION_V1)
        self.assertEqual(validate_claim_verdicts(artifact), [])
        self.assertEqual(validate_claim_verdicts_for_claim_index(artifact), [])

        attacked = copy.deepcopy(artifact)
        attacked["contrasts"][0]["claim_side_bound"] = {}
        attacked["claim_verdicts_id"] = calculate_claim_verdicts_id(attacked)
        self.assertTrue(
            any("claim_side_bound" in error for error in validate_claim_verdicts(attacked))
        )

    def test_producer_emits_closed_v2_claim_side_bound(self) -> None:
        artifact = _v3_fixture_artifact()
        self.assertEqual(artifact["schema_version"], SCHEMA_VERSION_V2)
        self.assertEqual(validate_claim_verdicts(artifact), [])
        self.assertEqual(validate_claim_verdicts_for_claim_index(artifact), [])

        contrast = artifact["contrasts"][0]
        expected = {
            "role": "claim_measurement_uncertainty_bound",
            "source_term_name": "E_clock_anchor_shift_bound_j",
            "value_j": 0.2,
            "composition_rule": "exact_named_contrast_deterministic_term.v1",
            "single_count_discipline_rule_id": (
                "attribution_floor_plus_claim_side_bound.v1"
            ),
        }
        self.assertEqual(contrast["claim_side_bound"], expected)

        mutations = {
            "missing": lambda row: row.pop("claim_side_bound"),
            "extra": lambda row: row["claim_side_bound"].__setitem__("extra", True),
            "role": lambda row: row["claim_side_bound"].__setitem__("role", "other"),
            "source": lambda row: row["claim_side_bound"].__setitem__(
                "source_term_name", "E_interpolation_joint_edge_bound_j"
            ),
            "value": lambda row: row["claim_side_bound"].__setitem__("value_j", 0.3),
            "composition": lambda row: row["claim_side_bound"].__setitem__(
                "composition_rule", "other"
            ),
            "single_count": lambda row: row["claim_side_bound"].__setitem__(
                "single_count_discipline_rule_id", "other"
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                attacked = copy.deepcopy(artifact)
                mutate(attacked["contrasts"][0])
                attacked["claim_verdicts_id"] = calculate_claim_verdicts_id(attacked)
                self.assertTrue(validate_claim_verdicts(attacked))


if __name__ == "__main__":
    unittest.main()
