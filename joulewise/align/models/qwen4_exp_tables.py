"""Backend-independent Qwen4-Exp checkpoint and PLE layout rules.

Derived from the official transformers Qwen4ExpTextNGramEmbedding, not the
community MLX implementation. Keep integer hashing on the CPU: int64 tensors
must never be cast with the floating-point model parameters.
"""
import math
import re
from pathlib import Path


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


def row_dtype(dim, storage, group_size=None):
    import numpy as np
    if storage in ("bf16", "fp32"):
        return np.dtype(("<u2" if storage == "bf16" else "<f4", (dim,)))
    if storage not in ("q4", "q8"):
        raise ValueError(f"Unknown PLE storage {storage}")
    group_size = group_size or dim
    if dim % group_size or (storage == "q4" and dim % 2):
        raise ValueError("PLE row dimensions must divide the quantization group / packing")
    return np.dtype([("values", "u1", (dim // 2 if storage == "q4" else dim,)),
                     ("scales", "<f4", (dim // group_size,)),
                     ("biases", "<f4", (dim // group_size,))])


def encode_rows(values, storage, group_size=None):
    """Row-local affine quantization, independent of MLX's GPU packing format."""
    import numpy as np
    x = np.asarray(values, dtype=np.float32)
    if storage == "fp32":
        return x.astype("<f4")
    if storage == "bf16":
        # Round to nearest, ties to even, including fp32 inputs from tiny tests.
        u = x.view(np.uint32)
        return ((u + 0x7fff + ((u >> 16) & 1)) >> 16).astype("<u2")
    dim = x.shape[-1]
    group_size = group_size or dim
    dtype = row_dtype(dim, storage, group_size)
    groups = x.reshape(len(x), -1, group_size)
    low, high = groups.min(axis=-1), groups.max(axis=-1)
    levels = 15 if storage == "q4" else 255
    scales = np.where(high > low, (high - low) / levels, 1).astype(np.float32)
    q = np.rint((groups - low[..., None]) / scales[..., None]).clip(0, levels).astype(np.uint8).reshape(x.shape)
    rows = np.empty(len(x), dtype=dtype)
    rows["values"] = (q[:, ::2] | (q[:, 1::2] << 4)) if storage == "q4" else q
    rows["scales"], rows["biases"] = scales, low
    return rows


class MMapTable:
    """Read-only mmap; the mapping itself is never wrapped in an MLX array.

    Logical bytes and page-span estimates count gathered rows, not physical
    disk I/O (the OS may satisfy reads from its shared page cache).
    """
    def __init__(self, path, rows, dim, storage="bf16", group_size=None):
        import numpy as np
        self.rows, self.dim, self.storage = rows, dim, storage
        self.group_size = group_size or dim
        self.dtype = row_dtype(dim, storage, self.group_size)
        path = Path(path)
        if path.stat().st_size != rows * self.dtype.itemsize:
            raise ValueError(f"PLE file length mismatch: {path}")
        self._map = np.memmap(path, mode="r", dtype=self.dtype, shape=(rows,))
        self.logical_bytes = self.lookups = 0

    def lookup(self, indices):
        import numpy as np
        indices = np.asarray(indices, dtype=np.int64)
        if np.any(indices < 0) or np.any(indices >= self.rows):
            raise IndexError("PLE row index outside table")
        unique, inverse = np.unique(indices, return_inverse=True)
        # Advanced indexing copies exactly the selected rows, never the table.
        gathered = self._map[unique]
        self.logical_bytes += len(unique) * self.dtype.itemsize
        self.lookups += 1
        if self.storage == "bf16":
            values = (gathered.astype(np.uint32) << 16).view(np.float32)
        elif self.storage == "fp32":
            values = gathered
        else:
            packed = gathered["values"]
            if self.storage == "q4":
                q = np.empty((len(unique), self.dim), dtype=np.uint8)
                q[:, ::2], q[:, 1::2] = packed & 15, packed >> 4
            else:
                q = packed
            q = q.reshape(len(unique), -1, self.group_size).astype(np.float32)
            values = (q * gathered["scales"][..., None] + gathered["biases"][..., None]).reshape(len(unique), self.dim)
        return values[inverse].reshape(*indices.shape, self.dim)

    def close(self):
        self._map._mmap.close()
