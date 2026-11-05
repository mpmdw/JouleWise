"""Auditable byte accounting; this is a planning estimate, not an OOM proof."""
import argparse
import json
import math
from pathlib import Path

from joulewise.align.models.qwen4_exp_tables import parameter_shapes, ple_storage_for, quantization_for, text_config

ALIGN_CONTEXT_CAP = 40960  # scripts/align_pilot_kit.py:CONTEXT_CAP, lead ruling
GPU_WORKING_SET_BYTES = 115_400_000_000  # decimal GB; hardware constraint


class MemoryReport(dict):
    """JSON-serializable byte accounting with a caller-supplied hardware gate."""

    def fits_gpu_working_set(self, limit_bytes):
        if limit_bytes <= 0:
            raise ValueError("GPU working set limit must be positive")
        return self["resident_peak_estimate"] <= limit_bytes


def component(key):
    if ".ngram_embedding." in key:
        return "PLE table (offloaded)"
    if ".switch_mlp." in key:
        return "Routed experts"
    if ".indexer." in key:
        return "QSA indexer"
    if ".linear_attn." in key:
        return "DeltaNet"
    if ".self_attn." in key:
        return "Attention"
    if "hyper_connection" in key:
        return "Hyper connections"
    if "embed_tokens" in key or "lm_head" in key:
        return "Token embedding / head"
    if ".ple." in key:
        return "PLE projections / conv"
    if ".mlp.gate." in key or "shared_expert_gate" in key:
        return "Routers / shared gates"
    return "Shared experts"


def memory_model(config, profile="mixed", context_tokens=ALIGN_CONTEXT_CAP, chunk_tokens=64,
                 group_size=64, batch_size=1, ple_storage=None, runtime_reserve_bytes=3_000_000_000,
                 gpu_working_set_limit_bytes=GPU_WORKING_SET_BYTES):
    """Return integer component bytes and named, explicit workspace assumptions.

    Uniform bit profiles quantize eligible leaves only. The same exclusions as
    conversion apply. BF16 KV/state accounting is conservative for model weights
    but excludes speculative MTP and vision, as does the port. File-cache pages
    consume physical unified memory despite not being GPU model parameters.
    """
    if context_tokens <= 0 or chunk_tokens <= 0 or batch_size <= 0:
        raise ValueError("Context, chunk and batch must be positive")
    ple_storage = ple_storage_for(profile, group_size, ple_storage)
    c = text_config(config)
    shapes = parameter_shapes(c)
    resident, params, disk_bytes = {}, {}, 0
    table_rows, head_count = 0, 0
    for key, shape in shapes.items():
        name, n = component(key), math.prod(shape)
        params[name] = params.get(name, 0) + n
        if name == "PLE table (offloaded)":
            rows, dim = shape
            table_rows += rows
            head_count += (c.get("ngram_size", 3) - 1) * c.get("heads_per_ngram", 8)
            rowbytes = dim * {"fp32": 4, "bf16": 2, "q8": 1, "q4": .5}[ple_storage]
            if ple_storage in ("q4", "q8"):
                rowbytes += 8  # one fp32 scale and bias per row
            disk_bytes += int(rows * rowbytes)
            resident[name] = 0
            continue
        quant = quantization_for(key, shape, profile, group_size)
        bytes_ = n * (4 if profile == "fp32" else 2)
        if quant:
            bytes_ = n * quant["bits"] // 8 + n // group_size * 4  # BF16 scale + bias
        resident[name] = resident.get(name, 0) + bytes_
    types = c.get("layer_types") or ["linear_attention" if (i + 1) % c.get("full_attention_interval", 4)
                                    else "indexed_attention" for i in range(c["num_hidden_layers"])]
    full = sum(t != "linear_attention" for t in types)
    linear = len(types) - full
    b, t, s = batch_size, context_tokens, min(chunk_tokens, context_tokens)
    # The actual KVCache allocates in 256-token blocks.
    capacity = math.ceil(t / 256) * 256
    cache_dtype_bytes = 4 if profile == "fp32" else 2
    per_layer_kv = b * capacity * c["num_key_value_heads"] * c["head_dim"] * 2 * cache_dtype_bytes
    per_layer_index = b * t * c["indexer_head_dim"] * cache_dtype_bytes
    cache = dict(kv=full * per_layer_kv, qsa_raw_keys=full * per_layer_index,
                 qsa_validity=full * b * t,
                 recurrent_fp32=linear * b * c["linear_num_value_heads"] * c["linear_key_head_dim"] * c["linear_value_head_dim"] * 4,
                 delta_conv=linear * b * (c["linear_conv_kernel_dim"] - 1) *
                 (2 * c["linear_num_key_heads"] * c["linear_key_head_dim"] + c["linear_num_value_heads"] * c["linear_value_head_dim"]) * cache_dtype_bytes,
                 ple_conv=len(c.get("ple_layer_ids", [])) * b * (c["ple_conv_kernel_size"] - 1) * c.get("ngram_size", 3) * c.get("hc_count", 4) * c["hidden_size"] * cache_dtype_bytes,
                 ple_token_history=len(c.get("ple_layer_ids", [])) * b * (c.get("ngram_size", 3) - 1) * 4)
    selected = min(t, c["indexer_budget"] + c["indexer_compress_ratio"] - 1)
    blocks = t // c["indexer_compress_ratio"]
    # Both sparse K/V gathers, fp32 QSA head scores and normalized DeltaNet
    # q/k/v buffers can coexist. Reserve includes unmodelled SDPA/allocator work.
    workspace = dict(sparse_kv_gather=b * s * c["num_key_value_heads"] * selected * c["head_dim"] * 2 * cache_dtype_bytes,
                     indexer_scores=b * s * blocks * (c["indexer_n_heads"] + 1) * 4,
                     hyper_activations=4 * b * s * c["hidden_size"] * c.get("hc_count", 4) * cache_dtype_bytes,
                     delta_fp32_qkv=b * s * (2 * c["linear_num_key_heads"] * c["linear_key_head_dim"] + c["linear_num_value_heads"] * c["linear_value_head_dim"]) * 4,
                     expert_activations=4 * b * s * c["num_experts_per_tok"] * c["moe_intermediate_size"] * cache_dtype_bytes,
                     kv_growth_copy=per_layer_kv + per_layer_index if full else 0,
                     ple_gather_fp32=2 * b * s * c.get("ple_embed_dim", c["hidden_size"]) * 4 if table_rows else 0,
                     runtime_reserve=runtime_reserve_bytes)
    weights = sum(resident.values())
    peak = weights + sum(cache.values()) + sum(workspace.values())
    # Assuming uniform random row accesses provides an illustrative expectation,
    # never a hard residency cap. Worst bound includes cross-page rows.
    pages = math.ceil(disk_bytes / 16384) if disk_bytes else 0
    lookups = b * t * head_count
    expected_pages = pages * -math.expm1(-lookups / pages) if pages else 0
    report = MemoryReport(profile=profile, ple_storage=ple_storage,
                context_tokens=t, chunk_tokens=s, batch_size=b,
                parameter_counts=params, resident_by_component=resident, weights_resident=weights,
                state_bytes=cache, workspace_bytes=workspace, resident_peak_estimate=peak,
                gpu_working_set_limit_bytes=gpu_working_set_limit_bytes,
                gpu_working_set_headroom_bytes=gpu_working_set_limit_bytes - peak,
                ple_disk_bytes=disk_bytes, ple_page_cache_uniform_estimate=int(expected_pages * 16384),
                ple_page_cache_upper_bound=min(disk_bytes, lookups * 2 * 16384),
                physical_peak_upper_estimate=peak + min(disk_bytes, lookups * 2 * 16384),
                caveat="No swap guarantee: validate actual peaks, OS headroom and swap counters on target Mac; file pages are physical memory.")
    report["fits_gpu_working_set"] = report.fits_gpu_working_set(gpu_working_set_limit_bytes)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("config", type=Path)
    p.add_argument("--chunk-tokens", type=int, default=64)
    p.add_argument("--gpu-working-set-bytes", type=int, default=GPU_WORKING_SET_BYTES)
    a = p.parse_args()
    config = json.loads(a.config.read_text())
    print(json.dumps({profile: memory_model(config, profile, chunk_tokens=a.chunk_tokens,
                                           gpu_working_set_limit_bytes=a.gpu_working_set_bytes)
                      for profile in ("8", "6", "4", "3", "mixed", "maxfit", "maxfit5")}, indent=2))


if __name__ == "__main__":
    main()
