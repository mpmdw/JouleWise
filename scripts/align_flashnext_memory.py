#!/usr/bin/env python3
"""Config-only Flash-Next sizing. Stdlib; never imports the staged engine."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def prime_after(start, count):
    value = start
    for _ in range(count):
        value += 1
        while value < 2 or any(value % d == 0 for d in range(2, math.isqrt(value) + 1)):
            value += 1
    return value


def components(config):
    """(quantizable matrix elements, unquantized elements) by implemented component."""
    c = config["text_config"]
    d, layers = c["hidden_size"], c["num_hidden_layers"]
    attn = c["layer_types"].count("full_attention")
    linear = layers - attn
    h, kv, hd = c["num_attention_heads"], c["num_key_value_heads"], c["head_dim"]
    ih, ik, idim = c["indexer_n_heads"], c["indexer_kv_heads"], c["indexer_head_dim"]
    kd = c["linear_num_key_heads"] * c["linear_key_head_dim"]
    vd = c["linear_num_value_heads"] * c["linear_value_head_dim"]
    nv = c["linear_num_value_heads"]
    conv = 2 * kd + vd
    hc, rank = c["hc_count"] * d, c["hc_lowrank"]
    nheads = (c["ngram_size"] - 1) * c["heads_per_ngram"]
    head_dim = c["ple_embed_dim"] // nheads
    table = 0
    for layer_index in range(len(c["ple_layer_ids"])):
        total = sum(prime_after(c["ngram_vocab_size_base"] - 1, layer_index * nheads + i + 1)
                    for i in range(nheads))
        padded = math.ceil(total / c["make_ngram_vocab_size_divisible_by"]) * c["make_ngram_vocab_size_divisible_by"]
        table += math.ceil(padded / c["split_ngram_parts"]) * c["split_ngram_parts"] * head_dim
    return {
        "routed_experts": (layers * c["num_experts"] * 3 * d * c["moe_intermediate_size"], 0),
        "shared_experts": (layers * (3 * d * c["shared_expert_intermediate_size"] + d), 0),
        "routers": (0, layers * d * c["num_experts"]),
        "attention_qsa": (attn * (d * (3 * h * hd + 2 * kv * hd) + d * (ih + ik) * idim),
                          attn * (2 * hd + 2 * idim)),
        "deltanet_weights": (linear * d * (conv + 2 * vd + 2 * nv),
                             linear * (conv * c["linear_conv_kernel_dim"] + 2 * nv + c["linear_value_head_dim"])),
        "hyper_connections": (2 * layers * (2 * hc * rank + hc * c["hc_count"]) + 2 * hc * rank,
                              (2 * layers + 1) * hc),
        "word_embedding_head": (c["vocab_size"] * d * (1 if c["tie_word_embeddings"] else 2), 0),
        "ple_projection_conv": (len(c["ple_layer_ids"]) * c["ple_embed_dim"] * (hc + d),
                                len(c["ple_layer_ids"]) * (hc * c["ple_conv_kernel_size"] + 3 * hc)),
        "ngram_table": (table, 0),
    }


def affine_bytes(elements, bits, group):
    # bf16 scale + bf16 affine bias per group. Headers/alignment not included.
    return elements * bits / 8 + math.ceil(elements / group) * 4


def estimate(config, context=40960, chunk=512, workspace_gb=12.0):
    counts = components(config)
    c = config["text_config"]
    rows = {}
    recipes = {f"q{bits}": {name: bits for name in counts} for bits in (8, 6, 4, 3)}
    for experts in (4, 3):
        for ple in (8, 4):
            recipe = {name: 8 for name in counts}
            recipe.update(routed_experts=experts, shared_experts=experts, ngram_table=ple)
            recipes[f"e{experts}_ple{ple}_other8"] = recipe
    for name, (matrix, fixed) in counts.items():
        rows[name] = {"parameters": matrix + fixed,
                      "ideal_bytes": {str(b): (matrix + fixed) * b / 8 for b in (8, 6, 4, 3)}}
    weights = {}
    for name, bits_by_component in recipes.items():
        weights[name] = sum(affine_bytes(matrix, bits_by_component[key], 32 if key == "ngram_table" else 64)
                            + fixed * (4 if key == "routers" else 2)
                            for key, (matrix, fixed) in counts.items())
    attention = c["layer_types"].count("full_attention")
    linear = c["num_hidden_layers"] - attention
    kv = attention * context * 2 * c["num_key_value_heads"] * c["head_dim"] * 2
    index = attention * context * c["indexer_kv_heads"] * c["indexer_head_dim"] * 2
    recurrent = linear * c["linear_num_value_heads"] * c["linear_value_head_dim"] * c["linear_key_head_dim"] * 4
    conv = linear * (c["linear_conv_kernel_dim"] - 1) * (2 * c["linear_num_key_heads"] * c["linear_key_head_dim"] + c["linear_num_value_heads"] * c["linear_value_head_dim"]) * 2
    ple_state = len(c["ple_layer_ids"]) * ((c["ple_conv_kernel_size"] - 1) * c["ngram_size"] * c["hc_count"] * c["hidden_size"] * 2 + (c["ngram_size"] - 1) * 8)
    state = recurrent + conv + ple_state
    return {
        "status": "STATIC_ESTIMATE_NOT_HARDWARE_VALIDATION", "units": "bytes; GB=1e9; GiB=2**30",
        "context": context, "prefill_chunk": chunk, "components": rows,
        "text_parameters": sum(a + b for a, b in counts.values()),
        "mtp_card_estimate_parameters": 4_000_000_000,
        "mtp_card_estimate_ideal_bytes": {str(b): 4_000_000_000 * b / 8 for b in (8, 6, 4, 3)},
        "mtp_resident_bytes_in_port": 0, "weight_bytes_affine": weights,
        "cache_bytes": {"kv_bf16": kv, "qsa_raw_keys_bf16": index, "delta_fp32": recurrent,
                        "delta_conv_bf16": conv, "ple_state": ple_state, "total": kv + index + state},
        "prefill_arrays_bytes": {
            "logits_bf16": chunk * c["vocab_size"] * 2,
            "qsa_head_scores_fp32": chunk * (context // c["indexer_compress_ratio"]) * c["indexer_n_heads"] * 4,
            "qsa_dense_keep_bool": chunk * context,
            "possible_attention_scores_fp32": c["num_attention_heads"] * chunk * context * 4,
        },
        "workspace_reserve_bytes_assumed": workspace_gb * 1e9,
        "planning_peak_bytes": {name: value + kv + index + state + workspace_gb * 1e9 for name, value in weights.items()},
        "gpu_working_set_bytes_supplied": 115.4e9, "physical_bytes_nominal": 128e9,
        "admission_peak_bytes_proposed": 0.9 * 115.4e9,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=Path(".engine/hf-flashnext/config.json"))
    p.add_argument("--context", type=int, default=40960)
    p.add_argument("--chunk", type=int, default=512)
    args = p.parse_args()
    if args.context < 1 or args.chunk < 1:
        p.error("context and chunk must be positive")
    print(json.dumps(estimate(json.loads(args.config.read_text()), args.context, args.chunk), indent=2))


if __name__ == "__main__":
    main()
