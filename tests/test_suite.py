import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from joulewise.schemas import SchemaError
from joulewise.suite import (
    ITEM_END,
    ITEM_START,
    MARKER_DEFAULTS,
    OUTPUT_DEFAULTS,
    REDUCER_ASSIGNABLE,
    RUNTIME_ASSIGNABLE,
    SUITE_START,
    ItemStatus,
    SuiteManifest,
    canonical_effective_manifest,
    load_suite_manifest,
    order_seed,
    suite_manifest_sha256,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json"
SUITE_CONFIG_PATH = ROOT / "configs" / "examples" / "mock_suite_local.json"
PINNED_MOCK_SUITE_MANIFEST_SHA256 = (
    "16c2d67f8c5e84b369938ee8d633dec01c594f5f7fcbf22fcaa2301d986e1267"
)


def manifest_data() -> dict:
    return json.loads(MANIFEST_PATH.read_text())


class SuiteManifestTests(unittest.TestCase):
    def test_manifest_round_trips_with_effective_defaults(self) -> None:
        manifest = SuiteManifest.from_mapping(manifest_data())
        payload = manifest.to_dict()
        self.assertEqual(payload["markers"], MARKER_DEFAULTS)
        self.assertEqual(payload["outputs"], OUTPUT_DEFAULTS)
        self.assertEqual(SuiteManifest.from_mapping(payload).to_dict(), payload)

    def test_canonical_sha_uses_effective_sorted_json(self) -> None:
        data = manifest_data()
        effective = canonical_effective_manifest(data)
        expected_bytes = (json.dumps(effective, indent=2, sort_keys=True) + "\n").encode()
        self.assertEqual(
            suite_manifest_sha256(data),
            hashlib.sha256(expected_bytes).hexdigest(),
        )
        with_defaults = copy.deepcopy(data)
        with_defaults["markers"] = dict(MARKER_DEFAULTS)
        with_defaults["outputs"] = dict(OUTPUT_DEFAULTS)
        self.assertEqual(suite_manifest_sha256(data), suite_manifest_sha256(with_defaults))

    def test_suite_config_hash_matches_referenced_effective_manifest(self) -> None:
        config = json.loads(SUITE_CONFIG_PATH.read_text())
        ref = config["workload_profile"]["suite_manifest_ref"]
        manifest_path = (SUITE_CONFIG_PATH.parent / ref).resolve()
        manifest = json.loads(manifest_path.read_text())
        digest = suite_manifest_sha256(manifest)
        self.assertEqual(config["workload_profile"]["suite_manifest_sha256"], digest)
        self.assertEqual(digest, PINNED_MOCK_SUITE_MANIFEST_SHA256)

    def test_marker_and_output_blocks_must_match_pinned_defaults(self) -> None:
        data = manifest_data()
        data["markers"] = dict(MARKER_DEFAULTS)
        data["markers"]["item_start_event"] = "item_begin"
        with self.assertRaisesRegex(SchemaError, "markers.item_start_event"):
            SuiteManifest.from_mapping(data)

        data = manifest_data()
        data["outputs"] = dict(OUTPUT_DEFAULTS)
        data["outputs"]["per_item_status"] = "state"
        with self.assertRaisesRegex(SchemaError, "outputs.per_item_status"):
            SuiteManifest.from_mapping(data)

    def test_deferred_and_unknown_fields_are_rejected(self) -> None:
        data = manifest_data()
        data["items"][0]["scoring"] = {"scorer_id": "later"}
        with self.assertRaisesRegex(SchemaError, "deferred"):
            SuiteManifest.from_mapping(data)

        data = manifest_data()
        data["items"][0]["source"]["benchmark_import"] = "later"
        with self.assertRaisesRegex(SchemaError, "deferred"):
            SuiteManifest.from_mapping(data)

        data = manifest_data()
        data["items"][0]["unexpected"] = True
        with self.assertRaisesRegex(SchemaError, "unknown key"):
            SuiteManifest.from_mapping(data)

    def test_prompt_sources_are_mutually_exclusive(self) -> None:
        data = manifest_data()
        data["items"][0]["source"]["prompt_text"] = "hello"
        data["items"][0]["source"]["prompt_token_ids"] = [1, 2]
        with self.assertRaisesRegex(SchemaError, "mutually exclusive"):
            SuiteManifest.from_mapping(data)

    def test_ids_native_shape_mismatch_rejected(self) -> None:
        data = manifest_data()
        data["items"][1]["source"]["prompt_token_ids"] = [9, 8, 7]
        data["items"][1]["shape"]["planned_prompt_tokens"] = 4
        with self.assertRaisesRegex(SchemaError, "got 3, expected 4"):
            SuiteManifest.from_mapping(data)

    def test_duplicate_item_ids_require_sentinel_tags(self) -> None:
        data = manifest_data()
        duplicate = copy.deepcopy(data["items"][0])
        data["items"].insert(1, duplicate)
        with self.assertRaisesRegex(SchemaError, "duplicate item_id"):
            SuiteManifest.from_mapping(data)

        data = manifest_data()
        self.assertEqual(
            [item["item_id"] for item in data["items"]].count("mock_sentinel_repeat"),
            2,
        )
        self.assertEqual(
            [item.item_id for item in SuiteManifest.from_mapping(data).items].count(
                "mock_sentinel_repeat"
            ),
            2,
        )

    def test_block_and_level_ids_must_be_contiguous_runs(self) -> None:
        data = manifest_data()
        third = copy.deepcopy(data["items"][0])
        third["item_id"] = "mock_item_003"
        third["grouping"]["block_id"] = "block_a"
        data["items"].append(third)
        data["items"][1]["grouping"]["block_id"] = "block_b"
        with self.assertRaisesRegex(SchemaError, "block_id is not contiguous"):
            SuiteManifest.from_mapping(data)

        data = manifest_data()
        data["items"][2]["grouping"]["level_id"] = data["items"][0]["grouping"]["level_id"]
        SuiteManifest.from_mapping(data)

        data = manifest_data()
        recur = copy.deepcopy(data["items"][0])
        recur["item_id"] = "mock_item_level_recur"
        recur["grouping"]["block_id"] = "block_a"
        recur["grouping"]["level_id"] = "level_1"
        data["items"][1]["grouping"]["level_id"] = "level_2"
        data["items"].insert(2, recur)
        with self.assertRaisesRegex(SchemaError, "level_id is not contiguous within block"):
            SuiteManifest.from_mapping(data)

    def test_schema_version_output_policy_and_status_policy_are_pinned(self) -> None:
        data = manifest_data()
        data["schema_version"] = "suite_manifest.v2"
        with self.assertRaisesRegex(SchemaError, "expected|got|schema_version"):
            SuiteManifest.from_mapping(data)

        data = manifest_data()
        data["items"][0]["output_policy"] = "other"
        with self.assertRaisesRegex(SchemaError, "items\\[\\]\\.output_policy"):
            SuiteManifest.from_mapping(data)

        data = manifest_data()
        data["items"][0]["status_policy"] = "strict_json"
        with self.assertRaisesRegex(SchemaError, "items\\[\\]\\.status_policy"):
            SuiteManifest.from_mapping(data)

    def test_status_assignable_subsets_are_pinned(self) -> None:
        self.assertEqual(ItemStatus.SUCCEEDED.value, "succeeded")
        self.assertEqual(ItemStatus.EXCLUDED_FROM_CLAIM.value, "excluded_from_claim")

    def test_suite_status_assignment_sets_are_pinned(self) -> None:
        self.assertEqual(
            {status.value for status in RUNTIME_ASSIGNABLE},
            {"succeeded", "malformed", "capped", "runtime_failed"},
        )
        self.assertEqual(
            {status.value for status in REDUCER_ASSIGNABLE},
            {"succeeded", "malformed", "capped", "runtime_failed", "below_floor"},
        )
        self.assertNotIn(ItemStatus.EXCLUDED_FROM_CLAIM, RUNTIME_ASSIGNABLE)
        self.assertNotIn(ItemStatus.EXCLUDED_FROM_CLAIM, REDUCER_ASSIGNABLE)

    def test_order_seed_derivation(self) -> None:
        expected = hashlib.sha256(b"seed\0manifest_order\0007").hexdigest()
        self.assertEqual(order_seed("seed", "manifest_order", 7), expected)

    def test_load_suite_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "suite.json"
            path.write_text(json.dumps(manifest_data()))
            self.assertEqual(load_suite_manifest(path).suite_id, "mock_suite_smoke")

    def test_marker_constants_are_exported(self) -> None:
        self.assertEqual(SUITE_START, "suite_start")
        self.assertEqual(ITEM_START, "item_start")
        self.assertEqual(ITEM_END, "item_end")


if __name__ == "__main__":
    unittest.main()
