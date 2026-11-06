"""mlx-vlm side of the qwen4_exp numerical audit (released mlx-vlm from PyPI,
isolated venv). Loads the real-layout tiny checkpoints written by ref_gen.py
with mlx_vlm.utils.load_model and records logits for every scenario.

Usage: python run_vlm.py WORKDIR
"""
import json
import sys
from pathlib import Path

import numpy as np

STEPS = 3
NEXT = [5, 6, 7]


def f(v):
    import mlx.core as mx
    v = getattr(v, "logits", v)
    mx.eval(v)
    return np.array(v.astype(mx.float32))


def reset(lm):
    # What mlx_vlm.generate.ar.generate_step does before each request.
    lm._position_ids = None
    lm._rope_deltas = None


def scenarios(lm, ids, mask_rows):
    import mlx.core as mx
    from mlx_vlm.generate.ar import _make_cache
    L = len(ids)
    x = mx.array(np.array(ids, dtype=np.int32)[None])
    r = {}
    reset(lm)
    r["prefill_nocache"] = f(lm(x))
    reset(lm)
    r["prefill"] = f(lm(x, cache=lm.make_cache()))
    reset(lm)
    cache, steps = lm.make_cache(), []
    for i in range(L):
        steps.append(f(lm(x[:, i:i + 1], cache=cache)))
    r["stepwise"] = np.concatenate(steps, 1)
    reset(lm)
    cache, chunks = lm.make_cache(), []
    P = L // 2 + 1
    chunks.append(f(lm(x[:, :P], cache=cache)))
    for s in range(P, L, 4):
        chunks.append(f(lm(x[:, s:s + 4], cache=cache)))
    r["chunked"] = np.concatenate(chunks, 1)
    # Left-padded batch exactly as BatchGenerator builds it: left-padded ids,
    # _make_cache(model, left_padding) and no explicit mask.
    pads = [int((~m.astype(bool)).sum()) for m in mask_rows]
    batch = np.zeros(mask_rows.shape, dtype=np.int32)
    for b, pad in enumerate(pads):
        batch[b, pad:] = ids[:L - pad]
    # Prompt metadata as batch_generate/BatchGenerator forward it (text-only):
    # per-row positions 0..n-1 left-padded with zeros, rope_deltas 0, and
    # rope_deltas re-sent on each decode step.
    pos = np.zeros(mask_rows.shape, dtype=np.int32)
    for b, pad in enumerate(pads):
        pos[b, pad:] = np.arange(L - pad)
    kw = dict(rope_deltas=mx.zeros((len(pads), 1), dtype=mx.int32))
    reset(lm)
    cache = _make_cache(lm, pads)
    r["padded_batch"] = f(lm(mx.array(batch), cache=cache, position_ids=mx.array(pos), **kw))
    cont = []
    for t in range(STEPS):
        cont.append(f(lm(mx.full((len(pads), 1), NEXT[t], dtype=mx.int32), cache=cache, **kw)))
    r["padded_continuation"] = np.concatenate(cont, 1)
    for b, pad in enumerate(pads):
        reset(lm)
        r[f"single_row{b}"] = f(lm(mx.array(np.array([list(ids[:L - pad]) + NEXT], dtype=np.int32))))
    return r


def speculative_rollback(lm, ids, keep=2, block=5):
    """Hybrid-cache 'trim': prefill P, speculate a block, commit `keep`, continue."""
    import mlx.core as mx
    from mlx_vlm.speculative.cache_state import start_speculative_cache
    L = len(ids)
    x = mx.array(np.array(ids, dtype=np.int32)[None])
    P = L // 2
    reset(lm)
    cache = lm.make_cache()
    out = [f(lm(x[:, :P], cache=cache))]
    tx = start_speculative_cache(cache, block)
    f(lm(x[:, P:P + block], cache=cache))
    tx.commit(keep)
    out.append(f(lm(x[:, P + keep:], cache=cache)))
    return np.concatenate(out, 1)


def vlm_view(src):
    """mlx-vlm 0.7.12 rejects layer_types 'indexed_attention' (what transformers
    5.22.1 writes on save_pretrained; finding F1). Present the same weights with
    the original checkpoint spelling 'full_attention' (identical semantics in
    the official config, which maps full_attention -> indexed_attention)."""
    dst = src.parent / ("vlm_" + src.name)
    if not dst.exists():
        dst.mkdir()
        for p in src.iterdir():
            if p.name != "config.json":
                (dst / p.name).symlink_to(p.resolve())
        cfg = json.loads((src / "config.json").read_text())
        tc = cfg["text_config"]
        tc["layer_types"] = ["full_attention" if t == "indexed_attention" else t for t in tc["layer_types"]]
        (dst / "config.json").write_text(json.dumps(cfg, indent=2))
    return dst


def main(work, patched=False):
    import mlx.core as mx
    if patched:
        sys.path.insert(0, str(Path(__file__).parent))
        import d1_patch
        d1_patch.apply()
    import mlx_vlm
    from mlx_vlm.utils import load_model
    work = Path(work)
    meta = dict(mlx_vlm=mlx_vlm.__version__, mlx=mx.__version__)
    for d in sorted(p for p in work.iterdir() if p.is_dir() and (p / "ref.npz").exists()):
        ref = np.load(d / "ref.npz")
        ids = [int(t) for t in ref["ids"]]
        model = load_model(vlm_view(d / "hf_fused"))
        lm = model.language_model
        r = scenarios(lm, ids, ref["padded_mask"])
        r["spec_rollback"] = speculative_rollback(lm, ids)
        # Per-expert layout (what transformers save_pretrained writes) must load identically.
        per_expert = load_model(vlm_view(d / "hf")).language_model
        reset(per_expert)
        r["prefill_perexpert"] = f(per_expert(mx.array(np.array([ids], dtype=np.int32))))
        np.savez(d / ("vlmP.npz" if patched else "vlm.npz"), **r)
        types = {k: str(v.dtype) for k, v in __import__("mlx.utils", fromlist=["tree_flatten"]).tree_flatten(lm.parameters())
                 if any(s in k for s in ("A_log", "layers.0.linear_attn.norm.weight", "embed_tokens"))}
        meta[d.name] = dict(param_dtypes=types)
        print(json.dumps(dict(case=d.name, **meta[d.name])))
    (work / ("vlmP_meta.json" if patched else "vlm_meta.json")).write_text(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], "--patched" in sys.argv)
