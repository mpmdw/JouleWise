"""Synthetic workload selection tests; no MATH installation is required."""
import tempfile
import unittest
from pathlib import Path

from joulewise.benchmark_import_math import (
    _expected_rendered_prompt, eligible_records, select_items, select_pilot,
)
from joulewise.packs.difficulty.config import load_config
from joulewise.packs.difficulty.manifest import build_manifest, rendered_prompt

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/difficulty/pack_config.json"


def math_rows(count=30):
    return [{"unique_id": f"test/synthetic/{level}-{index}.json", "level": level,
             "subject": ("Algebra", "Geometry", "Prealgebra")[index % 3],
             "problem": f"Compute {level} + {index}.", "answer": str(level + index),
             "solution": f"\\boxed{{{level + index}}}", "source_file": "test.jsonl"}
            for level in range(1, 6) for index in range(count)]


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.config = {**load_config(FIXTURE), "n_per_level": 12, "energy_per_level": 3,
                       "exclude_importer_sets": False, "exclude_item_id_files": []}
        self.rows = math_rows()

    def test_seed_reproducibility_and_subject_prefix(self):
        manifest = build_manifest(self.config, self.rows)
        self.assertEqual(manifest, build_manifest(self.config, list(reversed(self.rows))))
        other = build_manifest({**self.config, "seed": "different"}, self.rows)
        self.assertNotEqual([item["item_id"] for item in manifest["items"]],
                            [item["item_id"] for item in other["items"]])
        for level in range(1, 6):
            selected = [item for item in manifest["items"] if item["level"] == level]
            for index in range(0, 12, 3):
                self.assertEqual(len({item["subject"] for item in selected[index:index+3]}), 3)

    def test_level_round_robin_and_energy_prefix(self):
        items = build_manifest(self.config, self.rows)["items"]
        for index, item in enumerate(items):
            self.assertEqual(item["order"], index)
            self.assertEqual(item["level"], index % 5 + 1)
            self.assertEqual(item["energy_subset"], index < 15)
        self.assertEqual(sum(item["energy_subset"] for item in items), 15)

    def test_file_exclusions(self):
        eligible, _ = eligible_records(self.rows)
        ids = [row["source_item_id"] for row in eligible[:8]]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exclude.txt"
            path.write_text("\n" + "\n".join(ids + [ids[0], "absent"]) + "\n", encoding="utf-8")
            manifest = build_manifest({**self.config, "n_per_level": 30,
                                       "exclude_item_id_files": [str(path)]}, self.rows)
        self.assertTrue(set(ids).isdisjoint(item["item_id"] for item in manifest["items"]))
        self.assertEqual(manifest["excluded_count"], 8)

    def test_importer_sets_excluded(self):
        rows = math_rows(160)
        eligible, _ = eligible_records(rows)
        pilot = select_pilot(eligible)
        excluded = {row["source_item_id"] for row in pilot + select_items(eligible, pilot, 128)}
        manifest = build_manifest({**self.config, "exclude_importer_sets": True}, rows)
        self.assertTrue(excluded.isdisjoint(item["item_id"] for item in manifest["items"]))
        self.assertEqual(manifest["excluded_count"], 5 * (16 + 128))
        self.assertEqual(manifest["level_counts"], dict.fromkeys(map(str, range(1, 6)), 12))

    def test_short_level_and_missing_level(self):
        rows = [row for row in self.rows if row["level"] != 5
                and not (row["level"] == 2 and int(row["unique_id"].split("-")[1].split(".")[0]) >= 2)]
        manifest = build_manifest(self.config, rows)
        self.assertIn("short_level:2:2", manifest["flags"])
        self.assertIn("short_level:5:0", manifest["flags"])
        self.assertEqual(manifest["level_counts"]["2"], 2)
        self.assertEqual(sum(item["energy_subset"] for item in manifest["items"]), 11)
        self.assertEqual([item["order"] for item in manifest["items"]], list(range(38)))

    def test_rendered_prompt_reuses_importer(self):
        item = build_manifest(self.config, self.rows)["items"][0]
        for thinking in (False, True):
            self.assertEqual(rendered_prompt(item, thinking), _expected_rendered_prompt(item["problem"], thinking))
        self.assertIn("Please reason step by step", item["prompt"])


if __name__ == "__main__":
    unittest.main()
