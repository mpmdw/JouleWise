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
        from joulewise.align.qwen4_gold.core import digest
        from joulewise.align.qwen4_gold.runner import artifacts
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); path = root / "report.json"
            for side in ("reference", "mlx"):
                (root / side).mkdir()
                write_json(root / side / "request.json", {"backend": side})
                write_json(root / side / "result.json", {"traces": {"output": "output.npy"}})
            array = root / "reference/output.npy"
            array.write_bytes(b"test")
            (root / "mlx/output.npy").write_bytes(b"test")
            inventory = artifacts(root)
            write_json(path, {"fingerprint": "a", "status": "FAIL", "artifacts": inventory,
                              "evidence_digest": digest({"fingerprint": "a", "artifacts": inventory})})
            self.assertTrue(reusable(path, "a"))
            # The report verdict is presentation only; resume authenticates
            # worker evidence and recomputes it under the current gate.
            value = json.loads(path.read_text()); value["status"] = "PASS"; write_json(path, value)
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


def f32_norm(x, scale, group, eps=1e-6, axis_group=None):
    """Float32 RMSNorm as a kernel would compute it; scale is the effective (1+w)."""
    import numpy as np
    x = np.asarray(x, np.float32)
    group = axis_group or group
    g = x.reshape(*x.shape[:-1], -1, group)
    r = np.sqrt((g*g).mean(-1, keepdims=True, dtype=np.float32) + np.float32(eps)).astype(np.float32)
    return ((g / r).reshape(x.shape) * np.asarray(scale, np.float32)).astype(np.float32)


@unittest.skipUnless(HAS_ARRAYS, "optional NumPy")
class NormGateTests(unittest.TestCase):
    """Gate amendment A1: the outlier-gain case passes; real norm bugs fail."""
    H, C = 64, 4

    def setUp(self):
        import numpy as np
        rng = np.random.default_rng(7)
        self.rng = rng
        self.spec = {"kind": "offset", "group": self.H, "eps": 1e-6, "input": "n.input"}
        width = self.H * self.C
        # Effective gains around 163 with one ~906 outlier channel, as observed
        # at layer 0 mlp_hyper_connection.hc_norm (raw stored w = gain - 1).
        scale = rng.normal(163, 30, width).astype(np.float32)
        self.outlier = 3*self.H + 20
        scale[self.outlier] = 906.5
        self.weight = (scale - 1).astype(np.float32)
        self.x = rng.normal(0, 1, (1, 8, width)).astype(np.float32)
        self.x[0, 0, self.outlier] = -4.773969e-4

    def norm(self, x):
        return f32_norm(x, 1 + self.weight, self.H)

    def compare(self, y_ref, y_mlx, x_ref, x_mlx, dtype="fp32", spec=None):
        from joulewise.align.qwen4_gold.core import compare_norm
        return compare_norm(y_ref, y_mlx, x_ref, x_mlx, self.weight, spec or self.spec, dtype)

    def observed_inputs(self):
        """Upstream fp32 rounding noise (max 6e-7) and the observed -1.86e-7 element."""
        import numpy as np
        noise = self.rng.uniform(-6e-7, 6e-7, self.x.shape).astype(np.float32)
        x_mlx = (self.x + noise).astype(np.float32)
        x_mlx[0, 0, self.outlier] = np.float32(-4.775831e-4)
        return x_mlx

    def test_observed_outlier_gain_amplifying_input_noise_passes(self):
        x_mlx = self.observed_inputs()
        y_ref, y_mlx = self.norm(self.x), self.norm(x_mlx)
        # Precondition: this is exactly the failure the unamended gate reports.
        plain = compare_arrays(y_ref, y_mlx, "fp32")
        self.assertFalse(plain["pass"])
        self.assertGreater(abs(y_ref[0, 0, self.outlier] - y_mlx[0, 0, self.outlier]), 1.43e-4)
        self.assertTrue(compare_arrays(self.x, x_mlx, "fp32")["pass"])
        result = self.compare(y_ref, y_mlx, self.x, x_mlx)
        self.assertTrue(result["pass"], result)
        self.assertFalse(result["unpropagated_pass"])
        self.assertTrue(result["mlx_op"]["pass"] and result["reference_op"]["pass"])
        self.assertLess(result["mlx_op"]["max_relative"], 1e-6)

    def test_wrong_weight_on_one_channel_fails(self):
        x_mlx = self.observed_inputs()
        scale = (1 + self.weight).copy()
        scale[5] *= 1.001
        result = self.compare(self.norm(self.x), f32_norm(x_mlx, scale, self.H), self.x, x_mlx)
        self.assertFalse(result["pass"])
        self.assertFalse(result["mlx_op"]["pass"])
        self.assertTrue(result["reference_op"]["pass"])
        # Stored-convention bug (w instead of 1+w) on every channel also fails.
        self.assertFalse(self.compare(self.norm(self.x), f32_norm(x_mlx, self.weight, self.H),
                                      self.x, x_mlx)["mlx_op"]["pass"])

    def test_wrong_eps_fails(self):
        x = (self.x * 0.03).astype("float32")  # row RMS 0.03: eps 1e-5 vs 1e-6 shifts y by ~0.45%
        y_mlx = f32_norm(x, 1 + self.weight, self.H, eps=1e-5)
        result = self.compare(self.norm(x), y_mlx, x, x)
        self.assertFalse(result["pass"])
        self.assertFalse(result["mlx_op"]["pass"])

    def test_wrong_axis_or_stream_grouping_fails(self):
        import numpy as np
        x = self.x.copy()
        for stream in range(self.C):  # Streams with distinct scales expose grouping.
            x[..., stream*self.H:(stream+1)*self.H] *= 2.0 ** stream
        whole = f32_norm(x, 1 + self.weight, self.H, axis_group=self.H*self.C)
        result = self.compare(self.norm(x), whole, x, x)
        self.assertFalse(result["pass"])
        self.assertFalse(result["mlx_op"]["pass"])
        # Normalizing over the sequence axis instead of channels also fails.
        seq = x / np.sqrt((x*x).mean(1, keepdims=True) + 1e-6) * (1 + self.weight)
        self.assertFalse(self.compare(self.norm(x), seq.astype(np.float32), x, x)["mlx_op"]["pass"])

    def test_large_chained_difference_fails_even_when_both_ops_are_consistent(self):
        import numpy as np
        broad = (self.x + self.rng.normal(0, 0.05, self.x.shape)).astype(np.float32)
        result = self.compare(self.norm(self.x), self.norm(broad), self.x, broad)
        self.assertTrue(result["mlx_op"]["pass"] and result["reference_op"]["pass"])
        self.assertFalse(result["pass"])

    def test_input_outlier_does_not_loosen_another_row(self):
        """Regression: the former trace-global maximum made row 1 pass."""
        import numpy as np
        from joulewise.align.qwen4_gold.core import compare_norm
        x_ref = np.ones((2, 4), np.float32)
        x_mlx = x_ref.copy(); x_mlx[0, 0] += 9e-5
        weight = np.zeros(4, np.float32)
        spec = {"kind": "offset", "group": 4, "eps": 1e-6}
        f_ref, f_mlx = f32_norm(x_ref, 1 + weight, 4), f32_norm(x_mlx, 1 + weight, 4)
        y_ref, y_mlx = f_ref.copy(), f_mlx.copy()
        # Each worker remains individually within its 2e-4 op allowance, but
        # their opposite rounding errors exceed the chained base allowance.
        y_ref[1, 3] -= 1.5e-4; y_mlx[1, 3] += 1.5e-4
        result = compare_norm(y_ref, y_mlx, x_ref, x_mlx, weight, spec, "fp32")
        self.assertFalse(result["pass"])
        self.assertTrue(result["mlx_op"]["pass"] and result["reference_op"]["pass"])
        self.assertFalse(result["chained_pass"])
        # Causal row 0 receives a nonzero allowance; unrelated row 1 does not.
        clean = compare_norm(f_ref, f_mlx, x_ref, x_mlx, weight, spec, "fp32")
        self.assertGreater(clean["propagation"]["max_allowance"], 0)
        self.assertTrue(clean["chained_pass"], clean)
        # The cosine floor is satisfied, so it is the elementwise row-1 check
        # (allowance 0 there) that fails; exactly one element is outside.
        self.assertGreaterEqual(result["cosine"], 0.999999)
        self.assertEqual(result["fraction_within"], 7 / 8)
        # Non-vacuous regression: the former trace-global bound
        # P = |s|/r * e_x * (1 + |x|*mean|x|/r^2) would have admitted row 1.
        e_x = float(np.abs(x_ref.astype(np.float64) - x_mlx).max())
        r = np.sqrt(1.0 + 1e-6)
        old_allowance = 1.0 / r * e_x * (1.0 + 1.0 / (r * r))
        diff = abs(float(y_ref[1, 3]) - float(y_mlx[1, 3]))
        self.assertLess(diff, 1e-4 + 1e-4 * abs(float(y_ref[1, 3])) + old_allowance)
        local = self.x.copy()
        local[0, 3, 7] += 0.5  # One large upstream error cannot buy a loose allowance.
        result = self.compare(self.norm(self.x), self.norm(local), self.x, local)
        self.assertTrue(result["mlx_op"]["pass"] and result["reference_op"]["pass"])
        self.assertFalse(result["input"]["pass"])
        self.assertFalse(result["pass"])

    def test_other_rms_group_neither_loosens_nor_dilutes(self):
        """The cross term averages over the element's own group, not the row."""
        import numpy as np
        from joulewise.align.qwen4_gold.core import compare_norm
        # One row holding two RMS groups of 4 (as an hc_norm holds hc_count streams).
        spec = {"kind": "offset", "group": 4, "eps": 1e-6}
        weight = np.zeros(8, np.float32)
        x_ref = np.ones((1, 8), np.float32)
        x_mlx = x_ref.copy(); x_mlx[0, 0] += 9e-5
        f_ref, f_mlx = f32_norm(x_ref, 1 + weight, 4), f32_norm(x_mlx, 1 + weight, 4)
        # Group 1 has no input error, so its propagated allowance is exactly 0;
        # a row-wide mean would have granted it 9e-5/8 ~ 1.1e-5.
        y_ref, y_mlx = f_ref.copy(), f_mlx.copy()
        y_ref[0, 5] -= 1.025e-4; y_mlx[0, 5] += 1.025e-4
        result = compare_norm(y_ref, y_mlx, x_ref, x_mlx, weight, spec, "fp32")
        self.assertTrue(result["mlx_op"]["pass"] and result["reference_op"]["pass"])
        self.assertFalse(result["chained_pass"])
        self.assertEqual(result["fraction_within"], 7 / 8)
        # Not diluted: for a large in-group error the group-mean cross term is
        # needed in full; a row-wide mean (half as large here) is not a bound.
        # (The cosine floor and input gate fail at this size; only the
        # elementwise allowance is under test.)
        x_mlx = x_ref.copy(); x_mlx[0, 0] += 0.02
        f_mlx = f32_norm(x_mlx, 1 + weight, 4)
        clean = compare_norm(f_ref, f_mlx, x_ref, x_mlx, weight, spec, "fp32")
        self.assertEqual(clean["fraction_within"], 1.0, clean)
        dy = abs(float(f_ref[0, 1]) - float(f_mlx[0, 1]))  # ~5.01e-3, x_1 = 1, dx_1 = 0
        row_wide = 1.0 * (0.02 / 8)  # what a row-wide mean would allow
        self.assertGreater(dy, 1e-4 + 1e-4 * abs(float(f_ref[0, 1])) + row_wide)

    def test_allowance_bounds_float64_propagation_elementwise(self):
        """P bounds |f(x_ref)-f(x_mlx)| per element in float64, including second order."""
        import numpy as np
        from joulewise.align.qwen4_gold.core import norm_allowance, norm_reference
        x = self.x[0].astype(np.float64)
        weight = self.weight.astype(np.float64)
        G = self.spec["group"]
        for scale in (6e-7, 1e-3, 0.05, 0.3):  # fp32 noise ... large bf16-like relative errors
            dx = self.rng.uniform(-scale, scale, x.shape) * (1 + 50 * (self.rng.random(x.shape) < 0.01))
            f_ref, r, _ = norm_reference(x, weight, self.spec)
            f_mlx, _, _ = norm_reference(x + dx, weight, self.spec)
            allowance = norm_allowance(x, x + dx, weight, self.spec)
            ratio = np.abs(f_ref - f_mlx) / allowance
            self.assertLessEqual(ratio.max(), 1 + 1e-9, scale)
            self.assertGreater(ratio.max(), 0.5)  # and it is not vacuously loose
            if scale == 6e-7:  # first-order limit: the documented P_c
                cross = (np.abs(x) * np.abs(dx)).reshape(x.shape[0], -1, G).mean(-1, keepdims=True)
                cross = np.broadcast_to(cross, (x.shape[0], x.shape[1] // G, G)).reshape(x.shape)
                first = np.abs(1 + weight) * (np.abs(dx) / r + np.abs(x) * cross / r**3)
                np.testing.assert_allclose(allowance, first, rtol=1e-4)
        # Gated norm, including the gate's own error.
        spec = {"kind": "gated", "group": 32, "eps": 1e-6, "activation": "silu"}
        w = self.rng.normal(1, 0.2, 32)
        x = self.rng.normal(0, 0.3, (16, 32)); z = self.rng.normal(0, 2, (16, 32))
        for scale in (1e-6, 0.02, 0.2):
            dx, dz = (self.rng.uniform(-scale, scale, x.shape) for _ in range(2))
            f_ref, _, _ = norm_reference(x, w, spec, z)
            f_mlx, _, _ = norm_reference(x + dx, w, spec, z + dz)
            ratio = np.abs(f_ref - f_mlx) / norm_allowance(x, x + dx, w, spec, z, z + dz)
            self.assertLessEqual(ratio.max(), 1 + 1e-9, scale)

    def test_reference_self_consistency_is_gated(self):
        y_ref = self.norm(self.x)
        y_ref[0, 1, 2] += 1e-2
        result = self.compare(y_ref, self.norm(self.x), self.x, self.x)
        self.assertFalse(result["reference_op"]["pass"])
        self.assertFalse(result["pass"])

    def test_bf16_rounded_outputs_pass(self):
        from joulewise.align.qwen4_gold.core import round_bf16
        x = round_bf16(self.x)
        y = round_bf16(self.norm(x))
        self.assertTrue(self.compare(y, y, x, x, "bf16")["pass"])

    def test_gated_norm_activation_weight_and_gate(self):
        import numpy as np
        from joulewise.align.qwen4_gold.core import compare_norm
        dv = 32
        spec = {"kind": "gated", "group": dv, "eps": 1e-6, "activation": "sigmoid"}
        w = self.rng.normal(1, 0.2, dv).astype(np.float32)
        x = self.rng.normal(0, 0.3, (16, dv)).astype(np.float32)
        z = self.rng.normal(0, 2, (16, dv)).astype(np.float32)
        def gated(x, z, w, act="sigmoid", eps=1e-6):
            n = x / np.sqrt((x*x).mean(-1, keepdims=True) + np.float32(eps))
            sig = 1 / (1 + np.exp(-z))
            return (w * n * (sig if act == "sigmoid" else z*sig)).astype(np.float32)
        z_mlx = (z + self.rng.uniform(-2e-7, 2e-7, z.shape)).astype(np.float32)
        ok = compare_norm(gated(x, z, w), gated(x, z_mlx, w), x, x, w, spec, "fp32", z, z_mlx)
        self.assertTrue(ok["pass"], ok)
        bad = compare_norm(gated(x, z, w), gated(x, z, w, "silu"), x, x, w, spec, "fp32", z, z)
        self.assertFalse(bad["mlx_op"]["pass"])
        offset = compare_norm(gated(x, z, w), gated(x, z, 1 + w), x, x, w, spec, "fp32", z, z)
        self.assertFalse(offset["mlx_op"]["pass"])  # (1+w) convention is wrong for the gated norm
        self.assertEqual(compare_norm(gated(x, z, w), gated(x, z, w), x, x, w, spec, "fp32")["reason"],
                         "missing_gate_input")

    def test_shape_and_nonfinite_fail_closed(self):
        import numpy as np
        y = self.norm(self.x)
        self.assertEqual(self.compare(y, y, self.x, self.x[..., :-1])["reason"], "shape_mismatch")
        bad = y.copy(); bad[0, 0, 0] = np.nan
        self.assertFalse(self.compare(y, bad, self.x, self.x)["pass"])

    def test_norm_trace_inventory(self):
        from joulewise.align.qwen4_gold.core import norm_specs
        c = {"layer_types": ["linear_attention", "full_attention"], "ple_layer_ids": [2], "hidden_size": 8,
             "hc_count": 2, "head_dim": 4, "linear_value_head_dim": 4, "output_gate_type": "sigmoid"}
        self.assertEqual(set(norm_specs(c, "0")), {"attn.norm", "mlp.norm", "attention.gated_norm"})
        self.assertEqual(set(norm_specs(c, "1")), {"attn.norm", "mlp.norm", "attention.q_norm", "attention.k_norm",
                                                   "ple.norm_key", "ple.norm_query", "ple.norm_conv"})
        self.assertEqual(set(norm_specs(c, "final")), {"final.norm"})
        self.assertEqual(norm_specs(c, "embed"), {})
        self.assertEqual(norm_specs(c, "0")["attention.gated_norm"]["activation"], "sigmoid")
        self.assertEqual(norm_specs(c, "1")["mlp.norm"]["weight"], "layers.1.mlp_hyper_connection.hc_norm.weight")
        self.assertTrue({"attention.gated_norm.input", "attention.gated_norm.gate", "mlp.norm.input"}
                        <= required_traces(c, "0"))
        self.assertIn("final.norm.input", required_traces(c, "final"))
        c.pop("output_gate_type")
        self.assertEqual(norm_specs(c, "0")["attention.gated_norm"]["activation"], "silu")


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


    def test_router_topk_ties_break_to_lowest_expert_inside_router_only(self):
        """Live gold run, layer 1, tokens-b bf16 real, token row 2 (official router)."""
        import types
        import torch
        from transformers.models.qwen4_exp.modeling_qwen4_exp import Qwen4ExpTextTopKRouter
        from joulewise.align.qwen4_gold.reference import deterministic_router_ties
        # The saved bf16 router logits of that row (512 experts, little-endian
        # bf16 bit patterns). Experts 50, 228, 234 tie exactly at -4.125 for the
        # 9th and 10th slots; torch's own order picked {228, 234}, MLX {50, 228}.
        bits = bytes.fromhex(
            "afc0bcc0bfc0c6c0e6c0c8c0b6c0cfc0b3c0b3c09ac086c0a6c0b2c0a1c0b2c0e0c0bcc0b1c073c0a6c0b7c0d1c0cbc0"
            "adc0bdc0c3c099c092c0b5c0ccc0a7c0b7c0aac0dcc0c9c0acc0a2c0acc0d9c0d1c091c09fc0afc0b4c0abc0a1c0ccc0"
            "bec0afc084c093c0a2c0b0c09ec0bcc0cdc0b7c0a9c0cbc0dac0cac0e3c09bc0bfc0d1c0bdc09cc0b9c0afc097c0c7c0"
            "d9c0d5c0b4c0c9c0cac0acc0c2c0abc0cfc09bc0a8c0c0c0c8c0d4c0b8c0c2c0aec0a6c0adc0c7c0b2c0b9c0b5c090c0"
            "bcc0b8c09fc0e2c0abc09fc0d0c09fc0c5c092c0b3c0b6c0adc0b0c0d1c0b8c0bec0d8c0bac0e3c0b6c0bfc0a2c0d2c0"
            "a6c0b4c05ec0c6c0a4c0bdc0b5c098c0b9c0c3c0e5c0abc0a0c0c4c0bbc0d9c0a4c099c09ec0adc097c0bbc094c0d2c0"
            "c1c0c3c0b9c081c0afc0b6c090c0a7c0c0c08bc094c0a7c0e6c0bbc0a2c0bec0d7c0bac0c0c06ac0c1c098c09cc0bac0"
            "a5c0ddc0b8c0b7c0b5c0c7c0bfc0b0c090c08fc09dc0d0c0b3c0aac0b5c0d6c0aac0c0c0c0c0b0c0a6c0c4c0a8c0b5c0"
            "a7c0a7c093c0cec0b1c0ccc0acc0c3c0aac0bfc0b9c0cec0d7c0cfc0a1c0b2c0afc0cdc0bfc0cdc0e1c0aac0a7c0bac0"
            "b0c0bec0bcc09cc0b1c0b0c07fc0b6c0f5c0d2c0cbc0cdc084c09dc0aec0b8c092c0b2c084c0b0c0d4c0ecc0f5c0b0c0"
            "cac0bdc0b6c0cbc0ecc099c0dac0b6c0acc077c0aec0dbc0c2c0b5c0a2c0afc0bcc0c8c07dc0b0c0c2c0c4c0cec0dec0"
            "d6c0c8c0b9c0a2c0d1c08bc08cc0b1c0b8c0d8c0e0c0bac0b8c0bbc0a4c0a3c0d2c0c5c08fc0acc0c8c0c3c0b8c0c5c0"
            "b9c098c0a5c0c5c0bac0fcc0e6c0b1c0c0c098c092c098c0b0c0dac0e1c0b0c0dbc0d7c092c0c7c093c0b3c094c0d8c0"
            "aec0abc0bbc0bcc0d3c09dc0d0c0c0c0a6c0c0c0b9c0afc0acc0eac0a2c0a5c0b2c0aec0d3c0b7c0b7c0b0c0e3c0bcc0"
            "cdc09fc0c8c0b1c0dbc09ac0cfc0c1c0b2c0bbc0bbc0b5c0abc093c0bec0d1c0afc0c1c093c0bbc09bc0c0c0a9c0bec0"
            "c0c0b6c0b2c0cdc0bac0b4c0b8c0b0c0bfc0aac0e7c09dc0bfc0c4c0bfc0c3c0a2c0b0c0e8c0b7c0bcc0c4c0afc0b2c0"
            "cbc0cdc0a6c089c09dc0a7c0b2c0a9c08ec0b6c0bdc0c3c094c0a6c0bbc0b1c0b0c0c6c0c4c0f0c0d4c0cfc0b0c0a8c0"
            "b8c0b1c0c8c0afc0adc0d2c0bac0c4c0b5c09bc0a6c0b6c0d9c0c8c0c9c0c7c0bec09bc0aec0c1c0b9c0c2c0c0c0b4c0"
            "bfc0c5c0dbc0bbc0a0c0b9c0aac08ec0c1c0cac09fc0a8c0c3c0bdc09fc0c1c0a4c0bdc0dbc0b8c0b5c0a2c0d1c0c1c0"
            "b6c0aec0b6c0c7c0c4c0bac0a2c0b0c0b5c0cbc0a9c0afc0a8c0c0c0adc0c8c0b6c0bbc0b7c0b4c0d8c0b7c0bdc0b3c0"
            "b7c0d2c0c6c0d7c0adc0acc0a3c0c2c0a8c0b3c0b5c0d6c0b7c0cac0b1c0e4c0b7c0b1c0adc0e1c094c0c0c05bc0c4c0"
            "d1c0a4c0b0c0a0c091c0c3c0dfc0bac0"
        )
        import numpy as np
        logits = torch.from_numpy(np.frombuffer(bits, "<i2").copy()).view(torch.bfloat16).float()[None]
        self.assertEqual([logits[0, e].item() for e in (50, 228, 234)], [-4.125] * 3)
        config = types.SimpleNamespace(num_experts_per_tok=10, num_experts=512, norm_topk_prob=True, hidden_size=512)
        router = Qwen4ExpTextTopKRouter(config).to(torch.bfloat16)
        with torch.no_grad():
            router.weight.copy_(torch.eye(512, dtype=torch.bfloat16))  # logits == the bf16 inputs exactly
        hidden = logits.to(torch.bfloat16)
        _, plain_scores, _ = router(hidden)
        counts, seen = {"topk_calls": 0, "rows": 0, "straddling_ties": 0}, []
        original = torch.topk
        deterministic_router_ties(router, torch, counts)
        router.register_forward_hook(lambda m, a, o: seen.append(o))
        router_logits, scores, indices = router(hidden)
        self.assertEqual(router_logits[0, 50].item(), router_logits[0, 234].item())
        self.assertEqual(set(indices[0].tolist()), {502, 122, 163, 19, 249, 258, 222, 147, 50, 228})
        self.assertEqual(indices[0, -2:].tolist(), [50, 228])  # tied block in ascending expert order
        # Probabilities/weights are untouched: same multiset as torch's own call.
        self.assertTrue(torch.equal(scores.sort(dim=-1).values, plain_scores.sort(dim=-1).values))
        self.assertEqual(len(seen), 1)  # registered hooks still run
        self.assertEqual(counts, {"topk_calls": 1, "rows": 1, "straddling_ties": 1})
        self.assertIs(torch.topk, original)  # patched only inside the router forward
        # No tie at the cut: identical to torch.topk, and not counted.
        logits[0, 228], logits[0, 234] = -4.0, -4.15625
        _, _, untied = router(logits.to(torch.bfloat16))
        self.assertEqual(set(untied[0].tolist()), {502, 122, 163, 19, 249, 258, 222, 147, 228, 50})
        self.assertEqual(counts["straddling_ties"], 1)


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

    def test_norm_gate_wiring_uses_checkpoint_weight_and_returns_reference_chain(self):
        import argparse
        import numpy as np
        import types
        from joulewise.align.qwen4_gold.runner import failure_summary
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            H, C = 4, 2
            w = np.linspace(-0.5, 5, H*C).astype(np.float32)
            c = {"hidden_size": H, "hc_count": C}
            args = argparse.Namespace(output=str(root / "out"), dtypes="fp32", input_modes="real", seed=1,
                random_scale=1., mlx_module=str(Path(__file__).resolve()), adapter_dependency=[],
                ref_python="unused", mlx_python="unused", max_gb=12, timeout=1, resume=False)
            reads = []
            def read(name, selection=None, framework="numpy", dtype="fp32"):
                reads.append(name)
                return w
            cp = types.SimpleNamespace(config=c, root=root, weight_map={}, prefix="model.", read=read)
            harness = Harness(args, cp, {}, [], {})
            x = np.random.default_rng(3).normal(0, 1, (1, 3, H*C)).astype(np.float32)
            hidden = root / "hidden.npy"
            np.save(hidden, x)
            def runner(scale):
                def fake(python, request, directory, *a):
                    directory.mkdir(parents=True, exist_ok=True)
                    mlx = request["backend"] == "mlx"
                    traces = {"final.norm": f32_norm(x, (1 + w) * (scale if mlx else 1), H),
                              "final.norm.input": x, "output": np.full((1, 3, H), 2. if mlx else 1., np.float32)}
                    for name, value in traces.items():
                        np.save(directory / (name + ".npy"), value)
                    return {"traces": {n: n + ".npy" for n in traces}, "metadata": {"adapter_kind": "mlx"}}
                return fake
            prompt = {"name": "p", "input_ids": [1, 2, 3]}
            with patch("joulewise.align.qwen4_gold.runner.execute", runner(1.0)):
                out = harness.case("final", "fp32", prompt, "real", hidden)
            row = harness.rows["final"][0]
            self.assertEqual(reads, ["model.hyper_connection_mixer.hc_norm.weight"])
            self.assertTrue(row["metrics"]["final.norm"]["pass"])
            self.assertEqual(row["metrics"]["final.norm"]["gate"], "A1-input-conditioned")
            self.assertTrue(row["metrics"]["final.norm.input"]["pass"])
            # The MLX output disagrees, so the case FAILs, yet the returned
            # chain input is the official reference output.
            self.assertEqual(row["status"], "FAIL")
            self.assertEqual(out, (root / "out/final/p-fp32-real/reference/output.npy").resolve())
            np.testing.assert_array_equal(np.load(out), np.ones((1, 3, H)))
            with patch("joulewise.align.qwen4_gold.runner.execute", runner(1.001)):
                harness.case("final", "fp32", prompt, "other", hidden)
            row = harness.rows["final"][1]
            self.assertFalse(row["metrics"]["final.norm"]["mlx_op"]["pass"])
            summary = failure_summary({"cases": harness.rows["final"]})
            self.assertEqual(summary[1]["failing_traces"], ["final.norm", "output"])


@unittest.skipUnless(HAS_ARRAYS, "optional NumPy")
class RouterA2Tests(unittest.TestCase):
    """Gate amendment A2: bf16 router boundary swaps under teacher-forced MoE."""
    E, K, H, ROWS = 512, 10, 16, 4

    def logits(self):
        import numpy as np
        from joulewise.align.qwen4_gold.core import round_bf16
        rng = np.random.default_rng(5)
        value = rng.uniform(-9, -6, (self.ROWS, self.E))
        top = [1.5, 1.4375, 1.375, 1.3125, 1.25, 1.1875, 1.15625, 1.125, 1.09375]
        for row in range(self.ROWS):
            value[row, [3, 17, 40, 77, 101, 150, 200, 260, 300]] = top
            value[row, 342] = value[row, 349] = 1.015625  # exact reference tie at the k-th slot
            value[row, 400] = 0.5
        return round_bf16(value)

    def run_case(self, ref_logits, mlx_logits, mlx_ids=None, forced=True, forced_scale=1.0, dtype="bf16"):
        import numpy as np
        from joulewise.align.qwen4_gold.core import compare_arrays
        experts_out = np.random.default_rng(9).normal(0, 1, (self.E, self.H))

        def select(logits):  # canonical/A2 reference rule: descending, lowest index first
            return np.argsort(-logits, axis=-1, kind="stable")[:, :self.K]

        def weights(logits, ids):
            p = np.exp(logits - logits.max(-1, keepdims=True)); p /= p.sum(-1, keepdims=True)
            w = np.take_along_axis(p, ids, -1)
            return (w / w.sum(-1, keepdims=True)).astype(np.float32)

        def moe(ids, w):
            return np.einsum("rk,rkh->rh", w, experts_out[ids]).astype(np.float32)[None]

        ref_ids = select(ref_logits)
        mlx_ids = select(mlx_logits) if mlx_ids is None else mlx_ids
        arrays = {"reference": {"router.logits": ref_logits, "router.experts": ref_ids,
                                "router.weights": weights(ref_logits, ref_ids),
                                "moe": moe(ref_ids, weights(ref_logits, ref_ids))},
                  "mlx": {"router.logits": mlx_logits, "router.experts": mlx_ids,
                          "router.weights": weights(mlx_logits, mlx_ids), "moe": moe(mlx_ids, weights(mlx_logits, mlx_ids))}}
        if forced:  # the candidate's whole-layer re-run under the reference's selection
            w = weights(mlx_logits, ref_ids)
            arrays["mlx"].update({"router.logits.forced": mlx_logits, "router.experts.forced": ref_ids,
                                  "router.weights.forced": w, "moe.forced": moe(ref_ids, w) * forced_scale})
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        results = {}
        for side, values in arrays.items():
            (root / side).mkdir()
            for name, value in values.items():
                np.save(root / side / (name + ".npy"), np.asarray(value))
            results[side] = {"traces": {name: name + ".npy" for name in values}}
        a, b = arrays["reference"], arrays["mlx"]
        aligned = [np.take_along_axis(v["router.weights"], np.argsort(v["router.experts"], -1), -1) for v in (a, b)]
        report = {"metrics": {"router.logits": compare_arrays(a["router.logits"], b["router.logits"], dtype),
                              "router.experts": compare_arrays(a["router.experts"], b["router.experts"], dtype, exact=True),
                              "router.weights": compare_arrays(*aligned, dtype),
                              "moe": compare_arrays(a["moe"], b["moe"], dtype)}}
        import types
        harness = object.__new__(Harness)
        harness.checkpoint = types.SimpleNamespace(config={"layer_types": ["linear_attention"], "hidden_size": self.H})
        harness.router_a2("0", report, root, results["reference"], results["mlx"], dtype)
        return report

    def flip(self):
        """The observed 1-ulp flip: layer 2, tokens-b bf16 random, row 7."""
        ref = self.logits()
        mlx = ref.copy(); mlx[1, 342] = 1.0078125  # one bf16 ulp below; MLX now ranks 349 first
        return ref, mlx

    def test_exact_reference_tie_resolves_to_the_same_set(self):
        ref = self.logits()
        report = self.run_case(ref, ref.copy())
        self.assertTrue(report["metrics"]["router.experts"]["pass"])
        self.assertTrue(report["metrics"]["router.experts"]["exact_set_agreement"])
        self.assertNotIn("gate", report["metrics"]["router.experts"])  # A2 was never needed

    def test_one_ulp_boundary_flip_passes_only_with_forced_moe(self):
        import numpy as np
        ref, mlx = self.flip()
        report = self.run_case(ref, mlx)
        experts = report["metrics"]["router.experts"]
        self.assertTrue(experts["pass"], experts)
        self.assertFalse(experts["unforced"]["pass"])
        self.assertEqual(experts["admissible_rows"], [1])
        self.assertEqual(experts["admissible_swaps"], 1)
        pair = experts["rows"][0]["pairs"][0]
        self.assertEqual((pair["reference"], pair["candidate"]), (342, 349))
        self.assertTrue(pair["exact_reference_tie"])
        self.assertAlmostEqual(pair["candidate_margin"], 0.0078125)
        self.assertTrue(report["metrics"]["router.logits"]["pass"])
        self.assertTrue(experts["forced"]["pass"])  # forced selection is exactly the reference's
        for name in ("router.logits", "router.weights", "moe"):
            self.assertEqual(report["metrics"][name]["gate"], "A2-teacher-forced")
            self.assertTrue(report["metrics"][name]["pass"], report["metrics"][name])
        self.assertFalse(report["metrics"]["moe"]["unforced"]["pass"])  # the flip is visible unforced
        self.assertTrue(all(m["pass"] for m in report["metrics"].values()))
        # Without the teacher-forced traces the swapped row cannot pass.
        report = self.run_case(ref, mlx, forced=False)
        self.assertEqual(report["metrics"]["router.experts"]["admissible_rows"], [1])  # classified admissible
        self.assertFalse(report["metrics"]["router.experts"]["pass"])  # but no forced run to confirm it
        self.assertFalse(report["metrics"]["moe"]["pass"])
        self.assertIn("a2_forced_trace_missing", report["metrics"]["moe"]["reason"])
        # fp32 stays exact set agreement.
        report = self.run_case(ref, mlx, dtype="fp32")
        self.assertFalse(report["metrics"]["router.experts"]["pass"])
        self.assertNotIn("gate", report["metrics"]["router.experts"])

    def test_mid_ranking_expert_difference_fails(self):
        ref = self.logits()
        ids = __import__("numpy").argsort(-ref, axis=-1, kind="stable")[:, :self.K].copy()
        ids[2, 2] = 400  # drop the 3rd-ranked expert (40), select a far lower one
        report = self.run_case(ref, ref.copy(), mlx_ids=ids)
        self.assertFalse(report["metrics"]["router.experts"]["pass"])
        self.assertEqual(report["metrics"]["router.experts"]["non_admissible_rows"], [2])

    def test_boundary_swap_with_large_margin_fails(self):
        ref = self.logits()
        ids = __import__("numpy").argsort(-ref, axis=-1, kind="stable")[:, :self.K].copy()
        ids[0, -1] = 400  # k-th selected 349 at 1.0156 vs 400 at 0.5: margin far above the allowance
        report = self.run_case(ref, ref.copy(), mlx_ids=ids)
        self.assertFalse(report["metrics"]["router.experts"]["pass"])
        self.assertEqual(report["metrics"]["router.experts"]["non_admissible_rows"], [0])

    def test_wrong_weights_moe_under_forced_routing_fails(self):
        ref, mlx = self.flip()
        report = self.run_case(ref, mlx, forced_scale=1.2)
        self.assertTrue(report["metrics"]["router.experts"]["pass"])
        self.assertFalse(report["metrics"]["moe"]["pass"])
        self.assertEqual(report["metrics"]["moe"]["gate"], "A2-teacher-forced")


@unittest.skipUnless(HAS_ARRAYS, "optional NumPy")
class RegateToolTests(unittest.TestCase):
    """Offline re-grading recomputes verdicts and refuses unauthenticated evidence."""

    def make_case(self, work, mlx_value, legacy):
        import numpy as np
        from joulewise.align.qwen4_gold.core import digest, sha256
        from joulewise.align.qwen4_gold.runner import artifacts
        case = work / "parity/embed/p-fp32-real"
        for side, value in (("reference", 1.0), ("mlx", mlx_value)):
            (case / side).mkdir(parents=True)
            traces = {"output": "output.npy", "embedding": "embedding.npy"}
            for name, filename in traces.items():
                np.save(case / side / filename, np.full((1, 2, 4), value if name == "output" else 1.0, np.float32))
            write_json(case / side / "request.json", {"backend": side})
            write_json(case / side / "result.json", {"traces": traces, "metadata": {"adapter_kind": "mlx"}})
        if legacy:  # pre-inventory report: npy hashes only
            inventory = {str(p.relative_to(case)): sha256(p) for p in case.rglob("*.npy")}
            report = {"fingerprint": "f", "status": "PASS", "artifacts": inventory}
        else:
            inventory = artifacts(case)
            report = {"fingerprint": "f", "status": "PASS", "artifacts": inventory,
                      "evidence_digest": digest({"fingerprint": "f", "artifacts": inventory})}
        write_json(case / "report.json", report)
        write_json(work / "parity/embed.json", {"expected_cases": 1})
        return case

    def regate(self, work):
        import importlib.util as util
        import types
        spec = util.spec_from_file_location("regate", Path(__file__).resolve().parents[1] / "scripts/qwen4_gold_regate_legacy.py")
        module = util.module_from_spec(spec); spec.loader.exec_module(module)
        checkpoint = types.SimpleNamespace(config={"hidden_size": 2, "hc_count": 2}, prefix="model.")
        return module.regate_work(work, checkpoint)["units"]["embed"]

    def test_verdicts_are_recomputed_and_evidence_is_authenticated(self):
        import numpy as np
        for legacy in (True, False):
            with tempfile.TemporaryDirectory() as d:
                work = Path(d)
                case = self.make_case(work, 1.0, legacy)
                unit = self.regate(work)
                self.assertEqual(unit["status"], "PASS")
                self.assertEqual(unit["cases"][0]["evidence"], "legacy-npy" if legacy else "v2")
                # A result map aliasing the reference's arrays is refused.
                result = json.loads((case / "mlx/result.json").read_text())
                write_json(case / "mlx/result.json", dict(result, traces={"output": "../reference/output.npy",
                                                                         "embedding": "embedding.npy"}))
                self.assertEqual(self.regate(work)["cases"][0]["status"], "EVIDENCE_ERROR")
                write_json(case / "mlx/result.json", result)
                # A changed array is refused.
                np.save(case / "mlx/output.npy", np.full((1, 2, 4), 2.0, np.float32))
                self.assertEqual(self.regate(work)["cases"][0]["status"], "EVIDENCE_ERROR")
            with tempfile.TemporaryDirectory() as d:
                # Authentic evidence of a mismatch FAILs although the report says PASS.
                work = Path(d)
                self.make_case(work, 2.0, legacy)
                unit = self.regate(work)
                self.assertEqual(unit["cases"][0]["recorded_status"], "PASS")
                self.assertEqual(unit["cases"][0]["status"], "FAIL")
                self.assertEqual(unit["status"], "FAILED")


if __name__ == "__main__":
    unittest.main()
