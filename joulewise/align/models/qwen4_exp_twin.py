# Copyright 2026 JouleWise. Independent MLX port of the official Qwen
# ``qwen4_exp`` (Qwen3.8-Flash-Next) text decoder.
#
# Authority: transformers ``models/qwen4_exp/modeling_qwen4_exp.py`` (the copy
# pinned under ``.engine/transformers-qwen4_exp``). Every numbered comment
# ``[ref: Class.method]`` names the reference function a block mirrors.
#
# This file is loaded by mlx-lm 0.31.3 through ``config.json`` ``model_file``
# (``mlx_lm.utils.load_model``), so it must stay self-contained: it imports
# only numpy, mlx and the pinned mlx_lm library. No ``from __future__ import
# annotations``: mlx-lm does not register the module in ``sys.modules``, which
# dataclasses need to resolve string annotations.
"""MLX port of Qwen3.8-Flash-Next (``model_type: qwen4_exp``), text path only.

Architecture (48 layers, 12 x [3 x GatedDeltaNet -> MoE, 1 x QSA -> MoE]):

* Gated residual ("hyper-connections"): the residual stream is ``hc_count``
  (4) copies of the hidden state. Each branch reads a gated mixture of the
  streams and writes back with a per-stream scalar gate.
* Gated DeltaNet linear attention (36 layers) with conv + recurrent state.
* Qwen Sparse Attention (12 layers): gated GQA attention whose key set is
  restricted by a block indexer (mean-pooled key blocks of ``compress_ratio``
  tokens, top ``budget / compress_ratio`` blocks plus the incomplete tail).
* Hashed n-gram "per-layer embedding" (PLE) at decoder layer 2: a 51B-param
  table that is NEVER made GPU-resident here. It lives on disk, memory-mapped,
  and only the looked-up rows are read and dequantized on the host
  (``NgramTable``).
* 512-expert MoE (top-10 + 1 gated shared expert) on every layer.

MTP is not implemented: the reference ignores ``mtp.*`` weights on load
(``_keys_to_ignore_on_load_unexpected``), so it does not affect next-token
logits. Vision is not implemented (text path only; M-RoPE collapses to plain
RoPE for text because all three position rows are equal).
"""

import fcntl
import math
import mmap
import os
import resource
import time
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Sequence

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx_lm.models.base import BaseModelArgs
from mlx_lm.models.cache import ArraysCache, KVCache
from mlx_lm.models.gated_delta import gated_delta_kernel, gated_delta_ops
from mlx_lm.models.switch_layers import SwitchGLU

TWIN_FORMAT_VERSION = "qwen4_exp_twin/v1"
_F32 = mx.float32

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

_ATTN_TYPES = ("indexed_attention", "full_attention")


@dataclass
class TextModelArgs(BaseModelArgs):
    """Mirror of ``Qwen4ExpTextConfig`` (fields + ``__post_init__`` rules)."""

    model_type: str = "qwen4_exp_text"
    vocab_size: int = 248320
    hidden_size: int = 2048
    num_hidden_layers: int = 40
    num_attention_heads: int = 16
    num_key_value_heads: int = 2
    head_dim: int = 256
    hidden_act: str = "silu"
    rms_norm_eps: float = 1e-6
    attention_bias: bool = False
    tie_word_embeddings: bool = False
    max_position_embeddings: int = 32768
    rope_parameters: Optional[Dict[str, Any]] = None
    linear_conv_kernel_dim: int = 4
    linear_key_head_dim: int = 128
    linear_value_head_dim: int = 128
    linear_num_key_heads: int = 16
    linear_num_value_heads: int = 32
    moe_intermediate_size: int = 512
    shared_expert_intermediate_size: int = 512
    num_experts_per_tok: int = 10
    num_experts: int = 512
    norm_topk_prob: bool = True
    layer_types: Optional[List[str]] = None
    full_attention_interval: int = 4
    eos_token_id: Any = None
    hc_count: int = 4
    hc_lowrank: int = 320
    ple_layer_ids: Optional[List[int]] = None
    ple_embed_dim: Optional[int] = None
    ple_conv_kernel_size: int = 4
    ngram_size: int = 3
    heads_per_ngram: int = 8
    ngram_vocab_size_base: int = 20_000_000
    make_ngram_vocab_size_divisible_by: int = 128
    seed: int = 1234
    split_ngram_parts: int = 512
    indexer_n_heads: Optional[int] = None
    indexer_kv_heads: Optional[int] = None
    indexer_head_dim: Optional[int] = None
    indexer_budget: Optional[int] = None
    indexer_compress_ratio: Optional[int] = None
    output_gate_type: Optional[str] = None

    def __post_init__(self):
        # [ref: Qwen4ExpTextConfig.__post_init__]
        self.ple_layer_ids = sorted(set(self.ple_layer_ids or []))
        if self.ple_embed_dim is None:
            self.ple_embed_dim = self.hidden_size
        if self.layer_types is None:
            self.layer_types = [
                "linear_attention"
                if (i + 1) % self.full_attention_interval
                else "indexed_attention"
                for i in range(self.num_hidden_layers)
            ]
        # The released checkpoint says "full_attention" for QSA layers.
        self.layer_types = [
            "indexed_attention" if t in _ATTN_TYPES else t for t in self.layer_types
        ]
        if self.rope_parameters is None:
            self.rope_parameters = {"rope_type": "default", "rope_theta": 10000.0}
        self._validate()

    @property
    def eos_id(self) -> int:
        eos = self.eos_token_id
        return int(eos[0] if isinstance(eos, (list, tuple)) else eos)

    @property
    def rotary_dim(self) -> int:
        factor = self.rope_parameters.get("partial_rotary_factor", 1.0)
        return int(self.head_dim * factor)

    @property
    def block_topk(self) -> int:
        return self.indexer_budget // self.indexer_compress_ratio

    def _validate(self):
        # [ref: Qwen4ExpTextConfig.validate_architecture], restricted to what
        # this port implements. Anything outside it fails loudly.
        bad = sorted(set(self.layer_types) - {"linear_attention", "indexed_attention"})
        if bad:
            raise ValueError(f"unsupported qwen4_exp layer types: {bad}")
        if len(self.layer_types) != self.num_hidden_layers:
            raise ValueError("layer_types length must equal num_hidden_layers")
        if (self.output_gate_type or self.hidden_act) not in ("sigmoid", "silu"):
            raise ValueError("output gate activation must be sigmoid or silu")
        if self.hidden_act != "silu":
            raise ValueError("this port implements hidden_act == 'silu' only")
        if self.hc_count <= 1:
            raise ValueError("qwen4_exp requires hc_count > 1")
        if self.num_experts <= 0:
            raise ValueError(f"num_experts must be > 0, got {self.num_experts}")
        if not 0 < self.num_experts_per_tok <= self.num_experts:
            raise ValueError("num_experts_per_tok must be in [1, num_experts], got "
                             f"{self.num_experts_per_tok} and {self.num_experts}")
        if self.moe_intermediate_size <= 0 or self.shared_expert_intermediate_size <= 0:
            raise ValueError("moe_intermediate_size and shared_expert_intermediate_size must be > 0")
        qsa = (
            self.indexer_n_heads,
            self.indexer_kv_heads,
            self.indexer_head_dim,
            self.indexer_budget,
            self.indexer_compress_ratio,
        )
        if any(v is None for v in qsa):
            raise ValueError("QSA indexer config is required (the reference always builds it)")
        if any(v <= 0 for v in qsa):
            raise ValueError(f"QSA indexer config values must be positive: {qsa}")
        if self.indexer_kv_heads != 1:
            raise ValueError("qwen4_exp QSA requires indexer_kv_heads == 1")
        if self.indexer_budget % self.indexer_compress_ratio:
            raise ValueError("indexer_budget must be divisible by indexer_compress_ratio")
        if self.rotary_dim > self.indexer_head_dim:
            raise ValueError("rotary dims must fit the QSA index head")
        rope_type = self.rope_parameters.get("rope_type", self.rope_parameters.get("type"))
        if rope_type not in (None, "default"):
            # YaRN etc. are not implemented; refuse rather than silently
            # computing different positions than the reference.
            raise ValueError(f"rope_type {rope_type!r} is not implemented by this port")
        if self.linear_num_value_heads % self.linear_num_key_heads:
            raise ValueError("linear value heads must be a multiple of key heads")
        if self.ple_layer_ids:
            heads = (self.ngram_size - 1) * self.heads_per_ngram
            if heads <= 0 or self.ple_embed_dim % heads:
                raise ValueError("ple_embed_dim must be divisible by the n-gram head count")
            for lid in self.ple_layer_ids:
                if not 1 <= lid <= self.num_hidden_layers:
                    raise ValueError(f"ple layer id {lid} out of range")
                if self.layer_types[lid - 1] != "linear_attention":
                    raise ValueError("PLE is only supported on linear_attention layers")
            if self.eos_token_id is None:
                raise ValueError("eos_token_id must be set when PLE layers are enabled")


@dataclass
class ModelArgs(BaseModelArgs):
    model_type: str
    text_config: dict
    twin: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, params):
        if "text_config" not in params:
            return cls(model_type=params["model_type"], text_config=params,
                       twin=params.get("twin", {}))
        return cls(model_type=params["model_type"], text_config=params["text_config"],
                   twin=params.get("twin", {}))


# --------------------------------------------------------------------------
# Hashed n-gram ids  [ref: _splitmix64, _build_layer_multipliers,
#                     _find_nth_prime_after, Qwen4ExpTextNGramEmbedding]
# --------------------------------------------------------------------------

_MASK64 = (1 << 64) - 1
_SPLITMIX_GAMMA = 0x9E3779B97F4A7C15
_SPLITMIX_M1 = 0xBF58476D1CE4E5B9
_SPLITMIX_M2 = 0x94D049BB133111EB
_PRIME_1 = 10007


def _splitmix64(value: int) -> int:
    value = (value + _SPLITMIX_GAMMA) & _MASK64
    value = ((value ^ (value >> 30)) * _SPLITMIX_M1) & _MASK64
    value = ((value ^ (value >> 27)) * _SPLITMIX_M2) & _MASK64
    return (value ^ (value >> 31)) & _MASK64


def layer_multipliers(unigram_vocab_size: int, ngram_size: int, ple_layer_index: int,
                      seed: int) -> List[int]:
    max_long = (1 << 63) - 1
    multiplier_max = max_long // max(unigram_vocab_size, 1)
    half_bound = max(1, multiplier_max // 2)
    base_seed = seed + _PRIME_1 * ple_layer_index
    out = []
    for index in range(ngram_size):
        value = (base_seed + _SPLITMIX_GAMMA * (index + 1)) & _MASK64
        out.append(2 * (_splitmix64(value) % half_bound) + 1)
    return out


def _is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    for divisor in range(3, math.isqrt(value) + 1, 2):
        if value % divisor == 0:
            return False
    return True


def _primes_after(start: int, count: int) -> List[int]:
    """The first ``count`` primes strictly greater than ``start``."""
    out, p = [], start
    while len(out) < count:
        p += 1
        if _is_prime(p):
            out.append(p)
    return out


class NgramHashSpec:
    """Host-side (numpy int64) n-gram id computation for one PLE layer.

    Token ids are < vocab and multipliers are <= (2**63-1)//vocab, so every
    product fits int64 exactly; XOR and the prime remainder are exact too.
    """

    def __init__(self, args: TextModelArgs, ple_layer_index: int):
        self.ngram_size = args.ngram_size
        self.context_len = args.ngram_size - 1
        self.heads_per_ngram = args.heads_per_ngram
        self.ngram_heads = (args.ngram_size - 1) * args.heads_per_ngram
        self.ple_layer_index = ple_layer_index
        self.eos = args.eos_id
        self.head_dim = args.ple_embed_dim // self.ngram_heads
        first = ple_layer_index * self.ngram_heads
        primes = _primes_after(args.ngram_vocab_size_base - 1, first + self.ngram_heads)
        self.head_vocab_sizes = primes[first:first + self.ngram_heads]
        self.head_offsets = list(np.cumsum([0] + self.head_vocab_sizes[:-1]).tolist())
        self.total_vocab_size = int(sum(self.head_vocab_sizes))
        div = args.make_ngram_vocab_size_divisible_by
        self.padded_vocab_size = int(math.ceil(self.total_vocab_size / div) * div)
        self.multipliers = layer_multipliers(args.vocab_size, args.ngram_size,
                                             ple_layer_index, args.seed)
        self._mult = np.asarray(self.multipliers, dtype=np.int64)
        self._sizes = np.asarray(self.head_vocab_sizes, dtype=np.int64)
        self._offsets = np.asarray(self.head_offsets, dtype=np.int64)

    def _shift_right_ignore_eos(self, h: np.ndarray, shift: int) -> np.ndarray:
        # [ref: Qwen4ExpTextNGramEmbedding._shift_right_ignore_eos]
        if shift == 0:
            return h
        B, T = h.shape
        pos = np.arange(T, dtype=np.int64)
        eos_pos = np.where(h == self.eos, pos[None, :], -1)
        prev_incl = np.maximum.accumulate(eos_pos, axis=1)
        prev = np.concatenate([np.full((B, 1), -1, np.int64), prev_incl[:, :-1]], axis=1)
        pos_in_seg = pos[None, :] - (prev + 1)
        src = pos - shift
        shifted = h[:, np.clip(src, 0, None)]
        valid = (pos_in_seg >= shift) & (src[None, :] >= 0)
        return np.where(valid, shifted, self.eos)

    def _ngram_ids_one(self, row: Sequence[int]) -> List[int]:
        """Pure-int fast path for one new token (decode); identical results.

        ``row`` = the last ``context_len + 1`` history tokens. Shift ``s`` of
        the new token is ``row[-1-s]`` unless an EOS occurs in
        ``row[-1-s:-1]`` (the reference ``_shift_right_ignore_eos``).
        """
        eos = self.eos
        n = len(row)
        shifted = [row[-1]]
        blocked = False
        for s in range(1, self.ngram_size):
            src = n - 1 - s
            blocked = blocked or src < 0 or row[src] == eos
            shifted.append(eos if blocked else row[src])
        mult, sizes, offs = self.multipliers, self.head_vocab_sizes, self.head_offsets
        out = []
        mixed = shifted[0] * mult[0]
        for order in range(2, self.ngram_size + 1):
            mixed ^= shifted[order - 1] * mult[order - 1]
            lo = (order - 2) * self.heads_per_ngram
            for h in range(lo, lo + self.heads_per_ngram):
                out.append(mixed % sizes[h] + offs[h])
        return out

    def ngram_ids(self, history: np.ndarray, n_new: int) -> np.ndarray:
        """``history``: (B, context_len + n_new) int64 -> (B, n_new, heads)."""
        if n_new == 1 and history.shape[1] == self.context_len + 1:
            rows = [self._ngram_ids_one([int(v) for v in r]) for r in history]
            return np.asarray(rows, dtype=np.int64)[:, None, :]
        h = history.astype(np.int64, copy=False)
        shifted = [self._shift_right_ignore_eos(h, s) for s in range(self.ngram_size)]
        blocks = []
        for n in range(2, self.ngram_size + 1):
            lo = (n - 2) * self.heads_per_ngram
            hi = lo + self.heads_per_ngram
            mixed = shifted[0] * self._mult[0]
            for p in range(1, n):
                mixed = np.bitwise_xor(mixed, shifted[p] * self._mult[p])
            ids = np.remainder(mixed[..., None], self._sizes[None, None, lo:hi])
            blocks.append(ids + self._offsets[None, None, lo:hi])
        return np.concatenate(blocks, axis=-1)[:, -n_new:]


# --------------------------------------------------------------------------
# Off-GPU n-gram table: memory-mapped rows, dequantize-on-gather
# --------------------------------------------------------------------------

NGRAM_FORMATS = ("f32", "bf16", "q8", "q4")


def ngram_record_layout(fmt: str, dim: int, group_size: int) -> Dict[str, int]:
    if fmt == "f32":
        return {"code_bytes": 4 * dim, "groups": 0, "record_bytes": 4 * dim}
    if fmt == "bf16":
        return {"code_bytes": 2 * dim, "groups": 0, "record_bytes": 2 * dim}
    if fmt in ("q8", "q4"):
        if dim % group_size:
            raise ValueError(f"n-gram dim {dim} not divisible by group size {group_size}")
        bits = 8 if fmt == "q8" else 4
        if bits == 4 and dim % 2:
            raise ValueError("q4 n-gram rows need an even dim")
        groups = dim // group_size
        code_bytes = dim * bits // 8
        # codes | fp16 scales[groups] | fp16 biases[groups]
        return {"code_bytes": code_bytes, "groups": groups,
                "record_bytes": code_bytes + 4 * groups}
    raise ValueError(f"unknown n-gram format {fmt!r}")


def _f32_to_bf16_bits(x: np.ndarray) -> np.ndarray:
    """Round-to-nearest-even float32 -> bfloat16 bit pattern (uint16)."""
    u = np.ascontiguousarray(x, dtype=np.float32).view(np.uint32)
    rounding = ((u >> 16) & 1) + np.uint32(0x7FFF)
    return ((u + rounding) >> 16).astype(np.uint16)


def encode_ngram_rows(x: np.ndarray, fmt: str, group_size: int) -> np.ndarray:
    """Encode float rows (N, dim) to fixed-size records (N, record_bytes) uint8."""
    x = np.ascontiguousarray(x, dtype=np.float32)
    n, dim = x.shape
    lay = ngram_record_layout(fmt, dim, group_size)
    if fmt == "f32":
        return x.view(np.uint8).reshape(n, lay["record_bytes"])
    if fmt == "bf16":
        return _f32_to_bf16_bits(x).view(np.uint8).reshape(n, lay["record_bytes"])
    bits = 8 if fmt == "q8" else 4
    levels = (1 << bits) - 1
    g = lay["groups"]
    xg = x.reshape(n, g, group_size)
    lo = xg.min(axis=-1)
    hi = xg.max(axis=-1)
    if not (np.isfinite(lo).all() and np.isfinite(hi).all()):
        raise ValueError("non-finite n-gram embedding values")
    if max(float(np.abs(lo).max(initial=0)), float(np.abs(hi).max(initial=0))) > 6.0e4:
        raise ValueError("n-gram values exceed the fp16 scale/bias range")
    scale16 = ((hi - lo) / levels).astype(np.float16)
    scale16 = np.where(scale16 == 0, np.float16(1.0), scale16)
    bias16 = lo.astype(np.float16)
    codes = np.rint((xg - bias16.astype(np.float32)[..., None])
                    / scale16.astype(np.float32)[..., None])
    codes = np.clip(codes, 0, levels).astype(np.uint8).reshape(n, dim)
    if bits == 4:
        codes = (codes[:, 0::2] | (codes[:, 1::2] << 4)).astype(np.uint8)
    out = np.empty((n, lay["record_bytes"]), dtype=np.uint8)
    cb = lay["code_bytes"]
    out[:, :cb] = codes
    out[:, cb:cb + 2 * g] = scale16.view(np.uint8).reshape(n, 2 * g)
    out[:, cb + 2 * g:] = bias16.view(np.uint8).reshape(n, 2 * g)
    return out


def decode_ngram_rows(rec: np.ndarray, fmt: str, dim: int, group_size: int) -> np.ndarray:
    """Decode records (N, record_bytes) uint8 back to float32 rows (N, dim)."""
    rec = np.ascontiguousarray(rec)
    n = rec.shape[0]
    lay = ngram_record_layout(fmt, dim, group_size)
    if fmt == "f32":
        return rec.view(np.float32).reshape(n, dim).copy()
    if fmt == "bf16":
        u16 = rec.view(np.uint16).reshape(n, dim)
        return (u16.astype(np.uint32) << 16).view(np.float32)
    cb, g = lay["code_bytes"], lay["groups"]
    codes = rec[:, :cb]
    if fmt == "q4":
        unpacked = np.empty((n, dim), dtype=np.uint8)
        unpacked[:, 0::2] = codes & 0x0F
        unpacked[:, 1::2] = codes >> 4
        codes = unpacked
    scales = np.ascontiguousarray(rec[:, cb:cb + 2 * g]).view(np.float16).astype(np.float32)
    biases = np.ascontiguousarray(rec[:, cb + 2 * g:]).view(np.float16).astype(np.float32)
    x = codes.reshape(n, g, group_size).astype(np.float32) * scales[..., None] + biases[..., None]
    return x.reshape(n, dim)


_F_NOCACHE = 48  # macOS fcntl: bypass the unified buffer cache for this fd


class NgramTable:
    """One PLE layer's n-gram embedding table, kept on disk.

    ``io="mmap"``: rows are gathered from a read-only ``np.memmap``; touched
    pages enter the OS file cache (clean, reclaimable, never wired by MLX).
    ``io="pread"``: rows are read with ``pread`` on an ``F_NOCACHE`` fd, so the
    process never grows a file-cache footprint (each lookup hits the SSD).
    Either way only the looked-up rows are dequantized, on the host.
    """

    PREFETCH_MAX_ROWS = 4096

    def __init__(self, path: os.PathLike, rows: int, dim: int, fmt: str,
                 group_size: int = 32, io: str = "mmap", prefetch: bool = True):
        self.path = Path(path)
        self.rows, self.dim, self.fmt, self.group_size = int(rows), int(dim), fmt, int(group_size)
        self.layout = ngram_record_layout(fmt, self.dim, self.group_size)
        self.record_bytes = self.layout["record_bytes"]
        expected = self.rows * self.record_bytes
        actual = self.path.stat().st_size
        if actual != expected:
            raise ValueError(f"{self.path}: size {actual} != rows*record_bytes {expected}")
        self.io = io
        self.prefetch = prefetch
        self._mm = None
        self._fd = None
        if io == "mmap":
            self._mm = np.memmap(self.path, dtype=np.uint8, mode="r",
                                 shape=(self.rows, self.record_bytes))
        elif io == "pread":
            self._fd = os.open(self.path, os.O_RDONLY)
            try:
                fcntl.fcntl(self._fd, _F_NOCACHE, 1)
            except OSError:
                pass
        else:
            raise ValueError(f"unknown n-gram io mode {io!r}")
        self.lookups = 0
        self.unique_rows = 0
        self.seconds = 0.0
        # Major page faults observed during gathers (mmap mode): a nonzero
        # count means rows were paged in from disk inside the gather.
        self.major_faults = 0

    def close(self):
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        self._mm = None

    def _prefetch(self, ids: np.ndarray) -> None:
        """MADV_WILLNEED each row's pages so cold rows page in concurrently
        instead of as serial faults inside the gather."""
        raw = getattr(self._mm, "_mmap", None)
        if raw is None or not hasattr(raw, "madvise"):
            return
        rb, page = self.record_bytes, mmap.PAGESIZE
        offset = getattr(self._mm, "offset", 0)
        for row in ids.tolist():
            start = offset + row * rb
            first = (start // page) * page
            raw.madvise(mmap.MADV_WILLNEED, first, start + rb - first)

    def _read_rows(self, ids: np.ndarray) -> np.ndarray:
        if self._mm is not None:
            if self.prefetch and ids.size <= self.PREFETCH_MAX_ROWS:
                self._prefetch(ids)
            return np.asarray(self._mm[ids])
        rb = self.record_bytes
        out = np.empty((ids.shape[0], rb), dtype=np.uint8)
        for i, row in enumerate(ids.tolist()):
            buf = os.pread(self._fd, rb, row * rb)
            if len(buf) != rb:
                raise IOError(f"short n-gram read at row {row}")
            out[i] = np.frombuffer(buf, dtype=np.uint8)
        return out

    def gather(self, ids: np.ndarray) -> np.ndarray:
        """``ids`` (...) int64 -> float32 rows (..., dim); dedupes repeated ids."""
        t0 = time.perf_counter()
        faults0 = resource.getrusage(resource.RUSAGE_SELF).ru_majflt
        flat = ids.reshape(-1).astype(np.int64, copy=False)
        if flat.size and (flat.min() < 0 or flat.max() >= self.rows):
            raise IndexError("n-gram id out of table range")
        if flat.size <= 64:                       # decode: dedupe not worth it
            uniq, inverse = flat, None
        else:
            uniq, inverse = np.unique(flat, return_inverse=True)
        rows = decode_ngram_rows(self._read_rows(uniq), self.fmt, self.dim, self.group_size)
        out = (rows if inverse is None else rows[inverse]).reshape(*ids.shape, self.dim)
        self.lookups += int(flat.size)
        self.unique_rows += int(uniq.size)
        self.major_faults += resource.getrusage(resource.RUSAGE_SELF).ru_majflt - faults0
        self.seconds += time.perf_counter() - t0
        return out


# --------------------------------------------------------------------------
# Small numerics helpers (dtype behaviour mirrors the reference)
# --------------------------------------------------------------------------


def _rms(x32: mx.array, eps: float) -> mx.array:
    return mx.fast.rms_norm(x32, None, eps)


class OffsetRMSNorm(nn.Module):
    """[ref: Qwen4ExpTextRMSNorm] fp32 norm, ``* (1 + w)`` in fp32, cast back."""

    def __init__(self, dims: int, eps: float = 1e-6, group_size: Optional[int] = None):
        super().__init__()
        self.weight = mx.zeros((dims,))
        self.eps = eps
        self.group_size = group_size

    def __call__(self, x: mx.array) -> mx.array:
        dt = x.dtype
        h = x.astype(_F32)
        if self.group_size is not None:
            shape = h.shape
            h = _rms(h.reshape(*shape[:-1], -1, self.group_size), self.eps).reshape(shape)
        else:
            h = _rms(h, self.eps)
        return (h * (1.0 + self.weight.astype(_F32))).astype(dt)


class GatedRMSNorm(nn.Module):
    """[ref: Qwen4ExpTextRMSNormGated] norm-before-gate, weight in model dtype."""

    def __init__(self, dims: int, eps: float, activation: str):
        super().__init__()
        self.weight = mx.ones((dims,))
        self.eps = eps
        self.activation = activation

    def __call__(self, x: mx.array, gate: mx.array) -> mx.array:
        dt = x.dtype
        h = _rms(x.astype(_F32), self.eps).astype(dt)
        h = self.weight * h
        g = gate.astype(_F32)
        g = mx.sigmoid(g) if self.activation == "sigmoid" else nn.silu(g)
        return (h.astype(_F32) * g).astype(dt)


class DepthwiseConv(nn.Module):
    """Causal depthwise conv with dilation; weight layout (C, K, 1) like mlx.

    The sum is accumulated in fp32 and rounded once to the input dtype,
    matching a single-rounding conv kernel.
    """

    def __init__(self, channels: int, kernel: int, dilation: int = 1):
        super().__init__()
        self.weight = mx.zeros((channels, kernel, 1))
        self.kernel = kernel
        self.dilation = dilation

    @property
    def history(self) -> int:
        return (self.kernel - 1) * self.dilation

    def __call__(self, full: mx.array, n_out: int) -> mx.array:
        # full: (B, history + n_out, C) -> (B, n_out, C)
        w = self.weight[:, :, 0].astype(_F32)
        f = full.astype(_F32)
        acc = None
        for k in range(self.kernel):
            start = k * self.dilation
            term = f[:, start:start + n_out, :] * w[:, k]
            acc = term if acc is None else acc + term
        return acc.astype(full.dtype)


def silu_rounded_once(x: mx.array) -> mx.array:
    """[ref: ACT2FN["silu"] / F.silu on a low-precision tensor] silu evaluated
    in fp32 and rounded once to ``x.dtype``.

    torch computes bf16 silu internally in fp32 with a single rounding;
    ``nn.silu`` on a bf16 array rounds after the sigmoid and again after the
    multiply (5.4% of bf16 inputs then differ from torch on GPU, vs 1.5% with
    one rounding). Identity cost for fp32 inputs.
    """
    return nn.silu(x.astype(_F32)).astype(x.dtype)


def conv_history_tail(full: mx.array, hist: int) -> mx.array:
    """The last ``hist`` positions of ``full`` (B, T, C): the conv cache.

    ``full[:, -hist:]`` would keep the WHOLE sequence when ``hist == 0``
    (kernel size 1), so the cache would grow every call and the next call's
    conv would read the oldest tokens instead of the new ones.
    """
    return full[:, full.shape[1] - hist:, :]


def rope_inv_freq(args: TextModelArgs) -> mx.array:
    """[ref: Qwen4ExpTextRotaryEmbedding.compute_default_rope_parameters]
    ``1 / base ** (arange(0, dim, 2) / dim)`` in float32, computed on the host.

    The exponent and the reciprocal are float32 as in the reference; the pow
    is evaluated in float64 and rounded once to float32 (its correctly
    rounded value). mlx's float32 ``**`` differed from the reference by 1 ulp
    on 11 of the 32 entries at the released config (rope_theta 1e7,
    rotary_dim 64); the phase error is position x delta, so it grows with
    context (2.65% of bf16 cos/sin entries differed over positions 0-262k).
    torch's CPU float32 pow is not correctly rounded either, so a few other
    (theta, dim) pairs keep 1-ulp entries; the released and test configs are
    bit-identical to the reference (checked by the parity test).
    """
    base = np.float64(np.float32(args.rope_parameters.get("rope_theta", 10000.0)))
    dim = args.rotary_dim
    exponent = np.arange(0, dim, 2, dtype=np.float32) / np.float32(dim)
    powed = np.power(base, exponent.astype(np.float64)).astype(np.float32)
    return mx.array(np.float32(1.0) / powed)


def rope_cos_sin(positions: mx.array, inv_freq: mx.array):
    """positions (...) -> cos, sin (..., rotary_dim) in fp32."""
    freqs = positions.astype(_F32)[..., None] * inv_freq
    emb = mx.concatenate([freqs, freqs], axis=-1)
    return mx.cos(emb), mx.sin(emb)


def apply_rope(x: mx.array, cos: mx.array, sin: mx.array) -> mx.array:
    """[ref: apply_rotary_pos_emb] rotate-half RoPE on the leading dims only."""
    rot = cos.shape[-1]
    cos = cos.astype(x.dtype)
    sin = sin.astype(x.dtype)
    xr, xp = x[..., :rot], x[..., rot:]
    half = rot // 2
    rotated = mx.concatenate([-xr[..., half:], xr[..., :half]], axis=-1)
    out = xr * cos + rotated * sin
    return mx.concatenate([out, xp], axis=-1) if xp.shape[-1] else out


def topk_mask_lowest_index(scores: mx.array, k: int) -> mx.array:
    """Boolean mask of the top-``k`` entries along the last axis.

    Ties at the k-th value are broken toward the LOWEST index (deterministic).
    ``torch.topk`` leaves tie order unspecified; on CPU it picks lowest index
    for small inputs, which is what the parity test exercises.
    """
    n = scores.shape[-1]
    kth = mx.partition(scores, n - k, axis=-1)[..., n - k:n - k + 1]
    gt = scores > kth
    eq = scores == kth
    need = k - gt.astype(mx.int32).sum(axis=-1, keepdims=True)
    rank = mx.cumsum(eq.astype(mx.int32), axis=-1)
    return gt | (eq & (rank <= need))


# --------------------------------------------------------------------------
# Caches
# --------------------------------------------------------------------------


class QSACache(KVCache):
    """KV cache for a QSA layer plus the indexer's key history.

    * ``keys/values``: inherited ``KVCache`` buffers (B, Hkv, L, D).
    * ``idx_keys``: raw indexer keys (B, L, Di), needed to pool blocks.
    * ``blk_keys``: pooled + normed + RoPE'd block keys (B, NBcap, Di).
      Block ``j`` of row ``b`` covers tokens ``[p_b + j*r, p_b + (j+1)*r)``
      where ``p_b`` is that row's left padding; it is computed exactly once,
      when it completes, from its own tokens and its start position only, so
      trimming is exact: slots beyond the new length are simply invalid.
    * Positions are padding-aware: token ``i`` of row ``b`` has position
      ``i - p_b`` (the mlx-lm ``BatchKVCache`` convention).
    """

    def __init__(self, left_padding: Optional[Sequence[int]] = None):
        super().__init__()
        self.left_padding = (None if not left_padding or not any(left_padding)
                             else np.asarray(left_padding, dtype=np.int64))
        self._batch_hint = len(left_padding) if left_padding else None
        self.idx_keys = None
        self.blk_keys = None

    def lp(self, batch: int) -> np.ndarray:
        if self.left_padding is None:
            return np.zeros((batch,), dtype=np.int64)
        if self.left_padding.shape[0] != batch:
            raise ValueError("left padding batch size mismatch")
        return self.left_padding

    def append_index_keys(self, ik: mx.array):
        """Store raw indexer keys for the tokens just added by ``update_and_fetch``."""
        B, S, D = ik.shape
        end = self.offset
        prev = end - S
        if self.idx_keys is None or end > self.idx_keys.shape[1]:
            steps = (self.step + S - 1) // self.step
            fresh = mx.zeros((B, steps * self.step, D), dtype=ik.dtype)
            if self.idx_keys is None:
                self.idx_keys = fresh
            else:
                self.idx_keys = mx.concatenate([self.idx_keys[:, :prev], fresh], axis=1)
        self.idx_keys[:, prev:end, :] = ik

    def write_blocks(self, j: np.ndarray, vals: mx.array):
        B, M, D = vals.shape
        need = int(j.max()) + 1
        if self.blk_keys is None or need > self.blk_keys.shape[1]:
            cap = ((need + 63) // 64) * 64
            fresh = mx.zeros((B, cap, D), dtype=vals.dtype)
            if self.blk_keys is not None:
                old = self.blk_keys.shape[1]
                fresh[:, :old, :] = self.blk_keys
            self.blk_keys = fresh
        idx = mx.broadcast_to(mx.array(j.astype(np.int32))[..., None], (B, M, D))
        self.blk_keys = mx.put_along_axis(self.blk_keys, idx, vals, axis=1)

    @property
    def state(self):
        if self.keys is None:
            return []
        out = [self.keys[..., :self.offset, :], self.values[..., :self.offset, :]]
        if self.idx_keys is not None:
            out.append(self.idx_keys[:, :self.offset])
        if self.blk_keys is not None:
            out.append(self.blk_keys)
        return out

    @state.setter
    def state(self, v):
        raise NotImplementedError("QSACache does not support prompt-cache files")

    def to_quantized(self, group_size: int = 64, bits: int = 4):
        raise NotImplementedError("KV-cache quantization is not implemented for QSA layers")


def make_layer_caches(args: TextModelArgs, left_padding: Optional[Sequence[int]] = None):
    ple_layers = {lid - 1 for lid in args.ple_layer_ids}
    caches = []
    for i, t in enumerate(args.layer_types):
        if t == "linear_attention":
            # [conv, recurrent] (+ [ple_conv, ngram_context] on PLE layers)
            caches.append(ArraysCache(size=4 if i in ple_layers else 2))
        else:
            caches.append(QSACache(left_padding))
    return caches


def snapshot_cache(cache: List[Any]) -> List[Any]:
    """Zero-copy checkpoint: mx arrays are immutable values, ArraysCache slots
    are rebound (never mutated in place), and KV buffers below the current
    offset are never rewritten, so recording offsets + slot references is
    enough to restore exactly."""
    snap = []
    for c in cache:
        if isinstance(c, QSACache):
            snap.append(("qsa", c.offset))
        elif isinstance(c, ArraysCache):
            snap.append(("arrays", list(c.cache)))
        else:
            raise TypeError(f"unsupported cache type {type(c).__name__}")
    return snap


def restore_cache(cache: List[Any], snap: List[Any]) -> None:
    for c, (kind, payload) in zip(cache, snap):
        if kind == "qsa":
            if c.offset < payload:
                raise ValueError("cannot restore a QSA cache forward in time")
            c.trim(c.offset - payload)
        else:
            c.cache = list(payload)


# --------------------------------------------------------------------------
# Blocks
# --------------------------------------------------------------------------


class _Step:
    """Per-forward context shared by all layers."""

    def __init__(self, B: int, S: int, offset: int, lp: np.ndarray, inv_freq: mx.array):
        self.B, self.S, self.offset = B, S, offset
        self.lp = lp
        t = offset + np.arange(S, dtype=np.int64)
        pos = t[None, :] - lp[:, None]
        self.positions_host = pos
        valid = pos >= 0
        self.valid_host = None if valid.all() else valid
        self.valid = None if self.valid_host is None else mx.array(self.valid_host)
        self.cos, self.sin = rope_cos_sin(mx.array(pos.astype(np.int32)), inv_freq)
        self.inv_freq = inv_freq
        self.ngram_emb: Dict[int, mx.array] = {}


class GatedResidual(nn.Module):
    """[ref: Qwen4ExpTextGatedResidual]"""

    def __init__(self, args: TextModelArgs, use_combine: bool = True):
        super().__init__()
        self.hc = args.hc_count
        self.hidden = args.hidden_size
        width = self.hc * self.hidden
        self.hc_norm = OffsetRMSNorm(width, eps=args.rms_norm_eps, group_size=self.hidden)
        self.input_mix_weight_down = nn.Linear(width, args.hc_lowrank, bias=False)
        self.input_mix_weight_up = nn.Linear(args.hc_lowrank, width, bias=False)
        self.use_combine = use_combine
        if use_combine:
            self.block_inject_weight = nn.Linear(width, self.hc, bias=False)

    def __call__(self, hyper_input: mx.array):
        normed = self.hc_norm(hyper_input)
        w = nn.silu(self.input_mix_weight_down(normed) / self.hc)
        w = mx.sigmoid(self.input_mix_weight_up(w))
        shape = (*normed.shape[:-1], self.hc, self.hidden)
        prod = w.reshape(shape) * normed.reshape(shape)
        mixed = prod.astype(_F32).mean(axis=-2).astype(prod.dtype)
        if not self.use_combine:
            return mixed
        inject = 2 * mx.sigmoid(self.block_inject_weight(normed) / self.hc)
        return mixed, hyper_input, inject


def _inject(hyper_input: mx.array, branch: mx.array, weights: mx.array) -> mx.array:
    # [ref: Qwen4ExpTextDecoderLayer.forward] hyper + (out ⊗ w).flatten
    injection = branch[..., None, :] * weights[..., :, None]
    return hyper_input + injection.reshape(hyper_input.shape)


class GatedDeltaNet(nn.Module):
    """[ref: Qwen4ExpTextGatedDeltaNet] recurrent form for prefill and decode."""

    def __init__(self, args: TextModelArgs):
        super().__init__()
        self.hidden = args.hidden_size
        self.hv = args.linear_num_value_heads
        self.hk = args.linear_num_key_heads
        self.dk = args.linear_key_head_dim
        self.dv = args.linear_value_head_dim
        self.key_dim = self.hk * self.dk
        self.value_dim = self.hv * self.dv
        self.conv_dim = 2 * self.key_dim + self.value_dim
        # mlx-lm's Metal gated_delta_kernel splits Dk over one 32-lane
        # simdgroup (n_per_t = Dk / 32): Dk < 32 fails to compile and any
        # other non-multiple of 32 silently covers only part of the key dims.
        # Such configs use the exact ops recurrence instead.
        self.metal_kernel_ok = self.dk % 32 == 0
        self.kernel = args.linear_conv_kernel_dim
        self.conv1d = DepthwiseConv(self.conv_dim, self.kernel)
        self.in_proj_qkv = nn.Linear(self.hidden, self.conv_dim, bias=False)
        self.in_proj_z = nn.Linear(self.hidden, self.value_dim, bias=False)
        self.in_proj_b = nn.Linear(self.hidden, self.hv, bias=False)
        self.in_proj_a = nn.Linear(self.hidden, self.hv, bias=False)
        self.dt_bias = mx.ones((self.hv,))
        self.A_log = mx.zeros((self.hv,))
        self.norm = GatedRMSNorm(self.dv, args.rms_norm_eps,
                                 args.output_gate_type or args.hidden_act)
        self.out_proj = nn.Linear(self.value_dim, self.hidden, bias=False)

    def __call__(self, x: mx.array, step: _Step, cache: Optional[ArraysCache]) -> mx.array:
        B, S, _ = x.shape
        dt = x.dtype
        if step.valid is not None:
            x = mx.where(step.valid[..., None], x, mx.zeros((), dt))
        qkv = self.in_proj_qkv(x)
        z = self.in_proj_z(x).reshape(B, S, self.hv, self.dv)
        b = self.in_proj_b(x)
        a = self.in_proj_a(x)

        hist = self.kernel - 1
        conv_state = cache[0] if cache is not None and cache[0] is not None else None
        if conv_state is None:
            conv_state = mx.zeros((B, hist, self.conv_dim), dtype=qkv.dtype)
        full = mx.concatenate([conv_state, qkv], axis=1)
        if cache is not None:
            cache[0] = conv_history_tail(full, hist)
        # [ref: causal_conv1d_fn/_update] conv rounded to bf16, then silu
        # (fp32 inside, one rounding)
        conv = silu_rounded_once(self.conv1d(full, S))

        q, k, v = mx.split(conv, [self.key_dim, 2 * self.key_dim], axis=-1)
        q = q.reshape(B, S, self.hk, self.dk).astype(_F32)
        k = k.reshape(B, S, self.hk, self.dk).astype(_F32)
        v = v.reshape(B, S, self.hv, self.dv).astype(_F32)
        # [ref: l2norm(eps=1e-6) on the sum of squares, then q * Dk**-0.5]
        q = q * mx.rsqrt((q * q).sum(axis=-1, keepdims=True) + 1e-6) * (self.dk ** -0.5)
        k = k * mx.rsqrt((k * k).sum(axis=-1, keepdims=True) + 1e-6)
        beta = mx.sigmoid(b).astype(_F32)
        g = -mx.exp(self.A_log.astype(_F32)) * nn.softplus(
            a.astype(_F32) + self.dt_bias.astype(_F32))
        decay = mx.exp(g)

        state = cache[1] if cache is not None and cache[1] is not None else None
        if state is None:
            state = mx.zeros((B, self.hv, self.dv, self.dk), dtype=_F32)
        if self.metal_kernel_ok and mx.default_device() == mx.gpu and mx.metal.is_available():
            out, state = gated_delta_kernel(q, k, v, decay, beta, state)
        else:
            out, state = gated_delta_ops(q, k, v, decay, beta, state)
        if cache is not None:
            cache[1] = state

        out = self.norm(out.astype(dt), z)
        return self.out_proj(out.reshape(B, S, -1))


class QSAIndexer(nn.Module):
    """[ref: Qwen4ExpTextQSAIndexer] block selection -> boolean attention mask."""

    def __init__(self, args: TextModelArgs):
        super().__init__()
        self.n_heads = args.indexer_n_heads
        self.head_dim = args.indexer_head_dim
        self.ratio = args.indexer_compress_ratio
        self.block_topk = args.block_topk
        self.index_qk_proj = nn.Linear(
            args.hidden_size, (self.n_heads + args.indexer_kv_heads) * self.head_dim, bias=False)
        self.q_layernorm = OffsetRMSNorm(self.head_dim, eps=args.rms_norm_eps)
        self.k_layernorm = OffsetRMSNorm(self.head_dim, eps=args.rms_norm_eps)
        # Diagnostics only (underscore: never an MLX parameter).
        self._last_selection = None
        self._last_stats = None

    def _update_blocks(self, cache: QSACache, S: int, inv_freq: mx.array):
        B = cache.idx_keys.shape[0]
        r = self.ratio
        L_new = cache.offset
        L_old = L_new - S
        lp = cache.lp(B)
        nb_old = np.maximum(L_old - lp, 0) // r
        nb_new = np.maximum(L_new - lp, 0) // r
        M = int((nb_new - nb_old).max())
        if M <= 0:
            return
        j = nb_old[:, None] + np.arange(M, dtype=np.int64)[None, :]
        tok = lp[:, None, None] + j[..., None] * r + np.arange(r, dtype=np.int64)
        tok = np.clip(tok, 0, L_new - 1).reshape(B, M * r)
        raw = mx.take_along_axis(cache.idx_keys,
                                 mx.array(tok.astype(np.int32))[..., None], axis=1)
        raw = raw.reshape(B, M, r, self.head_dim)
        pooled = raw.astype(_F32).mean(axis=2).astype(raw.dtype)
        pooled = self.k_layernorm(pooled)
        cos, sin = rope_cos_sin(mx.array((j * r).astype(np.int32)), inv_freq)
        pooled = apply_rope(pooled, cos, sin)
        cache.write_blocks(j, pooled)

    def __call__(self, x: mx.array, step: _Step, cache: QSACache):
        B, S, _ = x.shape
        qk = self.index_qk_proj(x)
        iq = qk[..., :self.n_heads * self.head_dim].reshape(B, S, self.n_heads, self.head_dim)
        ik = qk[..., self.n_heads * self.head_dim:]
        iq = self.q_layernorm(iq)
        iq = apply_rope(iq, step.cos[:, :, None, :], step.sin[:, :, None, :])
        cache.append_index_keys(ik)
        self._update_blocks(cache, S, step.inv_freq)
        return self._mask(iq, step, cache)

    def _mask(self, iq: mx.array, step: _Step, cache: QSACache):
        B, S = iq.shape[:2]
        r, K = self.ratio, self.block_topk
        L = cache.offset
        L_old = L - S
        lp = cache.lp(B)
        t = L_old + np.arange(S, dtype=np.int64)
        padded = bool(lp.any())
        NB = int((np.maximum(L - lp, 0) // r).max())
        pad_q = t[None, :] < lp[:, None]

        if NB <= K:
            # Every complete block is selected for every query: QSA reduces
            # exactly to causal (+padding) attention.
            self._last_selection = None
            self._last_stats = SimpleNamespace(queries=B * S, sparse_queries=0,
                                               excluded_block_tokens=0)
            if not padded:
                return "causal" if S > 1 else None
            ar = np.arange(L, dtype=np.int64)
            m = (ar[None, None, :] <= t[None, :, None]) & (ar[None, None, :] >= lp[:, None, None])
            m |= (ar[None, None, :] == t[None, :, None]) & pad_q[..., None]
            return mx.array(m)[:, None]

        n_t = np.maximum(t[None, :] - lp[:, None] + 1, 0) // r            # (B, S)
        # Plain object (not a dict) so it never joins the MLX module tree.
        self._last_stats = SimpleNamespace(
            queries=B * S, sparse_queries=int((n_t > K).sum()),
            excluded_block_tokens=int((np.maximum(n_t - K, 0) * r).sum()))
        bk = cache.blk_keys[:, :NB].astype(_F32)                            # (B, NB, Di)
        bkT = bk.transpose(0, 2, 1)
        iqf = iq.astype(_F32)
        acc = None
        for h in range(self.n_heads):
            s = mx.maximum(iqf[:, :, h, :] @ bkT, 0.0)
            acc = s if acc is None else acc + s
        scores = acc / math.sqrt(self.head_dim)                             # (B, S, NB)
        n_t_mx = mx.array(n_t.astype(np.int32))
        valid_blk = mx.arange(NB)[None, None, :] < n_t_mx[..., None]
        scores = mx.where(valid_blk, scores, -mx.inf)
        sel_blk = topk_mask_lowest_index(scores, K) & valid_blk             # (B, S, NB)
        self._last_selection = sel_blk

        ar = mx.arange(L)
        if not padded:
            tok_sel = mx.repeat(sel_blk, r, axis=-1)
            if NB * r < L:
                tok_sel = mx.concatenate(
                    [tok_sel, mx.zeros((B, S, L - NB * r), dtype=mx.bool_)], axis=-1)
        else:
            blk_of_tok = (np.arange(L, dtype=np.int64)[None, :] - lp[:, None]) // r  # (B, L)
            in_block = mx.array((blk_of_tok >= 0) & (blk_of_tok < NB))
            gidx = mx.array(np.clip(blk_of_tok, 0, NB - 1).astype(np.int32))
            gidx = mx.broadcast_to(gidx[:, None, :], (B, S, L))
            tok_sel = mx.take_along_axis(sel_blk, gidx, axis=2) & in_block[:, None, :]
        lp_mx = mx.array(lp.astype(np.int32))
        t_mx = mx.array(t.astype(np.int32))
        tail_start = lp_mx[:, None] + n_t_mx * r                            # (B, S)
        tail = ar[None, None, :] >= tail_start[..., None]
        causal = ar[None, None, :] <= t_mx[None, :, None]
        real = ar[None, None, :] >= lp_mx[:, None, None]
        mask = causal & real & (tok_sel | tail)
        if pad_q.any():
            diag = ar[None, None, :] == t_mx[None, :, None]
            mask = mask | (diag & mx.array(pad_q)[..., None])
        return mask[:, None]


class QSAAttention(nn.Module):
    """[ref: Qwen4ExpTextAttention] gated GQA attention with the QSA mask.

    mlx 0.31.2 has no fused full-attention kernel for head_dim 256, so SDPA
    falls back to materialising (B, Hq, S, L) scores. Queries are therefore
    processed in chunks of ``query_chunk`` rows (rows are independent, so the
    result is unchanged) to bound that transient at long context.
    """

    query_chunk = 512

    def __init__(self, args: TextModelArgs):
        super().__init__()
        self.n_heads = args.num_attention_heads
        self.n_kv = args.num_key_value_heads
        self.head_dim = args.head_dim
        self.scale = self.head_dim ** -0.5
        bias = args.attention_bias
        self.q_proj = nn.Linear(args.hidden_size, self.n_heads * self.head_dim * 2, bias=bias)
        self.k_proj = nn.Linear(args.hidden_size, self.n_kv * self.head_dim, bias=bias)
        self.v_proj = nn.Linear(args.hidden_size, self.n_kv * self.head_dim, bias=bias)
        self.o_proj = nn.Linear(self.n_heads * self.head_dim, args.hidden_size, bias=bias)
        self.q_norm = OffsetRMSNorm(self.head_dim, eps=args.rms_norm_eps)
        self.k_norm = OffsetRMSNorm(self.head_dim, eps=args.rms_norm_eps)
        self.indexer = QSAIndexer(args)

    def __call__(self, x: mx.array, step: _Step, cache: QSACache) -> mx.array:
        B, S, _ = x.shape
        D = self.head_dim
        qg = self.q_proj(x).reshape(B, S, self.n_heads, 2 * D)
        q, gate = qg[..., :D], qg[..., D:]
        gate = gate.reshape(B, S, self.n_heads * D)
        q = self.q_norm(q).transpose(0, 2, 1, 3)
        k = self.k_norm(self.k_proj(x).reshape(B, S, self.n_kv, D)).transpose(0, 2, 1, 3)
        v = self.v_proj(x).reshape(B, S, self.n_kv, D).transpose(0, 2, 1, 3)
        cos, sin = step.cos[:, None], step.sin[:, None]
        q = apply_rope(q, cos, sin)
        k = apply_rope(k, cos, sin)
        keys, values = cache.update_and_fetch(k, v)
        mask = self.indexer(x, step, cache)
        if S <= self.query_chunk:
            out = mx.fast.scaled_dot_product_attention(q, keys, values, scale=self.scale, mask=mask)
        else:
            L = keys.shape[2]
            outs = []
            for s0 in range(0, S, self.query_chunk):
                s1 = min(S, s0 + self.query_chunk)
                end = L - S + s1                      # no key beyond the last query is visible
                if isinstance(mask, str):             # "causal"
                    rows = mx.arange(L - S + s0, end)
                    m = (mx.arange(end)[None, :] <= rows[:, None])[None, None]
                else:
                    m = mask[:, :, s0:s1, :end]
                outs.append(mx.fast.scaled_dot_product_attention(
                    q[:, :, s0:s1], keys[:, :, :end], values[:, :, :end], scale=self.scale, mask=m))
            out = mx.concatenate(outs, axis=2)
        out = out.transpose(0, 2, 1, 3).reshape(B, S, -1)
        out = out * mx.sigmoid(gate)
        return self.o_proj(out)


class MLP(nn.Module):
    def __init__(self, dim: int, hidden: int):
        super().__init__()
        self.gate_proj = nn.Linear(dim, hidden, bias=False)
        self.up_proj = nn.Linear(dim, hidden, bias=False)
        self.down_proj = nn.Linear(hidden, dim, bias=False)

    def __call__(self, x):
        return self.down_proj(nn.silu(self.gate_proj(x)) * self.up_proj(x))


class SparseMoeBlock(nn.Module):
    """[ref: Qwen4ExpTextSparseMoeBlock + TopKRouter]

    Router softmax/top-k/renormalisation run in fp32 (the reference does
    ``softmax(dtype=float)``); mlx-lm's stock Qwen MoE uses bf16 here.
    """

    def __init__(self, args: TextModelArgs):
        super().__init__()
        self.top_k = args.num_experts_per_tok
        self.norm_topk_prob = args.norm_topk_prob
        self.gate = nn.Linear(args.hidden_size, args.num_experts, bias=False)
        self.switch_mlp = SwitchGLU(args.hidden_size, args.moe_intermediate_size, args.num_experts)
        self.shared_expert = MLP(args.hidden_size, args.shared_expert_intermediate_size)
        self.shared_expert_gate = nn.Linear(args.hidden_size, 1, bias=False)

    def __call__(self, x: mx.array) -> mx.array:
        logits = self.gate(x)
        probs = mx.softmax(logits.astype(_F32), axis=-1)
        k = self.top_k
        inds = mx.argpartition(-probs, kth=k - 1, axis=-1)[..., :k]
        scores = mx.take_along_axis(probs, inds, axis=-1)
        if self.norm_topk_prob:
            scores = scores / scores.sum(axis=-1, keepdims=True)
        scores = scores.astype(logits.dtype)
        y = self.switch_mlp(x, inds)
        y = (y * scores[..., None]).astype(_F32).sum(axis=-2).astype(x.dtype)
        shared = mx.sigmoid(self.shared_expert_gate(x)) * self.shared_expert(x)
        return y + shared


class PLELayer(nn.Module):
    """[ref: Qwen4ExpTextPLELayer] (the n-gram rows arrive pre-gathered)."""

    def __init__(self, args: TextModelArgs):
        super().__init__()
        self.hidden = args.hidden_size
        self.hc = args.hc_count
        width = self.hidden * self.hc
        self.key_proj = nn.Linear(args.ple_embed_dim, width, bias=False)
        self.value_proj = nn.Linear(args.ple_embed_dim, self.hidden, bias=False)
        self.norm_key = OffsetRMSNorm(width, eps=args.rms_norm_eps, group_size=self.hidden)
        self.norm_query = OffsetRMSNorm(width, eps=args.rms_norm_eps, group_size=self.hidden)
        self.norm_conv = OffsetRMSNorm(width, eps=args.rms_norm_eps, group_size=self.hidden)
        self.conv1d = DepthwiseConv(width, args.ple_conv_kernel_size, dilation=args.ngram_size)

    def __call__(self, h: mx.array, emb: mx.array, step: _Step,
                 cache: Optional[ArraysCache]) -> mx.array:
        B, S, _ = h.shape
        dt = h.dtype
        shape = (B, S, self.hc, self.hidden)
        key = self.norm_key(self.key_proj(emb)).reshape(shape)
        value = self.value_proj(emb)
        query = self.norm_query(h).reshape(shape)
        prod = key * query
        gate = prod.astype(_F32).sum(axis=-1, keepdims=True).astype(dt) / math.sqrt(self.hidden)
        gate = mx.sqrt(mx.maximum(mx.abs(gate), 1e-6)) * mx.sign(gate)
        gated = mx.sigmoid(gate) * value[:, :, None, :]
        gated_normed = self.norm_conv(gated.reshape(B, S, -1))
        gated = gated.reshape(B, S, -1)
        if step.valid is not None:
            zero = mx.zeros((), dt)
            gated = mx.where(step.valid[..., None], gated, zero)
            gated_normed = mx.where(step.valid[..., None], gated_normed, zero)
        # [ref: _short_conv] dilated causal depthwise conv over the last
        # (K-1)*dilation inputs, zero history at the start.
        hist = self.conv1d.history
        state = cache[2] if cache is not None and cache[2] is not None else None
        if state is None:
            state = mx.zeros((B, hist, gated_normed.shape[-1]), dtype=gated_normed.dtype)
        full = mx.concatenate([state, gated_normed], axis=1)
        if cache is not None:
            cache[2] = conv_history_tail(full, hist)
        return gated + silu_rounded_once(self.conv1d(full, S))


class DecoderLayer(nn.Module):
    """[ref: Qwen4ExpTextDecoderLayer]"""

    def __init__(self, args: TextModelArgs, layer_idx: int):
        super().__init__()
        self.layer_idx = layer_idx
        self.is_linear = args.layer_types[layer_idx] == "linear_attention"
        if self.is_linear:
            self.linear_attn = GatedDeltaNet(args)
        else:
            self.self_attn = QSAAttention(args)
        self.mlp = SparseMoeBlock(args)
        self.has_ple = (layer_idx + 1) in args.ple_layer_ids
        if self.has_ple:
            self.ple = PLELayer(args)
        self.attn_hyper_connection = GatedResidual(args)
        self.mlp_hyper_connection = GatedResidual(args)

    def __call__(self, h: mx.array, step: _Step, cache) -> mx.array:
        if self.has_ple:
            h = h + self.ple(h, step.ngram_emb[self.layer_idx], step, cache)
        x, hyper, inject = self.attn_hyper_connection(h)
        if self.is_linear:
            x = self.linear_attn(x, step, cache)
        else:
            x = self.self_attn(x, step, cache)
        h = _inject(hyper, x, inject)
        x, hyper, inject = self.mlp_hyper_connection(h)
        return _inject(hyper, self.mlp(x), inject)


class Qwen4ExpTextModel(nn.Module):
    def __init__(self, args: TextModelArgs):
        super().__init__()
        self.args = args
        self.embed_tokens = nn.Embedding(args.vocab_size, args.hidden_size)
        self.layers = [DecoderLayer(args, i) for i in range(args.num_hidden_layers)]
        self.hyper_connection_mixer = GatedResidual(args, use_combine=False)


class _NgramRuntime:
    """Host-side n-gram state (plain object: never an MLX parameter)."""

    def __init__(self, args: TextModelArgs, twin: dict):
        self.args = args
        self.specs: Dict[int, NgramHashSpec] = {}
        for ple_index, lid in enumerate(args.ple_layer_ids):
            self.specs[lid - 1] = NgramHashSpec(args, ple_index)
        self.meta = (twin or {}).get("ngram", {})
        self.base_dir: Optional[Path] = None
        self.io = self.meta.get("io", "mmap")
        self.tables: Dict[int, NgramTable] = {}

    def resolve_dir(self) -> Path:
        if self.base_dir is not None:
            return self.base_dir
        d = Path(self.meta.get("dir", "ngram"))
        if not d.is_absolute():
            d = Path(__file__).resolve().parent / d
        return d

    def table(self, layer_idx: int) -> NgramTable:
        if layer_idx not in self.tables:
            layers = self.meta.get("layers", {})
            entry = layers.get(str(layer_idx))
            if entry is None:
                raise FileNotFoundError(
                    f"no n-gram table registered for layer {layer_idx}; convert with "
                    "scripts/align_convert_qwen4_exp_twin.py")
            spec = self.specs[layer_idx]
            if int(entry["rows"]) != spec.padded_vocab_size or int(entry["dim"]) != spec.head_dim:
                raise ValueError("n-gram table shape does not match the config")
            self.tables[layer_idx] = NgramTable(
                self.resolve_dir() / entry["file"], entry["rows"], entry["dim"],
                entry["format"], entry.get("group_size", 32), io=self.io)
        return self.tables[layer_idx]


class TextModel(nn.Module):
    def __init__(self, args: TextModelArgs, twin: Optional[dict] = None):
        super().__init__()
        self.args = args
        self.model_type = args.model_type
        self.model = Qwen4ExpTextModel(args)
        if not args.tie_word_embeddings:
            self.lm_head = nn.Linear(args.hidden_size, args.vocab_size, bias=False)
        self._inv_freq = rope_inv_freq(args)
        self._ngram = _NgramRuntime(args, twin or {})
        self._first_attn = args.layer_types.index("indexed_attention")

    @property
    def layers(self):
        return self.model.layers

    def make_cache(self, left_padding: Optional[Sequence[int]] = None):
        return make_layer_caches(self.args, left_padding)

    def _gather_ngrams(self, ids: np.ndarray, step: _Step, cache, dtype) -> None:
        if step.valid_host is not None:
            ids = np.where(step.valid_host, ids, self.args.eos_id)
        for layer_idx, spec in self._ngram.specs.items():
            c = cache[layer_idx]
            ctx = c[3] if c is not None and c[3] is not None else None
            if ctx is None:
                ctx_np = np.full((step.B, spec.context_len), spec.eos, dtype=np.int64)
            else:
                ctx_np = np.asarray(ctx).astype(np.int64)
            history = np.concatenate([ctx_np, ids], axis=1)
            ng = spec.ngram_ids(history, step.S)
            rows = self._ngram.table(layer_idx).gather(ng)        # (B, S, heads, d) f32
            c[3] = mx.array(history[:, -spec.context_len:].astype(np.int32))
            step.ngram_emb[layer_idx] = mx.array(rows.reshape(step.B, step.S, -1)).astype(dtype)

    def __call__(self, inputs: mx.array, cache=None, input_embeddings=None) -> mx.array:
        if input_embeddings is not None:
            raise NotImplementedError("qwen4_exp PLE needs token ids; input_embeddings unsupported")
        B, S = inputs.shape
        if cache is None:
            cache = self.make_cache()
        ref = cache[self._first_attn]
        step = _Step(B, S, ref.offset, ref.lp(B), self._inv_freq)

        h = self.model.embed_tokens(inputs)
        if self._ngram.specs:
            # Host sync: the n-gram rows depend on the token ids just fed.
            self._gather_ngrams(np.asarray(inputs).astype(np.int64), step, cache, h.dtype)
        h = mx.tile(h, (1, 1, self.args.hc_count))
        for layer, c in zip(self.model.layers, cache):
            h = layer(h, step, c)
        h = self.model.hyper_connection_mixer(h)
        if self.args.tie_word_embeddings:
            return self.model.embed_tokens.as_linear(h)
        return self.lm_head(h)


# --------------------------------------------------------------------------
# Weight-name handling (shared with the converter)
# --------------------------------------------------------------------------


def hf_to_mlx_key(key: str) -> Optional[str]:
    """Map a reference/HF checkpoint key to this port's parameter path.

    Returns ``None`` for weights the text path does not use (``mtp.*``, the
    vision tower). Already-converted keys map to themselves.
    """
    if key.startswith("mtp.") or key.startswith("model.mtp."):
        return None
    if key.startswith(("model.visual.", "visual.", "vision_tower.", "model.vision_tower.")):
        return None
    if key.startswith("language_model."):
        return key
    if key.startswith("model.language_model."):
        return "language_model.model." + key[len("model.language_model."):]
    if key.startswith("lm_head."):
        return "language_model." + key
    if key.startswith("model."):
        return "language_model.model." + key[len("model."):]
    raise KeyError(f"unrecognised qwen4_exp weight name: {key}")


NGRAM_BUFFER_SUFFIXES = (
    "ple.ple_embedding.layer_multipliers",
    "ple.ple_embedding.ngram_heads_vocab_sizes",
    "ple.ple_embedding.ngram_heads_offsets",
)


def is_ngram_table_key(key: str) -> bool:
    return ".ple.ple_embedding.ngram_embedding." in key


def is_ngram_buffer_key(key: str) -> bool:
    return key.endswith(NGRAM_BUFFER_SUFFIXES)


def quant_policy(path: str, shape: Sequence[int], expert_bits: Optional[int],
                 dense_bits: Optional[int], group_size: int) -> Optional[int]:
    """Bits for the MLX module at ``path`` (None = keep float).

    * routed experts (``switch_mlp``): ``expert_bits``;
    * router, shared-expert gate, QSA indexer, DeltaNet a/b projections and
      hyper-connection write gates stay float (small, selection-critical);
    * every other Linear/Embedding: ``dense_bits``.
    Norms, convs, ``A_log`` and ``dt_bias`` are never quantized.
    """
    if shape[-1] % group_size:
        return None
    if ".switch_mlp." in path:
        return expert_bits
    if len(shape) != 2:
        return None
    keep_float = (
        path.endswith(".mlp.gate"),
        path.endswith(".shared_expert_gate"),
        ".self_attn.indexer." in path,
        path.endswith(".in_proj_a"),
        path.endswith(".in_proj_b"),
        path.endswith(".block_inject_weight"),
    )
    if any(keep_float):
        return None
    return dense_bits


# --------------------------------------------------------------------------
# Top-level model (mlx-lm entry point)
# --------------------------------------------------------------------------


class Model(nn.Module):
    def __init__(self, args: ModelArgs):
        super().__init__()
        self.args = args
        self.model_type = args.model_type
        self.language_model = TextModel(TextModelArgs.from_dict(args.text_config), args.twin)

    def __call__(self, inputs: mx.array, cache=None, input_embeddings=None):
        return self.language_model(inputs, cache=cache, input_embeddings=input_embeddings)

    @property
    def layers(self):
        return self.language_model.model.layers

    def make_cache(self, left_padding: Optional[Sequence[int]] = None):
        return self.language_model.make_cache(left_padding)

    # Checkpoint helpers live on the model because mlx-lm loads this file as
    # an anonymous module (``custom_model``) that callers cannot import.
    snapshot_cache = staticmethod(snapshot_cache)
    restore_cache = staticmethod(restore_cache)

    def set_ngram_dir(self, path: os.PathLike, io: Optional[str] = None):
        rt = self.language_model._ngram
        for t in rt.tables.values():
            t.close()
        rt.tables = {}
        rt.base_dir = Path(path)
        if io is not None:
            rt.io = io

    def ngram_tables(self) -> Dict[int, NgramTable]:
        rt = self.language_model._ngram
        for lid in rt.specs:
            rt.table(lid)
        return rt.tables

    def sanitize(self, weights: Dict[str, mx.array]) -> Dict[str, mx.array]:
        """HF/reference names -> port names; idempotent on converted weights.

        The n-gram table is not an MLX parameter: its rows (and the derived
        hash buffers) are dropped here and served from the on-disk store.
        """
        out: Dict[str, mx.array] = {}
        experts: Dict[tuple, Dict[int, mx.array]] = {}
        n_exp = self.language_model.args.num_experts
        for key, value in weights.items():
            mk = hf_to_mlx_key(key)
            if mk is None or is_ngram_table_key(mk) or is_ngram_buffer_key(mk):
                continue
            if ".mlp.experts." in mk:
                head, rest = mk.split(".mlp.experts.", 1)
                if rest == "gate_up_proj":
                    half = value.shape[1] // 2
                    out[f"{head}.mlp.switch_mlp.gate_proj.weight"] = value[:, :half]
                    out[f"{head}.mlp.switch_mlp.up_proj.weight"] = value[:, half:]
                elif rest == "down_proj":
                    out[f"{head}.mlp.switch_mlp.down_proj.weight"] = value
                else:
                    e, proj, _ = rest.split(".")
                    experts.setdefault((head, proj), {})[int(e)] = value
                continue
            if mk.endswith("conv1d.weight") and value.ndim == 3 and value.shape[-1] != 1:
                value = value.moveaxis(2, 1)
            out[mk] = value
        for (head, proj), per in experts.items():
            if len(per) != n_exp:
                raise ValueError(f"{head}: {proj} has {len(per)}/{n_exp} experts")
            out[f"{head}.mlp.switch_mlp.{proj}.weight"] = mx.stack([per[e] for e in range(n_exp)])
        return out

    @property
    def quant_predicate(self):
        def predicate(path, module):
            shape = module.weight.shape if hasattr(module, "weight") else (1,)
            bits = quant_policy(path, shape, 4, 8, 64)
            if bits is None:
                return False
            return {"group_size": 64, "bits": bits}
        return predicate

    @property
    def cast_predicate(self):
        def predicate(path: str):
            return not path.endswith("A_log")
        return predicate
