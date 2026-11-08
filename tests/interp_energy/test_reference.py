"""NumPy numerical reference and CLI dry-run tests; no model artifacts."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from joulewise.interp_energy.forced_decode import NumpyBackend, replay
from joulewise.interp_energy.reference import NumpyReferenceModel

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/interp_energy/forced_decode.py"


@unittest.skipUnless(importlib.util.find_spec("numpy") is not None, "optional NumPy unavailable")
class ReferenceTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np = np
        self.model = NumpyReferenceModel(seed=4)
        self.backend = NumpyBackend()

    def run_replay(self, model=None, **options):
        model = model if model is not None else self.model
        defaults = dict(backend=self.backend, vocab_size=model.vocab_size,
                        model_weights_sha256=model.weights_sha256(), top_k=4)
        defaults.update(options)
        return replay(model, [1, 2, 3, 4], [0, 7, 5, 8], **defaults)

    def test_cached_scores_match_independent_full_causal_forwards(self):
        for chunk in (1, 2, 512):
            with self.subTest(chunk=chunk):
                result = self.run_replay(prefill_chunk_size=chunk)
                context = [1, 2, 3, 4]
                for row in result.tokens:
                    logits = self.model(self.np.array([context]), cache=None)[0, -1]
                    expected = self.backend.diagnostics(logits, row["forced_token_id"], 4)
                    self.assertEqual(row["argmax_token_id"], expected["argmax_token_id"])
                    self.assertAlmostEqual(row["forced_token_logprob"], expected["forced_token_logprob"], places=6)
                    self.assertEqual([v["token_id"] for v in row["top_k"]], [v["token_id"] for v in expected["top_k"]])
                    context.append(row["forced_token_id"])

    def test_null_replay_is_identical_apart_from_timestamps(self):
        a, b = self.run_replay(), self.run_replay()
        for x, y in zip(a.tokens, b.tokens):
            for key in ("argmax_token_id", "argmax_agrees", "forced_token_logprob", "top_k",
                        "input_token_id", "forced_token_id", "context_tokens"):
                self.assertEqual(x[key], y[key])

    def test_edited_weights_change_scores_but_never_the_replayed_tokens(self):
        a = self.run_replay()
        self.model.weights["output"] *= -2
        b = self.run_replay()
        self.assertNotEqual(a.metadata["model_weights_sha256"], b.metadata["model_weights_sha256"])
        self.assertEqual(a.metadata["token_sequence_sha256"], b.metadata["token_sequence_sha256"])
        self.assertEqual(a.metadata["replay_policy_sha256"], b.metadata["replay_policy_sha256"])
        self.assertEqual([r["input_token_id"] for r in a.tokens], [r["input_token_id"] for r in b.tokens])
        self.assertTrue(any(x["forced_token_logprob"] != y["forced_token_logprob"] for x, y in zip(a.tokens, b.tokens)))

    def test_scores_use_full_vocabulary_normalizer_even_outside_top_k(self):
        logits = self.np.array([10000., 10000., 9999., -10000.])
        result = self.backend.diagnostics(logits, 3, 2)
        self.assertEqual(result["argmax_token_id"], 0)
        self.assertEqual([r["token_id"] for r in result["top_k"]], [0, 1])
        self.assertAlmostEqual(result["forced_token_logprob"], -20000 - self.np.log(2 + self.np.exp(-1)))

    def test_nonfinite_model_outputs_are_refused(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.backend.diagnostics(self.np.array([0., value]), 0, 1)

    def test_cache_state_grows_once_per_consumed_token(self):
        cache = self.model.make_cache()
        for ids in ([1, 2], [3], [4]):
            self.model(self.np.array([ids]), cache=cache)
        self.assertEqual(cache[0].offset, 4)
        self.assertEqual(cache[0].keys.shape, (1, 4, 8))
        self.assertEqual(cache[0].values.shape, (1, 4, 8))

    def test_synthetic_model_hash_is_reproducible(self):
        self.assertEqual(self.model.weights_sha256(), NumpyReferenceModel(seed=4).weights_sha256())
        self.assertNotEqual(self.model.weights_sha256(), NumpyReferenceModel(seed=5).weights_sha256())

    def test_cli_dry_run_fixed_inputs_and_exclusive_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "prompt.json").write_text("[2]")
            (root / "forced.json").write_text("[0,1,0]")
            output = root / "replay.jsonl"
            command = [sys.executable, "-B", str(CLI), "--dry-run", "--prompt-tokens", str(root / "prompt.json"),
                       "--tokens", str(root / "forced.json"), "--output", str(output)]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            original = output.read_bytes()
            rows = [json.loads(s) for s in original.splitlines()]
            self.assertTrue(rows[0]["dry_run"])
            self.assertEqual(rows[0]["prompt_tokens"], [2])
            self.assertEqual([r["forced_token_id"] for r in rows[1:-1]], [0, 1, 0])
            self.assertEqual(rows[-1]["record_type"], "complete")
            repeat = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(repeat.returncode, 2)
            self.assertEqual(json.loads(repeat.stderr)["error_type"], "FileExistsError")
            self.assertEqual(output.read_bytes(), original)

    def test_cli_rejects_malformed_token_file_without_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tokens = root / "bad.json"
            output = root / "out.jsonl"
            for data in ('{"tokens":[1]}', '[1.5]', '[true]', '[]', '[99]', 'not json'):
                with self.subTest(data=data):
                    tokens.write_text(data)
                    result = subprocess.run([
                        sys.executable, "-B", str(CLI), "--dry-run", "--tokens", str(tokens), "--output", str(output),
                    ], cwd=ROOT, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
