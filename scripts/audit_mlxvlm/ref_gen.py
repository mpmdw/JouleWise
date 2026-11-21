"""Reference side of the mlx-vlm qwen4_exp numerical audit (tiny random configs only).

Builds tiny random Qwen3.8-Flash-Next text models in the official transformers
5.22.1 implementation, writes them as REAL-LAYOUT checkpoints
(Qwen4ExpForConditionalGeneration: model.language_model.*, fused experts,
sharded n-gram table, a tiny vision tower) and records reference logits for
every audit scenario. No real weights are touched.

Usage: python ref_gen.py OUTDIR
"""
import copy
import json
import sys
from pathlib import Path

import numpy as np
import torch

EOS = 2
STEPS = 3  # cached continuation steps after a padded prefill


def config_a():
    """Exactly the Sol port's tests/align/qwen4_exp_reference.py tiny config."""
    return dict(vocab_size=64, hidden_size=64, num_hidden_layers=2,
                num_attention_heads=2, num_key_value_heads=1, head_dim=32,
                hc_count=2, hc_lowrank=8, linear_conv_kernel_dim=3,
                linear_key_head_dim=32, linear_value_head_dim=32,
                linear_num_key_heads=1, linear_num_value_heads=2,
                moe_intermediate_size=64, shared_expert_intermediate_size=64,
                num_experts=4, num_experts_per_tok=2,
                layer_types=["linear_attention", "indexed_attention"],
                ple_layer_ids=[1], ple_embed_dim=64, ple_conv_kernel_size=2,
                ngram_size=3, heads_per_ngram=2, ngram_vocab_size_base=17,
                make_ngram_vocab_size_divisible_by=8, split_ngram_parts=4,
                eos_token_id=EOS, indexer_n_heads=2, indexer_kv_heads=1,
                indexer_head_dim=16, indexer_budget=4, indexer_compress_ratio=2,
                output_gate_type="sigmoid",
                # mrope_section is the reference default ([11, 11, 10]) and is a
                # no-op for text-only positions; mlx-vlm's config requires it.
                rope_parameters=dict(rope_type="default", rope_theta=10000., partial_rotary_factor=.25,
                                     mrope_section=[11, 11, 10]))


def config_b():
    """Discriminating config: real layer pattern (3 DeltaNet + 1 QSA, PLE at
    one-indexed layer 2), GQA 2x in attention, 3x DeltaNet value/key ratio with
    2 key heads (separates repeat vs tile and qkv layouts), hc_count=4, real
    compress ratio 4, 8 experts top-3, real mrope rope_parameters."""
    return dict(vocab_size=96, hidden_size=64, num_hidden_layers=4,
                num_attention_heads=4, num_key_value_heads=2, head_dim=32,
                hc_count=4, hc_lowrank=16, linear_conv_kernel_dim=4,
                linear_key_head_dim=32, linear_value_head_dim=32,
                linear_num_key_heads=2, linear_num_value_heads=6,
                moe_intermediate_size=32, shared_expert_intermediate_size=48,
                num_experts=8, num_experts_per_tok=3,
                layer_types=["linear_attention", "linear_attention", "linear_attention", "full_attention"],
                ple_layer_ids=[2], ple_embed_dim=64, ple_conv_kernel_size=4,
                ngram_size=3, heads_per_ngram=2, ngram_vocab_size_base=29,
                make_ngram_vocab_size_divisible_by=8, split_ngram_parts=4,
                eos_token_id=EOS, indexer_n_heads=2, indexer_kv_heads=1,
                indexer_head_dim=16, indexer_budget=8, indexer_compress_ratio=4,
                output_gate_type="sigmoid", initializer_range=0.05,
                rope_parameters=dict(rope_type="default", rope_theta=10000., partial_rotary_factor=.25,
                                     mrope_interleaved=True, mrope_section=[11, 11, 10]))


def config_c():
    """Config B made tie-free and quantizable: 16 indexer heads (an exact-zero
    relu score then needs all 16 head dots negative, so QSA top-k has no exact
    ties; finding P3 is shown on B) and every Linear in-dim a multiple of 64."""
    c = config_b()
    c.update(indexer_n_heads=16, hc_lowrank=64, moe_intermediate_size=64,
             shared_expert_intermediate_size=64)
    return c


T1_PROMPTS = (20, 17)  # coordinator T1: prompts of 20 and 17 tokens, left padding [0, 3]
T1_GREEDY, T1_VERIFY = 4, 3


def ids_for(name):
    if name == "A":
        return [7, 8, 9, 10, 2, 12, 13, 14, 15, 16, 17]
    if name == "T1":
        rng = np.random.default_rng(1105)
        return [rng.integers(3, 96, size=n).tolist() for n in T1_PROMPTS]
    rng = np.random.default_rng(2026_11_05)
    ids = rng.integers(3, 96, size=40).tolist()
    ids[9] = EOS
    ids[25] = EOS
    return ids


# Left padding per row for the padded-batch scenario: (pad, kept_length).
def pad_rows(n):
    return [(0, n), (4, n - 4), (n // 3 + 1, n - (n // 3 + 1))]


def build_model(text_cfg, seed):
    from transformers import Qwen4ExpTextConfig, Qwen4ExpForCausalLM
    torch.manual_seed(seed)
    config = Qwen4ExpTextConfig(**text_cfg)
    config._attn_implementation = "eager"
    model = Qwen4ExpForCausalLM(config).eval()
    # As in the Sol port's gold harness: nonzero zero-centred norms (exercise
    # `1 + w` in fp32) and a nonzero PLE dilated conv (zero would hide history bugs).
    with torch.no_grad():
        for n, p in model.named_parameters():
            if n.endswith("ple.conv1d.weight") or ("norm" in n and ".linear_attn.norm." not in n):
                p.normal_(mean=0, std=.02)
            if n.endswith("linear_attn.norm.weight"):
                p.copy_(1 + .1 * torch.randn_like(p))
    return model


def real_layout_checkpoint(causal, directory, dtype):
    """Save the causal LM's text weights as a Qwen4ExpForConditionalGeneration
    checkpoint (the layout of Qwen/Qwen3.8-Flash-Next) via transformers itself."""
    from transformers import Qwen4ExpConfig, Qwen4ExpForConditionalGeneration
    tc = causal.config.to_dict()
    vision = dict(depth=1, hidden_size=32, intermediate_size=64, num_heads=2, patch_size=4,
                  spatial_merge_size=2, temporal_patch_size=2, out_hidden_size=tc["hidden_size"],
                  num_position_embeddings=16)
    cfg = Qwen4ExpConfig(text_config=tc, vision_config=vision, image_token_id=60, video_token_id=61,
                         vision_start_token_id=58, vision_end_token_id=59, tie_word_embeddings=False)
    torch.manual_seed(5)
    full = Qwen4ExpForConditionalGeneration(cfg).eval()
    full.model.language_model.load_state_dict(causal.model.state_dict(), strict=True)
    full.lm_head.load_state_dict(causal.lm_head.state_dict())
    full = full.to(dtype)
    full.save_pretrained(directory, max_shard_size="200KB")
    return full


def fuse_experts(src, dst):
    """Rewrite transformers' per-expert save into the fused layout of the real
    Qwen/Qwen3.8-Flash-Next shards: mlp.experts.gate_up_proj [E, 2I, H]
    (gate rows first, as the official Qwen4ExpTextExperts chunks them) and
    mlp.experts.down_proj [E, H, I]."""
    import re
    from safetensors.torch import load_file, save_file
    src, dst = Path(src), Path(dst)
    dst.mkdir(parents=True)
    tensors = {}
    for f in sorted(src.glob("*.safetensors")):
        tensors.update(load_file(f))
    pat = re.compile(r"^(.*\.mlp\.experts)\.(\d+)\.(gate|up|down)_proj\.weight$")
    groups = {}
    out = {}
    for k, v in tensors.items():
        m = pat.match(k)
        if m:
            groups.setdefault(m[1], {}).setdefault(m[3], {})[int(m[2])] = v
        else:
            out[k] = v
    for base, parts in groups.items():
        n = len(parts["gate"])
        gate = torch.stack([parts["gate"][i] for i in range(n)])
        up = torch.stack([parts["up"][i] for i in range(n)])
        out[base + ".gate_up_proj"] = torch.cat([gate, up], dim=1).contiguous()
        out[base + ".down_proj"] = torch.stack([parts["down"][i] for i in range(n)]).contiguous()
    save_file(out, dst / "model.safetensors", metadata={"format": "pt"})
    (dst / "model.safetensors.index.json").write_text(json.dumps(
        {"metadata": {}, "weight_map": {k: "model.safetensors" for k in sorted(out)}}, indent=1))
    for name in ("config.json", "generation_config.json"):
        if (src / name).exists():
            (dst / name).write_text((src / name).read_text())


@torch.inference_mode()
def logits(model, ids, cache=None, mask=None, pos=None):
    kw = dict(use_cache=cache is not None)
    if cache is not None:
        kw["past_key_values"] = cache
    if mask is not None:
        kw["attention_mask"] = mask
    if pos is not None:
        kw["position_ids"] = pos
    out = model(torch.as_tensor(ids), **kw)
    return out.logits.float().numpy(), out.past_key_values


def scenarios(model, ids):
    from transformers import DynamicCache
    r = {}
    L = len(ids)
    x = np.array([ids])
    r["prefill"], _ = logits(model, x)
    cache, steps = DynamicCache(config=model.config), []
    for i in range(L):
        lg, cache = logits(model, x[:, i:i + 1], cache)
        steps.append(lg)
    r["stepwise"] = np.concatenate(steps, 1)
    # Prefill a prefix, then continue in multi-token chunks (generation pattern).
    cache, chunks = DynamicCache(config=model.config), []
    P = L // 2 + 1
    lg, cache = logits(model, x[:, :P], cache)
    chunks.append(lg)
    for s in range(P, L, 4):
        lg, cache = logits(model, x[:, s:s + 4], cache)
        chunks.append(lg)
    r["chunked"] = np.concatenate(chunks, 1)
    # Left-padded batch with HF-generate-style positions, then cached steps.
    rows = pad_rows(L)
    B = len(rows)
    batch = np.zeros((B, L), dtype=np.int64)
    mask = np.zeros((B, L), dtype=np.int64)
    for b, (pad, n) in enumerate(rows):
        batch[b, pad:] = ids[:n]
        mask[b, pad:] = 1
    pos = np.maximum(np.cumsum(mask, 1) - 1, 0)
    cache = DynamicCache(config=model.config)
    lg, cache = logits(model, batch, cache, torch.as_tensor(mask), torch.as_tensor(pos))
    r["padded_batch"] = lg
    r["padded_mask"] = mask
    cont = []
    nxt = [5, 6, 7]
    for t in range(STEPS):
        mask = np.concatenate([mask, np.ones((B, 1), dtype=np.int64)], 1)
        pos = mask.sum(1, keepdims=True) - 1
        lg, cache = logits(model, np.full((B, 1), nxt[t]), cache, torch.as_tensor(mask), torch.as_tensor(pos))
        cont.append(lg)
    r["padded_continuation"] = np.concatenate(cont, 1)
    for b, (pad, n) in enumerate(rows):
        seq = np.array([ids[:n] + nxt])
        r[f"single_row{b}"], _ = logits(model, seq)  # [1, n + STEPS, V]
    return r


@torch.inference_mode()
def t1_reference(model):
    """Per-row truth for T1: reference greedy continuation (teacher-forced for
    every implementation) and full-sequence single-row prefill logits."""
    out = {}
    for b, prompt in enumerate(ids_for("T1")):
        seq = list(prompt)
        for _ in range(T1_GREEDY + T1_VERIFY):
            lg, _ = logits(model, np.array([seq]))
            seq.append(int(lg[0, -1].argmax()))
        out[f"t1_seq{b}"] = np.array(seq)
        out[f"t1_logits{b}"], _ = logits(model, np.array([seq]))
    # Equal-length control and padded batch through the reference itself.
    seqs = [out[f"t1_seq{b}"] for b in range(len(T1_PROMPTS))]
    n = max(len(s) for s in seqs)
    batch = np.zeros((len(seqs), n), dtype=np.int64)
    mask = np.zeros_like(batch)
    for b, s_ in enumerate(seqs):
        batch[b, n - len(s_):] = s_
        mask[b, n - len(s_):] = 1
    pos = np.maximum(np.cumsum(mask, 1) - 1, 0)
    out["t1_ref_padded"], _ = logits(model, batch, None, torch.as_tensor(mask), torch.as_tensor(pos))
    return out


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(2)
    meta = dict(torch=torch.__version__)
    import transformers
    meta["transformers"] = transformers.__version__
    for name, fn, seed in (("A", config_a, 631), ("B", config_b, 1105), ("C", config_c, 1105)):
        base = build_model(fn(), seed)
        ids = ids_for(name)
        # Evidence that QSA selection is really active: same weights, budget >= context.
        dense_cfg = copy.deepcopy(base.config)
        dense_cfg.indexer_budget = 1024
        from transformers import Qwen4ExpForCausalLM
        dense = Qwen4ExpForCausalLM(dense_cfg).eval()
        dense.load_state_dict(base.state_dict())
        for dtype_name, dtype in (("fp32", torch.float32), ("bf16", torch.bfloat16)):
            model = copy.deepcopy(base).to(dtype)
            d = out / f"{name}_{dtype_name}"
            full = real_layout_checkpoint(base, d / "hf", dtype)
            fuse_experts(d / "hf", d / "hf_fused")
            r = scenarios(model, ids)
            # ConditionalGeneration text-only path must equal the causal LM.
            with torch.inference_mode():
                cg = full(torch.as_tensor([ids])).logits.float().numpy()
            r["cg_prefill"] = cg
            dl, _ = logits(dense.to(dtype), np.array([ids]))
            r["dense_prefill"] = dl
            if name == "C":
                r.update(t1_reference(model))
            np.savez(d / "ref.npz", ids=np.array(ids), **r)
            info = dict(config=name, dtype=dtype_name, L=len(ids),
                        cg_vs_causal_max_abs=float(np.abs(cg - r["prefill"]).max()),
                        prefill_vs_stepwise_max_abs=float(np.abs(r["prefill"] - r["stepwise"]).max()),
                        sparse_vs_dense_max_abs=float(np.abs(dl - r["prefill"]).max()),
                        logit_absmax=float(np.abs(r["prefill"]).max()),
                        params=sum(p.numel() for p in model.parameters()))
            (d / "ref.json").write_text(json.dumps(info, indent=2))
            meta[f"{name}_{dtype_name}"] = info
            print(json.dumps(info))
    (out / "ref_meta.json").write_text(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
