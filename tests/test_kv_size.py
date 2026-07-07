import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from joulewise.cli import main
from joulewise.kv_size import bytes_per_token, extract_kv_params, prompt_totals


class KVSizeTests(unittest.TestCase):
    def test_plan_table_anchor_rows(self) -> None:
        anchors = [
            (28, 2, 128, 28_672, 56, 224),
            (16, 8, 64, 32_768, 64, 256),
            (28, 4, 128, 57_344, 112, 448),
            (28, 8, 128, 114_688, 224, 896),
            (32, 8, 128, 131_072, 256, 1024),
        ]
        for layers, kv_heads, head_dim, expected_bpt, mib_2048, mib_8192 in anchors:
            with self.subTest(layers=layers, kv_heads=kv_heads, head_dim=head_dim):
                actual_bpt = bytes_per_token(layers, kv_heads, head_dim)
                self.assertEqual(actual_bpt, expected_bpt)
                self.assertEqual(actual_bpt // 1024, expected_bpt // 1024)
                totals = dict(prompt_totals(actual_bpt, [2048, 8192]))
                self.assertEqual(totals[2048], mib_2048 * 1024 * 1024)
                self.assertEqual(totals[8192], mib_8192 * 1024 * 1024)

    def test_extracts_nested_text_config(self) -> None:
        params = extract_kv_params(
            {"text_config": {"num_hidden_layers": 48, "num_key_value_heads": 2, "head_dim": 256}}
        )
        self.assertEqual(bytes_per_token(params.n_layers, params.n_kv_heads, params.head_dim), 98_304)

    def test_text_config_takes_precedence_over_top_level(self) -> None:
        params = extract_kv_params(
            {
                "num_hidden_layers": 12,
                "num_key_value_heads": 16,
                "head_dim": 64,
                "text_config": {
                    "num_hidden_layers": 48,
                    "num_key_value_heads": 2,
                    "head_dim": 256,
                },
            }
        )
        self.assertEqual((params.n_layers, params.n_kv_heads, params.head_dim), (48, 2, 256))

    def test_text_config_falls_back_to_top_level_for_missing_keys(self) -> None:
        params = extract_kv_params(
            {
                "head_dim": 128,
                "text_config": {"num_hidden_layers": 28, "num_key_value_heads": 2},
            }
        )
        self.assertEqual((params.n_layers, params.n_kv_heads, params.head_dim), (28, 2, 128))

    def test_non_divisible_hidden_size_raises(self) -> None:
        with self.assertRaises(ValueError):
            extract_kv_params(
                {
                    "num_hidden_layers": 28,
                    "num_key_value_heads": 2,
                    "num_attention_heads": 32,
                    "hidden_size": 4097,
                }
            )

    def test_derives_head_dim_when_absent_or_null(self) -> None:
        params = extract_kv_params(
            {
                "num_hidden_layers": 28,
                "num_key_value_heads": 2,
                "head_dim": None,
                "num_attention_heads": 12,
                "hidden_size": 1536,
            }
        )
        self.assertEqual(params.head_dim, 128)
        self.assertEqual(bytes_per_token(params.n_layers, params.n_kv_heads, params.head_dim), 28_672)

    def test_missing_kv_heads_falls_back_to_attention_heads(self) -> None:
        params = extract_kv_params(
            {"num_hidden_layers": 16, "num_attention_heads": 8, "head_dim": 64}
        )
        self.assertEqual(params.n_kv_heads, 8)
        self.assertEqual(bytes_per_token(params.n_layers, params.n_kv_heads, params.head_dim), 32_768)

    def test_cli_config_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "num_hidden_layers": 28,
                        "num_key_value_heads": 2,
                        "head_dim": None,
                        "num_attention_heads": 12,
                        "hidden_size": 1536,
                    }
                )
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["kv-size", str(config_path)])

        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn(
            "kv-size: layers=28 kv_heads=2 head_dim=128 dtype_bytes=2 "
            "bytes_per_token=28672 human=28 KiB",
            output,
        )
        self.assertIn(
            "kv-size-total: prompt_tokens=2048 bytes=58720256 human=56 MiB",
            output,
        )

    def test_cli_explicit_params(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["kv-size", "--layers", "32", "--kv-heads", "8", "--head-dim", "128"])

        self.assertEqual(exit_code, 0)
        self.assertIn("bytes_per_token=131072 human=128 KiB", stdout.getvalue())

    def test_cli_partial_explicit_params_exit_2(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = main(["kv-size", "--layers", "32", "--kv-heads", "8"])
        self.assertEqual(exit_code, 2)
        self.assertIn("error:", stderr.getvalue())

    def test_cli_bad_prompt_tokens_exit_2(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = main(
                ["kv-size", "--layers", "32", "--kv-heads", "8", "--head-dim", "128",
                 "--prompt-tokens", "a,b"]
            )
        self.assertEqual(exit_code, 2)
        self.assertIn("--prompt-tokens", stderr.getvalue())

    def test_bad_config_exits_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps({"hidden_size": 1536}))
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(["kv-size", str(config_path)])

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("error:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
