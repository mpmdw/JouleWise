#!/usr/bin/env python3
# UNRUN: written 2026-11-07 by an agent from source reading only; never executed.
# It imports llama.cpp's converter package from the checkout you name (upstream code), so only Ed runs it,
# inside a venv that has llama.cpp's requirements/requirements-convert_hf_to_gguf.txt installed.
#
# Ed's commands (checkpoint dirs come from make_tiny_qwen4exp.py; config.json only, no weights):
#     python repro_compress_ratios.py ~/src/llama.cpp /tmp/q4x/legacy    # expect exit 0 on any commit
#     python repro_compress_ratios.py ~/src/llama.cpp /tmp/q4x/resaved   # expect exit 1 on f477f795c, 0 after the fix
#
# Exit status: 0 = every trunk attention layer got a nonzero compress ratio; 1 = at least one trunk attention
# layer got ratio 0 (the bug); 3 = setup problem (bad paths, missing keys).
"""Show the attention.compress_ratios that convert_hf_to_gguf.py would write for a Qwen4-Exp checkpoint.

It follows convert_hf_to_gguf.py main() up to the metadata step: ModelBase.load_hparams, get_model_class,
the model constructor, then set_gguf_parameters() (the call prepare_metadata() makes inside write()).
It writes no GGUF file and reads no tensors.

It also prints the layer_types in config.json next to the layer_types the converter actually saw, because
load_hparams() tries transformers.AutoConfig first (conversion/base.py:1699) and a transformers release that
knows qwen4_exp rewrites "full_attention" to "indexed_attention" on load.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} LLAMA_CPP_DIR CHECKPOINT_DIR", file=sys.stderr)
        return 3
    llama_dir = Path(argv[1]).expanduser().resolve()
    ckpt = Path(argv[2]).expanduser().resolve()
    if not (llama_dir / "conversion" / "qwen4exp.py").is_file():
        print(f"{llama_dir} has no conversion/qwen4exp.py", file=sys.stderr)
        return 3
    if not (ckpt / "config.json").is_file():
        print(f"{ckpt} has no config.json", file=sys.stderr)
        return 3

    # WARNING shows the converter's "Failed to load model config ... Trying to load config.json instead" line
    logging.basicConfig(level=logging.WARNING)
    sys.path.insert(0, str(llama_dir))
    from conversion import ModelBase, ModelType, get_model_architecture, get_model_class
    from conversion.base import gguf

    import transformers
    try:
        from transformers.models.auto.configuration_auto import CONFIG_MAPPING_NAMES
        knows_qwen4_exp = "qwen4_exp" in CONFIG_MAPPING_NAMES
    except Exception:
        knows_qwen4_exp = None  # informational only
    print(f"llama.cpp checkout : {llama_dir}")
    print(f"checkpoint         : {ckpt}")
    print(f"transformers       : {transformers.__version__} (knows qwen4_exp: {knows_qwen4_exp})")

    raw = json.loads((ckpt / "config.json").read_text(encoding="utf-8"))
    raw_types = raw.get("text_config", raw).get("layer_types")

    hparams = ModelBase.load_hparams(ckpt, False)
    arch = get_model_architecture(hparams, ModelType.TEXT)
    model_class = get_model_class(arch)
    print(f"architecture       : {arch} -> {model_class.__name__}")

    model = model_class(ckpt, gguf.LlamaFileType.ALL_F32, ckpt / "not-written.gguf")
    try:
        model.set_gguf_parameters()
    except ValueError as e:
        # a real config with ple_layer_ids needs PLE constant tensors; compress_ratios is written before that step
        if "PLE constant" not in str(e):
            raise
        print(f"note               : stopped at the PLE step ({e}); compress_ratios was already written")

    seen_types = model.hparams["layer_types"]
    n_layer = model.hparams["num_hidden_layers"]
    expected_ratio = model.hparams["indexer_compress_ratio"]
    kv = model.gguf_writer.kv_data[0]
    arch_name = model.gguf_writer.arch
    ratios = list(kv[gguf.Keys.Attention.COMPRESS_RATIOS.format(arch=arch_name)].value)
    recurrent = list(kv[gguf.Keys.Attention.RECURRENT_LAYERS.format(arch=arch_name)].value)

    print(f"layer_types rewritten by AutoConfig: {raw_types != seen_types}")
    print(f"block_count        : {model.block_count} (trunk {n_layer} + MTP {model.block_count - n_layer})")
    print(f"expected QSA ratio : {expected_ratio}")
    print()
    print(f"{'layer':>5}  {'config.json':<22} {'converter saw':<22} {'recurrent':<9} compress_ratio")
    for i in range(model.block_count):
        raw_t = raw_types[i] if raw_types and i < len(raw_types) else "(MTP)"
        seen_t = seen_types[i] if i < n_layer else "(MTP)"
        print(f"{i:>5}  {raw_t:<22} {seen_t:<22} {str(bool(recurrent[i])):<9} {ratios[i]}")
    print()

    dense = [i for i in range(n_layer) if not recurrent[i] and ratios[i] == 0]
    if dense:
        print(f"BUG: trunk attention layers {dense} are QSA layers in the checkpoint but got compress ratio 0.")
        print("     At runtime src/models/qwen4exp.cpp:1019 treats ratio 0 as dense attention, with no warning.")
        return 1
    print("OK: every trunk attention layer got a nonzero compress ratio.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
