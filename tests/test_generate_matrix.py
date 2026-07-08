from __future__ import annotations

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
COMMAND_TIMEOUT_S = 60
REPETITIONS = 5
ORDER_MANIFEST = "order_manifest.json"


def expected_filenames(model_tag: str) -> set[str]:
    return {
        f"{model_tag}-r{rep}-{profile}.json"
        for rep in range(1, REPETITIONS + 1)
        for profile in PROFILE_EXPECTED
    }


def expected_json_filenames(model_tag: str) -> set[str]:
    return expected_filenames(model_tag) | {ORDER_MANIFEST}


def run_generator(base: Path, model_tag: str, out_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--base",
            str(base),
            "--model-tag",
            model_tag,
            "--out-dir",
            str(out_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=COMMAND_TIMEOUT_S,
    )


def generated_payloads(out_dir: Path) -> dict[str, dict]:
    return {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(out_dir.glob("*.json"))
        if path.name != ORDER_MANIFEST
    }


def order_manifest(out_dir: Path) -> dict:
    return json.loads((out_dir / ORDER_MANIFEST).read_text(encoding="utf-8"))


class GenerateMatrixTests(unittest.TestCase):
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
                expected_filenames(other_tag) | expected_filenames(tag) | {ORDER_MANIFEST},
            )

    def test_both_example_base_configs_produce_forty_distinct_run_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            for base, tag in BASE_CONFIGS:
                result = run_generator(base, tag, out_dir)
                self.assertEqual(result.returncode, 0, result.stderr)

            payloads = generated_payloads(out_dir)
            run_ids = [payload["run_id"] for payload in payloads.values()]
            self.assertEqual(len(payloads), 40)
            self.assertEqual(len(set(run_ids)), 40)

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
                if path.name == ORDER_MANIFEST:
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
            self.assertEqual(len(order), 40)
            self.assertEqual(order[0]["rep"], 1)
            self.assertEqual(order[0]["model_tag"], tag_a)
            self.assertEqual(order[0]["workload"], "short_short")
            self.assertEqual(order[4]["model_tag"], tag_b)
            self.assertEqual(order[8]["rep"], 2)
            self.assertEqual(order[8]["model_tag"], tag_b)
            self.assertEqual(order[8]["workload"], "long_short")

    def test_invalid_model_tag_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(BASE_CONFIGS[0][0], "Qwen.25", out_dir)

            self.assertEqual(result.returncode, 2)
            self.assertIn("--model-tag must match", result.stderr)
            self.assertFalse(out_dir.exists())


if __name__ == "__main__":
    unittest.main()
