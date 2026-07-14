from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.schemas import BenchmarkConfig


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_matrix.py"
BASE_CONFIGS = (
    (ROOT / "configs" / "examples" / "mac_mlx_local.json", "qwen25-1p5b"),
    (ROOT / "configs" / "examples" / "mac_mlx_qwen35_122b.json", "qwen35-122b"),
)
PROFILE_EXPECTED = {
    "short_short": {"prompt_tokens": 128, "output_tokens": 64},
    "long_short": {"prompt_tokens": 4096, "output_tokens": 64},
    "short_long": {"prompt_tokens": 128, "output_tokens": 512},
    "mid_mid": {"prompt_tokens": 1024, "output_tokens": 256},
}
SENTINEL_PROFILE = "short_short_sentinel"
SENTINEL_POSITIONS = ("start", "end")
COMMAND_TIMEOUT_S = 60
REPETITIONS = 5
ORDER_MANIFEST = "order_manifest.json"
ANALYSIS_MANIFEST = "analysis_manifest.json"
MANIFEST_SIDECARS = {ORDER_MANIFEST, ANALYSIS_MANIFEST}


def expected_filenames(model_tag: str) -> set[str]:
    baseline = {
        f"{model_tag}-r{rep}-{profile}.json"
        for rep in range(1, REPETITIONS + 1)
        for profile in PROFILE_EXPECTED
    }
    sentinels = {
        f"{model_tag}-r{rep}-{SENTINEL_PROFILE}-{position}.json"
        for rep in range(1, REPETITIONS + 1)
        for position in SENTINEL_POSITIONS
    }
    return baseline | sentinels


def expected_baseline_filenames(model_tag: str) -> set[str]:
    return {
        f"{model_tag}-r{rep}-{profile}.json"
        for rep in range(1, REPETITIONS + 1)
        for profile in PROFILE_EXPECTED
    }


def expected_json_filenames(model_tag: str) -> set[str]:
    return expected_filenames(model_tag) | MANIFEST_SIDECARS


def run_generator(
    base: Path,
    model_tag: str,
    out_dir: Path,
    *,
    registry_path: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
            sys.executable,
            str(SCRIPT),
            "--base",
            str(base),
            "--model-tag",
            model_tag,
            "--out-dir",
            str(out_dir),
        ]
    if registry_path is not None:
        command.extend(["--analysis-registry", str(registry_path)])
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=COMMAND_TIMEOUT_S,
    )


def registry_with_n(path: Path, planned_n_blocks: int) -> Path:
    registry = json.loads(
        (ROOT / "configs" / "analysis_registry" / "slice_2m_ap2.v1.json").read_text(
            encoding="utf-8"
        )
    )
    registry["sampling_plan"]["planned_n_blocks"] = planned_n_blocks
    path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return path


def generated_payloads(out_dir: Path) -> dict[str, dict]:
    return {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(out_dir.glob("*.json"))
        if path.name not in MANIFEST_SIDECARS
    }


def order_manifest(out_dir: Path) -> dict:
    return json.loads((out_dir / ORDER_MANIFEST).read_text(encoding="utf-8"))


class GenerateMatrixTests(unittest.TestCase):
    def test_freeze_time_n_binding_round_trips_authorized_n10_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            registry_path = registry_with_n(tmp_path / "registry-n10.json", 10)
            out_dir = tmp_path / "out"

            result = run_generator(
                *BASE_CONFIGS[0],
                out_dir,
                registry_path=registry_path,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((out_dir / ANALYSIS_MANIFEST).read_text(encoding="utf-8"))
            self.assertEqual(manifest["design"]["sampling_plan"]["planned_n_blocks"], 10)
            self.assertEqual(len(manifest["contrasts"][0]["block_ids"]), 10)
            self.assertEqual(order_manifest(out_dir)["planned_n_blocks"], 10)
            self.assertEqual(
                manifest["source"]["registry_template"]["sha256"],
                hashlib.sha256(registry_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(len(generated_payloads(out_dir)), 60)

    def test_post_freeze_n_mutation_is_detected_before_output_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            registry_n5 = registry_with_n(tmp_path / "registry-n5.json", 5)
            registry_n10 = registry_with_n(tmp_path / "registry-n10.json", 10)
            out_dir = tmp_path / "out"
            base, tag = BASE_CONFIGS[0]
            first = run_generator(base, tag, out_dir, registry_path=registry_n5)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = {path.name: path.read_bytes() for path in out_dir.glob("*.json")}

            mutated = run_generator(base, tag, out_dir, registry_path=registry_n10)

            self.assertEqual(mutated.returncode, 1)
            self.assertIn("post-freeze n mutation detected", mutated.stderr)
            self.assertEqual(
                {path.name: path.read_bytes() for path in out_dir.glob("*.json")},
                before,
            )

    def test_mixed_n_inconsistent_block_authority_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            registry_n5 = registry_with_n(tmp_path / "registry-n5.json", 5)
            registry_n10 = registry_with_n(tmp_path / "registry-n10.json", 10)
            out_dir = tmp_path / "out"
            first = run_generator(*BASE_CONFIGS[0], out_dir, registry_path=registry_n5)
            self.assertEqual(first.returncode, 0, first.stderr)
            (out_dir / ANALYSIS_MANIFEST).unlink()
            (out_dir / ORDER_MANIFEST).unlink()
            before = {path.name: path.read_bytes() for path in out_dir.glob("*.json")}

            mixed = run_generator(*BASE_CONFIGS[1], out_dir, registry_path=registry_n10)

            self.assertEqual(mixed.returncode, 1)
            self.assertIn("mixed-n composition or incomplete block authority", mixed.stderr)
            self.assertEqual(
                {path.name: path.read_bytes() for path in out_dir.glob("*.json")},
                before,
            )

    def test_determinism_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_a = tmp_path / "a"
            out_b = tmp_path / "b"
            base, tag = BASE_CONFIGS[0]

            first = run_generator(base, tag, out_a)
            second = run_generator(base, tag, out_b)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            files_a = sorted(out_a.glob("*.json"))
            files_b = sorted(out_b.glob("*.json"))
            self.assertEqual({path.name for path in files_a}, expected_json_filenames(tag))
            self.assertEqual({path.name for path in files_b}, expected_json_filenames(tag))
            self.assertEqual([path.name for path in files_a], [path.name for path in files_b])
            for left, right in zip(files_a, files_b, strict=True):
                self.assertEqual(left.read_bytes(), right.read_bytes(), left.name)

    def test_reusing_out_dir_overwrites_expected_files_byte_identically(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            base, tag = BASE_CONFIGS[0]

            first = run_generator(base, tag, out_dir)
            self.assertEqual(first.returncode, 0, first.stderr)
            first_bytes = {
                path.name: path.read_bytes()
                for path in sorted(out_dir.glob("*.json"))
            }
            self.assertEqual(set(first_bytes), expected_json_filenames(tag))
            deleted_name = f"{tag}-r2-long_short.json"
            (out_dir / deleted_name).unlink()

            second = run_generator(base, tag, out_dir)
            second_bytes = {
                path.name: path.read_bytes()
                for path in sorted(out_dir.glob("*.json"))
            }

            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(set(second_bytes), expected_json_filenames(tag))
            self.assertEqual(second_bytes[deleted_name], first_bytes[deleted_name])

    def test_reusing_out_dir_with_stale_same_tag_file_refuses_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            base, tag = BASE_CONFIGS[0]

            first = run_generator(base, tag, out_dir)
            self.assertEqual(first.returncode, 0, first.stderr)
            expected_name = f"{tag}-r1-short_short.json"
            (out_dir / expected_name).write_text("corrupt expected file\n", encoding="utf-8")
            stale_name = f"{tag}-stale-profile.json"
            (out_dir / stale_name).write_text('{"stale": true}\n', encoding="utf-8")

            second = run_generator(base, tag, out_dir)

            self.assertEqual(second.returncode, 1)
            self.assertIn("stale same-tag JSON", second.stderr)
            self.assertIn(stale_name, second.stderr)
            self.assertEqual(
                (out_dir / expected_name).read_text(encoding="utf-8"),
                "corrupt expected file\n",
            )

    def test_reusing_out_dir_with_other_tag_files_keeps_working(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            base, tag = BASE_CONFIGS[0]
            other_tag = f"{tag}-variant"

            other = run_generator(base, other_tag, out_dir)
            current = run_generator(base, tag, out_dir)

            self.assertEqual(other.returncode, 0, other.stderr)
            self.assertEqual(current.returncode, 0, current.stderr)
            self.assertEqual(
                {path.name for path in out_dir.glob("*.json")},
                expected_filenames(other_tag) | expected_filenames(tag) | MANIFEST_SIDECARS,
            )

    def test_both_example_base_configs_produce_sixty_distinct_run_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            for base, tag in BASE_CONFIGS:
                result = run_generator(base, tag, out_dir)
                self.assertEqual(result.returncode, 0, result.stderr)

            payloads = generated_payloads(out_dir)
            run_ids = [payload["run_id"] for payload in payloads.values()]
            self.assertEqual(len(payloads), 60)
            self.assertEqual(len(set(run_ids)), 60)

    def test_matrix_cells_for_both_base_configs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for base, tag in BASE_CONFIGS:
                with self.subTest(base=base.name):
                    out_dir = tmp_path / tag
                    result = run_generator(base, tag, out_dir)
                    self.assertEqual(result.returncode, 0, result.stderr)

                    payloads = generated_payloads(out_dir)
                    self.assertEqual(
                        set(payloads),
                        expected_filenames(tag),
                    )
                    self.assertEqual(
                        {name for name in payloads if SENTINEL_PROFILE not in name},
                        expected_baseline_filenames(tag),
                    )
                    base_payload = json.loads(base.read_text(encoding="utf-8"))
                    for profile, expected in PROFILE_EXPECTED.items():
                        payload = payloads[f"{tag}-r1-{profile}.json"]
                        self.assertEqual(payload["run_id"], f"{tag}-r1-{profile}")
                        self.assertEqual(payload["model"], base_payload["model"])
                        workload = payload["workload_profile"]
                        self.assertEqual(workload["name"], profile)
                        self.assertEqual(workload["prompt_tokens"], expected["prompt_tokens"])
                        self.assertEqual(workload["output_tokens"], expected["output_tokens"])
                        self.assertEqual(workload["repetitions"], 1)
                        self.assertEqual(workload["warmup_runs"], 1)
                        self.assertNotIn("prompt_text", workload)
                        self.assertNotIn("dataset_ref", workload)
                        self.assertEqual(
                            payload["run_metadata"]["tags"],
                            base_payload["run_metadata"]["tags"] + ["2m", profile, "rep1"],
                        )
                    for position in SENTINEL_POSITIONS:
                        payload = payloads[f"{tag}-r1-{SENTINEL_PROFILE}-{position}.json"]
                        self.assertEqual(
                            payload["run_id"],
                            f"{tag}-r1-{SENTINEL_PROFILE}-{position}",
                        )
                        workload = payload["workload_profile"]
                        self.assertEqual(workload["name"], SENTINEL_PROFILE)
                        self.assertEqual(workload["prompt_tokens"], 128)
                        self.assertEqual(workload["output_tokens"], 64)
                        self.assertEqual(workload["repetitions"], 1)
                        self.assertEqual(workload["warmup_runs"], 1)

    def test_context_window_cap_records_tag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            base_payload = json.loads(BASE_CONFIGS[0][0].read_text(encoding="utf-8"))
            base_payload["model"]["context_window"] = 512
            base_path = tmp_path / "small-context.json"
            base_path.write_text(json.dumps(base_payload), encoding="utf-8")

            out_dir = tmp_path / "out"
            result = run_generator(base_path, "smallctx", out_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            long_short = json.loads((out_dir / "smallctx-r1-long_short.json").read_text(encoding="utf-8"))
            self.assertEqual(long_short["workload_profile"]["prompt_tokens"], 512)
            self.assertIn("prompt_capped_512", long_short["run_metadata"]["tags"])

    def test_every_emitted_config_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(BASE_CONFIGS[1][0], BASE_CONFIGS[1][1], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            paths = sorted(out_dir.glob("*.json"))
            self.assertEqual({path.name for path in paths}, expected_json_filenames(BASE_CONFIGS[1][1]))
            for path in paths:
                if path.name in MANIFEST_SIDECARS:
                    continue
                with self.subTest(path=path.name):
                    config = BenchmarkConfig.from_mapping(json.loads(path.read_text(encoding="utf-8")))
                    config.validate()

    def test_order_manifest_records_counterbalanced_execution_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            for base, tag in BASE_CONFIGS:
                result = run_generator(base, tag, out_dir)
                self.assertEqual(result.returncode, 0, result.stderr)

            manifest = order_manifest(out_dir)

            self.assertEqual(manifest["schema_version"], "joulewise.order_manifest.v1")
            self.assertEqual(manifest["seed"], 2000005)
            self.assertIn("seeded imbalance", manifest["imbalance_note"])
            self.assertEqual(
                manifest["rotation_scheme"]["rep_workload_order"]["1"],
                ["short_short", "long_short", "short_long", "mid_mid"],
            )
            self.assertEqual(
                manifest["rotation_scheme"]["rep_workload_order"]["2"],
                ["long_short", "short_long", "mid_mid", "short_short"],
            )
            tag_a, tag_b = sorted(tag for _, tag in BASE_CONFIGS)
            self.assertEqual(manifest["rotation_scheme"]["rep_model_order"]["1"], [tag_a, tag_b])
            self.assertEqual(manifest["rotation_scheme"]["rep_model_order"]["2"], [tag_b, tag_a])
            order = manifest["executed_order"]
            self.assertEqual(len(order), 60)
            self.assertEqual(order[0]["rep"], 1)
            self.assertEqual(order[0]["model_tag"], tag_a)
            self.assertEqual(order[0]["workload"], SENTINEL_PROFILE)
            self.assertEqual(order[0]["role"], "drift_sentinel")
            self.assertEqual(order[0]["block_index"], 1)
            self.assertEqual(order[0]["position_in_block"], 1)
            self.assertEqual(order[1]["workload"], "short_short")
            self.assertEqual(order[1]["block_index"], 1)
            self.assertEqual(order[1]["position_in_block"], 2)
            self.assertEqual(order[5]["workload"], SENTINEL_PROFILE)
            self.assertEqual(order[5]["role"], "drift_sentinel")
            self.assertEqual(order[5]["block_index"], 1)
            self.assertEqual(order[5]["position_in_block"], 6)
            self.assertEqual(order[6]["model_tag"], tag_b)
            self.assertEqual(order[6]["block_index"], 2)
            self.assertEqual(order[12]["rep"], 2)
            self.assertEqual(order[12]["model_tag"], tag_b)
            self.assertEqual(order[12]["workload"], SENTINEL_PROFILE)
            self.assertEqual(order[13]["workload"], "long_short")
            self.assertEqual(order[13]["block_index"], 3)
            self.assertEqual(order[13]["position_in_block"], 2)

            for entry in order:
                self.assertIn("block_index", entry)
                self.assertIn("position_in_block", entry)
                if entry["workload"] == SENTINEL_PROFILE:
                    self.assertEqual(entry["role"], "drift_sentinel")
                    self.assertIn(entry["position_in_block"], {1, 6})
                else:
                    self.assertNotIn("role", entry)

    def test_order_manifest_records_start_and_end_sentinel_identity_per_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            for base, tag in BASE_CONFIGS:
                result = run_generator(base, tag, out_dir)
                self.assertEqual(result.returncode, 0, result.stderr)

            order = order_manifest(out_dir)["executed_order"]
            block_indexes = sorted({entry["block_index"] for entry in order})

            for block_index in block_indexes:
                with self.subTest(block_index=block_index):
                    block = [entry for entry in order if entry["block_index"] == block_index]
                    self.assertEqual([entry["position_in_block"] for entry in block], [1, 2, 3, 4, 5, 6])
                    start = block[0]
                    end = block[-1]
                    self.assertEqual(start["role"], "drift_sentinel")
                    self.assertEqual(start["sentinel_position"], "start")
                    self.assertTrue(start["config"].endswith(f"-{SENTINEL_PROFILE}-start.json"))
                    self.assertTrue(start["run_id"].endswith(f"-{SENTINEL_PROFILE}-start"))
                    self.assertEqual(end["role"], "drift_sentinel")
                    self.assertEqual(end["sentinel_position"], "end")
                    self.assertTrue(end["config"].endswith(f"-{SENTINEL_PROFILE}-end.json"))
                    self.assertTrue(end["run_id"].endswith(f"-{SENTINEL_PROFILE}-end"))

    def test_order_manifest_has_complete_model_block_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            for base, tag in BASE_CONFIGS:
                result = run_generator(base, tag, out_dir)
                self.assertEqual(result.returncode, 0, result.stderr)

            order = order_manifest(out_dir)["executed_order"]
            expected_blocks = REPETITIONS * len(BASE_CONFIGS)

            self.assertEqual([entry["index"] for entry in order], list(range(1, len(order) + 1)))
            self.assertEqual(
                sorted({entry["block_index"] for entry in order}),
                list(range(1, expected_blocks + 1)),
            )
            for block_index in range(1, expected_blocks + 1):
                with self.subTest(block_index=block_index):
                    block = [entry for entry in order if entry["block_index"] == block_index]
                    self.assertEqual(len(block), 6)
                    self.assertEqual([entry["position_in_block"] for entry in block], [1, 2, 3, 4, 5, 6])
                    sentinel_entries = [
                        entry for entry in block if entry["workload"] == SENTINEL_PROFILE
                    ]
                    self.assertEqual(
                        [entry["sentinel_position"] for entry in sentinel_entries],
                        ["start", "end"],
                    )
                    self.assertEqual(
                        [entry["role"] for entry in sentinel_entries],
                        ["drift_sentinel", "drift_sentinel"],
                    )
                    self.assertEqual(
                        [entry["workload"] for entry in block[1:5]],
                        order_manifest(out_dir)["rotation_scheme"]["rep_workload_order"][str(block[0]["rep"])],
                    )

    def test_single_model_out_dir_manifest_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            base, tag = BASE_CONFIGS[0]

            result = run_generator(base, tag, out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)

            manifest = order_manifest(out_dir)
            order = manifest["executed_order"]
            self.assertEqual(len(order), REPETITIONS * 6)
            self.assertEqual(manifest["rotation_scheme"]["workloads"], list(PROFILE_EXPECTED))
            self.assertEqual(
                manifest["rotation_scheme"]["rep_model_order"],
                {str(rep): [tag] for rep in range(1, REPETITIONS + 1)},
            )
            self.assertEqual([entry["block_index"] for entry in order[:6]], [1] * 6)
            self.assertEqual(order[0]["sentinel_position"], "start")
            self.assertEqual(order[5]["sentinel_position"], "end")
            self.assertEqual({entry["model_tag"] for entry in order}, {tag})

    def test_sentinel_config_tags_include_role_and_position(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            base, tag = BASE_CONFIGS[0]

            result = run_generator(base, tag, out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)

            payloads = generated_payloads(out_dir)
            for position in SENTINEL_POSITIONS:
                with self.subTest(position=position):
                    payload = payloads[f"{tag}-r1-{SENTINEL_PROFILE}-{position}.json"]
                    tags = payload["run_metadata"]["tags"]
                    self.assertIn("drift_sentinel", tags)
                    self.assertIn(f"sentinel_{position}", tags)

    def test_manifest_builder_errors_when_existing_model_blocks_lack_sentinels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            base, old_tag = BASE_CONFIGS[0]
            _, new_tag = BASE_CONFIGS[1]

            old = run_generator(base, old_tag, out_dir)
            self.assertEqual(old.returncode, 0, old.stderr)
            for path in out_dir.glob(f"{old_tag}-r*-{SENTINEL_PROFILE}-*.json"):
                path.unlink()
            (out_dir / ORDER_MANIFEST).unlink()

            new = run_generator(base, new_tag, out_dir)

            self.assertEqual(new.returncode, 1)
            self.assertIn("mixed-n composition or incomplete block authority", new.stderr)
            self.assertIn(f"model_tag={old_tag}, rep=1", new.stderr)
            self.assertNotIn(f"model_tag={new_tag}, rep=1", new.stderr)

    def test_invalid_model_tag_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(BASE_CONFIGS[0][0], "Qwen.25", out_dir)

            self.assertEqual(result.returncode, 2)
            self.assertIn("--model-tag must match", result.stderr)
            self.assertFalse(out_dir.exists())


if __name__ == "__main__":
    unittest.main()
