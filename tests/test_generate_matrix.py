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


def expected_filenames(model_tag: str) -> set[str]:
    return {f"{model_tag}-{profile}.json" for profile in PROFILE_EXPECTED}


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
    }


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
            self.assertEqual({path.name for path in files_a}, expected_filenames(tag))
            self.assertEqual({path.name for path in files_b}, expected_filenames(tag))
            self.assertEqual([path.name for path in files_a], [path.name for path in files_b])
            for left, right in zip(files_a, files_b, strict=True):
                self.assertEqual(left.read_bytes(), right.read_bytes(), left.name)

    def test_reusing_out_dir_overwrites_byte_identically(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            base, tag = BASE_CONFIGS[0]

            first = run_generator(base, tag, out_dir)
            self.assertEqual(first.returncode, 0, first.stderr)
            first_bytes = {
                path.name: path.read_bytes()
                for path in sorted(out_dir.glob("*.json"))
            }
            self.assertEqual(set(first_bytes), expected_filenames(tag))
            deleted_name = f"{tag}-long_short.json"
            (out_dir / deleted_name).unlink()
            stale_name = "stale-extra.json"
            (out_dir / stale_name).write_text('{"stale": true}\n', encoding="utf-8")

            second = run_generator(base, tag, out_dir)
            second_bytes = {
                path.name: path.read_bytes()
                for path in sorted(out_dir.glob("*.json"))
            }

            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(set(second_bytes), expected_filenames(tag) | {stale_name})
            self.assertEqual(second_bytes[deleted_name], first_bytes[deleted_name])
            self.assertEqual(second_bytes[stale_name], b'{"stale": true}\n')

    def test_both_example_base_configs_produce_eight_distinct_run_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            for base, tag in BASE_CONFIGS:
                result = run_generator(base, tag, out_dir)
                self.assertEqual(result.returncode, 0, result.stderr)

            payloads = generated_payloads(out_dir)
            run_ids = [payload["run_id"] for payload in payloads.values()]
            self.assertEqual(len(payloads), 8)
            self.assertEqual(len(set(run_ids)), 8)

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
                        payload = payloads[f"{tag}-{profile}.json"]
                        self.assertEqual(payload["run_id"], f"{tag}-{profile}")
                        self.assertEqual(payload["model"], base_payload["model"])
                        workload = payload["workload_profile"]
                        self.assertEqual(workload["name"], profile)
                        self.assertEqual(workload["prompt_tokens"], expected["prompt_tokens"])
                        self.assertEqual(workload["output_tokens"], expected["output_tokens"])
                        self.assertEqual(workload["repetitions"], 5)
                        self.assertEqual(workload["warmup_runs"], 1)
                        self.assertNotIn("prompt_text", workload)
                        self.assertNotIn("dataset_ref", workload)
                        self.assertEqual(
                            payload["run_metadata"]["tags"],
                            base_payload["run_metadata"]["tags"] + ["2m", profile],
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
            long_short = json.loads((out_dir / "smallctx-long_short.json").read_text(encoding="utf-8"))
            self.assertEqual(long_short["workload_profile"]["prompt_tokens"], 512)
            self.assertIn("prompt_capped_512", long_short["run_metadata"]["tags"])

    def test_every_emitted_config_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(BASE_CONFIGS[1][0], BASE_CONFIGS[1][1], out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            paths = sorted(out_dir.glob("*.json"))
            self.assertEqual({path.name for path in paths}, expected_filenames(BASE_CONFIGS[1][1]))
            for path in paths:
                with self.subTest(path=path.name):
                    config = BenchmarkConfig.from_mapping(json.loads(path.read_text(encoding="utf-8")))
                    config.validate()

    def test_invalid_model_tag_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            result = run_generator(BASE_CONFIGS[0][0], "Qwen.25", out_dir)

            self.assertEqual(result.returncode, 2)
            self.assertIn("--model-tag must match", result.stderr)
            self.assertFalse(out_dir.exists())


if __name__ == "__main__":
    unittest.main()
