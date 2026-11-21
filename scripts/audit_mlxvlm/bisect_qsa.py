"""Localize a QSA-layer divergence: compare the indexer's selected-token masks
and per-query attention outputs between mlx-vlm and transformers.

Usage: python bisect_qsa.py CASE_DIR LAYER
"""
import sys
from pathlib import Path

import numpy as np
import torch


def main(case, li):
    import mlx.core as mx
    from mlx_vlm.utils import load_model
    from transformers import Qwen4ExpForConditionalGeneration
    from transformers.masking_utils import create_causal_mask
    case = Path(case)
    ids = [int(t) for t in np.load(case / "ref.npz")["ids"]]
    L = len(ids)
    ref = Qwen4ExpForConditionalGeneration.from_pretrained(case / "hf", dtype=torch.float32).eval()
    ref.config.text_config._attn_implementation = "eager"
    lm_ref = ref.model.language_model
    attn_ref = lm_ref.layers[li].self_attn
    cap = {}
    names = ("hidden_states", "position_embeddings", "attention_mask")
    attn_ref.register_forward_hook(lambda m, a, k, o: cap.update(
        **{n: (a[i] if i < len(a) else k[n]) for i, n in enumerate(names)}, out=o[0].detach(), weights=o[1].detach()), with_kwargs=True)
    with torch.inference_mode():
        ref(torch.tensor([ids]), use_cache=False)
        cap["x"] = cap["hidden_states"]
        # Effective attended set = nonzero eager attention weights (any head).
        sel_ref = (cap["weights"][0] > 0).any(0).numpy()  # [L, L] bool

    model = load_model(case / "vlm_hf_fused")
    att = model.language_model.model.layers[li].self_attn
    x = mx.array(cap["x"].numpy())
    pos = mx.arange(L)[None]
    selection = att.indexer.select(x, None, pos)
    sel_vlm = np.array(att.indexer.build_mask(selection))[0, 0]
    diff = np.argwhere(sel_ref != sel_vlm)
    am = cap["attention_mask"]
    print("ref attention_mask dtype", am.dtype, "row0", am[0, 0, 0, :4].tolist(), "row5", am[0, 0, 5, :8].tolist())
    print("selected-token mask mismatches:", len(diff))
    rows = sorted(set(int(r) for r, _ in diff))
    for q in [r for r in rows if r >= 10][:6]:
        print(f" q={q:2d} ref={np.flatnonzero(sel_ref[q]).tolist()}")
        print(f"      vlm={np.flatnonzero(sel_vlm[q]).tolist()}")
    out_vlm = np.array(att(x, mask=None, cache=None, position_ids=pos))
    d = np.abs(out_vlm - cap["out"].numpy()).max(axis=-1)[0]
    print("per-query max|attn out diff|:", np.array2string(d, precision=2, max_line_width=200))
    print("first divergent query:", int(np.argmax(d > 1e-5)) if (d > 1e-5).any() else None)
    scores_vlm(att, x, pos, range(11, 16))




def scores_vlm(att, x, pos, queries):
    """Recompute mlx-vlm's per-block indexer scores (same ops as
    select_from_projected, zero padding, no cache) for the given queries."""
    import mlx.core as mx
    import math
    ix = att.indexer
    qk = ix.index_qk_proj(x)
    b, s, _ = qk.shape
    qk = qk.reshape(b, s, ix.n_heads + ix.kv_heads, ix.head_dim)
    q = ix._apply_rope(ix.q_layernorm(qk[:, :, :ix.n_heads]).transpose(0, 2, 1, 3), pos)
    raw = qk[:, :, ix.n_heads:].squeeze(2)
    nb = s // ix.compress_ratio
    pooled = raw[:, :nb * ix.compress_ratio].reshape(b, nb, ix.compress_ratio, ix.head_dim)
    pooled = ix.k_layernorm(mx.mean(pooled.astype(mx.float32), axis=2).astype(raw.dtype))[:, None]
    pooled = ix._apply_rope(pooled, pos[..., mx.arange(nb) * ix.compress_ratio])
    sc = q.astype(mx.float32) @ pooled.astype(mx.float32).transpose(0, 1, 3, 2)  # [b, H, s, nb]
    per_head = np.array(sc)[0]
    tot = np.maximum(per_head, 0).sum(0) / math.sqrt(ix.head_dim)
    for qi in queries:
        n = (qi + 1) // ix.compress_ratio
        print(f" q={qi}: block scores={np.array2string(tot[qi, :n], precision=4)} "
              f"per-head dots={np.array2string(per_head[:, qi, :n], precision=3)}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
