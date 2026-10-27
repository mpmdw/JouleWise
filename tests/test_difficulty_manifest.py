"""v2 config (J), independently keyed selections (K), and real manifest CLI (S)."""
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from joulewise.benchmark_import_math import (
    _expected_rendered_prompt, eligible_records, select_items, select_pilot,
)
from joulewise.packs.difficulty.config import load_config, validate_config
from joulewise.packs.difficulty.manifest import build_manifest, rendered_prompt, selections_only

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/difficulty/pack_config.json"


def math_rows(count=30):
    return [{"unique_id": f"test/synthetic/{level}-{index}.json", "level": level,
             "subject": ("Algebra", "Geometry", "Prealgebra")[index % 3],
             "problem": f"Compute {level} + {index}.", "answer": str(level + index),
             "solution": f"\\boxed{{{level + index}}}", "source_file": "test.jsonl"}
            for level in range(1, 6) for index in range(count)]


class ConfigTests(unittest.TestCase):
    def test_J_invalid_configs(self):
        base = load_config(FIXTURE)
        cases = [({"confidence": .95}, "replaced in v2 by descriptive_confidence/decision_confidence and sizes"),
                 ({"energy_per_level": 20}, "replaced in v2"),
                 ({"schema_version": "difficulty_config.v1"}, "schema_version"),
                 ({"physical_exclude_flags": ["runtime_failed"]}, "physical_exclude_flags"),
                 ({"primary_comparison": {"a": "qwen3-1.7b/off", "b": "absent/off"}}, "primary_comparison.b")]
        for changes, message in cases:
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, message):
                validate_config(base | changes)
        changed = copy.deepcopy(base)
        changed["sizes"]["off"]["bench"]["1"] = 20
        changed["sizes"]["off"]["energy"]["1"] = 30
        with self.assertRaisesRegex(ValueError, "sizes.off"):
            validate_config(changed)
        changed = copy.deepcopy(base)
        del changed["configurations"][0]["status"]
        with self.assertRaisesRegex(ValueError, "status"):
            validate_config(changed)

    def test_no_number_changing_defaults_and_validation_edges(self):
        base = load_config(FIXTURE)
        for key in base:
            if key in ("schema_version", "version", "seed", "n_per_level", "sizes", "boundaries", "configurations",
                       "primary_comparison", "descriptive_confidence", "decision_confidence", "bootstrap",
                       "exclude_flags", "physical_exclude_flags", "loop_detector", "exclude_importer_sets", "exclude_item_id_files"):
                changed = copy.deepcopy(base)
                del changed[key]
                with self.subTest(missing=key), self.assertRaises(ValueError):
                    validate_config(changed)
        for key, values in (("n_per_level", [0, True, 1.0]), ("boundaries", [[], ["rails", "rails"], "rails"]),
                            ("decision_confidence", [.5, 1, True, "0.99", float("nan")]),
                            ("descriptive_confidence", [.5, 1]), ("exclude_flags", [None, [1]])):
            for value in values:
                with self.subTest(key=key, value=value), self.assertRaisesRegex(ValueError, key):
                    validate_config(base | {key: value})
        for key, value in (("tail_fraction", 0), ("tail_fraction", 1.1), ("min_span", 0), ("min_repeats", 1)):
            with self.subTest(loop=key), self.assertRaisesRegex(ValueError, key):
                validate_config(base | {"loop_detector": base["loop_detector"] | {key: value}})
        validate_config(base | {"decision_confidence": .95})


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(FIXTURE)
        self.config.update(n_per_level=12, exclude_importer_sets=False, exclude_item_id_files=[])
        self.config["sizes"] = {mode: {role: {str(l): value for l in range(1, 6)}
                                      for role, value in (("bench", n), ("energy", m))}
                                for mode, n, m in (("off", 12, 3), ("on", 8, 2))}
        self.rows = math_rows()

    def test_K_key_orders_nesting_sizes_and_subject_counts(self):
        config = load_config(FIXTURE) | {"exclude_importer_sets": False, "exclude_item_id_files": []}
        rows = math_rows(217)
        manifest = build_manifest(config, rows)
        eligible, _ = eligible_records(rows)
        domain = "joulewise.packs.difficulty.selection.v2/" + config["seed"]
        def order(ids, tag):
            return sorted(ids, key=lambda item: (hashlib.sha256((domain + "/" + tag + "/" + item).encode()).hexdigest(), item))
        for level in range(1, 6):
            ids = [row["source_item_id"] for row in eligible if row["level"] == level]
            selected = order(ids, "level")[:200]
            self.assertEqual([item["item_id"] for item in manifest["items"] if item["level"] == level], selected)
            for mode in ("off", "on"):
                bench = order(selected, f"bench/{mode}/{level}")[:config["sizes"][mode]["bench"][str(level)]]
                energy = order(bench, f"energy/{mode}/{level}")[:config["sizes"][mode]["energy"][str(level)]]
                self.assertEqual(manifest["selections"][mode]["bench"][str(level)], bench)
                self.assertEqual(manifest["selections"][mode]["energy"][str(level)], energy)
                self.assertTrue(set(energy) <= set(bench) <= set(selected))
                subjects = {item["item_id"]: item["subject"] for item in manifest["items"]}
                for role, subset in (("bench", bench), ("energy", energy), ("holdout", set(bench)-set(energy))):
                    self.assertEqual(manifest["subject_counts"][mode][role][str(level)], dict(Counter(subjects[i] for i in subset)))
        self.assertEqual(manifest, build_manifest(config, list(reversed(rows))))
        self.assertNotEqual(manifest["selections"], build_manifest(config | {"seed": "different"}, rows)["selections"])
        self.assertEqual(set(selections_only(manifest)), {"schema_version", "pack_version", "seed", "selection_domain", "sizes", "selections"})

    def test_K_uniformity_smoke(self):
        config = copy.deepcopy(self.config)
        config["n_per_level"] = 50
        for mode in ("off", "on"):
            for role, count in (("bench", 50), ("energy", 10)):
                config["sizes"][mode][role] = dict.fromkeys(map(str, range(1, 6)), count)
        counts = Counter()
        rows = math_rows(50)
        for seed in range(400):
            config["seed"] = str(seed)
            counts.update(build_manifest(config, rows)["selections"]["off"]["energy"]["1"])
        self.assertEqual(len(counts), 50)
        self.assertTrue(all(40 <= count <= 120 for count in counts.values()), counts)

    def test_round_robin_item_booleans_and_prompt(self):
        manifest = build_manifest(self.config, self.rows)
        for index, item in enumerate(manifest["items"]):
            self.assertEqual((item["order"], item["level"]), (index, index % 5 + 1))
            for mode in ("off", "on"):
                for role in ("bench", "energy"):
                    self.assertEqual(item[f"{role}_{mode}"], item["item_id"] in manifest["selections"][mode][role][str(item["level"])])
            for thinking in (False, True):
                self.assertEqual(rendered_prompt(item, thinking), _expected_rendered_prompt(item["problem"], thinking))
            self.assertIn("Please reason step by step", item["prompt"])

    def test_file_and_importer_exclusions(self):
        rows = math_rows(160)
        eligible, _ = eligible_records(rows)
        pilot = select_pilot(eligible)
        excluded = {row["source_item_id"] for row in pilot + select_items(eligible, pilot, 128)}
        manifest = build_manifest(self.config | {"exclude_importer_sets": True}, rows)
        self.assertTrue(excluded.isdisjoint(item["item_id"] for item in manifest["items"]))
        self.assertEqual(manifest["excluded_count"], 5 * (16 + 128))
        ids = [row["source_item_id"] for row in eligible[:8]]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exclude.txt"
            path.write_text("\n" + "\n".join(ids + [ids[0], "absent"]) + "\n")
            manifest = build_manifest(self.config | {"n_per_level": 160, "exclude_item_id_files": [str(path)]}, rows)
        self.assertTrue(set(ids).isdisjoint(item["item_id"] for item in manifest["items"]))
        self.assertEqual(manifest["excluded_count"], 8)

    def test_unreadable_exclusion_stops_build_and_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            for excluded in (path / "missing.txt", path):
                config = self.config | {"exclude_item_id_files": [str(excluded)]}
                with self.subTest(excluded=excluded), self.assertRaisesRegex(ValueError, "configured exclusion file"):
                    build_manifest(config, self.rows)
                (path / "config.json").write_text(json.dumps(config))
                result = subprocess.run([sys.executable, str(ROOT / "scripts/difficulty_manifest.py"),
                    "--config", str(path / "config.json"), "--out", str(path / "out/manifest.json")],
                    capture_output=True, text=True, env=os.environ.copy())
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(str(excluded), result.stderr)
                self.assertFalse((path / "out").exists())

    def test_K_short_and_missing_levels(self):
        rows = [row for row in self.rows if row["level"] != 5
                and not (row["level"] == 2 and int(row["unique_id"].split("-")[1].split(".")[0]) >= 2)]
        manifest = build_manifest(self.config, rows)
        self.assertIn("short_level:2:2", manifest["flags"])
        self.assertIn("short_level:5:0", manifest["flags"])
        for mode in ("off", "on"):
            self.assertIn(f"short_selection:{mode}:bench:2:2", manifest["flags"])
            self.assertIn(f"short_selection:{mode}:energy:5:0", manifest["flags"])
        self.assertEqual([item["order"] for item in manifest["items"]], list(range(38)))

    def test_S_real_math_manifest_cli(self):
        source = Path.home() / "jw_data/math-prm800k-7ecc7947"
        required = [source / name for name in ("prm_test.jsonl", "prm_train.jsonl", "ptr_test.txt", "ptr_train.txt", "prm_LICENSE")]
        if not all(path.is_file() for path in required):
            self.skipTest("real MATH importer files are absent")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            result = subprocess.run([sys.executable, str(ROOT / "scripts/difficulty_manifest.py"),
                "--config", str(FIXTURE), "--out", str(path / "manifest.json")],
                capture_output=True, text=True, env=os.environ.copy())
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((path / "manifest.json").read_text())
            self.assertEqual(manifest["level_counts"], dict.fromkeys(map(str, range(1, 6)), 200))
            self.assertFalse(any(flag.startswith("short_") for flag in manifest["flags"]))
            self.assertEqual(json.loads((path / "selections-difficulty-v2.json").read_text()), selections_only(manifest))
            for mode in ("off", "on"):
                for level in map(str, range(1, 6)):
                    bench, energy = (manifest["selections"][mode][role][level] for role in ("bench", "energy"))
                    self.assertTrue(set(energy) <= set(bench))
                    self.assertEqual(len(bench), 200 if mode == "off" else 64)
                    self.assertEqual(len(energy), (20 if int(level) < 3 else 40) if mode == "off" else 20)


if __name__ == "__main__":
    unittest.main()
