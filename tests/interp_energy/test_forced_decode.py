"""Stdlib-only loop, provenance and CLI refusals; all inputs are synthetic."""

import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from joulewise.interp_energy.forced_decode import (
    canonical_sha256, replay, token_ids, token_sequence_sha256, weight_file_identity,
)

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/interp_energy/forced_decode.py"


class Vector:
    shape = (11,)


class Cache:
    def __init__(self):
        self.offset = 0


class Model:
    def __init__(self):
        self.caches = []
        self.calls = []
        self.eval_called = False

    def eval(self):
        self.eval_called = True


class Backend:
    name = "synthetic-stdlib"

    def prepare(self, model):
        assert model.eval_called

    def make_cache(self, model):
        cache = [Cache()]
        model.caches.append(cache)
        return cache

    def prefill(self, model, inputs, cache):
        model.calls.append(("prefill", list(inputs), cache[0].offset))
        cache[0].offset += len(inputs)

    def forward(self, model, inputs, cache):
        model.calls.append(("decode", list(inputs), cache[0].offset))
        cache[0].offset += len(inputs)
        return Vector()

    def diagnostics(self, logits, forced, top_k):
        return {"argmax_token_id": 0, "forced_token_logprob": -3.0,
                "top_k": [{"token_id": i, "logprob": -2.0 - i} for i in range(top_k)]}


class ReplayTests(unittest.TestCase):
    def run_replay(self, model=None, **kwargs):
        params = dict(model_weights_sha256="a" * 64, vocab_size=11,
                      backend=Backend(), clock_ns=iter(range(100, 10000, 10)).__next__)
        params.update(kwargs)
        return replay(model if model is not None else Model(), [1, 2, 3, 4, 5], [0, 8, 0], **params)

    def test_prefill_then_single_token_steps_and_last_token_lag(self):
        model = Model()
        result = self.run_replay(model, prefill_chunk_size=2)
        self.assertEqual(model.calls, [
            ("prefill", [1, 2], 0), ("prefill", [3, 4], 2),
            ("decode", [5], 4), ("decode", [0], 5), ("decode", [8], 6),
        ])
        self.assertEqual(model.caches[0][0].offset, 7)
        self.assertEqual(result.summary["cache_input_token_count"], 7)
        self.assertEqual([r["context_tokens"] for r in result.tokens], [5, 6, 7])
        self.assertEqual([r["argmax_agrees"] for r in result.tokens], [True, False, True])
        self.assertEqual([r["forced_in_top_k"] for r in result.tokens], [True, False, True])

    def test_fresh_cache_each_arm_and_no_sampling_or_eos_stop(self):
        model = Model()
        a = self.run_replay(model)
        b = self.run_replay(model, model_weights_sha256="b" * 64)
        self.assertIsNot(model.caches[0][0], model.caches[1][0])
        self.assertEqual(model.calls[:4], model.calls[4:])
        self.assertEqual(len(a.tokens), 3)  # token 0 is deliberately in the middle
        for key in ("prompt_sha256", "token_sequence_sha256", "replay_policy_sha256"):
            self.assertEqual(a.metadata[key], b.metadata[key])
        self.assertNotEqual(a.metadata["model_weights_sha256"], b.metadata["model_weights_sha256"])

    def test_single_prompt_token_has_no_prefill(self):
        model = Model()
        replay(model, [2], [0], backend=Backend(), vocab_size=11, model_weights_sha256="a" * 64)
        self.assertEqual(model.calls, [("decode", [2], 0)])

    def test_timestamp_boundaries_jsonl_and_completion_marker(self):
        result = self.run_replay()
        self.assertEqual(result.summary["prefill_started_ns"], 100)
        self.assertEqual(result.summary["prefill_finished_ns"], 110)
        for i, row in enumerate(result.tokens):
            self.assertEqual(row["forward_started_ns"], 120 + 30 * i)
            self.assertEqual(row["forward_finished_ns"], 130 + 30 * i)
            self.assertEqual(row["diagnostics_finished_ns"], 140 + 30 * i)
            self.assertEqual(row["forward_duration_ns"], 10)
        output = io.StringIO()
        result.write_jsonl(output)
        records = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([r["record_type"] for r in records], ["replay", "token", "token", "token", "complete"])
        for record in records:
            self.assertEqual(record["token_sequence_sha256"], token_sequence_sha256([0, 8, 0]))
        self.assertEqual(records[-1]["argmax_agreement_count"], 2)

    def test_invalid_settings_fail_before_model_or_cache_work(self):
        for change in ({"vocab_size": 5}, {"vocab_size": True}, {"top_k": 0},
                       {"top_k": 1.5}, {"prefill_chunk_size": -1},
                       {"model_weights_sha256": "not-a-hash"}):
            with self.subTest(change=change):
                model = Model()
                with self.assertRaises(ValueError):
                    self.run_replay(model, **change)
                self.assertFalse(model.caches)
                self.assertFalse(model.eval_called)

    def test_invalid_sequences(self):
        for values in ([], [-1], [2**31], [1.0], ["1"], [True]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                token_ids(values)

    def test_top_k_clamped_to_vocabulary_and_policy_hash_changes(self):
        a = self.run_replay(top_k=20)
        b = self.run_replay(top_k=5)
        self.assertEqual(len(a.tokens[0]["top_k"]), 11)
        self.assertNotEqual(a.metadata["replay_policy_sha256"], b.metadata["replay_policy_sha256"])

    def test_clock_regression_is_rejected_between_steps_and_in_prefill(self):
        for times in ([100, 99], [100, 110, 120, 130, 140, 139, 150, 160]):
            with self.subTest(times=times), self.assertRaisesRegex(ValueError, "nondecreasing"):
                self.run_replay(clock_ns=iter(times).__next__)

    def test_shape_mismatch_and_nonfinite_diagnostics_refused(self):
        class WrongShape(Backend):
            def forward(self, model, inputs, cache):
                value = Vector()
                value.shape = (12,)
                return value
        class NonFinite(Backend):
            def diagnostics(self, *args):
                result = super().diagnostics(*args)
                result["forced_token_logprob"] = float("nan")
                return result
        for backend in (WrongShape(), NonFinite()):
            with self.subTest(backend=type(backend).__name__), self.assertRaises(ValueError):
                self.run_replay(backend=backend)

    def test_import_with_no_site_packages_does_not_import_optional_runtimes(self):
        code = (
            "import sys; import joulewise.interp_energy.forced_decode; "
            "import joulewise.interp_energy.reference; "
            "assert not any(n.split('.')[0] in {'numpy','mlx','mlx_lm'} for n in sys.modules)"
        )
        result = subprocess.run([sys.executable, "-B", "-S", "-c", code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_token_hash_is_canonical_and_order_sensitive(self):
        self.assertEqual(token_sequence_sha256([1, 2]), hashlib.sha256(b"[1,2]").hexdigest())
        self.assertNotEqual(token_sequence_sha256([1, 2]), token_sequence_sha256([2, 1]))

    def test_local_weight_manifest_tracks_bytes_and_file_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                weight_file_identity(root)
            (root / "b.safetensors").write_bytes(b"synthetic b")
            (root / "a.safetensors").write_bytes(b"synthetic a")
            a = weight_file_identity(root)
            self.assertEqual([f["name"] for f in a["files"]], ["a.safetensors", "b.safetensors"])
            self.assertEqual(a["sha256"], canonical_sha256(a["files"]))
            (root / "a.safetensors").write_bytes(b"synthetic edit")
            b = weight_file_identity(root)
            self.assertNotEqual(a["sha256"], b["sha256"])
            (root / "b.safetensors").rename(root / "c.safetensors")
            self.assertNotEqual(b["sha256"], weight_file_identity(root)["sha256"])

    def test_cli_refuses_hub_id_before_importing_or_loading_native_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            tokens = Path(tmp) / "tokens.json"
            tokens.write_text("[1,2]")
            result = subprocess.run([
                sys.executable, "-B", str(CLI), "--model", str(Path(tmp) / "missing-model"),
                "--tokens", str(tokens), "--prompt-tokens", str(tokens),
            ], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stderr)["error_type"], "FileNotFoundError")
            self.assertEqual(result.stdout, "")

    def test_cli_native_ingress_with_fake_loader_is_local_only(self):
        # Protocol/ingress evidence only: no MLX or native execution is claimed.
        from scripts.interp_energy import forced_decode as cli
        utils = ModuleType("mlx_lm.utils")
        seen = {}
        def encode(text, **kwargs):
            seen["encode"] = (text, kwargs)
            return [2]
        def load(path, **kwargs):
            seen["load"] = (path, kwargs)
            seen["offline"] = (os.environ.get("HF_HUB_OFFLINE"), os.environ.get("TRANSFORMERS_OFFLINE"))
            return Model(), SimpleNamespace(encode=encode), {"text_config": {"vocab_size": 11}}
        utils.load = load
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "model.safetensors").write_bytes(b"synthetic fake-loader artifact")
            (root / "config.json").write_text('{"text_config":{"vocab_size":11}}')
            tokens = root / "tokens.json"
            tokens.write_text("[0,8]")
            output = root / "output.jsonl"
            with patch.dict(sys.modules, {"mlx_lm": ModuleType("mlx_lm"), "mlx_lm.utils": utils}), \
                 patch.object(cli, "MLXBackend", return_value=Backend()), patch.dict(os.environ):
                code = cli.main(["--model", str(root), "--tokens", str(tokens),
                                 "--prompt", "synthetic", "--output", str(output)])
            self.assertEqual(code, 0)
            self.assertEqual(seen["load"], (str(root.resolve()), {
                "tokenizer_config": {"local_files_only": True}, "return_config": True,
            }))
            self.assertEqual(seen["offline"], ("1", "1"))
            self.assertEqual(seen["encode"], ("synthetic", {"add_special_tokens": False}))
            records = [json.loads(s) for s in output.read_text().splitlines()]
            self.assertFalse(records[0]["dry_run"])
            self.assertEqual(records[0]["model_weights_sha256"], weight_file_identity(root)["sha256"])
            self.assertEqual(records[0]["prompt_tokens"], [2])
            self.assertEqual(records[-1]["token_count"], 2)


if __name__ == "__main__":
    unittest.main()
