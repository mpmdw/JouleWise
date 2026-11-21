"""Minimal reproducer, mlx-vlm 0.7.12: a left-padded batch scored WITHOUT a
cache (e.g. log-likelihood scoring: LanguageModel(ids, attention_mask=mask))
silently ignores the padding. Attention is plain causal over the pad columns,
DeltaNet/PLE consume the pad tokens, and PLE hashes pad ids instead of EOS.
The unpadded row is exact; the padded row is wrong. No error is raised.

Cause: LanguageModel.__call__ (qwen3_5/language.py) uses attention_mask only
for RoPE positions and never forwards it to Qwen4ExpModel; padding is only
honoured through a batch cache's left_padding (qwen4_exp/language.py
1624-1717). Patch draft: p5_padded_no_cache.patch (fail loudly).

  python repro_p5_padded_no_cache.py
"""
import sys
from pathlib import Path

import mlx.core as mx
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from repro_d1_ragged_qsa import tiny_model  # noqa: E402


def main():
    lm = tiny_model().language_model
    rng = np.random.default_rng(7)
    ids = rng.integers(3, 96, 30).astype(np.int32)
    pad = 8
    batch = np.stack([ids, np.concatenate([np.zeros(pad, np.int32), ids[:-pad]])])
    mask = (np.arange(30)[None] >= np.array([[0], [pad]])).astype(np.int32)
    try:
        out = np.array(lm(mx.array(batch), attention_mask=mx.array(mask)).logits)
    except NotImplementedError as e:
        print("refused (patched):", e)
        return
    lm._position_ids = lm._rope_deltas = None
    row0 = np.array(lm(mx.array(ids[None])).logits)[0]
    lm._position_ids = lm._rope_deltas = None
    row1 = np.array(lm(mx.array(ids[None, :-pad])).logits)[0]
    print(f"unpadded row  max|batch - single| = {np.abs(out[0] - row0).max():.2e}")
    print(f"padded row    max|batch - single| = {np.abs(out[1, pad:] - row1).max():.2e}   <- silently wrong")


if __name__ == "__main__":
    main()
