#!/usr/bin/env python3
"""Build tiny upstream quants and check the pinned Flash-Next model_file loader."""
import argparse
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path

import mlx.core as mx
from mlx.utils import tree_flatten
import numpy as np

from qwen4_upstream_parity import metrics, upstream_module, vendored_checkpoint, write_json


CASES = {
    "affine": ("fp32", 64, 6, "affine", False),
    "nvfp4": ("bf16", 16, 4, "nvfp4", False),
    "nvfp4-global-scale": ("bf16", 16, 4, "nvfp4", True),
}


def decode(model, config):
    ids = mx.array([config["ids"]])
    cache = model.make_cache()
    prefill = model(ids[:, :-1], cache=cache)
    continuation = model(ids[:, -1:], cache=cache)
    return {name: np.asarray(value.astype(mx.float32))
            for name, value in (("prefill", prefill), ("decode", continuation))}


def prepare(root, fixtures):
    from mlx_lm.utils import load_model, quantize_model

    arch = upstream_module()
    for name, (dtype, group, bits, mode, global_scale) in CASES.items():
        fixture = fixtures / f"C-{dtype}"
        config = json.loads((fixture / "config.json").read_text())
        hf_weights = mx.load(str(fixture / "hf.safetensors"))
        model = arch.Model(arch.ModelArgs.from_dict(config))
        model.load_weights(list(model.sanitize(hf_weights).items()), strict=True)
        model, config = quantize_model(model, config, group, bits, mode=mode,
                                       global_scale=global_scale)
        path = root / name
        path.mkdir(parents=True)
        write_json(path / "config.json", config)
        weights = dict(tree_flatten(model.parameters()))
        scales = sum(key.endswith(".global_scale") for key in weights)
        if bool(scales) != global_scale:
            raise ValueError(f"{name} produced {scales} global scale tensors")
        weight_file = path / "model.safetensors"
        mx.save_safetensors(str(weight_file), weights)
        model, _ = load_model(path)
        outputs = decode(model, config)
        if not all(np.isfinite(value).all() for value in outputs.values()):
            raise ValueError(f"{name} upstream logits are nonfinite")
        np.savez(path / "upstream.npz", **outputs)
        write_json(path / "upstream.json", {
            "weights_sha256": sha256(weight_file.read_bytes()).hexdigest(),
            "global_scale_tensors": scales,
            "upstream_finite": True,
        })


def verify(root):
    from mlx_lm.utils import load_model

    if (version("mlx"), version("mlx-lm")) != ("0.31.2", "0.31.3"):
        raise ValueError("verify requires MLX 0.31.2 and mlx-lm 0.31.3")
    if not mx.metal.is_available():
        raise RuntimeError("verify requires Metal")
    result = {}
    for name in CASES:
        path = root / name
        config = json.loads((path / "config.json").read_text())
        upstream = json.loads((path / "upstream.json").read_text())
        weights = path / "model.safetensors"
        if sha256(weights.read_bytes()).hexdigest() != upstream["weights_sha256"]:
            raise ValueError(f"{name} checkpoint differs from the upstream replay")
        with vendored_checkpoint(path, config, weights) as checkpoint, mx.stream(mx.gpu):
            try:
                model, _ = load_model(checkpoint)
            except ValueError as exc:
                if name == "affine" or "quantization.mode='nvfp4' is unsupported" not in str(exc):
                    raise
                result[name] = dict(upstream, refusal=str(exc))
                continue
            if name != "affine":
                raise AssertionError(f"pinned model_file accepted {name}")
            outputs = decode(model, config)
        with np.load(path / "upstream.npz") as expected:
            rows = {key: metrics(expected[key], value, 1e-4) for key, value in outputs.items()}
        if not all(row["pass"] for row in rows.values()):
            raise AssertionError(f"pinned affine checkpoint disagrees with upstream: {rows}")
        result[name] = dict(upstream, comparisons=rows)
    write_json(root / "pinned-quantization-results.json", result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("prepare", "verify"))
    parser.add_argument("root", type=Path)
    parser.add_argument("--fixtures", type=Path, help="reference harness output with C-fp32 and C-bf16")
    args = parser.parse_args()
    if args.stage == "prepare":
        if args.fixtures is None:
            parser.error("prepare requires --fixtures")
        prepare(args.root, args.fixtures)
    else:
        verify(args.root)
