"""MLX adapter for the qwen4 quant-quality harness.

``load`` opens an assembled qwen4_exp artifact once, through the converter's
pinned ``load_verified_model`` (the only supported loader: it verifies the
manifest pin, executes only the hashed ``qwen4_exp.py`` and opens the PLE
tables).  Stock ``mlx_lm.load`` would execute the artifact's module unpinned
and, called per prompt, would reopen a ~200 GB model for every prompt.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def load(model_path, manifest_sha256=None):
    if not re.fullmatch(r"[0-9a-f]{64}", manifest_sha256 or ""):
        raise ValueError("--manifest-sha256 (the artifact's pinned manifest.json sha256) is required")
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    try:
        import align_convert_qwen4_exp as converter
    except ImportError as exc:  # The converter lives on the live-kit lane.
        raise ValueError("align_convert_qwen4_exp (live kit) is required to load an assembled artifact") from exc
    model, _ = converter.load_verified_model(Path(model_path), manifest_sha256, lazy=True)
    model.eval()
    return model


def teacher_forced_logits(model, input_ids):
    import mlx.core as mx
    import numpy as np
    value = model(mx.array([list(input_ids)]))
    logits = value.logits if hasattr(value, "logits") else value
    result = logits.astype(mx.float32)
    mx.eval(result)
    # Copy to host before releasing Metal allocations.
    output = np.array(result)
    del value, logits, result
    mx.clear_cache()
    return output
