"""Lazy, offline MLX implementation of the R0 backend. Never imported by fakes.

Uses the production endpoint, sampler and episode cache; no controller, monitor,
SMC reader or pinned runtime changes. Imports/loads happen only after census.
"""
from __future__ import annotations

import inspect
from pathlib import Path
import time

from joulewise.align.r0 import PINS
from joulewise.align.r0_host import swap_bytes


class ObservedNative:
    def __init__(self, native, guard):
        self.native, self.guard = native, guard
        self.observe = lambda index: None

    def __getattr__(self, name):
        return getattr(self.native, name)

    def stream_generate(self, *args, **kwargs):
        for index, response in enumerate(self.native.stream_generate(*args, **kwargs)):
            self.guard.check()
            self.observe(index + 1)
            yield response


class MlxBackend:
    def __init__(self, tag, source, shade_cache, guard):
        from importlib.metadata import version
        from joulewise.align.apple.endpoint import MlxEndpoint
        from joulewise.align.shade.upstream import PinnedUpstream
        from joulewise.clock import SystemClock
        from joulewise.schemas import BenchmarkConfig
        from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter

        # B1/B2 belong to Stage 1. Fail explicitly instead of shadowing them in
        # desk-only code and thereby certifying a different production path.
        if (not callable(getattr(MlxEndpoint, "assistant_history_message", None))
                or "reasoning_effort" not in inspect.signature(MlxEndpoint).parameters):
            raise RuntimeError("Stage-1 B2 history/effort API missing; integrate before live R0")
        for dist, expected in (("mlx", "0.31.2"), ("mlx-lm", "0.31.3"), ("transformers", "5.12.1")):
            if version(dist) != expected:
                raise RuntimeError(f"stack pin mismatch: {dist} requires {expected}, found {version(dist)}")
        source = Path(source)
        if not source.is_absolute() or not source.is_dir():
            raise ValueError("model.source must be an existing absolute local directory; no downloads")
        self.tag, self.guard = tag, guard
        pin = PINS[tag]
        self.clock = SystemClock()
        self.upstream = PinnedUpstream(cache_dir=shade_cache, allow_fetch=False)
        self.config = BenchmarkConfig.from_mapping({
            "schema_version": "0.1", "run_id": "align-r0-" + tag,
            "model": {"name": pin["name"], "family": pin["family"], "source": str(source),
                      "revision": pin["revision"], "weight_format": "mlx", "context_window": 40960},
            "quantization": {"name": f"int{pin['bits']}", "bits": pin["bits"], "group_size": 64},
            "hardware_target": {"id": "macbook_m3_max", "transport": "local", "runtime_backend": "mlx",
                                "telemetry_backend": "powermetrics", "device_kind": "apple_silicon_unified_memory"},
            "workload_profile": {"name": "align_r0", "prompt_tokens": 2048, "output_tokens": 4096,
                                 "repetitions": 1, "warmup_runs": 1},
            "sampling": {"power_hz": 1, "idle_seconds": 0, "warmup_seconds": 0},
            "run_metadata": {"project": "joulewise", "tags": ["align-r0-selection", "align-model=" + pin["tag"]]},
        })
        guard.check(force=True)
        self.runtime = MlxRuntimeAdapter(self.clock)
        prepared = self.runtime.prepare(self.config)
        if not prepared.ok:
            self.runtime.cleanup(self.config)
            raise RuntimeError(f"model load failed: {prepared.message}")
        self.prepared = prepared.metadata
        import mlx.core as mx
        self.mx = mx
        mx.eval(self.runtime._model.parameters())
        guard.check(force=True)
        self.native = ObservedNative(self.runtime._mlx_lm, guard)
        self.runtime._mlx_lm = self.native
        self.tokenizer = self.runtime._tokenizer
        self.new_session(None)

    def close(self):
        self.endpoint = None
        self.runtime.cleanup(self.config)
        self.mx.clear_cache()

    def new_session(self, effort):
        from joulewise.align.apple.endpoint import MlxEndpoint
        self.endpoint = MlxEndpoint(
            self.runtime, self.config, self.clock, episode_domain="align-r0",
            prepare_metadata=self.prepared, enable_thinking=True, prompt_cache="episode_prefix",
            sampler={"temperature": 1.0 if self.tag == "D" else 0.6, "top_p": 0.95, "top_k": 20, "min_p": 0},
            reasoning_effort=effort,
        )

    def encode(self, text):
        from joulewise.adapters.mlx_runtime import _encode
        return _encode(self.tokenizer, text, add_special_tokens=False)

    def render(self, messages, tools):
        return self.encode(self.endpoint._render_prompt(messages, tools))

    def synthetic_completion(self, index):
        body = ("<tool_call>\n<function=r0_echo>\n<parameter=value>desk-check</parameter>\n</function>\n</tool_call>"
                if self.tag == "D" else '<tool_call>\n{"name":"r0_echo","arguments":{"value":"desk-check"}}\n</tool_call>')
        # Both pinned models prefill <think>\n; generated content begins inside
        # it. Use the exact emitted IDs including the Qwen assistant stop ID.
        raw = f"Check echo {index}.\n</think>\n\n{body}"
        return raw, self.encode(raw + "<|im_end|>")

    def chat(self, messages, tools, max_tokens, seed):
        self.guard.check(force=True)
        result = self.endpoint.chat(messages, tools=tools, max_tokens=max_tokens,
                                    temperature=1.0 if self.tag == "D" else 0.6, seed=seed)
        self.guard.check()
        flags = result.raw_usage.get("joulewise", {}).get("flags", [])
        if any(flag.startswith("endpoint_error:") for flag in flags):
            raise RuntimeError(f"native endpoint failed: {flags}")
        return result

    def last_generation(self):
        return self.endpoint.turn_provenance[-1]["generation"]

    def task(self, pair, seed_index):
        from joulewise.align.shade.task import ShadeTask
        task = ShadeTask(pair, upstream=self.upstream, give_hint=True)
        task.reset(seed_index)
        if task._definition is None:
            raise RuntimeError(f"offline pinned SHADE task unavailable: {task.flags}")
        return task

    def nll(self, ids):
        from mlx_lm.models.cache import make_prompt_cache
        mx = self.mx
        cache = make_prompt_cache(self.runtime._model)
        total, count = 0.0, len(ids) - 1
        for start in range(0, count, 128):
            self.guard.check()
            end = min(count, start + 128)
            logits = self.runtime._model(mx.array([ids[start:end]]), cache=cache).astype(mx.float32)
            targets = mx.array([ids[start + 1:end + 1]])
            losses = mx.logsumexp(logits, axis=-1) - mx.take_along_axis(logits, targets[..., None], axis=-1).squeeze(-1)
            value = mx.sum(losses)
            mx.eval(value, [c.state for c in cache])
            total += value.item()
        del cache
        mx.clear_cache()
        return total / count

    def _fixed_context(self, prompt_size, output_size, *, eval_metadata):
        from joulewise.align.apple.prompt_cache import EpisodePromptCache
        mx = self.mx
        # Fresh episode cache; never re-use ladder state. Natural token IDs
        # give a valid-vocabulary synthetic memory stress, not NLL evidence.
        self.new_session(None)
        cache = EpisodePromptCache(self.runtime._model)
        base = self.encode("A desk check repeats a short neutral sentence. ")
        prompt = (base * ((prompt_size + len(base) - 1) // len(base)))[:prompt_size]
        delta, metadata = cache.prepare(prompt)
        mx.synchronize()
        samples = [{"position": 0, "active_bytes": mx.get_active_memory()}]
        errors = []
        metadata_arrays_evaluated = 0

        def kv_bytes():
            def size(value):
                if isinstance(value, (tuple, list)):
                    return sum(size(v) for v in value)
                return getattr(value, "nbytes", 0)
            return sum(size(c.state) for c in cache.cache if "KVCache" in type(c).__name__)

        def observe(count):
            nonlocal metadata_arrays_evaluated
            # Simulated turn boundaries for the council's first mitigation;
            # no production behavior is changed by this diagnostic probe.
            if eval_metadata and (count % 4096 == 0 or count == output_size):
                arrays = [getattr(c, name) for c in cache.cache for name in ("lengths", "left_padding")
                          if getattr(c, name, None) is not None]
                if arrays:
                    mx.eval(arrays)
                    metadata_arrays_evaluated += len(arrays)
            if count == 1 or count % 256 == 0 or count == output_size:
                mx.synchronize()
                samples.append({"position": prompt_size + count, "active_bytes": mx.get_active_memory(),
                                "kv_cache_bytes": kv_bytes()})
        self.native.observe = observe
        started = time.monotonic()
        record = None
        try:
            self.guard.check(force=True)
            record = self.runtime._generate(delta, prompt, None, output_size, suppress_eos=True,
                                             stream_options={"prompt_cache": cache.cache})
            cache.finish(prompt, record.output_token_ids, metadata)
            if record.output_tokens != output_size:
                errors.append("fixed decode did not emit the full token budget")
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
        finally:
            self.native.observe = lambda index: None
        self.guard.check()  # propagate a latched refusal caught above
        result = {"positions": prompt_size + (record.output_tokens if record else 0),
                  "decode_tokens": record.output_tokens if record else 0,
                  "prompt_tokens": prompt_size, "seconds": time.monotonic() - started,
                  "cache_classes": [type(c).__name__ for c in cache.cache],
                  "memory_samples": samples, "errors": errors, "eval_metadata": eval_metadata,
                  "metadata_arrays_evaluated": metadata_arrays_evaluated,
                  "metadata_evaluation": ("evaluated" if metadata_arrays_evaluated else
                      "metadata_absent_single_stream" if eval_metadata else "not_requested"),
                  "peak_bytes": mx.get_peak_memory()}
        del cache, record
        mx.clear_cache()
        return result

    def long_decode(self, *, eval_metadata):
        return self._fixed_context(2048, 40960 - 2048, eval_metadata=eval_metadata)

    def memory_peak(self, *, context, decode_budget):
        self.mx.reset_peak_memory()
        before = swap_bytes()
        result = self._fixed_context(context - decode_budget, decode_budget, eval_metadata=False)
        result.update(swap_before_bytes=before, swap_after_bytes=swap_bytes())
        return result

    def device_info(self):
        target = self.mx if hasattr(self.mx, "device_info") else self.mx.metal
        return {"status": "pass", "device_info": target.device_info(), "load": self.prepared}
