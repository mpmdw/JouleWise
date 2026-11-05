"""Reusable MLX kernels for the qwen4_exp (Qwen3.8-Flash-Next) port.

Performance track of docs/align/qwen4_exp_port/GOAL.md (item 8); design notes
and measurements are in docs/align/qwen4_exp_port/perf.md.

Authority is transformers 5.22.1 ``models/qwen4_exp`` (vendored at
``.engine/transformers-qwen4_exp/modeling_qwen4_exp.py``; ``HF:<line>`` below
cites that file). The pinned mlx-lm is 0.31.3.

This file imports only ``mlx`` and ``mlx_lm`` (absolute imports, no joulewise
imports), so the canonical ``qwen4_exp.py`` can vendor it verbatim or load it
as a sibling of a ``model_file`` module. Every fast path has a straightforward
pure-MLX reference in section 4, used by tests/align/test_qwen4_exp_kernels.py.

Sections
  1. Gated DeltaNet: an adapter over mlx-lm's Metal ``gated_delta_kernel``.
     The kernel is reused unchanged. The call site changes: the l2norm eps,
     fp32 gate math, and the state layout.
  2. QSA indexer: block keys, scores, top-k block selection, the token mask,
     an incremental per-layer cache, sparse decode attention (gather + SDPA),
     and a new block-sparse prefill attention Metal kernel.
  3. MoE: an fp32 router and a SwitchGLU with fused gate_up via ``gather_qmm``.
     Optionally the shared expert is folded in as expert ``E``.
  4. References: literal transcriptions of the transformers math.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import partial
from typing import Any, List, Optional, Tuple

import mlx.core as mx
import mlx.nn as nn
from mlx_lm.models.gated_delta import gated_delta_kernel, gated_delta_ops

F32 = mx.float32

# --------------------------------------------------------------------------
# 1. Gated DeltaNet
# --------------------------------------------------------------------------
#
# transformers (HF:245-248, 403-448, 570-602) computes, per value head h and
# token t, with S in [Dk, Dv] layout:
#   q, k  <- l2norm(x) = x * rsqrt(sum(x^2) + 1e-6)     (fp32)
#   q     <- q / sqrt(Dk)
#   g      = -exp(A_log) * softplus(a.float() + dt_bias)  (log decay, fp32)
#   beta   = sigmoid(b)                                    (model dtype)
#   S      = S * exp(g)
#   S      = S + k (x) ((v - S^T k) * beta)
#   y      = S^T q
# with GQA head h reading key head h // (Hv / Hk) (repeat_interleave).
#
# mlx-lm 0.31.3 ``gated_delta_kernel`` (models/gated_delta.py) runs exactly this
# recurrence with S stored [Dv, Dk] and g passed as the multiplicative decay
# exp(g); its GQA mapping ``hk = hv / (Hv / Hk)`` is repeat_interleave. The
# kernel is reused unchanged. Its *callers* in qwen3_next.py / qwen3_5.py differ
# from qwen4_exp in three call-site details, which this adapter fixes:
#   (a) l2norm eps: they use ``Dk**-1 * rms_norm(q, eps=1e-6)``, which equals
#       q * rsqrt(sum(q^2) + Dk*1e-6) / sqrt(Dk), so the effective eps is
#       1.28e-4 instead of 1e-6. With rms_norm eps = 1e-6 / Dk the identity is
#       exact: Dk**-0.5 * rms_norm(x, eps/Dk) = x * rsqrt(sum(x^2) + eps).
#   (b) precision: they compute softplus(a + dt_bias) in the model dtype and
#       feed q/k in the model dtype. HF does both in fp32. Here a is cast
#       first, and fp32 q/k feed the kernel, whose y is then fp32 and is cast
#       to the model dtype as in HF.
#   (c) the output norm gate is sigmoid (config.output_gate_type), not silu:
#       see ``rms_norm_gated``.

GDN_L2NORM_EPS = 1e-6


def gdn_qk_normalize(
    q: mx.array, k: mx.array, eps: float = GDN_L2NORM_EPS
) -> Tuple[mx.array, mx.array]:
    """HF ``l2norm`` of q and k in fp32, with q also scaled by ``Dk**-0.5``.

    Uses ``mx.fast.rms_norm`` at ``eps / Dk``, which is the exact algebraic
    identity of the HF formula (see the section comment).
    """
    dk = q.shape[-1]
    qn = mx.fast.rms_norm(q.astype(F32), None, eps / dk) * (1.0 / dk)
    kn = mx.fast.rms_norm(k.astype(F32), None, eps / dk) * (dk**-0.5)
    return qn, kn


@partial(mx.compile, shapeless=True)
def gdn_gates(
    a: mx.array, b: mx.array, A_log: mx.array, dt_bias: mx.array
) -> Tuple[mx.array, mx.array]:
    """Return (beta, decay): beta = sigmoid(b) in the model dtype as in HF, and
    decay = exp(-exp(A_log) * softplus(a + dt_bias)), all in fp32."""
    beta = mx.sigmoid(b)
    g = -mx.exp(A_log.astype(F32)) * nn.softplus(a.astype(F32) + dt_bias.astype(F32))
    return beta, mx.exp(g)


def gated_delta(
    q: mx.array,
    k: mx.array,
    v: mx.array,
    a: mx.array,
    b: mx.array,
    A_log: mx.array,
    dt_bias: mx.array,
    state: Optional[mx.array] = None,
    mask: Optional[mx.array] = None,
    *,
    use_kernel: bool = True,
) -> Tuple[mx.array, mx.array]:
    """The qwen4_exp gated delta rule (HF semantics) on mlx-lm's Metal kernel.

    Args:
      q, k: [B, T, Hk, Dk] conv outputs after silu (not yet normalized).
      v: [B, T, Hv, Dv].
      a, b: [B, T, Hv] raw ``in_proj_a`` / ``in_proj_b`` outputs.
      A_log, dt_bias: [Hv].
      state: [B, Hv, Dv, Dk] fp32 (mlx-lm layout; HF's is the transpose, see
        ``gdn_state_to_hf``), or None for zeros.
      mask: optional [B, T] bool. False steps leave the state unchanged and
        output 0. That equals HF for left padding from a zero state (see perf.md).

    Returns:
      y: [B, T, Hv, Dv] in ``v.dtype``; new state [B, Hv, Dv, Dk] fp32.
    """
    B, T, Hk, Dk = q.shape
    Hv, Dv = v.shape[-2:]
    if Hv % Hk:
        raise ValueError(f"Hv={Hv} must be a multiple of Hk={Hk}")
    qn, kn = gdn_qk_normalize(q, k)
    beta, decay = gdn_gates(a, b, A_log, dt_bias)
    if state is None:
        state = mx.zeros((B, Hv, Dv, Dk), dtype=F32)
    kernel_ok = (
        use_kernel
        and Dk % 32 == 0
        and Dv % 4 == 0
        and mx.default_device() == mx.gpu
        and mx.metal.is_available()
    )
    if kernel_ok:
        y, state = gated_delta_kernel(qn, kn, v, decay, beta, state, mask)
    else:
        y, state = gated_delta_ops(qn, kn, v, decay, beta, state, mask)
    return y.astype(v.dtype), state


def gdn_state_to_hf(state: mx.array) -> mx.array:
    """mlx-lm [B, Hv, Dv, Dk] -> transformers [B, Hv, Dk, Dv]."""
    return state.swapaxes(-1, -2)


def gdn_state_from_hf(state: mx.array) -> mx.array:
    """transformers [B, Hv, Dk, Dv] -> mlx-lm [B, Hv, Dv, Dk] (contiguous)."""
    return mx.contiguous(state.swapaxes(-1, -2).astype(F32))


def depthwise_causal_conv1d(
    x: mx.array, weight: mx.array, state: Optional[mx.array] = None
) -> Tuple[mx.array, mx.array]:
    """Causal depthwise conv without activation; HF ``causal_conv1d_fn`` / ``_update``.

    Args:
      x: [B, T, C]; weight: [C, K] (HF ``conv1d.weight.squeeze(1)``);
      state: [B, K-1, C] previous inputs, or None for zeros.
    Returns:
      out [B, T, C] in ``x.dtype``, new state [B, K-1, C].

    ``mx.conv1d(groups=C)`` accumulates in fp32 and rounds once. In bf16 it is
    bit-identical to the fp32 sum of K products cast to bf16 (tested). It is
    5-6x faster than K shifted multiply-adds (perf.md).
    """
    B, T, C = x.shape
    K = weight.shape[-1]
    if state is None:
        state = mx.zeros((B, K - 1, C), dtype=x.dtype)
    xs = mx.concatenate([state.astype(x.dtype), x], axis=1)
    out = mx.conv1d(xs, weight.astype(x.dtype)[:, :, None], groups=C)
    return out, xs[:, T:]


def rms_norm_gated(x: mx.array, gate: mx.array, weight: mx.array, eps: float) -> mx.array:
    """HF ``Qwen4ExpTextRMSNormGated`` with ``output_gate_type='sigmoid'`` (HF:168-185).

    out = (w * rms_norm(x).to(dtype)) * sigmoid(gate.float()), cast to x.dtype.
    """
    y = mx.fast.rms_norm(x, weight.astype(x.dtype), eps)
    return (y.astype(F32) * mx.sigmoid(gate.astype(F32))).astype(x.dtype)


# --------------------------------------------------------------------------
# 2. QSA indexer
# --------------------------------------------------------------------------
#
# HF:663-765. For a query at absolute position p (batch row without padding):
#   visible complete blocks j < nvis = (p + 1) // r   (r = compress_ratio = 4)
#   block key  kb_j = RoPE_{pos = r*j}( k_norm( mean_fp32(raw_k[r*j : r*j+r]).to(dtype) ) )
#   score      s_j  = sum_h relu(q_h . kb_j) / sqrt(D)  (fp32; q is q_norm+RoPE_p)
#   selected   = tokens of the top-min(K, nvis) blocks by s  (K = budget / r = 512)
#                + the tail tokens r*nvis .. p (always kept)
# Facts the fast paths use:
#   * kb_j depends only on raw_k[r*j : r*j+r] and r*j, so a completed block's
#     key is computed once and cached (exact; HF recomputes it per query).
#   * nvis <= K selects every visible token, so for kv length <= r*(K+1)-1
#     = 2051 the mask is plain causal and scoring is skipped (exact).
#   * Decode reads only the selected K*r + tail tokens of the KV cache
#     (gather, then dense SDPA), not the whole cache.
# Top-k ties are broken arbitrarily by both torch.topk and mx.argpartition;
# torch CPU does not pick the lowest index (perf.md, open issues).


@dataclass(frozen=True)
class QSAConfig:
    n_heads: int = 4  # indexer_n_heads
    head_dim: int = 128  # indexer_head_dim
    budget: int = 2048  # indexer_budget (tokens)
    compress_ratio: int = 4  # indexer_compress_ratio
    rope_dims: int = 64  # int(attention head_dim * partial_rotary_factor)
    rope_base: float = 10_000_000.0
    eps: float = 1e-6

    @property
    def block_topk(self) -> int:
        return self.budget // self.compress_ratio

    @property
    def dense_limit(self) -> int:
        """Largest visible kv length for which QSA selects every token."""
        return self.compress_ratio * (self.block_topk + 1) - 1

    @classmethod
    def from_text_config(cls, cfg: dict) -> "QSAConfig":
        rope = cfg.get("rope_parameters") or {}
        prf = rope.get("partial_rotary_factor", cfg.get("partial_rotary_factor", 0.25))
        return cls(
            n_heads=cfg["indexer_n_heads"],
            head_dim=cfg["indexer_head_dim"],
            budget=cfg["indexer_budget"],
            compress_ratio=cfg["indexer_compress_ratio"],
            rope_dims=int(cfg["head_dim"] * prf),
            rope_base=float(rope.get("rope_theta", cfg.get("rope_theta", 1e7))),
            eps=cfg.get("rms_norm_eps", 1e-6),
        )


def rms_norm_1p(x: mx.array, weight: mx.array, eps: float) -> mx.array:
    """HF ``Qwen4ExpTextRMSNorm`` (HF:141-161): fp32 normalize, multiply by
    (1 + w) in fp32, cast back. Computed fully in fp32, as HF does."""
    w = 1.0 + weight.astype(F32)
    return mx.fast.rms_norm(x.astype(F32), w, eps).astype(x.dtype)


def rope_offset(x: mx.array, offset: Any) -> Any:
    """Offset argument for ``mx.fast.rope`` that is safe for every batch size.

    mlx 0.31.2: with B > 1, T == 1 and a *scalar* offset, ``mx.fast.rope``
    applies the offset to batch row 0 only; the other rows get position 0
    (tests/align/test_qwen4_exp_kernels.py, ``test_mlx_rope_scalar_offset_bug``).
    A [B] int32 offset array is correct, so pass one whenever B > 1.
    """
    B = x.shape[0]
    if B > 1 and not (isinstance(offset, mx.array) and offset.size == B):
        off = offset if isinstance(offset, mx.array) else mx.array(offset, dtype=mx.int32)
        return mx.broadcast_to(off.astype(mx.int32).reshape(-1)[:1], (B,))
    return offset


def qsa_rope(x: mx.array, cfg: QSAConfig, offset: Any = 0, scale: float = 1.0) -> mx.array:
    """Partial non-interleaved RoPE on [B, *, T, D] at positions
    ``scale * (offset + i)``. For text inputs the interleaved-mRoPE sections
    collapse to plain RoPE (HF:129-138)."""
    return mx.fast.rope(
        x,
        cfg.rope_dims,
        traditional=False,
        base=cfg.rope_base,
        scale=scale,
        offset=rope_offset(x, offset),
    )


def qsa_split_qk(
    qk: mx.array, q_norm_weight: mx.array, cfg: QSAConfig, offset: Any = 0
) -> Tuple[mx.array, mx.array]:
    """Split ``index_qk_proj`` output [B, L, (H+1)*D] into q [B, L, H, D]
    (q_layernorm then RoPE at offset+i) and raw keys [B, L, D] (cached raw:
    no norm and no RoPE, HF:696-707)."""
    B, L, _ = qk.shape
    H, D = cfg.n_heads, cfg.head_dim
    q = qk[..., : H * D].reshape(B, L, H, D)
    raw_k = qk[..., H * D : (H + 1) * D]
    q = rms_norm_1p(q, q_norm_weight, cfg.eps)
    q = qsa_rope(q.transpose(0, 2, 1, 3), cfg, offset).transpose(0, 2, 1, 3)
    return q, raw_k


def qsa_block_keys(
    raw_keys: mx.array, k_norm_weight: mx.array, cfg: QSAConfig, block_offset: int = 0
) -> mx.array:
    """Block keys for complete blocks [B, n*r, D] -> [B, n, D].

    The keys start at block index ``block_offset``, so RoPE uses positions
    r*(block_offset+i). That is ``mx.fast.rope`` with scale=r, which is exact
    in fp32 for positions < 2**24.
    """
    B, N, D = raw_keys.shape
    r = cfg.compress_ratio
    n = N // r
    if n * r != N:
        raise ValueError(f"raw key count {N} is not a multiple of {r}")
    pooled = raw_keys.reshape(B, n, r, D).astype(F32).mean(axis=2).astype(raw_keys.dtype)
    normed = rms_norm_1p(pooled, k_norm_weight, cfg.eps)
    return qsa_rope(normed[:, None], cfg, block_offset, scale=float(r))[:, 0]


def qsa_scores(q: mx.array, block_keys: mx.array) -> mx.array:
    """[B, L, H, D] x [B, n, D] -> [B, L, n] fp32: sum_h relu(q_h . kb) / sqrt(D).

    One fp32 matmul [B, L*H, D] @ [B, D, n], then relu and a head sum. The
    division matches HF's ``/ math.sqrt(D)`` rounding.
    """
    B, L, H, D = q.shape
    s = q.astype(F32).reshape(B, L * H, D) @ block_keys.astype(F32).swapaxes(-1, -2)
    s = mx.maximum(s, 0.0).reshape(B, L, H, -1).sum(axis=2)
    return s / math.sqrt(D)


def qsa_select_blocks(
    scores: mx.array, q_positions: mx.array, cfg: QSAConfig
) -> mx.array:
    """Top-K block selection -> bool block mask [B, L, n].

    ``scores``: [B, L, n] over blocks 0..n-1; ``q_positions``: [L] absolute
    query positions (int32). Block j is visible to the query at p iff
    j < (p+1)//r. When every row has at most K visible blocks, all of them are
    selected and no top-k runs.
    """
    B, L, n = scores.shape
    K = cfg.block_topk
    nvis = (q_positions.astype(mx.int32) + 1) // cfg.compress_ratio
    valid = mx.arange(n, dtype=mx.int32)[None, :] < nvis[:, None]  # [L, n]
    valid = mx.broadcast_to(valid[None], (B, L, n))
    if n <= K:
        return valid
    masked = mx.where(valid, scores, -mx.inf)
    idx = mx.argpartition(-masked, kth=K - 1, axis=-1)[..., :K]
    keep = mx.take_along_axis(valid, idx, axis=-1)
    out = mx.zeros((B, L, n), dtype=mx.bool_)
    return mx.put_along_axis(out, idx, keep, axis=-1)


def qsa_token_mask(
    block_mask: mx.array, q_positions: mx.array, kv_len: int, cfg: QSAConfig
) -> mx.array:
    """Expand a block mask [B, L, n] to the token mask [B, 1, L, kv_len].

    The result includes the always-kept tail r*nvis..p. Causality is implied.
    """
    B, L, n = block_mask.shape
    r = cfg.compress_ratio
    tok = mx.repeat(block_mask, r, axis=-1)
    if n * r < kv_len:
        tok = mx.concatenate(
            [tok, mx.zeros((B, L, kv_len - n * r), dtype=mx.bool_)], axis=-1
        )
    elif n * r > kv_len:
        tok = tok[..., :kv_len]
    p = q_positions.astype(mx.int32)[:, None]
    t = mx.arange(kv_len, dtype=mx.int32)[None, :]
    tail = (t >= r * ((p + 1) // r)) & (t <= p)
    return (tok | tail[None])[:, None]


def qsa_prefill_mask(
    q: mx.array, block_keys: mx.array, offset: int, cfg: QSAConfig
) -> Optional[mx.array]:
    """Selection mask for a chunk of L queries at positions offset..offset+L-1.

    ``block_keys`` must hold every complete block of kv[0 : offset+L]. Returns
    None when the whole chunk is in the dense regime (use the causal mask), else
    the bool mask [B, 1, L, offset+L].
    """
    B, L = q.shape[:2]
    kv_len = offset + L
    if kv_len <= cfg.dense_limit:
        return None
    pos = mx.arange(offset, kv_len, dtype=mx.int32)
    scores = qsa_scores(q, block_keys)
    block_mask = qsa_select_blocks(scores, pos, cfg)
    return qsa_token_mask(block_mask, pos, kv_len, cfg)


def qsa_decode_token_indices(
    q: mx.array, block_keys: mx.array, position: int, cfg: QSAConfig
) -> Optional[mx.array]:
    """Selected kv token indices [B, K*r + tail] for one decode query at
    ``position`` (the current token, already in the cache), or None if dense.

    Incremental scoring touches only the cached block keys. The order of
    indices is irrelevant to attention.
    """
    r, K = cfg.compress_ratio, cfg.block_topk
    nvis = (position + 1) // r
    if nvis <= K:
        return None
    s = qsa_scores(q, block_keys[:, :nvis])[:, 0]  # [B, nvis]
    blk = mx.argpartition(-s, kth=K - 1, axis=-1)[:, :K]  # [B, K]
    tok = (blk[..., None] * r + mx.arange(r, dtype=blk.dtype)).reshape(blk.shape[0], -1)
    tail = position + 1 - r * nvis
    if tail:
        t = mx.arange(r * nvis, position + 1, dtype=tok.dtype)
        tok = mx.concatenate([tok, mx.broadcast_to(t, (tok.shape[0], tail))], axis=-1)
    return tok


def qsa_sparse_decode_attention(
    queries: mx.array,
    keys: mx.array,
    values: mx.array,
    token_idx: Optional[mx.array],
    scale: float,
    kv_len: Optional[int] = None,
) -> mx.array:
    """Decode attention over the QSA-selected tokens only.

    queries: [B, Hq, 1, Dh]; keys/values: [B, Hkv, >=kv_len, Dh] (the cache
    buffer may be longer than kv_len). ``token_idx`` [B, S] comes from
    ``qsa_decode_token_indices``. None means dense over kv[:kv_len].
    """
    if token_idx is None:
        if kv_len is not None:
            keys, values = keys[..., :kv_len, :], values[..., :kv_len, :]
        return mx.fast.scaled_dot_product_attention(queries, keys, values, scale=scale)
    if token_idx.shape[0] == 1:
        ks = mx.take(keys, token_idx[0], axis=2)
        vs = mx.take(values, token_idx[0], axis=2)
    else:
        idx = token_idx[:, None, :, None]
        ks = mx.take_along_axis(keys, idx, axis=2)
        vs = mx.take_along_axis(values, idx, axis=2)
    return mx.fast.scaled_dot_product_attention(queries, ks, vs, scale=scale)


def sdpa_query_chunked(
    queries: mx.array,
    keys: mx.array,
    values: mx.array,
    scale: float,
    mask: Optional[mx.array],
    max_score_bytes: int = 256 * 2**20,
) -> mx.array:
    """``mx.fast.scaled_dot_product_attention``, split over query rows.

    With head_dim 256, MLX 0.31.2 has no fused prefill kernel and materializes
    [B, Hq, L, T] scores (perf.md). Splitting the rows bounds that
    transient; FLOPs are unchanged. ``mask`` may be None, "causal" (the
    queries are the last L of the T keys), or an array broadcastable to
    [B, 1, L, T].
    """
    B, Hq, L, D = queries.shape
    T = keys.shape[-2]
    per_row = B * Hq * T * 4
    rows = max(16, min(L, max_score_bytes // max(per_row, 1)))
    if rows >= L:
        return mx.fast.scaled_dot_product_attention(queries, keys, values, scale=scale, mask=mask)
    if isinstance(mask, str):
        if mask != "causal":
            raise ValueError(mask)
        pos = mx.arange(T - L, T)
        mask = (mx.arange(T)[None, :] <= pos[:, None])[None, None]
    outs = []
    for s in range(0, L, rows):
        m = None if mask is None else mask[..., s : s + rows, :]
        outs.append(
            mx.fast.scaled_dot_product_attention(
                queries[:, :, s : s + rows], keys, values, scale=scale, mask=m
            )
        )
    return mx.concatenate(outs, axis=2)


def qsa_select_token_indices(
    scores: mx.array, q_positions: mx.array, cfg: QSAConfig
) -> mx.array:
    """Top-K block selection as per-query token lists [B, L, K*r + r - 1] int32.

    Lists hold the tokens of the selected blocks, then the tail r*nvis..p.
    Unused slots are -1. This is the input of ``qsa_sparse_attention``, and it
    selects the same set as ``qsa_select_blocks`` + ``qsa_token_mask`` (same
    argpartition on the same scores) without a [L, T] mask.
    """
    B, L, n = scores.shape
    r, K = cfg.compress_ratio, cfg.block_topk
    pos = q_positions.astype(mx.int32)
    nvis = (pos + 1) // r
    valid = mx.broadcast_to((mx.arange(n, dtype=mx.int32)[None, :] < nvis[:, None])[None], (B, L, n))
    if n <= K:
        blk = mx.broadcast_to(mx.arange(n, dtype=mx.int32), (B, L, n))
        keep = valid
    else:
        masked = mx.where(valid, scores, -mx.inf)
        blk = mx.argpartition(-masked, kth=K - 1, axis=-1)[..., :K].astype(mx.int32)
        keep = mx.take_along_axis(valid, blk, axis=-1)
    tok = blk[..., None] * r + mx.arange(r, dtype=mx.int32)
    tok = mx.where(keep[..., None], tok, -1).reshape(B, L, -1)
    tail = r * nvis[:, None] + mx.arange(r - 1, dtype=mx.int32)[None, :]
    tail = mx.where(tail <= pos[:, None], tail, -1)
    return mx.concatenate([tok, mx.broadcast_to(tail[None], (B, L, r - 1))], axis=-1)


# Block-sparse QSA attention (new Metal kernel). One threadgroup per (query l,
# kv head g, batch b). Its NSG simdgroups each own HPS of the Hq/Hkv query
# heads that share kv head g, so the K/V rows of one selected token are reused
# from L1 by every head. Scores are lane-per-token: lane j computes q_h . k_t for
# token t = idx[j0 + j], with q in threadgroup memory, so there is no per-token
# simd_sum. Then an online softmax per 32-token tile (simd_max / simd_sum), and
# P.V lane-per-dims (E = D/32 dims per lane, p broadcast by simd_shuffle).
# Cost is O(L * S * D), independent of the context length T; dense-masked
# SDPA is O(L * T * D). Measured crossover on the M4 is about 6K tokens
# (perf.md). Unused idx slots are -1. Every row has at least one valid token
# (the tail always holds token p).
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
    const device int* ip = idx + ((size_t)(b * L + l) * S);
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


def qsa_sparse_attention(
    queries: mx.array,
    keys: mx.array,
    values: mx.array,
    token_idx: mx.array,
    scale: float,
    heads_per_simdgroup: Optional[int] = None,
) -> mx.array:
    """Attention of each query over its own selected tokens (Metal kernel).

    queries [B, Hq, L, D]; keys/values [B, Hkv, Tcap, D], which may be a
    whole preallocated cache buffer: only indexed rows are read, and a
    contiguous buffer avoids the copy ``metal_kernel`` makes of a strided
    slice. token_idx [B, L, S] int32, -1 = unused. Returns [B, Hq, L, D] in
    ``queries.dtype``; softmax and accumulation are fp32.
    """
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
    if D % 32 or Hq % Hkv or (Hq // Hkv) * D > 8192:
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


# Below this kv length dense-masked SDPA beats the sparse kernel for a prefill
# chunk (M4 measurement, perf.md). Re-measure on the target machine.
QSA_SPARSE_PREFILL_MIN_KV = 6144


def qsa_prefill_attention(
    queries: mx.array,
    keys: mx.array,
    values: mx.array,
    kv_len: int,
    index_q: mx.array,
    block_keys: mx.array,
    offset: int,
    cfg: QSAConfig,
    scale: float,
    sparse_min_kv: int = QSA_SPARSE_PREFILL_MIN_KV,
) -> mx.array:
    """QSA attention for a prefill chunk of L queries at positions offset.. .

    keys/values may be whole cache buffers; kv[:kv_len] is valid and
    kv_len == offset + L. The path depends on the regime: dense causal while
    every query sees <= K blocks; dense SDPA under the selection mask below
    ``sparse_min_kv``; the sparse kernel above it. All three compute the same
    function.
    """
    L = queries.shape[2]
    if kv_len != offset + L:
        raise ValueError("kv_len must equal offset + L")
    if kv_len <= cfg.dense_limit:
        return sdpa_query_chunked(queries, keys[..., :kv_len, :], values[..., :kv_len, :], scale, "causal")
    pos = mx.arange(offset, kv_len, dtype=mx.int32)
    scores = qsa_scores(index_q, block_keys)
    if kv_len < sparse_min_kv:
        mask = qsa_token_mask(qsa_select_blocks(scores, pos, cfg), pos, kv_len, cfg)
        return sdpa_query_chunked(queries, keys[..., :kv_len, :], values[..., :kv_len, :], scale, mask)
    idx = qsa_select_token_indices(scores, pos, cfg)
    return qsa_sparse_attention(queries, keys, values, idx, scale)


# Decode: below this kv length, dense SDPA under the [1, T] selection mask
# beats gathering the selected rows (M4 measurement, perf.md). On the higher
# bandwidth M3 Max the crossover is expected to move up. Re-measure there.
QSA_SPARSE_DECODE_MIN_KV = 8192


def qsa_decode_attention(
    queries: mx.array,
    keys: mx.array,
    values: mx.array,
    kv_len: int,
    index_q: mx.array,
    block_keys: mx.array,
    cfg: QSAConfig,
    scale: float,
    sparse_min_kv: int = QSA_SPARSE_DECODE_MIN_KV,
) -> mx.array:
    """QSA attention for one decode query at position kv_len - 1.

    Takes the dense causal path while kv_len <= dense_limit (all selected), a
    dense SDPA under the selection mask below ``sparse_min_kv``, and the gather
    of the selected rows above it. All three compute the same function.
    """
    p = kv_len - 1
    k, v = keys[..., :kv_len, :], values[..., :kv_len, :]
    if kv_len <= cfg.dense_limit:
        return mx.fast.scaled_dot_product_attention(queries, k, v, scale=scale)
    if kv_len < sparse_min_kv:
        mask = qsa_prefill_mask(index_q, block_keys, p, cfg)
        return mx.fast.scaled_dot_product_attention(queries, k, v, scale=scale, mask=mask)
    idx = qsa_decode_token_indices(index_q, block_keys, p, cfg)
    return qsa_sparse_decode_attention(queries, keys, values, idx, scale)


class QSAIndexerCache:
    """Per-layer indexer state: all raw keys plus derived block keys.

    The raw keys [B, T, D] are what HF caches (``update_indexer``). They are
    needed for the open tail block and for ``trim``. Block keys [B, T//r, D]
    are computed once per completed block. Both buffers grow in ``step`` tokens
    like mlx-lm's KVCache. Batch rows must share one offset (no left padding):
    see perf.md, open issues.
    """

    step = 1024

    def __init__(self, cfg: QSAConfig):
        self.cfg = cfg
        self.raw: Optional[mx.array] = None
        self.blocks: Optional[mx.array] = None
        self.offset = 0
        self.n_blocks = 0

    def _grow(self, buf: Optional[mx.array], need: int, shape_tail, dtype, B: int):
        if buf is not None and buf.shape[1] >= need:
            return buf
        cap = ((need + self.step - 1) // self.step) * self.step
        new = mx.zeros((B, cap, *shape_tail), dtype=dtype)
        if buf is not None:
            new[:, : buf.shape[1]] = buf
        return new

    def update(self, raw_k: mx.array, k_norm_weight: mx.array) -> mx.array:
        """Append raw keys [B, L, D]; return block keys [B, n_blocks, D]."""
        B, L, D = raw_k.shape
        r = self.cfg.compress_ratio
        prev, end = self.offset, self.offset + L
        self.raw = self._grow(self.raw, end, (D,), raw_k.dtype, B)
        self.raw[:, prev:end] = raw_k
        nb = end // r
        if nb > self.n_blocks:
            self.blocks = self._grow(self.blocks, max(nb, 1), (D,), raw_k.dtype, B)
            new = qsa_block_keys(
                self.raw[:, self.n_blocks * r : nb * r], k_norm_weight, self.cfg, self.n_blocks
            )
            self.blocks[:, self.n_blocks : nb] = new
        self.offset, self.n_blocks = end, nb
        if self.blocks is None:
            return mx.zeros((B, 0, D), dtype=raw_k.dtype)
        return self.blocks[:, :nb]

    def trim(self, n: int) -> int:
        n = min(self.offset, n)
        self.offset -= n
        # A partially trimmed block becomes the open tail again. Its raw keys
        # are still in self.raw, and its key is recomputed once it completes.
        self.n_blocks = self.offset // self.cfg.compress_ratio
        return n

    @property
    def state(self) -> List[mx.array]:
        """Live arrays: raw keys [B, offset, D] and block keys [B, n_blocks, D]."""
        out = [] if self.raw is None else [self.raw[:, : self.offset]]
        if self.blocks is not None:
            out.append(self.blocks[:, : self.n_blocks])
        return out

    @property
    def nbytes(self) -> int:
        return sum(a.nbytes for a in (self.raw, self.blocks) if a is not None)


# --------------------------------------------------------------------------
# 3. MoE
# --------------------------------------------------------------------------
#
# HF:907-987. Router: logits = x W^T (model dtype); probs = softmax(fp32);
# top-k on fp32 probs; renormalize (norm_topk_prob=True); cast to the logits
# dtype. Note: mlx-lm's Qwen3NextSparseMoeBlock calls
# mx.softmax(bf16, precise=True), which returns *bf16* probabilities, and ranks
# those. Among 512 experts, bf16 rounding creates ties and reorders near-equal
# experts, so routing differs from HF. ``moe_router`` ranks fp32 probs.
# Experts: HF stores gate_up_proj [E, 2I, H] fused (gate rows first) and
# down_proj [E, H, I]. ``FusedSwitchGLU`` keeps the fusion: two gather_qmm
# calls per token instead of three.


def moe_router(
    logits: mx.array, top_k: int, norm_topk_prob: bool = True
) -> Tuple[mx.array, mx.array]:
    """logits [..., E] (model dtype) -> (indices [..., k] uint32, weights [..., k] in logits dtype)."""
    probs = mx.softmax(logits.astype(F32), axis=-1)
    inds = mx.argpartition(-probs, kth=top_k - 1, axis=-1)[..., :top_k]
    w = mx.take_along_axis(probs, inds, axis=-1)
    if norm_topk_prob:
        w = w / w.sum(axis=-1, keepdims=True)
    return inds.astype(mx.uint32), w.astype(logits.dtype)


def _gather_sort(x, indices):
    *_, M = indices.shape
    indices = indices.flatten()
    order = mx.argsort(indices)
    inv_order = mx.argsort(order)
    return x.flatten(0, -3)[order // M], indices[order], inv_order


class FusedSwitchGLU(nn.Module):
    """SwitchGLU with HF's fused gate_up [E, 2I, H]: one gather for gate+up.

    Weights are plain arrays or quantized triples. Use ``from_weights`` /
    ``quantize``. Each projection may carry its own bits (mixed 3/4-bit is
    fine: per call, not per expert). ``__call__(x [..., H], idx [..., k])``
    returns [..., k, H].
    """

    def __init__(self, gate_up: mx.array, down: mx.array):
        super().__init__()
        self.gate_up = gate_up  # [E, 2I, H]
        self.down = down  # [E, H, I]
        self.gu_q: Optional[Tuple[int, int]] = None
        self.dn_q: Optional[Tuple[int, int]] = None

    def quantize(self, gu_bits=4, down_bits=4, group_size=64) -> "FusedSwitchGLU":
        w, s, b = mx.quantize(self.gate_up, group_size=group_size, bits=gu_bits)
        self.gate_up = {"weight": w, "scales": s, "biases": b}
        self.gu_q = (group_size, gu_bits)
        w, s, b = mx.quantize(self.down, group_size=group_size, bits=down_bits)
        self.down = {"weight": w, "scales": s, "biases": b}
        self.dn_q = (group_size, down_bits)
        return self

    def _proj(self, x, w, q, idx, sorted_indices):
        if q is None:
            return mx.gather_mm(x, w.swapaxes(-1, -2), rhs_indices=idx, sorted_indices=sorted_indices)
        gs, bits = q
        return mx.gather_qmm(
            x, w["weight"], w["scales"], w["biases"], rhs_indices=idx, transpose=True,
            group_size=gs, bits=bits, sorted_indices=sorted_indices,
        )

    def __call__(self, x: mx.array, indices: mx.array) -> mx.array:
        x = mx.expand_dims(x, (-2, -3))
        do_sort = indices.size >= 64
        idx, inv = indices, None
        if do_sort:
            x, idx, inv = _gather_sort(x, indices)
        h = self._proj(x, self.gate_up, self.gu_q, idx, do_sort)
        I = h.shape[-1] // 2
        h = swiglu_hf(h[..., :I], h[..., I:])
        y = self._proj(h, self.down, self.dn_q, idx, do_sort)
        if do_sort:
            y = y[inv]
            y = mx.unflatten(y, 0, indices.shape)
        return y.squeeze(-2)


@partial(mx.compile, shapeless=True)
def swiglu_hf(gate: mx.array, up: mx.array) -> mx.array:
    """HF ``act_fn(gate) * up`` (silu)."""
    return nn.silu(gate) * up


def fold_shared_expert(
    gate_up: mx.array, down: mx.array, shared_gate_up: mx.array, shared_down: mx.array
) -> Tuple[mx.array, mx.array]:
    """Append the shared expert as expert E: [E+1, 2I, H], [E+1, H, I].

    Valid when the shared expert's intermediate size equals the routed one
    (640 = 640 here) and both share one quantization recipe. Then
    ``moe_block_folded`` runs 10+1 experts in one pair of gather_qmm calls.
    """
    return (
        mx.concatenate([gate_up, shared_gate_up[None]], axis=0),
        mx.concatenate([down, shared_down[None]], axis=0),
    )


def moe_block_folded(
    x: mx.array,
    router_w: mx.array,
    experts: FusedSwitchGLU,
    top_k: int,
    num_experts: int,
    norm_topk_prob: bool = True,
) -> mx.array:
    """Routed + shared MoE, with the shared expert folded in as expert E.

    ``router_w`` is [E+1, H]: router rows, then the ``shared_expert_gate``
    row (a single fused router matmul). x: [..., H] -> [..., H].
    """
    logits = x @ router_w.T
    inds, w = moe_router(logits[..., :num_experts], top_k, norm_topk_prob)
    sg = mx.sigmoid(logits[..., num_experts:]).astype(w.dtype)
    shared_idx = mx.full((*inds.shape[:-1], 1), num_experts, dtype=inds.dtype)
    inds = mx.concatenate([inds, shared_idx], axis=-1)
    w = mx.concatenate([w, sg], axis=-1)
    y = experts(x, inds)
    return (y * w[..., None]).sum(axis=-2)


def moe_block_split(
    x: mx.array,
    router_w: mx.array,
    experts: FusedSwitchGLU,
    shared: "DenseGLU",
    shared_gate_w: mx.array,
    top_k: int,
    norm_topk_prob: bool = True,
) -> mx.array:
    """Routed experts plus a separate shared-expert MLP (HF structure)."""
    inds, w = moe_router(x @ router_w.T, top_k, norm_topk_prob)
    y = (experts(x, inds) * w[..., None]).sum(axis=-2)
    return y + mx.sigmoid(x @ shared_gate_w.T) * shared(x)


class DenseGLU(nn.Module):
    """Dense SwiGLU with fused gate_up [2I, H] (the shared expert)."""

    def __init__(self, gate_up: mx.array, down: mx.array):
        super().__init__()
        self.gate_up = nn.Linear(gate_up.shape[1], gate_up.shape[0], bias=False)
        self.gate_up.weight = gate_up
        self.down = nn.Linear(down.shape[1], down.shape[0], bias=False)
        self.down.weight = down

    def __call__(self, x):
        h = self.gate_up(x)
        I = h.shape[-1] // 2
        return self.down(swiglu_hf(h[..., :I], h[..., I:]))


# --------------------------------------------------------------------------
# 4. References (slow, literal; used by tests)
# --------------------------------------------------------------------------


def gated_delta_reference(
    q, k, v, a, b, A_log, dt_bias, state_hf: Optional[mx.array] = None
) -> Tuple[mx.array, mx.array]:
    """Literal MLX transcription of HF ``torch_recurrent_gated_delta_rule``,
    including the GatedDeltaNet gate math. State in HF layout [B, Hv, Dk, Dv]."""
    out_dtype = v.dtype
    B, T, Hk, Dk = q.shape
    Hv, Dv = v.shape[-2:]
    beta = mx.sigmoid(b).astype(F32)
    g = -mx.exp(A_log.astype(F32)) * nn.softplus(a.astype(F32) + dt_bias.astype(F32))
    r = Hv // Hk
    q = mx.repeat(q, r, axis=2)
    k = mx.repeat(k, r, axis=2)
    q, k, v = (x.astype(F32).transpose(0, 2, 1, 3) for x in (q, k, v))
    q = q * mx.rsqrt((q * q).sum(axis=-1, keepdims=True) + 1e-6)
    k = k * mx.rsqrt((k * k).sum(axis=-1, keepdims=True) + 1e-6)
    q = q / (Dk**0.5)
    S = mx.zeros((B, Hv, Dk, Dv), dtype=F32) if state_hf is None else state_hf.astype(F32)
    outs = []
    for t in range(T):
        S = S * mx.exp(g[:, t])[..., None, None]
        kt = k[:, :, t]
        kv_mem = (S * kt[..., None]).sum(axis=-2)
        delta = (v[:, :, t] - kv_mem) * beta[:, t][..., None]
        S = S + kt[..., None] * delta[..., None, :]
        outs.append((S * q[:, :, t][..., None]).sum(axis=-2))
    y = mx.stack(outs, axis=2).transpose(0, 2, 1, 3)
    return y.astype(out_dtype), S


def gated_delta_native_mlx_lm(q, k, v, a, b, A_log, dt_bias, state=None):
    """What qwen3_next.py / qwen3_5.py do (for the eps-difference test)."""
    from mlx_lm.models.gated_delta import gated_delta_update

    inv_scale = k.shape[-1] ** -0.5
    qn = (inv_scale**2) * mx.fast.rms_norm(q, None, 1e-6)
    kn = inv_scale * mx.fast.rms_norm(k, None, 1e-6)
    return gated_delta_update(qn, kn, v, a, b, A_log, dt_bias, state)


def qsa_reference_mask(
    q: mx.array,
    raw_keys: mx.array,
    k_norm_weight: mx.array,
    cfg: QSAConfig,
    offset: int = 0,
    return_scores: bool = False,
):
    """Per-query loop transcription of HF ``Qwen4ExpTextQSAIndexer.forward``
    (HF:719-765) for unpadded rows. q: [B, L, H, D] post-norm/RoPE at
    offset..offset+L-1; raw_keys: [B, offset+L, D]. Returns the bool mask
    [B, 1, L, offset+L], plus the per-query block scores if requested."""
    B, L, H, D = q.shape
    T = raw_keys.shape[1]
    r, K = cfg.compress_ratio, cfg.block_topk
    rows, all_scores = [], []
    for bi in range(B):
        brows, bscores = [], []
        for qi in range(L):
            p = offset + qi
            nvis = (p + 1) // r
            sel = mx.zeros((T,), dtype=mx.bool_)
            sc = None
            if nvis > 0:
                grp = raw_keys[bi, : nvis * r].reshape(nvis, r, D)
                pooled = grp.astype(F32).mean(axis=1).astype(raw_keys.dtype)
                normed = rms_norm_1p(pooled, k_norm_weight, cfg.eps)
                pos = mx.arange(nvis, dtype=F32) * r
                inv = 1.0 / (cfg.rope_base ** (mx.arange(0, cfg.rope_dims, 2, dtype=F32) / cfg.rope_dims))
                fr = pos[:, None] * inv[None]
                emb = mx.concatenate([fr, fr], axis=-1)
                cos, sin = mx.cos(emb), mx.sin(emb)
                xr, xp = normed[:, : cfg.rope_dims].astype(F32), normed[:, cfg.rope_dims :]
                half = cfg.rope_dims // 2
                rot = mx.concatenate([-xr[:, half:], xr[:, :half]], axis=-1)
                kb = mx.concatenate([(xr * cos + rot * sin).astype(normed.dtype), xp], axis=-1)
                sc = mx.maximum(q[bi, qi].astype(F32) @ kb.astype(F32).T, 0.0).sum(axis=0) / math.sqrt(D)
                kk = min(K, nvis)
                blk = mx.argsort(-sc)[:kk]
                tok = (blk[:, None] * r + mx.arange(r)).flatten()
                sel = (mx.arange(T)[:, None] == tok[None, :]).any(axis=1)
            tail = mx.arange(T)
            sel = sel | ((tail >= nvis * r) & (tail <= p))
            brows.append(sel)
            bscores.append(sc)
        rows.append(mx.stack(brows))
        all_scores.append(bscores)
    mask = mx.stack(rows)[:, None]
    return (mask, all_scores) if return_scores else mask


def moe_reference(
    x: mx.array,
    router_w: mx.array,
    gate_up: mx.array,
    down: mx.array,
    shared_gate_up: mx.array,
    shared_down: mx.array,
    shared_gate_w: mx.array,
    top_k: int,
    norm_topk_prob: bool = True,
) -> mx.array:
    """Dense per-token loop of HF ``Qwen4ExpTextSparseMoeBlock`` (fp32 math)."""
    xs = x.reshape(-1, x.shape[-1]).astype(F32)
    logits = xs @ router_w.astype(F32).T
    probs = mx.softmax(logits, axis=-1)
    order = mx.argsort(-probs, axis=-1)[:, :top_k]
    I = down.shape[-1]
    outs = []
    for t in range(xs.shape[0]):
        w = probs[t][order[t]]
        if norm_topk_prob:
            w = w / w.sum()
        acc = mx.zeros((xs.shape[1],), dtype=F32)
        for j in range(top_k):
            e = order[t, j].item()
            h = gate_up[e].astype(F32) @ xs[t]
            h = nn.silu(h[:I]) * h[I:]
            acc = acc + w[j] * (down[e].astype(F32) @ h)
        h = shared_gate_up.astype(F32) @ xs[t]
        h = nn.silu(h[:I]) * h[I:]
        sh = shared_down.astype(F32) @ h
        acc = acc + mx.sigmoid(shared_gate_w.astype(F32) @ xs[t]) * sh
        outs.append(acc)
    return mx.stack(outs).reshape(x.shape)
