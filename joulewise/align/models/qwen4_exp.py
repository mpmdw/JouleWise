# Copyright 2026 JouleWise. Canonical MLX port of the official Qwen
# ``qwen4_exp`` (Qwen3.8-Flash-Next) text decoder.
#
# Authority: transformers 5.22.1 ``models/qwen4_exp/modeling_qwen4_exp.py``
# (``HF:<line>`` below). This file is the convergence of two independent ports
# and the performance track (docs/align/qwen4_exp_port/canonical.md has the
# per-component provenance):
#   * Opus twin  (lane/2026-11-05-align-flashnext-twin, qwen4_exp_twin.py, T:)
#   * Sol port   (lane/2026-11-05-align-flashnext-port @ 28d153449, S:)
#   * perf track (PR #670, qwen4_exp_kernels.py, P:)
# following the binding recommendation of
# docs/align/qwen4_exp_port/differential_sol_vs_twin.md (D0-D10).
#
# Loaded by mlx-lm 0.31.3 through ``config.json`` ``model_file``
# (``mlx_lm.utils.load_model``), so it is ONE self-contained file: it imports
# only numpy, mlx and the pinned mlx_lm. No ``from __future__ import
# annotations``: mlx-lm does not register the module in ``sys.modules``, which
# dataclasses need to resolve string annotations. Community PR #1788 code was
# neither read nor run.
"""MLX port of Qwen3.8-Flash-Next (``model_type: qwen4_exp``), text path only.

Architecture (48 layers: 12 x [3 x GatedDeltaNet, 1 x QSA], MoE everywhere):

* Hyper-connections: the residual stream is ``hc_count`` copies of the hidden
  state; each branch reads a gated mixture and writes back with per-stream
  scalar gates.
* Gated DeltaNet linear attention, on mlx-lm's Metal ``gated_delta_kernel``.
* Qwen Sparse Attention: gated GQA attention whose keys are restricted by a
  block indexer (top ``budget / ratio`` mean-pooled key blocks plus the open
  tail). Block keys are cached once per completed block; the attention core
  follows the perf-track policy (dense, masked SDPA, block-sparse Metal
  prefill kernel, gathered decode).
* Hashed n-gram per-layer embedding (PLE): the 51B-parameter table stays on
  disk, memory-mapped; only looked-up rows are read (``NgramTable``).
* 512-expert MoE (top-10 + 1 gated shared expert), fused gate_up experts.

Numerics: every bf16 op follows the reference's rounding (one rounding per
torch op; transcendental activations evaluated in fp32 and rounded once; fp32
reductions where torch accumulates in fp32). In fp32 every cast is identity.
Inside the attention core the rounding is the SDPA backend's: MLX's fused
kernels (head_dim 64, decode) and the block-sparse kernel keep fp32
probabilities through P.V, MLX's head_dim-256 prefill fallback rounds scores
and probabilities like HF's eager path, and torch's CPU bf16 SDPA rounds the
unnormalised probabilities (canonical.md, deviation 12).
MTP and vision are not implemented: the reference ignores ``mtp.*`` on load.
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
from typing import Any, Dict, List, Optional, Sequence, Tuple

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx_lm.models import cache as _cache_api
from mlx_lm.models.base import BaseModelArgs, create_ssm_mask
from mlx_lm.models.cache import ArraysCache, KVCache
from mlx_lm.models.gated_delta import gated_delta_kernel, gated_delta_ops
from mlx_lm.models.switch_layers import SwitchLinear, _gather_sort, _scatter_unsort

FORMAT_VERSION = "qwen4_exp-canonical-v1"
_F32 = mx.float32

# Perf-track dispatch thresholds (P:640, P:680; M4 crossovers, re-measure on
# the Mac). Overridable per model via config.json (see ModelArgs).
QSA_SPARSE_PREFILL_MIN_KV = 6144
QSA_SPARSE_DECODE_MIN_KV = 8192

# fp32 scalars that a compiled decode trace must not inline. mlx 0.31.2's
# fused-kernel codegen prints an inlined scalar constant with 7 significant
# digits (digits10 + 1, not max_digits10 = 9), so ``x * 32 ** -0.5`` compiles
# to a different fp32 multiplier than the eager kernel uses (59 of 64 fp32
# outputs differ by one ulp). Every such constant on the decode path is
# registered here when its module is built and read through ``exact_f32``;
# ``DecoderLayer`` compiles with ``inputs=EXACT_F32``, so inside a trace these
# are tracer inputs carrying the exact fp32 bits, never inlined literals.
# Eager arithmetic is unchanged: an fp32 array times a 0-d fp32 array equal
# to ``float32(c)`` is the same op as the array times the Python float ``c``.
EXACT_F32: Dict[float, mx.array] = {}


def exact_f32(value: float) -> mx.array:
    """0-d fp32 array for ``value``; register at module construction (a first
    use inside a compiled trace would be an inlined constant again)."""
    value = float(value)
    arr = EXACT_F32.get(value)
    if arr is None:
        arr = EXACT_F32[value] = mx.array(value, dtype=mx.float32)
    return arr

# --------------------------------------------------------------------------
# Configuration  (T:65-217)
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

    @classmethod
    def from_dict(cls, params):
        """``BaseModelArgs.from_dict`` drops unknown keys, so legacy top-level
        RoPE keys would be silently ignored (theta 1e4, full rotary). Fold
        them into ``rope_parameters`` as HF does (modeling_rope_utils), and
        refuse conflicting or unsupported ones."""
        params = dict(params)
        legacy = {k: params[k] for k in ("rope_theta", "partial_rotary_factor") if params.get(k) is not None}
        if params.get("rope_scaling"):
            raise ValueError("rope_scaling is not implemented by this port")
        if legacy:
            rope = dict(params.get("rope_parameters") or {"rope_type": "default"})
            for k, v in legacy.items():
                if k in rope and rope[k] != v:
                    raise ValueError(f"conflicting RoPE settings: {k}={v} vs rope_parameters[{k!r}]={rope[k]}")
                rope[k] = v
            params["rope_parameters"] = rope
        return super().from_dict(params)

    def __post_init__(self):
        # [HF Qwen4ExpTextConfig.__post_init__]
        self.ple_layer_ids = sorted(set(self.ple_layer_ids or []))
        if self.ple_embed_dim is None:
            self.ple_embed_dim = self.hidden_size
        if self.layer_types is None:
            self.layer_types = [
                "linear_attention" if (i + 1) % self.full_attention_interval else "indexed_attention"
                for i in range(self.num_hidden_layers)
            ]
        # The released checkpoint says "full_attention" for QSA layers.
        self.layer_types = ["indexed_attention" if t in _ATTN_TYPES else t for t in self.layer_types]
        if self.rope_parameters is None:
            self.rope_parameters = {"rope_type": "default", "rope_theta": 10000.0}
        self._validate()

    @property
    def eos_id(self) -> int:
        eos = self.eos_token_id
        return int(eos[0] if isinstance(eos, (list, tuple)) else eos)

    @property
    def rotary_dim(self) -> int:
        return int(self.head_dim * self.rope_parameters.get("partial_rotary_factor", 1.0))

    @property
    def block_topk(self) -> int:
        return self.indexer_budget // self.indexer_compress_ratio

    def _validate(self):
        # [HF Qwen4ExpTextConfig.validate_architecture], restricted to what this
        # port implements. Anything outside it fails loudly.
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
        if not 0 < self.num_experts_per_tok <= self.num_experts:
            raise ValueError("num_experts_per_tok must be in [1, num_experts]")
        if self.moe_intermediate_size <= 0 or self.shared_expert_intermediate_size <= 0:
            raise ValueError("expert intermediate sizes must be > 0")
        qsa = (self.indexer_n_heads, self.indexer_kv_heads, self.indexer_head_dim,
               self.indexer_budget, self.indexer_compress_ratio)
        if any(v is None for v in qsa):
            raise ValueError("QSA indexer config is required (the reference always builds it)")
        if any(v <= 0 for v in qsa):
            raise ValueError(f"QSA indexer config values must be positive: {qsa}")
        if self.indexer_kv_heads != 1:
            raise ValueError("qwen4_exp QSA requires indexer_kv_heads == 1")
        if self.indexer_budget % self.indexer_compress_ratio:
            raise ValueError("indexer_budget must be divisible by indexer_compress_ratio")
        if self.rotary_dim > self.indexer_head_dim or self.rotary_dim % 2:
            raise ValueError("rotary dims must be even and fit the QSA index head")
        rope_type = self.rope_parameters.get("rope_type", self.rope_parameters.get("type"))
        if rope_type not in (None, "default"):
            raise ValueError(f"rope_type {rope_type!r} is not implemented by this port")
        if self.num_attention_heads % self.num_key_value_heads:
            raise ValueError("attention heads must be a multiple of kv heads")
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
    """Top-level config: the HF ``text_config`` plus JouleWise runtime fields.

    ``ngram_tables``: on-disk n-gram stores written by the converter
    (``{"dir", "io", "layers": {"<decoder layer idx>": {file, rows, dim,
    format, group_size}}}``). The two thresholds select the QSA attention core
    (perf.md §3); every path computes the same function.
    """

    model_type: str
    text_config: dict
    ngram_tables: dict = field(default_factory=dict)
    qsa_sparse_prefill_min_kv: int = QSA_SPARSE_PREFILL_MIN_KV
    qsa_sparse_decode_min_kv: int = QSA_SPARSE_DECODE_MIN_KV
    compile_decode: bool = True

    @classmethod
    def from_dict(cls, params):
        text = params.get("text_config", params)
        return cls(
            model_type=params["model_type"],
            text_config=dict(text),
            ngram_tables=dict(params.get("ngram_tables") or {}),
            qsa_sparse_prefill_min_kv=int(params.get("qsa_sparse_prefill_min_kv", QSA_SPARSE_PREFILL_MIN_KV)),
            qsa_sparse_decode_min_kv=int(params.get("qsa_sparse_decode_min_kv", QSA_SPARSE_DECODE_MIN_KV)),
            compile_decode=bool(params.get("compile_decode", True)),
        )


# --------------------------------------------------------------------------
# Hashed n-gram ids  (T:225-357; HF:1026-1174)
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
    """[HF _build_layer_multipliers]"""
    multiplier_max = ((1 << 63) - 1) // max(unigram_vocab_size, 1)
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
        self.head_offsets = [int(v) for v in np.cumsum([0] + self.head_vocab_sizes[:-1])]
        self.total_vocab_size = int(sum(self.head_vocab_sizes))
        div = args.make_ngram_vocab_size_divisible_by
        self.padded_vocab_size = int(math.ceil(self.total_vocab_size / div) * div)
        self.multipliers = layer_multipliers(args.vocab_size, args.ngram_size, ple_layer_index, args.seed)
        self._mult = np.asarray(self.multipliers, dtype=np.int64)
        self._sizes = np.asarray(self.head_vocab_sizes, dtype=np.int64)
        self._offsets = np.asarray(self.head_offsets, dtype=np.int64)

    def _shift_right_ignore_eos(self, h: np.ndarray, shift: int) -> np.ndarray:
        # [HF Qwen4ExpTextNGramEmbedding._shift_right_ignore_eos]
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
        """Pure-int decode path for one new token; identical results."""
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
# Off-GPU n-gram table: memory-mapped rows, decode-on-gather  (T:364-548)
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
        return {"code_bytes": code_bytes, "groups": groups, "record_bytes": code_bytes + 4 * groups}
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
    lo, hi = xg.min(axis=-1), xg.max(axis=-1)
    if not (np.isfinite(lo).all() and np.isfinite(hi).all()):
        raise ValueError("non-finite n-gram embedding values")
    if max(float(np.abs(lo).max(initial=0)), float(np.abs(hi).max(initial=0))) > 6.0e4:
        raise ValueError("n-gram values exceed the fp16 scale/bias range")
    scale16 = ((hi - lo) / levels).astype(np.float16)
    scale16 = np.where(scale16 == 0, np.float16(1.0), scale16)
    bias16 = lo.astype(np.float16)
    codes = np.rint((xg - bias16.astype(np.float32)[..., None]) / scale16.astype(np.float32)[..., None])
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
    process never grows a file-cache footprint. Only looked-up rows are decoded.
    """

    PREFETCH_MAX_ROWS = 4096

    def __init__(self, path: os.PathLike, rows: int, dim: int, fmt: str,
                 group_size: int = 32, io: str = "mmap", prefetch: bool = True, offset: int = 0):
        """``offset``: byte position of row 0 in ``path`` (0 for the converter's
        own record files, which must then be exactly rows * record_bytes)."""
        self.path = Path(path)
        self.rows, self.dim, self.fmt, self.group_size = int(rows), int(dim), fmt, int(group_size)
        self.layout = ngram_record_layout(fmt, self.dim, self.group_size)
        self.record_bytes = self.layout["record_bytes"]
        self.offset = int(offset)
        expected = self.rows * self.record_bytes
        actual = self.path.stat().st_size
        if self.offset < 0 or (actual != expected if self.offset == 0 else actual < self.offset + expected):
            raise ValueError(f"{self.path}: size {actual} does not hold rows*record_bytes {expected} "
                             f"at offset {self.offset}")
        self.io, self.prefetch = io, prefetch
        self._mm = self._fd = None
        if io == "mmap":
            self._mm = np.memmap(self.path, dtype=np.uint8, mode="r", offset=self.offset,
                                 shape=(self.rows, self.record_bytes))
        elif io == "pread":
            self._fd = os.open(self.path, os.O_RDONLY)
            try:
                fcntl.fcntl(self._fd, _F_NOCACHE, 1)
            except OSError:
                pass
        else:
            raise ValueError(f"unknown n-gram io mode {io!r}")
        self.lookups = self.unique_rows = self.major_faults = 0
        self.seconds = 0.0

    def close(self):
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        self._mm = None

    def _map_base(self) -> Optional[int]:
        """Position of row 0 inside the memmap's underlying ``mmap``. numpy maps
        from the file offset rounded down to the allocation granularity, so
        this is NOT the file offset (validation round 1: madvise used the file
        offset, advising wrong pages and raising past the mapping's end)."""
        raw = getattr(self._mm, "_mmap", None)
        if raw is None or not hasattr(raw, "madvise"):
            return None
        start = np.frombuffer(raw, dtype=np.uint8, count=1)
        try:
            return int(self._mm.ctypes.data - start.ctypes.data)
        finally:
            del start

    def _prefetch(self, ids: np.ndarray) -> None:
        """MADV_WILLNEED each row's pages so cold rows page in concurrently."""
        base = self._map_base()
        if base is None:
            return
        raw, rb, page = self._mm._mmap, self.record_bytes, mmap.PAGESIZE
        for row in ids.tolist():
            start = base + row * rb
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
            buf = os.pread(self._fd, rb, self.offset + row * rb)
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
        if flat.size <= 64:
            uniq, inverse = flat, None
        else:
            uniq, inverse = np.unique(flat, return_inverse=True)
        rows = decode_ngram_rows(self._read_rows(uniq), self.fmt, self.dim, self.group_size)
        out = (rows if inverse is None else rows[inverse.reshape(-1)]).reshape(*ids.shape, self.dim)
        self.lookups += int(flat.size)
        self.unique_rows += int(uniq.size)
        self.major_faults += resource.getrusage(resource.RUSAGE_SELF).ru_majflt - faults0
        self.seconds += time.perf_counter() - t0
        return out


# --------------------------------------------------------------------------
# Numerics helpers: one rounding per reference op
# --------------------------------------------------------------------------


def silu_once(x: mx.array) -> mx.array:
    """``F.silu`` on a low-precision tensor: torch evaluates it in fp32 and
    rounds once (T:627-636; D4, D5, expert/shared SwiGLU). ``nn.silu`` on bf16
    rounds twice and differs on ~5% of inputs. Identity cast in fp32."""
    return nn.silu(x.astype(_F32)).astype(x.dtype)


def sigmoid_once(x: mx.array) -> mx.array:
    """``torch.sigmoid`` on bf16: fp32 evaluation, one rounding (S:229-233,
    unconditional; D3). ``mx.sigmoid`` on bf16 differs from torch on 3%."""
    return mx.sigmoid(x.astype(_F32)).astype(x.dtype)


class OffsetRMSNorm(nn.Module):
    """[HF Qwen4ExpTextRMSNorm:143-163] fp32 norm, ``* (1 + w)`` in fp32, cast
    back; optional per-group normalisation (T:556-577, fused rms_norm)."""

    def __init__(self, dims: int, eps: float = 1e-6, group_size: Optional[int] = None):
        super().__init__()
        self.weight = mx.zeros((dims,))
        self.eps = eps
        self.group_size = group_size

    def __call__(self, x: mx.array) -> mx.array:
        h = x.astype(_F32)
        if self.group_size is not None:
            shape = h.shape
            h = mx.fast.rms_norm(h.reshape(*shape[:-1], -1, self.group_size), None, self.eps).reshape(shape)
        else:
            h = mx.fast.rms_norm(h, None, self.eps)
        return (h * (1.0 + self.weight.astype(_F32))).astype(x.dtype)


class GatedRMSNorm(nn.Module):
    """[HF Qwen4ExpTextRMSNormGated:170-187] fp32 norm rounded to the input
    dtype, times the weight in that dtype, times the fp32 gate activation,
    rounded once (T:580-595)."""

    def __init__(self, dims: int, eps: float, activation: str):
        super().__init__()
        self.weight = mx.ones((dims,))
        self.eps = eps
        self.activation = activation

    def __call__(self, x: mx.array, gate: mx.array) -> mx.array:
        dt = x.dtype
        h = mx.fast.rms_norm(x.astype(_F32), None, self.eps).astype(dt)
        h = self.weight * h
        g = gate.astype(_F32)
        g = mx.sigmoid(g) if self.activation == "sigmoid" else nn.silu(g)
        return (h.astype(_F32) * g).astype(dt)


def conv_history_tail(full: mx.array, hist: int) -> mx.array:
    """Last ``hist`` positions of ``full`` (B, T, C); correct for hist == 0."""
    return full[:, full.shape[1] - hist:, :]


def rope_inv_freq(args: TextModelArgs) -> mx.array:
    """[HF compute_default_rope_parameters:107-115] ``1 / base ** (arange/dim)``
    (T:649-667, D2): fp32 exponent and reciprocal as the reference; the pow in
    float64 rounded once to fp32. Bit-identical to the reference at the
    released config ONLY (rope_theta 1e7, rotary_dim 64: 32/32); mlx's fp32
    ``**`` (Sol) differed in 15/32 entries, a 9.8e-4 rad phase drift by 40K
    positions. The recipe is not torch's fp32 pow in general (63/64 at
    rope_theta 1e6, rotary_dim 128): re-verify inv_freq bitwise for any other
    theta or rotary_dim (validation round 1)."""
    base = np.float64(np.float32(args.rope_parameters.get("rope_theta", 10000.0)))
    dim = args.rotary_dim
    exponent = np.arange(0, dim, 2, dtype=np.float32) / np.float32(dim)
    powed = np.power(base, exponent.astype(np.float64)).astype(np.float32)
    return mx.array(np.float32(1.0) / powed)


def rope_cos_sin(positions: mx.array, inv_freq: mx.array) -> Tuple[mx.array, mx.array]:
    """[HF Qwen4ExpTextRotaryEmbedding.forward:119-129] positions (...) ->
    fp32 cos, sin (..., rotary_dim). Text mRoPE sections collapse to plain RoPE."""
    freqs = positions.astype(_F32)[..., None] * inv_freq
    emb = mx.concatenate([freqs, freqs], axis=-1)
    return mx.cos(emb), mx.sin(emb)


def apply_rope(x: mx.array, cos: mx.array, sin: mx.array) -> mx.array:
    """[HF apply_rotary_pos_emb:627-662] rotate-half RoPE on the leading
    ``rotary_dim`` dims, with cos/sin cast to the model dtype first (HF:129).
    Explicit, never ``mx.fast.rope``: its fp32-internal rotation changes bf16
    indexer selection beyond ties (perf critic HIGH item)."""
    rot = cos.shape[-1]
    cos, sin = cos.astype(x.dtype), sin.astype(x.dtype)
    xr, xp = x[..., :rot], x[..., rot:]
    half = rot // 2
    rotated = mx.concatenate([-xr[..., half:], xr[..., :half]], axis=-1)
    out = xr * cos + rotated * sin
    return mx.concatenate([out, xp], axis=-1) if xp.shape[-1] else out


def topk_mask_lowest_index(scores: mx.array, k: int) -> mx.array:
    """Boolean mask of the top-``k`` entries along the last axis; ties at the
    k-th value go to the LOWEST index (T:689-707). Same set as Sol's stable
    (score desc, index asc) rule (D0), built without a host sync (Sol's
    ``mx.any(crosses).item()``, S:363, synced once per QSA layer per call).

    ``torch.topk`` leaves tie order unspecified: relu makes block scores
    exactly 0.0 whenever every indexer head's dot product is <= 0, so
    zero-score blocks can straddle the cut. Reference comparisons must be
    tie-aware (tests/align/test_qwen4_exp_canonical.py)."""
    n = scores.shape[-1]
    kth = mx.partition(scores, n - k, axis=-1)[..., n - k:n - k + 1]
    gt = scores > kth
    eq = scores == kth
    need = k - gt.astype(mx.int32).sum(axis=-1, keepdims=True)
    rank = mx.cumsum(eq.astype(mx.int32), axis=-1)
    return gt | (eq & (rank <= need))


# --------------------------------------------------------------------------
# Caches: cache-carried left padding (T:715-826) on mlx-lm's ArraysCache /
# KVCache, serializable (S:131-198) and registered with mlx_lm.models.cache.
# --------------------------------------------------------------------------


def _csv(values) -> str:
    return "" if values is None else ",".join(str(int(v)) for v in values)


def _uncsv(text: str):
    return None if not text else tuple(int(v) for v in text.split(","))


def _unsupported_batching(*args, **kwargs):
    raise NotImplementedError("qwen4_exp caches carry left padding and the QSA indexer state; BatchGenerator "
                              "filter / extend / extract / merge / prepare / finalize are unsupported: rebuild "
                              "the batch with make_cache(left_padding=...)")


class Qwen4ExpLinearCache(ArraysCache):
    """GatedDeltaNet layer state: ``[conv, recurrent]`` (+ ``[ple_conv,
    ngram_context]`` on PLE layers). The recurrent state is fp32
    ``[B, Hv, Dv, Dk]`` (mlx-lm layout; HF's is the transpose).

    Left padding follows mlx-lm's ``ArraysCache`` protocol: ``left_padding``
    counts pad tokens still ahead of the current chunk (``make_mask`` /
    ``advance``). ``padding`` keeps the constant per-row value and ``offset``
    the tokens seen, for positions and prompt-cache files. A recurrent state
    cannot be cropped: prefix rewrites restore a snapshot (``restore_cache``).

    ``left_padding`` is derived from the host ints ``padding - offset`` on
    each read. mlx-lm 0.31.3's ``ArraysCache.advance`` does a lazy
    ``left_padding -= n``; only the first linear cache's value is ever read
    (``create_ssm_mask``), so every other layer grew one graph node and one
    Metal buffer per decode step until the allocator's resource limit
    (mlx-lm #1632; validation round 1, systems MEDIUM).
    """

    qwen4_exp_cache = (FORMAT_VERSION, "linear")

    def __init__(self, size: int, left_padding: Optional[Sequence[int]] = None):
        self.padding = tuple(int(p) for p in left_padding) if left_padding and any(left_padding) else None
        self.offset = 0
        super().__init__(size)

    @property
    def left_padding(self):
        padding = self.__dict__.get("padding")
        if padding is None:
            return None
        return mx.array(np.asarray(padding, dtype=np.int32) - np.int32(self.offset))

    @left_padding.setter
    def left_padding(self, value):
        if value is None and self.__dict__.get("padding") is None:
            return  # ArraysCache.__new__ initialises the field
        raise NotImplementedError("qwen4_exp linear caches derive left padding from make_cache(left_padding=...) "
                                  "and the offset")

    def advance(self, n: int):
        self.offset += n

    def size(self):
        return self.offset

    @property
    def state(self):
        return self.cache

    @state.setter
    def state(self, v):
        self.cache = list(v)

    @property
    def meta_state(self):
        lp = None if self.padding is None else [p - self.offset for p in self.padding]
        return (str(self.offset), _csv(self.padding), _csv(lp))

    @meta_state.setter
    def meta_state(self, v):
        self.offset = int(v[0])
        self.padding = _uncsv(v[1])
        want = None if self.padding is None else tuple(p - self.offset for p in self.padding)
        if _uncsv(v[2]) != want:
            raise ValueError("prompt-cache left padding disagrees with padding - offset")
        self.lengths = None

    # BatchGenerator protocol: unsupported, failing loudly here rather than
    # relying on mlx-lm's _make_cache refusing KVCache subclasses. The
    # inherited extract returned a plain ArraysCache without offset or
    # padding, and prepare / finalize were accepted silently (finalize
    # cleared the padding). Validation round 1, systems LOW.
    filter = extend = extract = prepare = finalize = _unsupported_batching
    merge = classmethod(_unsupported_batching)


class Qwen4ExpQSACache(KVCache):
    """KV cache of a QSA layer plus the indexer's key history (T:715-787).

    * ``keys/values``: the inherited ``KVCache`` buffers ``(B, Hkv, cap, D)``.
    * ``raw_keys``: un-normed, un-roped indexer keys ``(B, cap, Di)``, as HF's
      ``update_indexer`` caches them (needed for the open block and trims).
    * ``block_keys``: pooled + normed + roped block keys ``(B, NBcap, Di)``.
      Block ``j`` of row ``b`` covers tokens ``[p_b + j*r, p_b + (j+1)*r)``
      (``p_b`` = that row's left padding). It is computed once, when it
      completes, from its own tokens and its position ``j*r`` only, so it equals
      HF's per-query recomputation and trimming is exact: slots past the new
      length are recomputed when they complete again.
    * ``padding``: constant per-row left padding (host ints).
    """

    qwen4_exp_cache = (FORMAT_VERSION, "qsa")

    def __init__(self, left_padding: Optional[Sequence[int]] = None):
        super().__init__()
        self.padding = tuple(int(p) for p in left_padding) if left_padding and any(left_padding) else None
        self.raw_keys = None
        self.block_keys = None

    def lp(self, batch: int) -> np.ndarray:
        if self.padding is None:
            return np.zeros((batch,), dtype=np.int64)
        if len(self.padding) != batch:
            raise ValueError("left padding batch size mismatch")
        return np.asarray(self.padding, dtype=np.int64)

    def append_index_keys(self, ik: mx.array):
        """Store raw indexer keys for the tokens just added by ``update_and_fetch``."""
        B, S, D = ik.shape
        end = self.offset
        prev = end - S
        if self.raw_keys is None or end > self.raw_keys.shape[1]:
            steps = (self.step + end - 1) // self.step
            fresh = mx.zeros((B, steps * self.step, D), dtype=ik.dtype)
            if self.raw_keys is not None:
                fresh[:, :prev] = self.raw_keys[:, :prev]
            self.raw_keys = fresh
        self.raw_keys[:, prev:end, :] = ik

    def write_blocks(self, j0: int, vals: mx.array, j: Optional[np.ndarray] = None):
        """Write block keys ``vals`` (B, M, Di) at block slots ``j0..j0+M`` (or
        per-row slots ``j`` (B, M) for padded batches)."""
        B, M, D = vals.shape
        need = (j0 + M) if j is None else int(j.max()) + 1
        if self.block_keys is None or need > self.block_keys.shape[1]:
            cap = ((need + 63) // 64) * 64
            fresh = mx.zeros((B, cap, D), dtype=vals.dtype)
            if self.block_keys is not None:
                fresh[:, :self.block_keys.shape[1]] = self.block_keys
            self.block_keys = fresh
        if j is None:
            self.block_keys[:, j0:j0 + M] = vals
        else:
            idx = mx.broadcast_to(mx.array(j.astype(np.int32))[..., None], (B, M, D))
            self.block_keys = mx.put_along_axis(self.block_keys, idx, vals, axis=1)

    def n_blocks(self) -> int:
        if self.keys is None:
            return 0
        lp = self.lp(self.keys.shape[0])
        return int((np.maximum(self.offset - lp, 0) // self._ratio).max()) if self._ratio else 0

    _ratio = 0  # set by the model (indexer_compress_ratio); class default for from_state

    @property
    def state(self):
        if self.keys is None:
            return []
        # At least one block slot, so safetensors never sees an empty array
        # (no block completes before ``ratio`` real tokens). Slots past the
        # complete-block count are never read: validity derives from offset.
        nb = max(self.n_blocks(), 1)
        if self.block_keys is None or self.block_keys.shape[1] < nb:
            blocks = mx.zeros((self.keys.shape[0], nb, self.raw_keys.shape[-1]), self.raw_keys.dtype)
            if self.block_keys is not None:
                blocks[:, :self.block_keys.shape[1]] = self.block_keys
        else:
            blocks = self.block_keys[:, :nb]
        return [self.keys[..., :self.offset, :], self.values[..., :self.offset, :],
                self.raw_keys[:, :self.offset], blocks]

    @state.setter
    def state(self, v):
        if not v:
            self.keys = self.values = self.raw_keys = self.block_keys = None
            self.offset = 0
            return
        self.keys, self.values, self.raw_keys, self.block_keys = v
        self.offset = self.keys.shape[2]

    @property
    def meta_state(self):
        return (str(self.offset), _csv(self.padding), str(self._ratio))

    @meta_state.setter
    def meta_state(self, v):
        self.offset = int(v[0])
        self.padding = _uncsv(v[1])
        self._ratio = int(v[2])

    def make_mask(self, N: int, return_array: bool = False, window_size=None):
        """Causal mask aware of this cache's left padding (house-style hook)."""
        if self.padding is None:
            return super().make_mask(N, return_array=return_array, window_size=window_size)
        B = len(self.padding)
        L = self.offset + N
        t = self.offset + np.arange(N)
        ar = np.arange(L)
        lp = self.lp(B)
        m = (ar[None, None, :] <= t[None, :, None]) & (ar[None, None, :] >= lp[:, None, None])
        m |= (ar[None, None, :] == t[None, :, None]) & (t[None, :] < lp[:, None])[..., None]
        return mx.array(m)[:, None]

    def to_quantized(self, group_size: int = 64, bits: int = 4):
        raise NotImplementedError("KV-cache quantization would drop the QSA indexer state")

    filter = extend = extract = prepare = finalize = _unsupported_batching
    merge = classmethod(_unsupported_batching)

    @property
    def nbytes(self):
        return super().nbytes + sum(a.nbytes for a in (self.raw_keys, self.block_keys) if a is not None)


# mlx-lm 0.31.3's load_prompt_cache resolves cache classes in its own globals.
# Every load of this file (mlx-lm runs it as an anonymous module) rebinds them,
# so with two models in one process load_prompt_cache returns the last-loaded
# module's classes: the code below dispatches on the ``qwen4_exp_cache``
# marker, never on class identity (validation round 1, systems LOW).
_cache_api.Qwen4ExpLinearCache = Qwen4ExpLinearCache
_cache_api.Qwen4ExpQSACache = Qwen4ExpQSACache


def cache_kind(c) -> Optional[str]:
    """``"linear"`` / ``"qsa"`` for this format's caches from any loaded copy
    of this module, else None."""
    marker = getattr(type(c), "qwen4_exp_cache", None)
    return marker[1] if isinstance(marker, tuple) and marker[:1] == (FORMAT_VERSION,) else None


def make_layer_caches(args: TextModelArgs, left_padding: Optional[Sequence[int]] = None):
    ple_layers = {lid - 1 for lid in args.ple_layer_ids}
    caches = []
    for i, t in enumerate(args.layer_types):
        if t == "linear_attention":
            caches.append(Qwen4ExpLinearCache(4 if i in ple_layers else 2, left_padding))
        else:
            c = Qwen4ExpQSACache(left_padding)
            c._ratio = args.indexer_compress_ratio
            caches.append(c)
    return caches


def _batch(arrays) -> Optional[int]:
    return next((int(a.shape[0]) for a in arrays if a is not None), None)


def snapshot_cache(cache: List[Any]) -> List[Any]:
    """Zero-copy checkpoint of a hybrid cache. Arrays are values (slots are
    rebound, never mutated) and KV/indexer buffers below the current offset
    are never rewritten, so offsets + slot references restore exactly."""
    snap = []
    for c in cache:
        kind = cache_kind(c)
        if kind == "qsa":
            snap.append(("qsa", c.offset, c.padding, _batch([c.keys])))
        elif kind == "linear":
            snap.append(("linear", list(c.cache), c.offset, c.padding, _batch(c.cache)))
        else:
            raise TypeError(f"unsupported cache type {type(c).__name__}")
    return snap


def restore_cache(cache: List[Any], snap: List[Any]) -> None:
    """Restore ``snapshot_cache`` output (QSA caches are trimmed back).

    Every entry is checked before any cache is touched (validation round 1),
    so a refused restore leaves the caller's cache exactly as it was."""
    if len(cache) != len(snap):
        raise ValueError("snapshot and cache have different layer counts")
    if len({entry[1] if entry[0] == "qsa" else entry[2] for entry in snap}) > 1:
        raise ValueError("snapshot offsets disagree")
    for c, entry in zip(cache, snap):
        if cache_kind(c) != entry[0]:
            raise ValueError("snapshot layer kinds do not match the cache")
        if entry[0] == "qsa":
            _, offset, padding, batch = entry
            if c.offset < offset:
                raise ValueError("cannot restore a QSA cache forward in time")
            now = _batch([c.keys])
        else:
            _, _, _, padding, batch = entry
            now = _batch(c.cache)
        if c.padding != padding:
            raise ValueError("snapshot was taken on a batch with different left padding")
        if batch is not None and now is not None and batch != now:
            raise ValueError("snapshot was taken on a different batch size")
    for c, entry in zip(cache, snap):
        if entry[0] == "qsa":
            c.trim(c.offset - entry[1])
        else:
            c.cache = list(entry[1])
            c.offset = entry[2]  # left_padding derives from padding - offset


# --------------------------------------------------------------------------
# Gated DeltaNet on mlx-lm's Metal kernel  (P:71-146, eps adapter)
# --------------------------------------------------------------------------

GDN_L2NORM_EPS = 1e-6


def gated_delta(q, k, v, a, b, A_log, dt_bias, state, mask=None, use_kernel=True):
    """HF ``torch_*_gated_delta_rule`` (HF:253-450) on mlx-lm's kernel, unchanged.

    q, k: [B, T, Hk, Dk] conv outputs (after silu); v: [B, T, Hv, Dv];
    a, b: [B, T, Hv]; state: [B, Hv, Dv, Dk] fp32; mask: [B, T] bool or None.

    * l2norm in fp32 with HF's eps, fused: ``Dk**-0.5 * rms_norm(x, eps/Dk)``
      is exactly ``x * rsqrt(sum(x^2) + eps)`` (perf adapter; mlx-lm's own
      callers use eps 1e-6 under rms, an effective 1.28e-4).
    * beta = sigmoid(b) in the model dtype, fp32 evaluation rounded once (D3);
      g = -exp(A_log) * softplus(a + dt_bias) in fp32 (mlx-vlm audit P2).
    * Masked steps leave the state unchanged and output 0 (S:243-260 seam); for
      left padding from a zero state this equals HF's zeroed inputs.
    """
    B, T, Hk, Dk = q.shape
    Hv, Dv = v.shape[-2:]
    qn = mx.fast.rms_norm(q.astype(_F32), None, GDN_L2NORM_EPS / Dk) * exact_f32(1.0 / Dk)
    kn = mx.fast.rms_norm(k.astype(_F32), None, GDN_L2NORM_EPS / Dk) * exact_f32(Dk ** -0.5)
    beta = sigmoid_once(b)
    decay = mx.exp(-mx.exp(A_log.astype(_F32)) * nn.softplus(a.astype(_F32) + dt_bias.astype(_F32)))
    if state is None:
        state = mx.zeros((B, Hv, Dv, Dk), dtype=_F32)
    if (use_kernel and Dk % 32 == 0 and Dv % 4 == 0
            and mx.default_device() == mx.gpu and mx.metal.is_available()):
        y, state = gated_delta_kernel(qn, kn, v, decay, beta, state, mask)
    else:
        y, state = gated_delta_ops(qn, kn, v, decay, beta, state, mask)
    return y, state


# --------------------------------------------------------------------------
# QSA attention cores  (P:445-708; block-sparse prefill Metal kernel P:512-635)
# --------------------------------------------------------------------------


def sdpa_query_chunked(queries, keys, values, scale, mask, max_score_bytes=256 * 2 ** 20):
    """``mx.fast.scaled_dot_product_attention`` split over query rows (P:445-480).

    mlx 0.31.2 has no fused prefill kernel for head_dim 256 and materialises
    [B, Hq, L, T] scores; splitting rows bounds that transient (rows are
    independent, so the result is unchanged). ``mask``: None, "causal" (queries
    are the last L of the T keys), or broadcastable to [B, 1, L, T]."""
    B, Hq, L, _ = queries.shape
    T = keys.shape[-2]
    rows = max(16, min(L, max_score_bytes // max(B * Hq * T * 4, 1)))
    if rows >= L:
        return mx.fast.scaled_dot_product_attention(queries, keys, values, scale=scale, mask=mask)
    if isinstance(mask, str):
        pos = mx.arange(T - L, T)
        mask = (mx.arange(T)[None, :] <= pos[:, None])[None, None]
    outs = []
    for s in range(0, L, rows):
        m = None if mask is None else mask[..., s:s + rows, :]
        outs.append(mx.fast.scaled_dot_product_attention(
            queries[:, :, s:s + rows], keys, values, scale=scale, mask=m))
    return mx.concatenate(outs, axis=2)


# One threadgroup per (query l, kv head g, batch b); its NSG simdgroups each own
# HPS of the query heads sharing kv head g, so a selected token's K/V row is
# reused from L1 by every head. Scores lane-per-token, online softmax per
# 32-token tile, P.V lane-per-dims; fp32 accumulation. Unused idx slots are -1;
# every row holds at least one valid token. Verbatim from the perf track, except
# the token-list pointer's address space (validation round 1).
_QSA_SPARSE_ATTN_SRC = """
    constexpr int E = D / 32;
    const uint lane = thread_index_in_simdgroup;
    const uint sg = simdgroup_index_in_threadgroup;
    const uint l = thread_position_in_grid.y / Hkv;
    const uint g = thread_position_in_grid.y % Hkv;
    const uint b = thread_position_in_grid.z;
    const uint h0 = g * (Hq / Hkv) + sg * HPS;
    threadgroup float4 q_sh[NSG][HPS][D / 4];
    for (int h = 0; h < HPS; h++) {
      const device InT* qp = q + (((size_t)(b * Hq + h0 + h) * L + l) * D);
      for (int d4 = lane; d4 < D / 4; d4 += 32) {
        q_sh[sg][h][d4] = float4(static_cast<float>(qp[4 * d4]), static_cast<float>(qp[4 * d4 + 1]),
                                 static_cast<float>(qp[4 * d4 + 2]), static_cast<float>(qp[4 * d4 + 3])) * scale;
      }
    }
    simdgroup_barrier(mem_flags::mem_threadgroup);
    // auto: mx.fast.metal_kernel passes inputs of fewer than 8 elements in the
    // constant address space, so the pointer must not be declared device.
    auto ip = idx + ((size_t)(b * L + l) * S);
    const device InT* kb = k + ((size_t)(b * Hkv + g) * Tcap) * D;
    const device InT* vb = v + ((size_t)(b * Hkv + g) * Tcap) * D + lane * E;
    float m[HPS], lsum[HPS], o[HPS][E];
    for (int h = 0; h < HPS; h++) {
      m[h] = -INFINITY;
      lsum[h] = 0.0f;
      for (int i = 0; i < E; i++) o[h][i] = 0.0f;
    }
    for (int j0 = 0; j0 < S; j0 += 32) {
      int t = (j0 + (int)lane < S) ? ip[j0 + lane] : -1;
      if (!simd_any(t >= 0)) continue;
      float s[HPS];
      for (int h = 0; h < HPS; h++) s[h] = 0.0f;
      if (t >= 0) {
        const device InT* kp = kb + (size_t)t * D;
        for (int d4 = 0; d4 < D / 4; d4++) {
          float4 kk = float4(static_cast<float>(kp[4 * d4]), static_cast<float>(kp[4 * d4 + 1]),
                             static_cast<float>(kp[4 * d4 + 2]), static_cast<float>(kp[4 * d4 + 3]));
          for (int h = 0; h < HPS; h++) s[h] += dot(q_sh[sg][h][d4], kk);
        }
      } else {
        for (int h = 0; h < HPS; h++) s[h] = -INFINITY;
      }
      float p[HPS];
      for (int h = 0; h < HPS; h++) {
        float mn = max(m[h], simd_max(s[h]));
        float f = metal::exp(m[h] - mn);
        p[h] = metal::exp(s[h] - mn);
        lsum[h] = lsum[h] * f + simd_sum(p[h]);
        for (int i = 0; i < E; i++) o[h][i] *= f;
        m[h] = mn;
      }
      for (int jj = 0; jj < 32; jj++) {
        int tj = simd_shuffle(t, (ushort)jj);
        if (tj < 0) continue;
        const device InT* vp = vb + (size_t)tj * D;
        float vv[E];
        for (int i = 0; i < E; i++) vv[i] = static_cast<float>(vp[i]);
        for (int h = 0; h < HPS; h++) {
          float pj = simd_shuffle(p[h], (ushort)jj);
          for (int i = 0; i < E; i++) o[h][i] += pj * vv[i];
        }
      }
    }
    for (int h = 0; h < HPS; h++) {
      device InT* op = out + (((size_t)(b * Hq + h0 + h) * L + l) * D) + lane * E;
      float inv = 1.0f / lsum[h];
      for (int i = 0; i < E; i++) op[i] = static_cast<InT>(o[h][i] * inv);
    }
"""

_qsa_sparse_attn_kernel = None


def qsa_sparse_attention(queries, keys, values, token_idx, scale, heads_per_simdgroup=None):
    """Attention of each query over its own selected tokens (Metal kernel, P:595-635).

    queries [B, Hq, L, D]; keys/values [B, Hkv, Tcap, D] (whole cache buffers:
    only indexed rows are read); token_idx [B, L, S] int32, -1 = unused.
    Cost O(L * S * D), independent of the context length."""
    global _qsa_sparse_attn_kernel
    if _qsa_sparse_attn_kernel is None:
        _qsa_sparse_attn_kernel = mx.fast.metal_kernel(
            name="qwen4_exp_qsa_sparse_attention",
            input_names=["q", "k", "v", "idx", "scale", "L", "S", "Tcap"],
            output_names=["out"],
            source=_QSA_SPARSE_ATTN_SRC,
        )
    B, Hq, L, D = queries.shape
    Hkv, Tcap = keys.shape[1], keys.shape[2]
    group = Hq // Hkv
    if D % 32 or Hq % Hkv or group * D > 8192:
        raise ValueError(f"unsupported shapes D={D}, Hq={Hq}, Hkv={Hkv}")
    hps = heads_per_simdgroup or next(h for h in (4, 3, 2, 1) if group % h == 0)
    nsg = group // hps
    if keys.dtype != queries.dtype or values.dtype != queries.dtype:
        keys, values = keys.astype(queries.dtype), values.astype(queries.dtype)
    return _qsa_sparse_attn_kernel(
        inputs=[queries, keys, values, token_idx.astype(mx.int32), float(scale), L, token_idx.shape[-1], Tcap],
        template=[("InT", queries.dtype), ("D", D), ("Hq", Hq), ("Hkv", Hkv), ("HPS", hps), ("NSG", nsg)],
        grid=(32 * nsg, L * Hkv, B),
        threadgroup=(32 * nsg, 1, 1),
        output_shapes=[queries.shape],
        output_dtypes=[queries.dtype],
    )[0]


def sparse_kernel_supported(head_dim: int, n_heads: int, n_kv_heads: int) -> bool:
    group = n_heads // n_kv_heads
    return (head_dim % 32 == 0 and n_heads % n_kv_heads == 0 and group * head_dim <= 8192
            and mx.default_device() == mx.gpu and mx.metal.is_available())


# --------------------------------------------------------------------------
# Blocks
# --------------------------------------------------------------------------


class _Context:
    """Per-forward state shared by all layers (T:833-847): host positions and
    padding (no device sync), RoPE cos/sin computed once, masks, n-gram rows."""

    def __init__(self, B: int, S: int, offset: int, lp: np.ndarray, inv_freq: mx.array,
                 ssm_mask: Optional[mx.array], prefill_min_kv: int, decode_min_kv: int,
                 kernel_ok: bool = False):
        self.B, self.S, self.offset, self.lp = B, S, offset, lp
        t = offset + np.arange(S, dtype=np.int64)
        pos = t[None, :] - lp[:, None]
        self.positions_host = pos
        valid = pos >= 0
        self.valid_host = None if valid.all() else valid
        # Pad tokens take position 0 (HF: cumsum(mask) - 1, clamped); they are
        # masked everywhere, so only finiteness matters.
        self.cos, self.sin = rope_cos_sin(mx.array(np.maximum(pos, 0).astype(np.int32)), inv_freq)
        self.inv_freq = inv_freq
        self.ssm_mask = ssm_mask
        self.prefill_min_kv = prefill_min_kv
        self.decode_min_kv = decode_min_kv
        self.kernel_ok = kernel_ok
        self.ngram_emb: Dict[int, mx.array] = {}


class GatedResidual(nn.Module):
    """[HF Qwen4ExpTextGatedResidual:995-1023] Sol's structure (S:263-279), fp32
    stream mean (both ports), silu and sigmoids rounded once (D3, D5)."""

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
        w = silu_once(self.input_mix_weight_down(normed) / self.hc)
        w = sigmoid_once(self.input_mix_weight_up(w))
        shape = (*normed.shape[:-1], self.hc, self.hidden)
        prod = w.reshape(shape) * normed.reshape(shape)
        mixed = prod.astype(_F32).mean(axis=-2).astype(prod.dtype)
        if not self.use_combine:
            return mixed
        inject = 2 * sigmoid_once(self.block_inject_weight(normed) / self.hc)
        return mixed, hyper_input, inject


def _inject(hyper_input: mx.array, branch: mx.array, weights: mx.array) -> mx.array:
    # [HF Qwen4ExpTextDecoderLayer.forward:1296-1303] hyper + (out (x) w).flatten
    injection = branch[..., None, :] * weights[..., :, None]
    return hyper_input + injection.reshape(hyper_input.shape)


class GatedDeltaNet(nn.Module):
    """[HF Qwen4ExpTextGatedDeltaNet:456-617] ``mx.conv1d`` (S:282-287) with
    silu rounded once (T:627-636, D4); the perf eps adapter on mlx-lm's kernel."""

    def __init__(self, args: TextModelArgs):
        super().__init__()
        self.hidden = args.hidden_size
        self.hv, self.hk = args.linear_num_value_heads, args.linear_num_key_heads
        self.dk, self.dv = args.linear_key_head_dim, args.linear_value_head_dim
        self.key_dim, self.value_dim = self.hk * self.dk, self.hv * self.dv
        self.conv_dim = 2 * self.key_dim + self.value_dim
        self.kernel = args.linear_conv_kernel_dim
        self.conv1d = nn.Conv1d(self.conv_dim, self.conv_dim, self.kernel, groups=self.conv_dim, bias=False)
        self.in_proj_qkv = nn.Linear(self.hidden, self.conv_dim, bias=False)
        self.in_proj_z = nn.Linear(self.hidden, self.value_dim, bias=False)
        self.in_proj_b = nn.Linear(self.hidden, self.hv, bias=False)
        self.in_proj_a = nn.Linear(self.hidden, self.hv, bias=False)
        self.dt_bias = mx.ones((self.hv,))
        self.A_log = mx.zeros((self.hv,))
        self.norm = GatedRMSNorm(self.dv, args.rms_norm_eps, args.output_gate_type or args.hidden_act)
        self.out_proj = nn.Linear(self.value_dim, self.hidden, bias=False)
        exact_f32(1.0 / self.dk), exact_f32(self.dk ** -0.5)  # gated_delta's l2norm scales

    def __call__(self, x: mx.array, ctx: _Context, cache: Qwen4ExpLinearCache) -> mx.array:
        B, S, _ = x.shape
        dt = x.dtype
        mask = ctx.ssm_mask
        if mask is not None:  # [HF apply_mask_to_padding_states]
            x = mx.where(mask[..., None], x, mx.zeros((), dt))
        qkv = self.in_proj_qkv(x)
        z = self.in_proj_z(x).reshape(B, S, self.hv, self.dv)
        b = self.in_proj_b(x)
        a = self.in_proj_a(x)

        hist = self.kernel - 1
        conv_state = cache[0]
        if conv_state is None:
            conv_state = mx.zeros((B, hist, self.conv_dim), dtype=qkv.dtype)
        full = mx.concatenate([conv_state, qkv], axis=1)
        cache[0] = conv_history_tail(full, hist)
        conv = silu_once(self.conv1d(full))  # [HF causal_conv1d_fn/_update]

        q, k, v = mx.split(conv, [self.key_dim, 2 * self.key_dim], axis=-1)
        q = q.reshape(B, S, self.hk, self.dk)
        k = k.reshape(B, S, self.hk, self.dk)
        v = v.reshape(B, S, self.hv, self.dv)
        out, cache[1] = gated_delta(q, k, v, a, b, self.A_log, self.dt_bias, cache[1], mask,
                                    use_kernel=not self.training)
        cache.advance(S)
        out = self.norm(out.astype(dt), z)
        return self.out_proj(out.reshape(B, S, -1))


class _Selection(SimpleNamespace):
    """What the indexer decided for one call: ``kind`` in dense | mask |
    kernel | gather, plus a mask and/or token indices."""


class QSAIndexer(nn.Module):
    """[HF Qwen4ExpTextQSAIndexer:665-771] block selection.

    Block keys come from the per-block cache (T:986-1007, the perf design);
    scores ``sum_h relu(q_h . kb) / sqrt(Di)`` in fp32 (T:1052-1056, D7); the
    tie rule is ``topk_mask_lowest_index`` (D0). The result is a mask or the
    per-query token lists of the perf kernel, per the dispatch policy.
    """

    # Diagnostics, off by default (plain class attribute, never an MLX
    # parameter): when True, ``last`` keeps the last sparse call's scores,
    # block selection and exact-tie count.
    record_selection = False
    # Rows of queries scored at once (bounds the [S*H, NB] fp32 score transient).
    score_bytes = 256 * 2 ** 20

    def __init__(self, args: TextModelArgs):
        super().__init__()
        self.n_heads = args.indexer_n_heads
        self.head_dim = args.indexer_head_dim
        self.ratio = args.indexer_compress_ratio
        self.block_topk = args.block_topk
        self.index_qk_proj = nn.Linear(args.hidden_size, (self.n_heads + args.indexer_kv_heads) * self.head_dim,
                                       bias=False)
        self.q_layernorm = OffsetRMSNorm(self.head_dim, eps=args.rms_norm_eps)
        self.k_layernorm = OffsetRMSNorm(self.head_dim, eps=args.rms_norm_eps)
        self.last = None

    def _update_blocks(self, cache: Qwen4ExpQSACache, S: int, inv_freq: mx.array):
        """Compute the blocks completed by this call, once (T:986-1007)."""
        B = cache.raw_keys.shape[0]
        r = self.ratio
        L_new = cache.offset
        L_old = L_new - S
        lp = cache.lp(B)
        nb_old = np.maximum(L_old - lp, 0) // r
        nb_new = np.maximum(L_new - lp, 0) // r
        M = int((nb_new - nb_old).max())
        if M <= 0:
            return
        if not lp.any():
            j0 = int(nb_old[0])
            raw = cache.raw_keys[:, j0 * r:(j0 + M) * r].reshape(B, M, r, self.head_dim)
            j = None
            starts = (j0 + np.arange(M, dtype=np.int64)) * r
            pos = np.broadcast_to(starts[None], (B, M))
        else:
            jj = nb_old[:, None] + np.arange(M, dtype=np.int64)[None, :]
            tok = lp[:, None, None] + jj[..., None] * r + np.arange(r, dtype=np.int64)
            tok = np.clip(tok, 0, L_new - 1).reshape(B, M * r)
            raw = mx.take_along_axis(cache.raw_keys, mx.array(tok.astype(np.int32))[..., None], axis=1)
            raw = raw.reshape(B, M, r, self.head_dim)
            j, j0, pos = jj, 0, jj * r
        # [HF:733-742] fp32 mean rounded to the key dtype, k_layernorm, RoPE at
        # the block's first position (logical j*r).
        pooled = raw.astype(_F32).mean(axis=2).astype(raw.dtype)
        pooled = self.k_layernorm(pooled)
        cos, sin = rope_cos_sin(mx.array(np.ascontiguousarray(pos).astype(np.int32)), inv_freq)
        cache.write_blocks(j0, apply_rope(pooled, cos, sin), j)

    def __call__(self, x: mx.array, ctx: _Context, cache: Qwen4ExpQSACache) -> _Selection:
        B, S, _ = x.shape
        qk = self.index_qk_proj(x)
        iq = qk[..., :self.n_heads * self.head_dim].reshape(B, S, self.n_heads, self.head_dim)
        ik = qk[..., self.n_heads * self.head_dim:]
        iq = self.q_layernorm(iq)
        iq = apply_rope(iq, ctx.cos[:, :, None, :], ctx.sin[:, :, None, :])
        cache.append_index_keys(ik)
        self._update_blocks(cache, S, ctx.inv_freq)
        return self._select(iq, ctx, cache)

    def _scores(self, iq: mx.array, bk: mx.array) -> mx.array:
        """[B, S, H, Di] x [B, NB, Di] -> [B, S, NB] fp32 (P:317-326)."""
        B, S, H, D = iq.shape
        s = iq.astype(_F32).reshape(B, S * H, D) @ bk.astype(_F32).swapaxes(-1, -2)
        s = mx.maximum(s, 0.0).reshape(B, S, H, -1).sum(axis=2)
        return s / math.sqrt(D)

    def _select(self, iq: mx.array, ctx: _Context, cache: Qwen4ExpQSACache) -> _Selection:
        B, S = iq.shape[:2]
        r, K = self.ratio, self.block_topk
        L = cache.offset
        lp = cache.lp(B)
        padded = bool(lp.any())
        t = (L - S) + np.arange(S, dtype=np.int64)                          # physical query index
        pos = t[None, :] - lp[:, None]                                       # (B, S) logical
        n_t = np.maximum(pos + 1, 0) // r                                    # visible complete blocks
        pad_q = pos < 0

        if int(n_t.max()) <= K:
            # Every visible block is selected: QSA is exactly causal attention.
            self.last = None
            if not padded:
                return _Selection(kind="dense", mask=None if S == 1 else "causal")
            return _Selection(kind="dense", mask=self._dense_mask(t, lp, L, pad_q))

        NB = int((np.maximum(L - lp, 0) // r).max())
        bk = cache.block_keys[:, :NB]
        valid_blk = mx.arange(NB)[None, None, :] < mx.array(n_t.astype(np.int32))[..., None]
        rows = max(1, min(S, self.score_bytes // max(B * self.n_heads * NB * 4, 1)))
        sels, all_scores = [], []
        for s0 in range(0, S, rows):
            sc = self._scores(iq[:, s0:s0 + rows], bk)
            vb = valid_blk[:, s0:s0 + rows]
            masked = mx.where(vb, sc, -mx.inf)
            sels.append(topk_mask_lowest_index(masked, K) & vb)
            if self.record_selection:
                all_scores.append(masked)
        sel_blk = sels[0] if len(sels) == 1 else mx.concatenate(sels, axis=1)
        if self.record_selection:
            scores = all_scores[0] if len(all_scores) == 1 else mx.concatenate(all_scores, axis=1)
            srt = mx.sort(scores, axis=-1)
            kth, k1th = srt[..., NB - K], srt[..., NB - K - 1]
            ties = (kth == k1th) & mx.array(n_t > K) & (kth > -mx.inf)
            self.last = SimpleNamespace(scores=scores, blocks=sel_blk, n_visible=n_t,
                                        straddling_ties=int(ties.sum().item()),
                                        sparse_queries=int((n_t > K).sum()))
        else:
            self.last = None

        if S == 1:
            use_indices = L >= ctx.decode_min_kv
        else:
            use_indices = L >= ctx.prefill_min_kv and ctx.kernel_ok
        if not use_indices:
            return _Selection(kind="mask", mask=self._token_mask(sel_blk, t, lp, L, n_t, pad_q, NB))
        idx = self._token_indices(sel_blk, t, lp, n_t, pad_q)
        if S > 1:
            return _Selection(kind="kernel", idx=idx)
        # Host-known: fewer than K visible blocks, a short tail, or padding.
        any_invalid = bool(padded or (n_t < K).any() or ((pos + 1) % r < r - 1).any())
        return _Selection(kind="gather", idx=idx[:, 0], valid=(idx[:, 0] >= 0) if any_invalid else None)

    @staticmethod
    def _dense_mask(t, lp, L, pad_q):
        ar = np.arange(L, dtype=np.int64)
        m = (ar[None, None, :] <= t[None, :, None]) & (ar[None, None, :] >= lp[:, None, None])
        m |= (ar[None, None, :] == t[None, :, None]) & pad_q[..., None]
        return mx.array(m)[:, None]

    def _token_mask(self, sel_blk, t, lp, L, n_t, pad_q, NB):
        """Selected blocks -> token mask [B, 1, S, L] incl. the open tail (T:1064-1086)."""
        B, S = sel_blk.shape[:2]
        r = self.ratio
        if not lp.any():
            tok_sel = mx.repeat(sel_blk, r, axis=-1)
            if NB * r < L:
                tok_sel = mx.concatenate([tok_sel, mx.zeros((B, S, L - NB * r), dtype=mx.bool_)], axis=-1)
        else:
            blk_of_tok = (np.arange(L, dtype=np.int64)[None, :] - lp[:, None]) // r      # (B, L)
            in_block = mx.array((blk_of_tok >= 0) & (blk_of_tok < NB))
            gidx = mx.array(np.clip(blk_of_tok, 0, NB - 1).astype(np.int32))
            tok_sel = mx.take_along_axis(sel_blk, mx.broadcast_to(gidx[:, None, :], (B, S, L)), axis=2)
            tok_sel = tok_sel & in_block[:, None, :]
        ar = np.arange(L, dtype=np.int64)
        tail_start = lp[:, None] + n_t * r                                               # (B, S)
        fixed = ((ar[None, None, :] <= t[None, :, None]) & (ar[None, None, :] >= lp[:, None, None]))
        tail = fixed & (ar[None, None, :] >= tail_start[..., None])
        diag = (ar[None, None, :] == t[None, :, None]) & pad_q[..., None]
        mask = (mx.array(fixed) & tok_sel) | mx.array(tail | diag)
        return mask[:, None]

    def _token_indices(self, sel_blk, t, lp, n_t, pad_q):
        """Selected blocks -> per-query token lists [B, S, K*r + r - 1 (+1)],
        -1 = unused (the perf kernel's input, P:483-509, with per-row padding)."""
        B, S, NB = sel_blk.shape
        r, K = self.ratio, self.block_topk
        # The K smallest of -sel are exactly the selected blocks (<= K of them).
        order = mx.argpartition(-sel_blk.astype(mx.int32), kth=K - 1, axis=-1)[..., :K]
        keep = mx.take_along_axis(sel_blk, order, axis=-1)
        tok = mx.array(lp.astype(np.int32))[:, None, None, None] + order[..., None].astype(mx.int32) * r \
            + mx.arange(r, dtype=mx.int32)
        tok = mx.where(keep[..., None], tok, -1).reshape(B, S, K * r)
        tail = (lp[:, None] + n_t * r)[..., None] + np.arange(r - 1, dtype=np.int64)       # (B, S, r-1)
        tail = np.where(tail <= t[None, :, None], tail, -1)
        parts = [tok, mx.array(tail.astype(np.int32))]
        if pad_q.any():  # pad queries attend to themselves (outputs discarded, kept finite)
            parts.append(mx.array(np.where(pad_q, t[None, :], -1).astype(np.int32))[..., None])
        return mx.concatenate(parts, axis=-1)


class QSAAttention(nn.Module):
    """[HF Qwen4ExpTextAttention:811-893] gated GQA attention, QSA selection."""

    # Path counters (diagnostics; plain class attribute).
    paths = SimpleNamespace(dense=0, mask=0, kernel=0, gather=0, gather_single=0)

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

    def __call__(self, x: mx.array, ctx: _Context, cache: Qwen4ExpQSACache) -> mx.array:
        B, S, _ = x.shape
        D = self.head_dim
        qg = self.q_proj(x).reshape(B, S, self.n_heads, 2 * D)
        q, gate = qg[..., :D], qg[..., D:]
        gate = gate.reshape(B, S, self.n_heads * D)
        q = self.q_norm(q).transpose(0, 2, 1, 3)
        k = self.k_norm(self.k_proj(x).reshape(B, S, self.n_kv, D)).transpose(0, 2, 1, 3)
        v = self.v_proj(x).reshape(B, S, self.n_kv, D).transpose(0, 2, 1, 3)
        cos, sin = ctx.cos[:, None], ctx.sin[:, None]
        q = apply_rope(q, cos, sin)
        k = apply_rope(k, cos, sin)
        keys, values = cache.update_and_fetch(k, v)
        sel = self.indexer(x, ctx, cache)
        out = self._core(q, keys, values, cache, sel)
        out = out.transpose(0, 2, 1, 3).reshape(B, S, -1)
        out = out * sigmoid_once(gate)
        out = self.o_proj(out)
        # The indexer's cache writes (raw keys, completed block keys) feed the
        # output only once a query drops blocks; in the dense regime (fewer
        # than budget + ratio tokens) and between block completions nothing
        # reads them. mlx-lm evaluates only the logits per decode step, so
        # without this tie the writes pile up as one unevaluated graph that runs
        # in a burst at the first sparse token, or never (mlx-lm #1662 class;
        # validation round 1, systems HIGH).
        return mx.depends(out, [a for a in (cache.raw_keys, cache.block_keys) if a is not None])

    def _core(self, q, keys, values, cache, sel):
        p = QSAAttention.paths
        if sel.kind == "dense":
            p.dense += 1
            if sel.mask is None:
                return mx.fast.scaled_dot_product_attention(q, keys, values, scale=self.scale)
            return sdpa_query_chunked(q, keys, values, self.scale, sel.mask)
        if sel.kind == "mask":
            p.mask += 1
            return sdpa_query_chunked(q, keys, values, self.scale, sel.mask)
        if sel.kind == "kernel":
            p.kernel += 1
            return qsa_sparse_attention(q, cache.keys, cache.values, sel.idx, self.scale)
        # Decode gather: attend over the selected rows only (P:417-442).
        p.gather += 1
        idx = sel.idx                                                      # (B, W)
        if idx.shape[0] == 1 and sel.valid is None:
            p.gather_single += 1  # one row, every slot valid (released config: decode past 8192)
            ks, vs = mx.take(keys, idx[0], axis=2), mx.take(values, idx[0], axis=2)
            return mx.fast.scaled_dot_product_attention(q, ks, vs, scale=self.scale)
        g = mx.maximum(idx, 0)[:, None, :, None]
        ks, vs = mx.take_along_axis(keys, g, axis=2), mx.take_along_axis(values, g, axis=2)
        m = None if sel.valid is None else sel.valid[:, None, None, :]
        return mx.fast.scaled_dot_product_attention(q, ks, vs, scale=self.scale, mask=m)


class MLP(nn.Module):
    """[HF Qwen4ExpTextMLP:896-909] shared expert, silu rounded once."""

    def __init__(self, dim: int, hidden: int):
        super().__init__()
        self.gate_proj = nn.Linear(dim, hidden, bias=False)
        self.up_proj = nn.Linear(dim, hidden, bias=False)
        self.down_proj = nn.Linear(hidden, dim, bias=False)

    def __call__(self, x):
        return self.down_proj(silu_once(self.gate_proj(x)) * self.up_proj(x))


class FusedSwitchGLU(nn.Module):
    """Routed experts with HF's fused ``gate_up_proj`` [E, 2I, H] (gate rows
    first; P:814-861): one ``gather_mm``/``gather_qmm`` for gate+up, then
    ``silu_once(gate) * up`` (HF ``_apply_gate``), then down. Built on mlx-lm's
    ``SwitchLinear`` so load-time quantization (``to_quantized``) applies."""

    def __init__(self, dims: int, hidden: int, num_experts: int):
        super().__init__()
        self.gate_up_proj = SwitchLinear(dims, 2 * hidden, num_experts, bias=False)
        self.down_proj = SwitchLinear(hidden, dims, num_experts, bias=False)

    def __call__(self, x: mx.array, indices: mx.array) -> mx.array:
        x = mx.expand_dims(x, (-2, -3))
        do_sort = indices.size >= 64
        idx, inv_order = indices, None
        if do_sort:
            x, idx, inv_order = _gather_sort(x, indices)
        h = self.gate_up_proj(x, idx, sorted_indices=do_sort)
        gate, up = mx.split(h, 2, axis=-1)
        x = self.down_proj(silu_once(gate) * up, idx, sorted_indices=do_sort)
        if do_sort:
            x = _scatter_unsort(x, inv_order, indices.shape)
        return x.squeeze(-2)


class SparseMoeBlock(nn.Module):
    """[HF Qwen4ExpTextSparseMoeBlock + TopKRouter:952-992].

    Router: fp32 softmax, top-k of the fp32 probabilities (mlx-vlm audit P1),
    renormalised in fp32, cast to the logit dtype. Exact fp32 ties at the cut
    are broken by ``argpartition`` (``torch.topk``'s CPU order is unspecified
    and not reproducible either). With bf16 logits such ties are common at
    the released scale (512 experts, top-10): a real-weight bf16 prefill
    ties on 8 of 54 router rows at layer 2 (official model; 7 in this port)
    and 5 of 54 at layer 3, 0 in fp32; a tied swap selects a different expert
    of equal weight, so parity checks must be tie-aware. Combine: the k
    weighted rows summed in fp32 and rounded once, as the reference's default
    ``grouped_mm`` experts path (transformers moe.py; T:1195, D6)."""

    def __init__(self, args: TextModelArgs):
        super().__init__()
        self.top_k = args.num_experts_per_tok
        self.norm_topk_prob = args.norm_topk_prob
        self.gate = nn.Linear(args.hidden_size, args.num_experts, bias=False)
        self.switch_mlp = FusedSwitchGLU(args.hidden_size, args.moe_intermediate_size, args.num_experts)
        self.shared_expert = MLP(args.hidden_size, args.shared_expert_intermediate_size)
        self.shared_expert_gate = nn.Linear(args.hidden_size, 1, bias=False)

    def route(self, x: mx.array):
        logits = self.gate(x)
        probs = mx.softmax(logits.astype(_F32), axis=-1)
        k = self.top_k
        inds = mx.argpartition(-probs, kth=k - 1, axis=-1)[..., :k]
        scores = mx.take_along_axis(probs, inds, axis=-1)
        if self.norm_topk_prob:
            scores = scores / scores.sum(axis=-1, keepdims=True)
        return logits, inds, scores.astype(logits.dtype)

    def __call__(self, x: mx.array) -> mx.array:
        _, inds, scores = self.route(x)
        y = self.switch_mlp(x, inds)
        y = (y * scores[..., None]).astype(_F32).sum(axis=-2).astype(x.dtype)
        shared = sigmoid_once(self.shared_expert_gate(x)) * self.shared_expert(x)
        return y + shared


class PLELayer(nn.Module):
    """[HF Qwen4ExpTextPLELayer:1177-1249] (n-gram rows arrive pre-gathered).

    Gate: bf16 product, fp32 sum rounded once (T:1224), fp32 division by
    sqrt(hidden) rounded once (D8: MLX would round the Python divisor to bf16,
    50.596 -> 50.5 at the released hidden 2560, changing 35.9% of bf16 values
    in [2^-8, 2^8)); sigmoid and conv silu rounded once."""

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
        self.history = (args.ple_conv_kernel_size - 1) * args.ngram_size
        self.conv1d = nn.Conv1d(width, width, args.ple_conv_kernel_size, groups=width,
                                dilation=args.ngram_size, bias=False)
        exact_f32(math.sqrt(self.hidden))  # the D8 gate divisor

    def __call__(self, h: mx.array, emb: mx.array, ctx: _Context, cache: Qwen4ExpLinearCache) -> mx.array:
        B, S, _ = h.shape
        dt = h.dtype
        shape = (B, S, self.hc, self.hidden)
        key = self.norm_key(self.key_proj(emb)).reshape(shape)
        value = self.value_proj(emb)
        query = self.norm_query(h).reshape(shape)
        gate = (key * query).astype(_F32).sum(axis=-1, keepdims=True).astype(dt)
        gate = (gate.astype(_F32) / exact_f32(math.sqrt(self.hidden))).astype(dt)
        gate = mx.sqrt(mx.maximum(mx.abs(gate), 1e-6)) * mx.sign(gate)
        gated = sigmoid_once(gate) * value[:, :, None, :]
        gated_normed = self.norm_conv(gated.reshape(B, S, -1))
        gated = gated.reshape(B, S, -1)
        if ctx.ssm_mask is not None:
            zero = mx.zeros((), dt)
            gated = mx.where(ctx.ssm_mask[..., None], gated, zero)
            gated_normed = mx.where(ctx.ssm_mask[..., None], gated_normed, zero)
        # [HF _short_conv:1210-1227] dilated causal depthwise conv, zero history.
        state = cache[2]
        if state is None:
            state = mx.zeros((B, self.history, gated_normed.shape[-1]), dtype=gated_normed.dtype)
        full = mx.concatenate([state, gated_normed], axis=1)
        cache[2] = conv_history_tail(full, self.history)
        return gated + silu_once(self.conv1d(full))


class DecoderLayer(nn.Module):
    """[HF Qwen4ExpTextDecoderLayer:1252-1304]"""

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
        # Decode compilation is deliberately local to a layer.  Compiling the
        # model loop would capture the Python cache objects and make their
        # mutations invisible after the first trace.  It is lazy so mx.compile
        # sees the final (possibly quantized) module.
        self._decode_ctx = None
        self._compiled_decode = None

    def _decode_arrays(self, h: mx.array, ssm_mask: mx.array, ngram_emb: mx.array, *state):
        """Compiled boundary of one batch-1, one-token linear-attention layer.

        ``mx.compile`` may only track array data.  A short-lived cache view
        supplies the layer implementation with its Python protocol; all
        mutable device state crosses this boundary in ``state`` and in the
        returned tuple.  The linear body reads no host metadata that changes
        between tokens, so one trace per input shape serves every step.
        """
        shared, original = self._decode_ctx
        # The trace works on a private copy of the context: binding its tracer
        # placeholders into the forward's shared context would hand them to
        # every later layer as real inputs ("eval an array without a
        # primitive" at the first compiled step; review of 0715fdf74).  The
        # empty sentinels stand for the two optional arrays.
        ctx = SimpleNamespace(**vars(shared))
        ctx.ngram_emb = dict(shared.ngram_emb)
        ctx.ssm_mask = None if ssm_mask.size == 0 else ssm_mask
        if self.has_ple:
            ctx.ngram_emb[self.layer_idx] = ngram_emb
        view = Qwen4ExpLinearCache(len(state))
        view.padding, view.offset = original.padding, original.offset
        view.cache = list(state)
        out = self._body(h, ctx, view)
        return (out, *view.cache)

    def _qsa_pre(self, h: mx.array):
        x, _, inject = self.attn_hyper_connection(h)
        return x, inject

    def _qsa_post(self, h: mx.array, attn: mx.array, inject: mx.array) -> mx.array:
        h = _inject(h, attn, inject)
        x, hyper, inject = self.mlp_hyper_connection(h)
        return _inject(hyper, self.mlp(x), inject)

    def _body(self, h: mx.array, ctx: _Context, cache) -> mx.array:
        """The common layer body; prefill always calls this directly."""
        if self.has_ple:
            h = h + self.ple(h, ctx.ngram_emb[self.layer_idx], ctx, cache)
        x, hyper, inject = self.attn_hyper_connection(h)
        x = self.linear_attn(x, ctx, cache) if self.is_linear else self.self_attn(x, ctx, cache)
        h = _inject(hyper, x, inject)
        x, hyper, inject = self.mlp_hyper_connection(h)
        return _inject(hyper, self.mlp(x), inject)

    def __call__(self, h: mx.array, ctx: _Context, cache, compile_decode: bool = True) -> mx.array:
        # Prefill (and every batched/multi-token call) remains uncompiled.
        if not compile_decode or ctx.B != 1 or ctx.S != 1 or cache.offset == 0:
            return self._body(h, ctx, cache)
        if not self.is_linear:
            # QSA: the hyper-connections and the MoE are compiled; attention
            # stays eager.  Its cache protocol slices and selects on the host
            # offset (and builds offset-sized masks on the host), so a compiled
            # attention must retrace at every token: slower than eager, and
            # every trace with its offset-sized constants stays in mlx's
            # compile cache for the life of the model (review of 0715fdf74).
            if self._compiled_decode is None:
                self._compiled_decode = (mx.compile(self._qsa_pre, inputs=EXACT_F32, shapeless=False),
                                         mx.compile(self._qsa_post, inputs=EXACT_F32, shapeless=False))
            pre, post = self._compiled_decode
            x, inject = pre(h)
            return post(h, self.self_attn(x, ctx, cache), inject)
        if self._compiled_decode is None:
            self._compiled_decode = mx.compile(self._decode_arrays, inputs=EXACT_F32, shapeless=False)
        empty = mx.zeros((0,), dtype=h.dtype)
        self._decode_ctx = (ctx, cache)
        try:
            result = self._compiled_decode(h, ctx.ssm_mask if ctx.ssm_mask is not None else empty,
                                           ctx.ngram_emb[self.layer_idx] if self.has_ple else empty,
                                           *cache.cache)
        finally:
            self._decode_ctx = None
        cache.cache = list(result[1:])
        # _body advanced only the view; the owning cache carries host state.
        cache.advance(1)
        return result[0]


class Qwen4ExpTextModel(nn.Module):
    def __init__(self, args: TextModelArgs):
        super().__init__()
        self.args = args
        self.embed_tokens = nn.Embedding(args.vocab_size, args.hidden_size)
        self.layers = [DecoderLayer(args, i) for i in range(args.num_hidden_layers)]
        self.hyper_connection_mixer = GatedResidual(args, use_combine=False)


class _NgramRuntime:
    """Host-side n-gram state (plain object: never an MLX parameter)."""

    def __init__(self, args: TextModelArgs, meta: dict):
        self.args = args
        self.specs: Dict[int, NgramHashSpec] = {}
        for ple_index, lid in enumerate(args.ple_layer_ids):
            self.specs[lid - 1] = NgramHashSpec(args, ple_index)
        self.meta = meta or {}
        self.base_dir: Optional[Path] = None
        self.io = self.meta.get("io", "mmap")
        self.tables: Dict[int, NgramTable] = {}

    def resolve_dir(self) -> Path:
        if self.base_dir is not None:
            return self.base_dir
        d = Path(self.meta.get("dir", "."))
        return d if d.is_absolute() else Path(__file__).resolve().parent / d

    def table(self, layer_idx: int) -> NgramTable:
        if layer_idx not in self.tables:
            entry = self.meta.get("layers", {}).get(str(layer_idx))
            if entry is None:
                raise FileNotFoundError(f"no n-gram table registered for layer {layer_idx}; convert with "
                                        "scripts/align_convert_qwen4_exp.py")
            spec = self.specs[layer_idx]
            if int(entry["rows"]) != spec.padded_vocab_size or int(entry["dim"]) != spec.head_dim:
                raise ValueError("n-gram table shape does not match the config")
            self.tables[layer_idx] = NgramTable(self.resolve_dir() / entry["file"], entry["rows"], entry["dim"],
                                                entry["format"], entry.get("group_size", 32), io=self.io)
        return self.tables[layer_idx]


class TextModel(nn.Module):
    def __init__(self, args: TextModelArgs, runtime: Optional[ModelArgs] = None):
        super().__init__()
        self.args = args
        self.model_type = args.model_type
        self.model = Qwen4ExpTextModel(args)
        if not args.tie_word_embeddings:
            self.lm_head = nn.Linear(args.hidden_size, args.vocab_size, bias=False)
        self._inv_freq = rope_inv_freq(args)
        self._ngram = _NgramRuntime(args, runtime.ngram_tables if runtime else {})
        self._prefill_min_kv = runtime.qsa_sparse_prefill_min_kv if runtime else QSA_SPARSE_PREFILL_MIN_KV
        self._decode_min_kv = runtime.qsa_sparse_decode_min_kv if runtime else QSA_SPARSE_DECODE_MIN_KV
        self._first_linear = (args.layer_types.index("linear_attention")
                              if "linear_attention" in args.layer_types else None)
        self._kernel_ok = sparse_kernel_supported(args.head_dim, args.num_attention_heads, args.num_key_value_heads)
        self.compile_decode = runtime.compile_decode if runtime else True

    @property
    def layers(self):
        return self.model.layers

    def make_cache(self, left_padding: Optional[Sequence[int]] = None):
        return make_layer_caches(self.args, left_padding)

    def _gather_ngrams(self, ids: np.ndarray, ctx: _Context, cache, dtype) -> None:
        if ctx.valid_host is not None:  # [HF:1467-1470] pads hash as EOS
            ids = np.where(ctx.valid_host, ids, self.args.eos_id)
        for layer_idx, spec in self._ngram.specs.items():
            c = cache[layer_idx]
            ctx_ids = c[3]
            if ctx_ids is None:
                ctx_np = np.full((ctx.B, spec.context_len), spec.eos, dtype=np.int64)
            else:
                ctx_np = np.asarray(ctx_ids).astype(np.int64)
            history = np.concatenate([ctx_np, ids], axis=1)
            rows = self._ngram.table(layer_idx).gather(spec.ngram_ids(history, ctx.S))
            c[3] = mx.array(history[:, history.shape[1] - spec.context_len:].astype(np.int32))
            ctx.ngram_emb[layer_idx] = mx.array(rows.reshape(ctx.B, ctx.S, -1)).astype(dtype)

    def __call__(self, inputs: mx.array, cache=None, input_embeddings=None) -> mx.array:
        if input_embeddings is not None:
            raise NotImplementedError("qwen4_exp PLE needs token ids; input_embeddings are unsupported")
        if inputs.ndim != 2 or inputs.shape[1] == 0:
            raise ValueError("non-empty [batch, tokens] input required")
        B, S = inputs.shape
        if cache is None:
            cache = self.make_cache()
        if len(cache) != len(self.model.layers):
            raise ValueError("wrong cache layer count")
        offsets = {c.offset for c in cache}
        if len(offsets) != 1:
            raise ValueError(f"hybrid cache offsets disagree: {sorted(offsets)}")
        c0 = cache[0]
        if any(cache_kind(c) is None for c in cache):
            raise TypeError("qwen4_exp needs the caches of make_cache()")
        lp = (c0.lp(B) if cache_kind(c0) == "qsa"
              else (np.asarray(c0.padding, np.int64) if c0.padding is not None else np.zeros((B,), np.int64)))
        ssm = create_ssm_mask(inputs, cache[self._first_linear]) if self._first_linear is not None else None
        ctx = _Context(B, S, c0.offset, lp, self._inv_freq, ssm, self._prefill_min_kv, self._decode_min_kv,
                       self._kernel_ok)
        if ssm is None and ctx.valid_host is not None:
            ctx.ssm_mask = mx.array(ctx.valid_host)

        h = self.model.embed_tokens(inputs)
        if self._ngram.specs:
            # Host sync: the n-gram rows depend on the token ids just fed.
            self._gather_ngrams(np.asarray(inputs).astype(np.int64), ctx, cache, h.dtype)
        h = mx.tile(h, (1, 1, self.args.hc_count))
        for layer, c in zip(self.model.layers, cache):
            h = layer(h, ctx, c, compile_decode=self.compile_decode)
        h = self.model.hyper_connection_mixer(h)
        if self.args.tie_word_embeddings:
            return self.model.embed_tokens.as_linear(h)
        return self.lm_head(h)


# --------------------------------------------------------------------------
# Weight names and precision policy (shared with the converter)
# --------------------------------------------------------------------------


def hf_to_mlx_key(key: str) -> Optional[str]:
    """Reference/HF checkpoint key -> this port's parameter path (T:1385-1403).

    ``None`` for weights the text path does not use (``mtp.*``, vision).
    Already-converted keys map to themselves."""
    if key.startswith(("mtp.", "model.mtp.")):
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


NGRAM_BUFFER_SUFFIXES = ("ple.ple_embedding.layer_multipliers", "ple.ple_embedding.ngram_heads_vocab_sizes",
                         "ple.ple_embedding.ngram_heads_offsets")


def is_ngram_table_key(key: str) -> bool:
    return ".ple.ple_embedding.ngram_embedding." in key


def is_ngram_buffer_key(key: str) -> bool:
    return key.endswith(NGRAM_BUFFER_SUFFIXES)


def ngram_buffer_expected(args: TextModelArgs, key: str) -> List[int]:
    """Expected value of a serialized n-gram hash buffer (S:651-657 check)."""
    layer_idx = int(key.split(".layers.", 1)[1].split(".", 1)[0])
    spec = NgramHashSpec(args, args.ple_layer_ids.index(layer_idx + 1))
    if key.endswith("layer_multipliers"):
        return list(spec.multipliers)
    if key.endswith("ngram_heads_vocab_sizes"):
        return list(spec.head_vocab_sizes)
    return list(spec.head_offsets)


# Precision profiles (S qwen4_exp_tables.py:157-222). maxfit / maxfit5: ONLY the
# routed experts quantized (6 / 5 bit, group 64, affine); every other float
# weight native bf16; the n-gram table bf16 on disk (GOAL precision target).
MAXFIT_BITS = {"maxfit": 6, "maxfit5": 5}
PROFILES = ("fp32", "bf16", "mixed", *MAXFIT_BITS)


def ple_storage_for(profile: str, storage: Optional[str] = None, group_size: int = 64) -> str:
    """Resolve the n-gram table format; refuse overrides that change maxfit."""
    if profile not in PROFILES:
        raise ValueError(f"unknown precision profile: {profile}")
    if profile in MAXFIT_BITS:
        if group_size != 64:
            raise ValueError("maxfit profiles require group_size=64")
        if storage not in (None, "bf16"):
            raise ValueError("maxfit profiles require the bf16 n-gram table")
        return "bf16"
    if storage not in (None, *NGRAM_FORMATS):
        raise ValueError(f"unknown n-gram storage: {storage}")
    return storage or {"fp32": "f32", "bf16": "bf16"}.get(profile, "q4")


def quantization_for(path: str, shape: Sequence[int], profile: str, group_size: int = 64) -> Optional[dict]:
    """Quantization of the module at ``path`` (``None`` = keep float).

    maxfit*: routed experts (``.switch_mlp.``) only. mixed: experts 4 bit,
    other wide linears 8 bit, keeping float the selection-critical and small
    modules (twin keep-float list T:1421-1447 plus Sol's: router, shared gate,
    QSA indexer, DeltaNet, hyper-connection gates, convs, norms, embeddings of
    the n-gram table)."""
    if profile not in PROFILES:
        raise ValueError(f"unknown precision profile: {profile}")
    if profile in ("fp32", "bf16") or len(shape) < 2:
        return None
    is_expert = ".switch_mlp." in path
    if profile in MAXFIT_BITS:
        if not is_expert:
            return None
        if shape[-1] % group_size:
            raise ValueError(f"maxfit expert width must divide group_size={group_size}: {path}")
        return {"group_size": group_size, "bits": MAXFIT_BITS[profile], "mode": "affine"}
    keep_float = (path.endswith(".mlp.gate"), path.endswith(".shared_expert_gate"), ".indexer." in path,
                  ".linear_attn." in path, "conv1d" in path, "hyper_connection" in path,
                  ".ple_embedding." in path)
    if any(keep_float) or shape[-1] % group_size:
        return None
    return {"group_size": group_size, "bits": 4 if is_expert else 8, "mode": "affine"}


# --------------------------------------------------------------------------
# Top-level model (mlx-lm entry point)
# --------------------------------------------------------------------------


class Model(nn.Module):
    def __init__(self, args: ModelArgs):
        super().__init__()
        self.args = args
        self.model_type = args.model_type
        self.language_model = TextModel(TextModelArgs.from_dict(args.text_config), args)

    def __call__(self, inputs: mx.array, cache=None, input_embeddings=None):
        return self.language_model(inputs, cache=cache, input_embeddings=input_embeddings)

    @property
    def layers(self):
        return self.language_model.model.layers

    def make_cache(self, left_padding: Optional[Sequence[int]] = None):
        """Per-layer caches; ``left_padding`` (one int per row) carries the
        batch's left padding for every later call."""
        return self.language_model.make_cache(left_padding)

    # mlx-lm loads this file as an anonymous module that callers cannot import.
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

        Per-expert ``mlp.experts.{e}.{gate,up,down}_proj`` (the released
        serialization) and HF's fused ``mlp.experts.gate_up_proj`` both become
        ``mlp.switch_mlp.gate_up_proj`` [E, 2I, H] (gate rows first) and
        ``down_proj`` [E, H, I]. The n-gram table is served from disk: its rows
        are dropped and its hash buffers are checked against the config."""
        targs = self.language_model.args
        out: Dict[str, mx.array] = {}
        experts: Dict[Tuple[str, str], Dict[int, mx.array]] = {}
        for key, value in weights.items():
            mk = hf_to_mlx_key(key)
            if mk is None or is_ngram_table_key(mk):
                continue
            if is_ngram_buffer_key(mk):
                if np.array(value).astype(np.int64).tolist() != ngram_buffer_expected(targs, mk):
                    raise ValueError(f"n-gram hash buffer disagrees with the config: {key}")
                continue
            if ".mlp.experts." in mk:
                head, rest = mk.split(".mlp.experts.", 1)
                base = f"{head}.mlp.switch_mlp."
                if rest == "gate_up_proj":
                    out[base + "gate_up_proj.weight"] = value
                elif rest == "down_proj":
                    out[base + "down_proj.weight"] = value
                else:
                    e, proj, _ = rest.split(".")
                    experts.setdefault((head, proj), {})[int(e)] = value
                continue
            if mk.endswith((".mlp.switch_mlp.gate_proj.weight", ".mlp.switch_mlp.up_proj.weight")):
                # Split mlx-lm SwitchGLU layout [E, I, H] x2 -> fused gate_up.
                head, proj = mk.rsplit(".mlp.switch_mlp.", 1)
                experts.setdefault((head, "stacked_" + proj.split("_")[0]), {})[0] = value
                continue
            if mk.endswith("conv1d.weight") and value.ndim == 3 and value.shape[-1] != 1:
                value = value.moveaxis(2, 1)  # HF [C, 1, K] -> mlx [C, K, 1]
            out[mk] = value
        n_exp = targs.num_experts
        heads = sorted({h for h, _ in experts})
        for head in heads:
            if (head, "stacked_gate") in experts:
                g, u = experts[(head, "stacked_gate")][0], experts[(head, "stacked_up")][0]
                out[f"{head}.mlp.switch_mlp.gate_up_proj.weight"] = mx.concatenate([g, u], axis=1)
                continue
            per = {p: experts.get((head, p), {}) for p in ("gate_proj", "up_proj", "down_proj")}
            for p, d in per.items():
                if len(d) != n_exp:
                    raise ValueError(f"{head}: {p} has {len(d)}/{n_exp} experts")
            out[f"{head}.mlp.switch_mlp.gate_up_proj.weight"] = mx.stack(
                [mx.concatenate([per["gate_proj"][e], per["up_proj"][e]], axis=0) for e in range(n_exp)])
            out[f"{head}.mlp.switch_mlp.down_proj.weight"] = mx.stack([per["down_proj"][e] for e in range(n_exp)])
        if targs.tie_word_embeddings:
            out.pop("language_model.lm_head.weight", None)
        return out

    @property
    def quant_predicate(self):
        """Default mlx_lm.convert policy: the maxfit target (6-bit experts)."""
        def predicate(path, module):
            if not hasattr(module, "to_quantized"):
                return False
            return quantization_for(path, module.weight.shape, "maxfit") or False
        return predicate

    @property
    def cast_predicate(self):
        def predicate(path: str):
            return not path.endswith("A_log")
        return predicate
