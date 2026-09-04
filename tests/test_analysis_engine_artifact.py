import copy
import unittest

from joulewise.analysis_engine.artifact import (
    SCHEMA_VERSION,
    calculate_claim_verdicts_id,
    validate_claim_verdicts,
    validate_claim_verdicts_for_claim_index,
)
from tests.test_analysis_claims import minimal_artifact
from tests.test_analysis_integration import _v3_fixture_artifact


class ClaimVerdictsV1ClosureTests(unittest.TestCase):
    def test_v1_remains_closed_and_valid(self) -> None:
        artifact = minimal_artifact()
        self.assertEqual(artifact["schema_version"], SCHEMA_VERSION)
        self.assertEqual(validate_claim_verdicts(artifact), [])
        self.assertEqual(validate_claim_verdicts_for_claim_index(artifact), [])

        attacked = copy.deepcopy(artifact)
        attacked["contrasts"][0]["claim_side_bound"] = {}
        attacked["claim_verdicts_id"] = calculate_claim_verdicts_id(attacked)
        self.assertTrue(
            any(
                "claim_side_bound" in error
                for error in validate_claim_verdicts(attacked)
            )
        )

    def test_producer_still_emits_closed_v1(self) -> None:
        artifact = _v3_fixture_artifact()
        self.assertEqual(artifact["schema_version"], SCHEMA_VERSION)
        self.assertEqual(validate_claim_verdicts(artifact), [])
        self.assertEqual(validate_claim_verdicts_for_claim_index(artifact), [])
        self.assertTrue(
            all("claim_side_bound" not in row for row in artifact["contrasts"])
        )


if __name__ == "__main__":
    unittest.main()
