"""Synthetic official checkpoints only; no network or measurement inputs.

CPU checks extract pinned source from this clone's Git objects. Native tests
require MLX importability and the two explicit JW_GOLD_CANONICAL_* paths; they
never try a Metal/CPU fallback probe in an implementation sandbox.
"""
import ast
import importlib.util
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.align.qwen4_gold.canonical_adapter import (
    checkpoint_hash_spec, dependency_sources, import_source, unit_inventory,
)
from joulewise.align.qwen4_gold.core import IndexedCheckpoint, sha256, write_json
from joulewise.align.qwen4_gold.runner import Harness, execute

REPO = Path(__file__).resolve().parents[1]
COMMIT = "65763077aec03235d149517f6c97a7cda987a74c"
MODULE_SHA256 = "f4ec75d16f0af0517b63e202abeef704c9a775e9111949ab003250d51d982c37"
ADAPTER = REPO / "joulewise/align/qwen4_gold/canonical_adapter.py"
HAS_ARRAYS = importlib.util.find_spec("numpy") is not None
HAS_REFERENCE = all(importlib.util.find_spec(n) is not None for n in ("numpy", "torch", "transformers", "safetensors"))
HAS_MLX = importlib.util.find_spec("mlx") is not None and importlib.util.find_spec("mlx.core") is not None
NATIVE_PATHS = bool(os.environ.get("JW_GOLD_CANONICAL_MODULE") and os.environ.get("JW_GOLD_CANONICAL_CONVERTER"))


def pinned_sources(root):
    paths = []
    for source, name in (("joulewise/align/models/qwen4_exp.py", "qwen4_exp.py"),
                         ("scripts/align_convert_qwen4_exp.py", "canonical_converter.py")):
        result = subprocess.run(["git", "show", f"{COMMIT}:{source}"], cwd=REPO, capture_output=True)
        if result.returncode:
            raise unittest.SkipTest("canonical Git object unavailable; no fetch or package-tree fallback")
        raw = result.stdout
        path = root / name
        path.write_bytes(raw)
        paths.append(path)
    return {str(p.resolve()): sha256(p) for p in paths}


def synthetic_sources(root):
    """Provenance tests also work in shallow CI clones without the peer commit."""
    module = root / "qwen4_exp.py"
    module.write_text('VERSION = "synthetic provenance fixture"\n')
    converter = root / "canonical_converter.py"
    converter.write_text(f'MODULE_SHA256 = "{sha256(module)}"\n')
    return {str(p.resolve()): sha256(p) for p in (module, converter)}


def host_rules(source, hashing=False):
    """Execute the canonical host-only definitions verbatim, without MLX.

    This test seam doesn't copy the mapping or hashing logic into production.
    All executed nodes come from the pinned source whose sha is also asserted.
    """
    names = {"hf_to_mlx_key", "is_ngram_table_key", "is_ngram_buffer_key"}
    if hashing:
        names |= {"_splitmix64", "layer_multipliers", "_is_prime", "_primes_after", "NgramHashSpec"}
    tree = ast.parse(source)
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    nodes += [n for n in tree.body if isinstance(n, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id in {"NGRAM_BUFFER_SUFFIXES", "_MASK64", "_PRIME_1",
                                            "_SPLITMIX_GAMMA", "_SPLITMIX_M1", "_SPLITMIX_M2"}
        for t in n.targets)]
    nodes.insert(0, ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0))
    module = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    ns = {"math": math}
    if hashing:
        import numpy as np
        ns["np"] = np
    exec(compile(module, "<canonical host-only test definitions>", "exec"), ns)
    from types import SimpleNamespace
    return SimpleNamespace(**{k: v for k, v in ns.items() if k != "__builtins__"})


class ProvenanceTests(unittest.TestCase):
    def test_exact_source_bytes_and_stale_bytecode_are_not_substituted(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            deps = synthetic_sources(root)
            sources, provenance = dependency_sources({"adapter_dependencies": deps})
            expected = sha256(root / "qwen4_exp.py")
            self.assertEqual(provenance["module"]["sha256"], expected)
            converter = import_source("gold_test_converter", *sources["converter"])
            self.assertEqual(converter.MODULE_SHA256, expected)
            path = root / "probe.py"
            path.write_text("raise AssertionError('path re-read')\n")
            loaded = import_source("gold_test_verified_source", path, b"VALUE = 19\n")
            self.assertEqual(loaded.VALUE, 19)
            path = root / "qwen4_exp.py"
            path.write_bytes(path.read_bytes() + b"\n# changed\n")
            with self.assertRaisesRegex(ValueError, "changed after fingerprinting"):
                dependency_sources({"adapter_dependencies": deps})

    def test_missing_ambiguous_and_restricted_dependencies_fail_before_import(self):
        for deps in ({}, {"/restricted/qwen4_exp.py": "a"*64},
                     {"a/qwen4_exp.py": "a"*64, "b/qwen4_exp.py": "b"*64}):
            with self.subTest(deps=deps), self.assertRaises(ValueError):
                dependency_sources({"adapter_dependencies": deps})

    def test_coordinator_records_and_passes_source_digests(self):
        import argparse
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            deps = synthetic_sources(root)
            args = argparse.Namespace(output=str(root / "out"), dtypes="fp32", input_modes="real", seed=1,
                random_scale=1., mlx_module=str(ADAPTER), adapter_dependency=list(deps),
                ref_python="unused", mlx_python="unused", max_gb=12, timeout=1, resume=False)
            cp = SimpleNamespace(config={"hidden_size": 2, "hc_count": 2}, root=root, weight_map={})
            harness = Harness(args, cp, {}, [], {})
            provenance = json.loads((harness.out / "provenance.json").read_text())
            self.assertEqual(provenance["adapter_dependencies"], deps)
            # Reference error stops before array exports and MLX import. This
            # tests request plumbing independently of either numerical stack.
            if HAS_ARRAYS:
                with patch("joulewise.align.qwen4_gold.runner.execute", return_value={"error": "fixture"}) as call:
                    harness.case("embed", "fp32", {"name": "one", "input_ids": [1]}, "real", None)
                self.assertEqual(call.call_args.args[1]["adapter_dependencies"], deps)


@unittest.skipUnless(HAS_REFERENCE, "optional official CPU reference stack")
class TinyMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.deps = pinned_sources(cls.root)
        cls.sources, _ = dependency_sources({"adapter_dependencies": cls.deps})
        cls.converter = import_source("gold_mapping_test_converter", *cls.sources["converter"])
        cls.rules = host_rules(cls.sources["module"][1], hashing=True)
        cls.fixture = cls.root / "checkpoint"
        result = execute(sys.executable, {"backend": "tiny", "checkpoint": str(cls.fixture)},
                         cls.root / "create", 8, 120)
        if "error" in result:
            cls.temp.cleanup()
            raise AssertionError(result)
        cls.cp = IndexedCheckpoint(cls.fixture)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_tiny_index_mapping_is_complete_and_matches_canonical_parameter_paths(self):
        self.assertEqual(sha256(self.root / "qwen4_exp.py"), MODULE_SHA256)
        inventory, tables, constants, omitted, _ = self.converter.sources(self.fixture, self.rules)
        consumed = [e[2] for entries in inventory.values() for e in entries]
        consumed += [e[2] for entries in tables.values() for e in entries]
        consumed += [e[1] for e in constants]
        self.assertFalse(omitted)
        self.assertEqual(len(consumed), len(set(consumed)))
        self.assertEqual(set(consumed), set(self.cp.weight_map))
        hc = {f"{stem}_hyper_connection.{leaf}.weight" for stem in ("attn", "mlp") for leaf in (
            "hc_norm", "input_mix_weight_down", "input_mix_weight_up", "block_inject_weight")}
        moe = {"mlp." + leaf + ".weight" for leaf in ("gate", "switch_mlp.gate_up_proj", "switch_mlp.down_proj",
            "shared_expert.gate_proj", "shared_expert.up_proj", "shared_expert.down_proj", "shared_expert_gate")}
        linear = {"linear_attn." + leaf for leaf in ("A_log", "dt_bias", "conv1d.weight", "in_proj_qkv.weight",
            "in_proj_z.weight", "in_proj_b.weight", "in_proj_a.weight", "norm.weight", "out_proj.weight")}
        qsa = {"self_attn." + leaf + ".weight" for leaf in ("q_proj", "k_proj", "v_proj", "o_proj", "q_norm", "k_norm",
            "indexer.index_qk_proj", "indexer.q_layernorm", "indexer.k_layernorm")}
        ple = {"ple." + leaf + ".weight" for leaf in ("key_proj", "value_proj", "norm_key", "norm_query", "norm_conv", "conv1d")}
        for i in range(4):
            with self.subTest(layer=i):
                mapped = unit_inventory(self.cp, self.converter, self.rules, str(i))
                self.assertEqual(set(mapped), hc | moe | (qsa if i == 3 else linear) | (ple if i == 1 else set()))
                self.assertEqual(self.converter.target_shape(mapped["mlp.switch_mlp.gate_up_proj.weight"]), (4, 32, 32))
        self.assertEqual(set(unit_inventory(self.cp, self.converter, self.rules, "final")),
                         {p + ".weight" for p in ("hc_norm", "input_mix_weight_down", "input_mix_weight_up")})

    def test_packed_and_unpacked_experts_share_converter_shapes(self):
        from safetensors.torch import load_file, save_file
        import torch
        values = {}
        for path in self.fixture.glob("*.safetensors"):
            values.update(load_file(path))  # tiny fixture only
        # Exercise the released fused layout too; save_pretrained uses unpacked
        # expert leaves, whereas the real released index has packed tensors.
        for layer in range(4):
            base = f"model.layers.{layer}.mlp.experts."
            for leaf, parts in (("gate_up_proj", ("gate", "up")), ("down_proj", ("down",))):
                values[base + leaf] = torch.stack([torch.cat([
                    values.pop(f"{base}{e}.{part}_proj.weight") for part in parts]) for e in range(4)])
        root = self.root / "packed"
        root.mkdir()
        (root / "config.json").write_bytes((self.fixture / "config.json").read_bytes())
        save_file(values, root / "model.safetensors")
        cp = IndexedCheckpoint(root)
        for layer in range(4):
            a = unit_inventory(self.cp, self.converter, self.rules, str(layer))
            b = unit_inventory(cp, self.converter, self.rules, str(layer))
            self.assertEqual(set(a), set(b))
            self.assertEqual({k: self.converter.target_shape(v) for k, v in a.items()},
                             {k: self.converter.target_shape(v) for k, v in b.items()})

    def test_unit_inventory_ignores_unselected_unhashed_shards(self):
        # An offline checkpoint can have unrelated shards not included in this
        # invocation's hashes. Even their headers must not be inventoried.
        path = self.fixture / "unselected.safetensors"
        path.write_bytes(b"not a safetensors header")
        try:
            actual = unit_inventory(self.cp, self.converter, self.rules, "0")
            self.assertIn("mlp.switch_mlp.down_proj.weight", actual)
        finally:
            path.unlink()

    def test_hashing_uses_checkpoint_buffers_for_vector_and_single_token_paths(self):
        import numpy as np
        from types import SimpleNamespace
        args = SimpleNamespace(**self.cp.text)
        args.eos_id = args.eos_token_id
        spec, base = checkpoint_hash_spec(self.cp, self.rules, args, 1)
        ids = np.array([[5, 11, 0, 17, 23]])
        history = np.concatenate([np.full((1, spec.context_len), spec.eos, np.int64), ids], axis=1)
        expected = spec.ngram_ids(history, len(ids[0]))
        np.testing.assert_array_equal(expected[:, -1:], spec.ngram_ids(history[:, -spec.context_len-1:], 1))
        self.assertTrue(base.endswith("layers.1.ple.ple_embedding.ngram_embedding"))
        original_read = self.cp.read
        def altered(name, *a, **kw):
            value = original_read(name, *a, **kw)
            return np.ones_like(value) if name.endswith("layer_multipliers") else value
        with patch.object(self.cp, "read", altered):
            changed, _ = checkpoint_hash_spec(self.cp, self.rules, args, 1)
        self.assertEqual(changed.multipliers, [1] * args.ngram_size)
        self.assertFalse(np.array_equal(expected, changed.ngram_ids(history, len(ids[0]))))
        with patch.object(self.cp, "info", return_value=((3,), "F32")), self.assertRaisesRegex(ValueError, "persistent PLE"):
            checkpoint_hash_spec(self.cp, self.rules, args, 1)


@unittest.skipUnless(HAS_MLX and HAS_REFERENCE and NATIVE_PATHS,
                     "native MLX/Metal, reference stack and explicit canonical source paths required")
class NativeCanonicalAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dependencies = [os.environ["JW_GOLD_CANONICAL_MODULE"], os.environ["JW_GOLD_CANONICAL_CONVERTER"]]
        self.prompts = self.root / "prompts.json"
        # EOS, duplicates, and QSA
        # pruning (9 tokens exceeds budget + ratio) without a large fixture.
        write_json(self.prompts, [{"name": "probe", "input_ids": [5, 11, 5, 23, 0, 31, 37, 41, 43]}])

    def harness(self, dtype):
        from joulewise.align.qwen4_gold.runner import main
        output = self.root / "parity"
        argv = ["--make-tiny", "--checkpoint", str(self.root / "checkpoint"), "--output", str(output),
                "--mlx-module", str(ADAPTER), "--ref-python", sys.executable, "--mlx-python", sys.executable,
                "--dtypes", dtype, "--input-modes", "real,random", "--prompts-json", str(self.prompts), "--timeout", "120"]
        for dep in self.dependencies:
            argv += ["--adapter-dependency", dep]
        self.assertEqual(main(argv), 0, f"inspect {output} for failing traces")
        self.check_reports(output, {dtype})

    def check_reports(self, output, dtypes):
        from joulewise.align.qwen4_gold.core import required_traces
        cp = IndexedCheckpoint(self.root / "checkpoint")
        expected = {"embed", "0", "1", "2", "3", "final", "head"}
        for unit in expected:
            report = json.loads((output / (f"layer-{int(unit):03d}.json" if unit.isdigit() else unit + ".json")).read_text())
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["completed_cases"], len(dtypes)*(1 if unit == "embed" else 2))
            for case in report["cases"]:
                self.assertEqual(case["status"], "PASS")
                self.assertTrue(required_traces(cp.config, unit) <= case["metrics"].keys())
                metadata = case["mlx"]["metadata"]
                self.assertEqual(metadata["module_sha256"], sha256(self.dependencies[0]))
                self.assertEqual(metadata["converter_sha256"], sha256(self.dependencies[1]))
        provenance = json.loads((output / "provenance.json").read_text())
        self.assertEqual(provenance["adapter_dependencies"], {str(Path(p).resolve()): sha256(p) for p in self.dependencies})

    def test_fp32_all_units_make_tiny(self):
        self.harness("fp32")

    def test_bf16_all_units_make_tiny(self):
        self.harness("bf16")

    def test_streaming_tiny_sparse_ple_and_resume(self):
        from tests.test_qwen4_gold_stream import LocalSource, options
        from joulewise.align.qwen4_gold.stream import StreamDriver
        # Create through the same --make-tiny worker, then serve locally. Hub
        # metadata/download calls are replaced; parity workers remain real.
        result = execute(sys.executable, {"backend": "tiny", "checkpoint": str(self.root / "checkpoint")},
                         self.root / "create", 8, 120)
        self.assertNotIn("error", result)
        work = self.root / "stream"
        args = options(work)
        args.mlx_module, args.adapter_dependency = str(ADAPTER), self.dependencies
        args.prompts_json, args.timeout, args.shared_shards = str(self.prompts), 120, "restage"
        driver = StreamDriver(args, LocalSource(self.root / "checkpoint", work))
        self.assertEqual(driver.run()["status"], "PASS")
        self.check_reports(work / "parity", {"fp32", "bf16"})
        args.resume = True
        resumed = StreamDriver(args, LocalSource(self.root / "checkpoint", work))
        with patch.object(resumed, "run_unit", side_effect=AssertionError("completed units reran")):
            self.assertEqual(resumed.run()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
