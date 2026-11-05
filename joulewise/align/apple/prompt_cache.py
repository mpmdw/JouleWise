"""Episode-local native cache reconciliation against represented token IDs.

The ledger contains consumed causal inputs, including consumed EOS IDs. Native
attention offsets witness its length; recurrent layers are never trimmed alone.
No generated text is encoded to reconstruct cache contents.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass


CHECKPOINT_POLICY = "hybrid_boundary_v1"
DEFAULT_CHECKPOINT_LIMIT = 0


def hybrid_checkpoint_policy(config, checkpoint_limit=DEFAULT_CHECKPOINT_LIMIT):
    """Shared identity/runtime policy; None/zero preserve rebuild-only execution."""
    if checkpoint_limit is not None and (type(checkpoint_limit) is not int or checkpoint_limit < 0):
        raise ValueError("hybrid_checkpoint_limit must be a nonnegative integer or null")
    if not checkpoint_limit:
        return None
    cfg = (config or {}).get("text_config", config or {})
    if cfg.get("model_type") in {"qwen3_next", "qwen3_5_text", "qwen3_5", "qwen3_5_moe", "qwen3_5_moe_text"}:
        return {"policy": CHECKPOINT_POLICY, "limit": checkpoint_limit,
                "boundary": "closed_history_token_prefix", "prefill_step_size": 512}
    return None


def common_prefix_length(left, right):
    return next((i for i, (a, b) in enumerate(zip(left, right)) if a != b),
                min(len(left), len(right)))


def _arrays(state):
    if isinstance(state, dict):
        for value in state.values():
            yield from _arrays(value)
    elif isinstance(state, (list, tuple)):
        for value in state:
            yield from _arrays(value)
    elif hasattr(state, "nbytes"):
        yield state


def _recurrent_arrays(layers):
    """Include auxiliary ArraysCache arrays as well as its public state."""
    seen = set()
    for layer in layers:
        for array in _arrays([layer.state, getattr(layer, "__dict__", {})]):
            if id(array) not in seen:
                seen.add(id(array))
                yield array


@dataclass
class _Checkpoint:
    length: int
    offsets: tuple
    recurrent: dict
    state_bytes: int


def checkpoint_size_from_config(config, *, state_itemsize=4, conv_itemsize=2):
    """Batch-one payload; no KV arrays are copied. Dtypes are explicit inputs.

    Gated-delta state is [B, Hv, Dv, Dk]; convolution history is
    [B, kernel-1, 2*Hk*Dk + Hv*Dv]. Python/container overhead is excluded.
    """
    cfg = config.get("text_config", config)
    layers = cfg["num_hidden_layers"]
    kinds = cfg.get("layer_types")
    if kinds is None:
        interval = cfg["full_attention_interval"]
        kinds = ["full_attention" if (i + 1) % interval == 0 else "linear_attention"
                 for i in range(layers)]
    if len(kinds) != layers or set(kinds) - {"linear_attention", "full_attention"}:
        raise ValueError("unsupported_hybrid_layer_config")
    linear = kinds.count("linear_attention")
    attention = kinds.count("full_attention")
    hk, hv = cfg["linear_num_key_heads"], cfg["linear_num_value_heads"]
    dk, dv = cfg["linear_key_head_dim"], cfg["linear_value_head_dim"]
    conv = (cfg["linear_conv_kernel_dim"] - 1) * (2 * hk * dk + hv * dv) * conv_itemsize
    recurrent = hv * dk * dv * state_itemsize
    return {"linear_layers": linear, "attention_layers": attention,
            "conv_bytes_per_layer": conv, "recurrent_bytes_per_layer": recurrent,
            "state_bytes": linear * (conv + recurrent),
            "offset_bytes": attention * 8,
            "checkpoint_bytes": linear * (conv + recurrent) + attention * 8,
            "state_itemsize": state_itemsize, "conv_itemsize": conv_itemsize}


def native_cache_api():
    from mlx_lm.models import cache
    return cache


def ids_digest(ids):
    return hashlib.sha256(json.dumps(ids, separators=(",", ":")).encode()).hexdigest()


class EpisodePromptCache:
    def __init__(self, model, *, checkpoint_limit=DEFAULT_CHECKPOINT_LIMIT):
        if type(checkpoint_limit) is not int or checkpoint_limit < 0:
            raise ValueError("checkpoint_limit must be a nonnegative integer")
        self.model = model
        self.api = native_cache_api()
        self.cache = None
        self.represented_ids = []
        self.checkpoint_limit = checkpoint_limit
        self.checkpoints = []
        self._checkpoint_length = None

    @property
    def hybrid(self):
        # Only the pinned, non-rotating KV + ArraysCache pair is supported.
        # Unknown cache classes retain the established whole-cache fallback.
        kinds = {type(c).__name__ for c in self.cache or ()}
        return kinds == {"KVCache", "ArraysCache"}

    def _snapshot(self):
        length = len(self.represented_ids)
        self.verify_length(length)
        if self.checkpoints and self.checkpoints[-1].length == length:
            return
        recurrent = {i: deepcopy(c)
                     for i, c in enumerate(self.cache) if type(c).__name__ == "ArraysCache"}
        import mlx.core as mx
        arrays = list(_recurrent_arrays(recurrent.values()))
        mx.eval(*arrays)  # materialize before generation can replace/mutate state
        checkpoint = _Checkpoint(length, tuple(getattr(c, "offset", None) for c in self.cache),
                                 recurrent, sum(int(a.nbytes) for a in arrays))
        self.checkpoints = [c for c in self.checkpoints if c.length != length]
        self.checkpoints.append(checkpoint)
        self.checkpoints = self.checkpoints[-self.checkpoint_limit:]

    def _restore(self, checkpoint):
        for i, layer in enumerate(self.cache):
            offset = checkpoint.offsets[i]
            if i in checkpoint.recurrent:
                # Copy the complete ArraysCache, including optional metadata
                # such as lengths/padding. Restoring must not mutate the saved
                # checkpoint on the subsequent forward pass.
                self.cache[i] = deepcopy(checkpoint.recurrent[i])
            else:
                rewind = int(layer.offset) - int(offset)
                if rewind < 0:
                    raise ValueError("cache_checkpoint_wrong_trim")
                actual = layer.trim(rewind)
                if type(actual) is not int or actual != rewind:
                    raise ValueError("cache_checkpoint_wrong_trim")
        import mlx.core as mx
        mx.eval(*list(_arrays([c.state for c in self.cache])))
        self.represented_ids = self.represented_ids[:checkpoint.length]
        self.verify_length(checkpoint.length)

    def prefill_checkpoint(self, delta, metadata, *, step_size=512):
        """Called inside the measured prefill phase, before native generation.

        Stop exactly at the closed-history boundary; leave at least one token
        for generate_step. No sampler calls or generated-text retokenization.
        """
        if self._checkpoint_length is None:
            return delta
        import mlx.core as mx
        count = self._checkpoint_length - len(self.represented_ids)
        if not 0 <= count < len(delta):
            raise ValueError("cache_checkpoint_boundary_invalid")
        for start in range(0, count, step_size):
            chunk = delta[start:min(start + step_size, count)]
            self.model(mx.array([chunk]), cache=self.cache)
            mx.eval(*list(_arrays([c.state for c in self.cache])))
            self.represented_ids.extend(chunk)
        self._snapshot()
        metadata.update(cache_checkpoint_count=len(self.checkpoints),
                        cache_checkpoint_boundary_tokens=self._checkpoint_length,
                        cache_checkpoint_bytes=self.checkpoints[-1].state_bytes + 8 * len(self.offsets()),
                        cache_checkpoint_retained_bytes=sum(c.state_bytes + 8 * len(self.offsets()) for c in self.checkpoints))
        self._checkpoint_length = None
        return delta[count:]

    def plan_checkpoint(self, prompt_ids, stable_prefix_ids):
        if self.hybrid and self.checkpoint_limit:
            boundary = min(common_prefix_length(prompt_ids, stable_prefix_ids), len(prompt_ids) - 1)
            if boundary > 0 and boundary >= len(self.represented_ids):
                self._checkpoint_length = boundary
        return self._checkpoint_length

    def offsets(self):
        return [int(c.offset) for c in self.cache if hasattr(c, "offset")]

    def verify_length(self, expected):
        offsets = self.offsets()
        if not offsets or any(n != expected for n in offsets):
            raise ValueError(f"cache_offset_mismatch:expected={expected},actual={offsets}")
        # Stateful synthetic caches can additionally expose the exact causal
        # inputs. This catches omitted/duplicated prefixes even at equal lengths.
        for c in self.cache:
            if hasattr(c, "represented_tokens") and list(c.represented_tokens) != self.represented_ids:
                raise ValueError("cache_represented_ids_mismatch")

    def prepare(self, prompt_ids, *, stable_prefix_ids=None):
        if not prompt_ids:
            raise ValueError("cache_empty_prompt")
        before = len(self.represented_ids)
        before_digest = ids_digest(self.represented_ids)
        cached = 0
        trimmed = 0
        fallback = None
        rebuilt = False
        restored = None
        self._checkpoint_length = None
        if self.cache is not None:
            self.verify_length(before)
            for a, b in zip(self.represented_ids, prompt_ids):
                if a != b:
                    break
                cached += 1
            # Native generation requires a nonempty fed input, even when the
            # whole prompt is represented already.
            cached = min(cached, len(prompt_ids) - 1)
            rewind = before - cached
            if rewind:
                if self.api.can_trim_prompt_cache(self.cache):
                    actual = self.api.trim_prompt_cache(self.cache, rewind)
                    if type(actual) is not int or actual != rewind:
                        raise ValueError(f"cache_wrong_trim:requested={rewind},actual={actual}")
                    trimmed = rewind
                    self.represented_ids = self.represented_ids[:cached]
                    self.verify_length(cached)
                else:
                    restored = next((c for c in reversed(self.checkpoints) if c.length <= cached), None)
                    if restored is not None:
                        self._restore(restored)
                        trimmed = before - restored.length
                        cached = restored.length
                    else:
                        fallback = "untrimmable_rewrite"
                        rebuilt = True
                        self.cache = None
                        self.represented_ids = []
                        self.checkpoints = []
                        cached = 0
            self.checkpoints = [c for c in self.checkpoints if c.length <= cached]
        created = self.cache is None
        if created:
            self.cache = self.api.make_prompt_cache(self.model)
            self.verify_length(0)
        delta = list(prompt_ids[cached:])
        if self.represented_ids + delta != list(prompt_ids):
            raise ValueError("cache_prompt_partition_mismatch")
        metadata = {
            "cache_policy": "episode_prefix", "cache_accounting_version": "represented_ids_v1",
            "prompt_tokens": len(prompt_ids), "cached_prompt_tokens": cached,
            "prefill_tokens": len(delta), "fed_delta_ids": delta,
            "fed_delta_ids_sha256": ids_digest(delta),
            "cache_classes": [type(c).__name__ for c in self.cache],
            "cache_trimmable": self.api.can_trim_prompt_cache(self.cache),
            "cache_created": created, "cache_rebuilt": rebuilt,
            "cache_trimmed_tokens": trimmed, "cache_fallback_reason": fallback,
            "cache_represented_tokens_before": before,
            "cache_represented_ids_before_sha256": before_digest,
            "cache_reconciled_prefix_sha256": ids_digest(self.represented_ids),
            "cache_offsets_before_prefill": self.offsets(),
        }
        if self.hybrid and self.checkpoint_limit:
            # The actual next render's LCP always gates restoration. A template
            # that rewrites earlier than this candidate safely uses an older
            # checkpoint or rebuilds; a boundary is never trusted on its own.
            if stable_prefix_ids is not None:
                self.plan_checkpoint(prompt_ids, stable_prefix_ids)
            metadata.update(cache_checkpoint_policy=CHECKPOINT_POLICY,
                            cache_checkpoint_limit=self.checkpoint_limit,
                            cache_checkpoint_boundary_tokens=self._checkpoint_length,
                            cache_checkpoint_byte_accounting="array_nbytes_plus_u64_offsets",
                            cache_checkpoint_count=len(self.checkpoints),
                            cache_checkpoint_bytes=(self.checkpoints[-1].state_bytes + 8 * len(self.offsets())) if self.checkpoints else 0,
                            cache_checkpoint_retained_bytes=sum(c.state_bytes + 8 * len(self.offsets()) for c in self.checkpoints),
                            cache_checkpoint_restore_count=int(restored is not None),
                            cache_checkpoint_restore_bytes=(restored.state_bytes + 8 * len(self.offsets())) if restored else 0,
                            cache_checkpoint_restored_tokens=restored.length if restored else 0,
                            cache_prefill_tokens_saved=len(prompt_ids) - len(delta))
        return delta, metadata

    def finish(self, prompt_ids, output_ids, metadata):
        # MLX's asynchronous one-token lookahead consumes each yielded token,
        # including terminal EOS. Read the native offsets rather than assuming
        # every native implementation consumes the last emitted token.
        candidate = list(prompt_ids) + list(output_ids)
        offsets = self.offsets()
        if not offsets or len(set(offsets)) != 1 or not len(prompt_ids) <= offsets[0] <= len(candidate):
            raise ValueError(f"cache_consumed_length_invalid:{offsets}")
        self.represented_ids = candidate[:offsets[0]]
        self.verify_length(len(self.represented_ids))
        metadata.update(cache_offsets_after_generation=offsets,
                        cache_represented_tokens_after=len(self.represented_ids),
                        cache_represented_ids_after_sha256=ids_digest(self.represented_ids),
                        cache_unconsumed_output_tokens=len(candidate) - offsets[0])
