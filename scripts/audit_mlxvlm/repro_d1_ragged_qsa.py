"""Minimal reproducer, mlx-vlm 0.7.12 (= main 5cdc659b for these files):
qwen4_exp ragged (left-padded) batched decode silently drops Qwen Sparse
Attention selection and attends densely, so every row of a ragged batch,
including the unpadded one, diverges from its single-request result once a
row's visible context exceeds indexer_budget + compress_ratio tokens
(real config: 2048 + 4 = 2052 tokens).

Self-contained: a random tiny qwen4_exp built in mlx-vlm itself (budget 8,
ratio 4 -> sparse from 12 visible tokens), driven through mlx-vlm's own
BatchGenerator (the continuous-batching engine behind batch_generate and the
server). Compares each row's greedy tokens and token logprobs with the same
prompt generated alone. An equal-length batch is the control.

  python repro_d1_ragged_qsa.py            # shows the bug
  python repro_d1_ragged_qsa.py --patched  # with d1_patch.py applied: exact

Root cause (mlx_vlm/models/qwen4_exp/language.py):
  * Qwen4ExpAttention.__call__ computes the selection, then for the string mask
    "left_padded_decode" returns super().__call__(...) (Qwen3_5Attention),
    discarding it (lines 1112-1122).
  * Qwen4ExpBatchInvariantForward._qsa_attention (the decode path actually
    used) builds qsa_mask but merges it only into None/"causal"/array masks
    (1871-1885) and then calls _attention, which routes "left_padded_decode"
    and any L>1 padded call to _qwen3_5_left_padded_attention, which never
    reads its mask (qwen3_5/language.py:878-940; speculative_verifier.py:97-112).
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import mlx.core as mx
import numpy as np

TEXT = dict(
    model_type="qwen4_exp_text", vocab_size=96, hidden_size=64, num_hidden_layers=4,
    num_attention_heads=4, num_key_value_heads=2, head_dim=32, hc_count=4, hc_lowrank=64,
    linear_conv_kernel_dim=4, linear_key_head_dim=32, linear_value_head_dim=32,
    linear_num_key_heads=2, linear_num_value_heads=6, moe_intermediate_size=64,
    shared_expert_intermediate_size=64, num_experts=8, num_experts_per_tok=3,
    layer_types=["linear_attention"] * 3 + ["full_attention"], ple_layer_ids=[2],
    ple_embed_dim=64, ple_conv_kernel_size=4, ngram_size=3, heads_per_ngram=2,
    ngram_vocab_size_base=29, make_ngram_vocab_size_divisible_by=8, split_ngram_parts=4,
    eos_token_id=2, indexer_n_heads=16, indexer_kv_heads=1, indexer_head_dim=16,
    indexer_budget=8, indexer_compress_ratio=4, output_gate_type="sigmoid",
    rms_norm_eps=1e-6, max_position_embeddings=4096, tie_word_embeddings=False,
    rope_parameters=dict(rope_type="default", rope_theta=10000.0, partial_rotary_factor=0.25,
                         mrope_interleaved=True, mrope_section=[11, 11, 10]))
VISION = dict(model_type="qwen4_exp_vision", depth=1, hidden_size=32, intermediate_size=64,
              num_heads=2, patch_size=4, spatial_merge_size=2, temporal_patch_size=2,
              out_hidden_size=64, num_position_embeddings=16, in_channels=3)


def tiny_model():
    from mlx_vlm.models import qwen4_exp
    mx.random.seed(0)
    cfg = qwen4_exp.ModelConfig.from_dict(dict(model_type="qwen4_exp", text_config=TEXT, vision_config=VISION,
                                               image_token_id=60, video_token_id=61,
                                               vision_start_token_id=58, vision_end_token_id=59))
    model = qwen4_exp.Model(cfg)
    mx.eval(model.parameters())
    return model


def generate(model, prompts, max_new=6):
    """mlx_vlm.generate.ar.batch_generate's text-only body with a stub processor."""
    from mlx_vlm.generate.ar import BatchGenerator, _split_prompt_kwargs_per_row
    from mlx_vlm.utils import StoppingCriteria
    width = max(map(len, prompts))
    ids = np.zeros((len(prompts), width), np.int32)
    mask = np.zeros_like(ids)
    for b, p in enumerate(prompts):
        ids[b, width - len(p):], mask[b, width - len(p):] = p, 1
    ids, mask = mx.array(ids), mx.array(mask)
    emb = model.get_input_embeddings(ids, None, mask=mask)
    kwargs = {k: v for k, v in emb.to_dict().items() if v is not None}
    proc = SimpleNamespace(tokenizer=SimpleNamespace(stopping_criteria=StoppingCriteria([10_000], None)))
    gen = BatchGenerator(model.language_model, proc, prefill_batch_size=len(prompts),
                         completion_batch_size=len(prompts), compute_logprobs=True,
                         max_tokens=max_new, manage_wired_limit=False)
    uids = gen.insert(ids, max_new, prompt_kwargs=_split_prompt_kwargs_per_row(kwargs, len(prompts)),
                      attention_mask=mask)
    out = {u: [] for u in uids}
    while gen.has_work:
        for r in gen.next()[1]:
            out[r.uid].append((r.token, r.token_logprob))
    return [out[u] for u in uids]


def main():
    if "--patched" in sys.argv:
        sys.path.insert(0, str(Path(__file__).parent))
        import d1_patch
        d1_patch.apply()
    model = tiny_model()
    rng = np.random.default_rng(1105)
    a, b = rng.integers(3, 96, 20).tolist(), rng.integers(3, 96, 17).tolist()
    single = [generate(model, [p])[0] for p in (a, b)]
    for name, prompts, refs in (("ragged [20, 17] (left pad [0, 3])", [a, b], single),
                                ("equal-length control [20, 20]", [a, a], [single[0], single[0]])):
        rows = generate(model, prompts)
        print(name)
        for r, (got, want) in enumerate(zip(rows, refs)):
            err = max(abs(g[1] - w[1]) for g, w in zip(got, want))
            print(f"  row {r}: tokens {'match' if [g[0] for g in got] == [w[0] for w in want] else 'DIFFER'}"
                  f" | max |logprob - single-request logprob| = {err:.2e}")


if __name__ == "__main__":
    main()
