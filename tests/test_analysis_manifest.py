from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.analysis_manifest import calculate_manifest_id, validate_analysis_manifest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_matrix.py"
BASE_CONFIGS = (
    (ROOT / "configs" / "examples" / "mac_mlx_local.json", "qwen25-1p5b"),
    (ROOT / "configs" / "examples" / "mac_mlx_qwen35_122b.json", "qwen35-122b"),
)
METRIC_TAGS = ("gross_request", "idle_request", "gross_prefill", "gross_decode")
PAIRS = (
    ("short_short", "long_short"),
    ("short_short", "short_long"),
    ("short_short", "mid_mid"),
    ("long_short", "short_long"),
    ("long_short", "mid_mid"),
    ("short_long", "mid_mid"),
)


def run_generator(base: Path, tag: str, out_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--base",
            str(base),
            "--model-tag",
            tag,
            "--out-dir",
            str(out_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )


def load_manifest(out_dir: Path) -> dict:
    return json.loads((out_dir / "analysis_manifest.json").read_text(encoding="utf-8"))


def reidentify(manifest: dict) -> None:
    manifest["manifest_id"] = calculate_manifest_id(manifest)


class AnalysisManifestTests(unittest.TestCase):
    def test_one_and_two_model_shape_and_entry_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            first = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(first.returncode, 0, first.stderr)
            one = load_manifest(out_dir)

            self.assertEqual(one["schema_version"], "joulewise.analysis_manifest.v1")
            self.assertEqual(one["freeze_status"], "frozen")
            self.assertEqual(
                (len(one["entries"]), len(one["sentinel_links"]), len(one["families"]), len(one["contrasts"])),
                (30, 5, 4, 24),
            )
            for entry in one["entries"]:
                self.assertIsInstance(entry["cell_id"], str)
                self.assertIsInstance(entry["block_id"], str)
                self.assertIsInstance(entry["condition_id"], str)

            second = run_generator(*BASE_CONFIGS[1], out_dir)
            self.assertEqual(second.returncode, 0, second.stderr)
            two = load_manifest(out_dir)
            self.assertEqual(
                (len(two["entries"]), len(two["sentinel_links"]), len(two["families"]), len(two["contrasts"])),
                (60, 10, 8, 48),
            )
            self.assertEqual(validate_analysis_manifest(two, manifest_dir=out_dir), [])

    def test_exact_one_model_contrast_enumeration_matches_hand_built_cross_product(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            tag = BASE_CONFIGS[0][1]
            expected = [
                f"ctr-ap2-{tag}-{metric_tag}-{condition_b}-minus-{condition_a}"
                for metric_tag in METRIC_TAGS
                for condition_a, condition_b in PAIRS
            ]

            manifest = load_manifest(out_dir)

            self.assertEqual([row["contrast_id"] for row in manifest["contrasts"]], expected)
            self.assertEqual(
                [contrast_id for family in manifest["families"] for contrast_id in family["contrast_ids"]],
                expected,
            )

    def test_sentinel_and_family_linkage_invariants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = load_manifest(out_dir)
            entries = {entry["entry_id"]: entry for entry in manifest["entries"]}

            for link in manifest["sentinel_links"]:
                start = entries[link["start_entry_id"]]
                end = entries[link["end_entry_id"]]
                linked = [entries[entry_id] for entry_id in link["linked_condition_entry_ids"]]
                self.assertEqual(start["role"], "drift_sentinel_start")
                self.assertEqual(end["role"], "drift_sentinel_end")
                self.assertEqual(start["block_id"], link["block_id"])
                self.assertEqual(end["block_id"], link["block_id"])
                self.assertEqual(
                    [entry["condition_id"] for entry in linked],
                    ["cond-2m-short_short", "cond-2m-long_short", "cond-2m-short_long", "cond-2m-mid_mid"],
                )
                self.assertTrue(all(entry["block_id"] == link["block_id"] for entry in linked))
            for family in manifest["families"]:
                self.assertEqual(family["multiplicity"]["m"], len(family["contrast_ids"]))
                self.assertEqual(family["multiplicity"]["m"], 6)

    def test_analysis_manifest_bytes_are_identical_across_double_run_and_reverse_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            forward = tmp_path / "forward"
            reverse = tmp_path / "reverse"
            for base, tag in BASE_CONFIGS:
                result = run_generator(base, tag, forward)
                self.assertEqual(result.returncode, 0, result.stderr)
            first_bytes = (forward / "analysis_manifest.json").read_bytes()
            rerun = run_generator(*BASE_CONFIGS[1], forward)
            self.assertEqual(rerun.returncode, 0, rerun.stderr)
            self.assertEqual((forward / "analysis_manifest.json").read_bytes(), first_bytes)
            for base, tag in reversed(BASE_CONFIGS):
                result = run_generator(base, tag, reverse)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((reverse / "analysis_manifest.json").read_bytes(), first_bytes)

    def test_semantic_block_ids_do_not_follow_mutable_numeric_block_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            first = run_generator(*BASE_CONFIGS[1], out_dir)
            self.assertEqual(first.returncode, 0, first.stderr)
            one = load_manifest(out_dir)
            tag = BASE_CONFIGS[1][1]
            before = {
                entry["run_id"]: entry["block_id"]
                for entry in one["entries"]
                if entry["model_tag"] == tag
            }
            second = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(second.returncode, 0, second.stderr)
            two = load_manifest(out_dir)
            after = {
                entry["run_id"]: entry["block_id"]
                for entry in two["entries"]
                if entry["model_tag"] == tag
            }
            self.assertEqual(after, before)

    def test_validation_rejects_dropped_cell_id_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            mutated = copy.deepcopy(load_manifest(out_dir))
            del mutated["entries"][0]["cell_id"]
            reidentify(mutated)

            errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)

            self.assertTrue(any("missing key(s): cell_id" in error for error in errors), errors)

    def test_validation_rejects_duplicated_contrast_id_across_families_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            mutated = copy.deepcopy(load_manifest(out_dir))
            mutated["families"][1]["contrast_ids"][0] = mutated["families"][0]["contrast_ids"][0]
            reidentify(mutated)

            errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)

            self.assertTrue(any("appears in more than one family" in error for error in errors), errors)

    def test_validation_rejects_cross_block_end_sentinel_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            mutated = copy.deepcopy(load_manifest(out_dir))
            mutated["sentinel_links"][0]["end_entry_id"] = mutated["sentinel_links"][1]["end_entry_id"]
            reidentify(mutated)

            errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)

            self.assertTrue(any("does not link this block's end sentinel" in error for error in errors), errors)

    def test_validation_rejects_removed_contrast_with_frozen_m(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            mutated = copy.deepcopy(load_manifest(out_dir))
            del mutated["families"][0]["contrast_ids"][0]
            reidentify(mutated)

            errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)

            self.assertTrue(any("does not equal contrast_ids length" in error for error in errors), errors)

    def test_validation_rejects_non_frozen_status_and_ap_snapshot_mutations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = load_manifest(out_dir)
            mutations = (
                ("freeze", lambda value: value.__setitem__("freeze_status", "draft"), "must be 'frozen'"),
                (
                    "ap_hash",
                    lambda value: value["source"]["ap_rows"][0].__setitem__("section_sha256", "0" * 64),
                    "AP snapshot mismatch",
                ),
            )
            for name, mutate, expected in mutations:
                with self.subTest(name=name):
                    mutated = copy.deepcopy(manifest)
                    mutate(mutated)
                    reidentify(mutated)
                    errors = validate_analysis_manifest(mutated, manifest_dir=out_dir)
                    self.assertTrue(any(expected in error for error in errors), errors)

    def test_validation_rejects_tampered_config_and_order_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(*BASE_CONFIGS[0], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = load_manifest(out_dir)
            config_path = out_dir / manifest["entries"][0]["config"]
            config_path.write_bytes(config_path.read_bytes() + b" ")
            errors = validate_analysis_manifest(manifest, manifest_dir=out_dir)
            self.assertTrue(any("does not match config bytes" in error for error in errors), errors)

            config_path.write_bytes(config_path.read_bytes()[:-1])
            order_path = out_dir / "order_manifest.json"
            order_path.write_bytes(order_path.read_bytes() + b" ")
            errors = validate_analysis_manifest(manifest, manifest_dir=out_dir)
            self.assertTrue(any("order_manifest.sha256: source hash mismatch" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
