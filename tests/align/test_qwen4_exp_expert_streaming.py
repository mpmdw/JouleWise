"""CPU contracts for optional qwen4_exp expert streaming."""
import ast
import os
import tempfile
import unittest
from collections import OrderedDict
from pathlib import Path

try:
    import numpy as np
except ImportError:  # bare CI; exercised in the pinned MLX environment
    np = None

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "joulewise/align/models/qwen4_exp.py"
CONVERTER = ROOT / "scripts/align_convert_qwen4_exp.py"


class _FakeArray:
    def __init__(self, value): self.value = np.asarray(value)
    def astype(self, _dtype): return self


class _FakeMX:
    bfloat16 = object()
    @staticmethod
    def array(value): return _FakeArray(value)
    @staticmethod
    def eval(*_values): return None


class _ForwardArray(np.ndarray if np is not None else object):
    """NumPy-backed array whose type distinguishes mx.array indices."""

    def __new__(cls, value):
        return np.asarray(value).view(cls)


class _ForwardMX:
    """Strict subset of MLX used by StreamingFusedSwitchGLU."""

    @staticmethod
    def array(value): return _ForwardArray(value)
    @staticmethod
    def repeat(*args, **kwargs): return _ForwardArray(np.repeat(*args, **kwargs))
    @staticmethod
    def split(*args, **kwargs): return [_ForwardArray(v) for v in np.split(*args, **kwargs)]
    @staticmethod
    def matmul(a, b): return _ForwardArray(np.matmul(a, b))
    @staticmethod
    def concatenate(*args, **kwargs): return _ForwardArray(np.concatenate(*args, **kwargs))

    @staticmethod
    def take(a, indices, axis=None):
        if not isinstance(indices, _ForwardArray):
            raise TypeError("take(): indices must be an mlx array, not ndarray")
        return _ForwardArray(np.take(a, indices, axis=axis))


def _production_store_class():
    """Execute just the host-side production class; MLX is Metal-only."""
    tree = ast.parse(MODULE.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ExpertStream")
    import threading
    namespace = {"OrderedDict": OrderedDict, "Path": Path, "os": os, "np": np, "mx": _FakeMX,
                 "threading": threading}
    exec(compile(ast.Module([node], []), str(MODULE), "exec"), namespace)
    return namespace["ExpertStream"]


def _production_forward_class():
    """Execute the production streaming forward against a strict NumPy mx."""
    tree = ast.parse(MODULE.read_text())
    node = next(n for n in tree.body
                if isinstance(n, ast.ClassDef) and n.name == "StreamingFusedSwitchGLU")
    fake_nn = type("FakeNN", (), {"Module": object})
    namespace = {"np": np, "mx": _ForwardMX, "nn": fake_nn,
                 "silu_once": lambda z: _ForwardArray(z / (1 + np.exp(-z)))}
    exec(compile(ast.Module([node], []), str(MODULE), "exec"), namespace)
    return namespace["StreamingFusedSwitchGLU"]


def _bf16(values):
    return (np.asarray(values, np.float32).view(np.uint32) >> 16).astype("<u2")


class ExpertStreamingValidationTest(unittest.TestCase):
    def test_negative_cache_is_refused_before_output_creation(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("qwen4_exp_streaming_converter", CONVERTER)
        converter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(converter)
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "must-not-exist"
            with self.assertRaisesRegex(ValueError, "must not be negative"):
                converter.convert(Path(td) / "checkpoint", output, profile="bf16",
                                  expert_streaming_cache_gb=-1)
            self.assertFalse(output.exists())

    def test_streaming_profile_is_refused_before_output_creation(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("qwen4_exp_streaming_converter_profile", CONVERTER)
        converter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(converter)
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "must-not-exist"
            with self.assertRaisesRegex(ValueError, "use --profile bf16"):
                converter.convert(Path(td) / "checkpoint", output, profile="maxfit",
                                  expert_streaming_cache_gb=1)
            self.assertFalse(output.exists())


@unittest.skipUnless(np is not None, "numpy required for the CPU numerical fixture")
class ExpertStreamingCpuTest(unittest.TestCase):
    def test_tiny_stream_matches_resident_and_counts_lru(self):
        # dims=hidden=2 => 12 bf16 values/expert. Values are exactly bf16, so
        # streamed and fully resident matmuls must be bit-identical.
        experts = []
        for e in range(3):
            gu = np.arange(4 * 2, dtype=np.float32).reshape(4, 2) / 8 + e
            down = np.arange(2 * 2, dtype=np.float32).reshape(2, 2) / 4 + e
            experts.append((gu, down))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "experts.bf16"
            path.write_bytes(b"".join(_bf16(np.concatenate([g.ravel(), d.ravel()])).tobytes()
                                      for g, d in experts))
            # One expert per layer fits: 24 bytes / 2**30 GiB.
            meta = {"dir": td, "format": "bf16", "cache_gb": 24 / 2**30, "layers": {
                "0": {"file": path.name, "dims": 2, "hidden": 2, "experts": 3,
                      "size_bytes": path.stat().st_size}}}
            store = _production_store_class()(meta, 0)
            x = np.array([.5, -.25], np.float32)
            for expert in (0, 0, 1, 0):
                gu, down = store.get(expert)
                sg, su = np.split(x @ gu.value.T, 2)
                rg, ru = np.split(x @ experts[expert][0].T, 2)
                silu = lambda z: z / (1.0 + np.exp(-z))
                streamed = (silu(sg) * su) @ down.value.T
                resident = (silu(rg) * ru) @ experts[expert][1].T
                np.testing.assert_array_equal(streamed, resident)
            self.assertEqual(store.counters(), {"hits": 1, "misses": 3, "bytes_read": 72,
                                                "prefill": {"calls": 0, "experts": 0},
                                                "decode": {"calls": 0, "experts": 0}})
            self.assertEqual(list(store.cache), [0])
            store.reset()
            self.assertEqual(store.counters()["misses"], 0)
            store.close()
            self.assertEqual(store.fd, -1)

    def test_deduplicated_call_loads_each_expert_once_and_matches_per_row(self):
        class MissCountingCache:
            def __init__(self, values):
                self.values, self.loads = values, 0

            def get(self, expert):
                self.loads += 1
                return self.values[int(expert)]

        rng = np.random.default_rng(7)
        values = [(rng.normal(size=(6, 4)), rng.normal(size=(4, 3))) for _ in range(4)]
        x = rng.normal(size=(7, 4))
        indices = np.array([2, 1, 2, 3, 1, 1, 3])
        silu = lambda z: z / (1 + np.exp(-z))

        def apply(rows, expert, cache):
            gu, down = cache.get(expert)
            gate, up = np.split(rows @ gu.T, 2, axis=-1)
            return (silu(gate) * up) @ down.T

        per_row_cache = MissCountingCache(values)
        expected = np.stack([apply(x[p:p + 1], e, per_row_cache)[0]
                             for p, e in enumerate(indices)])
        unique = np.unique(indices)
        dedup_cache = MissCountingCache(values)
        dedup_cache.record_call = lambda *_args, **_kwargs: None
        forward_class = _production_forward_class()
        layer = forward_class.__new__(forward_class)
        layer.stream = dedup_cache
        actual = np.asarray(layer(_ForwardArray(x[:, None, :]),
                                  _ForwardArray(indices[:, None])))[:, 0]
        self.assertEqual(dedup_cache.loads, len(unique))
        self.assertEqual(per_row_cache.loads, len(indices))
        np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)

    def test_default_config_does_not_enable_streaming(self):
        source = MODULE.read_text()
        self.assertIn("expert_streaming: dict = field(default_factory=dict)", source)
        self.assertIn('if streaming and streaming.get("enabled") else', source)


def _mlx_available():
    try:
        import mlx.core  # noqa: F401
        import mlx_lm  # noqa: F401
        return __import__("sys").platform == "darwin"
    except ImportError:
        return False


@unittest.skipUnless(_mlx_available(), "MLX/Metal integration unavailable")
class ExpertStreamingMetalTest(unittest.TestCase):
    def test_streaming_conversion_parity_and_memory_bound(self):
        """Real conversion/load: prefill, decode, padding, eviction, and memory."""
        import importlib.util
        import mlx.core as mx

        path = ROOT / "tests/align/test_qwen4_exp_canonical.py"
        spec = importlib.util.spec_from_file_location("qwen4_exp_canonical_streaming", path)
        canonical = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(canonical)
        if canonical.SKIP:
            self.skipTest(canonical.SKIP)
        fx = canonical.fixture()
        # Exactly two experts per layer: every nontrivial routing call evicts.
        per_expert = 2 * (2 * canonical.TEXT["moe_intermediate_size"] * canonical.TEXT["hidden_size"]
                          + canonical.TEXT["hidden_size"] * canonical.TEXT["moe_intermediate_size"])
        cache_gb = 2 * per_expert * canonical.TEXT["num_hidden_layers"] / 2**30
        resident = fx.model("bf16")
        streamed = fx.model("bf16", convert_options={"expert_streaming_cache_gb": cache_gb})

        def scenarios(model):
            seq = fx.seqs["seq_a"]
            prefill = canonical.run(model, [seq])[0]
            cache, decode = model.make_cache(), []
            for token in seq:
                decode.append(canonical.run(model, [[token]], cache)[0, 0])
            padded_ids = [seq, [canonical.EOS] * canonical.PAD_B + fx.seqs["seq_b"]]
            padded = canonical.run(model, padded_ids,
                                   model.make_cache(left_padding=[0, canonical.PAD_B]))
            return {"prefill": prefill, "stepwise": np.stack(decode), "padded": padded}

        expected, actual = scenarios(resident), scenarios(streamed)
        noise = canonical.noise_table(fx)
        for name in ("prefill", "stepwise"):
            tolerance = canonical.BF16_VS_B16_RATIO * noise[name]
            self.assertLessEqual(float(np.max(np.abs(actual[name] - expected[name]))), tolerance)
            # Never demand equality: top-1 changes are accepted only at a
            # resident or streamed top-two tie within the same bf16 bound.
            for a, b in zip(actual[name].reshape(-1, actual[name].shape[-1]),
                            expected[name].reshape(-1, expected[name].shape[-1])):
                if a.argmax() != b.argmax():
                    self.assertLessEqual(min(np.partition(a, -2)[-1] - np.partition(a, -2)[-2],
                                             np.partition(b, -2)[-1] - np.partition(b, -2)[-2]), tolerance)
        for row, start, key in ((0, 0, "padded_row0"), (1, canonical.PAD_B, "padded_row1")):
            tolerance = canonical.BF16_VS_B16_RATIO * noise[key]
            self.assertLessEqual(float(np.max(np.abs(actual["padded"][row, start:]
                                                    - expected["padded"][row, start:]))), tolerance)

        counters = streamed.expert_streaming_counters()
        self.assertTrue(all(v["prefill"]["calls"] and v["decode"]["calls"] for v in counters.values()))

        def measured_peak(model):
            mx.clear_cache()
            mx.reset_peak_memory()
            canonical.run(model, [fx.seqs["long"][:256]])
            return mx.get_peak_memory()

        resident_peak = measured_peak(resident)
        streamed_peak = measured_peak(streamed)
        distinct_layer_bound = canonical.TEXT["num_experts"] * per_expert
        self.assertLessEqual(streamed_peak - resident_peak,
                             int(cache_gb * 2**30) + distinct_layer_bound)


if __name__ == "__main__":
    unittest.main()
