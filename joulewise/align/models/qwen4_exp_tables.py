"""Backend-independent Qwen4-Exp checkpoint and PLE layout rules.

Derived from the official transformers Qwen4ExpTextNGramEmbedding, not the
community MLX implementation. Keep integer hashing on the CPU: int64 tensors
must never be cast with the floating-point model parameters.
"""
import math
import re


def text_config(config):
    return dict(config.get("text_config", config))


def ngram_layout(config, ple_index=0):
    c = text_config(config)
    heads = (c.get("ngram_size", 3) - 1) * c.get("heads_per_ngram", 8)
    prime = c.get("ngram_vocab_size_base", 20_000_000) - 1
    sizes = []
    for i in range((ple_index + 1) * heads):
        prime += 1
        while prime < 2 or any(prime % d == 0 for d in range(2, math.isqrt(prime) + 1)):
            prime += 1
        if i >= ple_index * heads:
            sizes.append(prime)
    offsets, total = [], 0
    for size in sizes:
        offsets.append(total)
        total += size
    divisor = c.get("make_ngram_vocab_size_divisible_by", 128)
    rows = math.ceil(total / divisor) * divisor
    mask = (1 << 64) - 1
    gamma = 0x9E3779B97F4A7C15
    half = max(1, (((1 << 63) - 1) // max(c["vocab_size"], 1)) // 2)
    multipliers = []
    for i in range(c.get("ngram_size", 3)):
        x = (c.get("seed", 1234) + 10007 * ple_index + gamma * (i + 1)) & mask
        x = (x + gamma) & mask
        x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & mask
        x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & mask
        x ^= x >> 31
        multipliers.append(2 * (x % half) + 1)
    return dict(rows=rows, dim=c.get("ple_embed_dim", c["hidden_size"]) // heads,
                sizes=sizes, offsets=offsets, multipliers=multipliers)


def ngram_ids(ids, previous, config, ple_index=0):
    import numpy as np
    c = text_config(config)
    layout = ngram_layout(c, ple_index)
    eos = c["eos_token_id"]
    eos = eos[0] if isinstance(eos, list) else eos
    history = np.concatenate([previous, ids], axis=1).astype(np.int64)
    positions = np.arange(history.shape[1])
    eos_positions = np.where(history == eos, positions, -1)
    inclusive = np.maximum.accumulate(eos_positions, axis=1)
    prior = np.concatenate([np.full((len(ids), 1), -1), inclusive[:, :-1]], axis=1)
    shifted = [history]
    for shift in range(1, c.get("ngram_size", 3)):
        valid = (positions - prior - 1 >= shift) & (positions >= shift)
        shifted.append(np.where(valid, history[:, np.maximum(positions - shift, 0)], eos))
    blocks = []
    h = c.get("heads_per_ngram", 8)
    for order in range(2, c.get("ngram_size", 3) + 1):
        mixed = shifted[0] * layout["multipliers"][0]
        for p in range(1, order):
            mixed = np.bitwise_xor(mixed, shifted[p] * layout["multipliers"][p])
        sl = slice((order - 2) * h, (order - 1) * h)
        blocks.append(mixed[..., None] % np.array(layout["sizes"][sl]) + np.array(layout["offsets"][sl]))
    return np.concatenate(blocks, axis=-1)[:, -ids.shape[1]:]


CONSTANTS = ("layer_multipliers", "ngram_heads_vocab_sizes", "ngram_heads_offsets")
SHARD_RE = re.compile(r"\.ngram_embedding\.shard_(\d+)\.weight$")


def canonical_name(key):
    if key.startswith(("mtp.", "model.mtp.", "model.visual.", "visual.", "vision_tower.")):
        return None
    if key.startswith("model.language_model."):
        return "model." + key[len("model.language_model."):]
    if key.startswith("language_model."):
        tail = key[len("language_model."):]
        return tail if tail.startswith(("model.", "lm_head.")) else "model." + tail
    return key
