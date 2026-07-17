from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from joulewise.analysis_engine.registry import normalize_technical_invalid_reason
from joulewise.output_identity import (
    DISPOSITIONS,
    MISSING_EVIDENCE_REASONS,
    OutputIdentityError,
    build_output_identity_report,
    calculate_report_id,
    render_output_identity_report,
    validate_output_identity_report,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "axi_valid_burst"
GOLDENS = ROOT / "tests" / "goldens"
MANIFEST_ID = "am-" + "a" * 64


def load_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def request_rows(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in (path / "outputs" / "requests.jsonl").read_text().splitlines()
        if line
    ]


def write_request_rows(path: Path, rows: list[dict]) -> None:
    (path / "outputs" / "requests.jsonl").write_text(
        "".join(json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n" for row in rows)
    )


def expanded_golden(name: str) -> dict:
    if name == "exact":
        return load_json(GOLDENS / "output_identity_exact.json")
    value = load_json(GOLDENS / "output_identity_exact.json")
    patch = load_json(GOLDENS / f"output_identity_{name}.patch.json")
    for pointer, replacement in patch["replacements"].items():
        target = value
        parts = pointer.removeprefix("/").split("/")
        for part in parts[:-1]:
            target = target[int(part)] if isinstance(target, list) else target[part]
        if isinstance(target, list):
            target[int(parts[-1])] = replacement
        else:
            target[parts[-1]] = replacement
    return value


class AxiOutputIdentityTests(unittest.TestCase):
    @staticmethod
    def strict_valid(_path: Path, _strict: bool) -> list[str]:
        return []

    def copied(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temporary = tempfile.TemporaryDirectory()
        path = Path(temporary.name) / "bundle"
        shutil.copytree(FIXTURE, path)
        return temporary, path

    def report(self, off: Path | None, on: Path | None, validator=None) -> dict:
        return build_output_identity_report(
            manifest_id=MANIFEST_ID,
            pair_id="pair-000",
            spec_off_bundle=off,
            spec_on_bundle=on,
            strict_validator=validator or self.strict_valid,
        )

    def mutate_request(self, path: Path, **changes) -> None:
        rows = request_rows(path)
        rows[0].update(changes)
        write_request_rows(path, rows)

    def test_all_four_state_reports_match_hand_authored_canonical_goldens(self) -> None:
        cases = {
            "exact": {},
            "text_divergent": {
                "emitted_token_ids_sha256": "d" * 64,
                "output_token_count": 4,
            },
            "output_divergent": {
                "response_text": "different",
                "response_text_sha256": "e" * 64,
            },
            "unassessable": {"emitted_token_ids_sha256": None},
        }
        for name, mutation in cases.items():
            with self.subTest(state=name):
                if not mutation:
                    on = FIXTURE
                    temporary = None
                else:
                    temporary, on = self.copied()
                    self.mutate_request(on, **mutation)
                try:
                    report = self.report(FIXTURE, on)
                    expected = expanded_golden(name)
                    self.assertEqual(report, expected)
                    self.assertEqual(
                        render_output_identity_report(report),
                        (json.dumps(expected, indent=2, sort_keys=True) + "\n").encode(),
                    )
                    self.assertEqual(
                        report["claim_disposition"],
                        DISPOSITIONS[report["overall_state"]],
                    )
                finally:
                    if temporary is not None:
                        temporary.cleanup()

    def test_equal_text_different_tokens_is_token_divergent_for_equal_or_unequal_counts(self) -> None:
        for count in (3, 4):
            with self.subTest(count=count):
                temporary, on = self.copied()
                try:
                    self.mutate_request(
                        on,
                        emitted_token_ids_sha256="d" * 64,
                        output_token_count=count,
                    )
                    request = self.report(FIXTURE, on)["requests"][0]
                    self.assertEqual(request["state"], "text_match_token_divergent")
                    self.assertEqual(request["output_token_count_equal"], count == 3)
                finally:
                    temporary.cleanup()

    def test_text_and_stop_divergence_are_output_divergent(self) -> None:
        for mutation, reason in (
            ({"response_text_sha256": "d" * 64}, "response_text_differs"),
            ({"stop_reason": "natural_eos"}, "stop_reason_differs"),
        ):
            with self.subTest(reason=reason):
                temporary, on = self.copied()
                try:
                    self.mutate_request(on, **mutation)
                    request = self.report(FIXTURE, on)["requests"][0]
                    self.assertEqual(request["state"], "output_divergent")
                    self.assertIn(reason, request["reason_codes"])
                finally:
                    temporary.cleanup()

    def test_missing_tokens_with_equal_text_is_unassessable(self) -> None:
        temporary, on = self.copied()
        self.addCleanup(temporary.cleanup)
        self.mutate_request(on, emitted_token_ids_sha256=None)
        request = self.report(FIXTURE, on)["requests"][0]
        self.assertEqual(request["state"], "unassessable")
        self.assertEqual(
            request["missing_evidence_reasons"],
            ["spec_on_token_ids_unavailable"],
        )

    def test_target_tokenizer_exact_mismatch_and_missing_are_derived_without_boolean(self) -> None:
        exact = self.report(FIXTURE, FIXTURE)
        self.assertEqual(exact["target_tokenizer_comparison"], "exact_match")
        self.assertNotIn("target_tokenizer_equal", exact)
        for replacement, expected, reason in (
            ("other-revision", "mismatch", "target_tokenizer_identity_mismatch"),
            (None, "unassessable", "target_tokenizer_identity_unavailable"),
        ):
            with self.subTest(expected=expected):
                temporary, on = self.copied()
                try:
                    metadata = load_json(on / "metadata.json")
                    if replacement is None:
                        metadata["runtime"]["target_tokenizer_identity"] = None
                    else:
                        metadata["runtime"]["target_tokenizer_identity"]["revision"] = replacement
                    write_json(on / "metadata.json", metadata)
                    report = self.report(FIXTURE, on)
                    self.assertEqual(report["target_tokenizer_comparison"], expected)
                    self.assertEqual(report["overall_state"], "unassessable")
                    self.assertIn(reason, report["requests"][0]["reason_codes"])
                finally:
                    temporary.cleanup()

    def test_unexpected_config_difference_overrides_equal_output(self) -> None:
        temporary, on = self.copied()
        self.addCleanup(temporary.cleanup)
        config = load_json(on / "config.json")
        config["model"]["name"] = "unexpected-other-target"
        write_json(on / "config.json", config)
        report = self.report(FIXTURE, on)
        self.assertEqual(report["overall_state"], "unassessable")
        self.assertEqual(
            report["config_gate"]["unexpected_difference_pointers"],
            ["/model/name"],
        )
        self.assertIn("unexpected_config_difference", report["requests"][0]["reason_codes"])

    def test_missing_or_malformed_bundle_artifacts_still_form_valid_unassessable_reports(self) -> None:
        missing = self.report(None, None)
        validate_output_identity_report(missing)
        self.assertEqual(missing["overall_state"], "unassessable")
        self.assertEqual(missing["requests"], [])
        self.assertEqual(
            missing["spec_off_bundle"]["missing_evidence_reasons"],
            sorted(
                {
                    "config_sha256_unavailable",
                    "request_tokens_artifact_unavailable",
                    "requests_artifact_unavailable",
                    "run_id_unavailable",
                    "strict_validation_report_unavailable",
                    "summary_artifact_unavailable",
                    "target_tokenizer_identity_unavailable",
                }
            ),
        )
        self.assertTrue(
            set(missing["spec_off_bundle"]["missing_evidence_reasons"])
            <= set(MISSING_EVIDENCE_REASONS)
        )

        temporary, malformed = self.copied()
        self.addCleanup(temporary.cleanup)
        (malformed / "outputs" / "requests.jsonl").write_text("not-json\n")
        report = self.report(FIXTURE, malformed)
        validate_output_identity_report(report)
        self.assertEqual(report["overall_state"], "unassessable")
        self.assertIn(
            "requests_artifact_unavailable",
            report["spec_on_bundle"]["missing_evidence_reasons"],
        )

    def test_canonical_arrays_reject_duplicates_or_unsorted_values_before_hashing(self) -> None:
        report = self.report(FIXTURE, FIXTURE)
        cases = []
        unsorted_reasons = copy.deepcopy(report)
        unsorted_reasons["requests"][0]["reason_codes"] = [
            "token_ids_unavailable",
            "response_text_unavailable",
        ]
        cases.append(unsorted_reasons)
        duplicate_missing = copy.deepcopy(report)
        duplicate_missing["requests"][0]["missing_evidence_reasons"] = [
            "spec_on_token_ids_unavailable",
            "spec_on_token_ids_unavailable",
        ]
        duplicate_missing["requests"][0]["spec_on_token_ids_sha256"] = None
        cases.append(duplicate_missing)
        duplicate_pointer = copy.deepcopy(report)
        duplicate_pointer["config_gate"]["unexpected_difference_pointers"] = [
            "/model/name", "/model/name"
        ]
        cases.append(duplicate_pointer)
        for changed in cases:
            changed["report_id"] = calculate_report_id(changed)
            with self.assertRaisesRegex(OutputIdentityError, "unique|sorted"):
                validate_output_identity_report(changed)

    def test_doctored_well_formed_assertions_fail_mechanical_rederivation(self) -> None:
        report = self.report(FIXTURE, FIXTURE)
        mutations = (
            lambda value: value.__setitem__(
                "target_tokenizer_comparison", "mismatch"
            ),
            lambda value: value["requests"][0].__setitem__(
                "state", "output_divergent"
            ),
            lambda value: value["requests"][0].__setitem__(
                "reason_codes", ["token_ids_differ"]
            ),
            lambda value: value.__setitem__(
                "overall_state", "output_divergent"
            ),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                changed = copy.deepcopy(report)
                mutate(changed)
                if changed["overall_state"] == "output_divergent":
                    changed["claim_disposition"] = "descriptive_only"
                changed["report_id"] = calculate_report_id(changed)
                with self.assertRaisesRegex(
                    OutputIdentityError, "re-derived"
                ):
                    validate_output_identity_report(changed)

    def test_config_gate_and_bundle_references_are_rederived(self) -> None:
        report = self.report(FIXTURE, FIXTURE)
        changed_gate = copy.deepcopy(report)
        changed_gate["config_gate"]["spec_on_projection_sha256"] = "d" * 64
        changed_gate["report_id"] = calculate_report_id(changed_gate)
        with self.assertRaisesRegex(OutputIdentityError, "config gate"):
            validate_output_identity_report(changed_gate)

        changed_bundle = copy.deepcopy(report)
        changed_bundle["spec_off_bundle"]["config_sha256"] = "d" * 64
        changed_bundle["report_id"] = calculate_report_id(changed_bundle)
        with self.assertRaisesRegex(OutputIdentityError, "underlying bundle"):
            validate_output_identity_report(
                changed_bundle,
                spec_off_bundle=FIXTURE,
                spec_on_bundle=FIXTURE,
                strict_validator=self.strict_valid,
            )

    def test_roster_mismatch_is_not_hidden_by_runtime_request_ids(self) -> None:
        temporary, on = self.copied()
        self.addCleanup(temporary.cleanup)
        roster = load_json(on / "request_roster.json")
        roster["requests"][0]["request_input_id"] = "other-input"
        write_json(on / "request_roster.json", roster)
        report = self.report(FIXTURE, on)
        self.assertEqual(report["overall_state"], "unassessable")
        self.assertIn("request_roster_mismatch", report["requests"][0]["reason_codes"])

    def test_worst_state_rollup_across_requests(self) -> None:
        off_tmp, off = self.copied()
        on_tmp, on = self.copied()
        self.addCleanup(off_tmp.cleanup)
        self.addCleanup(on_tmp.cleanup)
        for path in (off, on):
            roster = load_json(path / "request_roster.json")
            second_descriptor = copy.deepcopy(roster["requests"][0])
            second_descriptor.update(request_ordinal=1, request_input_id="prompt-001")
            roster["requests"].append(second_descriptor)
            write_json(path / "request_roster.json", roster)
            rows = request_rows(path)
            second = copy.deepcopy(rows[0])
            second.update(request_ordinal=1, request_input_id="prompt-001", request_id="request-001")
            rows.append(second)
            write_request_rows(path, rows)
        on_rows = request_rows(on)
        on_rows[0]["response_text_sha256"] = "d" * 64
        on_rows[1]["emitted_token_ids_sha256"] = "e" * 64
        write_request_rows(on, on_rows)
        report = self.report(off, on)
        self.assertEqual(
            [row["state"] for row in report["requests"]],
            ["output_divergent", "text_match_token_divergent"],
        )
        self.assertEqual(report["overall_state"], "output_divergent")
        self.assertEqual(report["claim_disposition"], "descriptive_only")

    def test_unknown_attempt_reason_is_normalized_to_eligible_null(self) -> None:
        self.assertIsNone(normalize_technical_invalid_reason("output_divergent"))
        self.assertIsNone(normalize_technical_invalid_reason("favorable_later_retry"))
        self.assertEqual(
            normalize_technical_invalid_reason("strict_bundle_invalid"),
            "strict_bundle_invalid",
        )


if __name__ == "__main__":
    unittest.main()
