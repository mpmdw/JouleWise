"""Private single-framework subprocess entry point."""
from __future__ import annotations

import importlib.util
import json
import os
import threading
import resource
import sys
from pathlib import Path

from .core import IndexedCheckpoint, SCHEMA, digest, write_json


def import_adapter(path):
    path = Path(path).resolve()
    spec = importlib.util.spec_from_file_location("qwen4_gold_user_adapter", path)
    if spec is None or spec.loader is None:
        raise ValueError("cannot import adapter")
    sys.path.insert(0, str(path.parent))  # Thin adapters can import sibling port files.
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if getattr(module, "GOLD_ADAPTER_VERSION", None) != 1:
        raise ValueError("adapter must declare GOLD_ADAPTER_VERSION = 1")
    if getattr(module, "GOLD_ADAPTER_KIND", None) not in {"mlx", "stub"}:
        raise ValueError("adapter must declare GOLD_ADAPTER_KIND = 'mlx' or 'stub'")
    return module


def main():
    request_path = Path(sys.argv[1])
    request = json.loads(request_path.read_text())
    out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    def guard():
        while True:
            peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            peak *= 1 if sys.platform == "darwin" else 1024
            if peak > request["max_memory_bytes"]:
                print("memory_guard: child RSS budget exceeded", file=sys.stderr, flush=True)
                os._exit(86)
            threading.Event().wait(0.05)
    threading.Thread(target=guard, daemon=True).start()
    if request["backend"] == "tiny":
        from .reference import make_tiny
        write_json(out / "result.json", make_tiny(request["checkpoint"]))
        return
    checkpoint = IndexedCheckpoint(request["checkpoint"], request.get("shard_guards"))
    if request.get("config_digest") != digest(checkpoint.config) or request.get("weight_map_digest") != digest(checkpoint.weight_map):
        raise ValueError("checkpoint config/index changed after fingerprinting")
    if request["backend"] == "reference":
        from .reference import run_reference
        traces, metadata = run_reference(request, checkpoint)
    else:
        module = import_adapter(request["mlx_module"])
        traces, metadata = module.run_gold(request, checkpoint)
        metadata = dict(metadata, adapter_kind=module.GOLD_ADAPTER_KIND, reads=checkpoint.reads)
    # Recheck every accessed shard after execution as well as before each read.
    for filename in {entry["shard"] for entry in checkpoint.reads}:
        checkpoint.path(filename)
    import numpy as np
    files = {}
    for name, value in traces.items():
        if not name or any(c not in "abcdefghijklmnopqrstuvwxyz_0123456789." for c in name):
            raise ValueError("invalid trace name")
        # Adapters return NumPy arrays (MLX adapters must evaluate/cast to fp32).
        value = np.ascontiguousarray(value)
        if value.dtype.kind not in "biuf":
            raise ValueError("trace must be numeric, non-object NumPy array")
        np.save(out / (name + ".npy"), value, allow_pickle=False)
        files[name] = name + ".npy"
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    metadata["peak_rss_bytes"] = peak if sys.platform == "darwin" else peak * 1024
    write_json(out / "result.json", {"schema": SCHEMA, "traces": files, "metadata": metadata})


if __name__ == "__main__":
    main()
