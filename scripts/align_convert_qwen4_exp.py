#!/usr/bin/env python3
"""Offline, streaming HF bf16/fp32 -> JouleWise-owned pinned-stack MLX format.

No model construction, checkpoint-wide materialization, downloads or inference.
Quantization requires mlx 0.31.2; unquantized conversion needs numpy only.
The output directory must be new. A failed conversion has no manifest.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.align.models import qwen4_exp_tables as rules


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tensor_header(path):
    with path.open("rb") as f:
        length = struct.unpack("<Q", f.read(8))[0]
        if length > 100_000_000:
            raise ValueError("Safetensors header too large")
        return json.loads(f.read(length)), 8 + length


def tensor_array(path, key):
    import numpy as np
    header, offset = tensor_header(path)
    info = header[key]
    dtype = dict(BF16="<u2", F32="<f4", F16="<f2", I64="<i8")[info["dtype"]]
    start, end = info["data_offsets"]
    if end - start != math.prod(info["shape"]) * np.dtype(dtype).itemsize or offset + end > path.stat().st_size:
        raise ValueError(f"Invalid safetensors bounds: {key}")
    return np.memmap(path, mode="r", offset=offset + start, dtype=dtype, shape=tuple(info["shape"])), info["dtype"]


class TensorFile:
    """Small safetensors writer accepting sequential slices of large tensors."""
    def __init__(self, path, tensors):
        offset, header, self.offsets = 0, {"__metadata__": {"format": "mlx"}}, {}
        for key, (shape, dtype) in tensors.items():
            length = math.prod(shape) * dict(F32=4, BF16=2, U32=4)[dtype]
            header[key] = dict(dtype=dtype, shape=list(shape), data_offsets=[offset, offset + length])
            self.offsets[key] = (offset, offset + length)
            offset += length
        raw = json.dumps(header, separators=(",", ":")).encode()
        raw += b" " * (-len(raw) % 8)
        self.base = len(raw) + 8
        self.file = path.open("xb")
        self.file.write(struct.pack("<Q", len(raw)))
        self.file.write(raw)
        self.file.truncate(self.base + offset)
        self.written = {k: 0 for k in tensors}

    def write(self, key, data):
        start, end = self.offsets[key]
        position = start + self.written[key]
        if position + len(data) > end:
            raise ValueError(f"Tensor overflow: {key}")
        self.file.seek(self.base + position)
        self.file.write(data)
        self.written[key] += len(data)

    def close(self):
        self.file.close()
        for key, (start, end) in self.offsets.items():
            if self.written[key] != end - start:
                raise ValueError(f"Incomplete tensor: {key}")


def sources(checkpoint):
    """Inventory headers only; PLE shards stay separate until row streaming."""
    found, constants, omitted = {}, [], []
    files = sorted(checkpoint.glob("*.safetensors"))
    if not files:
        raise ValueError("No local HF safetensors files")
    for path in files:
        header, _ = tensor_header(path)
        for original, info in header.items():
            if original == "__metadata__":
                continue
            key = rules.canonical_name(original)
            if key is None:
                omitted.append(original)
                continue
            if key.rsplit(".", 1)[-1] in rules.CONSTANTS:
                constants.append((path, original, key))
                continue
            shape = tuple(info["shape"])
            if info["dtype"] not in ("BF16", "F32", "F16"):
                raise ValueError(f"Nonfloating weight: {original}")
            expert = rules.EXPERT_RE.search(key)
            if expert:
                name = rules.EXPERT_RE.sub(f".mlp.switch_mlp.{expert[2]}_proj.weight", key)
                found.setdefault(name, []).append((int(expert[1]), path, original, shape, "expert"))
                continue
            match = rules.SHARD_RE.search(key)
            if match:
                name = rules.SHARD_RE.sub(".ngram_embedding.weight", key)
                entry = (int(match[1]), path, original, shape, None)
                found.setdefault(name, []).append(entry)
                continue
            entries = [(key, None)]
            if key.endswith("mlp.experts.gate_up_proj"):
                base = key[:-len("experts.gate_up_proj")]
                entries = [(base + "switch_mlp.gate_proj.weight", 0),
                           (base + "switch_mlp.up_proj.weight", 1)]
            elif key.endswith("mlp.experts.down_proj"):
                entries = [(key[:-len("experts.down_proj")] + "switch_mlp.down_proj.weight", None)]
            for name, half in entries:
                if name in found:
                    raise ValueError(f"Duplicate mapped tensor: {name}")
                found[name] = [(0, path, original, shape, half)]
    for key, entries in found.items():
        entries.sort()
        if [e[0] for e in entries] != list(range(len(entries))):
            raise ValueError(f"Missing / duplicate PLE shards: {key}")
    return found, constants, omitted, files


def target_shape(key, entries):
    shape = list(entries[0][3])
    if entries[0][4] == "expert":
        if any(e[3] != tuple(shape) or e[4] != "expert" for e in entries):
            raise ValueError(f"Inconsistent expert dimensions: {key}")
        return (len(entries), *shape)
    if len(entries) > 1:
        if any(e[3][1:] != tuple(shape[1:]) for e in entries):
            raise ValueError(f"Inconsistent shard dimensions: {key}")
        shape[0] = sum(e[3][0] for e in entries)
    if entries[0][4] is not None:
        if shape[-2] % 2:
            raise ValueError(f"Odd fused gate/up dimension: {key}")
        shape[-2] //= 2
    if key.endswith("conv1d.weight"):
        shape[1], shape[2] = shape[2], shape[1]
    return tuple(shape)


def tensor_chunks(key, entries, max_bytes=32 * 1024 * 1024):
    import numpy as np
    for _, path, original, shape, half in entries:
        rows = max(1, max_bytes // (math.prod(shape[1:]) * 4))
        source, dtype = tensor_array(path, original)
        try:
            for start in range(0, shape[0], rows):
                sl = [slice(None)] * len(shape)
                sl[0] = slice(start, min(start + rows, shape[0]))
                if isinstance(half, int):
                    sl[-2] = slice(half * (shape[-2] // 2), (half + 1) * (shape[-2] // 2))
                raw = source[tuple(sl)]
                value = (raw.astype(np.uint32) << 16).view(np.float32) if dtype == "BF16" else raw.astype(np.float32)
                if half == "expert":
                    value = value[None]
                if key.endswith("conv1d.weight"):
                    value = value.transpose(0, 2, 1)
                yield np.ascontiguousarray(value)
        finally:
            source._mmap.close()


def verify_manifest(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if actual != set(manifest["files"]) | {"manifest.json"}:
        raise ValueError("Manifest file inventory mismatch")
    for name, expected in manifest["files"].items():
        if sha256(directory / name) != expected:
            raise ValueError(f"Manifest SHA256 mismatch: {name}")
    return manifest


def convert(checkpoint, output, profile="mixed", group_size=64, ple_storage="q4"):
    import numpy as np
    checkpoint, output = Path(checkpoint), Path(output)
    if "restricted" in checkpoint.parts or "restricted" in output.parts:
        raise ValueError("Restricted paths are not conversion inputs/outputs")
    if output.exists():
        raise ValueError("Output directory must not exist")
    config = json.loads((checkpoint / "config.json").read_text())
    c = rules.text_config(config)
    expected = rules.parameter_shapes(c)
    inventory, constants, omitted, input_files = sources(checkpoint)
    if c.get("tie_word_embeddings", False):
        inventory.pop("lm_head.weight", None)
    if set(inventory) != set(expected):
        raise ValueError(f"Text tensor inventory mismatch: missing={sorted(set(expected) - set(inventory))}; "
                         f"unexpected={sorted(set(inventory) - set(expected))}")
    for key, entries in inventory.items():
        if target_shape(key, entries) != expected[key]:
            raise ValueError(f"Shape mismatch: {key}: {target_shape(key, entries)} != {expected[key]}")
    for path, original, key in constants:
        layer = int(key.split("layers.")[1].split(".")[0]) + 1
        layout = rules.ngram_layout(c, c["ple_layer_ids"].index(layer))
        attr = dict(zip(rules.CONSTANTS, ("multipliers", "sizes", "offsets")))[key.rsplit(".", 1)[-1]]
        value, dtype = tensor_array(path, original)
        if dtype != "I64" or value.tolist() != layout[attr]:
            raise ValueError(f"Hash constant mismatch: {key}")
        value._mmap.close()
    # Import MLX only if necessary; conversion without quantization works on
    # non-Metal machines and does not construct a second copy of the model.
    quantizers = {k: rules.quantization_for(k, shape, profile, group_size) for k, shape in expected.items()}
    mx = None
    if any(quantizers.values()):
        import importlib.metadata
        if importlib.metadata.version("mlx") != "0.31.2" or importlib.metadata.version("mlx-lm") != "0.31.3":
            raise ValueError("Quantized conversion requires pinned mlx 0.31.2 / mlx-lm 0.31.3")
        import mlx.core as mx
        mx.eval(mx.array([0]))  # fail before creating output on unavailable device
    output.mkdir(parents=True)
    descriptors, weight_map, quantization = {}, {}, dict(group_size=group_size, bits=4, mode="affine")
    dtype_name = "F32" if profile == "fp32" else "BF16"
    for ordinal, (key, entries) in enumerate(sorted(inventory.items())):
        shape, quant = expected[key], quantizers[key]
        if ".ngram_embedding." in key:
            layer = int(key.split("layers.")[1].split(".")[0]) + 1
            name = f"ple-{layer}.{ple_storage}.bin"
            descriptor = dict(path=name, rows=shape[0], dim=shape[1], storage=ple_storage, group_size=shape[1])
            with (output / name).open("xb") as f:
                for chunk in tensor_chunks(key, entries):
                    f.write(rules.encode_rows(chunk, ple_storage).tobytes())
            descriptors[str(layer)] = descriptor
            continue
        name = f"model-{ordinal:05d}.safetensors"
        tensors = {key: (shape, dtype_name)}
        if quant:
            base = key[:-len("weight")]
            tensors = {key: ((*shape[:-1], shape[-1] * quant["bits"] // 32), "U32"),
                       base + "scales": ((*shape[:-1], shape[-1] // group_size), "BF16"),
                       base + "biases": ((*shape[:-1], shape[-1] // group_size), "BF16")}
            quantization[key[:-len(".weight")]] = quant
        writer = TensorFile(output / name, tensors)
        for chunk in tensor_chunks(key, entries):
            if quant:
                arr = mx.array(chunk).astype(mx.bfloat16)
                packed, scales, biases = mx.quantize(arr, **quant)
                mx.eval(packed, scales, biases)
                writer.write(key, np.array(packed).astype("<u4").tobytes())
                writer.write(base + "scales", np.array(scales.view(mx.uint16)).astype("<u2").tobytes())
                writer.write(base + "biases", np.array(biases.view(mx.uint16)).astype("<u2").tobytes())
            else:
                writer.write(key, rules.encode_rows(chunk, "fp32" if profile == "fp32" else "bf16").tobytes())
        writer.close()
        for tensor in tensors:
            weight_map[tensor] = name
    config_out = dict(model_type="qwen4_exp", architectures=["Model"], model_file="qwen4_exp.py",
                      text_config=c, jw_format="hf-zero-centered-v1", ple_tables=descriptors,
                      eos_token_id=c.get("eos_token_id"), tie_word_embeddings=c.get("tie_word_embeddings", False))
    if any(quantizers.values()):
        config_out["quantization"] = quantization
    (output / "config.json").write_text(json.dumps(config_out, indent=2) + "\n")
    (output / "model.safetensors.index.json").write_text(json.dumps(dict(weight_map=weight_map), indent=2) + "\n")
    owned = Path(__file__).resolve().parents[1] / "joulewise/align/models"
    for name in ("qwen4_exp.py", "qwen4_exp_tables.py"):
        shutil.copyfile(owned / name, output / name)
    for name in ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "generation_config.json", "chat_template.jinja"):
        if (checkpoint / name).is_file():
            shutil.copyfile(checkpoint / name, output / name)
    manifest = dict(format="joulewise-qwen4-exp-v1", pins=dict(mlx="0.31.2", mlx_lm="0.31.3"),
                    profile=profile, ple_storage=ple_storage, norm_representation="raw HF zero-centered; runtime 1 + w",
                    omitted_keys=omitted, qsa_indexer="retained unquantized; strict shape inventory checked",
                    inputs={p.name: sha256(p) for p in [checkpoint / "config.json", *input_files]},
                    files={p.name: sha256(p) for p in sorted(output.iterdir()) if p.is_file()})
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    verify_manifest(output)
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("checkpoint", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--profile", choices=("fp32", "bf16", "mixed", "3", "4", "6", "8"), default="mixed")
    p.add_argument("--group-size", type=int, choices=(32, 64, 128), default=64)
    p.add_argument("--ple-storage", choices=("fp32", "bf16", "q4", "q8"), default="q4")
    a = p.parse_args()
    manifest = convert(a.checkpoint, a.output, a.profile, a.group_size, a.ple_storage)
    print(json.dumps(dict(output=str(a.output), payload_files=len(manifest["files"]),
                          manifest_sha256=sha256(a.output / "manifest.json"))))


if __name__ == "__main__":
    main()
