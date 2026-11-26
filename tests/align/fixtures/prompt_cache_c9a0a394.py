"""Episode-local native cache reconciliation against represented token IDs.

The ledger contains consumed causal inputs, including consumed EOS IDs. Native
attention offsets witness its length; recurrent layers are never trimmed alone.
No generated text is encoded to reconstruct cache contents.
"""
from __future__ import annotations

import hashlib
import json


def native_cache_api():
    from mlx_lm.models import cache
    return cache


def ids_digest(ids):
    return hashlib.sha256(json.dumps(ids, separators=(",", ":")).encode()).hexdigest()


class EpisodePromptCache:
    def __init__(self, model):
        self.model = model
        self.api = native_cache_api()
        self.cache = None
        self.represented_ids = []

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

    def prepare(self, prompt_ids):
        if not prompt_ids:
            raise ValueError("cache_empty_prompt")
        before = len(self.represented_ids)
        before_digest = ids_digest(self.represented_ids)
        cached = 0
        trimmed = 0
        fallback = None
        rebuilt = False
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
                    fallback = "untrimmable_rewrite"
                    rebuilt = True
                    self.cache = None
                    self.represented_ids = []
                    cached = 0
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
