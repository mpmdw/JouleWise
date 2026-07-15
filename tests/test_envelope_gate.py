from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Callable

from joulewise.cli import main, validate_bundle
from joulewise.clock import FakeClock
from joulewise.controller import run_benchmark
from joulewise.envelope_gate import (
    EXPECTED_LEVEL_IDS,
    REASON_DENOMINATOR_NOT_8,
    REASON_DISTINCT_ITEM_EVIDENCE_CONFLICT,
    REASON_BUNDLE_NOT_STRICT_VALID,
    REASON_E1,
    REASON_E2,
    REASON_E3,
    REASON_E4,
    REASON_ITEM_EVIDENCE_MALFORMED,
    REASON_LEVEL_SET_MISMATCH,
    REASON_SUITE_MANIFEST_IDENTITY_MISMATCH,
    REASON_SUITE_PROFILE_MISMATCH,
    VERDICT_FAILED,
    VERDICT_REFUSED,
    VERDICT_VALIDATED,
    _ItemEvidence,
    _advisory_e5,
    analyze_envelope_gate,
)
from joulewise.reduce import reduce_bundle
from joulewise.schemas import BenchmarkConfig
from joulewise.suite import suite_manifest_sha256
from joulewise.provenance import suite_prompt_rollup

ROOT = Path(__file__).resolve().parents[1]
AFFINE_CONFIG = ROOT / "configs" / "examples" / "mock_affine_smoke.json"


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records))


class EnvelopeGateTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self.counter = 0

    def make_bundle(
        self,
        mutator: Callable[[dict, dict | None], None] | None = None,
        *,
        corrupt_after_reduce: bool = False,
    ) -> Path:
        self.counter += 1
        raw_config = json.loads(AFFINE_CONFIG.read_text())
        raw_config["run_id"] = f"envelope-gate-{self.counter}"
        config = BenchmarkConfig.from_mapping(raw_config)
        bundle_path, _ = run_benchmark(config, self.runs_root, FakeClock(start=1000.0))
        if mutator is not None:
            self._mutate_item_evidence(bundle_path, mutator)
        summary = reduce_bundle(bundle_path).to_dict()
        (bundle_path / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        if corrupt_after_reduce:
            summary["gross_energy_j"] = 12345
            (bundle_path / "summary_metrics.json").write_text(
                json.dumps(summary, indent=2, sort_keys=True) + "\n"
            )
        return bundle_path

    def _mutate_item_evidence(
        self,
        bundle_path: Path,
        mutator: Callable[[dict, dict | None], None],
    ) -> None:
        outputs_path = bundle_path / "outputs" / "suite_items.jsonl"
        output_records = _read_jsonl(outputs_path)
        outputs_by_index = {record["item_index"]: record for record in output_records}
        events_path = bundle_path / "events.jsonl"
        events = _read_jsonl(events_path)
        for event in events:
            if event["event_type"] != "item_end":
                continue
            metadata = event["metadata"]
            output = outputs_by_index.get(metadata["item_index"])
            mutator(metadata, output)
            if output is not None:
                self._reconcile_output_emitted_token_ids(output)
        _write_jsonl(events_path, events)
        _write_jsonl(outputs_path, output_records)

    def _reconcile_output_emitted_token_ids(self, output: dict) -> None:
        emitted_tokens = output.get("emitted_tokens")
        if (
            isinstance(emitted_tokens, bool)
            or not isinstance(emitted_tokens, int)
            or emitted_tokens < 0
        ):
            return
        token_ids = output.get("emitted_token_ids")
        if not isinstance(token_ids, list):
            return
        if len(token_ids) >= emitted_tokens:
            output["emitted_token_ids"] = token_ids[:emitted_tokens]
        else:
            next_id = max(
                (token for token in token_ids if isinstance(token, int)),
                default=0,
            ) + 1
            output["emitted_token_ids"] = token_ids + list(
                range(next_id, next_id + emitted_tokens - len(token_ids))
            )

    def normalize_pass(self, metadata: dict, output: dict | None) -> None:
        if metadata["item_id"] == "affine_v1_sentinel":
            return
        metadata["stop_reason"] = "eos"
        metadata["emitted_tokens"] = 2
        metadata["prompt_tokens"] = 80
        if output is not None:
            output["stop_reason"] = metadata["stop_reason"]
            output["emitted_tokens"] = metadata["emitted_tokens"]

    def verdict(self, bundle: Path) -> dict:
        return analyze_envelope_gate([bundle], lambda path: validate_bundle(path, strict=True))

    def rewrite_config(self, bundle_path: Path, mutator: Callable[[dict], None]) -> None:
        config_path = bundle_path / "config.json"
        config = json.loads(config_path.read_text())
        mutator(config)
        config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
        metadata_path = bundle_path / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        metadata["config_sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")

    def rewrite_suite_manifest(
        self,
        bundle_path: Path,
        mutator: Callable[[dict], None],
    ) -> None:
        manifest_path = bundle_path / "suite_manifest.json"
        manifest = json.loads(manifest_path.read_text())
        mutator(manifest)
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        manifest_sha = suite_manifest_sha256(manifest)

        def update_config(config: dict) -> None:
            config["workload_profile"]["suite_manifest_sha256"] = manifest_sha

        self.rewrite_config(bundle_path, update_config)
        metadata_path = bundle_path / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        suite = metadata["suite"]
        suite["suite_id"] = manifest["suite_id"]
        suite["suite_profile"] = manifest["suite_profile"]
        suite["suite_revision"] = manifest["suite_revision"]
        suite["manifest_sha256"] = manifest_sha
        suite["item_count"] = len(manifest["items"])
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")

    def remove_l64_level(self, bundle_path: Path) -> None:
        keep_indexes = set(range(17)) | {25}
        remap = {old: new for new, old in enumerate(sorted(keep_indexes))}

        def keep_event(event: dict) -> bool:
            metadata = event.get("metadata")
            if not isinstance(metadata, dict):
                return True
            if metadata.get("level_id") == "L64" or metadata.get("block_id") == "L64":
                return False
            item_id = metadata.get("item_id")
            if isinstance(item_id, str) and item_id.startswith("affine_v1_L64_"):
                return False
            return True

        events = [event for event in _read_jsonl(bundle_path / "events.jsonl") if keep_event(event)]
        for event in events:
            metadata = event.get("metadata")
            if not isinstance(metadata, dict):
                continue
            if event["event_type"] == "suite_start":
                metadata["item_count"] = len(remap)
            if event["event_type"] == "suite_end":
                metadata["items_executed"] = len(remap)
                metadata["status_counts"] = {"capped": len(remap)}
            index = metadata.get("item_index")
            if index in remap:
                metadata["item_index"] = remap[index]
                if "position" in metadata:
                    metadata["position"] = remap[index]
                if metadata.get("item_id") == "affine_v1_sentinel" and index == 25:
                    metadata["prev_item"] = "affine_v1_L08_i07"
        _write_jsonl(bundle_path / "events.jsonl", events)

        outputs = [
            record
            for record in _read_jsonl(bundle_path / "outputs" / "suite_items.jsonl")
            if record.get("item_index") in remap
        ]
        for record in outputs:
            record["item_index"] = remap[record["item_index"]]
        _write_jsonl(bundle_path / "outputs" / "suite_items.jsonl", outputs)
        self.refresh_suite_prompt_rollup(bundle_path)

        def drop_l64(manifest: dict) -> None:
            manifest["items"] = [
                item
                for item in manifest["items"]
                if item["grouping"]["level_id"] != "L64"
            ]

        self.rewrite_suite_manifest(bundle_path, drop_l64)
        summary = reduce_bundle(bundle_path).to_dict()
        (bundle_path / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )

    def refresh_suite_prompt_rollup(self, bundle_path: Path) -> None:
        prompt_hashes: list[str] = []
        total_tokens = 0
        for record in _read_jsonl(bundle_path / "outputs" / "suite_items.jsonl"):
            prompt = record["prompt"]
            prompt_hashes.append(prompt["token_ids_sha256"])
            total_tokens += record["prompt_tokens"]
        metadata_path = bundle_path / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        metadata["workload_provenance"]["prompt"] = suite_prompt_rollup(
            prompt_hashes, total_tokens
        )
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")

    def test_all_pass_verdict(self) -> None:
        bundle = self.make_bundle(self.normalize_pass)
        result = self.verdict(bundle)
        self.assertEqual(result["verdict"], VERDICT_VALIDATED)
        self.assertEqual(result["reason_codes"], [])
        self.assertEqual(
            result["denominators"]["observed_distinct_non_sentinel_items_per_level"],
            {"L01": 8, "L08": 8, "L64": 8},
        )
        self.assertEqual(result["gates"]["E5"]["status"], "expected_not_evaluable")

    def test_e1_n8_zero_tolerance_and_first_attainable_failure(self) -> None:
        def mutate(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            if metadata["item_id"] == "affine_v1_L08_i00":
                metadata["stop_reason"] = "length"

        result = self.verdict(self.make_bundle(mutate))
        self.assertEqual(result["verdict"], VERDICT_FAILED)
        self.assertIn(REASON_E1, result["reason_codes"])
        e1 = result["gates"]["E1"]
        self.assertEqual(e1["counts"]["L08"], {"non_eos": 1, "denominator": 8})
        self.assertEqual(e1["rates"]["L08"], 1 / 8)
        self.assertEqual(e1["max_rate"], 0.125)
        self.assertLess(e1["thresholds"]["max_rate_lte"], 1 / 8)
        self.assertLess(e1["thresholds"]["spread_lte"], 1 / 8)
        self.assertEqual(
            e1["thresholds"]["zero_tolerance_note"],
            "at n=8 distinct items, the 5% threshold means zero tolerated "
            "non-EOS items per level",
        )

    def test_e2_failure_reason_code(self) -> None:
        def mutate(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            if metadata["item_id"] != "affine_v1_sentinel":
                metadata["emitted_tokens"] = 5
            if metadata["item_id"].startswith("affine_v1_L64_"):
                metadata["emitted_tokens"] = 7

        result = self.verdict(self.make_bundle(mutate))
        self.assertEqual(result["verdict"], VERDICT_FAILED)
        self.assertIn(REASON_E2, result["reason_codes"])
        self.assertNotIn(REASON_E3, result["reason_codes"])

    def test_e3_failure_reason_code(self) -> None:
        def mutate(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            item_id = metadata["item_id"]
            if item_id.startswith("affine_v1_L01_"):
                suffix = int(item_id.rsplit("i", 1)[1])
                metadata["emitted_tokens"] = 1 if suffix < 4 else 5
            elif item_id.startswith("affine_v1_L08_") or item_id.startswith("affine_v1_L64_"):
                metadata["emitted_tokens"] = 3

        result = self.verdict(self.make_bundle(mutate))
        self.assertEqual(result["verdict"], VERDICT_FAILED)
        self.assertIn(REASON_E3, result["reason_codes"])
        self.assertNotIn(REASON_E2, result["reason_codes"])

    def test_e4_failure_reason_code(self) -> None:
        def mutate(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            if metadata["item_id"].startswith("affine_v1_L64_"):
                metadata["prompt_tokens"] = 85

        result = self.verdict(self.make_bundle(mutate))
        self.assertEqual(result["verdict"], VERDICT_FAILED)
        self.assertIn(REASON_E4, result["reason_codes"])

    def test_sentinel_exclusion_from_e1(self) -> None:
        bundle = self.make_bundle(self.normalize_pass)
        result = self.verdict(bundle)
        self.assertEqual(result["verdict"], VERDICT_VALIDATED)
        groups = [
            record["group_id"]
            for record in result["calibration_evidence_only"]["level_window_gross_energies_j"]
        ]
        self.assertIn("sentinel_start/sentinel_start", groups)
        self.assertEqual(result["gates"]["E1"]["counts"]["L01"]["non_eos"], 0)

    def test_non_strict_bundle_refusal(self) -> None:
        bundle = self.make_bundle(self.normalize_pass, corrupt_after_reduce=True)
        result = self.verdict(bundle)
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_BUNDLE_NOT_STRICT_VALID, result["reason_codes"])
        self.assertFalse(result["bundle_hashes"][0]["strict_valid"])

    def test_wrong_profile_bundle_is_refused_not_validated(self) -> None:
        bundle = self.make_bundle(self.normalize_pass)
        self.rewrite_config(
            bundle,
            lambda config: config["workload_profile"].__setitem__("name", "mock_suite_smoke"),
        )
        self.assertEqual(validate_bundle(bundle, strict=True), [])

        result = self.verdict(bundle)
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_SUITE_PROFILE_MISMATCH, result["reason_codes"])

    def test_missing_expected_level_bundle_is_refused_not_validated(self) -> None:
        bundle = self.make_bundle(self.normalize_pass)
        self.remove_l64_level(bundle)
        self.assertEqual(validate_bundle(bundle, strict=True), [])

        result = self.verdict(bundle)
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_LEVEL_SET_MISMATCH, result["reason_codes"])
        self.assertEqual(result["expected_levels"], list(EXPECTED_LEVEL_IDS))

    def test_mismatched_manifest_identity_is_refused(self) -> None:
        first = self.make_bundle(self.normalize_pass)
        second = self.make_bundle(self.normalize_pass)
        self.rewrite_suite_manifest(
            second,
            lambda manifest: manifest.__setitem__(
                "suite_revision", "2026-07-08.p2-010b-unit1-alt"
            ),
        )
        summary = reduce_bundle(second).to_dict()
        (second / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = analyze_envelope_gate(
            [first, second], lambda path: validate_bundle(path, strict=True)
        )
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_SUITE_MANIFEST_IDENTITY_MISMATCH, result["reason_codes"])

    def test_multibundle_repetitions_keep_distinct_denominators(self) -> None:
        first = self.make_bundle(self.normalize_pass)
        second = self.make_bundle(self.normalize_pass)
        result = analyze_envelope_gate(
            [first, second], lambda path: validate_bundle(path, strict=True)
        )
        self.assertEqual(result["verdict"], VERDICT_VALIDATED)
        self.assertEqual(result["bundle_count"], 2)
        self.assertEqual(
            result["denominators"]["observed_distinct_non_sentinel_items_per_level"],
            {"L01": 8, "L08": 8, "L64": 8},
        )

    def test_multibundle_distinct_item_conflict_fails_closed(self) -> None:
        def mutate(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            if metadata["item_id"] == "affine_v1_L01_i00":
                metadata["emitted_tokens"] = 3
                if output is not None:
                    output["emitted_tokens"] = 3

        first = self.make_bundle(self.normalize_pass)
        second = self.make_bundle(mutate)
        result = analyze_envelope_gate(
            [first, second], lambda path: validate_bundle(path, strict=True)
        )
        self.assertEqual(result["verdict"], VERDICT_FAILED)
        self.assertIn(REASON_DISTINCT_ITEM_EVIDENCE_CONFLICT, result["reason_codes"])
        self.assertEqual(result["evidence_conflicts"][0]["item_id"], "affine_v1_L01_i00")

    def test_empty_input_is_refused(self) -> None:
        result = analyze_envelope_gate([], lambda path: validate_bundle(path, strict=True))
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_BUNDLE_NOT_STRICT_VALID, result["reason_codes"])

    def test_malformed_item_evidence_fields_emit_refused_verdicts(self) -> None:
        cases = {
            "prompt_tokens": None,
            "emitted_tokens": "2",
            "stop_reason": None,
        }
        for field_name, replacement in cases.items():
            with self.subTest(field_name=field_name):
                def mutate(metadata: dict, output: dict | None) -> None:
                    self.normalize_pass(metadata, output)
                    if metadata["item_id"] == "affine_v1_L01_i00":
                        if replacement is None:
                            metadata.pop(field_name, None)
                        else:
                            metadata[field_name] = replacement

                bundle = self.make_bundle(mutate)
                result = self.verdict(bundle)
                self.assertEqual(result["verdict"], VERDICT_REFUSED)
                self.assertIn(REASON_ITEM_EVIDENCE_MALFORMED, result["reason_codes"])
                self.assertIn(field_name, result["refusal_message"])

    def test_negative_token_counts_are_malformed_item_evidence(self) -> None:
        for field_name in ("prompt_tokens", "emitted_tokens"):
            with self.subTest(field_name=field_name):
                def mutate(metadata: dict, output: dict | None) -> None:
                    self.normalize_pass(metadata, output)
                    if metadata["item_id"] == "affine_v1_L01_i00":
                        metadata[field_name] = -1

                bundle = self.make_bundle(mutate)
                self.assertEqual(validate_bundle(bundle, strict=True), [])
                result = self.verdict(bundle)
                self.assertEqual(result["verdict"], VERDICT_REFUSED)
                self.assertIn(REASON_ITEM_EVIDENCE_MALFORMED, result["reason_codes"])
                self.assertIn(field_name, result["refusal_message"])

    def test_bool_token_counts_are_malformed_item_evidence(self) -> None:
        for field_name in ("prompt_tokens", "emitted_tokens"):
            with self.subTest(field_name=field_name):
                def mutate(metadata: dict, output: dict | None) -> None:
                    self.normalize_pass(metadata, output)
                    if metadata["item_id"] == "affine_v1_L01_i00":
                        metadata[field_name] = True

                bundle = self.make_bundle(mutate)
                self.assertEqual(validate_bundle(bundle, strict=True), [])
                result = self.verdict(bundle)
                self.assertEqual(result["verdict"], VERDICT_REFUSED)
                self.assertIn(REASON_ITEM_EVIDENCE_MALFORMED, result["reason_codes"])
                self.assertIn(field_name, result["refusal_message"])

    def test_zero_token_counts_are_accepted_as_item_evidence(self) -> None:
        def mutate(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            if metadata["item_id"] == "affine_v1_L01_i00":
                metadata["prompt_tokens"] = 0
                metadata["emitted_tokens"] = 0

        result = self.verdict(self.make_bundle(mutate))
        self.assertNotEqual(result["verdict"], VERDICT_REFUSED)
        self.assertNotIn(REASON_ITEM_EVIDENCE_MALFORMED, result["reason_codes"])

    def test_denominator_not_8_reason_code(self) -> None:
        bundle = self.make_bundle(self.normalize_pass)
        def tag_first_l01(manifest: dict) -> None:
            for item in manifest["items"]:
                if item["grouping"]["level_id"] == "L01" and "sentinel" not in item["tags"]:
                    item["tags"].append("sentinel")
                    return

        self.rewrite_suite_manifest(
            bundle,
            tag_first_l01,
        )
        summary = reduce_bundle(bundle).to_dict()
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        self.assertEqual(validate_bundle(bundle, strict=True), [])

        result = self.verdict(bundle)
        self.assertEqual(result["verdict"], VERDICT_FAILED)
        self.assertIn(REASON_DENOMINATOR_NOT_8, result["reason_codes"])
        self.assertEqual(
            result["denominators"]["observed_distinct_non_sentinel_items_per_level"],
            {"L01": 7, "L08": 8, "L64": 8},
        )

    def test_malformed_item_evidence_cli_writes_json_not_traceback(self) -> None:
        def mutate(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            if metadata["item_id"] == "affine_v1_L01_i00":
                metadata.pop("prompt_tokens", None)

        bundle = self.make_bundle(mutate)
        output = self.runs_root / "malformed_envelope_gate.json"
        stderr = StringIO()
        with redirect_stdout(StringIO()), redirect_stderr(stderr):
            exit_code = main(["envelope-gate", str(bundle), "--output", str(output)])
        self.assertEqual(exit_code, 2)
        self.assertEqual(stderr.getvalue(), "")
        payload = json.loads(output.read_text())
        self.assertEqual(payload["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_ITEM_EVIDENCE_MALFORMED, payload["reason_codes"])

    def test_verdict_json_schema_stability(self) -> None:
        result = self.verdict(self.make_bundle(self.normalize_pass))
        self.assertEqual(
            sorted(result),
            [
                "bundle_count",
                "bundle_hashes",
                "calibration_evidence_only",
                "denominators",
                "evidence_conflicts",
                "gates",
                "reason_codes",
                "schema_version",
                "suite",
                "verdict",
            ],
        )
        self.assertEqual(sorted(result["gates"]), ["E1", "E2", "E3", "E4", "E5"])
        self.assertEqual(result["schema_version"], "envelope_gate.v1")

    def test_cli_writes_verdict_artifact(self) -> None:
        bundle = self.make_bundle(self.normalize_pass)
        output = self.runs_root / "envelope_gate.json"
        with redirect_stdout(StringIO()):
            exit_code = main(["envelope-gate", str(bundle), "--output", str(output)])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output.read_text())
        self.assertEqual(payload["verdict"], VERDICT_VALIDATED)
        self.assertEqual(payload["schema_version"], "envelope_gate.v1")

    def test_cli_failed_and_refused_exit_codes_and_stdout_json(self) -> None:
        def fail_e1(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            if metadata["item_id"] == "affine_v1_L08_i00":
                metadata["stop_reason"] = "length"

        failed_bundle = self.make_bundle(fail_e1)
        stdout = StringIO()
        with redirect_stdout(stdout):
            failed_exit = main(["envelope-gate", str(failed_bundle)])
        failed_payload = json.loads(stdout.getvalue())
        self.assertEqual(failed_exit, 3)
        self.assertEqual(failed_payload["verdict"], VERDICT_FAILED)

        refused_bundle = self.make_bundle(self.normalize_pass, corrupt_after_reduce=True)
        stdout = StringIO()
        with redirect_stdout(stdout):
            refused_exit = main(["envelope-gate", str(refused_bundle)])
        refused_payload = json.loads(stdout.getvalue())
        self.assertEqual(refused_exit, 2)
        self.assertEqual(refused_payload["verdict"], VERDICT_REFUSED)

    def test_e2_exact_boundary_passes(self) -> None:
        def mutate(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            if metadata["item_id"].startswith("affine_v1_L64_"):
                metadata["emitted_tokens"] = 3
                if output is not None:
                    output["emitted_tokens"] = 3

        result = self.verdict(self.make_bundle(mutate))
        self.assertTrue(result["gates"]["E2"]["pass"])
        self.assertEqual(result["gates"]["E2"]["spread_tokens"], 1.0)
        self.assertNotIn(REASON_E2, result["reason_codes"])

    def test_e4_exact_boundary_passes(self) -> None:
        def mutate(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            if metadata["item_id"].startswith("affine_v1_L64_"):
                suffix = int(metadata["item_id"].rsplit("i", 1)[1])
                metadata["prompt_tokens"] = 84 if suffix < 4 else 80

        result = self.verdict(self.make_bundle(mutate))
        self.assertEqual(result["verdict"], VERDICT_VALIDATED)
        self.assertTrue(result["gates"]["E4"]["pass"])
        self.assertEqual(result["gates"]["E4"]["global_range_tokens"], 4)
        self.assertEqual(result["gates"]["E4"]["level_mean_spread_tokens"], 2.0)

    def test_e4_global_range_and_mean_spread_fail_independently(self) -> None:
        def mean_only(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            if metadata["item_id"].startswith("affine_v1_L64_"):
                metadata["prompt_tokens"] = 83

        mean_result = self.verdict(self.make_bundle(mean_only))
        self.assertIn(REASON_E4, mean_result["reason_codes"])
        self.assertEqual(mean_result["gates"]["E4"]["global_range_tokens"], 3)
        self.assertEqual(mean_result["gates"]["E4"]["level_mean_spread_tokens"], 3.0)

        def range_only(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            if metadata["item_id"] == "affine_v1_L64_i00":
                metadata["prompt_tokens"] = 85

        range_result = self.verdict(self.make_bundle(range_only))
        self.assertIn(REASON_E4, range_result["reason_codes"])
        self.assertEqual(range_result["gates"]["E4"]["global_range_tokens"], 5)
        self.assertLessEqual(range_result["gates"]["E4"]["level_mean_spread_tokens"], 2.0)

    def test_e3_seed_and_permutation_result_are_deterministic(self) -> None:
        emitted_by_level = {
            "L01": [1, 1, 1, 2, 3, 4, 4, 4],
            "L08": [1, 1, 2, 2, 3, 3, 4, 4],
            "L64": [1, 2, 2, 2, 3, 3, 3, 4],
        }

        def mutate(metadata: dict, output: dict | None) -> None:
            self.normalize_pass(metadata, output)
            item_id = metadata["item_id"]
            for level, values in emitted_by_level.items():
                prefix = f"affine_v1_{level}_"
                if item_id.startswith(prefix):
                    suffix = int(item_id.rsplit("i", 1)[1])
                    metadata["emitted_tokens"] = values[suffix]
                    if output is not None:
                        output["emitted_tokens"] = values[suffix]

        bundle = self.make_bundle(mutate)
        first = self.verdict(bundle)
        second = self.verdict(bundle)
        self.assertEqual(first["gates"]["E3"], second["gates"]["E3"])
        suite_seed = first["suite"]["suite_seed"]
        expected_seed_hash = hashlib.sha256(
            (suite_seed + "envelope_gate").encode("utf-8")
        ).hexdigest()
        self.assertEqual(first["gates"]["E3"]["rng_seed_sha256"], expected_seed_hash)
        self.assertGreater(first["gates"]["E3"]["chi_square"], 0)

    def test_e5_evaluable_branch_is_advisory_only(self) -> None:
        evidence: dict[str, _ItemEvidence] = {}
        for index in range(10):
            evidence[f"correct_{index}"] = _ItemEvidence(
                item_id=f"correct_{index}",
                level_id="L01",
                prompt_tokens=80,
                emitted_tokens=2,
                stop_reason="eos",
                status="succeeded",
                parse_status="parsed",
                correct=True,
            )
            evidence[f"incorrect_{index}"] = _ItemEvidence(
                item_id=f"incorrect_{index}",
                level_id="L01",
                prompt_tokens=80,
                emitted_tokens=4,
                stop_reason="eos",
                status="succeeded",
                parse_status="parsed",
                correct=False,
            )

        result = _advisory_e5(evidence, ["L01"])
        self.assertEqual(result["status"], "evaluable")
        self.assertFalse(result["gates_envelope"])
        self.assertEqual(result["per_level"]["L01"]["abs_mean_delta_tokens"], 2.0)


if __name__ == "__main__":
    unittest.main()
