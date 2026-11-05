"""Gold numerical gate; separate reference/MLX interpreters, no network.

Set JW_QWEN_REF_PYTHON and JW_QWEN_MLX_PYTHON for split venvs. Missing optional
dependencies/devices produce explicit skips; a numerical failure never skips.
The tolerances below are acceptance bounds, not claimed observed MLX results.
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOLERANCES = {"fp32": dict(atol=2e-5, rtol=2e-4), "bf16": dict(atol=.004, rtol=.02)}
# Prospective bounds for deterministic tiny-model logits; not observed results.
QUANTIZED_TOLERANCES = {
    "mixed": dict(atol=.04, rtol=.15, rmse=.012),
    "maxfit": dict(atol=.008, rtol=.03, rmse=.002),
    "maxfit5": dict(atol=.016, rtol=.06, rmse=.004),
}


def run(command, timeout=60):
    env = dict(os.environ, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
               OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1",
               TOKENIZERS_PARALLELISM="false")
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise AssertionError(f"{command!r}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def check_maxfit_storage(model, reference, path, profile):
    """Check both serialized headers and loaded native weights, exhaustively."""
    import numpy as np
    import mlx.core as mx
    from mlx.utils import tree_flatten
    from joulewise.align.models.qwen4_exp_tables import MAXFIT_BITS, parameter_shapes
    from scripts.align_convert_qwen4_exp import tensor_header
    config = json.loads((path / "config.json").read_text())
    index = json.loads((path / "model.safetensors.index.json").read_text())["weight_map"]
    shapes = parameter_shapes(config)
    params = dict(tree_flatten(model.parameters()))
    baseline = dict(tree_flatten(reference.parameters()))
    expected_params, expert_modules = set(), set()
    for key, shape in shapes.items():
        if ".ngram_embedding." in key:
            continue
        expected_params.add(key)
        if ".switch_mlp." in key:
            base = key[:-len("weight")]
            expected_params.update((base + "scales", base + "biases"))
            expert_modules.add(key[:-len(".weight")])
            header, _ = tensor_header(path / index[key])
            if header[key]["dtype"] != "U32" or header[key]["shape"] != [*shape[:-1], shape[-1] * MAXFIT_BITS[profile] // 32]:
                raise AssertionError(f"Wrong packed expert storage: {key}")
            for suffix in ("scales", "biases"):
                value = params[base + suffix]
                if value.dtype != mx.bfloat16 or value.shape != (*shape[:-1], shape[-1] // 64):
                    raise AssertionError(f"Wrong bf16 expert metadata: {base + suffix}")
            if params[key].dtype != mx.uint32:
                raise AssertionError(f"Expert weight is not packed: {key}")
        else:
            header, _ = tensor_header(path / index[key])
            if header[key]["dtype"] != "BF16" or params[key].dtype != mx.bfloat16:
                raise AssertionError(f"Non-expert weight is not native bf16: {key}")
            np.testing.assert_array_equal(np.array(params[key].view(mx.uint16)),
                                          np.array(baseline[key].view(mx.uint16)), err_msg=key)
    if set(params) != expected_params or set(index) != expected_params:
        raise AssertionError("Maxfit parameter inventory mismatch")
    records = {k: v for k, v in config["quantization"].items() if k not in ("bits", "group_size", "mode")}
    expected_quant = dict(bits=MAXFIT_BITS[profile], group_size=64, mode="affine")
    if records != {k: expected_quant for k in expert_modules}:
        raise AssertionError("Quantization config must name every expert and no other module")
    modules = dict(model.named_modules())
    for name in expert_modules:
        if modules[name].bits != MAXFIT_BITS[profile] or modules[name].group_size != 64:
            raise AssertionError(f"Wrong loaded native expert precision: {name}")
    for descriptor in config["ple_tables"].values():
        if descriptor["storage"] != "bf16":
            raise AssertionError("Maxfit PLE disk storage must be bf16")
        if (path / descriptor["path"]).stat().st_size != descriptor["rows"] * descriptor["dim"] * 2:
            raise AssertionError("Maxfit PLE disk length mismatch")


def mlx_checks(directory, dtype, profile=None, replay_reference=None):
    import numpy as np
    import mlx.core as mx
    from mlx_lm.utils import load_model
    from mlx_lm.models import cache as api
    from scripts.align_convert_qwen4_exp import convert, sha256, load_verified_model
    directory = Path(directory)
    gold = np.load(directory / "gold.npz")
    ids = gold["ids"].astype(np.int32)
    path = directory / "mlx"
    quantized = profile is not None
    if quantized:
        path = directory / profile
        convert(directory / "hf", path, profile, 64 if profile.startswith("maxfit") else 32)
    model, _ = load_verified_model(path, sha256(path / "manifest.json"))
    model.eval()
    evidence = dict(dtype=dtype, quantized=quantized, profile=profile, checks=[])
    tol = TOLERANCES[dtype]

    if replay_reference:
        # The synthetic fixture has zero indexer projections and nonzero
        # attention K/V. Export the port's actual ordered selection, then
        # monkeypatch the official topk indices in its separate interpreter.
        indexer = model.layers[1].self_attn.indexer
        length, ratio = ids.shape[1], model.args.indexer_compress_ratio
        selected, keep = indexer(mx.zeros((1, length, model.args.hidden_size)),
                                 mx.arange(length)[None], mx.ones((1, length), dtype=mx.bool_), None)
        mx.eval(selected, keep)
        selected, keep = np.array(selected), np.array(keep)
        orders = [(selected[0, i, :model.args.indexer_budget:ratio][
            keep[0, i, :model.args.indexer_budget:ratio]] // ratio).tolist() for i in range(length)]
        order_file = directory / "mlx-qsa-order.json"
        order_file.write_text(json.dumps(orders))
        evidence["reference_replay"] = json.loads(run([
            replay_reference, "-B", str(ROOT / "tests/align/qwen4_exp_reference.py"),
            str(directory), "--replay-qsa-order", str(order_file)]))
        if evidence["reference_replay"]["alternative_ties_max_abs"] <= 1e-6:
            raise AssertionError("Tie fixture did not distinguish arbitrary and forced block selection")
        gold = np.load(directory / "forced-gold.npz")

    def array(value):
        mx.eval(value)
        return np.array(value.astype(mx.float32))

    def close(name, actual, expected, tolerance=None):
        actual = array(actual) if isinstance(actual, mx.array) else actual
        np.testing.assert_allclose(actual, expected, **(tolerance or tol), err_msg=name)
        evidence["checks"].append(dict(name=name, max_abs=float(np.max(np.abs(actual - expected)))))

    inputs = mx.array(ids)
    full = array(model(inputs))
    if quantized:
        reference, _ = load_model(directory / "mlx", strict=True)
        baseline = array(reference(inputs))
        bounds = QUANTIZED_TOLERANCES[profile]
        close(profile + "_vs_bf16", full, baseline, {k: bounds[k] for k in ("atol", "rtol")})
        rmse = float(np.sqrt(np.mean((full - baseline) ** 2)))
        if not np.isfinite(rmse) or rmse > bounds["rmse"]:
            raise AssertionError(f"Quantization RMSE {rmse} > {bounds['rmse']}")
        if profile.startswith("maxfit"):
            check_maxfit_storage(model, reference, path, profile)
            evidence["checks"].append(dict(name="all_non_experts_bf16_exact_and_experts_packed"))
        # Quantization must leave the indexer present and unquantized.
        indexer = model.layers[1].self_attn.indexer.index_qk_proj
        if hasattr(indexer, "scales"):
            raise AssertionError("Indexer was quantized")
        evidence["quantization_rmse"] = rmse
    else:
        close("hf_full_prefill", full, gold["prefill"])
    cache, steps = model.make_cache(), []
    for i in range(ids.shape[1]):
        steps.append(array(model(inputs[:, i:i + 1], cache=cache)))
    steps = np.concatenate(steps, axis=1)
    close("mlx_prefill_stepwise", steps, full)
    if not quantized:
        close("hf_stepwise", steps, gold["stepwise"])
    cache, chunks = model.make_cache(), []
    for i in range(0, ids.shape[1], 3):
        chunks.append(array(model(inputs[:, i:i + 3], cache=cache)))
    chunked = np.concatenate(chunks, axis=1)
    close("chunked_prefill", chunked, full)
    if replay_reference:
        close("hf_forced_chunked", chunked, gold["chunked"])
    if api.can_trim_prompt_cache(cache):
        raise AssertionError("Hybrid recurrent cache must not advertise trimming")
    # Causality with sparse selection active and nonempty query-local tails.
    altered = ids.copy()
    altered[:, -1] = 25
    close("sparse_causality", array(model(mx.array(altered)))[:, :-1], full[:, :-1])
    # Two rows with distinct left padding, including cached continuation.
    padded = np.concatenate([ids, np.concatenate([np.zeros((1, 4), dtype=np.int32), ids[:, :7]], axis=1)], axis=0)
    mask = np.concatenate([np.ones_like(ids, dtype=bool), np.array([[False] * 4 + [True] * 7])])
    batch_cache = model.make_cache()
    batch = array(model(mx.array(padded), cache=batch_cache, attention_mask=mx.array(mask)))
    close("batch_full_row", batch[:1], full)
    close("left_padded_row", batch[1:, 4:], array(model(inputs[:, :7])))
    next_ids = mx.array([[18], [18]])
    continuation = array(model(next_ids, cache=batch_cache))
    close("left_pad_cached_continuation", continuation[1:], array(model(mx.array(
        np.concatenate([ids[:, :7], [[18]]], axis=1).astype(np.int32))))[:, -1:])
    # Snapshot/restore all recurrent and PLE state through native disk cache API.
    cache = model.make_cache()
    array(model(inputs[:, :6], cache=cache))
    snapshot = directory / (profile + "-cache.safetensors" if quantized else "cache.safetensors")
    api.save_prompt_cache(str(snapshot), cache, metadata={"purpose": "synthetic parity"})
    restored = api.load_prompt_cache(str(snapshot))
    suffix = array(model(inputs[:, 6:], cache=cache))
    close("native_snapshot_restore", model(inputs[:, 6:], cache=restored), suffix)
    close("snapshot_matches_fresh", suffix, full[:, 6:])
    for layer_cache in restored:
        if layer_cache.offset != ids.shape[1]:
            raise AssertionError("Restored hybrid offset mismatch")
    # Attention-only prefix crop must trim raw indexer keys with the K/V.
    attention = model.layers[1].self_attn
    hidden = mx.array(np.random.default_rng(91).normal(size=(1, 11, model.args.hidden_size)).astype(np.float32))
    if dtype == "bf16" or quantized:
        hidden = hidden.astype(mx.bfloat16)
    valid = mx.ones((1, 11), dtype=mx.bool_)
    ac = model.make_cache()[1]
    expected = array(attention(hidden, valid, None))
    array(attention(hidden, valid, ac))
    if ac.trim(7) != 7 or ac.raw_keys.shape[1] != 4:
        raise AssertionError("Attention crop lost QSA alignment")
    close("attention_trim_reprefill", attention(hidden[:, 4:], valid[:, 4:], ac), expected[:, 4:])
    try:
        ac.to_quantized()
    except ValueError:
        pass
    else:
        raise AssertionError("QSA cache quantization must fail closed")
    # Production artifacts have no n-gram GPU tensor in parameters.
    from mlx.utils import tree_flatten
    if any("ngram_embedding" in k for k, _ in tree_flatten(model.parameters())):
        raise AssertionError("Offloaded PLE table leaked into model.parameters()")
    print(json.dumps(evidence))


class TestGoldParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = os.environ.get("JW_QWEN_REF_PYTHON")
        if cls.ref is None:
            if not all(importlib.util.find_spec(x) for x in ("torch", "transformers", "numpy")):
                raise unittest.SkipTest("optional reference stack required; set JW_QWEN_REF_PYTHON")
            cls.ref = sys.executable
        cls.mlx = os.environ.get("JW_QWEN_MLX_PYTHON", sys.executable)
        cls.work = tempfile.TemporaryDirectory(prefix="jw-qwen-gold-")
        cls.addClassCleanup(cls.work.cleanup)
        cls.root = Path(cls.work.name)
        for dtype in TOLERANCES:
            stdout = run([cls.ref, "-B", str(ROOT / "tests/align/qwen4_exp_reference.py"),
                          str(cls.root / dtype), "--dtype", dtype])
            print(stdout.strip())
        print(run([cls.ref, "-B", str(ROOT / "tests/align/qwen4_exp_reference.py"),
                   str(cls.root / "fp32-ties"), "--force-qsa-ties"]).strip())
        # Probe in an isolated process: an unavailable device can raise again
        # at interpreter shutdown. It must not hide numerical test failures.
        probe = subprocess.run([cls.mlx, "-B", "-c", "import mlx.core as mx; mx.eval(mx.array([0])); print('MLX_OK')"],
                               cwd=ROOT, capture_output=True, text=True, timeout=30)
        cls.available = probe.returncode == 0 and "MLX_OK" in probe.stdout
        cls.unavailable_reason = probe.stderr.strip()
        if not cls.available and not any(x in cls.unavailable_reason for x in (
                "No Metal device available", "No module named 'mlx'")):
            raise RuntimeError("Unexpected MLX capability failure: " + cls.unavailable_reason)

    def require_mlx(self):
        if not self.available:
            self.skipTest("MLX parity NOT VALIDATED: " + self.unavailable_reason.splitlines()[-1])

    def test_reference_fp32(self):
        report = json.loads((self.root / "fp32/reference.json").read_text())
        self.assertLess(report["reference_prefill_stepwise_max_abs"], 2e-5)

    def test_reference_bf16(self):
        report = json.loads((self.root / "bf16/reference.json").read_text())
        self.assertLess(report["reference_prefill_stepwise_max_abs"], .004)

    def test_gold_fp32(self):
        self.require_mlx()
        print(run([self.mlx, "-B", __file__, "--mlx-worker", str(self.root / "fp32"), "fp32"]))

    def test_gold_bf16(self):
        self.require_mlx()
        print(run([self.mlx, "-B", __file__, "--mlx-worker", str(self.root / "bf16"), "bf16"]))

    def test_gold_fp32_forced_qsa_ties(self):
        self.require_mlx()
        print(run([self.mlx, "-B", __file__, "--mlx-ties-worker", str(self.root / "fp32-ties"), self.ref]))

    def test_mixed_quantization(self):
        self.require_mlx()
        print(run([self.mlx, "-B", __file__, "--mlx-worker", str(self.root / "bf16"), "bf16", "mixed"]))

    def test_maxfit_quantization(self):
        self.require_mlx()
        print(run([self.mlx, "-B", __file__, "--mlx-worker", str(self.root / "bf16"), "bf16", "maxfit"]))

    def test_maxfit5_quantization(self):
        self.require_mlx()
        print(run([self.mlx, "-B", __file__, "--mlx-worker", str(self.root / "bf16"), "bf16", "maxfit5"]))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mlx-worker":
        sys.path.insert(0, str(ROOT))
        mlx_checks(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif len(sys.argv) > 1 and sys.argv[1] == "--mlx-ties-worker":
        sys.path.insert(0, str(ROOT))
        mlx_checks(sys.argv[2], "fp32", replay_reference=sys.argv[3])
    else:
        unittest.main()
