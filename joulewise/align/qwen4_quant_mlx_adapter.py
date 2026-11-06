"""MLX adapter for the qwen4 quant-quality harness.

``load`` opens an assembled qwen4_exp artifact once, through the converter's
pinned ``load_verified_model`` (the only supported loader: it verifies the
manifest pin, executes only the hashed ``qwen4_exp.py`` and opens the PLE
tables).  Stock ``mlx_lm.load`` would execute the artifact's module unpinned
and, called per prompt, would reopen a ~200 GB model for every prompt.

It applies the live kit's guards (``scripts/qwen4exp_mbp_live.py``) before any
weight is allocated, exactly as the kit's native worker does:

- refuse while launchd measurement agents (night chain, b6 loop) are loaded;
- the artifact, and every PLE table it pages, must live on /Volumes/JW-EXT;
- Metal memory limit = min(kit cap 115.4 GB, device recommended working set),
  cache limit 256 MiB, checked against the peak after every prompt;
- PLE resident file pages stay under the kit's 21.5 GB operational cap,
  checked after load and after every prompt.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
CACHE_LIMIT_BYTES = 256 * 2**20  # as the live kit's native worker


@dataclass
class Handle:
    model: Any
    metal_cap_bytes: int
    artifact: Path


def _live():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import qwen4exp_mbp_live as live
    return live


def _check(live, mx, handle):
    """Kit guards that must hold after load and after every prompt."""
    if mx.get_peak_memory() > handle.metal_cap_bytes:
        raise ValueError("Metal peak exceeds the working-set cap")
    stats = live.table_stats(handle.model)
    for row in stats.values():
        live.external(row["path"])  # PLE must page from JW-EXT, never an internal copy.
    live.check_tables(stats)
    return stats


def load(model_path, manifest_sha256=None, metal_cap_gb=None):
    if not re.fullmatch(r"[0-9a-f]{64}", manifest_sha256 or ""):
        raise ValueError("--manifest-sha256 (the artifact's pinned manifest.json sha256) is required")
    live = _live()
    agents = live.measurement_agents_loaded()
    if agents:
        raise ValueError("measurement agents are loaded; quant-quality scoring is forbidden: " + ", ".join(agents))
    artifact = live.external(model_path)  # /Volumes/JW-EXT only; restricted paths refused.
    import mlx.core as mx
    device = mx.device_info() if hasattr(mx, "device_info") else mx.metal.device_info()
    cap = live.METAL_CAP if metal_cap_gb is None else float(metal_cap_gb) * 1e9
    cap = int(min(cap, int(device["max_recommended_working_set_size"])))
    # Limits are set before any weight is allocated, so a 128 GB-class model
    # cannot push the Mac into swap.
    mx.set_cache_limit(CACHE_LIMIT_BYTES)
    mx.set_memory_limit(cap)
    mx.reset_peak_memory()
    try:
        import align_convert_qwen4_exp as converter
    except ImportError as exc:  # pragma: no cover - the converter ships in scripts/
        raise ValueError("align_convert_qwen4_exp (live kit) is required to load an assembled artifact") from exc
    model, _ = converter.load_verified_model(artifact, manifest_sha256, lazy=True)
    model.eval()
    handle = Handle(model=model, metal_cap_bytes=cap, artifact=artifact)
    _check(live, mx, handle)
    return handle


def teacher_forced_logits(handle, input_ids):
    import mlx.core as mx
    import numpy as np
    model = handle.model if isinstance(handle, Handle) else handle
    value = model(mx.array([list(input_ids)]))
    logits = value.logits if hasattr(value, "logits") else value
    result = logits.astype(mx.float32)
    mx.eval(result)
    # Copy to host before releasing Metal allocations.
    output = np.array(result)
    del value, logits, result
    mx.clear_cache()
    if isinstance(handle, Handle):
        _check(_live(), mx, handle)
    return output
