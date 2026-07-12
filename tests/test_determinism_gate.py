from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import warnings
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch

from joulewise import determinism_gate as determinism_gate_module
from joulewise.cli import main, validate_bundle
from joulewise.clock import FakeClock
from joulewise.controller import run_benchmark
from joulewise.determinism_gate import (
    REASON_BUNDLE_NOT_STRICT_VALID,
    REASON_DIFFERENT_CONFIGS,
    REASON_DIFFERENT_REPETITION_GROUPS,
    REASON_DUPLICATE_BUNDLE,
    REASON_DUPLICATE_REPETITION,
    REASON_FEWER_THAN_TWO_BUNDLES,
    REASON_ITEM_STATUS_MISMATCH,
    REASON_RESPONSE_HASH_CONTENT_MISMATCH,
    REASON_RESPONSE_HASH_EVIDENCE_MISMATCH,
    REASON_RESPONSE_HASH_MALFORMED,
    REASON_RESPONSE_HASH_MISSING,
    REASON_RESPONSE_HASH_MISMATCH,
    VERDICT_REFUSED,
    VERDICT_SUPPORTED,
    VERDICT_VIOLATED,
    analyze_determinism_gate,
)
from joulewise.reduce import reduce_bundle
from joulewise.schemas import BenchmarkConfig, ConfigKeyWarning

ROOT = Path(__file__).resolve().parents[1]
AFFINE_CONFIG = ROOT / "configs" / "examples" / "mock_affine_smoke.json"
SINGLE_RESPONSE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"
RETAINED_RUNS_ROOT = ROOT / "runs"

IDENTITY_FIELD_NAMES = [
    "metadata.environment.python_packages",
    "metadata.workload_provenance.generator",
    "metadata.workload_provenance.model.artifact_identity.folded_sha256",
    "metadata.workload_provenance.model.artifact_identity.sha256",
    "metadata.workload_provenance.sampler",
    "metadata.workload_provenance.tokenizer",
]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


class DeterminismGateTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        manifest = json.loads(
            (ROOT / "configs" / "suite_manifests" / "affine_smoke_v1.json").read_text(
                encoding="utf-8"
            )
        )
        manifest["execution_policy"]["default_output_policy"] = "fixed_budget_exact"
        for item in manifest["items"]:
            item["output_policy"] = "fixed_budget_exact"
        self.affine_manifest = Path(tmp.name) / "affine-succeeded.json"
        self.affine_manifest.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        config = json.loads(AFFINE_CONFIG.read_text(encoding="utf-8"))
        config["workload_profile"]["suite_manifest_ref"] = str(self.affine_manifest)
        config["workload_profile"]["suite_manifest_sha256"] = hashlib.sha256(
            self.affine_manifest.read_bytes()
        ).hexdigest()
        self.affine_config = Path(tmp.name) / "affine-succeeded-config.json"
        self.affine_config.write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def make_bundle(
        self,
        group: str,
        repetition: int,
        *,
        config_path: Path | None = None,
        config_mutator: Callable[[dict[str, Any]], None] | None = None,
    ) -> Path:
        if config_path is None:
            config_path = self.affine_config
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["run_id"] = f"{group}__r{repetition}"
        raw["workload_profile"]["repetitions"] = 2
        if config_mutator is not None:
            config_mutator(raw)
        config = BenchmarkConfig.from_mapping(raw)
        bundle, _ = run_benchmark(
            config,
            self.runs_root,
            FakeClock(start=1_000_000.0 + repetition * 10_000.0),
        )
        self.assertEqual(validate_bundle(bundle, strict=True), [])
        return bundle

    def make_group(
        self,
        group: str = "determinism-fixture",
        *,
        config_path: Path | None = None,
    ) -> list[Path]:
        return [
            self.make_bundle(group, repetition, config_path=config_path)
            for repetition in (1, 2)
        ]

    def config_with_manifest(
        self,
        name: str,
        manifest_mutator: Callable[[dict[str, Any]], None],
    ) -> Path:
        manifest = json.loads(self.affine_manifest.read_text(encoding="utf-8"))
        manifest_mutator(manifest)
        manifest_path = self.affine_manifest.parent / f"{name}-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        config = json.loads(self.affine_config.read_text(encoding="utf-8"))
        config["workload_profile"]["suite_manifest_ref"] = str(manifest_path)
        config["workload_profile"]["suite_manifest_sha256"] = hashlib.sha256(
            manifest_path.read_bytes()
        ).hexdigest()
        config_path = self.affine_manifest.parent / f"{name}-config.json"
        config_path.write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return config_path

    def verdict(self, bundles: list[Path]) -> dict[str, Any]:
        return analyze_determinism_gate(
            bundles,
            lambda path: validate_bundle(path, strict=True),
        )

    def rewrite_item_hash(
        self,
        bundle: Path,
        item_id: str,
        response_hash: Any,
        *,
        item_index: int | None = None,
    ) -> tuple[int, str]:
        events_path = bundle / "events.jsonl"
        events = _read_jsonl(events_path)
        target: tuple[int, str] | None = None
        for event in events:
            metadata = event.get("metadata")
            if event.get("event_type") != "item_end" or not isinstance(metadata, dict):
                continue
            if metadata.get("item_id") == item_id and (
                item_index is None or metadata.get("item_index") == item_index
            ):
                metadata["response_sha256"] = response_hash
                target = (metadata["item_index"], metadata["item_id"])
                break
        self.assertIsNotNone(target)
        _write_jsonl(events_path, events)
        outputs_path = bundle / "outputs" / "suite_items.jsonl"
        outputs = _read_jsonl(outputs_path)
        for output in outputs:
            if output.get("item_id") == item_id and (
                item_index is None or output.get("item_index") == item_index
            ):
                output["response_sha256"] = response_hash
                break
        _write_jsonl(outputs_path, outputs)
        summary = reduce_bundle(bundle).to_dict()
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if target is None:
            raise AssertionError(f"missing item_end for {item_id}")
        return target

    def rewrite_event_hash_only(
        self,
        bundle: Path,
        item_id: str,
        response_hash: Any,
    ) -> None:
        events_path = bundle / "events.jsonl"
        events = _read_jsonl(events_path)
        changed = False
        for event in events:
            metadata = event.get("metadata")
            if event.get("event_type") != "item_end" or not isinstance(metadata, dict):
                continue
            if metadata.get("item_id") == item_id:
                metadata["response_sha256"] = response_hash
                changed = True
                break
        self.assertTrue(changed)
        _write_jsonl(events_path, events)
        summary = reduce_bundle(bundle).to_dict()
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def rewrite_item_response(
        self,
        bundle: Path,
        item_id: str,
        response_text: str,
        *,
        item_index: int | None = None,
    ) -> tuple[int, str]:
        response_hash = hashlib.sha256(response_text.encode("utf-8")).hexdigest()
        target = self.rewrite_item_hash(
            bundle,
            item_id,
            response_hash,
            item_index=item_index,
        )
        outputs_path = bundle / "outputs" / "suite_items.jsonl"
        outputs = _read_jsonl(outputs_path)
        changed = False
        for output in outputs:
            if output.get("item_id") == item_id and (
                item_index is None or output.get("item_index") == item_index
            ):
                output["response_text"] = response_text
                changed = True
                break
        self.assertTrue(changed)
        _write_jsonl(outputs_path, outputs)
        return target

    def rewrite_item_status(
        self,
        bundle: Path,
        item_id: str,
        status: str,
        *,
        item_index: int | None = None,
    ) -> tuple[int, str]:
        events_path = bundle / "events.jsonl"
        events = _read_jsonl(events_path)
        target: tuple[int, str] | None = None
        for event in events:
            metadata = event.get("metadata")
            if event.get("event_type") != "item_end" or not isinstance(metadata, dict):
                continue
            if metadata.get("item_id") == item_id and (
                item_index is None or metadata.get("item_index") == item_index
            ):
                metadata["status"] = status
                target = (metadata["item_index"], metadata["item_id"])
                break
        self.assertIsNotNone(target)

        status_counts: dict[str, int] = {}
        for event in events:
            metadata = event.get("metadata")
            if event.get("event_type") == "item_end" and isinstance(metadata, dict):
                item_status = metadata.get("status")
                if isinstance(item_status, str):
                    status_counts[item_status] = status_counts.get(item_status, 0) + 1
        for event in events:
            metadata = event.get("metadata")
            if event.get("event_type") == "suite_end" and isinstance(metadata, dict):
                metadata["status_counts"] = dict(sorted(status_counts.items()))
                break
        _write_jsonl(events_path, events)

        outputs_path = bundle / "outputs" / "suite_items.jsonl"
        outputs = _read_jsonl(outputs_path)
        changed = False
        for output in outputs:
            if output.get("item_id") == item_id and (
                item_index is None or output.get("item_index") == item_index
            ):
                output["status"] = status
                changed = True
                break
        self.assertTrue(changed)
        _write_jsonl(outputs_path, outputs)

        summary = reduce_bundle(bundle).to_dict()
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if target is None:
            raise AssertionError(f"missing item_end for {item_id}")
        return target

    def rewrite_raw_config_value(self, bundle: Path, key: str, value: Any) -> None:
        config_path = bundle / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config[key] = value
        config_path.write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        metadata_path = bundle / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["config_sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def rewrite_metadata(self, bundle: Path, mutator: Callable[[dict[str, Any]], None]) -> None:
        metadata_path = bundle / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        mutator(metadata)
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def test_matching_repetition_group_supports_determinism(self) -> None:
        result = self.verdict(self.make_group())
        self.assertEqual(result["verdict"], VERDICT_SUPPORTED)
        self.assertEqual(result["reason_codes"], [])
        self.assertEqual(result["bundle_count"], 2)
        self.assertGreater(result["comparison"]["item_count"], 1)
        self.assertEqual(result["comparison"]["response_hash_source"], "recorded_suite_item")
        self.assertEqual(result["mismatches"], [])
        self.assertEqual(
            result["identity_fields_compared"],
            [
                "metadata.environment.python_packages",
                "metadata.workload_provenance.generator",
                "metadata.workload_provenance.model.artifact_identity.sha256",
                "metadata.workload_provenance.tokenizer",
            ],
        )
        self.assertEqual(
            result["identity_fields_absent"],
            [
                "metadata.workload_provenance.model.artifact_identity.folded_sha256",
                "metadata.workload_provenance.sampler",
            ],
        )

    def test_capped_suite_item_is_comparison_eligible(self) -> None:
        def cap_first_item(manifest: dict[str, Any]) -> None:
            manifest["items"][0]["output_policy"] = "natural_eos"

        config_path = self.config_with_manifest("one-capped", cap_first_item)
        result = self.verdict(self.make_group("one-capped", config_path=config_path))

        self.assertEqual(result["verdict"], "determinism_supported")
        self.assertEqual(result["reason_codes"], [])
        for bundle in result["bundles"]:
            self.assertEqual(
                bundle["item_status_counts"],
                {"capped": 1, "succeeded": 25},
            )

    def test_all_capped_matching_group_supports_determinism_and_records_profile(
        self,
    ) -> None:
        result = self.verdict(
            self.make_group("all-capped", config_path=AFFINE_CONFIG)
        )

        self.assertEqual(result["verdict"], "determinism_supported")
        self.assertEqual(result["reason_codes"], [])
        self.assertEqual(result["item_status_mismatches"], [])
        for bundle in result["bundles"]:
            self.assertEqual(bundle["item_count"], 26)
            self.assertEqual(bundle["item_status_counts"], {"capped": 26})
            self.assertEqual(
                {item["status"] for item in bundle["items"]},
                {"capped"},
            )

    def test_succeeded_capped_status_flip_is_refused_and_names_item(self) -> None:
        first, second = self.make_group("status-flip", config_path=AFFINE_CONFIG)
        item_index, item_id = self.rewrite_item_status(
            first,
            "affine_v1_L08_i00",
            "succeeded",
        )
        self.assertEqual(validate_bundle(first, strict=True), [])

        result = self.verdict([first, second])

        self.assertEqual(result["verdict"], "bundle_refused")
        self.assertEqual(result["reason_codes"], ["item_status_mismatch"])
        self.assertEqual(len(result["item_status_mismatches"]), 1)
        mismatch = result["item_status_mismatches"][0]
        self.assertEqual(mismatch["item_index"], item_index)
        self.assertEqual(mismatch["item_id"], item_id)
        self.assertEqual(
            [entry["status"] for entry in mismatch["observed"]],
            ["succeeded", "capped"],
        )

    def test_status_flip_and_missing_hash_both_refuse_with_honest_profile(
        self,
    ) -> None:
        first, second = self.make_group(
            "status-flip-missing-hash",
            config_path=AFFINE_CONFIG,
        )
        item_index, item_id = self.rewrite_item_status(
            first,
            "affine_v1_L08_i00",
            "succeeded",
        )
        outputs_path = first / "outputs" / "suite_items.jsonl"
        outputs = _read_jsonl(outputs_path)
        target = next(output for output in outputs if output["item_index"] == item_index)
        target.pop("response_sha256")
        _write_jsonl(outputs_path, outputs)
        self.assertEqual(validate_bundle(first, strict=True), [])

        result = self.verdict([first, second])

        self.assertEqual(result["verdict"], "bundle_refused")
        self.assertEqual(
            result["reason_codes"],
            [
                "item_set_mismatch",
                "item_status_mismatch",
                "response_hash_missing",
            ],
        )
        self.assertEqual(result["bundles"][0]["item_status_counts"], {
            "capped": 25,
            "succeeded": 1,
        })
        self.assertEqual(result["bundles"][1]["item_status_counts"], {
            "capped": 26,
        })
        self.assertEqual(len(result["item_status_mismatches"]), 1)
        mismatch = result["item_status_mismatches"][0]
        self.assertEqual((mismatch["item_index"], mismatch["item_id"]), (item_index, item_id))
        self.assertEqual(
            [entry["status"] for entry in mismatch["observed"]],
            ["succeeded", "capped"],
        )

    def test_one_flipped_hash_violates_and_names_item(self) -> None:
        first, second = self.make_group()
        item_index, item_id = self.rewrite_item_response(
            second,
            "affine_v1_L08_i00",
            "one deliberately changed response\n",
        )
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_VIOLATED)
        self.assertEqual(result["reason_codes"], [REASON_RESPONSE_HASH_MISMATCH])
        self.assertEqual(len(result["mismatches"]), 1)
        mismatch = result["mismatches"][0]
        self.assertEqual((mismatch["item_index"], mismatch["item_id"]), (item_index, item_id))
        self.assertEqual(len(mismatch["observed"]), 2)

    def test_different_configs_are_refused(self) -> None:
        first = self.make_bundle("mixed-config", 1)

        def change_tags(raw: dict[str, Any]) -> None:
            raw["run_metadata"]["tags"].append("different-config")

        second = self.make_bundle("mixed-config", 2, config_mutator=change_tags)
        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_DIFFERENT_CONFIGS, result["reason_codes"])

    def test_json_distinct_boolean_and_integer_configs_refuse_in_either_argv_order(
        self,
    ) -> None:
        first, second = self.make_group("json-type-distinction")
        self.rewrite_raw_config_value(first, "future_x", True)
        self.rewrite_raw_config_value(second, "future_x", 1)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConfigKeyWarning)
            self.assertEqual(validate_bundle(first, strict=True), [])
            self.assertEqual(validate_bundle(second, strict=True), [])
            payloads = []
            for argv in ([first, second], [second, first]):
                stdout = StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(
                        ["determinism-gate", *(str(bundle) for bundle in argv)]
                    )
                self.assertEqual(exit_code, 2)
                payloads.append(json.loads(stdout.getvalue()))
        for payload in payloads:
            self.assertEqual(payload["verdict"], "bundle_refused")
            self.assertIn("different_configs", payload["reason_codes"])
            self.assertIsNone(payload["comparison"])
        self.assertEqual(payloads[0]["verdict"], payloads[1]["verdict"])
        self.assertEqual(payloads[0]["reason_codes"], payloads[1]["reason_codes"])

    def test_differing_model_artifact_identity_hashes_are_refused(self) -> None:
        first, second = self.make_group("model-identity-mismatch")

        def change_hash(metadata: dict[str, Any]) -> None:
            metadata["workload_provenance"]["model"]["artifact_identity"]["sha256"] = (
                "f" * 64
            )

        self.rewrite_metadata(second, change_hash)
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], "bundle_refused")
        self.assertIn("identity_evidence_mismatch", result["reason_codes"])

    def test_partial_identity_field_presence_is_refused(self) -> None:
        first, second = self.make_group("identity-presence-mismatch")

        def remove_hash(metadata: dict[str, Any]) -> None:
            del metadata["workload_provenance"]["model"]["artifact_identity"]["sha256"]

        self.rewrite_metadata(second, remove_hash)
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], "bundle_refused")
        self.assertIn("identity_evidence_mismatch", result["reason_codes"])

    def test_all_absent_identity_fields_remain_comparable_and_recorded(self) -> None:
        first, second = self.make_group("legacy-identity-absence")
        for bundle in (first, second):
            self.rewrite_metadata(
                bundle,
                lambda metadata: (
                    metadata.pop("workload_provenance", None),
                    metadata.pop("environment", None),
                ),
            )

        result = analyze_determinism_gate([first, second], lambda path: [])
        self.assertEqual(result["verdict"], "determinism_supported")
        self.assertEqual(result["identity_fields_compared"], [])
        self.assertEqual(result["identity_fields_absent"], IDENTITY_FIELD_NAMES)

    def test_unknown_raw_config_difference_is_refused(self) -> None:
        first, second = self.make_group("raw-config-difference")
        config_path = second / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["future_sampler"] = {"mode": "future"}
        config_path.write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        metadata_path = second / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["config_sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConfigKeyWarning)
            self.assertEqual(validate_bundle(second, strict=True), [])
            result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_DIFFERENT_CONFIGS, result["reason_codes"])

    def test_different_repetition_groups_are_refused(self) -> None:
        first = self.make_bundle("group-a", 1)
        second = self.make_bundle("group-b", 2)
        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_DIFFERENT_REPETITION_GROUPS, result["reason_codes"])

    def test_duplicate_bundle_and_repetition_are_refused(self) -> None:
        bundle = self.make_bundle("duplicate", 1)
        result = self.verdict([bundle, bundle])
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_DUPLICATE_BUNDLE, result["reason_codes"])
        self.assertIn(REASON_DUPLICATE_REPETITION, result["reason_codes"])

    def test_fewer_than_two_bundles_is_refused(self) -> None:
        result = self.verdict([self.make_bundle("singleton", 1)])
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_FEWER_THAN_TWO_BUNDLES, result["reason_codes"])

    def test_strict_invalid_bundle_is_refused(self) -> None:
        first, second = self.make_group()
        summary_path = second / "summary_metrics.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["gross_energy_j"] += 1.0
        summary_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.assertNotEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_BUNDLE_NOT_STRICT_VALID, result["reason_codes"])

    def test_malformed_hash_field_is_refused(self) -> None:
        first, second = self.make_group()
        self.rewrite_item_hash(second, "affine_v1_L08_i00", "A" * 64)
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_RESPONSE_HASH_MALFORMED, result["reason_codes"])

    def test_missing_hash_field_is_refused(self) -> None:
        first, second = self.make_group()
        outputs_path = second / "outputs" / "suite_items.jsonl"
        outputs = _read_jsonl(outputs_path)
        outputs[0].pop("response_sha256")
        _write_jsonl(outputs_path, outputs)
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_RESPONSE_HASH_MISSING, result["reason_codes"])

    def test_conflicting_duplicate_response_hash_key_is_refused(self) -> None:
        first, second = self.make_group("duplicate-json-key")
        outputs_path = second / "outputs" / "suite_items.jsonl"
        lines = outputs_path.read_text(encoding="utf-8").splitlines()
        output = json.loads(lines[0])
        response_hash = output["response_sha256"]
        conflicting_hash = "f" * 64 if response_hash != "f" * 64 else "e" * 64
        needle = f'"response_sha256": "{response_hash}"'
        replacement = (
            f'"response_sha256": "{conflicting_hash}", '
            f'"response_sha256": "{response_hash}"'
        )
        self.assertIn(needle, lines[0])
        lines[0] = lines[0].replace(needle, replacement, 1)
        outputs_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], "bundle_refused")
        self.assertIn("duplicate_json_key", result["reason_codes"])

    def test_conflicting_output_and_item_end_hashes_are_refused(self) -> None:
        first, second = self.make_group()
        self.rewrite_event_hash_only(second, "affine_v1_L08_i00", "e" * 64)
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_RESPONSE_HASH_EVIDENCE_MISMATCH, result["reason_codes"])

    def test_stale_suite_hashes_are_refused_against_response_text(self) -> None:
        first, second = self.make_group()
        outputs_path = second / "outputs" / "suite_items.jsonl"
        outputs = _read_jsonl(outputs_path)
        outputs[0]["response_text"] += "changed without refreshing hashes"
        _write_jsonl(outputs_path, outputs)
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_RESPONSE_HASH_CONTENT_MISMATCH, result["reason_codes"])

    def test_malformed_item_end_hash_is_refused(self) -> None:
        first, second = self.make_group()
        self.rewrite_event_hash_only(second, "affine_v1_L08_i00", "BAD")
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_RESPONSE_HASH_MALFORMED, result["reason_codes"])

    def test_repeated_sentinel_ids_are_compared_by_item_index(self) -> None:
        first, second = self.make_group()
        outputs = _read_jsonl(second / "outputs" / "suite_items.jsonl")
        sentinel_indexes = sorted(
            output["item_index"]
            for output in outputs
            if output.get("item_id") == "affine_v1_sentinel"
        )
        self.assertGreaterEqual(len(sentinel_indexes), 2)
        target_index = sentinel_indexes[-1]
        self.rewrite_item_response(
            second,
            "affine_v1_sentinel",
            "changed repeated sentinel response\n",
            item_index=target_index,
        )

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_VIOLATED)
        self.assertEqual(len(result["mismatches"]), 1)
        self.assertEqual(result["mismatches"][0]["item_index"], target_index)
        self.assertEqual(result["mismatches"][0]["item_id"], "affine_v1_sentinel")

    def test_malformed_and_runtime_failed_suite_items_are_refused(self) -> None:
        for tag, status in (
            ("mock-malformed", "malformed"),
            ("mock-runtime-failed", "runtime_failed"),
        ):
            with self.subTest(status=status):
                def mark_first_item(
                    manifest: dict[str, Any],
                    *,
                    item_tag: str = tag,
                ) -> None:
                    manifest["items"][0]["tags"].append(item_tag)

                config_path = self.config_with_manifest(status, mark_first_item)
                bundles = self.make_group(
                    f"ineligible-{status}",
                    config_path=config_path,
                )
                for bundle in bundles:
                    summary = json.loads(
                        (bundle / "summary_metrics.json").read_text()
                    )
                    outputs = _read_jsonl(bundle / "outputs" / "suite_items.jsonl")
                    self.assertEqual(summary["status"], "succeeded")
                    self.assertTrue(
                        any(output["status"] == status for output in outputs)
                    )
                    self.assertEqual(validate_bundle(bundle, strict=True), [])

                result = self.verdict(bundles)
                self.assertEqual(result["verdict"], "bundle_refused")
                self.assertEqual(result["reason_codes"], ["item_not_succeeded"])

    def test_asymmetric_whole_item_absence_is_refused(self) -> None:
        first, second = self.make_group("asymmetric-item-absence")
        outputs_path = second / "outputs" / "suite_items.jsonl"
        outputs = _read_jsonl(outputs_path)
        outputs.pop()
        _write_jsonl(outputs_path, outputs)

        result = analyze_determinism_gate([first, second], lambda path: [])
        self.assertEqual(result["verdict"], "bundle_refused")
        self.assertIn("item_set_mismatch", result["reason_codes"])

    def test_composed_and_decomposed_unicode_response_bytes_violate(self) -> None:
        first, second = self.make_group("unicode-byte-identity")
        item_id = "affine_v1_L08_i00"
        composed = "caf\u00e9\n"
        decomposed = "cafe\u0301\n"
        self.assertNotEqual(composed.encode("utf-8"), decomposed.encode("utf-8"))
        self.rewrite_item_response(first, item_id, composed)
        self.rewrite_item_response(second, item_id, decomposed)
        self.assertEqual(validate_bundle(first, strict=True), [])
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(
            result["verdict"],
            "determinism_violated(response_hash_mismatch)",
        )
        self.assertEqual(result["reason_codes"], ["response_hash_mismatch"])
        observed = result["mismatches"][0]["observed"]
        self.assertNotEqual(observed[0]["response_sha256"], observed[1]["response_sha256"])

    def test_non_suite_response_bytes_supply_the_single_item_hash(self) -> None:
        result = self.verdict(
            self.make_group("single-response", config_path=SINGLE_RESPONSE_CONFIG)
        )
        self.assertEqual(result["verdict"], VERDICT_SUPPORTED)
        self.assertEqual(result["comparison"]["item_count"], 1)
        self.assertEqual(
            result["comparison"]["response_hash_source"],
            "derived_response_bytes",
        )

    def test_non_suite_response_byte_change_violates_determinism(self) -> None:
        first, second = self.make_group(
            "single-response-change",
            config_path=SINGLE_RESPONSE_CONFIG,
        )
        response_path = second / "outputs" / "response.txt"
        response_path.write_bytes(response_path.read_bytes() + b"changed\n")
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_VIOLATED)
        self.assertEqual(result["mismatches"][0]["item_id"], "response")

    def test_missing_non_suite_response_is_refused(self) -> None:
        first, second = self.make_group(
            "single-response-missing",
            config_path=SINGLE_RESPONSE_CONFIG,
        )
        (second / "outputs" / "response.txt").unlink()
        self.assertEqual(validate_bundle(second, strict=True), [])

        result = self.verdict([first, second])
        self.assertEqual(result["verdict"], VERDICT_REFUSED)
        self.assertIn(REASON_RESPONSE_HASH_MISSING, result["reason_codes"])

    def test_hypothetical_zero_item_comparison_is_refused(self) -> None:
        bundles = self.make_group(
            "zero-item-defense",
            config_path=SINGLE_RESPONSE_CONFIG,
        )
        with patch(
            "joulewise.determinism_gate._single_response_hash",
            return_value=({}, []),
        ):
            result = self.verdict(bundles)
        self.assertEqual(result["verdict"], "bundle_refused")
        self.assertIn("no_items_to_compare", result["reason_codes"])

    def test_production_cli_argv_returns_exit_code_and_stdout_verdict(self) -> None:
        first, second = self.make_group("cli-fixture")
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["determinism-gate", str(first), str(second)])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["verdict"], VERDICT_SUPPORTED)
        self.assertEqual(payload["schema_version"], "determinism_gate.v1")

    def test_cli_violated_three_member_group_writes_matching_output_semantics(self) -> None:
        bundles = [self.make_bundle("cli-violated", repetition) for repetition in (1, 2, 3)]
        self.rewrite_item_response(
            bundles[2],
            "affine_v1_L08_i00",
            "only repetition three differs\n",
        )
        output_path = self.runs_root.parent / "violated-verdict.json"
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = main(
                [
                    "determinism-gate",
                    *(str(bundle) for bundle in bundles),
                    "--output",
                    str(output_path),
                ]
            )

        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 3)
        self.assertEqual(
            payload["verdict"],
            "determinism_violated(response_hash_mismatch)",
        )
        self.assertEqual(payload["reason_codes"], ["response_hash_mismatch"])
        self.assertEqual(len(payload["mismatches"]), 1)
        self.assertEqual(len(payload["mismatches"][0]["observed"]), 3)
        self.assertEqual(
            stdout.getvalue(),
            f"determinism-gate: {output_path} verdict={payload['verdict']}\n",
        )

    def test_cli_refused_group_writes_matching_output_semantics(self) -> None:
        bundle = self.make_bundle("cli-refused", 1)
        output_path = self.runs_root.parent / "refused-verdict.json"
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = main(
                [
                    "determinism-gate",
                    str(bundle),
                    "--output",
                    str(output_path),
                ]
            )

        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 2)
        self.assertEqual(payload["verdict"], "bundle_refused")
        self.assertIn("fewer_than_two_bundles", payload["reason_codes"])
        self.assertEqual(
            stdout.getvalue(),
            f"determinism-gate: {output_path} verdict={payload['verdict']}\n",
        )

    def test_cli_refuses_output_inside_input_bundle_without_writing(self) -> None:
        first, second = self.make_group("inside-output")
        output_path = first / "outputs" / ".." / "summary_metrics.json"
        before = output_path.read_bytes()
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = main(
                [
                    "determinism-gate",
                    str(first),
                    str(second),
                    "--output",
                    str(output_path),
                ]
            )

        self.assertEqual(exit_code, 2)
        self.assertEqual(output_path.read_bytes(), before)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["verdict"], "bundle_refused")
        self.assertIn("output_inside_input_bundle", payload["reason_codes"])

    def test_cli_output_write_failure_preserves_payload_and_computed_exit(self) -> None:
        first, second = self.make_group("write-failure")
        output_path = self.runs_root.parent / "unwritable-output-directory"
        output_path.mkdir()
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(
                [
                    "determinism-gate",
                    str(first),
                    str(second),
                    "--output",
                    str(output_path),
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["verdict"], "determinism_supported")
        self.assertIn("failed to write --output", stderr.getvalue())

    def test_cli_zero_bundle_arguments_emit_refusal_envelope(self) -> None:
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(["determinism-gate"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertEqual(payload["verdict"], "bundle_refused")
        self.assertEqual(payload["reason_codes"], ["fewer_than_two_bundles"])
        self.assertEqual(stderr.getvalue(), "")

    def test_wire_vocabulary_literals_and_payload_keys_are_pinned(self) -> None:
        expected_constants = {
            "SCHEMA_VERSION": "determinism_gate.v1",
            "VERDICT_SUPPORTED": "determinism_supported",
            "VERDICT_VIOLATED": "determinism_violated(response_hash_mismatch)",
            "VERDICT_REFUSED": "bundle_refused",
            "REASON_RESPONSE_HASH_MISMATCH": "response_hash_mismatch",
            "REASON_FEWER_THAN_TWO_BUNDLES": "fewer_than_two_bundles",
            "REASON_DUPLICATE_BUNDLE": "duplicate_bundle",
            "REASON_BUNDLE_NOT_STRICT_VALID": "bundle_not_strict_valid",
            "REASON_BUNDLE_NOT_SUCCEEDED": "bundle_not_succeeded",
            "REASON_BUNDLE_READ_ERROR": "bundle_read_error",
            "REASON_NOT_REPETITION_BUNDLE": "not_repetition_bundle",
            "REASON_DIFFERENT_REPETITION_GROUPS": "different_repetition_groups",
            "REASON_DUPLICATE_REPETITION": "duplicate_repetition",
            "REASON_DIFFERENT_CONFIGS": "different_configs",
            "REASON_IDENTITY_EVIDENCE_MISMATCH": "identity_evidence_mismatch",
            "REASON_ITEM_SET_MISMATCH": "item_set_mismatch",
            "REASON_ITEM_NOT_SUCCEEDED": "item_not_succeeded",
            "REASON_ITEM_STATUS_MISMATCH": "item_status_mismatch",
            "REASON_NO_ITEMS_TO_COMPARE": "no_items_to_compare",
            "REASON_DUPLICATE_JSON_KEY": "duplicate_json_key",
            "REASON_RESPONSE_HASH_MISSING": "response_hash_missing",
            "REASON_RESPONSE_HASH_MALFORMED": "response_hash_malformed",
            "REASON_RESPONSE_HASH_EVIDENCE_MISMATCH": "response_hash_evidence_mismatch",
            "REASON_RESPONSE_HASH_CONTENT_MISMATCH": "response_hash_content_mismatch",
            "REASON_RESPONSE_TEXT_MALFORMED": "response_text_missing_or_malformed",
            "REASON_RESPONSE_EVIDENCE_PROFILE_MISMATCH": "response_evidence_profile_mismatch",
            "REASON_OUTPUT_INSIDE_INPUT_BUNDLE": "output_inside_input_bundle",
        }
        for name, literal in expected_constants.items():
            self.assertEqual(getattr(determinism_gate_module, name), literal)

        first, second = self.make_group("wire-shape")
        supported = self.verdict([first, second])
        self.assertEqual(
            set(supported),
            {
                "schema_version",
                "verdict",
                "reason_codes",
                "bundle_count",
                "bundles",
                "comparison",
                "mismatches",
                "item_status_mismatches",
                "identity_fields_compared",
                "identity_fields_absent",
            },
        )
        self.assertEqual(
            set(supported["bundles"][0]),
            {
                "path",
                "strict_valid",
                "strict_problems",
                "status",
                "run_id",
                "repetition_group",
                "repetition_index",
                "config_sha256",
                "normalized_config_sha256",
                "response_hash_source",
                "item_count",
                "item_status_counts",
                "items",
                "evidence_problems",
            },
        )
        self.assertEqual(
            set(supported["bundles"][0]["items"][0]),
            {"item_index", "item_id", "response_sha256", "status"},
        )
        self.assertEqual(
            set(supported["comparison"]),
            {
                "repetition_group",
                "normalized_config_sha256",
                "item_count",
                "response_hash_source",
            },
        )

        self.rewrite_item_response(second, "affine_v1_L08_i00", "wire mismatch\n")
        violated = self.verdict([first, second])
        self.assertEqual(
            set(violated["mismatches"][0]),
            {"item_index", "item_id", "observed"},
        )
        self.assertEqual(
            set(violated["mismatches"][0]["observed"][0]),
            {"path", "run_id", "response_sha256"},
        )
        refused = analyze_determinism_gate([], lambda path: [])
        self.assertEqual(
            set(refused),
            {
                "schema_version",
                "verdict",
                "reason_codes",
                "bundle_count",
                "bundles",
                "comparison",
                "mismatches",
                "item_status_mismatches",
                "refusal_message",
                "identity_fields_compared",
                "identity_fields_absent",
            },
        )

    def test_retained_corpus_groups_pass_the_real_gate_read_only(self) -> None:
        if not RETAINED_RUNS_ROOT.is_dir():
            message = (
                "ACCEPTANCE GATE SKIP: determinism gate requires the retained "
                "runs/ corpus"
            )
            print(message, file=sys.stderr)
            self.skipTest(message)
        groups = {
            "example-mac-mlx-local": sorted(
                RETAINED_RUNS_ROOT.glob("example-mac-mlx-local__r[123]")
            ),
            "example-mac-mlx-qwen35-122b-512t": sorted(
                RETAINED_RUNS_ROOT.glob("example-mac-mlx-qwen35-122b-512t__r[123]")
            ),
        }
        self.assertEqual(
            {name: len(paths) for name, paths in groups.items()},
            {
                "example-mac-mlx-local": 3,
                "example-mac-mlx-qwen35-122b-512t": 3,
            },
        )
        for name, paths in groups.items():
            with self.subTest(group=name):
                payload = self.verdict(paths)
                self.assertEqual(payload["verdict"], "determinism_supported")
                self.assertEqual(payload["reason_codes"], [])
                self.assertEqual(payload["identity_fields_compared"], [])
                self.assertEqual(payload["identity_fields_absent"], IDENTITY_FIELD_NAMES)


if __name__ == "__main__":
    unittest.main()
