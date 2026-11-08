# KIT BANNER (delete these lines before copying upstream; 01-test.patch already omits them)
# UNRUN: written 2026-11-07 by an agent from source reading only; never imported, run or tested.
# Pinned upstream: ggml-org/llama.cpp f477f795cb071baf5b8af6488378366a72034ac4
# Ed runs it from the root of his llama.cpp checkout, after `git apply kit/01-test.patch`:
#     python -m unittest discover -s tests -p 'test_conversion_qwen4exp.py' -v
# Expected on the pinned commit: FAIL for layer_type=indexed_attention and qwen_sparse_attention ([0, 0, 2] != [0, 2, 2]).
# Expected after 02-fix-option-a.patch or 02-fix-option-b.patch: OK.
# END KIT BANNER
"""Test Qwen4-Exp conversion metadata with a small synthetic config; no GPU or model downloads required.

Install dependencies and run from the repository root:
    python -m pip install -r requirements/requirements-convert_hf_to_gguf.txt
    python -m unittest discover -s tests -p 'test_conversion_qwen4exp.py' -v

Use unittest discovery so the repository root is available for imports.
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from conversion.base import gguf
from conversion.qwen4exp import Qwen4ExpTextModel


class TestQwen4ExpConversion(unittest.TestCase):
    def compress_ratios(self, layer_types: list[str]) -> list[int]:
        hparams = {
            "architectures": ["Qwen4ExpForCausalLM"],
            "num_hidden_layers": len(layer_types),
            "mtp_num_hidden_layers": 1,
            "layer_types": layer_types,
            "hidden_size": 4,
            "head_dim": 4,
            "linear_conv_kernel_dim": 2,
            "linear_key_head_dim": 4,
            "linear_value_head_dim": 4,
            "linear_num_key_heads": 1,
            "linear_num_value_heads": 1,
            "hc_count": 2,
            "hc_lowrank": 1,
            "indexer_n_heads": 1,
            "indexer_head_dim": 4,
            "indexer_budget": 4,
            "indexer_compress_ratio": 2,
            "ple_layer_ids": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "config.json").write_text(json.dumps(hparams))
            model = Qwen4ExpTextModel(path, gguf.LlamaFileType.ALL_F32, path / "out.gguf", hparams=hparams)
            model.set_gguf_parameters()
            key = gguf.Keys.Attention.COMPRESS_RATIOS.format(arch=model.gguf_writer.arch)
            return list(model.gguf_writer.kv_data[0][key].value)

    def test_qsa_layer_types(self):
        # transformers saves "full_attention" as "indexed_attention"; the last entry is the MTP block
        for layer_type in ("full_attention", "indexed_attention", "qwen_sparse_attention"):
            with self.subTest(layer_type=layer_type):
                self.assertEqual(self.compress_ratios(["linear_attention", layer_type]), [0, 2, 2])


if __name__ == "__main__":
    unittest.main()
