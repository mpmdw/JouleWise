import copy
import hashlib
import json
import unittest

from joulewise.analysis_engine.artifact import (
    calculate_claim_verdicts_id,
    render_claim_verdicts,
)
from joulewise.claim_side_bound import (
    ClaimSideBoundError,
    calculate_claim_side_bound_id,
    finalize_claim_side_bound,
    load_claim_side_bound,
    render_claim_side_bound,
    validate_claim_side_bound,
)
from tests.test_analysis_claims import minimal_artifact


def _claim_bytes_with_named_bound(value_j=0.25):
    artifact = minimal_artifact()
    contrast = artifact["contrasts"][0]
    contrast["deterministic_bounds"]["terms"] = [
        {"name": "E_clock_anchor_shift_bound_j", "bound": value_j}
    ]
    contrast["deterministic_bounds"]["total"] = value_j
    estimate = contrast["estimator"]["estimate"]
    contrast["deterministic_bounds"]["decision_interval"] = {
        "lower": estimate - value_j,
        "upper": estimate + value_j,
    }
    artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
    return render_claim_verdicts(artifact)


class ClaimSideBoundTests(unittest.TestCase):
    def test_issues_content_addressed_digest_bound_projection(self) -> None:
        claim_bytes = _claim_bytes_with_named_bound()
        sidecar = finalize_claim_side_bound(claim_bytes)

        self.assertEqual(sidecar["schema_version"], "joulewise.claim_side_bound.v1")
        self.assertEqual(
            sidecar["claim_side_bound_id"],
            "csb-63ca3cef4e194c0056d4d037c6ab792f6c3460bec6e910dac661f37210ee1f1c",
        )
        self.assertEqual(
            sidecar["claim_verdicts_sha256"],
            hashlib.sha256(claim_bytes).hexdigest(),
        )
        self.assertEqual(
            sidecar["claim_side_bound_id"],
            calculate_claim_side_bound_id(sidecar),
        )
        self.assertEqual(
            sidecar["bounds"],
            [
                {
                    "contrast_id": "ctr-test",
                    "claim_side_bound": {
                        "role": "claim_measurement_uncertainty_bound",
                        "source_term_name": "E_clock_anchor_shift_bound_j",
                        "value_j": 0.25,
                        "composition_rule": (
                            "exact_named_contrast_deterministic_term.v1"
                        ),
                        "single_count_discipline_rule_id": (
                            "attribution_floor_plus_claim_side_bound.v1"
                        ),
                    },
                }
            ],
        )
        self.assertEqual(
            validate_claim_side_bound(
                sidecar,
                claim_verdicts_bytes=claim_bytes,
            ),
            [],
        )
        self.assertEqual(
            load_claim_side_bound(
                render_claim_side_bound(sidecar),
                expected_id=sidecar["claim_side_bound_id"],
                claim_verdicts_bytes=claim_bytes,
            ),
            sidecar,
        )

    def test_missing_named_term_stays_unissued_without_default(self) -> None:
        claim_bytes = render_claim_verdicts(minimal_artifact())
        sidecar = finalize_claim_side_bound(claim_bytes)
        self.assertEqual(sidecar["bounds"], [])
        self.assertEqual(
            validate_claim_side_bound(sidecar, claim_verdicts_bytes=claim_bytes),
            [],
        )

    def test_reauthenticated_semantic_and_digest_attacks_are_refused(self) -> None:
        claim_bytes = _claim_bytes_with_named_bound()
        sidecar = finalize_claim_side_bound(claim_bytes)

        changed_bound = copy.deepcopy(sidecar)
        changed_bound["bounds"][0]["claim_side_bound"]["value_j"] = 0.5
        changed_bound["claim_side_bound_id"] = calculate_claim_side_bound_id(
            changed_bound
        )
        self.assertTrue(
            any(
                "exactly project" in error
                for error in validate_claim_side_bound(
                    changed_bound,
                    claim_verdicts_bytes=claim_bytes,
                )
            )
        )

        changed_claim_bytes = claim_bytes + b" "
        self.assertTrue(
            any(
                "does not match" in error
                for error in validate_claim_side_bound(
                    sidecar,
                    claim_verdicts_bytes=changed_claim_bytes,
                )
            )
        )

        duplicate_key = render_claim_side_bound(sidecar).replace(
            b'{\n  "schema_version"',
            b'{\n  "schema_version": "joulewise.claim_side_bound.v1",\n  "schema_version"',
            1,
        )
        with self.assertRaises(ClaimSideBoundError):
            load_claim_side_bound(
                duplicate_key,
                expected_id=sidecar["claim_side_bound_id"],
                claim_verdicts_bytes=claim_bytes,
            )


if __name__ == "__main__":
    unittest.main()
