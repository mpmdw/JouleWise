"""Tiny random official model; deliberately exercises sparse QSA and PLE state."""


def tiny_config_dict():
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
                eos_token_id=2, indexer_n_heads=2, indexer_kv_heads=1,
                indexer_head_dim=16, indexer_budget=4, indexer_compress_ratio=2,
                output_gate_type="sigmoid",
                rope_parameters=dict(rope_type="default", rope_theta=10000., partial_rotary_factor=.25))


def reference_model(dtype="fp32"):
    import torch
    from transformers import Qwen4ExpTextConfig, Qwen4ExpForCausalLM
    torch.set_num_threads(1)
    torch.manual_seed(631)
    config = Qwen4ExpTextConfig(**tiny_config_dict())
    config._attn_implementation = "eager"
    model = Qwen4ExpForCausalLM(config).eval()
    # Default PLE conv is zero, which would conceal incorrect convolution
    # history/dilation. Nonzero norms also exercise fp32 `1 + weight` ordering.
    with torch.no_grad():
        for name, value in model.named_parameters():
            if name.endswith("ple.conv1d.weight") or ("norm" in name and ".linear_attn.norm." not in name):
                value.normal_(mean=0, std=.02)
    return model.to(torch.bfloat16 if dtype == "bf16" else torch.float32)


def write_gold(directory, dtype):
    import json
    from pathlib import Path
    import numpy as np
    import torch
    from scripts.align_convert_qwen4_exp import convert
    model = reference_model(dtype)
    directory = Path(directory)
    directory.mkdir(parents=True)
    model.save_pretrained(directory / "hf", max_shard_size="100KB")
    ids = torch.tensor([[7, 8, 9, 10, 2, 12, 13, 14, 15, 16, 17]])
    with torch.inference_mode():
        prefill = model(ids, use_cache=False).logits.float().numpy()
        cache, step = None, []
        for i in range(ids.shape[1]):
            out = model(ids[:, i:i + 1], past_key_values=cache, use_cache=True)
            cache = out.past_key_values
            step.append(out.logits.float().numpy())
        step = np.concatenate(step, axis=1)
    atol = 2e-5 if dtype == "fp32" else .004
    np.testing.assert_allclose(prefill, step, atol=atol, rtol=2e-4 if dtype == "fp32" else .02)
    np.savez(directory / "gold.npz", ids=ids.numpy(), prefill=prefill, stepwise=step)
    evidence = dict(dtype=dtype, reference_prefill_stepwise_max_abs=float(np.max(np.abs(prefill - step))),
                    parameters=sum(p.numel() for p in model.parameters()),
                    logits_shape=list(prefill.shape), torch=torch.__version__)
    (directory / "reference.json").write_text(json.dumps(evidence, indent=2) + "\n")
    convert(directory / "hf", directory / "mlx", dtype, 32, dtype)
    print(json.dumps(evidence))


if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    p = argparse.ArgumentParser()
    p.add_argument("output")
    p.add_argument("--dtype", choices=("fp32", "bf16"), default="fp32")
    a = p.parse_args()
    write_gold(a.output, a.dtype)
