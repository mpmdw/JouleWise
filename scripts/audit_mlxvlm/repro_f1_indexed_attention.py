"""Minimal reproducer, mlx-vlm 0.7.12 + transformers 5.22.1: any Qwen3.8-Flash-
Next checkpoint re-saved by transformers (fine-tune, merge, tiny test model)
fails to load in mlx-vlm, because Qwen4ExpTextConfig normalizes the
checkpoint's "full_attention" layer type to "indexed_attention" and writes
that on save_pretrained, while mlx-vlm's TextConfig only maps "full_attention".
Fails loudly (ValueError); the official checkpoint is unaffected.
Patch draft: f1_indexed_attention_layer_type.patch.

  python repro_f1_indexed_attention.py OUT_DIR
"""
import json
import sys
from pathlib import Path


def main(out):
    import torch
    from transformers import Qwen4ExpConfig, Qwen4ExpForConditionalGeneration
    text = dict(vocab_size=64, hidden_size=64, num_hidden_layers=2, num_attention_heads=2,
                num_key_value_heads=1, head_dim=32, hc_count=2, hc_lowrank=8, linear_key_head_dim=32,
                linear_value_head_dim=32, linear_num_key_heads=1, linear_num_value_heads=2,
                moe_intermediate_size=64, shared_expert_intermediate_size=64, num_experts=4,
                num_experts_per_tok=2, layer_types=["linear_attention", "full_attention"],
                ple_layer_ids=[1], ple_embed_dim=64, heads_per_ngram=2, ngram_vocab_size_base=17,
                make_ngram_vocab_size_divisible_by=8, split_ngram_parts=4, eos_token_id=2,
                indexer_n_heads=2, indexer_kv_heads=1, indexer_head_dim=16, indexer_budget=4,
                indexer_compress_ratio=2, linear_conv_kernel_dim=3, ple_conv_kernel_size=2, ngram_size=3,
                rope_parameters=dict(rope_type="default", rope_theta=1e4, partial_rotary_factor=.25,
                                     mrope_section=[11, 11, 10]))
    vision = dict(depth=1, hidden_size=32, intermediate_size=64, num_heads=2, patch_size=4,
                  out_hidden_size=64, num_position_embeddings=16)
    torch.manual_seed(0)
    Qwen4ExpForConditionalGeneration(Qwen4ExpConfig(text_config=text, vision_config=vision)).save_pretrained(out)
    print("saved layer_types:", json.loads((Path(out) / "config.json").read_text())["text_config"]["layer_types"])
    from mlx_vlm.utils import load_model
    try:
        load_model(Path(out))
        print("mlx-vlm: loaded")
    except ValueError as e:
        print("mlx-vlm:", type(e).__name__, e)


if __name__ == "__main__":
    main(sys.argv[1])
