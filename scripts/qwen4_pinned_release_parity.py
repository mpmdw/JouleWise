#!/usr/bin/env python3
"""Replay the released-structure B/C gold fixtures through pinned mlx-lm."""
import argparse
from contextlib import ExitStack
import json
from pathlib import Path

import mlx.core as mx
from mlx_lm.utils import load_model
import numpy as np

from qwen4_pinned_quantization_probe import released_fixture_config, vendored_checkpoint, write_json
from qwen4_ple_cache_probe import load_python


def replay(fixtures, parity, scratch):
    harness = load_python(parity, "qwen4_parity")
    sources = ("hf", "upstream", "port")
    pairs = (*harness.PAIRS, ("hf", "pinned"), ("upstream", "pinned"), ("port", "pinned"))
    result = {}
    for case in ("B", "C"):
        with np.load(fixtures / f"{case}-fp32" / "hf.npz") as hf32:
            for dtype in ("fp32", "bf16"):
                directory = fixtures / f"{case}-{dtype}"
                config = json.loads((directory / "config.json").read_text())
                config = released_fixture_config(config, "zero_centered")
                with vendored_checkpoint(scratch, config, directory / "hf.safetensors") as checkpoint:
                    model, _ = load_model(checkpoint)
                observed = harness.capture_mlx(model, model.model, mx.array([config["ids"]]), port=False)
                with ExitStack() as stack:
                    traces = {name: stack.enter_context(np.load(directory / f"{name}.npz")) for name in sources}
                    if any(observed.keys() != set(trace.files) for trace in traces.values()):
                        raise AssertionError(f"{directory.name}: component inventory differs")
                    traces["pinned"] = observed
                    rows = {}
                    for key in observed:
                        exact = key.endswith((".indexer", ".router")) or key == "greedy"
                        noise = np.max(np.abs(traces["hf"][key] - hf32[key])) if not exact and dtype == "bf16" else 0
                        atol = 0.0 if exact else float(max(1e-4, 1.5 * noise))
                        rows[key] = {f"{a}/{b}": harness.metrics(traces[a][key], traces[b][key], atol) for a, b in pairs}
                    for key, row in rows.items():
                        if dtype == "fp32" and any(not metric["pass"] for metric in row.values()):
                            raise AssertionError(f"{directory.name}/{key}: FP32 parity regression")
                        if (not row["upstream/pinned"]["pass"]
                            or (row["hf/upstream"]["pass"] and not row["hf/pinned"]["pass"])
                            or (row["upstream/port"]["pass"] and not row["port/pinned"]["pass"])):
                            raise AssertionError(f"{directory.name}/{key}: pinned adapter parity regression")
                    result[directory.name] = rows
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixtures", type=Path)
    parser.add_argument("--harness", type=Path, required=True, help="Path to the merged parity harness script")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_json(args.output, replay(args.fixtures, args.harness, args.output.parent))
