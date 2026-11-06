"""No study inputs, no network, no whole-suite or large-checkpoint dependency."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.align.qwen4_gold.core import IndexedCheckpoint, TraceFile, compare_arrays, compare_exact, required_traces, write_json
from joulewise.align.qwen4_gold.runner import Harness, execute, load_prompts, parse_layers, reusable

HAS_ARRAYS = importlib.util.find_spec("numpy") is not None
HAS_SAFE = importlib.util.find_spec("safetensors") is not None


class PolicyTests(unittest.TestCase):
    def test_layers_and_required_coverage(self):
        c = {"layer_types": ["linear_attention", "full_attention"], "ple_layer_ids": [2]}
        self.assertEqual(parse_layers("1,0,1", 2), [0, 1])
        self.assertEqual(parse_layers("all", 2), [0, 1])
        with self.assertRaises(ValueError):
            parse_layers("2", 2)
        self.assertIn("attention.gated_norm", required_traces(c, "0"))
        self.assertIn("qsa.mask", required_traces(c, "1"))
        self.assertIn("ple.ngram_ids", required_traces(c, "1"))
        self.assertIn("final.norm", required_traces(c, "final"))

    def test_prompt_validation(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "prompts.json"
            write_json(path, [{"name": "../escape", "input_ids": [1]}])
            with self.assertRaises(ValueError):
                load_prompts(path, {"vocab_size": 2})
            write_json(path, [{"name": "ok", "input_ids": [2]}])
            with self.assertRaises(ValueError):
                load_prompts(path, {"vocab_size": 2})

    def test_memory_parent_budget_prevents_launch(self):
        with tempfile.TemporaryDirectory() as d:
            result = execute("never-run", {}, Path(d), 0.0001, 1)
            self.assertEqual(result["error"], "memory_guard_parent_budget")

    def test_live_mlx_peak_metadata_is_required(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            process = SimpleNamespace(returncode=0, pid=1, poll=lambda: 0)
            write_json(root / "result.json", {"metadata":{"adapter_kind":"mlx"}})
            with patch("joulewise.align.qwen4_gold.runner.subprocess.Popen", return_value=process):
                result = execute("fake", {}, root, 12, 1)
            self.assertEqual(result["error"], "invalid_mlx_memory_metadata")

    def test_resume_requires_artifact_integrity(self):
        from joulewise.align.qwen4_gold.core import sha256
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "report.json"
            array = Path(d) / "output.npy"
            array.write_bytes(b"test")
            write_json(path, {"fingerprint": "a", "reference_valid": True, "artifacts": {"output.npy": sha256(array)}})
            self.assertTrue(reusable(path, "a"))
            self.assertFalse(reusable(path, "b"))
            array.write_bytes(b"changed")
            self.assertFalse(reusable(path, "a"))


@unittest.skipUnless(HAS_ARRAYS, "optional NumPy")
class MetricTests(unittest.TestCase):
    def test_relative_and_cosine_gate(self):
        self.assertTrue(compare_arrays([1., 2.], [1., 2.], "fp32")["pass"])
        self.assertFalse(compare_arrays([1., 2.], [1., 3.], "fp32")["pass"])
        self.assertFalse(compare_arrays([0.001], [-0.001], "bf16")["pass"])

    def test_exact_expert_sets_ignore_order_but_detect_mutation(self):
        result = compare_arrays([[1, 4], [2, 3]], [[4, 1], [3, 2]], "bf16", exact=True)
        self.assertTrue(result["pass"])
        self.assertFalse(result["ordered_agreement"])
        self.assertFalse(compare_arrays([[1, 4]], [[1, 5]], "bf16", exact=True)["pass"])

    def test_streamed_file_metrics_check_later_chunks(self):
        import numpy as np
        with tempfile.TemporaryDirectory() as d:
            a = np.linspace(-1, 1, 300001, dtype=np.float32)
            path = Path(d) / "trace.npy"
            np.save(path, a)
            streamed = TraceFile(path)
            self.assertTrue(compare_arrays(streamed, a, "fp32")["pass"])
            self.assertTrue(compare_exact(streamed, a))
            a[-1] += 1
            self.assertFalse(compare_arrays(streamed, a, "fp32")["pass"])
            self.assertFalse(compare_exact(streamed, a))
            a[-1] = float("nan")
            self.assertEqual(compare_arrays(streamed, a, "fp32")["reason"], "nonfinite")

    def test_nan_empty_shape_and_zero(self):
        self.assertFalse(compare_arrays([float("nan")], [1], "fp32")["pass"])
        self.assertFalse(compare_arrays([], [], "fp32")["pass"])
        self.assertFalse(compare_arrays([1], [[1]], "fp32")["pass"])
        self.assertTrue(compare_arrays([0], [0], "fp32")["pass"])


@unittest.skipUnless(HAS_ARRAYS and HAS_SAFE, "optional NumPy and safetensors")
class SliceTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        from safetensors.numpy import save_file
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        save_file({"model.embed_tokens.weight": np.arange(24, dtype=np.float32).reshape(8,3),
                   "model.layers.0.mlp.experts.0.gate_proj.weight": np.ones((2,3), dtype=np.float32),
                   "model.layers.0.mlp.experts.0.up_proj.weight": np.full((2,3),2., dtype=np.float32),
                   "model.table.shard_0.weight": np.arange(6, dtype=np.float32).reshape(2,3),
                   "model.table.shard_1.weight": np.arange(6,12,dtype=np.float32).reshape(2,3)}, self.root / "model.safetensors")
        write_json(self.root / "config.json", {"vocab_size":8, "num_experts":1})
        self.checkpoint = IndexedCheckpoint(self.root)

    def test_unique_rows_and_no_full_table_load(self):
        import numpy as np
        rows = self.checkpoint.rows("model.embed_tokens.weight", [[3,1,3]])
        np.testing.assert_array_equal(rows, [[[9,10,11],[3,4,5],[9,10,11]]])
        self.assertEqual(len(self.checkpoint.reads), 2)
        with self.assertRaises(ValueError):
            self.checkpoint.read("model.embed_tokens.weight")
        with self.assertRaises(ValueError):
            self.checkpoint.rows("model.embed_tokens.weight", [-1])

    def test_sharded_ngram_numeric_order_and_shape(self):
        import numpy as np
        rows = self.checkpoint.ngram_rows("model.table", [[3,0,3]])
        np.testing.assert_array_equal(rows, [[[9,10,11],[0,1,2],[9,10,11]]])
        self.assertEqual(len(self.checkpoint.reads), 2)

    def test_save_pretrained_unpacked_experts(self):
        import numpy as np
        shape, _ = self.checkpoint.info("model.layers.0.mlp.experts.gate_up_proj")
        self.assertEqual(shape, (1,4,3))
        values = self.checkpoint.read("model.layers.0.mlp.experts.gate_up_proj", (0,slice(None),slice(None)))
        np.testing.assert_array_equal(values, [[1]*3]*2 + [[2]*3]*2)

    def test_large_tensor_slice_policy(self):
        self.checkpoint.weight_map["model.layers.0.mlp.experts.gate_up_proj"] = "model.safetensors"
        with patch.object(self.checkpoint, "info", return_value=((512,1280,2560), "BF16")):
            with self.assertRaisesRegex(ValueError, "one expert index"):
                self.checkpoint.read("model.layers.0.mlp.experts.gate_up_proj", (slice(None),slice(None),slice(None)))
        with patch.object(self.checkpoint, "info", return_value=((100000,2560), "BF16")):
            with self.assertRaisesRegex(ValueError, "1024 rows"):
                self.checkpoint.read("model.embed_tokens.weight", (slice(0,1025),slice(None)))

    def test_unused_missing_ngram_parts_do_not_get_opened(self):
        write_json(self.root / "model.safetensors.index.json", {"weight_map": {
            "model.embed_tokens.weight": "model.safetensors",
            "model.table.shard_0.weight": "model.safetensors",
            "model.table.shard_1.weight": "absent.safetensors"}})
        checkpoint = IndexedCheckpoint(self.root)
        self.assertEqual(checkpoint.ngram_rows("model.table", [0]).tolist(), [[0.,1.,2.]])

    def test_numeric_shard_order_beyond_ten(self):
        import numpy as np
        from safetensors.numpy import save_file
        values = {"model.embed_tokens.weight": np.ones((1,3), dtype=np.float32)}
        values.update({f"model.table.shard_{i}.weight": np.full((2,3), i, dtype=np.float32) for i in range(12)})
        save_file(values, self.root / "many.safetensors")
        write_json(self.root / "model.safetensors.index.json", {"weight_map": dict.fromkeys(values, "many.safetensors")})
        rows = IndexedCheckpoint(self.root).ngram_rows("model.table", [20,4])
        np.testing.assert_array_equal(rows, [[10]*3, [2]*3])

    def test_hashed_shard_stamp_refuses_replacement(self):
        from joulewise.align.qwen4_gold.core import file_stamp
        file = self.root / "model.safetensors"
        checkpoint = IndexedCheckpoint(self.root, {"model.safetensors":file_stamp(file)})
        self.assertEqual(checkpoint.rows("model.embed_tokens.weight", [0]).tolist(), [[0.,1.,2.]])
        with file.open("ab") as stream:
            stream.write(b"changed")
        with self.assertRaisesRegex(ValueError, "changed after hashing"):
            checkpoint.rows("model.embed_tokens.weight", [0])

    def test_index_traversal_and_symlinks_refuse(self):
        with self.assertRaises(ValueError):
            self.checkpoint.path("../outside")
        (self.root / "link.safetensors").symlink_to(self.root / "model.safetensors")
        with self.assertRaises(ValueError):
            self.checkpoint.path("link.safetensors")


@unittest.skipUnless(HAS_ARRAYS and HAS_SAFE and importlib.util.find_spec("torch"), "optional Torch")
class BF16Tests(unittest.TestCase):
    def test_raw_bf16_numpy_matches_torch_without_torch_in_mlx(self):
        import numpy as np
        import torch
        from safetensors.torch import save_file
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            values = torch.tensor([[1., -2., 0.], [1/3, 0.007, 123.456]], dtype=torch.bfloat16)
            save_file({"model.embed_tokens.weight": values}, root / "model.safetensors")
            write_json(root / "config.json", {"vocab_size":2})
            checkpoint = IndexedCheckpoint(root)
            np.testing.assert_array_equal(checkpoint.rows("model.embed_tokens.weight", [1,0]), values[[1,0]].float().numpy())

    def test_native_integer_buffers_preserve_all_bits(self):
        import torch
        from safetensors.torch import save_file
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            values = torch.tensor([2**61+3, -(2**61)+7], dtype=torch.int64)
            save_file({"model.embed_tokens.weight":torch.ones((1,2)), "model.hash": values}, root / "model.safetensors")
            write_json(root / "config.json", {"vocab_size":1})
            checkpoint = IndexedCheckpoint(root)
            self.assertTrue(torch.equal(values, checkpoint.read("model.hash", framework="torch", dtype="native")))

    def test_qsa_topk_ties_break_to_lowest_block_inside_indexer_only(self):
        import torch
        from joulewise.align.qwen4_gold.reference import deterministic_qsa_ties

        class Indexer(torch.nn.Module):
            def forward(self, scores, k):
                return scores.topk(k, dim=0).indices

        # Query 8 of the native tiny fp32 random case: three exact zeros.
        scores = torch.tensor([0., 0., 1.7015357, 0.])
        indexer, counts, seen = Indexer(), {"topk_calls": 0, "straddling_ties": 0}, []
        original = torch.Tensor.topk
        deterministic_qsa_ties(indexer, torch, counts)
        indexer.register_forward_hook(lambda m, a, o: seen.append(o))
        self.assertEqual(indexer(scores, 2).tolist(), [2, 0])
        self.assertEqual(indexer(torch.tensor([3., 1., 2.]), 2).tolist(), [0, 2])
        self.assertEqual(len(seen), 2)  # registered hooks still run
        self.assertEqual(counts, {"topk_calls": 2, "straddling_ties": 1})
        self.assertIs(torch.Tensor.topk, original)  # patched only inside the indexer forward


@unittest.skipUnless(HAS_ARRAYS, "optional NumPy")
class VerdictTests(unittest.TestCase):
    def test_stub_can_never_pass_and_missing_trace_refuses(self):
        import argparse
        import numpy as np
        import types
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            c = {"hidden_size":2, "hc_count":2}
            args = argparse.Namespace(output=str(root), dtypes="fp32", input_modes="real", seed=1,
                random_scale=1., mlx_module=str(Path(__file__).resolve()), adapter_dependency=[],
                ref_python="unused", mlx_python="unused", max_gb=12, timeout=1, resume=False)
            cp = types.SimpleNamespace(config=c, root=root, weight_map={})
            harness = Harness(args, cp, {}, [], {})
            def fake_run(python, request, directory, *a):
                directory.mkdir(parents=True, exist_ok=True)
                traces = {"output": "output.npy", "embedding": "embedding.npy"}
                for name in traces:
                    np.save(directory / traces[name], np.ones((1,1,2)))
                return {"traces": traces, "metadata": {"adapter_kind": "stub"}}
            prompt = {"name":"test", "input_ids":[1]}
            with patch("joulewise.align.qwen4_gold.runner.execute", fake_run):
                harness.case("embed", "fp32", prompt, "real", None)
            self.assertEqual(harness.rows["embed"][0]["status"], "STUB_NOT_VALIDATED")
            def missing(python, request, directory, *a):
                result = fake_run(python, request, directory)
                if request["backend"] == "mlx":
                    result["traces"].pop("embedding")
                    result["metadata"]["adapter_kind"] = "mlx"
                return result
            with patch("joulewise.align.qwen4_gold.runner.execute", missing):
                harness.case("embed", "fp32", prompt, "other", None)
            self.assertEqual(harness.rows["embed"][1]["status"], "FAIL")
            self.assertEqual(harness.rows["embed"][1]["missing_traces"], ["embedding"])


if __name__ == "__main__":
    unittest.main()
