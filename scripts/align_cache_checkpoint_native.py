"""Offline tiny-model checkpoint gate; never loads weights, tokenizers or data.

Run with the measurement pins and PYTHONPATH=., on a Metal-visible session.
The executable prints JSON and fails rather than skipping an unusable backend.
"""
from __future__ import annotations

import argparse
import gc
import importlib
import importlib.metadata
import json
from pathlib import Path
import resource
import statistics
import sys
import time

from joulewise.align.apple.prompt_cache import (
    EpisodePromptCache, PREFILL_STEP_SIZE, _arrays, checkpoint_size_from_config,
)


PINS = {"mlx": "0.31.2", "mlx-lm": "0.31.3"}
FAMILIES = ("qwen3_next", "qwen3_5")
REWRITES = (143, 257, 560)
STEP = PREFILL_STEP_SIZE
MIB = 1024 ** 2
CONFIG_FIXTURES = {"qwen3_next": "qwen3_next_config.json", "qwen3_5": "qwen38_config.json"}


def payload_projection(family, dtype_name, timings=None):
    """Config-only memory arithmetic; optional timing scenario, never a forecast."""
    if dtype_name not in ("float32", "bfloat16"):
        raise ValueError(dtype_name)
    itemsize = 4 if dtype_name == "float32" else 2
    fixture = Path(__file__).resolve().parents[1] / "tests/align/fixtures" / CONFIG_FIXTURES[family]
    real = checkpoint_size_from_config(json.loads(fixture.read_text()), conv_itemsize=itemsize)
    tiny = checkpoint_size_from_config(tiny_config(family), conv_itemsize=itemsize)
    ratio = real["state_bytes"] / tiny["state_bytes"]
    # Production policy retains two copies; replacement briefly holds three.
    result = dict(family=family, dtype=dtype_name, config_fixture=CONFIG_FIXTURES[family],
                  tiny=tiny, real=real, state_byte_ratio=ratio,
                  two_retained_payload_bytes=2 * real["checkpoint_bytes"],
                  replacement_snapshot_array_bytes=3 * real["state_bytes"],
                  replacement_plus_active_recurrent_array_bytes=4 * real["state_bytes"],
                  byte_proportional_timing_ms=None)
    if timings is not None:
        result["byte_proportional_timing_ms"] = {
            op: values["median_ms"] * ratio for op, values in timings.items()
        }
    return result


def tiny_config(family):
    """Four layers, three recurrent and one full, as in both supplied configs."""
    if family not in FAMILIES:
        raise ValueError(f"unsupported tiny family: {family}")
    text = dict(
        model_type=family, hidden_size=64, num_hidden_layers=4,
        intermediate_size=128, num_attention_heads=2, num_key_value_heads=1,
        head_dim=32, rms_norm_eps=1e-6, vocab_size=64,
        max_position_embeddings=4096, rope_theta=10000., partial_rotary_factor=1.,
        rope_scaling=None, attention_bias=False, tie_word_embeddings=False,
        full_attention_interval=4, linear_conv_kernel_dim=4,
        linear_key_head_dim=32, linear_value_head_dim=32,
        linear_num_key_heads=1,
        linear_num_value_heads=2 if family == "qwen3_next" else 3,
    )
    if family == "qwen3_next":
        text.update(num_experts=4, num_experts_per_tok=2, moe_intermediate_size=16,
                    shared_expert_intermediate_size=16, decoder_sparse_step=1,
                    norm_topk_prob=True, mlp_only_layers=[])
        return text
    text.update(model_type="qwen3_5_text", num_experts=0, rope_parameters={
        "type": "default", "rope_theta": 10000., "partial_rotary_factor": 1.,
    })
    return {"model_type": "qwen3_5", "text_config": text}


def peak_rss_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


class NativeProbe:
    """Small inference models, bounded MLX allocator settings, eager barriers.

    MLX's memory limit is a guideline, not a hard process cap. Tiny dimensions,
    sequential cases and a 900 MiB RSS guard provide additional safeguards.
    No real-config model is ever instantiated.
    """

    def __enter__(self):
        self.previous_limits = []
        for name, expected in PINS.items():
            actual = importlib.metadata.version(name)
            if actual != expected:
                raise RuntimeError(f"{name}: expected {expected}, found {actual}")
        import mlx.core as mx
        self.mx = mx
        try:
            self.previous_limits.append((mx.set_memory_limit, mx.set_memory_limit(384 * MIB)))
            self.previous_limits.append((mx.set_cache_limit, mx.set_cache_limit(32 * MIB)))
            if mx.default_device() != mx.gpu:
                raise RuntimeError("Metal GPU required for the inference-kernel gate")
            # is_available() alone can say True when the sandbox denies a device.
            mx.eval(mx.zeros((1,)))
            mx.synchronize()
            self.check_memory()
        except Exception:
            self.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, *_):
        for setter, old_value in reversed(self.previous_limits):
            setter(old_value)

    def check_memory(self):
        rss = peak_rss_bytes()
        if rss >= 900 * MIB:
            raise MemoryError(f"native probe RSS guard exceeded: {rss} bytes")
        return rss

    def model(self, family, dtype_name):
        mx = self.mx
        module = importlib.import_module(f"mlx_lm.models.{family}")
        from mlx.utils import tree_map
        config = tiny_config(family)
        mx.random.seed(11)
        model = module.Model(module.ModelArgs.from_dict(config))
        model.update(tree_map(lambda a: a.astype(getattr(mx, dtype_name)), model.parameters()))
        model.eval()  # training=True selects the reference recurrence, not Metal.
        mx.eval(model.parameters())
        mx.synchronize()
        self.check_memory()
        if model.training or any(layer.training for layer in model.layers):
            raise AssertionError("native model must be in inference mode")
        return model, config

    def evaluate_cache(self, cache, *outputs):
        self.mx.eval(*outputs, *list(_arrays([c.state for c in cache])))
        self.mx.synchronize()
        self.check_memory()

    def feed(self, model, cache, ids):
        outputs = []
        for start in range(0, len(ids), STEP):
            logits = model(self.mx.array([ids[start:start + STEP]]), cache=cache)
            self.evaluate_cache(cache, logits)
            outputs.append(logits)
        return self.mx.concatenate(outputs, axis=1)

    def difference(self, left, right):
        mx = self.mx
        if left.shape != right.shape or left.dtype != right.dtype:
            raise AssertionError("logit shape/dtype mismatch")
        if not bool(mx.all(mx.isfinite(left)).item()) or not bool(mx.all(mx.isfinite(right)).item()):
            raise AssertionError("non-finite logits")
        bitwise = bool(mx.array_equal(left.view(mx.uint8), right.view(mx.uint8)).item())
        maximum = float(mx.max(mx.abs(left.astype(mx.float32) - right.astype(mx.float32))).item())
        return {"bitwise": bitwise, "max_abs": maximum}

    def exactness(self, family, dtype_name, boundary=STEP):
        """Three consecutive turns discard exactly the pilot's three trim sizes.

        Fresh references re-prefill EVERY token using the same prefix/suffix
        schedule. At boundary=2048 this is also the native full-chunk prefill.
        An additional one-call prefill is diagnostic: its different GEMM shapes
        may differ even when every kernel is individually deterministic.
        """
        mx = self.mx
        model, config = self.model(family, dtype_name)
        state = EpisodePromptCache(model, checkpoint_limit=2)
        prefix = [1 + (i % 23) for i in range(boundary)]
        old_prompt = prefix + [31] * (REWRITES[0] - 7)
        delta, metadata = state.prepare(old_prompt, stable_prefix_ids=prefix)
        delta = state.prefill_checkpoint(delta, metadata)
        self.feed(model, state.cache, delta)
        for token in range(40, 47):
            self.feed(model, state.cache, [token])
        state.finish(old_prompt, list(range(40, 47)), metadata)
        saved = state.checkpoints[-1]
        independent = state.api.make_prompt_cache(model)
        self.feed(model, independent, prefix)
        expected_size = checkpoint_size_from_config(config, conv_itemsize=4 if dtype_name == "float32" else 2)
        if saved.state_bytes != expected_size["state_bytes"]:
            raise AssertionError(f"native payload differs from formula: {saved.state_bytes} != {expected_size}")
        shapes = [{"shape": list(a.shape), "dtype": str(a.dtype), "nbytes": int(a.nbytes)}
                  for a in next(iter(saved.recurrent.values())).state]
        text = config.get("text_config", config)
        hk, hv = text["linear_num_key_heads"], text["linear_num_value_heads"]
        dk, dv = text["linear_key_head_dim"], text["linear_value_head_dim"]
        expected_shapes = [[1, text["linear_conv_kernel_dim"] - 1, 2 * hk * dk + hv * dv],
                           [1, hv, dv, dk]]
        if [a["shape"] for a in shapes] != expected_shapes:
            raise AssertionError(f"unexpected native recurrent shapes: {shapes}")
        if shapes[0]["dtype"] != str(getattr(mx, dtype_name)) or shapes[1]["dtype"] != str(mx.float32):
            raise AssertionError(f"unexpected native recurrent dtypes: {shapes}")

        def snapshot_unchanged():
            for index, layer in saved.recurrent.items():
                for actual, original in zip(layer.state, independent[index].state):
                    if not self.difference(actual, original)["bitwise"]:
                        raise AssertionError("saved recurrence changed after suffix/restore")

        def fresh(ids, *, one_shot=False):
            cache = state.api.make_prompt_cache(model)
            if one_shot:
                logits = model(mx.array([ids]), cache=cache)
                self.evaluate_cache(cache, logits)
                return logits[:, boundary:]
            self.feed(model, cache, ids[:boundary])
            return self.feed(model, cache, ids[boundary:])

        rows = []
        snapshot_unchanged()
        for turn, trim in enumerate(REWRITES):
            suffix_length = REWRITES[turn + 1] - 7 if turn + 1 < len(REWRITES) else 19
            ids = prefix + [48 + turn] * suffix_length
            delta, metadata = state.prepare(ids, stable_prefix_ids=prefix)
            if (metadata["cache_checkpoint_restore_count"] != 1
                    or metadata["cache_trimmed_tokens"] != trim
                    or metadata["cache_checkpoint_restored_tokens"] != boundary
                    or delta != ids[boundary:]):
                raise AssertionError(f"incorrect native restore partition: {metadata}")
            restored = self.feed(model, state.cache, state.prefill_checkpoint(delta, metadata))
            reference = fresh(ids)
            repeated = fresh(ids)
            determinism = self.difference(reference, repeated)
            restored_difference = self.difference(restored, reference)
            bulk_difference = self.difference(restored, fresh(ids, one_shot=True))
            row = dict(family=family, dtype=dtype_name, turn=turn + 2,
                       rewritten_tokens=trim, boundary=boundary,
                       suffix_tokens=len(delta), reference_repeat=determinism,
                       restored_vs_full_reprefill=restored_difference,
                       restored_vs_one_shot=bulk_difference,
                       checkpoint_bytes=expected_size["checkpoint_bytes"],
                       recurrent_arrays_per_layer=shapes,
                       peak_rss_bytes=self.check_memory())
            # Emit evidence before asserting, so a failed gate keeps its errors.
            print(json.dumps({"exactness": row}), flush=True)
            if not determinism["bitwise"]:
                raise AssertionError("reference is nondeterministic; no tolerance is preapproved")
            if not restored_difference["bitwise"]:
                raise AssertionError("deterministic restore differs from full matched-schedule re-prefill")
            for token in range(40, 47):
                self.feed(model, state.cache, [token])
            state.finish(ids, list(range(40, 47)), metadata)
            snapshot_unchanged()
            rows.append(row)
        return rows

    def release(self):
        gc.collect()
        self.mx.clear_cache()
        self.check_memory()

    def benchmark(self, family, dtype_name, samples=25):
        """Time synchronized snapshot/restore, excluding the forward prefill.

        Warm allocator, three untimed warmups, one operation per sample. Report
        operation-local MLX active-memory high water and process-wide peak RSS.
        No claim that a contended laptop provides production latency evidence.
        """
        mx = self.mx
        model, config = self.model(family, dtype_name)
        state = EpisodePromptCache(model, checkpoint_limit=2)
        prefix = [1 + (i % 23) for i in range(STEP)]
        delta, metadata = state.prepare(prefix + [31], stable_prefix_ids=prefix)
        state.prefill_checkpoint(delta, metadata)
        # The suffix [31] is intentionally unconsumed; the cache is at STEP.
        state.verify_length(STEP)
        expected = checkpoint_size_from_config(config, conv_itemsize=4 if dtype_name == "float32" else 2)
        if state.checkpoints[-1].state_bytes != expected["state_bytes"]:
            raise AssertionError("benchmark native payload differs from formula")
        timings = {}
        for operation in ("checkpoint", "restore"):
            rows = []
            for iteration in range(samples + 3):
                if operation == "checkpoint":
                    # Force a new copy rather than the duplicate-offset no-op.
                    state.checkpoints.clear()
                else:
                    tail = [50] * 17
                    self.feed(model, state.cache, tail)
                    state.finish(prefix + tail, [], {})
                mx.synchronize()
                before = mx.get_active_memory()
                mx.reset_peak_memory()
                start = time.perf_counter_ns()
                if operation == "checkpoint":
                    state._snapshot()
                else:
                    state._restore(state.checkpoints[-1])
                mx.synchronize()
                elapsed_ms = (time.perf_counter_ns() - start) / 1e6
                after = mx.get_active_memory()
                peak = mx.get_peak_memory()
                if iteration >= 3:
                    rows.append(dict(ms=elapsed_ms, active_before_bytes=before,
                                     active_after_bytes=after, peak_active_bytes=peak,
                                     peak_extra_active_bytes=max(0, peak - before)))
                self.check_memory()
                state.verify_length(STEP)
            timings[operation] = dict(
                samples=samples, median_ms=statistics.median(r["ms"] for r in rows),
                min_ms=min(r["ms"] for r in rows), max_ms=max(r["ms"] for r in rows),
                max_extra_active_bytes=max(r["peak_extra_active_bytes"] for r in rows),
                samples_raw=rows,
            )
        return dict(family=family, dtype=dtype_name, timings=timings,
                    checkpoint_payload_bytes=expected["checkpoint_bytes"],
                    peak_rss_bytes=self.check_memory(), mlx_cache_bytes=mx.get_cache_memory(),
                    projection=payload_projection(family, dtype_name, timings),
                    timing_projection_caveat="byte proportional scenario only; tiny fixed overhead and bandwidth do not scale uniformly")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=FAMILIES, action="append")
    parser.add_argument("--benchmark", action="store_true", help="measure copy/restore instead of logits")
    parser.add_argument("--estimate-only", action="store_true", help="config arithmetic; does not import MLX")
    parser.add_argument("--samples", type=int, default=25)
    args = parser.parse_args()
    if not 1 <= args.samples <= 100:
        parser.error("--samples must be between 1 and 100")
    if args.estimate_only:
        for family in args.family or FAMILIES:
            for dtype in ("float32", "bfloat16"):
                print(json.dumps({"projection": payload_projection(family, dtype)}))
        return 0
    try:
        with NativeProbe() as probe:
            for family in args.family or FAMILIES:
                for dtype in ("float32", "bfloat16"):
                    if args.benchmark:
                        print(json.dumps({"benchmark": probe.benchmark(family, dtype, args.samples)}), flush=True)
                        probe.release()
                    else:
                        for boundary in (STEP, 73):
                            probe.exactness(family, dtype, boundary)
                            probe.release()
        print(json.dumps({"status": "passed", "pins": PINS}))
        return 0
    except (RuntimeError, AssertionError, MemoryError, ImportError) as error:
        print(json.dumps({"status": "failed", "pins_required": PINS,
                          "error": str(error), "error_type": type(error).__name__,
                          "peak_rss_bytes": peak_rss_bytes()}), flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
