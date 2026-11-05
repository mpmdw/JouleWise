"""Minimal reproducer: mlx-vlm's qwen4_exp (Qwen3.8-Flash-Next) drops Qwen
Sparse Attention (QSA) in left-padded batches.

If any row of a batch is left-padded, each QSA layer computes its top-k block
selection during decode and speculative verify, then discards it and attends
to every key. Each row that has seen at least
indexer_budget + indexer_compress_ratio tokens (2052 on the released model,
12 here) then drifts from the same prompt run alone. This includes the
unpadded row.

Needs only mlx-vlm. It builds a tiny random fp32 qwen4_exp text model and runs
two prompts (14 and 11 tokens, so left padding [0, 3]) as one batch and one
at a time: 3 decode steps, then a 3-token speculative verify block. It prints
the largest logit difference per row for each decode path, plus an
equal-length batch as a control. Exit status: 1 if any ragged difference
exceeds 1e-4, else 0.

    python repro_minimal.py
"""

import os
import sys

# True fp32 matmuls, as mlx_vlm/tests/conftest.py sets for the test suite.
os.environ["MLX_ENABLE_TF32"] = "0"

import mlx.core as mx  # noqa: E402

from mlx_vlm.generate.ar import _make_cache  # noqa: E402
from mlx_vlm.models.qwen4_exp.language import LanguageModel, TextConfig  # noqa: E402

CONFIG = TextConfig(
    model_type="qwen4_exp_text",
    vocab_size=64,
    hidden_size=32,
    num_hidden_layers=2,
    layer_types=["linear_attention", "full_attention"],
    num_attention_heads=2,
    num_key_value_heads=1,
    head_dim=16,
    linear_num_key_heads=1,
    linear_num_value_heads=2,
    linear_key_head_dim=32,
    linear_value_head_dim=16,
    linear_conv_kernel_dim=4,
    num_experts=4,
    num_experts_per_tok=2,
    moe_intermediate_size=16,
    shared_expert_intermediate_size=16,
    hc_count=2,
    hc_lowrank=8,
    rms_norm_eps=1e-6,
    max_position_embeddings=128,
    rope_parameters={
        "rope_type": "default",
        "rope_theta": 10000,
        "partial_rotary_factor": 0.25,
        "mrope_section": [1, 1, 0],
    },
    # Keep the top 8 / 4 = 2 blocks of 4 tokens plus the partial tail block:
    # attention is sparse once a query sees 12 or more tokens.
    indexer_budget=8,
    indexer_compress_ratio=4,
    indexer_n_heads=16,  # many heads, so no exact-zero score ties
    indexer_head_dim=16,
)
PROMPT_A, PROMPT_B = list(range(1, 15)), list(range(20, 31))  # 14, 11 tokens


def run(lm, prompts, cache):
    """Prefill, decode 3 tokens, verify 3 more. Returns logits [B, 6, vocab]."""
    width = max(map(len, prompts))
    pads = [width - len(p) for p in prompts]
    ids = mx.array([[0] * n + p for n, p in zip(pads, prompts)])
    pos = mx.array([[0] * n + list(range(len(p))) for n, p in zip(pads, prompts)])
    lm(ids, cache=cache, position_ids=pos)
    out = []
    for step, token in enumerate([40, 41, 42]):
        pos = mx.array([[len(p) + step] for p in prompts])
        tokens = mx.full((len(prompts), 1), token)
        out.append(lm(tokens, cache=cache, position_ids=pos).logits)
    block = mx.array([[43, 44, 45]] * len(prompts))
    out.append(lm.speculative_verify_logits(block, cache, lambda x: x)[3])
    return mx.concatenate(out, axis=1)


def max_diff(batched, singles, part):
    """Largest |logit difference| per row over the decode or verify steps."""
    return [mx.abs(b[part] - s[part]).max().item() for b, s in zip(batched, singles)]


mx.random.seed(0)
lm = LanguageModel(CONFIG)
lm.eval()

print(
    "max |logit(batch) - logit(single request)|   ragged row 0 (pad 0)"
    "   ragged row 1 (pad 3)   equal-length control"
)
failed = False
for path in ("batch-invariant path (default)", "attention-module path"):
    if path.startswith("attention"):
        # Decode takes this path when lm_head is quantized in a format the
        # batch-invariant forward does not support (for example 6-bit).
        lm._supports_batch_invariant_decode = lambda: False
    single = [run(lm, [p], lm.make_cache())[0] for p in (PROMPT_A, PROMPT_B)]
    ragged = run(lm, [PROMPT_A, PROMPT_B], _make_cache(lm, [0, 3]))
    control = run(lm, [PROMPT_A, PROMPT_A], _make_cache(lm, [0, 0]))
    for name, part in (("decode", slice(0, 3)), ("verify", slice(3, 6))):
        row0, row1 = max_diff(ragged, single, part)
        ctrl = max(max_diff(control, [single[0]] * 2, part))
        label = f"{name}, {path}" if name == "decode" else "  then a 3-token verify"
        print(f"{label:45s}{row0:>9.1e}{row1:>23.1e}{ctrl:>23.1e}")
        failed |= max(row0, row1) > 1e-4

print("FAIL: the ragged batch differs from single requests" if failed else "PASS")
sys.exit(1 if failed else 0)
