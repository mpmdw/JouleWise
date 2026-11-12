"""Patch draft for finding P2 (mlx-vlm 0.7.12): match the reference's fp32
gating and q/k normalization in the Qwen4 Gated DeltaNet.

Reference (transformers modeling_qwen4_exp.py): g = -exp(A_log.float()) *
softplus(a.float() + dt_bias); q, k, v cast to fp32 BEFORE the L2 norm and the
1/sqrt(Dk) query scale; the kernel output is cast back to the input dtype.
mlx-vlm computes softplus(a + dt_bias) and the L2 norm in the activation
dtype (bf16), then feeds bf16 q/k to the fp32-accumulating kernel.

apply() monkeypatches for testing (T3); see p2_fp32_gating.patch for the
source change.
"""
from functools import partial

import mlx.core as mx
import mlx.nn as nn


def apply():
    from mlx_vlm.models.qwen3_5 import gated_delta as gd
    from mlx_vlm.models.qwen3_5 import language as q35
    from mlx_vlm.models.qwen4_exp import language as L4

    @partial(mx.compile, shapeless=True)
    def compute_g_beta(A_log, a, b, dt_bias):
        g = mx.exp(-mx.exp(A_log.astype(mx.float32))
                   * nn.softplus(a.astype(mx.float32) + dt_bias.astype(mx.float32)))
        return g, mx.sigmoid(b)

    gd._compute_g_beta = compute_g_beta

    def normalize_qk(self, q, k):
        q, k = q.astype(mx.float32), k.astype(mx.float32)
        q = q * mx.rsqrt(mx.sum(mx.square(q), axis=-1, keepdims=True) + 1e-6)
        k = k * mx.rsqrt(mx.sum(mx.square(k), axis=-1, keepdims=True) + 1e-6)
        return q * q.shape[-1] ** -0.5, k

    L4.Qwen4ExpGatedDeltaNet._normalize_qk = normalize_qk
    original = q35.gated_delta_update

    def update(q, k, v, *args, **kwargs):
        dtype = v.dtype
        out, state = original(q, k, v.astype(q.dtype), *args, **kwargs)
        return out.astype(dtype), state

    q35.gated_delta_update = update
