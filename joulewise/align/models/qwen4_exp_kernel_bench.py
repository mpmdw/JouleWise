"""Per-layer microbenchmarks for the qwen4_exp kernels at real dimensions.

Benchmarks run one layer at a time, with random weights at the real shapes
from .engine/hf-flashnext/config.json. Weight values do not affect speed.
Results feed docs/align/qwen4_exp_port/perf.md.

    nice -n 10 /private/tmp/jwsol/venv-mlx/bin/python -m \
        joulewise.align.models.qwen4_exp_kernel_bench --suite all --json out.json

Timing: ``mx.eval`` wall time, median of ``--iters``. Decode steps are chained
R times in one graph (the output of rep i feeds rep i+1, as consecutive layers
do), and the time per rep is reported, which amortizes the per-eval
synchronization a real forward pays once per token. Prefill is one 512-token
chunk per eval. Memory is capped with ``mx.set_memory_limit`` (``--mem-gb``).
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

import mlx.core as mx
import mlx.nn as nn

from joulewise.align.models import qwen4_exp_kernels as K

ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / ".engine" / "hf-flashnext" / "config.json"

BF16 = mx.bfloat16


def real_text_config() -> dict:
    return json.loads(CONFIG.read_text())["text_config"]


# --------------------------------------------------------------------------
# timing helpers
# --------------------------------------------------------------------------


def timeit(fn: Callable[[], object], iters: int = 10, warmup: int = 2) -> Dict[str, float]:
    for _ in range(warmup):
        mx.eval(fn())
    ts = []
    for _ in range(iters):
        t0 = time.perf_counter()
        mx.eval(fn())
        ts.append(time.perf_counter() - t0)
    ts.sort()
    return {
        "median_ms": 1e3 * statistics.median(ts),
        "p10_ms": 1e3 * ts[max(0, len(ts) // 10)],
        "p90_ms": 1e3 * ts[min(len(ts) - 1, (9 * len(ts)) // 10)],
    }


def per_rep(stats: Dict[str, float], reps: int) -> Dict[str, float]:
    return {k: v / reps for k, v in stats.items()}


def free():
    gc.collect()
    mx.clear_cache()


# --------------------------------------------------------------------------
# weights
# --------------------------------------------------------------------------


def rand_packed(shape) -> mx.array:
    """Random packed quantized words (uint32), without a bf16 intermediate."""
    return mx.random.randint(0, 2**31 - 1, shape, dtype=mx.int32).view(mx.uint32)


class Lin:
    """A [out, in] linear in bf16 or affine-quantized (group 64)."""

    def __init__(self, out_dim: int, in_dim: int, bits: Optional[int], scale: float = None):
        scale = scale if scale is not None else in_dim**-0.5
        self.bits = bits
        if bits is None:
            self.w = (mx.random.normal((out_dim, in_dim)) * scale).astype(BF16)
        else:
            # Random packed weights directly: avoids a transient bf16 copy.
            self.w = rand_packed((out_dim, in_dim * bits // 32))
            self.s = (mx.random.uniform(shape=(out_dim, in_dim // 64)) * scale * 0.1).astype(BF16)
            self.b = (-self.s * (2**bits - 1) / 2).astype(BF16)
        mx.eval(*self.arrays())

    def arrays(self):
        return [self.w] if self.bits is None else [self.w, self.s, self.b]

    @property
    def nbytes(self) -> int:
        return sum(a.nbytes for a in self.arrays())

    def __call__(self, x):
        if self.bits is None:
            return x @ self.w.T
        return mx.quantized_matmul(x, self.w, self.s, self.b, transpose=True, group_size=64, bits=self.bits)


def quantized_experts(E: int, out_dim: int, in_dim: int, bits: int) -> dict:
    w = rand_packed((E, out_dim, in_dim * bits // 32))
    s = (mx.random.uniform(shape=(E, out_dim, in_dim // 64)) * 1e-3).astype(BF16)
    b = (-s * (2**bits - 1) / 2).astype(BF16)
    mx.eval(w, s, b)
    return {"weight": w, "scales": s, "biases": b}


# --------------------------------------------------------------------------
# layer compositions (the wiring the canonical module would use)
# --------------------------------------------------------------------------


class GDNLayer:
    """Gated DeltaNet layer: one fused in-projection [qkv | z | b | a]."""

    def __init__(self, cfg: dict, bits: Optional[int]):
        self.H = cfg["hidden_size"]
        self.Hk, self.Hv = cfg["linear_num_key_heads"], cfg["linear_num_value_heads"]
        self.Dk, self.Dv = cfg["linear_key_head_dim"], cfg["linear_value_head_dim"]
        self.key_dim, self.value_dim = self.Hk * self.Dk, self.Hv * self.Dv
        self.conv_dim = 2 * self.key_dim + self.value_dim
        n_in = self.conv_dim + self.value_dim + 2 * self.Hv
        self.in_proj = Lin(n_in, self.H, bits)
        self.out_proj = Lin(self.H, self.value_dim, bits)
        self.conv_w = (mx.random.normal((self.conv_dim, cfg["linear_conv_kernel_dim"])) * 0.5).astype(BF16)
        self.A_log = mx.log(mx.random.uniform(1, 16, (self.Hv,))).astype(BF16)
        self.dt_bias = mx.ones((self.Hv,), dtype=BF16)
        self.norm_w = mx.ones((self.Dv,), dtype=BF16)
        self.eps = cfg["rms_norm_eps"]

    @property
    def weight_bytes(self) -> int:
        return self.in_proj.nbytes + self.out_proj.nbytes + self.conv_w.nbytes

    def __call__(self, x, conv_state=None, state=None, native_kernel_inputs=False):
        B, T, _ = x.shape
        p = self.in_proj(x)
        c, z_end = self.conv_dim, self.conv_dim + self.value_dim
        qkv, z, b, a = p[..., :c], p[..., c:z_end], p[..., z_end : z_end + self.Hv], p[..., z_end + self.Hv :]
        conv, conv_state = K.depthwise_causal_conv1d(qkv, self.conv_w, conv_state)
        conv = nn.silu(conv)
        q = conv[..., : self.key_dim].reshape(B, T, self.Hk, self.Dk)
        k = conv[..., self.key_dim : 2 * self.key_dim].reshape(B, T, self.Hk, self.Dk)
        v = conv[..., 2 * self.key_dim :].reshape(B, T, self.Hv, self.Dv)
        if native_kernel_inputs:
            y, state = K.gated_delta_native_mlx_lm(q, k, v, a, b, self.A_log, self.dt_bias, state)
        else:
            y, state = K.gated_delta(q, k, v, a, b, self.A_log, self.dt_bias, state)
        o = K.rms_norm_gated(y, z.reshape(B, T, self.Hv, self.Dv), self.norm_w, self.eps)
        return self.out_proj(o.reshape(B, T, -1)), conv_state, state


class QSALayer:
    """QSA attention layer: indexer, gated q, GQA attention, o_proj."""

    def __init__(self, cfg: dict, bits: Optional[int]):
        self.qcfg = K.QSAConfig.from_text_config(cfg)
        self.H = cfg["hidden_size"]
        self.Hq, self.Hkv, self.Dh = cfg["num_attention_heads"], cfg["num_key_value_heads"], cfg["head_dim"]
        q = self.qcfg
        self.index_qk = Lin((q.n_heads + 1) * q.head_dim, self.H, bits)
        self.qkv = Lin(self.Hq * self.Dh * 2 + 2 * self.Hkv * self.Dh, self.H, bits)
        self.o_proj = Lin(self.H, self.Hq * self.Dh, bits)
        self.iq_norm = mx.zeros((q.head_dim,), dtype=BF16)
        self.ik_norm = mx.zeros((q.head_dim,), dtype=BF16)
        self.q_norm = mx.ones((self.Dh,), dtype=BF16)  # (1 + w) folded
        self.k_norm = mx.ones((self.Dh,), dtype=BF16)
        self.scale = self.Dh**-0.5
        self.eps = cfg["rms_norm_eps"]

    @property
    def weight_bytes(self) -> int:
        return self.index_qk.nbytes + self.qkv.nbytes + self.o_proj.nbytes

    def new_cache(self):
        from mlx_lm.models.cache import KVCache

        return KVCache(), K.QSAIndexerCache(self.qcfg)

    def fill(self, caches, T: int):
        kv, ic = caches
        kv.update_and_fetch(
            mx.random.normal((1, self.Hkv, T, self.Dh)).astype(BF16),
            mx.random.normal((1, self.Hkv, T, self.Dh)).astype(BF16),
        )
        ic.update(mx.random.normal((1, T, self.qcfg.head_dim)).astype(BF16), self.ik_norm)
        mx.eval(kv.keys, kv.values, ic.raw, ic.blocks)

    def __call__(self, x, caches):
        kv, ic = caches
        B, L, _ = x.shape
        off = kv.offset
        iq, raw = K.qsa_split_qk(self.index_qk(x), self.iq_norm, self.qcfg, offset=off)
        bk = ic.update(raw, self.ik_norm)
        p = self.qkv(x)
        nq = self.Hq * self.Dh * 2
        qg = p[..., :nq].reshape(B, L, self.Hq, 2 * self.Dh)
        q, gate = qg[..., : self.Dh], qg[..., self.Dh :]
        k = p[..., nq : nq + self.Hkv * self.Dh].reshape(B, L, self.Hkv, self.Dh)
        v = p[..., nq + self.Hkv * self.Dh :].reshape(B, L, self.Hkv, self.Dh)
        q = mx.fast.rms_norm(q, self.q_norm, self.eps).transpose(0, 2, 1, 3)
        k = mx.fast.rms_norm(k, self.k_norm, self.eps).transpose(0, 2, 1, 3)
        q = K.qsa_rope(q, self.qcfg, off)
        k = K.qsa_rope(k, self.qcfg, off)
        keys, values = kv.update_and_fetch(k, v.transpose(0, 2, 1, 3))
        if L == 1:
            idx = K.qsa_decode_token_indices(iq, bk, off, self.qcfg)
            o = K.qsa_sparse_decode_attention(q, keys, values, idx, self.scale)
        else:
            mask = K.qsa_prefill_mask(iq, bk, off, self.qcfg)
            o = K.sdpa_query_chunked(q, keys, values, self.scale, "causal" if mask is None else mask)
        o = o.transpose(0, 2, 1, 3).reshape(B, L, -1) * mx.sigmoid(gate.reshape(B, L, -1))
        return self.o_proj(o)


class GatedResidual:
    """One hyper-connection read/write (HF:990-1018), 2 per decoder layer."""

    def __init__(self, cfg: dict, bits: Optional[int]):
        self.n, self.H = cfg["hc_count"], cfg["hidden_size"]
        self.down = Lin(cfg["hc_lowrank"], self.n * self.H, bits)
        self.up = Lin(self.n * self.H, cfg["hc_lowrank"], bits)
        self.inject = Lin(self.n, self.n * self.H, None)
        self.norm_w = mx.ones((self.n * self.H,), dtype=BF16)  # (1 + w) folded
        self.eps = cfg["rms_norm_eps"]

    @property
    def weight_bytes(self) -> int:
        return self.down.nbytes + self.up.nbytes + self.inject.nbytes

    def __call__(self, h4, branch: Callable):
        B, T, _ = h4.shape
        # Grouped RMSNorm (one group per stream), then the 4*H weight.
        hnf = mx.fast.rms_norm(h4.reshape(B, T, self.n, self.H), None, self.eps).reshape(B, T, -1) * self.norm_w
        hn = hnf.reshape(B, T, self.n, self.H)
        w = mx.sigmoid(self.up(nn.silu(self.down(hnf) / self.n))).reshape(B, T, self.n, self.H)
        mixed = (w * hn).mean(axis=-2)
        inj = 2 * mx.sigmoid(self.inject(hnf) / self.n)
        out = branch(mixed)
        return h4 + (out[..., None, :] * inj[..., None]).reshape(B, T, -1)


class MoEBlock:
    """512-expert MoE: router + routed experts + shared expert."""

    def __init__(self, cfg: dict, gu_bits: int, dn_bits: int, variant: str, shared_bits: Optional[int] = None):
        H, I, E = cfg["hidden_size"], cfg["moe_intermediate_size"], cfg["num_experts"]
        self.E, self.k, self.variant = E, cfg["num_experts_per_tok"], variant
        fold = variant == "fused_folded"
        Ee = E + 1 if fold else E
        if variant == "split3":
            self.gate = quantized_experts(Ee, I, H, gu_bits)
            self.up = quantized_experts(Ee, I, H, gu_bits)
        else:
            self.gate_up = quantized_experts(Ee, 2 * I, H, gu_bits)
        self.down = quantized_experts(Ee, H, I, dn_bits)
        self.gu_bits, self.dn_bits = gu_bits, dn_bits
        self.router = (mx.random.normal((E + 1, H)) * 0.02).astype(BF16)  # + shared_expert_gate row
        if not fold:
            sb = shared_bits if shared_bits is not None else gu_bits
            self.shared_gu = Lin(2 * I, H, sb)
            self.shared_dn = Lin(H, I, sb)
        mx.eval(self.router)

    @property
    def weight_bytes(self) -> int:
        n = 0
        for k in ("gate", "up", "gate_up", "down"):
            if hasattr(self, k):
                n += sum(a.nbytes for a in getattr(self, k).values())
        if hasattr(self, "shared_gu"):
            n += self.shared_gu.nbytes + self.shared_dn.nbytes
        return n + self.router.nbytes

    def bytes_per_token_decode(self) -> int:
        per_expert = 0
        for k in ("gate", "up", "gate_up", "down"):
            if hasattr(self, k):
                per_expert += sum(a.nbytes for a in getattr(self, k).values()) // getattr(self, k)["weight"].shape[0]
        n_act = self.k + (1 if self.variant == "fused_folded" else 0)
        shared = self.shared_gu.nbytes + self.shared_dn.nbytes if hasattr(self, "shared_gu") else 0
        return n_act * per_expert + shared + self.router.nbytes

    def _gq(self, x, w, idx, bits, srt):
        return mx.gather_qmm(
            x, w["weight"], w["scales"], w["biases"], rhs_indices=idx, transpose=True,
            group_size=64, bits=bits, sorted_indices=srt,
        )

    def experts(self, x, inds):
        x = mx.expand_dims(x, (-2, -3))
        do_sort = inds.size >= 64
        idx, inv = inds, None
        if do_sort:
            x, idx, inv = K._gather_sort(x, inds)
        if self.variant == "split3":
            g = self._gq(x, self.gate, idx, self.gu_bits, do_sort)
            u = self._gq(x, self.up, idx, self.gu_bits, do_sort)
        else:
            h = self._gq(x, self.gate_up, idx, self.gu_bits, do_sort)
            I = h.shape[-1] // 2
            g, u = h[..., :I], h[..., I:]
        y = self._gq(K.swiglu_hf(g, u), self.down, idx, self.dn_bits, do_sort)
        if do_sort:
            y = mx.unflatten(y[inv], 0, inds.shape)
        return y.squeeze(-2)

    def __call__(self, x):
        logits = x @ self.router.T
        inds, w = K.moe_router(logits[..., : self.E], self.k)
        sg = mx.sigmoid(logits[..., self.E :])
        if self.variant == "fused_folded":
            inds = mx.concatenate([inds, mx.full((*inds.shape[:-1], 1), self.E, dtype=inds.dtype)], -1)
            w = mx.concatenate([w, sg.astype(w.dtype)], -1)
            return (self.experts(x, inds) * w[..., None]).sum(axis=-2)
        y = (self.experts(x, inds) * w[..., None]).sum(axis=-2)
        h = self.shared_gu(x)
        I = h.shape[-1] // 2
        return y + sg * self.shared_dn(K.swiglu_hf(h[..., :I], h[..., I:]))


# --------------------------------------------------------------------------
# suites
# --------------------------------------------------------------------------


def _x(T, H=2560):
    return (mx.random.normal((1, T, H)) * 0.5).astype(BF16)


def bench_gdn(cfg, args) -> List[dict]:
    out = []
    Hk, Hv, Dk, Dv = (cfg[k] for k in ("linear_num_key_heads", "linear_num_value_heads", "linear_key_head_dim", "linear_value_head_dim"))
    # Kernel alone: native mlx-lm inputs (bf16 q/k) vs the HF-exact adapter (fp32 q/k).
    for T in (1, 512):
        reps = 36 if T == 1 else 1
        q = mx.random.normal((1, T, Hk, Dk)).astype(BF16)
        k = mx.random.normal((1, T, Hk, Dk)).astype(BF16)
        v = mx.random.normal((1, T, Hv, Dv)).astype(BF16)
        a = mx.random.normal((1, T, Hv)).astype(BF16)
        b = mx.random.normal((1, T, Hv)).astype(BF16)
        A_log = mx.zeros((Hv,), dtype=BF16)
        dt = mx.ones((Hv,), dtype=BF16)
        s0 = mx.zeros((1, Hv, Dv, Dk), dtype=mx.float32)
        mx.eval(q, k, v, a, b, s0)
        for name, f in (("native_bf16_qk", K.gated_delta_native_mlx_lm), ("adapter_fp32_qk", K.gated_delta)):
            def run(f=f):
                s, y = s0, None
                for _ in range(reps):
                    y, s = f(q, k, v, a, b, A_log, dt, s)
                return y, s
            st = per_rep(timeit(run, args.iters), reps)
            out.append({"suite": "gdn_kernel", "variant": name, "T": T, **st})
            print(out[-1], flush=True)
    # Conv: explicit shifted FMAs vs mx.conv1d(groups=C).
    C = 2 * Hk * Dk + Hv * Dv
    w = mx.random.normal((C, cfg["linear_conv_kernel_dim"])).astype(BF16)
    for T in (1, 512):
        reps = 36 if T == 1 else 1
        x = mx.random.normal((1, T, C)).astype(BF16)
        st0 = mx.zeros((1, 3, C), dtype=BF16)
        mx.eval(x, w, st0)

        wf = w.astype(mx.float32)

        def explicit():
            y = x
            for _ in range(reps):
                xs = mx.concatenate([st0, y], axis=1)
                acc = xs[:, 0:T].astype(mx.float32) * wf[:, 0]
                for j in range(1, wf.shape[1]):
                    acc = acc + xs[:, j : j + T].astype(mx.float32) * wf[:, j]
                y = acc.astype(BF16)
            return y

        def conv():
            y = x
            for _ in range(reps):
                y, _s = K.depthwise_causal_conv1d(y, w, st0)
            return y

        for name, f in (("explicit_fma", explicit), ("mx_conv1d_groups", conv)):
            st = per_rep(timeit(f, args.iters), reps)
            out.append({"suite": "gdn_conv", "variant": name, "T": T, **st})
            print(out[-1], flush=True)
    # Whole layer.
    for bits in args.other_bits:
        layer = GDNLayer(cfg, bits)
        for T in (1, 512):
            reps = 36 if T == 1 else 1
            x = _x(T)
            mx.eval(x)

            def run(native=False):
                y, cs, s = x, None, None
                for _ in range(reps):
                    y, cs, s = layer(y, cs, s, native_kernel_inputs=native)
                return y, s

            st = per_rep(timeit(run, args.iters), reps)
            out.append({"suite": "gdn_layer", "bits": bits, "T": T, "weight_MB": layer.weight_bytes / 1e6, **st})
            print(out[-1], flush=True)
        del layer
        free()
    return out


def bench_qsa(cfg, args) -> List[dict]:
    out = []
    qc = K.QSAConfig.from_text_config(cfg)
    H, D = qc.n_heads, qc.head_dim
    # Indexer scoring + selection, decode (L=1) and prefill (L=512).
    for nb in (2048, 10240, 32768):
        bk = mx.random.normal((1, nb, D)).astype(BF16)
        for L in (1, 512):
            if L == 512 and nb > 10240:
                continue
            q = mx.random.normal((1, L, H, D)).astype(BF16)
            mx.eval(bk, q)
            reps = 12 if L == 1 else 1
            pos = 4 * nb + 3 - L + 1

            def score():
                r = None
                for _ in range(reps):
                    r = K.qsa_scores(q, bk)
                return r

            def select():
                r = None
                for _ in range(reps):
                    if L == 1:
                        r = K.qsa_decode_token_indices(q, bk, pos, qc)
                    else:
                        r = K.qsa_prefill_mask(q, bk, pos - 0, qc)
                return r

            for name, f in (("scores_only", score), ("scores+select+index", select)):
                st = per_rep(timeit(f, args.iters), reps)
                out.append({"suite": "qsa_indexer", "variant": name, "blocks": nb, "L": L, **st})
                print(out[-1], flush=True)
        del bk
        free()
    # Decode attention at context T: dense full, dense masked, sparse gather.
    Hq, Hkv, Dh = cfg["num_attention_heads"], cfg["num_key_value_heads"], cfg["head_dim"]
    for T in args.contexts:
        keys = mx.random.normal((1, Hkv, T, Dh)).astype(BF16)
        vals = mx.random.normal((1, Hkv, T, Dh)).astype(BF16)
        q = mx.random.normal((1, Hq, 1, Dh)).astype(BF16)
        iq = mx.random.normal((1, 1, H, D)).astype(BF16)
        bk = mx.random.normal((1, T // 4, D)).astype(BF16)
        mx.eval(keys, vals, q, iq, bk)
        reps = 12
        p = T - 1

        def dense():
            o = q
            for _ in range(reps):
                o = mx.fast.scaled_dot_product_attention(o, keys, vals, scale=Dh**-0.5)
            return o

        def sparse():
            o = q
            for _ in range(reps):
                idx = K.qsa_decode_token_indices(iq, bk, p, qc)
                o = K.qsa_sparse_decode_attention(o, keys, vals, idx, Dh**-0.5)
            return o

        def masked():
            o = q
            for _ in range(reps):
                m = K.qsa_prefill_mask(iq, bk, p, qc)
                o = mx.fast.scaled_dot_product_attention(o, keys, vals, scale=Dh**-0.5, mask=m)
            return o

        for name, f in (("dense_full", dense), ("qsa_sparse_gather", sparse), ("qsa_dense_masked", masked)):
            st = per_rep(timeit(f, args.iters), reps)
            out.append({"suite": "qsa_decode_attn", "variant": name, "T": T, **st})
            print(out[-1], flush=True)
        del keys, vals
        free()
    # Whole layer, decode and one 512-token prefill chunk at context T.
    for bits in args.other_bits:
        layer = QSALayer(cfg, bits)
        for T in args.contexts:
            for L in (1, 512):
                if L == 512 and T > args.max_prefill_ctx:
                    continue
                caches = layer.new_cache()
                layer.fill(caches, T - L)
                x = _x(L)
                mx.eval(x)
                kv, ic = caches
                reps = 12 if L == 1 else 1

                def run():
                    y = x
                    for _ in range(reps):
                        y = layer(y, caches)
                    return y

                def reset():
                    kv.offset = T - L
                    ic.trim(ic.offset - (T - L))

                ts = []
                for i in range(args.iters + 2):
                    reset()
                    t0 = time.perf_counter()
                    mx.eval(run())
                    if i >= 2:
                        ts.append(time.perf_counter() - t0)
                st = {"median_ms": 1e3 * statistics.median(ts) / reps}
                out.append({"suite": "qsa_layer", "bits": bits, "T": T, "L": L, "weight_MB": layer.weight_bytes / 1e6, **st})
                print(out[-1], flush=True)
                del caches
                free()
        del layer
        free()
    return out


def bench_moe(cfg, args) -> List[dict]:
    out = []
    H, E, k = cfg["hidden_size"], cfg["num_experts"], cfg["num_experts_per_tok"]
    # Router alone (bf16 weights, fp32 softmax/top-k), fused with shared_expert_gate.
    router = (mx.random.normal((E + 1, H)) * 0.02).astype(BF16)
    for T in (1, 512):
        x = _x(T)
        mx.eval(router, x)
        reps = 48 if T == 1 else 1

        def run():
            r = None
            for _ in range(reps):
                logits = x @ router.T
                r = K.moe_router(logits[..., :E], k)
            return r

        st = per_rep(timeit(run, args.iters), reps)
        out.append({"suite": "moe_router", "T": T, **st})
        print(out[-1], flush=True)
    for gu_bits, dn_bits in args.expert_bits:
        for variant in args.moe_variants:
            blk = MoEBlock(cfg, gu_bits, dn_bits, variant)
            for T in (1, 512):
                reps = 48 if T == 1 else 1
                xs = [_x(T) for _ in range(min(reps, 8))]
                mx.eval(*xs)

                def run():
                    y = None
                    for i in range(reps):
                        # Fresh inputs per rep so expert picks differ (no SLC reuse).
                        y = blk(xs[i % len(xs)] + (0 if y is None else 1e-3 * y))
                    return y

                st = per_rep(timeit(run, args.iters), reps)
                out.append({
                    "suite": "moe_block", "variant": variant, "gate_up_bits": gu_bits, "down_bits": dn_bits,
                    "T": T, "resident_MB": blk.weight_bytes / 1e6,
                    "decode_bytes_per_token_MB": blk.bytes_per_token_decode() / 1e6, **st,
                })
                print(out[-1], flush=True)
            del blk
            free()
    return out


def bench_misc(cfg, args) -> List[dict]:
    out = []
    for bits in args.other_bits:
        hc = GatedResidual(cfg, bits)
        for T in (1, 512):
            reps = 96 if T == 1 else 2
            h4 = (mx.random.normal((1, T, cfg["hc_count"] * cfg["hidden_size"])) * 0.5).astype(BF16)
            mx.eval(h4)

            def run():
                y = h4
                for _ in range(reps):
                    y = hc(y, lambda m: m)
                return y

            st = per_rep(timeit(run, args.iters), reps)
            out.append({"suite": "hyper_connection", "bits": bits, "T": T, "weight_MB": hc.weight_bytes / 1e6, **st})
            print(out[-1], flush=True)
        del hc
        free()
        head = Lin(cfg["vocab_size"], cfg["hidden_size"], bits)
        for T in (1,):
            x = _x(T)
            mx.eval(x)
            st = timeit(lambda: head(x), args.iters)
            out.append({"suite": "lm_head", "bits": bits, "T": T, "weight_MB": head.nbytes / 1e6, **st})
            print(out[-1], flush=True)
        del head
        free()
    return out


class DepthModel:
    """All 48 layers in the real pattern, 12 x (3 GDN + 1 QSA), each with
    2 hyper-connections and the MoE. One weight set per layer type is shared
    by every layer (the M4 cannot hold 48), but each layer has its own caches.
    Every layer's weights exceed the GPU caches (>= 7 MB), so the bytes moved
    per layer match a real model. Expert picks vary by layer (inputs differ).
    lm_head, embedding and PLE are timed separately (see ``bench_misc``)."""

    def __init__(self, cfg: dict, other_bits: Optional[int], expert_bits=(3, 3)):
        self.cfg = cfg
        self.types = [
            "linear" if (i + 1) % cfg["full_attention_interval"] else "qsa"
            for i in range(cfg["num_hidden_layers"])
        ]
        self.gdn = GDNLayer(cfg, other_bits)
        self.qsa = QSALayer(cfg, other_bits)
        self.hc_attn = GatedResidual(cfg, other_bits)
        self.hc_mlp = GatedResidual(cfg, other_bits)
        self.moe = MoEBlock(cfg, expert_bits[0], expert_bits[1], "fused_folded")
        self.reset(0)

    def reset(self, context: int):
        self.gdn_state = {i: (None, None) for i, t in enumerate(self.types) if t == "linear"}
        self.qsa_cache = {}
        for i, t in enumerate(self.types):
            if t == "qsa":
                c = self.qsa.new_cache()
                if context:
                    self.qsa.fill(c, context)
                self.qsa_cache[i] = c
        if context:
            for i in self.gdn_state:
                self.gdn_state[i] = (
                    mx.zeros((1, self.cfg["linear_conv_kernel_dim"] - 1, self.gdn.conv_dim), dtype=BF16),
                    mx.zeros((1, self.gdn.Hv, self.gdn.Dv, self.gdn.Dk), dtype=mx.float32),
                )
        mx.eval([s for st in self.gdn_state.values() for s in st if s is not None])

    def __call__(self, h4):
        for i, t in enumerate(self.types):
            if t == "linear":
                cs, s = self.gdn_state[i]
                box = {}

                def branch(m, cs=cs, s=s, box=box):
                    y, box["cs"], box["s"] = self.gdn(m, cs, s)
                    return y

                h4 = self.hc_attn(h4, branch)
                self.gdn_state[i] = (box["cs"], box["s"])
            else:
                h4 = self.hc_attn(h4, lambda m, c=self.qsa_cache[i]: self.qsa(m, c))
            h4 = self.hc_mlp(h4, self.moe)
        return h4


def bench_model(cfg, args) -> List[dict]:
    out = []
    for bits in args.other_bits:
        model = DepthModel(cfg, bits, args.expert_bits[0])
        H4 = cfg["hc_count"] * cfg["hidden_size"]
        for ctx in args.model_contexts:
            # Decode: one eval per token, as in generation.
            model.reset(ctx)
            h = (mx.random.normal((1, 1, H4)) * 0.5).astype(BF16)
            mx.eval(h)
            ts = []
            for i in range(args.iters + 2):
                t0 = time.perf_counter()
                h = model(h)
                mx.eval(h)
                if i >= 2:
                    ts.append(time.perf_counter() - t0)
            ts.sort()
            out.append({
                "suite": "model_decode", "other_bits": bits, "expert_bits": args.expert_bits[0],
                "context": ctx, "median_ms": 1e3 * statistics.median(ts), "p10_ms": 1e3 * ts[len(ts) // 10],
                "tok_s_excl_head": 1.0 / statistics.median(ts),
            })
            print(out[-1], flush=True)
            free()
        for chunk in args.prefill_chunks:
            h = (mx.random.normal((1, chunk, H4)) * 0.5).astype(BF16)
            mx.eval(h)
            ts = []
            for i in range(max(2, args.iters // 2) + 1):
                model.reset(0)
                t0 = time.perf_counter()
                y = model(h)
                mx.eval(y)
                if i >= 1:
                    ts.append(time.perf_counter() - t0)
            med = statistics.median(ts)
            out.append({
                "suite": "model_prefill", "other_bits": bits, "expert_bits": args.expert_bits[0],
                "chunk": chunk, "context_end": chunk, "median_ms": 1e3 * med, "tok_s": chunk / med,
            })
            print(out[-1], flush=True)
            free()
        out.append({
            "suite": "model_weights", "other_bits": bits,
            "per_layer_MB": {
                "gdn": model.gdn.weight_bytes / 1e6, "qsa": model.qsa.weight_bytes / 1e6,
                "hc": model.hc_attn.weight_bytes / 1e6, "moe_resident": model.moe.weight_bytes / 1e6,
                "moe_decode_per_token": model.moe.bytes_per_token_decode() / 1e6,
            },
            "peak_MB": mx.get_peak_memory() / 1e6,
        })
        print(out[-1], flush=True)
        del model
        free()
    return out


SUITES = {"gdn": bench_gdn, "qsa": bench_qsa, "moe": bench_moe, "misc": bench_misc, "model": bench_model}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--suite", default="all", choices=["all", *SUITES])
    ap.add_argument("--json", type=Path)
    ap.add_argument("--iters", type=int, default=7)
    ap.add_argument("--mem-gb", type=float, default=2.5)
    ap.add_argument("--contexts", type=int, nargs="*", default=[2048, 8192, 32768, 40960])
    ap.add_argument("--max-prefill-ctx", type=int, default=16384)
    ap.add_argument("--other-bits", type=lambda s: None if s == "bf16" else int(s), nargs="*", default=[8])
    ap.add_argument("--expert-bits", type=lambda s: tuple(int(x) for x in s.split("/")), nargs="*",
                    default=[(3, 3), (4, 4), (3, 4)])
    ap.add_argument("--moe-variants", nargs="*", default=["split3", "fused", "fused_folded"])
    ap.add_argument("--model-contexts", type=int, nargs="*", default=[1024, 8192])
    ap.add_argument("--prefill-chunks", type=int, nargs="*", default=[512, 2048])
    args = ap.parse_args(argv)
    mx.set_memory_limit(int(args.mem_gb * 2**30))
    mx.set_cache_limit(256 * 2**20)
    mx.random.seed(0)
    cfg = real_text_config()
    results = []
    for name in (SUITES if args.suite == "all" else [args.suite]):
        results += SUITES[name](cfg, args)
        free()
    meta = {
        "device": mx.device_info() if hasattr(mx, "device_info") else {},
        "mlx": mx.__version__,
        "python": sys.version.split()[0],
        "machine": platform.platform(),
        "peak_memory_MB": mx.get_peak_memory() / 1e6,
        "argv": sys.argv[1:],
    }
    if args.json:
        args.json.write_text(json.dumps({"meta": meta, "results": results}, indent=1, default=str))
    print(json.dumps(meta, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
