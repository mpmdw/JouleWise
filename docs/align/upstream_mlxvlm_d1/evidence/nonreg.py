"""Bitwise non-regression check for the D1 fix: single-request and
equal-length-batch logits (and short-context ragged ones) must be identical
before and after. Usage: python nonreg.py OUT.npz"""

import sys

import mlx.core as mx
import numpy as np

from mlx_vlm.generate.ar import _make_cache
from mlx_vlm.models.qwen4_exp.language import LanguageModel, TextConfig


def config(head_dim):
    return TextConfig(
        model_type="qwen4_exp_text", vocab_size=64, hidden_size=32,
        num_hidden_layers=2, layer_types=["linear_attention", "full_attention"],
        num_attention_heads=2, num_key_value_heads=1, head_dim=head_dim,
        linear_num_key_heads=1, linear_num_value_heads=2, linear_key_head_dim=32,
        linear_value_head_dim=16, linear_conv_kernel_dim=4, num_experts=4,
        num_experts_per_tok=2, moe_intermediate_size=16,
        shared_expert_intermediate_size=16, hc_count=2, hc_lowrank=8,
        rms_norm_eps=1e-6, max_position_embeddings=128,
        rope_parameters={"rope_type": "default", "rope_theta": 10000,
                         "partial_rotary_factor": 0.25,
                         "mrope_section": [1, 1, 0] if head_dim == 16 else [2, 1, 1]},
        indexer_budget=8, indexer_compress_ratio=4, indexer_n_heads=16,
        indexer_head_dim=16,
    )


def run(lm, prompts, cache, verify_len):
    width = max(map(len, prompts))
    pads = [width - len(p) for p in prompts]
    ids = mx.array([[0] * n + p for n, p in zip(pads, prompts)])
    pos = mx.array([[0] * n + list(range(len(p))) for n, p in zip(pads, prompts)])
    out = [lm(ids, cache=cache, position_ids=pos).logits[:, -1:]]
    for step, token in enumerate([40, 41, 42]):
        pos = mx.array([[len(p) + step] for p in prompts])
        out.append(lm(mx.full((len(prompts), 1), token), cache=cache, position_ids=pos).logits)
    block = mx.array([[43, 44, 45, 46][:verify_len]] * len(prompts))
    out.append(lm.speculative_verify_logits(block, cache, lambda x: x)[3])
    return np.array(mx.concatenate(out, axis=1).astype(mx.float32))


results = {}
A, A2, B = list(range(1, 15)), list(range(30, 44)), list(range(20, 31))
SHORT_A, SHORT_B = list(range(1, 5)), list(range(20, 22))  # stays below 12 tokens
for dtype, head_dim in (("float32", 16), ("bfloat16", 32)):
    for path in ("invariant", "module"):
        for verify_len in (2, 3):
            mx.random.seed(0)
            lm = LanguageModel(config(head_dim))
            lm.set_dtype(getattr(mx, dtype))
            lm.eval()
            mx.eval(lm.parameters())
            if path == "module":
                lm._supports_batch_invariant_decode = lambda: False
            key = f"{dtype}_{path}_v{verify_len}"
            results[f"{key}_single_A"] = run(lm, [A], lm.make_cache(), verify_len)
            results[f"{key}_single_B"] = run(lm, [B], lm.make_cache(), verify_len)
            results[f"{key}_equal_AA2"] = run(lm, [A, A2], _make_cache(lm, [0, 0]), verify_len)
            results[f"{key}_ragged_short"] = run(
                lm, [SHORT_A, SHORT_B], _make_cache(lm, [0, 2]), verify_len)
            results[f"{key}_ragged_long"] = run(lm, [A, B], _make_cache(lm, [0, 3]), verify_len)
np.savez(sys.argv[1], **results)
print(len(results), "arrays saved")
