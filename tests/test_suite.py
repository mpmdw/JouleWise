import copy
import hashlib
import json
import tempfile
import unittest
from collections import Counter
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
    policy_row_count,
    realized_order,
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
