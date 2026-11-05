"""Numerical tests for joulewise/align/models/qwen4_exp_kernels.py.

Each fast path is compared with a straightforward pure-MLX reference on random
inputs. Runs only where mlx and the pinned mlx-lm import (the Mac venvs). CI,
which has no extras, skips it. Run with:

    /private/tmp/jwsol/venv-mlx/bin/python -m unittest -v tests.align.test_qwen4_exp_kernels
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

HAVE_MLX = (
    importlib.util.find_spec("mlx") is not None and importlib.util.find_spec("mlx_lm") is not None
)

ROOT = Path(__file__).resolve().parents[2]
REAL_CONFIG = ROOT / ".engine" / "hf-flashnext" / "config.json"

if HAVE_MLX:
    import mlx.core as mx
    import mlx.nn as nn

    from joulewise.align.models import qwen4_exp_kernels as K


def _maxabs(a, b) -> float:
    return mx.abs(a.astype(mx.float32) - b.astype(mx.float32)).max().item()


def _gdn_inputs(B, T, Hk, Hv, Dk, Dv, dtype=None, key_scale=1.0, seed=0):
    dtype = dtype or mx.float32
    mx.random.seed(seed)
    q = (mx.random.normal((B, T, Hk, Dk)) * key_scale).astype(dtype)
    k = (mx.random.normal((B, T, Hk, Dk)) * key_scale).astype(dtype)
    v = mx.random.normal((B, T, Hv, Dv)).astype(dtype)
    a = mx.random.normal((B, T, Hv)).astype(dtype)
    b = mx.random.normal((B, T, Hv)).astype(dtype)
    A_log = mx.log(mx.random.uniform(0.01, 16, (Hv,))).astype(dtype)
    dt_bias = mx.random.normal((Hv,)).astype(dtype)
    return q, k, v, a, b, A_log, dt_bias


@unittest.skipUnless(HAVE_MLX, "mlx / mlx_lm not installed")
class GatedDeltaNetTests(unittest.TestCase):
    def test_l2norm_identity(self):
        mx.random.seed(1)
        x = mx.random.normal((3, 5, 4, 128)) * 0.01
        q, k = K.gdn_qk_normalize(x, x)
        ref = x * mx.rsqrt((x * x).sum(-1, keepdims=True) + 1e-6)
        self.assertLess(_maxabs(k, ref), 1e-6)
        self.assertLess(_maxabs(q, ref / 128**0.5), 1e-7)

    def test_kernel_matches_reference_fp32_gqa_with_state(self):
        args = _gdn_inputs(2, 17, 2, 6, 64, 32, seed=2)
        Hv, Dk, Dv = 6, 64, 32
        s_hf = mx.random.normal((2, Hv, Dk, Dv)) * 0.1
        y_ref, s_ref = K.gated_delta_reference(*args, state_hf=s_hf)
        y, s = K.gated_delta(*args, state=K.gdn_state_from_hf(s_hf))
        self.assertEqual(y.dtype, mx.float32)
        self.assertLess(_maxabs(y, y_ref), 2e-6)
        self.assertLess(_maxabs(K.gdn_state_to_hf(s), s_ref), 2e-6)
        # The ops fallback (CPU-safe path) agrees too.
        y2, s2 = K.gated_delta(*args, state=K.gdn_state_from_hf(s_hf), use_kernel=False)
        self.assertLess(_maxabs(y2, y_ref), 2e-6)

    def test_kernel_matches_reference_real_head_counts(self):
        # Real config: 16 QK heads, 48 V heads, head dims 128.
        args = _gdn_inputs(1, 6, 16, 48, 128, 128, seed=3)
        y_ref, s_ref = K.gated_delta_reference(*args)
        y, s = K.gated_delta(*args)
        self.assertLess(_maxabs(y, y_ref), 2e-6)
        self.assertLess(_maxabs(K.gdn_state_to_hf(s), s_ref), 2e-6)

    def test_prefill_equals_stepwise(self):
        q, k, v, a, b, A_log, dt_bias = _gdn_inputs(1, 12, 2, 4, 64, 64, seed=4)
        y_all, s_all = K.gated_delta(q, k, v, a, b, A_log, dt_bias)
        s, ys = None, []
        for t in range(12):
            sl = slice(t, t + 1)
            y_t, s = K.gated_delta(q[:, sl], k[:, sl], v[:, sl], a[:, sl], b[:, sl], A_log, dt_bias, s)
            ys.append(y_t)
        self.assertEqual(_maxabs(mx.concatenate(ys, axis=1), y_all), 0.0)
        self.assertEqual(_maxabs(s, s_all), 0.0)

    def test_bf16_model_dtype(self):
        args32 = _gdn_inputs(1, 9, 2, 6, 64, 64, seed=5)
        args16 = [x.astype(mx.bfloat16) for x in args32]
        y_ref, _ = K.gated_delta_reference(*[x.astype(mx.float32) for x in args16])
        y, s = K.gated_delta(*args16)
        self.assertEqual(y.dtype, mx.bfloat16)
        self.assertEqual(s.dtype, mx.float32)
        # Only the final cast to bf16 differs: |y| <~ 4, bf16 half-ulp <= 2**-7.
        self.assertLess(_maxabs(y, y_ref), 2**-6)

    def test_native_mlx_lm_normalization_is_not_hf(self):
        # Small-norm q/k: sum(x^2) ~ 1e-4 makes the eps mismatch visible.
        args = _gdn_inputs(1, 5, 2, 4, 64, 64, key_scale=1.2e-3, seed=6)
        y_ref, _ = K.gated_delta_reference(*args)
        y_adapt, _ = K.gated_delta(*args)
        y_native, _ = K.gated_delta_native_mlx_lm(*args)
        self.assertLess(_maxabs(y_adapt, y_ref), 1e-6)
        self.assertGreater(_maxabs(y_native, y_ref), 1e-2)

    def test_left_padding_mask(self):
        args = _gdn_inputs(1, 10, 2, 4, 64, 32, seed=7)
        pad = 3
        mask = mx.arange(10)[None] >= pad
        y_m, s_m = K.gated_delta(*args, mask=mask)
        sliced = [x[:, pad:] if x.ndim >= 3 else x for x in args]
        y_u, s_u = K.gated_delta(*sliced)
        self.assertEqual(mx.abs(y_m[:, :pad]).max().item(), 0.0)
        self.assertLess(_maxabs(y_m[:, pad:], y_u), 1e-6)
        self.assertLess(_maxabs(s_m, s_u), 1e-6)

    def test_depthwise_conv_matches_fp32_sum_and_streams(self):
        mx.random.seed(8)
        B, T, C, Kw = 2, 11, 40, 4
        for dtype in (mx.float32, mx.bfloat16):
            x = mx.random.normal((B, T, C)).astype(dtype)
            w = mx.random.normal((C, Kw)).astype(dtype)
            out, st = K.depthwise_causal_conv1d(x, w)
            xp = mx.pad(x, [(0, 0), (Kw - 1, 0), (0, 0)]).astype(mx.float32)
            ref = sum(xp[:, j : j + T] * w[:, j].astype(mx.float32) for j in range(Kw))
            # fp32 accumulation, one final rounding (bit-exact in bf16).
            self.assertLess(_maxabs(out, ref.astype(dtype)), 1e-5)
            s, outs = None, []
            for t in range(T):
                o, s = K.depthwise_causal_conv1d(x[:, t : t + 1], w, s)
                outs.append(o)
            self.assertLess(_maxabs(mx.concatenate(outs, axis=1), out), 1e-6)
            self.assertEqual(_maxabs(s, st), 0.0)

    def test_rms_norm_gated_sigmoid(self):
        mx.random.seed(9)
        x, z = mx.random.normal((5, 128)), mx.random.normal((5, 128))
        w = mx.random.normal((128,))
        ref = w * (x * mx.rsqrt((x * x).mean(-1, keepdims=True) + 1e-6)) * mx.sigmoid(z)
        self.assertLess(_maxabs(K.rms_norm_gated(x, z, w, 1e-6), ref), 1e-5)


def _tiny_qsa():
    # Exercise sparsity at small sizes: budget 16 tokens = 4 blocks of 4.
    return K.QSAConfig(n_heads=4, head_dim=32, budget=16, compress_ratio=4, rope_dims=16, rope_base=1e4)


def _qsa_inputs(cfg, B, T, seed=0, dtype=None):
    dtype = dtype or mx.float32
    mx.random.seed(seed)
    qk = mx.random.normal((B, T, (cfg.n_heads + 1) * cfg.head_dim)).astype(dtype)
    qw = (mx.random.normal((cfg.head_dim,)) * 0.1).astype(dtype)
    kw = (mx.random.normal((cfg.head_dim,)) * 0.1).astype(dtype)
    return qk, qw, kw


@unittest.skipUnless(HAVE_MLX, "mlx / mlx_lm not installed")
class QSATests(unittest.TestCase):
    def assertSelectionEquivalent(self, mask, ref_mask, ref_scores, cfg, offset):
        """Masks must agree except on blocks tied with the K-th score."""
        r = cfg.compress_ratio
        diff = mask != ref_mask
        if not diff.any().item():
            return
        B, _, L, T = mask.shape
        for bi in range(B):
            for qi in range(L):
                row = diff[bi, 0, qi]
                if not row.any().item():
                    continue
                sc = ref_scores[bi][qi]
                kth = mx.sort(sc)[-cfg.block_topk].item()
                toks = [t for t in range(T) if row[t].item()]
                for t in toks:
                    self.assertLess(t // r, sc.shape[0], "difference outside the block region")
                    self.assertAlmostEqual(sc[t // r].item(), kth, delta=1e-6)

    def test_real_config_constants(self):
        cfg_json = json.loads(REAL_CONFIG.read_text())["text_config"]
        cfg = K.QSAConfig.from_text_config(cfg_json)
        self.assertEqual((cfg.block_topk, cfg.dense_limit, cfg.rope_dims), (512, 2051, 64))
        self.assertEqual(cfg.rope_base, 1e7)

    def test_mlx_rope_scalar_offset_bug_and_workaround(self):
        mx.random.seed(12)
        cfg = _tiny_qsa()
        x = mx.random.normal((3, 2, 1, cfg.head_dim))
        per_row = mx.concatenate(
            [mx.fast.rope(x[b : b + 1], cfg.rope_dims, traditional=False, base=cfg.rope_base, scale=1.0, offset=5) for b in range(3)]
        )
        self.assertLess(_maxabs(K.qsa_rope(x, cfg, 5), per_row), 1e-6)
        raw = mx.fast.rope(x, cfg.rope_dims, traditional=False, base=cfg.rope_base, scale=1.0, offset=5)
        if _maxabs(raw, per_row) < 1e-6:
            print("note: mx.fast.rope scalar-offset bug is fixed in this mlx; rope_offset() is now a no-op safeguard")

    def test_block_keys_match_explicit_rope(self):
        cfg = _tiny_qsa()
        qk, qw, kw = _qsa_inputs(cfg, 2, 40, seed=10)
        _, raw = K.qsa_split_qk(qk, qw, cfg)
        fast = K.qsa_block_keys(raw[:, 8:40], kw, cfg, block_offset=2)
        _, scores = K.qsa_reference_mask(
            mx.zeros((2, 40, cfg.n_heads, cfg.head_dim)), raw, kw, cfg, return_scores=True
        )
        # Rebuild the reference block keys for blocks 2..9 explicitly.
        r, D = cfg.compress_ratio, cfg.head_dim
        pooled = raw[:, 8:40].reshape(2, 8, r, D).mean(axis=2)
        normed = K.rms_norm_1p(pooled, kw, cfg.eps)
        pos = (mx.arange(2, 10) * r).astype(mx.float32)
        inv = 1.0 / (cfg.rope_base ** (mx.arange(0, cfg.rope_dims, 2, dtype=mx.float32) / cfg.rope_dims))
        fr = pos[:, None] * inv[None]
        emb = mx.concatenate([fr, fr], -1)
        xr, xp = normed[..., : cfg.rope_dims], normed[..., cfg.rope_dims :]
        h = cfg.rope_dims // 2
        rot = mx.concatenate([-xr[..., h:], xr[..., :h]], -1)
        ref = mx.concatenate([xr * mx.cos(emb) + rot * mx.sin(emb), xp], -1)
        self.assertLess(_maxabs(fast, ref), 2e-5)

    def test_scores_match_loop(self):
        cfg = _tiny_qsa()
        mx.random.seed(11)
        q = mx.random.normal((2, 3, cfg.n_heads, cfg.head_dim))
        kb = mx.random.normal((2, 7, cfg.head_dim))
        s = K.qsa_scores(q, kb)
        for bi in range(2):
            for qi in range(3):
                ref = mx.maximum(q[bi, qi] @ kb[bi].T, 0).sum(0) / cfg.head_dim**0.5
                self.assertLess(_maxabs(s[bi, qi], ref), 1e-5)

    def _prefill(self, cfg, qk, qw, kw, offset=0):
        q, raw = K.qsa_split_qk(qk, qw, cfg, offset=0)
        T = raw.shape[1]
        nb = T // cfg.compress_ratio
        bk = K.qsa_block_keys(raw[:, : nb * cfg.compress_ratio], kw, cfg)
        qc = q[:, offset:]
        mask = K.qsa_prefill_mask(qc, bk, offset, cfg)
        ref, scores = K.qsa_reference_mask(qc, raw, kw, cfg, offset=offset, return_scores=True)
        return mask, ref, scores

    def test_prefill_mask_matches_reference_sparse(self):
        cfg = _tiny_qsa()
        for seed, (B, T, off) in enumerate([(1, 45, 0), (2, 38, 21), (1, 64, 60)]):
            qk, qw, kw = _qsa_inputs(cfg, B, T, seed=20 + seed)
            mask, ref, scores = self._prefill(cfg, qk, qw, kw, off)
            self.assertIsNotNone(mask)
            self.assertEqual(mask.shape, ref.shape)
            self.assertSelectionEquivalent(mask, ref, scores, cfg, off)
            # Never more than K blocks + tail, and always causal.
            counts = mask.astype(mx.int32).sum(-1)
            self.assertLessEqual(counts.max().item(), cfg.budget + cfg.compress_ratio - 1)
            pos = mx.arange(off, T)[:, None]
            self.assertFalse((mask[:, 0] & (mx.arange(T)[None] > pos)[None]).any().item())

    def test_dense_regime_is_causal(self):
        cfg = _tiny_qsa()
        T = cfg.dense_limit  # 19 for the tiny config
        qk, qw, kw = _qsa_inputs(cfg, 1, T, seed=30)
        mask, ref, _ = self._prefill(cfg, qk, qw, kw, 0)
        self.assertIsNone(mask)
        causal = mx.arange(T)[None, :] <= mx.arange(T)[:, None]
        self.assertTrue(mx.array_equal(ref[0, 0], causal).item())
        qk2, qw2, kw2 = _qsa_inputs(cfg, 1, T + 1, seed=30)
        mask2, _, _ = self._prefill(cfg, qk2, qw2, kw2, 0)
        self.assertIsNotNone(mask2)

    def test_incremental_cache_matches_one_shot_and_trims(self):
        cfg = _tiny_qsa()
        qk, qw, kw = _qsa_inputs(cfg, 2, 41, seed=40)
        _, raw = K.qsa_split_qk(qk, qw, cfg)
        cache = K.QSAIndexerCache(cfg)
        cache.step = 8
        pos = 0
        for n in (5, 1, 1, 7, 3, 1, 12, 11):
            bk = cache.update(raw[:, pos : pos + n], kw)
            pos += n
        self.assertEqual((cache.offset, cache.n_blocks), (41, 10))
        one_shot = K.qsa_block_keys(raw[:, :40], kw, cfg)
        self.assertEqual(_maxabs(bk, one_shot), 0.0)
        # Trim into the middle of a block, then re-feed different keys.
        cache.trim(7)
        self.assertEqual((cache.offset, cache.n_blocks), (34, 8))
        _, raw2 = K.qsa_split_qk(_qsa_inputs(cfg, 2, 7, seed=41)[0], qw, cfg)
        bk2 = cache.update(raw2, kw)
        fresh = K.qsa_block_keys(mx.concatenate([raw[:, :34], raw2], axis=1)[:, :40], kw, cfg)
        self.assertEqual(_maxabs(bk2, fresh), 0.0)

    def test_decode_selection_and_sparse_attention(self):
        cfg = _tiny_qsa()
        T = 53
        qk, qw, kw = _qsa_inputs(cfg, 1, T, seed=50)
        q, raw = K.qsa_split_qk(qk, qw, cfg)
        cache = K.QSAIndexerCache(cfg)
        bk = cache.update(raw, kw)
        p = T - 1
        idx = K.qsa_decode_token_indices(q[:, p:], bk, p, cfg)
        self.assertEqual(idx.shape, (1, cfg.budget + (p + 1) % cfg.compress_ratio))
        mask = K.qsa_prefill_mask(q[:, p:], bk, p, cfg)
        from_idx = (mx.arange(T)[:, None] == idx[0][None, :]).any(axis=1)
        ref, scores = K.qsa_reference_mask(q[:, p:], raw, kw, cfg, offset=p, return_scores=True)
        self.assertSelectionEquivalent(from_idx[None, None, None], ref, scores, cfg, p)
        self.assertSelectionEquivalent(mask, ref, scores, cfg, p)
        # Gathered attention == dense attention under the same mask.
        Hq, Hkv, Dh = 6, 2, 64
        mx.random.seed(51)
        qq = mx.random.normal((1, Hq, 1, Dh))
        kk = mx.random.normal((1, Hkv, T + 9, Dh))  # buffer longer than kv_len
        vv = mx.random.normal((1, Hkv, T + 9, Dh))
        sparse = K.qsa_sparse_decode_attention(qq, kk, vv, idx, scale=Dh**-0.5)
        dense = mx.fast.scaled_dot_product_attention(
            qq, kk[:, :, :T], vv[:, :, :T], scale=Dh**-0.5, mask=from_idx[None, None, None]
        )
        self.assertLess(_maxabs(sparse, dense), 1e-5)
        full = K.qsa_sparse_decode_attention(qq, kk, vv, None, scale=Dh**-0.5, kv_len=T)
        ref_full = mx.fast.scaled_dot_product_attention(qq, kk[:, :, :T], vv[:, :, :T], scale=Dh**-0.5)
        self.assertLess(_maxabs(full, ref_full), 1e-6)

    def test_query_chunked_sdpa(self):
        mx.random.seed(60)
        q = mx.random.normal((1, 4, 70, 32))
        k = mx.random.normal((1, 2, 90, 32))
        v = mx.random.normal((1, 2, 90, 32))
        m = mx.random.uniform(shape=(1, 1, 70, 90)) > 0.3
        m = m | (mx.arange(90)[None, None, None] == 0)
        ref = mx.fast.scaled_dot_product_attention(q, k, v, scale=0.2, mask=m)
        out = K.sdpa_query_chunked(q, k, v, 0.2, m, max_score_bytes=4 * 2 * 90 * 4 * 16)
        self.assertLess(_maxabs(out, ref), 1e-5)
        outc = K.sdpa_query_chunked(q, k, v, 0.2, "causal", max_score_bytes=4 * 2 * 90 * 4 * 16)
        refc = mx.fast.scaled_dot_product_attention(q, k, v, scale=0.2, mask=(mx.arange(90)[None] <= mx.arange(20, 90)[:, None]))
        self.assertLess(_maxabs(outc, refc), 1e-5)


def _moe_weights(E, H, I, seed=0, dtype=None):
    dtype = dtype or mx.float32
    mx.random.seed(seed)
    gate_up = (mx.random.normal((E, 2 * I, H)) * H**-0.5).astype(dtype)
    down = (mx.random.normal((E, H, I)) * I**-0.5).astype(dtype)
    sgu = (mx.random.normal((2 * I, H)) * H**-0.5).astype(dtype)
    sdn = (mx.random.normal((H, I)) * I**-0.5).astype(dtype)
    router = mx.random.normal((E, H)).astype(dtype)
    sgate = mx.random.normal((1, H)).astype(dtype) * 0.1
    return gate_up, down, sgu, sdn, router, sgate


def _dequant(sw):
    gs, bits = sw.gu_q
    gu = mx.dequantize(sw.gate_up["weight"], sw.gate_up["scales"], sw.gate_up["biases"], gs, bits)
    gs, bits = sw.dn_q
    dn = mx.dequantize(sw.down["weight"], sw.down["scales"], sw.down["biases"], gs, bits)
    return gu, dn


@unittest.skipUnless(HAVE_MLX, "mlx / mlx_lm not installed")
class MoETests(unittest.TestCase):
    E, H, I, TOPK = 16, 128, 64, 4

    def test_router_ranks_fp32_probabilities(self):
        mx.random.seed(70)
        logits = (mx.random.normal((64, 512)) * 0.02).astype(mx.bfloat16)
        inds, w = K.moe_router(logits, 10)
        probs = mx.softmax(logits.astype(mx.float32), axis=-1)
        ref = mx.sort(mx.argsort(-probs, axis=-1)[:, :10], axis=-1)
        self.assertTrue(mx.array_equal(mx.sort(inds.astype(mx.int32), -1), ref.astype(mx.int32)).item())
        self.assertEqual(w.dtype, mx.bfloat16)
        self.assertLess(_maxabs(w.astype(mx.float32).sum(-1), mx.ones((64,))), 1e-2)
        # bf16 probabilities (mlx-lm's softmax(precise=True) on bf16 logits)
        # collapse distinct fp32 probabilities into ties.
        p16 = mx.softmax(logits, axis=-1, precise=True)
        self.assertEqual(p16.dtype, mx.bfloat16)
        uniq16 = len(set(p16[0].tolist()))
        uniq32 = len(set(probs[0].tolist()))
        self.assertLess(uniq16, uniq32)

    def _check_block(self, x, bits=None):
        gu, dn, sgu, sdn, router, sgate = _moe_weights(self.E, self.H, self.I, seed=71)
        experts = K.FusedSwitchGLU(gu, dn)
        if bits is not None:
            experts.quantize(gu_bits=bits[0], down_bits=bits[1], group_size=64)
            gu, dn = _dequant(experts)
        split = K.moe_block_split(x, router, experts, K.DenseGLU(sgu, sdn), sgate, self.TOPK)
        ref = K.moe_reference(x, router, gu, dn, sgu, sdn, sgate, self.TOPK)
        self.assertLess(_maxabs(split, ref), 1e-4)
        fgu, fdn = K.fold_shared_expert(gu, dn, sgu, sdn)
        folded_experts = K.FusedSwitchGLU(fgu, fdn)
        folded = K.moe_block_folded(x, mx.concatenate([router, sgate]), folded_experts, self.TOPK, self.E)
        self.assertLess(_maxabs(folded, ref), 1e-4)

    def test_unsorted_path_matches_reference(self):
        mx.random.seed(72)
        self._check_block(mx.random.normal((1, 3, self.H)))  # 12 picks < 64: no sort

    def test_sorted_path_matches_reference(self):
        mx.random.seed(73)
        self._check_block(mx.random.normal((2, 13, self.H)))  # 104 picks: sorted path

    def test_quantized_mixed_bits_match_dequantized_reference(self):
        mx.random.seed(74)
        x = mx.random.normal((1, 20, self.H))
        for bits in ((4, 4), (3, 3), (3, 4)):
            with self.subTest(bits=bits):
                self._check_block(x, bits)


if __name__ == "__main__":
    unittest.main()
