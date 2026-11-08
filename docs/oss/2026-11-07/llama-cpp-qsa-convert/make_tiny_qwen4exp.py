#!/usr/bin/env python3
# UNRUN: written 2026-11-07 by an agent; never executed. Standard library only (json, argparse, pathlib).
# It imports nothing from llama.cpp or transformers and downloads nothing.
#
# Ed's commands (any Python 3.9+, no venv needed):
#     python3 -I make_tiny_qwen4exp.py /tmp/q4x/legacy  --layer-type full_attention
#     python3 -I make_tiny_qwen4exp.py /tmp/q4x/resaved --layer-type indexed_attention
#     # optional, real 48-layer shape from a real config.json (config only, never weights):
#     python3 -I make_tiny_qwen4exp.py /tmp/q4x/real-resaved --layer-type indexed_attention --from-config /path/config.json
"""Write a config-only Qwen4-Exp (Qwen3.8-Flash-Next) checkpoint directory: config.json and nothing else.

The llama.cpp bug this kit targets lives in metadata that convert_hf_to_gguf.py derives from config.json
alone (attention.compress_ratios), so no weights or tokenizer are needed to show it.

transformers rewrites the checkpoint's "full_attention" layer type when it loads a Qwen4-Exp config, and
save_pretrained writes the new name: "qwen_sparse_attention" since the model was added (PR #48337, 2026-08-26),
"indexed_attention" since PR #48974 (2026-09-22). --layer-type indexed_attention (or qwen_sparse_attention)
therefore stands in for any fine-tune, merge or re-shard saved through transformers, without needing it here.

Default mode writes a tiny config: 4 trunk layers (3 linear_attention + 1 QSA layer, the official 1-in-4
pattern), 1 MTP block, indexer_budget=4, indexer_compress_ratio=2. Dims are borrowed from JouleWise's F1
reproducer (scripts/audit_mlxvlm/repro_f1_indexed_attention.py on port/qwen4-exp-mlx). That config (2 layers,
PLE on layer 1) was accepted by transformers 5.22.1; this one has 4 layers and no PLE, and whether
transformers' AutoConfig accepts it is unverified. The repro reports which config path was taken.

--from-config PATH copies a real config.json and replaces every "full_attention" entry in
text_config.layer_types (or top-level layer_types) with --layer-type, which is what transformers' remap does.
Nothing else is changed.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

QSA_NAMES = ("full_attention", "indexed_attention", "qwen_sparse_attention")

TINY_TEXT_CONFIG = {
    "model_type": "qwen4_exp_text",
    "vocab_size": 64,
    "hidden_size": 64,
    "num_hidden_layers": 4,
    "full_attention_interval": 4,
    "mtp_num_hidden_layers": 1,
    "num_attention_heads": 2,
    "num_key_value_heads": 1,
    "head_dim": 32,
    "hc_count": 2,
    "hc_lowrank": 8,
    "linear_conv_kernel_dim": 3,
    "linear_key_head_dim": 32,
    "linear_value_head_dim": 32,
    "linear_num_key_heads": 1,
    "linear_num_value_heads": 2,
    "moe_intermediate_size": 64,
    "shared_expert_intermediate_size": 64,
    "num_experts": 4,
    "num_experts_per_tok": 2,
    "indexer_n_heads": 2,
    "indexer_kv_heads": 1,
    "indexer_head_dim": 16,
    "indexer_budget": 4,
    "indexer_compress_ratio": 2,
    # empty: no PLE n-gram table, so the converter never looks for PLE constant tensors
    "ple_layer_ids": [],
    "eos_token_id": 2,
    "rms_norm_eps": 1e-6,
    "max_position_embeddings": 4096,
    "rope_parameters": {
        "rope_type": "default",
        "rope_theta": 10000.0,
        "partial_rotary_factor": 0.25,
        "mrope_section": [11, 11, 10],
        "mrope_interleaved": True,
    },
}


def tiny_config(layer_type: str) -> dict:
    text = copy.deepcopy(TINY_TEXT_CONFIG)
    n = text["num_hidden_layers"]
    interval = text["full_attention_interval"]
    text["layer_types"] = [layer_type if (i + 1) % interval == 0 else "linear_attention" for i in range(n)]
    return {
        "architectures": ["Qwen4ExpForConditionalGeneration"],
        "model_type": "qwen4_exp",
        "text_config": text,
        "tie_word_embeddings": False,
    }


def resaved_config(src: Path, layer_type: str) -> dict:
    cfg = json.loads(src.read_text(encoding="utf-8"))
    text = cfg["text_config"] if "text_config" in cfg else cfg
    before = list(text["layer_types"])
    text["layer_types"] = [layer_type if t == "full_attention" else t for t in before]
    changed = sum(1 for a, b in zip(before, text["layer_types"]) if a != b)
    sys.stderr.write(f"rewrote {changed} of {len(before)} layer_types entries to {layer_type!r}\n")
    return cfg


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out_dir", type=Path, help="directory to create; must not contain weight files")
    ap.add_argument("--layer-type", choices=QSA_NAMES, default="indexed_attention",
                    help="name to use for the QSA (sparse full-attention) layers")
    ap.add_argument("--from-config", type=Path, default=None,
                    help="real Qwen4-Exp config.json to copy instead of the tiny built-in config")
    args = ap.parse_args()

    cfg = resaved_config(args.from_config, args.layer_type) if args.from_config else tiny_config(args.layer_type)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stray = sorted(p.name for p in args.out_dir.iterdir()
                   if p.suffix in (".safetensors", ".bin") or p.name.endswith(".index.json"))
    if stray:
        # the converter would try to index these; the repro wants a config-only directory
        sys.stderr.write(f"refusing: {args.out_dir} already holds weight files: {stray}\n")
        return 2
    (args.out_dir / "config.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    text = cfg.get("text_config", cfg)
    sys.stdout.write(f"wrote {args.out_dir / 'config.json'}\n")
    sys.stdout.write(f"layer_types = {text['layer_types']}\n")
    sys.stdout.write(f"indexer_compress_ratio = {text['indexer_compress_ratio']}, "
                     f"indexer_budget = {text['indexer_budget']}, "
                     f"mtp_num_hidden_layers = {text.get('mtp_num_hidden_layers')}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
