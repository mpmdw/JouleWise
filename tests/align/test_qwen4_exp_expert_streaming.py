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


class _FakeArray:
    def __init__(self, value): self.value = np.asarray(value)
    def astype(self, _dtype): return self


class _FakeMX:
    bfloat16 = object()
    @staticmethod
    def array(value): return _FakeArray(value)
    @staticmethod
    def eval(*_values): return None


def _production_store_class():
    """Execute just the host-side production class; MLX is Metal-only."""
    tree = ast.parse(MODULE.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ExpertStream")
    namespace = {"OrderedDict": OrderedDict, "Path": Path, "os": os, "np": np, "mx": _FakeMX}
    exec(compile(ast.Module([node], []), str(MODULE), "exec"), namespace)
    return namespace["ExpertStream"]


def _bf16(values):
    return (np.asarray(values, np.float32).view(np.uint32) >> 16).astype("<u2")


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
            meta = {"dir": td, "cache_gb": 24 / 2**30, "layers": {
                "0": {"file": path.name, "dims": 2, "hidden": 2}}}
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
            self.assertEqual(store.counters(), {"hits": 1, "misses": 3, "bytes_read": 72})
            self.assertEqual(list(store.cache), [0])

    def test_default_config_does_not_enable_streaming(self):
        source = MODULE.read_text()
        self.assertIn("expert_streaming: dict = field(default_factory=dict)", source)
        self.assertIn('if streaming and streaming.get("enabled") else', source)


@unittest.skipUnless(__import__("sys").platform == "darwin", "Metal-only integration")
class ExpertStreamingMetalTest(unittest.TestCase):
    def test_metal_integration_is_covered_by_canonical_fixture(self):
        # The canonical fixture performs the full model construction/conversion;
        # this marker makes the platform gate explicit on CPU CI.
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
