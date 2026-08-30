"""Contract tests for ordered, hash-bound real-prompt profiles."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from joulewise.workload_profile import (
    WORKLOAD_PROFILE_REFUSAL_REASONS,
    WorkloadProfileError,
    calculate_prompt_set_sha256,
    load_workload_profile,
    validate_workload_profile,
)


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "configs/workloads/real_prompts_v1.json"


class WorkloadProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

    def reasons(self, value: object) -> set[str]:
        refusals = validate_workload_profile(value)
        self.assertTrue(
            all(row.reason in WORKLOAD_PROFILE_REFUSAL_REASONS for row in refusals)
        )
        return {row.reason for row in refusals}

    def test_real_profile_loads_and_binds_ordered_set(self) -> None:
        profile = load_workload_profile(PROFILE_PATH)
        self.assertEqual(profile.profile_id, "real_prompts_v1")
        self.assertEqual(len(profile.prompts), 8)
        self.assertEqual(
            profile.prompt_set_sha256,
            calculate_prompt_set_sha256(profile.prompts),
        )
        self.assertTrue(all(prompt["text"].endswith(".") for prompt in profile.prompts))

    def test_text_mutation_is_refused(self) -> None:
        candidate = copy.deepcopy(self.profile)
        candidate["prompts"][0]["text"] += " Changed."
        self.assertIn(
            "workload_profile_text_sha256_mismatch", self.reasons(candidate)
        )

    def test_order_mutation_is_refused_by_set_digest(self) -> None:
        candidate = copy.deepcopy(self.profile)
        candidate["prompts"][0], candidate["prompts"][1] = (
            candidate["prompts"][1],
            candidate["prompts"][0],
        )
        self.assertIn(
            "workload_profile_set_sha256_mismatch", self.reasons(candidate)
        )

    def test_duplicate_id_and_unknown_field_are_closed_refusals(self) -> None:
        duplicate = copy.deepcopy(self.profile)
        duplicate["prompts"][1]["prompt_id"] = duplicate["prompts"][0]["prompt_id"]
        self.assertIn(
            "workload_profile_duplicate_prompt_id", self.reasons(duplicate)
        )

        unknown = copy.deepcopy(self.profile)
        unknown["prompts"][0]["topic"] = "science"
        self.assertIn("workload_profile_unknown_field", self.reasons(unknown))

        top_unknown = copy.deepcopy(self.profile)
        top_unknown["notes"] = "not in schema"
        self.assertIn("workload_profile_unknown_field", self.reasons(top_unknown))

        missing = copy.deepcopy(self.profile)
        del missing["prompts"][0]["text_utf8_sha256"]
        self.assertIn("workload_profile_missing_field", self.reasons(missing))

    def test_loaded_profile_is_deterministic_and_immutable(self) -> None:
        first = load_workload_profile(PROFILE_PATH)
        second = load_workload_profile(PROFILE_PATH)
        self.assertEqual(first, second)
        with self.assertRaises(TypeError):
            first.prompts[0]["text"] = "mutated"

    def test_loader_raises_structured_json_refusal(self) -> None:
        with tempfile.TemporaryDirectory(prefix="workload-profile-") as temporary:
            path = Path(temporary) / "profile.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(WorkloadProfileError) as caught:
                load_workload_profile(path)
        self.assertEqual(
            caught.exception.refusals[0].reason,
            "workload_profile_json_invalid",
        )

    def test_loader_refuses_duplicate_keys_nonfinite_json_unicode_and_io(self) -> None:
        with tempfile.TemporaryDirectory(prefix="workload-profile-") as temporary:
            root = Path(temporary)
            duplicate = root / "duplicate.json"
            duplicate.write_text('{"profile_id":"a","profile_id":"b"}')
            with self.assertRaises(WorkloadProfileError) as caught:
                load_workload_profile(duplicate)
            self.assertEqual(
                caught.exception.refusals[0].reason,
                "workload_profile_duplicate_json_key",
            )

            nonfinite = root / "nonfinite.json"
            nonfinite.write_text('{"x":Infinity}')
            with self.assertRaises(WorkloadProfileError) as caught:
                load_workload_profile(nonfinite)
            self.assertEqual(
                caught.exception.refusals[0].reason,
                "workload_profile_json_invalid",
            )

            invalid_utf8 = root / "invalid-utf8.json"
            invalid_utf8.write_bytes(b"\xff")
            with self.assertRaises(WorkloadProfileError) as caught:
                load_workload_profile(invalid_utf8)
            self.assertEqual(
                caught.exception.refusals[0].reason,
                "workload_profile_json_invalid",
            )

            with self.assertRaises(WorkloadProfileError) as caught:
                load_workload_profile(root / "missing.json")
            self.assertEqual(
                caught.exception.refusals[0].reason,
                "workload_profile_io_error",
            )


if __name__ == "__main__":
    unittest.main()
