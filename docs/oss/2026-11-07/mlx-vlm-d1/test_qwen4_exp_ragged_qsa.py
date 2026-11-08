# UNRUN in this kit. Prepared read-only on 2026-11-07; not executed against
# upstream commit a54f1a0d86fa45c466c00d819ac6ac5ba9d61ac4.
# Provenance: the code below the docstring is byte-identical to
# docs/align/upstream_mlxvlm_d1/test_qwen4_exp_ragged_qsa.py at JouleWise
# f1e0f6673. On 2026-11-05, dropped into mlx_vlm/tests/ of mlx-vlm 5cdc659b,
# it failed 2/2 (max |delta| 0.133) and passed 2/2 with fix.diff applied.
#
# This standalone file is the optional route. The upstream-shaped route is
# test_only.diff, which adds the same function to mlx_vlm/tests/test_cache.py.
#
# How Ed runs it (see RUN-ME.md):
#   cp /private/tmp/jwoss-ro/mlx-vlm-d1/kit/test_qwen4_exp_ragged_qsa.py \
#      $W/mlx-vlm/mlx_vlm/tests/
#   cd $W/mlx-vlm/mlx_vlm && $W/venv/bin/python -m pytest -q \
#      tests/test_qwen4_exp_ragged_qsa.py
#   # expected: 2 failed on unpatched a54f1a0d; 2 passed after fix.diff
#   # delete the copied file afterwards (CI requires every tests/test_*.py
#   # file to be listed in a .github/workflows/tests.yml group).
#
"""Regression test: a left-padded qwen4_exp batch keeps QSA sparse attention.

Upstream placement: add the test function to mlx_vlm/tests/test_cache.py,
after test_qwen3_5_single_row_decode_retains_batch_cache. That module already
has the imports below, so the PR adds no new test file. A new file would also
have to be listed in a CI test group in .github/workflows/tests.yml.
"""

import mlx.core as mx
import numpy as np
import pytest

from mlx_vlm.generate.ar import _make_cache
from mlx_vlm.tests.test_models import build_config, model_case


@pytest.mark.parametrize("decode_path", ["batch_invariant", "attention"])
def test_qwen4_exp_ragged_batch_matches_single_requests(decode_path):
    from mlx_vlm.models import qwen4_exp

    fields = model_case("qwen4_exp")["config"]["text_config"]
    # With one indexer head, relu leaves exact-zero score ties, which a padded
    # row may break differently. Sixteen heads keep the selection unique.
    fields["indexer_n_heads"] = 16
    mx.random.seed(17)
    lm = qwen4_exp.LanguageModel(build_config(qwen4_exp, fields, "TextConfig"))
    lm.eval()
    if decode_path == "attention":
        # Decode takes this path when lm_head is quantized in a format the
        # batch-invariant forward does not support.
        lm._supports_batch_invariant_decode = lambda: False

    # Rows of 14 and 11 tokens, so left padding [0, 3]. QSA keeps 2 blocks of
    # 4 tokens, so both rows decode with sparse attention from the first step.
    prompts = [list(range(1, 15)), list(range(20, 31))]
    indexer = lm.model.layers[lm.model.fa_idx].self_attn.indexer
    assert (len(prompts[1]) + 1) // indexer.compress_ratio > indexer.block_topk

    def run(rows, cache):
        width = max(map(len, rows))
        ids = [[0] * (width - len(r)) + r for r in rows]
        positions = [[0] * (width - len(r)) + list(range(len(r))) for r in rows]
        lm(mx.array(ids), cache=cache, position_ids=mx.array(positions))
        logits = []
        for step in range(3):
            tokens = mx.full((len(rows), 1), 40 + step)
            positions = mx.array([[len(r) + step] for r in rows])
            logits.append(lm(tokens, cache=cache, position_ids=positions).logits)
        # A 3-token block through the speculative (MTP) verifier.
        block = mx.array([[43, 44, 45]] * len(rows))
        logits.append(lm.speculative_verify_logits(block, cache, lambda x: x)[3])
        return mx.concatenate(logits, axis=1)

    actual = run(prompts, _make_cache(lm, [0, 3]))
    for row, prompt in enumerate(prompts):
        expected = run([prompt], lm.make_cache())
        np.testing.assert_allclose(
            np.array(actual[row : row + 1]), np.array(expected), atol=1e-5, rtol=1e-5
        )
