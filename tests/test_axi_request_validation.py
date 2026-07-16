from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from joulewise.axi_decode_config import (
    AxiSchemaError,
    SpeculationPolicy,
    validate_v2_event,
)
from joulewise.bundle_read import (
    AXI_VALIDATOR_REASON_CODES,
    BundleReader,
    _axi_phase_pairs,
    axi_v2_validation_problems,
)
from joulewise.cli import validate_bundle


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "axi_valid_burst"
GOLDEN = ROOT / "tests" / "goldens"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def _axi_codes(path: Path) -> set[str]:
    return {
        problem.split(":", 2)[1]
        for problem in axi_v2_validation_problems(BundleReader(path))
        if problem.startswith("axi:")
    }


class AxiRequestValidationTests(unittest.TestCase):
    def copied_fixture(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temporary = tempfile.TemporaryDirectory()
        path = Path(temporary.name) / "bundle"
        shutil.copytree(FIXTURE, path)
        return temporary, path

    def assert_fixture_code(self, mutate, expected: str) -> None:
        temporary, path = self.copied_fixture()
        self.addCleanup(temporary.cleanup)
        mutate(path)
        self.assertIn(expected, _axi_codes(path))

    def test_hand_authored_burst_fixture_is_strict_valid(self) -> None:
        self.assertEqual(validate_bundle(FIXTURE, strict=True), [])
        self.assertEqual(axi_v2_validation_problems(BundleReader(FIXTURE)), [])
        self.assertEqual(
            hashlib.sha256((FIXTURE / "config.json").read_bytes()).hexdigest(),
            "79e34a9adef077ee3f82b4aed16bc551b1ad565fa285da44831917eba11ca48d",
        )

    def test_interleaved_equal_timestamps_pair_by_request_local_key(self) -> None:
        events = [
            {"event_type": "phase_start", "phase": "decode", "timestamp_s": 1.0,
             "metadata": {"source_identity": "meter-0", "request_id": "request-a", "request_phase_ordinal": 0}},
            {"event_type": "phase_start", "phase": "decode", "timestamp_s": 1.0,
             "metadata": {"source_identity": "meter-0", "request_id": "request-b", "request_phase_ordinal": 0}},
            {"event_type": "phase_end", "phase": "decode", "timestamp_s": 1.8,
             "metadata": {"source_identity": "meter-0", "request_id": "request-b", "request_phase_ordinal": 0}},
            {"event_type": "phase_end", "phase": "decode", "timestamp_s": 2.0,
             "metadata": {"source_identity": "meter-0", "request_id": "request-a", "request_phase_ordinal": 0}},
        ]
        pairs, problems = _axi_phase_pairs(events)
        self.assertEqual(problems, [])
        self.assertEqual(len(pairs), 2)
        self.assertEqual(pairs[("meter-0", "request-a", "decode", 0)].end_s, 2.0)
        self.assertEqual(pairs[("meter-0", "request-b", "decode", 0)].end_s, 1.8)

    def test_request_boundaries_need_not_be_shared(self) -> None:
        events = [
            {"event_type": "phase_start", "phase": "prefill", "timestamp_s": 0.2,
             "metadata": {"source_identity": "meter-0", "request_id": "request-a", "request_phase_ordinal": 0}},
            {"event_type": "phase_end", "phase": "prefill", "timestamp_s": 0.7,
             "metadata": {"source_identity": "meter-0", "request_id": "request-a", "request_phase_ordinal": 0}},
            {"event_type": "phase_start", "phase": "decode", "timestamp_s": 0.9,
             "metadata": {"source_identity": "meter-0", "request_id": "request-a", "request_phase_ordinal": 1}},
            {"event_type": "phase_end", "phase": "decode", "timestamp_s": 1.9,
             "metadata": {"source_identity": "meter-0", "request_id": "request-a", "request_phase_ordinal": 1}},
            {"event_type": "phase_start", "phase": "prefill", "timestamp_s": 0.4,
             "metadata": {"source_identity": "meter-0", "request_id": "request-b", "request_phase_ordinal": 0}},
            {"event_type": "phase_end", "phase": "prefill", "timestamp_s": 1.0,
             "metadata": {"source_identity": "meter-0", "request_id": "request-b", "request_phase_ordinal": 0}},
            {"event_type": "phase_start", "phase": "decode", "timestamp_s": 1.2,
             "metadata": {"source_identity": "meter-0", "request_id": "request-b", "request_phase_ordinal": 1}},
            {"event_type": "phase_end", "phase": "decode", "timestamp_s": 2.2,
             "metadata": {"source_identity": "meter-0", "request_id": "request-b", "request_phase_ordinal": 1}},
        ]
        pairs, problems = _axi_phase_pairs(events)
        self.assertEqual(problems, [])
        self.assertEqual(len(pairs), 4)

    def test_required_nullable_event_fields_accept_null_but_not_omission(self) -> None:
        emission = _load_json(GOLDEN / "axi_decode_emission.json")
        emission["metadata"]["emitted_token_ids"] = None
        emission["metadata"]["emitted_token_ids_sha256"] = None
        emission["metadata"]["scheduler_step_id"] = None
        speculation = SpeculationPolicy.from_mapping(
            _load_json(FIXTURE / "config.json")["speculation"]
        )
        validate_v2_event(emission, speculation)
        for key in (
            "scheduler_step_id",
            "emitted_token_ids",
            "emitted_token_ids_sha256",
        ):
            with self.subTest(key=key):
                missing = copy.deepcopy(emission)
                missing["metadata"].pop(key)
                with self.assertRaisesRegex(AxiSchemaError, rf"{key}.*required|keys mismatch"):
                    validate_v2_event(missing, speculation)

        token = copy.deepcopy(emission)
        token["event_type"] = "token"
        token["metadata"] = {
            key: emission["metadata"][key]
            for key in (
                "request_id", "request_ordinal", "request_input_id",
                "request_event_ordinal", "request_roster_sha256",
                "source_identity", "batch_group_id", "scheduler_step_id",
                "decode_step_ordinal",
            )
        }
        token["metadata"].update(
            output_token_ordinal=0,
            token_id=None,
            timestamp_provenance="runtime_per_token_callback",
        )
        validate_v2_event(token, speculation)
        token["metadata"].pop("token_id")
        with self.assertRaisesRegex(AxiSchemaError, "token_id.*required|keys mismatch"):
            validate_v2_event(token, speculation)

    def test_enabled_zero_and_off_null_counter_forms(self) -> None:
        enabled = SpeculationPolicy.from_mapping(
            _load_json(FIXTURE / "config.json")["speculation"]
        )
        emission = _load_json(GOLDEN / "axi_decode_emission.json")
        emission["metadata"].update(
            emitted_count=1,
            emitted_token_ids=[10],
            emitted_token_ids_sha256=None,
            tokens_proposed=0,
            tokens_accepted=0,
            target_emitted_count=1,
        )
        validate_v2_event(emission, enabled)

        off = SpeculationPolicy.from_mapping(
            {"mode": "off", "max_proposed_tokens": None,
             "draft_model_identity": None, "native_mtp_identity": None}
        )
        emission["metadata"].update(tokens_proposed=None, tokens_accepted=None)
        validate_v2_event(emission, off)
        emission["metadata"]["tokens_proposed"] = 0
        with self.assertRaisesRegex(AxiSchemaError, "spec-off emission counter null"):
            validate_v2_event(emission, off)

    def test_cancelled_proposal_work_is_retained_in_request_rollup(self) -> None:
        temporary, path = self.copied_fixture()
        self.addCleanup(temporary.cleanup)
        events = _load_jsonl(path / "events.jsonl")
        prefix = events[:3]
        terminal = _load_json(GOLDEN / "axi_cancelled_terminal.json")
        terminal["metadata"]["request_event_ordinal"] = 2
        terminal["timestamp_s"] = 0.3
        suffix = [
            {"event_type": "sampling_stopped", "message": "measurement stopped", "metadata": {}, "phase": "measured_run", "timestamp_s": 0.4},
            {"event_type": "run_finalized", "message": "bundle finalized", "metadata": {}, "phase": "finalization", "timestamp_s": 0.4},
        ]
        _write_jsonl(path / "events.jsonl", prefix + [terminal] + suffix)
        request = _load_jsonl(path / "outputs" / "requests.jsonl")[0]
        request.update(
            acceptance_rate=0.0,
            emitted_token_ids_sha256="544ca93c6bfa8ab35f4d26ada966212e3cef9d95312dac24c3292dae82997c82",
            failure_reason="cancelled_by_fixture",
            output_token_count=0,
            response_text="",
            response_text_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            stop_reason=None,
            target_emitted_count=0,
            terminal_status="cancelled_after_proposal_before_output",
            tokens_accepted=0,
            tokens_proposed=2,
        )
        _write_jsonl(path / "outputs" / "requests.jsonl", [request])
        (path / "outputs" / "request_tokens.jsonl").write_text("")
        summary = _load_json(path / "summary_metrics.json")
        summary["status"] = "failed"
        _write_json(path / "summary_metrics.json", summary)
        self.assertEqual(axi_v2_validation_problems(BundleReader(path)), [])

        terminal["metadata"]["cancelled_proposal_counters"]["tokens_proposed"] = 0
        with self.assertRaisesRegex(AxiSchemaError, "tokens_proposed"):
            enabled = SpeculationPolicy.from_mapping(
                _load_json(FIXTURE / "config.json")["speculation"]
            )
            validate_v2_event(terminal, enabled)

    def test_failed_bundle_still_requires_terminal_for_every_admitted_request(self) -> None:
        def mutate(path: Path) -> None:
            summary = _load_json(path / "summary_metrics.json")
            summary["status"] = "failed"
            _write_json(path / "summary_metrics.json", summary)
            events = [
                row for row in _load_jsonl(path / "events.jsonl")
                if row["event_type"] != "request_terminal"
            ]
            _write_jsonl(path / "events.jsonl", events)

        self.assert_fixture_code(mutate, "request_lifecycle_incomplete")

    def test_duplicate_singleton_token_callback_is_refused(self) -> None:
        def mutate(path: Path) -> None:
            rows = _load_jsonl(path / "events.jsonl")
            token_index = next(
                index
                for index, row in enumerate(rows)
                if row["event_type"] == "token"
            )
            rows.insert(token_index + 1, copy.deepcopy(rows[token_index]))
            ordinal = 0
            for row in rows:
                metadata = row.get("metadata")
                if isinstance(metadata, dict) and metadata.get("request_id") == "request-000":
                    metadata["request_event_ordinal"] = ordinal
                    ordinal += 1
            _write_jsonl(path / "events.jsonl", rows)

        self.assert_fixture_code(mutate, "request_output_artifact_invalid")

    def test_request_work_without_admission_is_refused(self) -> None:
        def mutate(path: Path) -> None:
            rows = [
                row
                for row in _load_jsonl(path / "events.jsonl")
                if row["event_type"] != "request_admitted"
            ]
            ordinal = 0
            for row in rows:
                metadata = row.get("metadata")
                if isinstance(metadata, dict) and metadata.get("request_id") == "request-000":
                    metadata["request_event_ordinal"] = ordinal
                    ordinal += 1
            _write_jsonl(path / "events.jsonl", rows)

        self.assert_fixture_code(mutate, "request_lifecycle_incomplete")

    def test_optional_b1_compatibility_mirrors_are_compared_to_authority(self) -> None:
        temporary, path = self.copied_fixture()
        self.addCleanup(temporary.cleanup)
        request = _load_jsonl(path / "outputs" / "requests.jsonl")[0]
        tokens = _load_jsonl(path / "outputs" / "request_tokens.jsonl")
        (path / "outputs" / "response.txt").write_bytes(
            request["response_text"].encode("utf-8")
        )
        _write_jsonl(
            path / "outputs" / "tokens.jsonl",
            [
                {
                    "index": row["output_token_ordinal"],
                    "timestamp_s": row["timestamp_s"],
                    "token_id": row["token_id"],
                }
                for row in tokens
            ],
        )
        self.assertEqual(axi_v2_validation_problems(BundleReader(path)), [])

        (path / "outputs" / "response.txt").write_text(
            "doctored", encoding="utf-8"
        )
        self.assertIn("request_output_artifact_invalid", _axi_codes(path))

        (path / "outputs" / "response.txt").write_bytes(
            request["response_text"].encode("utf-8")
        )
        mirror_tokens = _load_jsonl(path / "outputs" / "tokens.jsonl")
        mirror_tokens[0]["token_id"] = 999
        _write_jsonl(path / "outputs" / "tokens.jsonl", mirror_tokens)
        self.assertIn("request_output_artifact_invalid", _axi_codes(path))

    def test_all_validator_refusal_codes_have_exact_failing_cases(self) -> None:
        expected = {
            "axi_partial_opt_in", "batch_observation_mismatch",
            "cancelled_proposal_evidence_lost", "event_global_order_invalid",
            "event_semantics_invalid", "event_source_identity_unresolved",
            "primary_source_identity_unresolved",
            "proposal_count_exceeds_configured_cap",
            "request_counter_rollup_mismatch", "request_event_ordinal_invalid",
            "request_event_outside_decode", "request_identity_mismatch",
            "request_lifecycle_incomplete", "request_output_artifact_invalid",
            "request_output_count_mismatch", "request_output_hash_mismatch",
            "request_phase_overlap", "request_phase_pairing_invalid",
            "request_roster_hash_mismatch", "request_roster_invalid",
            "target_tokenizer_artifact_hash_mismatch",
            "target_tokenizer_identity_unavailable",
        }
        self.assertEqual(AXI_VALIDATOR_REASON_CODES, expected)

        def mutate_json(path: Path, name: str, mutate) -> None:
            value = _load_json(path / name)
            mutate(value)
            _write_json(path / name, value)

        def mutate_events(path: Path, mutate) -> None:
            rows = _load_jsonl(path / "events.jsonl")
            mutate(rows)
            _write_jsonl(path / "events.jsonl", rows)

        def mutate_request_rows(path: Path, mutate) -> None:
            rows = _load_jsonl(path / "outputs" / "requests.jsonl")
            mutate(rows)
            _write_jsonl(path / "outputs" / "requests.jsonl", rows)

        def cancelled_with_output(rows: list[dict]) -> None:
            terminal = next(
                row for row in rows if row["event_type"] == "request_terminal"
            )
            terminal["metadata"].update(
                terminal_status="cancelled_after_proposal_before_output",
                stop_reason=None,
                failure_reason="cancelled_by_fixture",
                failure_message="cancelled after proposal",
                cancelled_proposal_counters={
                    "tokens_proposed": 2,
                    "tokens_accepted": 0,
                    "target_emitted_count": 0,
                    "emitted_count": 0,
                    "acceptance_rate": 0.0,
                },
            )

        def move_emission_outside_decode(rows: list[dict]) -> None:
            next(
                row for row in rows if row["event_type"] == "decode_emission"
            )["timestamp_s"] = 2.05

        def cancelled_case(path: Path) -> None:
            mutate_events(path, cancelled_with_output)
            mutate_request_rows(
                path,
                lambda rows: rows[0].update(
                    terminal_status="cancelled_after_proposal_before_output",
                    stop_reason=None,
                    failure_reason="cancelled_by_fixture",
                ),
            )

        cases = {
            "axi_partial_opt_in": lambda p: mutate_json(p, "summary_metrics.json", lambda v: v["summary_provenance"].__setitem__("reducer_version", "0.5.0")),
            "batch_observation_mismatch": lambda p: mutate_json(p, "metadata.json", lambda v: v["batch"].__setitem__("realized_batch_size", 0)),
            "cancelled_proposal_evidence_lost": cancelled_case,
            "event_global_order_invalid": lambda p: mutate_events(p, lambda rows: rows[-1].__setitem__("timestamp_s", -1.0)),
            "event_semantics_invalid": lambda p: mutate_events(p, lambda rows: next(row for row in rows if row["event_type"] == "decode_emission")["metadata"].pop("emitted_token_ids_sha256")),
            "event_source_identity_unresolved": lambda p: mutate_events(p, lambda rows: next(row for row in rows if row["event_type"] == "decode_emission")["metadata"].__setitem__("source_identity", "missing:source")),
            "primary_source_identity_unresolved": lambda p: mutate_json(p, "metadata.json", lambda v: v["runtime"].__setitem__("primary_source_identity", "missing:source")),
            "proposal_count_exceeds_configured_cap": lambda p: mutate_events(p, lambda rows: next(row for row in rows if row["event_type"] == "decode_emission")["metadata"].__setitem__("tokens_proposed", 5)),
            "request_counter_rollup_mismatch": lambda p: mutate_request_rows(p, lambda rows: rows[0].update(tokens_proposed=3, acceptance_rate=2 / 3)),
            "request_event_ordinal_invalid": lambda p: mutate_events(p, lambda rows: next(row for row in rows if row["event_type"] == "decode_emission")["metadata"].__setitem__("request_event_ordinal", 6)),
            "request_event_outside_decode": lambda p: mutate_events(p, move_emission_outside_decode),
            "request_identity_mismatch": lambda p: mutate_events(p, lambda rows: next(row for row in rows if row["event_type"] == "decode_emission")["metadata"].__setitem__("request_input_id", "wrong-input")),
            "request_lifecycle_incomplete": lambda p: mutate_events(p, lambda rows: rows.remove(next(row for row in rows if row["event_type"] == "request_terminal"))),
            "request_output_artifact_invalid": lambda p: mutate_request_rows(p, lambda rows: rows[0].pop("response_text_sha256")),
            "request_output_count_mismatch": lambda p: mutate_events(p, lambda rows: next(row for row in rows if row["event_type"] == "request_terminal")["metadata"].__setitem__("realized_output_token_count", 2)),
            "request_output_hash_mismatch": lambda p: mutate_request_rows(p, lambda rows: rows[0].__setitem__("emitted_token_ids_sha256", "d" * 64)),
            "request_roster_hash_mismatch": lambda p: mutate_json(p, "request_roster.json", lambda v: v["requests"][0].__setitem__("request_input_id", "changed-input")),
            "request_roster_invalid": lambda p: mutate_json(p, "request_roster.json", lambda v: v.__setitem__("extra", None)),
            "target_tokenizer_artifact_hash_mismatch": lambda p: mutate_json(p, "metadata.json", lambda v: v["runtime"]["target_tokenizer_identity"].__setitem__("tokenizer_artifact_sha256", "d" * 64)),
            "target_tokenizer_identity_unavailable": lambda p: mutate_json(p, "metadata.json", lambda v: v["runtime"].__setitem__("target_tokenizer_identity", None)),
        }
        observed: set[str] = set()
        for expected_code, mutate in cases.items():
            with self.subTest(reason_code=expected_code):
                temporary, path = self.copied_fixture()
                try:
                    mutate(path)
                    codes = _axi_codes(path)
                    self.assertIn(expected_code, codes)
                    observed.add(expected_code)
                finally:
                    temporary.cleanup()

        overlap_events = [
            {"event_type": "phase_start", "phase": "prefill", "timestamp_s": 0.0, "metadata": {"source_identity": "s", "request_id": "r", "request_phase_ordinal": 0}},
            {"event_type": "phase_start", "phase": "decode", "timestamp_s": 0.5, "metadata": {"source_identity": "s", "request_id": "r", "request_phase_ordinal": 1}},
            {"event_type": "phase_end", "phase": "prefill", "timestamp_s": 1.0, "metadata": {"source_identity": "s", "request_id": "r", "request_phase_ordinal": 0}},
            {"event_type": "phase_end", "phase": "decode", "timestamp_s": 1.5, "metadata": {"source_identity": "s", "request_id": "r", "request_phase_ordinal": 1}},
        ]
        _, pairing_problems = _axi_phase_pairs(overlap_events)
        self.assertTrue(any(problem.startswith("axi:request_phase_overlap:") for problem in pairing_problems))
        observed.add("request_phase_overlap")
        unmatched = overlap_events[:-1]
        _, pairing_problems = _axi_phase_pairs(unmatched)
        self.assertTrue(any(problem.startswith("axi:request_phase_pairing_invalid:") for problem in pairing_problems))
        observed.add("request_phase_pairing_invalid")
        self.assertEqual(observed, AXI_VALIDATOR_REASON_CODES)


if __name__ == "__main__":
    unittest.main()
