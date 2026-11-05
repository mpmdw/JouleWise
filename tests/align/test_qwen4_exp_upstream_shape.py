"""Upstream-shaped tests for an MLX ``qwen4_exp`` (Qwen3.8-Flash-Next) port.

These tests are written in the style of ml-explore/mlx-lm's ``tests/test_models.py``
and ``tests/models/test_<model>.py`` so they can move upstream with minimal edits.
See ``docs/align/qwen4_exp_port/upstream.md`` for the porting checklist.

Module under test (pluggable)
-----------------------------
Set ``JW_QWEN4_EXP_MODULE`` to either

* a dotted module name (default: ``mlx_lm.models.qwen4_exp``), or
* a path to a ``.py`` file exposing mlx-lm's model-file interface
  (``ModelArgs``, ``Model``), as loaded by mlx-lm's ``model_file`` hook.

With the variable unset and no ``mlx_lm.models.qwen4_exp`` installed, the MLX
tests skip. With the variable set, an import failure is an error, not a skip.
Without MLX or NumPy (the JouleWise CI image) everything that needs them skips.

What the tests pin
------------------
* ``TINY_CONFIG`` is the official ``config.json`` shape (nested ``text_config``,
  ``layer_types`` with ``full_attention``, no ``seed`` key) shrunk to a tiny
  model that still has every layer type: Gated DeltaNet, QSA with its indexer
  (budget 8, blocks of 4, so selection is active at the pinned lengths),
  4 hyper-connection streams, a routed + shared MoE, and one n-gram PLE layer.
  All dimensions differ from each other so transposition bugs cannot hide.
* ``hf_checkpoint`` builds closed-form weights in the official checkpoint
  layout (``model.language_model.`` prefix, fused experts, ``shard_N`` n-gram
  parts, hash-constant buffers, zero-centred norms, ``mtp.*`` and
  ``model.visual.*`` extras). The values come from a counter-based hash, so
  NumPy, MLX and Torch see bit-identical float32 inputs.
* ``REFERENCE`` holds logits from the official transformers 5.22.1
  ``Qwen4ExpForCausalLM`` on those weights, written by
  ``scripts/align_qwen4_exp_upstream_pin.py``. The upstream version of this
  file keeps the closed-form generator and the pinned numbers, so mlx-lm CI
  needs neither Torch nor a download.

Upstream porting notes: drop the module-loader shim and the import guards,
use ``from mlx_lm.models import qwen4_exp``, call
``test_models.TestModels.model_test_runner`` instead of the local copy, and
add ``UPSTREAM_TEST_ALL_MODELS_ENTRY`` to ``test_all_models``.
"""

import copy
import importlib
import importlib.util
import math
import os
import tempfile
import unittest
import zlib
from pathlib import Path

try:
    import numpy as np
except ImportError:  # JouleWise core CI is stdlib-only.
    np = None

try:
    import mlx.core as mx
    import mlx.nn as nn
    from mlx.utils import tree_flatten, tree_map

    from mlx_lm.models.cache import (
        ArraysCache,
        BatchKVCache,
        CacheList,
        KVCache,
        can_trim_prompt_cache,
        load_prompt_cache,
        make_prompt_cache,
        save_prompt_cache,
        trim_prompt_cache,
    )
    from mlx_lm.utils import load_model, quantize_model, save_config, save_model
except ImportError:
    mx = None

MODULE_ENV = "JW_QWEN4_EXP_MODULE"
DEFAULT_MODULE = "mlx_lm.models.qwen4_exp"

# fp32 gate from GOAL item 2: max abs logit difference <= 1e-4.
ATOL = 1e-4
RTOL = 1e-4

# ---------------------------------------------------------------------------
# Tiny configuration in the official config.json shape.
# ---------------------------------------------------------------------------

TINY_TEXT_CONFIG = {
    "model_type": "qwen4_exp_text",
    "vocab_size": 128,
    "hidden_size": 64,
    "num_hidden_layers": 4,
    "num_attention_heads": 4,
    "num_key_value_heads": 2,
    "head_dim": 16,
    "hidden_act": "silu",
    "rms_norm_eps": 1e-6,
    "tie_word_embeddings": False,
    "attention_bias": False,
    "max_position_embeddings": 1024,
    "rope_parameters": {
        "rope_type": "default",
        "rope_theta": 10000.0,
        "partial_rotary_factor": 0.5,
        "mrope_section": [2, 1, 1],
        "mrope_interleaved": True,
    },
    "partial_rotary_factor": 0.5,
    "full_attention_interval": 4,
    "layer_types": [
        "linear_attention",
        "linear_attention",
        "linear_attention",
        "full_attention",
    ],
    "linear_conv_kernel_dim": 4,
    "linear_key_head_dim": 16,
    "linear_value_head_dim": 24,
    "linear_num_key_heads": 2,
    "linear_num_value_heads": 4,
    "moe_intermediate_size": 32,
    "shared_expert_intermediate_size": 48,
    "num_experts": 8,
    "num_experts_per_tok": 2,
    "hc_count": 4,
    "hc_lowrank": 12,
    # One-indexed, as in the official config ([2] means decoder index 1).
    "ple_layer_ids": [2],
    "ple_embed_dim": 128,
    "ple_conv_kernel_size": 4,
    "ngram_size": 3,
    "heads_per_ngram": 2,
    "ngram_vocab_size_base": 97,
    "make_ngram_vocab_size_divisible_by": 8,
    "split_ngram_parts": 4,
    "indexer_n_heads": 4,
    "indexer_kv_heads": 1,
    "indexer_head_dim": 16,
    "indexer_budget": 8,
    "indexer_compress_ratio": 4,
    "output_gate_type": "sigmoid",
    "mamba_ssm_dtype": "float32",
    "mtp_num_hidden_layers": 1,
    "bos_token_id": 1,
    "eos_token_id": 1,
    # No "seed": like the official config, the reference default (1234) applies.
}

TINY_CONFIG = {
    "model_type": "qwen4_exp",
    "architectures": ["Qwen4ExpForConditionalGeneration"],
    "tie_word_embeddings": False,
    "image_token_id": 120,
    "video_token_id": 121,
    "vision_start_token_id": 122,
    "vision_end_token_id": 123,
    "text_config": TINY_TEXT_CONFIG,
    # The official file labels the vision tower "qwen4_exp" too; text ports
    # must ignore it.
    "vision_config": {"model_type": "qwen4_exp", "depth": 1, "hidden_size": 8},
}

# The entry to append to upstream's test_all_models list.
UPSTREAM_TEST_ALL_MODELS_ENTRY = {
    "model_type": "qwen4_exp",
    "vocab_size": 128,
    "num_hidden_layers": 4,
    "text_config": TINY_TEXT_CONFIG,
}

# The official real config, for the hash-constant cross-check only.
REAL_NGRAM_TEXT_CONFIG = {
    "vocab_size": 248320,
    "ngram_size": 3,
    "heads_per_ngram": 8,
    "ngram_vocab_size_base": 20000000,
    "make_ngram_vocab_size_divisible_by": 128,
    "ple_layer_ids": [2],
}

ZERO_CENTERED_NORM_SUFFIXES = (
    "hc_norm.weight",
    "self_attn.q_norm.weight",
    "self_attn.k_norm.weight",
    "indexer.q_layernorm.weight",
    "indexer.k_layernorm.weight",
    "ple.norm_key.weight",
    "ple.norm_query.weight",
    "ple.norm_conv.weight",
)

# ---------------------------------------------------------------------------
# Reference n-gram hash constants (pure Python transcription of
# transformers' modeling_qwen4_exp.py; the pin script checks it against the
# installed reference module for both the tiny and the real config).
# ---------------------------------------------------------------------------

_MASK64 = (1 << 64) - 1
_SPLITMIX_GAMMA = 0x9E3779B97F4A7C15
_SPLITMIX_M1 = 0xBF58476D1CE4E5B9
_SPLITMIX_M2 = 0x94D049BB133111EB
_PRIME_1 = 10007
_REFERENCE_SEED_DEFAULT = 1234


def _splitmix64(value):
    value = (value + _SPLITMIX_GAMMA) & _MASK64
    value = ((value ^ (value >> 30)) * _SPLITMIX_M1) & _MASK64
    value = ((value ^ (value >> 27)) * _SPLITMIX_M2) & _MASK64
    return (value ^ (value >> 31)) & _MASK64


def _is_prime(value):
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    for divisor in range(3, math.isqrt(value) + 1, 2):
        if value % divisor == 0:
            return False
    return True


def _nth_prime_after(start, count):
    prime = start
    for _ in range(count):
        prime += 1
        while not _is_prime(prime):
            prime += 1
    return prime


def ngram_constants(text_config, ple_layer_index, seed=None):
    """Return the reference hash constants for one PLE layer."""
    seed = text_config.get("seed", _REFERENCE_SEED_DEFAULT) if seed is None else seed
    vocab = text_config["vocab_size"]
    ngram_size = text_config["ngram_size"]
    heads = (ngram_size - 1) * text_config["heads_per_ngram"]
    half_bound = max(1, (((1 << 63) - 1) // max(vocab, 1)) // 2)
    base_seed = seed + _PRIME_1 * ple_layer_index
    multipliers = []
    for i in range(ngram_size):
        mixed = _splitmix64((base_seed + _SPLITMIX_GAMMA * (i + 1)) & _MASK64)
        multipliers.append(2 * (mixed % half_bound) + 1)
    sizes, offsets, total = [], [], 0
    for head in range(heads):
        size = _nth_prime_after(
            text_config["ngram_vocab_size_base"] - 1, ple_layer_index * heads + head + 1
        )
        sizes.append(size)
        offsets.append(total)
        total += size
    divisor = text_config["make_ngram_vocab_size_divisible_by"]
    padded_rows = -(-total // divisor) * divisor
    return {
        "layer_multipliers": multipliers,
        "vocab_sizes": sizes,
        "offsets": offsets,
        "padded_rows": padded_rows,
    }


# ---------------------------------------------------------------------------
# Closed-form checkpoint in the official layout.
# ---------------------------------------------------------------------------


def _uniform(name, size):
    """Counter-based U[-1, 1) values keyed by tensor name (float64)."""
    key = np.uint64(zlib.crc32(name.encode("utf-8")))
    x = np.arange(size, dtype=np.uint64) + (key << np.uint64(32))
    x = x + np.uint64(_SPLITMIX_GAMMA)
    x = (x ^ (x >> np.uint64(30))) * np.uint64(_SPLITMIX_M1)
    x = (x ^ (x >> np.uint64(27))) * np.uint64(_SPLITMIX_M2)
    x = x ^ (x >> np.uint64(31))
    return (x >> np.uint64(11)).astype(np.float64) * (2.0**-52) - 1.0


def _closed_form(name, shape):
    u = _uniform(name, int(np.prod(shape))).reshape(shape)
    fan_in = shape[-1] if len(shape) > 1 else 1
    if name.endswith("linear_attn.norm.weight"):
        values = 1.0 + 0.2 * u  # RMSNormGated: conventional, ones-centred
    elif name.endswith(ZERO_CENTERED_NORM_SUFFIXES):
        values = 0.2 * u  # zero-centred: the model applies (1 + w)
    elif name.endswith("A_log"):
        values = np.log(4.5 + 3.5 * u)
    elif name.endswith("dt_bias"):
        values = 0.5 * u
    elif name.endswith("conv1d.weight"):
        values = 0.5 * u
    elif name.endswith("embed_tokens.weight") or "ngram_embedding" in name:
        values = math.sqrt(3.0) * u
    elif name.endswith("mlp.gate.weight"):
        values = 3.0 * math.sqrt(3.0 / fan_in) * u  # decisive routing
    else:
        values = math.sqrt(3.0 / fan_in) * u
    return values.astype(np.float32)


def _layer_types(text):
    if text.get("layer_types") is not None:
        return [
            "linear_attention" if t == "linear_attention" else "full_attention"
            for t in text["layer_types"]
        ]
    interval = text.get("full_attention_interval", 4)
    return [
        "linear_attention" if (i + 1) % interval else "full_attention"
        for i in range(text["num_hidden_layers"])
    ]


def hf_checkpoint(config=None, layout="official", seed=None):
    """Weights as a Hugging Face checkpoint stores them, as NumPy arrays.

    ``layout="official"`` mirrors ``Qwen/Qwen3.8-Flash-Next`` (fused experts,
    ``model.language_model.`` prefix, MTP and vision extras).
    ``layout="save_pretrained"`` mirrors ``Qwen4ExpForCausalLM.save_pretrained``
    (per-expert projections, ``model.`` prefix, no extras). Both layouts carry
    bit-identical values. ``seed`` overrides the seed used for the stored
    hash-constant buffers (to build deliberately inconsistent checkpoints).
    """
    config = TINY_CONFIG if config is None else config
    text = config.get("text_config", config)
    official = layout == "official"
    if layout not in ("official", "save_pretrained"):
        raise ValueError(layout)
    canon = "model.language_model."
    prefix = canon if official else "model."
    H = text["hidden_size"]
    C = text["hc_count"]
    CH = C * H
    R = text["hc_lowrank"]
    V = text["vocab_size"]
    hd = text["head_dim"]
    nh = text["num_attention_heads"]
    nkv = text["num_key_value_heads"]
    Hk, Dk = text["linear_num_key_heads"], text["linear_key_head_dim"]
    Hv, Dv = text["linear_num_value_heads"], text["linear_value_head_dim"]
    K = text["linear_conv_kernel_dim"]
    E, I = text["num_experts"], text["moe_intermediate_size"]
    S = text["shared_expert_intermediate_size"]
    ih, ihd = text["indexer_n_heads"], text["indexer_head_dim"]
    ikv = text["indexer_kv_heads"]
    Dp = text.get("ple_embed_dim") or H
    ple_ids = sorted(set(text.get("ple_layer_ids") or []))
    heads = (text["ngram_size"] - 1) * text["heads_per_ngram"]

    out = {}

    def add(rel, shape):
        # Values are keyed by the canonical (official) name in every layout.
        out[prefix + rel] = _closed_form(canon + rel, shape)

    add("embed_tokens.weight", (V, H))
    for part in ("hyper_connection_mixer",):
        add(f"{part}.hc_norm.weight", (CH,))
        add(f"{part}.input_mix_weight_down.weight", (R, CH))
        add(f"{part}.input_mix_weight_up.weight", (CH, R))

    for i, kind in enumerate(_layer_types(text)):
        p = f"layers.{i}."
        for hc in ("attn_hyper_connection", "mlp_hyper_connection"):
            add(p + f"{hc}.hc_norm.weight", (CH,))
            add(p + f"{hc}.input_mix_weight_down.weight", (R, CH))
            add(p + f"{hc}.input_mix_weight_up.weight", (CH, R))
            add(p + f"{hc}.block_inject_weight.weight", (C, CH))
        if kind == "linear_attention":
            conv_dim = 2 * Hk * Dk + Hv * Dv
            add(p + "linear_attn.A_log", (Hv,))
            add(p + "linear_attn.dt_bias", (Hv,))
            add(p + "linear_attn.conv1d.weight", (conv_dim, 1, K))
            add(p + "linear_attn.in_proj_qkv.weight", (conv_dim, H))
            add(p + "linear_attn.in_proj_z.weight", (Hv * Dv, H))
            add(p + "linear_attn.in_proj_a.weight", (Hv, H))
            add(p + "linear_attn.in_proj_b.weight", (Hv, H))
            add(p + "linear_attn.norm.weight", (Dv,))
            add(p + "linear_attn.out_proj.weight", (H, Hv * Dv))
        else:
            add(p + "self_attn.q_proj.weight", (2 * nh * hd, H))
            add(p + "self_attn.k_proj.weight", (nkv * hd, H))
            add(p + "self_attn.v_proj.weight", (nkv * hd, H))
            add(p + "self_attn.o_proj.weight", (H, nh * hd))
            add(p + "self_attn.q_norm.weight", (hd,))
            add(p + "self_attn.k_norm.weight", (hd,))
            add(p + "self_attn.indexer.index_qk_proj.weight", ((ih + ikv) * ihd, H))
            add(p + "self_attn.indexer.q_layernorm.weight", (ihd,))
            add(p + "self_attn.indexer.k_layernorm.weight", (ihd,))

        # MoE: official layout is fused, save_pretrained is per expert.
        gate_up = _closed_form(canon + p + "mlp.experts.gate_up_proj", (E, 2 * I, H))
        down = _closed_form(canon + p + "mlp.experts.down_proj", (E, H, I))
        if official:
            out[prefix + p + "mlp.experts.gate_up_proj"] = gate_up
            out[prefix + p + "mlp.experts.down_proj"] = down
        else:
            for e in range(E):
                q = prefix + p + f"mlp.experts.{e}."
                out[q + "gate_proj.weight"] = np.ascontiguousarray(gate_up[e, :I])
                out[q + "up_proj.weight"] = np.ascontiguousarray(gate_up[e, I:])
                out[q + "down_proj.weight"] = np.ascontiguousarray(down[e])
        add(p + "mlp.gate.weight", (E, H))
        add(p + "mlp.shared_expert.gate_proj.weight", (S, H))
        add(p + "mlp.shared_expert.up_proj.weight", (S, H))
        add(p + "mlp.shared_expert.down_proj.weight", (H, S))
        add(p + "mlp.shared_expert_gate.weight", (1, H))

        if (i + 1) in ple_ids:
            ple_index = ple_ids.index(i + 1)
            consts = ngram_constants(text, ple_index, seed=seed)
            q = p + "ple."
            add(q + "conv1d.weight", (CH, 1, text["ple_conv_kernel_size"]))
            add(q + "key_proj.weight", (CH, Dp))
            add(q + "value_proj.weight", (H, Dp))
            add(q + "norm_key.weight", (CH,))
            add(q + "norm_query.weight", (CH,))
            add(q + "norm_conv.weight", (CH,))
            e = prefix + q + "ple_embedding."
            out[e + "layer_multipliers"] = np.array(
                consts["layer_multipliers"], dtype=np.int64
            )
            out[e + "ngram_heads_vocab_sizes"] = np.array(
                consts["vocab_sizes"], dtype=np.int64
            )
            out[e + "ngram_heads_offsets"] = np.array(consts["offsets"], dtype=np.int64)
            rows = consts["padded_rows"]
            table = _closed_form(
                canon + q + "ple_embedding.ngram_embedding.weight", (rows, Dp // heads)
            )
            # torch.chunk partitioning, as save_pretrained writes it.
            parts = text["split_ngram_parts"]
            step = -(-rows // parts)
            for j, start in enumerate(range(0, rows, step)):
                out[e + f"ngram_embedding.shard_{j}.weight"] = np.ascontiguousarray(
                    table[start : start + step]
                )

    out["lm_head.weight"] = _closed_form("lm_head.weight", (V, H))
    if official:
        out["mtp.fc_hidden.weight"] = _closed_form("mtp.fc_hidden.weight", (H, 2 * H))
        out["mtp.layers.0.mlp.experts.gate_up_proj"] = _closed_form(
            "mtp.layers.0.mlp.experts.gate_up_proj", (E, 2 * I, H)
        )
        out["mtp.pre_fc_norm_hidden.weight"] = _closed_form(
            "mtp.pre_fc_norm_hidden.weight", (H,)
        )
        out["model.visual.patch_embed.proj.weight"] = _closed_form(
            "model.visual.patch_embed.proj.weight", (8, 3, 2, 2, 2)
        )
        out["model.visual.merger.norm.weight"] = _closed_form(
            "model.visual.merger.norm.weight", (8,)
        )
    return out


# Two rows, no padding. Row 0 has EOS (id 1) inside; row 1 repeats an n-gram
# and contains token 0. 21 tokens give 5 complete QSA blocks > budget/ratio (2).
REFERENCE_INPUT_IDS = [
    [5, 17, 99, 42, 3, 64, 1, 23, 77, 8, 120, 56, 31, 1, 90, 12, 45, 67, 2, 88, 101],
    [9, 33, 33, 70, 14, 9, 33, 33, 70, 0, 126, 51, 7, 19, 84, 62, 27, 115, 40, 73, 6],
]
REFERENCE_VOCAB_IDS = [0, 1, 7, 33, 64, 90, 101, 127]

# BEGIN PINNED REFERENCE (generated by scripts/align_qwen4_exp_upstream_pin.py)
REFERENCE = {'provenance': {'transformers': '5.22.1',
                'torch': '2.15.0',
                'modeling_qwen4_exp_sha256': 'e57b3617e71e81ecb7e5ae3b420c45b5aee80d76a07aa8c88b797c2642f1f5df',
                'configuration_qwen4_exp_sha256': 'bb1d71db625fb50d1bf86589032edaa9c0f00f8ba2b9f1d06946aa0a8eeae246',
                'generator_sha256': 'a608ef6c209b4baccf937f9233c128251a001ee689da89a8277056a7b48bf8bf',
                'dtype': 'float32',
                'attn_implementation': 'sdpa (eager max diff 3.58e-07)',
                'reference_stepwise_vs_prefill_max_abs': 1.773238182067871e-06,
                'from_pretrained_vs_direct_load_max_abs': 0.0,
                'min_router_topk_logit_gap': 0.008906364440917969,
                'min_qsa_block_score_gap': 0.10110408067703247,
                'qsa_selecting_queries': 20},
 'input_ids': [[5, 17, 99, 42, 3, 64, 1, 23, 77, 8, 120, 56, 31, 1, 90, 12, 45, 67, 2,
                88, 101],
               [9, 33, 33, 70, 14, 9, 33, 33, 70, 0, 126, 51, 7, 19, 84, 62, 27, 115,
                40, 73, 6]],
 'vocab_ids': [0, 1, 7, 33, 64, 90, 101, 127],
 'logits': [[[0.3525788, -0.08709206, 0.6449621, -0.6982834, -0.3100621, 0.367404,
              -0.7728213, -0.4247083],
             [0.1350634, -1.11557, -0.2532695, -0.2739548, -0.4830374, -0.04752972,
              -0.04636464, -0.01975056],
             [0.6128794, 1.078462, -0.334103, -0.1536275, -0.619514, -0.01348944,
              -0.5819005, -0.0911234],
             [-0.1490427, -0.2955832, -0.1545161, 0.469295, 0.1902096, 0.295976,
              -0.1107066, 0.1785304],
             [-0.2099268, -0.5255039, -0.5704639, -0.1484981, -0.4963005, 0.3270082,
              0.3734899, 0.01155787],
             [-0.3661765, 0.103118, 0.305566, 0.9775214, 0.3203176, 0.2958136,
              -0.8487842, -1.186995],
             [-0.6689327, 0.09256381, 0.3387513, 0.3890346, -0.3724011, -0.007981387,
              -0.1227732, -0.08907794],
             [0.4629744, -0.05085471, 0.02162838, -0.6777655, -0.3633947, -0.3136994,
              -0.3157598, 0.280441],
             [0.5312294, 0.5107451, -0.8144217, 0.06428132, 0.4624333, 0.002941534,
              -1.050111, -0.4549998],
             [-0.6153511, 0.1005186, -0.2911842, -0.5939156, -0.8916038, 0.4936389,
              -0.305989, -0.5628577],
             [-0.1960997, -0.2783303, -0.4501962, -0.4590923, 0.5476949, -0.7140824,
              0.6092164, -0.1990457],
             [-0.2861657, -0.03871094, -0.005447918, 0.3079716, -0.0100858, 0.5501046,
              0.2154482, 0.2084847],
             [0.8895896, 0.650203, -0.697231, -0.4328058, 0.2537636, -0.3599312,
              0.149524, 0.1950096],
             [-0.4574668, -0.04454194, -0.04022167, -0.4448255, -0.3854316, 0.5404946,
              -0.4751047, -1.110663],
             [-0.4677535, -1.030302, 0.1640774, -0.2910018, 0.8075969, 0.02951233,
              0.606274, -0.08512612],
             [-0.01166418, -0.6204461, -0.09742436, 0.4800635, -0.1924362, 0.7384548,
              -0.6990893, 0.5233688],
             [0.2433162, 0.03174309, -0.2146644, 0.180614, 1.09661, -0.2655169,
              0.1853047, -0.4593526],
             [-0.08068004, 0.04182423, -0.4461737, 0.5085711, -0.9149849, 0.1425497,
              0.4488189, 0.008590366],
             [0.04339315, 0.2521649, -0.3380848, 0.1362781, 0.09625562, 0.5069343,
              -0.5212758, 0.1246604],
             [0.4365, 0.06059433, -0.2804361, 0.1681884, 0.2169514, 0.1865439,
              -0.4616427, 0.1640922],
             [0.4212371, -0.5021541, 1.028832, 0.1376146, 0.5598946, 0.4148762,
              -0.2165289, -0.04197538]],
            [[0.1546998, -0.4205677, 0.6306675, 0.2643146, 0.2134077, 0.366388,
              0.3206134, 0.2505886],
             [0.142992, 0.7437269, -0.319993, 0.05680477, 0.7631557, 0.5477344,
              -0.9232705, 0.1831013],
             [0.3314957, 0.1965085, -0.5849224, -0.2966885, -0.1006881, -0.09673713,
              -0.8892165, 0.6645668],
             [-0.3904641, -0.4216034, -0.3538385, 0.3652128, 0.1686496, -0.1666067,
              0.1541042, 0.65648],
             [0.6722142, -0.03439596, 0.4363242, 0.4051048, -0.02125071, -0.787517,
              -0.3418166, -0.06810649],
             [0.09589969, -0.2566811, 0.7559553, -0.5451524, -0.2875651, 0.8614411,
              0.6312935, 0.4882549],
             [0.5914829, 0.6655237, 0.310369, 0.3915636, 0.2043419, 1.210121,
              -0.9461983, -0.1479663],
             [0.1116557, 0.9205245, -0.337732, -0.2860793, -0.107203, 0.2109526,
              -1.108406, 0.7750973],
             [-0.360918, -0.4106045, -0.1005693, 0.5079598, 0.1155236, 0.1332972,
              0.1719874, 0.3715496],
             [-0.3310588, 0.2169655, 0.3623642, 1.003229, 0.4275089, -0.04582854,
              0.2459442, 0.1982052],
             [0.9860346, -0.5425732, 0.5418484, -0.2166999, 0.4840783, 0.309832,
              -0.05556846, -0.3414867],
             [0.4788615, 0.5266258, 0.234502, -0.5185046, -0.7766533, -0.2535754,
              -0.2541225, -0.01705237],
             [-0.2722284, 0.4166624, 0.05554335, 0.8232278, 0.3695269, 0.561344,
              0.3036799, 0.08481365],
             [0.02454344, -0.04630095, 0.2106532, 0.6805736, 0.1101582, -0.3530636,
              0.5561938, 0.6043264],
             [0.1996397, 0.6982463, -0.2885444, 0.109097, 0.3721292, 0.05162604,
              -0.4632815, -0.1719074],
             [0.1333043, 0.1729671, 0.5936559, 0.70317, 0.3115383, -0.3885424,
              0.4957693, 0.2530728],
             [-0.673857, -0.5961928, 0.1119928, -0.08922746, 0.1222557, 0.1572482,
              -0.1583621, 0.594779],
             [0.06147056, 0.8023459, -0.6340524, 0.1720507, 0.06095453, 0.03607376,
              -0.858566, -0.07060462],
             [-0.1048442, 0.1186334, 0.7162624, 0.3883978, 0.8256792, 0.0018653,
              0.4280308, -0.3475475],
             [0.08027747, -0.375576, -0.2795864, 0.208266, -0.04511984, 0.5684759,
              -0.240714, -1.027441],
             [-0.9843798, -0.2744515, -0.4542764, 0.1713296, 0.09761073, -0.2185654,
              0.6783972, 0.4751422]]],
 'logsumexp': [[4.939741, 4.942393, 5.005742, 5.012982, 4.974848, 5.011926, 4.973127,
                4.940578, 4.951208, 4.969368, 4.94404, 5.013446, 4.962634, 4.986372,
                4.938561, 4.937277, 4.935587, 5.033797, 4.967473, 4.914308, 4.996457],
               [4.975022, 5.011005, 5.002608, 4.92694, 4.952383, 4.96449, 4.978754,
                4.997649, 4.911016, 5.012576, 5.021054, 5.011729, 5.009664, 4.970279,
                4.919714, 4.977487, 4.931886, 4.960449, 5.006301, 4.969456, 5.033336]],
 'argmax': [[124, 39, 9, 28, 39, 38, 88, 60, 24, 37, 53, 94, 27, 75, 73, 74, 5, 86, 70,
             77, 13],
            [121, 107, 79, 81, 94, 126, 107, 79, 81, 92, 95, 103, 102, 14, 69, 62, 5,
             14, 20, 107, 11]],
 'top2_margin': [[0.3935, 0.127, 0.1693, 0.162, 0.1377, 0.1919, 0.05074, 0.1842, 0.1244,
                  0.5089, 0.3071, 0.1501, 0.1049, 0.06396, 0.06068, 0.0003471, 0.1426,
                  0.07305, 0.03666, 0.08899, 0.06904],
                 [0.3141, 0.3968, 0.3404, 0.06796, 0.03327, 0.03663, 0.3079, 0.3432,
                  0.1478, 0.1736, 0.2689, 0.009277, 0.1066, 0.2037, 0.15, 0.188,
                  0.06509, 0.187, 0.1996, 0.159, 0.5219]],
 'tiny_ngram_constants': {'layer_multipliers': [40323955908725927, 35454616657218691,
                                                55314113489879455],
                          'vocab_sizes': [97, 101, 103, 107],
                          'offsets': [0, 97, 198, 301],
                          'padded_rows': 408},
 'real_ngram_constants': {'layer_multipliers': [23703573157769, 20109073645365,
                                                8052911324071],
                          'vocab_sizes': [20000003, 20000023, 20000033, 20000047,
                                          20000059, 20000063, 20000069, 20000077,
                                          20000081, 20000093, 20000107, 20000147,
                                          20000153, 20000159, 20000161, 20000171],
                          'offsets': [0, 20000003, 40000026, 60000059, 80000106,
                                      100000165, 120000228, 140000297, 160000374,
                                      180000455, 200000548, 220000655, 240000802,
                                      260000955, 280001114, 300001275],
                          'padded_rows': 320001536}}
# END PINNED REFERENCE


# ---------------------------------------------------------------------------
# Module loading (JouleWise shim; upstream: ``from mlx_lm.models import qwen4_exp``).
# ---------------------------------------------------------------------------

_ARCH = None


def _load_arch():
    global _ARCH
    if _ARCH is not None:
        return _ARCH
    if np is None or mx is None:
        raise unittest.SkipTest("MLX and NumPy are required")
    target = os.environ.get(MODULE_ENV)
    if not target:
        try:
            _ARCH = importlib.import_module(DEFAULT_MODULE)
        except ImportError:
            raise unittest.SkipTest(
                f"{DEFAULT_MODULE} is not installed; set {MODULE_ENV} to a port"
            )
        return _ARCH
    if target.endswith(".py") or os.sep in target:
        path = Path(target).expanduser().resolve()
        spec = importlib.util.spec_from_file_location("qwen4_exp_under_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _ARCH = module
    else:
        _ARCH = importlib.import_module(target)
    return _ARCH


def _logsumexp(x, axis=-1):
    m = np.max(x, axis=axis, keepdims=True)
    return (m + np.log(np.sum(np.exp(x - m), axis=axis, keepdims=True))).squeeze(axis)


def _np(a):
    return np.array(a.astype(mx.float32), dtype=np.float64)


def _cosine(a, b):
    a, b = a.reshape(-1), b.reshape(-1)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def _iter_caches(cache):
    for c in cache:
        if isinstance(c, CacheList):
            yield from _iter_caches(c.caches)
        else:
            yield c


def _to_batch_cache(c, left_padding):
    # Mirrors mlx_lm.generate._make_cache (0.31.x); main batches via merge().
    if type(c) is KVCache:
        return BatchKVCache(left_padding)
    if isinstance(c, ArraysCache):
        c.left_padding = mx.array(left_padding)
        return c
    if isinstance(c, CacheList):
        return CacheList(*(_to_batch_cache(s, left_padding) for s in c.caches))
    raise ValueError(f"{type(c).__name__} does not yet support batching")


def _make_batch_cache(model, left_padding):
    try:
        from mlx_lm.generate import _make_cache
    except ImportError:
        return [_to_batch_cache(c, left_padding) for c in model.make_cache()]
    return _make_cache(model, left_padding, None)


class _ArchTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arch = _load_arch()

    def make_model(self, config=None):
        mx.random.seed(0)
        args = self.arch.ModelArgs.from_dict(copy.deepcopy(config or TINY_CONFIG))
        return self.arch.Model(args)

    def hf_weights(self, layout="official", seed=None):
        weights = hf_checkpoint(layout=layout, seed=seed)
        return {k: mx.array(v) for k, v in weights.items()}

    def reference_model(self, config=None):
        """A model with the closed-form official weights, fp32."""
        model = self.make_model(config)
        weights = model.sanitize(self.hf_weights())
        model.load_weights(list(weights.items()), strict=True)
        model.eval()
        mx.eval(model.parameters())
        return model

    def require_reference(self):
        if REFERENCE is None:
            self.skipTest("no pinned reference: run align_qwen4_exp_upstream_pin.py")

    def assert_matches_reference(self, logits, rows=slice(None), positions=slice(None)):
        got = _np(logits)
        exp = np.array(REFERENCE["logits"], dtype=np.float64)[rows, positions]
        lse = np.array(REFERENCE["logsumexp"], dtype=np.float64)[rows, positions]
        top = np.array(REFERENCE["argmax"])[rows, positions]
        margin = np.array(REFERENCE["top2_margin"])[rows, positions]
        sub = got[..., REFERENCE["vocab_ids"]]
        err = float(np.max(np.abs(sub - exp)))
        np.testing.assert_allclose(
            sub, exp, rtol=RTOL, atol=ATOL, err_msg=f"logit slice, max abs {err:.3g}"
        )
        np.testing.assert_allclose(
            _logsumexp(got), lse, rtol=RTOL, atol=ATOL, err_msg="logsumexp"
        )
        decisive = margin > 1e-3
        np.testing.assert_array_equal(
            np.argmax(got, axis=-1)[decisive], top[decisive], err_msg="argmax"
        )

    # Copy of upstream TestModels.model_test_runner (main, 2026-10).
    def model_test_runner(self, model, model_type, vocab_size, num_layers):
        self.assertEqual(len(model.layers), num_layers)
        self.assertEqual(model.model_type, model_type)

        for t in [mx.float32, mx.float16]:
            model.update(
                tree_map(
                    lambda p: (
                        p.astype(t) if mx.issubdtype(p.dtype, mx.floating) else p
                    ),
                    model.parameters(),
                )
            )

            inputs = mx.array([[0, 1]])
            outputs = model(inputs)
            self.assertEqual(outputs.shape, (1, 2, vocab_size))
            self.assertEqual(outputs.dtype, t)

            cache = make_prompt_cache(model)
            outputs = model(inputs, cache=cache)
            self.assertEqual(outputs.shape, (1, 2, vocab_size))
            self.assertEqual(outputs.dtype, t)

            outputs = model(mx.argmax(outputs[0, -1:, :], keepdims=True), cache=cache)
            self.assertEqual(outputs.shape, (1, 1, vocab_size))
            self.assertEqual(outputs.dtype, t)

        inputs = mx.array([[0, 1], [2, 3]])
        outputs = model(inputs)
        self.assertEqual(outputs.shape, (2, 2, vocab_size))

        copy.deepcopy(model)


# ---------------------------------------------------------------------------
# Helper self-checks (no MLX needed).
# ---------------------------------------------------------------------------


class TestQwen4ExpReferenceHelpers(unittest.TestCase):
    def test_ngram_constants_match_reference(self):
        if REFERENCE is None:
            self.skipTest("no pinned reference")
        for name, text in (
            ("tiny_ngram_constants", TINY_TEXT_CONFIG),
            ("real_ngram_constants", REAL_NGRAM_TEXT_CONFIG),
        ):
            self.assertEqual(ngram_constants(text, 0), REFERENCE[name], name)

    def test_checkpoint_layouts_agree(self):
        if np is None:
            self.skipTest("NumPy is required")
        official = hf_checkpoint(layout="official")
        again = hf_checkpoint(layout="official")
        self.assertEqual(official.keys(), again.keys())
        for k in official:
            self.assertTrue(np.array_equal(official[k], again[k]), k)
        per_expert = hf_checkpoint(layout="save_pretrained")
        E = TINY_TEXT_CONFIG["num_experts"]
        I = TINY_TEXT_CONFIG["moe_intermediate_size"]
        fused = official["model.language_model.layers.0.mlp.experts.gate_up_proj"]
        up = per_expert["model.layers.0.mlp.experts.3.up_proj.weight"]
        self.assertTrue(np.array_equal(up, fused[3, I:]))
        self.assertEqual(
            sum(".mlp.experts.0.gate_proj.weight" in k for k in per_expert),
            TINY_TEXT_CONFIG["num_hidden_layers"],
        )
        self.assertEqual(E, 8)
        shards = [k for k in official if "ngram_embedding.shard_" in k]
        self.assertEqual(len(shards), TINY_TEXT_CONFIG["split_ngram_parts"])


# ---------------------------------------------------------------------------
# Model tests (mlx-lm style).
# ---------------------------------------------------------------------------


class TestQwen4Exp(_ArchTestCase):
    def test_qwen4_exp(self):
        model = self.make_model()
        self.model_test_runner(model, "qwen4_exp", 128, 4)

    def test_all_models_entry(self):
        # Exactly what upstream test_all_models does with the entry.
        config = copy.deepcopy(UPSTREAM_TEST_ALL_MODELS_ENTRY)
        args = self.arch.ModelArgs.from_dict(config)
        model = self.arch.Model(args)
        self.model_test_runner(
            model, args.model_type, config["vocab_size"], config["num_hidden_layers"]
        )

    def test_layer_types_and_cache_classes(self):
        # full_attention (official), indexed_attention (save_pretrained) and the
        # interval fallback must all give 3 DeltaNet layers and 1 QSA layer.
        flat = {**copy.deepcopy(TINY_TEXT_CONFIG)}
        indexed = {
            **flat,
            "layer_types": ["linear_attention"] * 3 + ["indexed_attention"],
        }
        interval = {k: v for k, v in flat.items() if k != "layer_types"}
        for name, config in (
            ("official", TINY_CONFIG),
            ("text_only_indexed", indexed),
            ("interval_fallback", interval),
        ):
            with self.subTest(config=name):
                model = self.make_model(config)
                cache = model.make_cache()
                self.assertEqual(len(cache), 4)
                linear = [isinstance(c, ArraysCache) for c in cache]
                self.assertEqual(linear, [True, True, True, False])
                out = model(mx.array([[2, 3, 4]]), cache=cache)
                self.assertEqual(out.shape, (1, 3, 128))
                # Standard classes only: load_prompt_cache resolves class
                # names in mlx_lm.models.cache, and batching dispatches on type.
                for c in _iter_caches(cache):
                    self.assertEqual(
                        type(c).__module__,
                        "mlx_lm.models.cache",
                        f"{type(c).__name__} is not an mlx_lm.models.cache class",
                    )

    def test_matches_reference_prefill(self):
        self.require_reference()
        model = self.reference_model()
        logits = model(mx.array(REFERENCE_INPUT_IDS))
        self.assertEqual(logits.dtype, mx.float32)
        self.assert_matches_reference(logits)

    def test_matches_reference_cached(self):
        # Chunked prefill then one token at a time, crossing QSA block
        # boundaries (12, 16, 20) and an EOS (row 0, position 13).
        self.require_reference()
        model = self.reference_model()
        tokens = mx.array(REFERENCE_INPUT_IDS)
        cache = model.make_cache()
        steps = [model(tokens[:, :9], cache=cache), model(tokens[:, 9:13], cache=cache)]
        for i in range(13, tokens.shape[1]):
            steps.append(model(tokens[:, i : i + 1], cache=cache))
        self.assert_matches_reference(mx.concatenate(steps, axis=1))

    def test_sanitize_official_checkpoint(self):
        model = self.make_model()
        sanitized = model.sanitize(self.hf_weights())
        self.assertFalse(any("mtp." in k for k in sanitized))
        self.assertFalse(any("visual" in k for k in sanitized))
        model.load_weights(list(sanitized.items()), strict=True)

    def test_sanitize_save_pretrained_layout(self):
        # transformers' save_pretrained writes per-expert projections and a
        # "model." prefix; both layouts must load to identical parameters.
        a = self.make_model()
        a.load_weights(list(a.sanitize(self.hf_weights()).items()), strict=True)
        b = self.make_model()
        b.load_weights(
            list(b.sanitize(self.hf_weights("save_pretrained")).items()), strict=True
        )
        pa, pb = dict(tree_flatten(a.parameters())), dict(tree_flatten(b.parameters()))
        self.assertEqual(pa.keys(), pb.keys())
        for k in pa:
            self.assertTrue(mx.array_equal(pa[k], pb[k]), k)

    def test_sanitize_converted_weights_is_identity(self):
        # convert calls sanitize, then load calls it again: no second (1 + w),
        # no second conv transpose, no key changes.
        model = self.reference_model()
        weights = dict(tree_flatten(model.parameters()))
        again = model.sanitize(dict(weights))
        self.assertEqual(again.keys(), weights.keys())
        for k, v in weights.items():
            self.assertTrue(mx.array_equal(again[k], v), k)

    def test_sanitize_rejects_inconsistent_hash_constants(self):
        # A checkpoint whose stored n-gram constants disagree with the
        # config-derived ones must fail closed, not degrade silently.
        corrupt = self.hf_weights()
        key = next(k for k in corrupt if k.endswith("layer_multipliers"))
        corrupt[key] = corrupt[key] + 2
        wrong_seed = self.hf_weights(seed=0)
        for name, weights in (("corrupt", corrupt), ("seed_0", wrong_seed)):
            with self.subTest(case=name):
                model = self.make_model()
                with self.assertRaises(ValueError):
                    model.load_weights(
                        list(model.sanitize(weights).items()), strict=True
                    )

    def test_left_padding(self):
        # A row run alone equals the same row left-padded inside a batch, for
        # every real position and the next decode step (QSA selection active).
        model = self.reference_model()
        short = REFERENCE_INPUT_IDS[0][:14]
        long = REFERENCE_INPUT_IDS[1][:19]
        pad = len(long) - len(short)

        cache = model.make_cache()
        single = model(mx.array([short]), cache=cache)
        next_tok = mx.argmax(single[0, -1])
        single_next = model(next_tok.reshape(1, 1), cache=cache)[0, -1]
        long_alone = model(mx.array([long]))[0]

        batch_cache = _make_batch_cache(model, [pad, 0])
        batched = model(mx.array([[0] * pad + short, long]), cache=batch_cache)
        next_toks = mx.array([[next_tok.item()], [0]])
        batched_next = model(next_toks, cache=batch_cache)[0, -1]

        for got, exp, what in (
            (batched[0, pad:], single[0], "padded row"),
            (batched[1], long_alone, "unpadded row"),
            (batched_next, single_next, "decode after padding"),
        ):
            err = float(mx.max(mx.abs(got - exp)).item())
            self.assertTrue(
                mx.allclose(got, exp, rtol=ATOL, atol=ATOL), f"{what}: {err:.3g}"
            )

    def test_prompt_cache_save_load(self):
        model = self.reference_model()
        tokens = mx.array(REFERENCE_INPUT_IDS[:1])
        cache = model.make_cache()
        model(tokens[:, :13], cache=cache)
        mx.eval([c.state for c in cache])
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "prompt.safetensors")
            save_prompt_cache(path, cache)
            loaded = load_prompt_cache(path)
        a = model(tokens[:, 13:], cache=cache)
        b = model(tokens[:, 13:], cache=loaded)
        self.assertTrue(mx.array_equal(a, b))

    def test_snapshot_restore(self):
        # The recurrent state (DeltaNet conv/state, PLE conv, n-gram context,
        # KV and raw indexer keys) snapshots and restores exactly.
        model = self.reference_model()
        prefix = mx.array([REFERENCE_INPUT_IDS[0][:12]])
        suffix_a = mx.array([REFERENCE_INPUT_IDS[0][12:17]])
        suffix_b = mx.array([REFERENCE_INPUT_IDS[1][12:17]])

        cache = model.make_cache()
        model(prefix, cache=cache)
        snapshot = copy.deepcopy(cache)
        model(suffix_a, cache=cache)
        restored = model(suffix_b, cache=copy.deepcopy(snapshot))

        fresh = model.make_cache()
        model(prefix, cache=fresh)
        expected = model(suffix_b, cache=fresh)
        self.assertTrue(mx.array_equal(restored, expected))

        one_shot = model(mx.concatenate([prefix, suffix_b], axis=1))[:, 12:]
        self.assertTrue(mx.allclose(restored, one_shot, rtol=ATOL, atol=ATOL))

    def test_trim(self):
        # Either trimming is exact (trim, re-feed equals fresh) or it is
        # refused for the whole cache without touching any state.
        model = self.reference_model()
        tokens = mx.array(REFERENCE_INPUT_IDS[:1])
        cache = model.make_cache()
        model(tokens[:, :15], cache=cache)
        if can_trim_prompt_cache(cache):
            self.assertEqual(trim_prompt_cache(cache, 3), 3)
            out = model(tokens[:, 12:16], cache=cache)
            fresh = model.make_cache()
            model(tokens[:, :12], cache=fresh)
            exp = model(tokens[:, 12:16], cache=fresh)
            self.assertTrue(mx.allclose(out, exp, rtol=ATOL, atol=ATOL))
        else:
            before = tree_flatten([c.state for c in cache])
            self.assertEqual(trim_prompt_cache(cache, 3), 0)
            after = tree_flatten([c.state for c in cache])
            self.assertEqual([k for k, _ in before], [k for k, _ in after])
            for (k, x), (_, y) in zip(before, after):
                if isinstance(x, mx.array) or isinstance(y, mx.array):
                    self.assertTrue(mx.array_equal(x, y), k)
                else:  # empty slots (None) and scalar metadata
                    self.assertEqual(x, y, k)

    def test_quant_predicate_convention(self):
        # mlx-lm calls predicates as predicate(path, module) (0.31.x and main).
        model = self.make_model()
        predicate = getattr(model, "quant_predicate", None)
        if predicate is None:
            return
        for path, module in model.named_modules():
            if hasattr(module, "to_quantized"):
                result = predicate(path, module)
                self.assertIsInstance(result, (bool, dict), path)

    def test_quantize_save_load(self):
        # convert -> save -> load (sanitize runs again on quantized weights).
        # Group 32 is the largest group that divides the n-gram row width
        # (160 in the real model, 32 here), so the n-gram table must quantize.
        model = self.reference_model()
        inputs = mx.array(REFERENCE_INPUT_IDS)
        full = _np(model(inputs))
        qmodel, qconfig = quantize_model(
            model, copy.deepcopy(TINY_CONFIG), group_size=32, bits=8
        )
        quantized = [
            name
            for name, m in qmodel.named_modules()
            if isinstance(m, (nn.QuantizedLinear, nn.QuantizedEmbedding))
        ]
        self.assertTrue(
            any("ngram" in n for n in quantized), "n-gram table not quantized"
        )
        qlogits = qmodel(inputs)
        self.assertGreater(_cosine(_np(qlogits), full), 0.999)
        with tempfile.TemporaryDirectory() as d:
            save_model(d, qmodel)
            save_config(qconfig, Path(d) / "config.json")
            classes = (self.arch.Model, self.arch.ModelArgs)
            loaded, _ = load_model(Path(d), get_model_classes=lambda config: classes)
            self.assertTrue(mx.array_equal(loaded(inputs), qlogits))

    def test_bf16_cast(self):
        # convert's dtype cast honours cast_predicate (e.g. A_log, integer
        # buffers) and the bf16 model stays close to fp32.
        model = self.reference_model()
        inputs = mx.array(REFERENCE_INPUT_IDS)
        full = _np(model(inputs))
        cast_predicate = getattr(model, "cast_predicate", lambda _: True)
        weights = {
            k: (
                v.astype(mx.bfloat16)
                if cast_predicate(k) and mx.issubdtype(v.dtype, mx.floating)
                else v
            )
            for k, v in tree_flatten(model.parameters())
        }
        model.load_weights(list(weights.items()))
        out = _np(model(inputs))
        self.assertTrue(np.all(np.isfinite(out)))
        self.assertGreater(_cosine(out, full), 0.99)


if __name__ == "__main__":
    unittest.main()
