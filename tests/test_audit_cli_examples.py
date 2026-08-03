from __future__ import annotations

import io
import json
import shlex
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from joulewise.adapters import resolve_runtime, resolve_telemetry, resolve_transport
from joulewise.adapters.node_client import NodeWorkerClient
from joulewise.cli import main
from joulewise.clock import FakeClock
from joulewise.kv_size import KVSizeError, bytes_per_token, extract_kv_params
from joulewise.schemas import BenchmarkConfig

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"


def config_from_example(path: Path = EXAMPLE_CONFIG, **overrides) -> BenchmarkConfig:
    data = json.loads(path.read_text())
    data.update(overrides)
    return BenchmarkConfig.from_mapping(data)


class CliCoverageGapTests(unittest.TestCase):
    def test_example_backend_resolution_is_structured(self) -> None:
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as tmpdir:
            retention_root = Path(tmpdir) / "node-custody"
            client_index = 0

            def node_client_factory(*args: Any, **kwargs: Any) -> NodeWorkerClient:
                nonlocal client_index
                client_index += 1
                return NodeWorkerClient(
                    *args,
                    retention_root=(
                        retention_root / f"client-{client_index:03d}"
                    ),
                    **kwargs,
                )

            with patch(
                "joulewise.adapters.node_client.NodeWorkerClient",
                new=node_client_factory,
            ):
                for path in sorted((ROOT / "configs" / "examples").glob("*.json")):
                    config = config_from_example(path)
                    with self.subTest(config=path.name, adapter="runtime"):
                        adapter, failure = resolve_runtime(config, clock)
                        self.assertEqual((adapter is None) + (failure is None), 1)
                    with self.subTest(config=path.name, adapter="telemetry"):
                        adapter, failure = resolve_telemetry(config, clock)
                        self.assertEqual((adapter is None) + (failure is None), 1)
                    with self.subTest(config=path.name, adapter="transport"):
                        adapter, failure = resolve_transport(config)
                        self.assertEqual((adapter is None) + (failure is None), 1)

    def test_schema_output_options_write_json_and_stdout_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            for command, title in (
                ("print-config-schema", "JouleWise BenchmarkConfig"),
                ("print-output-schema", "JouleWise SummaryMetrics"),
            ):
                output = Path(tmpdir) / f"{command}.json"
                stdout = io.StringIO()
                with self.subTest(command=command):
                    with redirect_stdout(stdout):
                        exit_code = main([command, "--output", str(output)])
                    self.assertEqual(exit_code, 0)
                    self.assertIn("wrote", stdout.getvalue())
                    self.assertEqual(json.loads(output.read_text())["title"], title)

    def test_validate_config_rejects_non_json_path_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.yaml"
            path.write_text("schema_version: '0.1'\n")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main(["validate-config", str(path)])
        self.assertEqual(exit_code, 2)
        self.assertIn("JSON configs", stderr.getvalue())

    def test_kv_size_rejects_empty_zero_and_negative_prompt_lists(self) -> None:
        for tokens in ("", "0", "-1,4"):
            stderr = io.StringIO()
            with self.subTest(tokens=tokens):
                prompt_arg = f"--prompt-tokens={tokens}" if tokens.startswith("-") else "--prompt-tokens"
                argv = [
                    "kv-size",
                    "--layers",
                    "1",
                    "--kv-heads",
                    "1",
                    "--head-dim",
                    "1",
                ]
                if prompt_arg == "--prompt-tokens":
                    argv.extend([prompt_arg, tokens])
                else:
                    argv.append(prompt_arg)
                with redirect_stderr(stderr):
                    exit_code = main(argv)
                self.assertEqual(exit_code, 2)
                self.assertIn("--prompt-tokens", stderr.getvalue())

    def test_kv_size_config_json_must_be_object(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            path.write_text("[]\n")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main(["kv-size", str(path)])
        self.assertEqual(exit_code, 2)
        self.assertIn("config JSON must be an object", stderr.getvalue())

    def test_dtype_bytes_zero_and_negative_raise(self) -> None:
        for dtype_bytes in (0, -1):
            with self.subTest(dtype_bytes=dtype_bytes):
                with self.assertRaisesRegex(KVSizeError, "dtype_bytes"):
                    bytes_per_token(1, 1, 1, dtype_bytes=dtype_bytes)


class CliAndKVSizeBugPins(unittest.TestCase):
    # K1: invalid UTF-8 config bytes raise UnicodeDecodeError instead of clean exit 2.
    def test_invalid_utf8_config_exits_2_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad.json"
            path.write_bytes(b"\xff")
            stderr = io.StringIO()
            try:
                with redirect_stderr(stderr):
                    exit_code = main(["validate-config", str(path)])
            except UnicodeDecodeError as exc:
                self.fail(f"K1: raw UnicodeDecodeError instead of clean exit 2: {exc}")
            except Exception as exc:
                self.fail(f"K1: raw {type(exc).__name__} instead of clean exit 2")
        self.assertEqual(exit_code, 2)
        self.assertIn("error:", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    # K2: Falcon-style num_kv_heads is ignored in favor of num_attention_heads.
    def test_extracts_num_kv_heads_alias(self) -> None:
        params = extract_kv_params(
            {
                "num_hidden_layers": 1,
                "num_kv_heads": 2,
                "num_attention_heads": 8,
                "head_dim": 4,
            }
        )
        self.assertEqual(params.n_kv_heads, 2)

    # K3: multi_query=true without an explicit KV-head count should mean one KV head.
    def test_multi_query_true_uses_one_kv_head(self) -> None:
        params = extract_kv_params(
            {
                "num_hidden_layers": 1,
                "multi_query": True,
                "num_attention_heads": 8,
                "head_dim": 4,
            }
        )
        self.assertEqual(params.n_kv_heads, 1)

    # K4: non-divisible attention-head/KV-head grouping is accepted.
    def test_attention_heads_must_be_divisible_by_kv_heads(self) -> None:
        with self.assertRaisesRegex(KVSizeError, "divisible"):
            extract_kv_params(
                {
                    "num_hidden_layers": 1,
                    "num_key_value_heads": 5,
                    "num_attention_heads": 12,
                    "head_dim": 4,
                }
            )

    # K5: bundle result lines with spaces in the path are not whitespace-token round-trip safe.
    def test_bundle_line_with_space_path_is_parseable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            data = json.loads(EXAMPLE_CONFIG.read_text())
            data["run_id"] = "space-run"
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps(data))
            runs_dir = Path(tmpdir) / "jw runs"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["run", str(config_path), "--runs-dir", str(runs_dir)])
        self.assertEqual(exit_code, 0)
        line = stdout.getvalue().strip()
        tokens = shlex.split(line)
        self.assertGreaterEqual(len(tokens), 3, line)
        self.assertEqual(tokens[0], "bundle:")
        self.assertEqual(tokens[-1], "status=succeeded")
        self.assertEqual(tokens[1], str(runs_dir / "space-run"))

    # K6: kv-size emits human=<n> <unit> values with a space before the unit.
    def test_cli_kv_size_output_human_value_includes_unit_token(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["kv-size", "--layers", "1", "--kv-heads", "1", "--head-dim", "1024"])
        self.assertEqual(exit_code, 0)
        first_line = stdout.getvalue().splitlines()[0]
        self.assertRegex(
            first_line,
            r"^kv-size: .* bytes_per_token=4096 human=4 KiB$",
        )


if __name__ == "__main__":
    unittest.main()
