"""T2 (router bf16 tie, P1), T6 (padded batch without cache, P5) and F1
(config spelling 'indexed_attention') for mlx-vlm 0.7.12.

Usage: python t_misc.py WORKDIR
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch


def t2_tie():
    import mlx.core as mx
    from mlx_vlm.models.qwen4_exp.language import (Qwen4ExpSparseMoeBlock,
                                                   _QWEN4_BATCH_INVARIANT_FORWARD as BIF)
    from transformers import Qwen4ExpTextConfig
    from transformers.models.qwen4_exp.modeling_qwen4_exp import Qwen4ExpTextTopKRouter
    E, K, H = 512, 10, 64
    logits = [3.0] * 9 + [0.5, 0.50390625] + [-1.0] * 501
    args = SimpleNamespace(hidden_size=H, moe_intermediate_size=64, shared_expert_intermediate_size=64,
                           num_experts=E, num_experts_per_tok=K, norm_topk_prob=True)
    block = Qwen4ExpSparseMoeBlock(args)
    w = np.zeros((E, H), dtype=np.float32)
    w[:, 0] = logits
    block.gate.weight = mx.array(w)
    block.set_dtype(mx.bfloat16)
    x = mx.zeros((1, 1, H), dtype=mx.bfloat16).at[..., 0].add(1.0)
    seen = {}

    class Rec:
        def __call__(self, x_, idx):
            seen.setdefault("main", np.array(idx).ravel().tolist())
            return mx.zeros((*idx.shape, H), dtype=x_.dtype)
    real = block.switch_mlp
    block.switch_mlp = Rec()
    gates = mx.softmax(block.gate(x), axis=-1, precise=True)  # the exact main-path expression
    block(x)
    block.switch_mlp = real
    BIF._switch_glu = lambda sm, x_, idx: (seen.setdefault("decode", np.array(idx).ravel().tolist()),
                                           mx.zeros((*idx.shape, H), dtype=x_.dtype))[1]
    BIF._feed_forward(block, x)
    del BIF._switch_glu  # drop the instance override
    probs = np.array(gates.astype(mx.float32)).ravel()
    # Reference router on identical bf16 logits.
    cfg = Qwen4ExpTextConfig(hidden_size=H, num_experts=E, num_experts_per_tok=K, norm_topk_prob=True)
    router = Qwen4ExpTextTopKRouter(cfg).to(torch.bfloat16)
    with torch.no_grad():
        router.weight.copy_(torch.tensor(w))
        _, rw, ri = router(torch.tensor(np.array(x.astype(mx.float32))).to(torch.bfloat16))
    p32 = torch.softmax(torch.tensor(logits, dtype=torch.bfloat16).float(), -1)
    return dict(
        softmax_output_dtype=str(gates.dtype),
        bf16_probs_experts_9_10=[float(probs[9]), float(probs[10])],
        fp32_probs_experts_9_10=[float(p32[9]), float(p32[10])],
        reference_selected=sorted(ri.ravel().tolist()),
        vlm_main_path_selected=sorted(seen["main"]),
        vlm_decode_path_selected=sorted(seen["decode"]),
        reference_weight_dtype=str(rw.dtype),
    )


def t2_flip_rate(n=20000, sigmas=(0.5, 1.0, 2.0, 4.0), E=512, K=10, seed=0):
    """Synthetic: how often bf16-softmax argpartition top-10 (mlx-vlm) differs
    from fp32-softmax topk (reference) on identical bf16 router logits."""
    import mlx.core as mx
    rng = np.random.default_rng(seed)
    out = {}
    for s in sigmas:
        lg = torch.tensor(rng.normal(0, s, size=(n, E)), dtype=torch.bfloat16)
        rp = torch.softmax(lg.float(), -1)
        rv, ri = torch.topk(rp, K, -1)
        rv = rv / rv.sum(-1, keepdim=True)
        g = mx.softmax(mx.array(lg.float().numpy()).astype(mx.bfloat16), axis=-1, precise=True)
        vi = mx.argpartition(g, kth=-K, axis=-1)[..., -K:]
        vs = mx.take_along_axis(g, vi, axis=-1)
        vs = vs / vs.sum(-1, keepdims=True)
        vi, vs = np.array(vi), np.array(vs.astype(mx.float32))
        ri, rv = ri.numpy(), rv.numpy()
        diff = np.array([set(a) != set(b) for a, b in zip(vi, ri)])
        set_diff = diff.mean()
        # Classify mismatches by the reference's own fp32 probabilities at the
        # rank-K/K+1 boundary: an exact fp32 tie (equal bf16 logits) is
        # implementation-defined tie order on both sides; a strict fp32 gap
        # that bf16 rounding of the softmax output erases is P1 proper.
        srt = torch.sort(rp, -1, descending=True).values.numpy()
        fp32_tie = srt[:, K - 1] == srt[:, K]
        b16 = np.array(g.astype(mx.float32))
        b16s = -np.sort(-b16, -1)
        bf16_tie = b16s[:, K - 1] == b16s[:, K]
        p1 = diff & ~fp32_tie
        out_extra = dict(
            mismatch_with_fp32_boundary_tie=float((diff & fp32_tie).mean()),
            mismatch_without_fp32_tie_P1=float(p1.mean()),
            P1_mismatches_where_bf16_rounding_created_the_tie=float((p1 & bf16_tie).mean()),
            fp32_boundary_tie_rate=float(fp32_tie.mean()),
            bf16_boundary_tie_rate=float(bf16_tie.mean()))
        # weight error on tokens with identical sets
        werr = []
        for a, av, b, bv in zip(vi[:2000], vs[:2000], ri[:2000], rv[:2000]):
            if set(a) == set(b):
                da = dict(zip(a.tolist(), av.tolist()))
                werr.append(max(abs(da[e] - w_) for e, w_ in zip(b.tolist(), bv.tolist())))
        out[f"sigma={s}"] = dict(topk_set_mismatch_rate=float(set_diff),
                                 max_weight_err_same_set=float(max(werr) if werr else 0), **out_extra)
    return out


def t6_no_cache(work):
    import mlx.core as mx
    from mlx_vlm.utils import load_model
    case = Path(work) / "C_fp32"
    ref = np.load(case / "ref.npz")
    ids = ref["ids"].astype(np.int32)
    L, pad = len(ids), 10
    lm = load_model(case / "vlm_hf_fused").language_model
    batch = np.stack([ids, np.concatenate([np.zeros(pad, np.int32), ids[:L - pad]])])
    mask = np.stack([np.ones(L, np.int32), np.concatenate([np.zeros(pad, np.int32), np.ones(L - pad, np.int32)])])
    lm._position_ids = lm._rope_deltas = None
    out = np.array(lm(mx.array(batch), attention_mask=mx.array(mask)).logits)
    truth_row1 = ref["prefill"][0][:L - pad]  # reference: unpadded single row
    return dict(row0_unpadded_max_abs=float(np.abs(out[0] - ref["prefill"][0]).max()),
                row1_leftpad10_max_abs=float(np.abs(out[1, pad:] - truth_row1).max()))


def f1_indexed_attention(work):
    from mlx_vlm.utils import load_model
    try:
        load_model(Path(work) / "C_fp32" / "hf_fused")
        return "loaded"
    except Exception as e:  # noqa: BLE001
        return f"{type(e).__name__}: {e}"


if __name__ == "__main__":
    w = sys.argv[1]
    print(json.dumps(dict(T2_tie=t2_tie(), T2_synthetic_flip_rate=t2_flip_rate(),
                          T6_padded_batch_no_cache=t6_no_cache(w), F1_transformers_saved_config=f1_indexed_attention(w)),
                     indent=1))
