import copy
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from joulewise.schemas import BenchmarkConfig, SchemaError
from joulewise.suite import SuiteManifest, suite_manifest_sha256
from joulewise.workloads import (
    DEFAULT_SMOKE_ITEMS_PER_LEVEL,
    DEFAULT_SMOKE_LEVELS,
    DEFAULT_SMOKE_SUITE_SEED,
    SCORER_ID,
    SENTINEL_ITEM_ID,
    SENTINEL_ITEM_INDEX,
    SENTINEL_N_ITER,
    build_affine_smoke_annotations,
    build_affine_smoke_manifest,
    derive_item,
    expected_answer_sha256,
    lenient_correct,
    parameters_hash,
    render_prompt,
    score_response,
)


ROOT = Path(__file__).resolve().parents[1]


def independent_derive(seed: str, n_iter: int, item_index: int) -> tuple[int, int, int, int, int]:
    msg = (
        "joulewise.workload.affine_mod_ladder.v1"
        f"\0{seed}\0{n_iter}\0{item_index}"
    ).encode("utf-8")
    digest = hashlib.sha256(msg).digest()
    m = 100 + int.from_bytes(digest[0:8], "big") % 900
    a = 10 + int.from_bytes(digest[8:16], "big") % 90
    b = 10 + int.from_bytes(digest[16:24], "big") % 90
    x0 = 100 + int.from_bytes(digest[24:32], "big") % 900
    x = x0
    for _ in range(n_iter):
        x = (a * x + b) % m
    return a, b, m, x0, x


class AffineWorkloadTests(unittest.TestCase):
    def test_derive_item_golden_values(self) -> None:
        cases = {
            (DEFAULT_SMOKE_SUITE_SEED, 1, 0): (51, 49, 959, 378, 147),
            (DEFAULT_SMOKE_SUITE_SEED, 8, 3): (21, 54, 608, 549, 53),
            (DEFAULT_SMOKE_SUITE_SEED, 64, 7): (36, 87, 387, 635, 114),
        }
        for args, expected in cases.items():
            with self.subTest(args=args):
                item = derive_item(*args)
                actual = (item.a, item.b, item.m, item.x0, item.expected)
                self.assertEqual(actual, expected)
                self.assertEqual(actual, independent_derive(*args))

    def test_parameter_ranges_are_level_invariant(self) -> None:
        for n_iter in DEFAULT_SMOKE_LEVELS:
            for item_index in range(DEFAULT_SMOKE_ITEMS_PER_LEVEL):
                item = derive_item(DEFAULT_SMOKE_SUITE_SEED, n_iter, item_index)
                with self.subTest(n_iter=n_iter, item_index=item_index):
                    self.assertGreaterEqual(item.m, 100)
                    self.assertLessEqual(item.m, 999)
                    self.assertGreaterEqual(item.a, 10)
                    self.assertLessEqual(item.a, 99)
                    self.assertGreaterEqual(item.b, 10)
                    self.assertLessEqual(item.b, 99)
                    self.assertGreaterEqual(item.x0, 100)
                    self.assertLessEqual(item.x0, 999)

    def test_render_prompt_is_raw_completion_text(self) -> None:
        item = derive_item(DEFAULT_SMOKE_SUITE_SEED, 1, 0)
        prompt = render_prompt(item)
        self.assertEqual(
            prompt,
            "Compute a modular recurrence.\n"
            "Start with x = 378.\n"
            "At each step, replace x with (51 * x + 49) mod 959.\n"
            "Perform exactly 1 steps.\n"
            "Answer with only the final value of x as a decimal integer. "
            "Output nothing except that integer.",
        )
        self.assertNotIn("<|", prompt)

    def test_score_response_matrix(self) -> None:
        cases = [
            ("42", 42, "parsed", 42, True, True),
            ("+42", 42, "parsed", 42, True, True),
            ("042", 42, "parsed", 42, True, True),
            ("**42**", 42, "malformed", None, False, True),
            ("42.", 42, "malformed", None, False, True),
            ("The answer is 42", 42, "malformed", None, False, True),
            ("\n\t42  \r", 42, "parsed", 42, True, True),
            ("", 42, "malformed", None, False, False),
            ("42 42 42 42 42 42 42 42 42 42 42 42 42 42 42 42", 42, "malformed", None, False, True),
            ("٤٢", 42, "malformed", None, False, False),
            ("４２", 42, "malformed", None, False, False),
        ]
        for text, expected, status, parsed, correct, lenient in cases:
            with self.subTest(text=text):
                result = score_response(text, expected)
                self.assertEqual(result.parse_status, status)
                self.assertEqual(result.parsed_value, parsed)
                self.assertEqual(result.correct, correct)
                self.assertEqual(lenient_correct(text, expected), lenient)

    def test_expected_answer_hash(self) -> None:
        digest = expected_answer_sha256("affine_v1_L01_i00", 147)
        self.assertEqual(
            digest,
            "17415d395ba899c93d20477636bcc1874fb3510ad85e3f634977aa552c789076",
        )
        payload = (
            "joulewise.affine_answer.v1\0affine_v1_L01_i00\0" + str(147)
        ).encode("utf-8")
        self.assertEqual(digest, hashlib.sha256(payload).hexdigest())

    def test_parameters_hash(self) -> None:
        self.assertEqual(
            parameters_hash(),
            "2dd6347eb863a81b55f30378bf37ccce66296e093768a99af55001d479494847",
        )


class AffineSmokeManifestTests(unittest.TestCase):
    def test_generator_is_deterministic(self) -> None:
        first_manifest = build_affine_smoke_manifest(DEFAULT_SMOKE_SUITE_SEED)
        second_manifest = build_affine_smoke_manifest(DEFAULT_SMOKE_SUITE_SEED)
        first = json.dumps(first_manifest, indent=2, sort_keys=True)
        second = json.dumps(second_manifest, indent=2, sort_keys=True)
        self.assertEqual(first, second)
        self.assertEqual(
            suite_manifest_sha256(first_manifest),
            suite_manifest_sha256(second_manifest),
        )

    def test_manifest_is_substrate_valid_with_dedicated_sentinel_duplicate(self) -> None:
        manifest = SuiteManifest.from_mapping(build_affine_smoke_manifest())
        self.assertEqual(len(manifest.items), 26)
        self.assertEqual(len({item.item_id for item in manifest.items}), 25)
        sentinel_entries = [
            item for item in manifest.items if "sentinel" in item.tags
        ]
        self.assertEqual(len(sentinel_entries), 2)
        self.assertEqual(
            [item.item_id for item in sentinel_entries],
            [SENTINEL_ITEM_ID, SENTINEL_ITEM_ID],
        )
        self.assertEqual(manifest.items[0].item_id, SENTINEL_ITEM_ID)
        self.assertEqual(manifest.items[-1].item_id, SENTINEL_ITEM_ID)
        self.assertEqual(manifest.items[0].category, "sentinel")
        self.assertEqual(manifest.items[-1].category, "sentinel")
        ordinary_items = [
            item
            for item in manifest.items
            if item.grouping.level_id in {"L01", "L08", "L64"}
        ]
        for level_id in ("L01", "L08", "L64"):
            level_items = [item for item in ordinary_items if item.grouping.level_id == level_id]
            self.assertEqual(len(level_items), DEFAULT_SMOKE_ITEMS_PER_LEVEL)
            self.assertEqual(len({item.item_id for item in level_items}), DEFAULT_SMOKE_ITEMS_PER_LEVEL)
            self.assertTrue(all("sentinel" not in item.tags for item in level_items))
        self.assertEqual(manifest.execution_policy.default_output_policy, "natural_eos")
        self.assertEqual(
            manifest.generator.parameters_hash,
            "2dd6347eb863a81b55f30378bf37ccce66296e093768a99af55001d479494847",
        )

    def test_duplicate_regular_item_without_sentinel_tags_is_rejected(self) -> None:
        data = build_affine_smoke_manifest()
        variant = copy.deepcopy(data)
        duplicate = copy.deepcopy(variant["items"][1])
        duplicate["tags"] = []
        variant["items"].insert(2, duplicate)
        with self.assertRaisesRegex(SchemaError, "duplicate item_id"):
            SuiteManifest.from_mapping(variant)

    def test_only_dedicated_sentinel_item_id_is_duplicated(self) -> None:
        data = build_affine_smoke_manifest()
        counts = Counter(item["item_id"] for item in data["items"])
        duplicates = {item_id for item_id, count in counts.items() if count > 1}
        self.assertEqual(duplicates, {SENTINEL_ITEM_ID})
        for item in data["items"]:
            if item["item_id"] != SENTINEL_ITEM_ID:
                self.assertNotIn("sentinel", item["tags"])

    def test_manifest_contains_no_scoring_fields(self) -> None:
        data = build_affine_smoke_manifest()
        text = json.dumps(data, sort_keys=True)
        self.assertNotIn("expected_answer", text)
        self.assertNotIn("expected_answer_sha256", text)
        self.assertNotIn("scoring", text)

    def test_forbidden_scoring_fields_are_rejected_by_schema(self) -> None:
        data = build_affine_smoke_manifest()
        data["items"][0]["scoring"] = {"scorer_id": "later"}
        with self.assertRaises(SchemaError):
            SuiteManifest.from_mapping(data)

        data = build_affine_smoke_manifest()
        data["items"][0]["expected_answer"] = 0
        with self.assertRaises(SchemaError):
            SuiteManifest.from_mapping(data)

    def test_sidecar_manifest_consistency(self) -> None:
        manifest = build_affine_smoke_manifest()
        sidecar = build_affine_smoke_annotations(manifest)
        self.assertEqual(sidecar["manifest_sha256"], suite_manifest_sha256(manifest))
        self.assertEqual(sidecar["scorer"]["scorer_id"], SCORER_ID)
        self.assertEqual(len(sidecar["annotations"]), len(manifest["items"]))
        by_execution = {
            row["execution_index"]: row for row in sidecar["annotations"]
        }
        for execution_index, item in enumerate(manifest["items"]):
            row = by_execution[execution_index]
            self.assertEqual(row["item_id"], item["item_id"])
            self.assertEqual(row["tags"], item["tags"])
            if item["item_id"] == SENTINEL_ITEM_ID:
                n_iter = SENTINEL_N_ITER
                item_index = SENTINEL_ITEM_INDEX
            else:
                n_iter = int(item["difficulty"]["value"])
                item_index = int(item["item_id"].split("_i", 1)[1])
            expected = derive_item(manifest["suite_seed"], n_iter, item_index).expected
            self.assertEqual(row["expected_answer"], expected)
            self.assertEqual(
                row["expected_answer_sha256"],
                expected_answer_sha256(item["item_id"], expected),
            )

    def test_generated_files_match_builder(self) -> None:
        manifest_path = ROOT / "configs" / "suite_manifests" / "affine_smoke_v1.json"
        sidecar_path = (
            ROOT / "configs" / "suite_manifests" / "affine_smoke_v1_annotations.json"
        )
        manifest = json.loads(manifest_path.read_text())
        sidecar = json.loads(sidecar_path.read_text())
        self.assertEqual(manifest, build_affine_smoke_manifest())
        self.assertEqual(sidecar, build_affine_smoke_annotations(manifest))

    def test_generated_manifest_bytes_match_canonical_builder_bytes(self) -> None:
        manifest_path = ROOT / "configs" / "suite_manifests" / "affine_smoke_v1.json"
        built = build_affine_smoke_manifest(DEFAULT_SMOKE_SUITE_SEED)
        canonical_bytes = (
            json.dumps(built, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        self.assertEqual(canonical_bytes, manifest_path.read_bytes())

    def test_on_disk_manifest_loads_with_expected_item_accounting(self) -> None:
        manifest_path = ROOT / "configs" / "suite_manifests" / "affine_smoke_v1.json"
        manifest_data = json.loads(manifest_path.read_text())
        manifest = SuiteManifest.from_mapping(manifest_data)
        self.assertEqual(len(manifest.items), 26)
        self.assertEqual(len({item.item_id for item in manifest.items}), 25)

    def test_mock_affine_config_hash_uses_manifest_hash(self) -> None:
        config_path = ROOT / "configs" / "examples" / "mock_affine_smoke.json"
        manifest_path = ROOT / "configs" / "suite_manifests" / "affine_smoke_v1.json"
        config_data = json.loads(config_path.read_text())
        manifest_data = json.loads(manifest_path.read_text())
        self.assertEqual(
            config_data["workload_profile"]["suite_manifest_sha256"],
            suite_manifest_sha256(manifest_data),
        )
        config = BenchmarkConfig.from_mapping(config_data)
        config_bytes = (
            json.dumps(config.to_dict(), indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        self.assertEqual(
            hashlib.sha256(config_bytes).hexdigest(),
            "cd113411afe49a2047b7efd1cd1237fca3f48c1e31fe54c5f15f610ef6190592",
        )


if __name__ == "__main__":
    unittest.main()
