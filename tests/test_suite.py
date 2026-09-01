import copy
import hashlib
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from joulewise.schemas import SchemaError
from joulewise.suite import (
    CACHE_POLICY_VERIFICATION_DECLARED_NOT_VERIFIED,
    ITEM_END,
    ITEM_START,
    LEGACY_SUITE_SCHEMA_VERSION,
    MARKER_DEFAULTS,
    OUTPUT_DEFAULTS,
    REDUCER_ASSIGNABLE,
    RUNTIME_ASSIGNABLE,
    SUITE_SCHEMA_VERSION,
    SUITE_POLICY_SEMANTICS,
    SUITE_START,
    ItemStatus,
    SuiteManifest,
    canonical_effective_manifest,
    load_suite_manifest,
    migrate_suite_manifest,
    order_seed,
    policy_row_count,
    realized_order,
    suite_manifest_sha256,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json"
GSM8K_MANIFEST_PATH = (
    ROOT / "configs" / "suite_manifests" / "gsm8k_scored_v6_qwen3.json"
)
SUITE_CONFIG_PATH = ROOT / "configs" / "examples" / "mock_suite_local.json"
PINNED_MOCK_SUITE_MANIFEST_SHA256 = (
    "16c2d67f8c5e84b369938ee8d633dec01c594f5f7fcbf22fcaa2301d986e1267"
)
RETAINED_SUITE_MANIFEST_SHA256 = {
    "affine_smoke_v1.json": "24fb008b7c38484b6a7cb36a4fef1fce4c47a669e3db23131bce06088340f7a9",
    "jw_mixed_v1_qwen25_15b.json": "855be4e5b40c70bd017d83c9c576b07e6912e9200ea5bbd90985f9a376a6c5f1",
    "jw_sentinel_v1_qwen25_15b.json": "0316283dde8afd5fc0dea66b56037a1aea34b42d415aec57af4831a119af8471",
    "mock_suite_manifest.json": PINNED_MOCK_SUITE_MANIFEST_SHA256,
}


def manifest_data() -> dict:
    return json.loads(MANIFEST_PATH.read_text())


def policy_manifest(
    order_policy: str,
    *,
    rotatable_blocks: int = 3,
    sentinel_anchors: bool = True,
    two_item_first_block: bool = False,
) -> SuiteManifest:
    data = manifest_data()
    data["execution_policy"]["order_policy"] = order_policy
    template = copy.deepcopy(data["items"][0])
    items = []
    if sentinel_anchors:
        items.append(_policy_item(template, "sentinel_start", "sentinel_start", ["sentinel"]))
    for block_index in range(rotatable_blocks):
        block = chr(ord("A") + block_index)
        items.append(_policy_item(template, f"item_{block}_0", block, []))
        if block_index == 0 and two_item_first_block:
            items.append(_policy_item(template, f"item_{block}_1", block, []))
    if sentinel_anchors:
        items.append(_policy_item(template, "sentinel_end", "sentinel_end", ["sentinel"]))
    data["items"] = items
    return SuiteManifest.from_mapping(data)


def _policy_item(template: dict, item_id: str, block_id: str, tags: list[str]) -> dict:
    item = copy.deepcopy(template)
    item["item_id"] = item_id
    item["source"]["source_item_id"] = item_id
    item["grouping"]["condition_id"] = block_id
    item["grouping"]["block_id"] = block_id
    item["grouping"]["level_id"] = block_id
    item["tags"] = tags
    return item


def realized_block_sequence(manifest: SuiteManifest, order_row: int) -> list[str]:
    blocks: list[str] = []
    previous = None
    for entry in realized_order(manifest, order_row=order_row):
        block_id = entry.item.grouping.block_id
        if block_id != previous:
            blocks.append(block_id)
            previous = block_id
    return blocks


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
        legacy_hash_projection = SuiteManifest.from_mapping(effective).to_dict(
            schema_version=LEGACY_SUITE_SCHEMA_VERSION
        )
        expected_bytes = (
            json.dumps(legacy_hash_projection, indent=2, sort_keys=True) + "\n"
        ).encode()
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
        manifest_path = (ROOT / ref).resolve()  # refs resolve from repo root (process cwd), matching the controller
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
        with self.assertRaisesRegex(SchemaError, "unknown key"):
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

    def test_v2_ids_native_prompt_may_retain_rendered_audit_text(self) -> None:
        data = migrate_suite_manifest(manifest_data())
        item = data["items"][0]
        item["source"]["prompt_text"] = "rendered audit text"
        item["source"]["prompt_token_ids"] = [1, 2, 3, 4]
        parsed = SuiteManifest.from_mapping(data)
        self.assertEqual(parsed.items[0].prompt_source_kind(), "prompt_token_ids")
        self.assertEqual(parsed.to_dict(), data)

    def test_v2_scoring_and_benchmark_import_are_exact_and_hash_validated(self) -> None:
        data = json.loads(GSM8K_MANIFEST_PATH.read_text())
        parsed = SuiteManifest.from_mapping(data)
        self.assertEqual(parsed.to_dict(), data)
        self.assertIsNotNone(parsed.benchmark_import)
        self.assertIsNotNone(parsed.items[0].scoring)

        unknown_scoring = copy.deepcopy(data)
        unknown_scoring["items"][0]["scoring"]["surprise"] = True
        with self.assertRaisesRegex(SchemaError, r"items\[\]\.scoring.*unknown key"):
            SuiteManifest.from_mapping(unknown_scoring)

        bad_scoring_hash = copy.deepcopy(data)
        bad_scoring_hash["items"][0]["scoring"]["expected_answer_hash"] = "bad"
        with self.assertRaisesRegex(SchemaError, "expected_answer_hash.*64-hex"):
            SuiteManifest.from_mapping(bad_scoring_hash)

        unknown_import = copy.deepcopy(data)
        unknown_import["benchmark_import"]["surprise"] = True
        with self.assertRaisesRegex(SchemaError, "benchmark_import.*unknown key"):
            SuiteManifest.from_mapping(unknown_import)

        unknown_rendered_with = copy.deepcopy(data)
        unknown_rendered_with["benchmark_import"]["rendered_with"]["surprise"] = True
        with self.assertRaisesRegex(
            SchemaError, r"benchmark_import\.rendered_with.*unknown key"
        ):
            SuiteManifest.from_mapping(unknown_rendered_with)

        bad_import_hash = copy.deepcopy(data)
        bad_import_hash["benchmark_import"]["selected_item_ids_sha256"] = "f" * 63
        with self.assertRaisesRegex(SchemaError, "selected_item_ids_sha256.*64-hex"):
            SuiteManifest.from_mapping(bad_import_hash)

        reordered_ids = copy.deepcopy(data)
        selected_ids = reordered_ids["benchmark_import"]["selected_item_ids"]
        selected_ids[0], selected_ids[1] = selected_ids[1], selected_ids[0]
        reordered_ids["benchmark_import"]["selected_item_ids_sha256"] = (
            hashlib.sha256(
                json.dumps(
                    selected_ids, sort_keys=True, separators=(",", ":")
                ).encode("utf-8")
            ).hexdigest()
        )
        with self.assertRaisesRegex(
            SchemaError, "selected_item_ids must match items"
        ):
            SuiteManifest.from_mapping(reordered_ids)

        mismatched_subset = copy.deepcopy(data)
        mismatched_subset["source_manifest"]["subset_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            SchemaError, "subset_sha256 must match benchmark_import"
        ):
            SuiteManifest.from_mapping(mismatched_subset)

        missing_scoring = copy.deepcopy(data)
        del missing_scoring["items"][0]["scoring"]
        with self.assertRaisesRegex(SchemaError, "requires items\\[\\]\\.scoring"):
            SuiteManifest.from_mapping(missing_scoring)

        mismatched_template = copy.deepcopy(data)
        mismatched_template["items"][0]["source"]["prompt_template_id"] = "other"
        with self.assertRaisesRegex(SchemaError, "prompt_template_id must match"):
            SuiteManifest.from_mapping(mismatched_template)

        with self.assertRaisesRegex(SchemaError, "benchmark_import requires suite_manifest.v2"):
            parsed.to_dict(schema_version=LEGACY_SUITE_SCHEMA_VERSION)

    def test_v1_still_defers_v2_scoring_and_benchmark_import(self) -> None:
        data = manifest_data()
        data["benchmark_import"] = {"dataset": "later"}
        with self.assertRaisesRegex(SchemaError, "deferred"):
            SuiteManifest.from_mapping(data)

        data = manifest_data()
        data["items"][0]["scoring"] = {
            "scorer_id": "later",
            "expected_answer_hash": "0" * 64,
            "correctness_quarantine": "later",
        }
        with self.assertRaisesRegex(SchemaError, "deferred"):
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

    def test_schema_version_output_policy_and_removed_status_policy_are_pinned(self) -> None:
        data = manifest_data()
        data["schema_version"] = "suite_manifest.v3"
        with self.assertRaisesRegex(SchemaError, "expected|got|schema_version"):
            SuiteManifest.from_mapping(data)

        data = manifest_data()
        data["items"][0]["output_policy"] = "other"
        with self.assertRaisesRegex(SchemaError, "items\\[\\]\\.output_policy"):
            SuiteManifest.from_mapping(data)

        data = manifest_data()
        data = migrate_suite_manifest(data)
        data["items"][0]["status_policy"] = "strict_json"
        with self.assertRaisesRegex(
            SchemaError, "items\\[\\]\\.status_policy was removed"
        ):
            SuiteManifest.from_mapping(data)

        legacy = SuiteManifest.from_mapping(manifest_data()).to_dict(
            schema_version=LEGACY_SUITE_SCHEMA_VERSION
        )
        legacy["items"][0]["status_policy"] = "strict_json"
        with self.assertRaisesRegex(
            SchemaError, "items\\[\\]\\.status_policy.*permits only 'none'"
        ):
            SuiteManifest.from_mapping(legacy)

    def test_v1_reader_migrates_without_rewriting_legacy_hash(self) -> None:
        legacy = canonical_effective_manifest(manifest_data())
        current = migrate_suite_manifest(legacy)

        migrated = migrate_suite_manifest(legacy)

        self.assertEqual(migrated, canonical_effective_manifest(current))
        self.assertEqual(migrated["schema_version"], SUITE_SCHEMA_VERSION)
        self.assertNotIn("status_policy", migrated["items"][0])
        self.assertNotEqual(
            suite_manifest_sha256(legacy), suite_manifest_sha256(migrated)
        )

    def test_all_retained_v1_manifests_migrate_with_pinned_hashes(self) -> None:
        manifest_root = ROOT / "configs" / "suite_manifests"
        for filename, expected_hash in RETAINED_SUITE_MANIFEST_SHA256.items():
            with self.subTest(filename=filename):
                legacy = json.loads((manifest_root / filename).read_text())
                self.assertEqual(legacy["schema_version"], LEGACY_SUITE_SCHEMA_VERSION)
                self.assertTrue(
                    all(item.get("status_policy") == "none" for item in legacy["items"])
                )
                migrated = migrate_suite_manifest(legacy)
                self.assertEqual(migrated["schema_version"], SUITE_SCHEMA_VERSION)
                self.assertTrue(
                    all("status_policy" not in item for item in migrated["items"])
                )
                self.assertTrue(
                    all(
                        item["output_policy"] in {"fixed_budget_exact", "natural_eos"}
                        for item in migrated["items"]
                    )
                )
                self.assertEqual(
                    migrated["execution_policy"]["cache_policy_verification"],
                    CACHE_POLICY_VERIFICATION_DECLARED_NOT_VERIFIED,
                )
                self.assertEqual(suite_manifest_sha256(legacy), expected_hash)
                self.assertNotEqual(suite_manifest_sha256(migrated), expected_hash)

    def test_r4_policy_semantics_are_explicit_and_reserved_values_are_pinned(self) -> None:
        data = migrate_suite_manifest(manifest_data())
        policy = data["execution_policy"]
        self.assertEqual(
            SUITE_POLICY_SEMANTICS,
            {
                "execution_policy.order_policy": "enforced",
                "execution_policy.within_bundle_repeats": "reserved_compat",
                "execution_policy.cooldown_policy": "descriptive_provenance",
                "execution_policy.cache_policy": (
                    "descriptive_provenance_declared_not_verified"
                ),
                "execution_policy.warmup_policy": "reserved_compat",
                "execution_policy.default_output_policy": "descriptive_provenance",
                "items[].output_policy": "enforced",
                "items[].status_policy": "removed",
            },
        )
        self.assertIn("order_policy", policy)
        self.assertNotIn("cache_policy", policy)
        self.assertEqual(
            policy["cache_policy_verification"],
            CACHE_POLICY_VERIFICATION_DECLARED_NOT_VERIFIED,
        )
        self.assertEqual(policy["within_bundle_repeats"], 1)
        self.assertEqual(policy["warmup_policy"], "adapter_default")
        self.assertIn("cooldown_policy", policy)
        self.assertIn("default_output_policy", policy)
        parsed = SuiteManifest.from_mapping(data)
        self.assertFalse(hasattr(parsed.execution_policy, "cache_policy"))
        self.assertEqual(
            parsed.execution_policy.declared_cache_policy,
            policy["declared_cache_policy"],
        )

        missing_marker = copy.deepcopy(data)
        del missing_marker["execution_policy"]["cache_policy_verification"]
        with self.assertRaisesRegex(SchemaError, "cache_policy_verification"):
            SuiteManifest.from_mapping(missing_marker)

        repeats = copy.deepcopy(data)
        repeats["execution_policy"]["within_bundle_repeats"] = 2
        with self.assertRaisesRegex(SchemaError, "reserved compatibility.*must be 1"):
            SuiteManifest.from_mapping(repeats)

        warmup = copy.deepcopy(data)
        warmup["execution_policy"]["warmup_policy"] = "custom"
        with self.assertRaisesRegex(SchemaError, "warmup_policy"):
            SuiteManifest.from_mapping(warmup)

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

    def test_unknown_order_policy_is_rejected(self) -> None:
        data = manifest_data()
        data["execution_policy"]["order_policy"] = "surprise_shuffle"
        with self.assertRaisesRegex(SchemaError, "execution_policy.order_policy"):
            SuiteManifest.from_mapping(data)

    def test_round_robin_rotates_only_non_sentinel_blocks(self) -> None:
        manifest = policy_manifest(
            "block_round_robin_v1",
            rotatable_blocks=3,
            sentinel_anchors=True,
            two_item_first_block=True,
        )

        entries = realized_order(manifest, order_row=1)

        self.assertEqual(
            [entry.item.grouping.block_id for entry in entries],
            ["sentinel_start", "B", "C", "A", "A", "sentinel_end"],
        )
        self.assertEqual([entry.item_index for entry in entries], [0, 3, 4, 1, 2, 5])
        self.assertEqual([entry.position for entry in entries], list(range(6)))

    def test_latin_square_even_rows_balance_positions_and_adjacencies(self) -> None:
        manifest = policy_manifest(
            "block_latin_square_v1",
            rotatable_blocks=4,
            sentinel_anchors=False,
        )
        rows = [realized_block_sequence(manifest, row) for row in range(policy_row_count(manifest))]

        for position in range(4):
            self.assertEqual({row[position] for row in rows}, {"A", "B", "C", "D"})
        adjacency_counts = Counter(
            (left, right)
            for row in rows
            for left, right in zip(row, row[1:], strict=False)
        )
        self.assertTrue(all(count == 1 for count in adjacency_counts.values()))

    def test_latin_square_odd_rows_use_williams_pair(self) -> None:
        manifest = policy_manifest(
            "block_latin_square_v1",
            rotatable_blocks=3,
            sentinel_anchors=False,
        )
        rows = [realized_block_sequence(manifest, row) for row in range(policy_row_count(manifest))]

        self.assertEqual(len(rows), 6)
        for position in range(3):
            self.assertEqual(Counter(row[position] for row in rows), Counter({"A": 2, "B": 2, "C": 2}))
        adjacency_counts = Counter(
            (left, right)
            for row in rows
            for left, right in zip(row, row[1:], strict=False)
        )
        self.assertEqual(
            set(adjacency_counts),
            {
                ("A", "B"),
                ("A", "C"),
                ("B", "A"),
                ("B", "C"),
                ("C", "A"),
                ("C", "B"),
            },
        )
        self.assertTrue(all(count == 2 for count in adjacency_counts.values()))

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
