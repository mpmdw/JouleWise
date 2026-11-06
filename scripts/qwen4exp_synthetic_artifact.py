#!/usr/bin/env python3
"""Build a deterministic, full-shape canonical qwen4_exp rehearsal artifact.

This deliberately contains no model weights.  It uses the canonical module and
converter as the sole source of tensor names, shapes, quantization and shard
layout so that storage, mmap paging and allocation behaviour match conversion.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import align_convert_qwen4_exp as converter

COPY_FILES = ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json",
              "generation_config.json", "chat_template.jinja", "vocab.json", "merges.txt")
BLOCK_BYTES = 32 * 2**20


def _bf16(values):
    """Canonical round-to-nearest-even bf16 bit patterns."""
    import numpy as np
    bits = np.asarray(values, dtype="<f4").view("<u4")
    rounded = bits + np.uint32(0x7FFF) + ((bits >> 16) & 1)
    return (rounded >> 16).astype("<u2")


def hash_buffers(rules, args):
    """The valid deterministic I64 buffers a corresponding source has.

    They are converter inputs, not model parameters, and consequently are not
    serialized in canonical-v2.  Keeping their derivation here makes synthetic
    inventory audits cover that part of the converter contract too.
    """
    import numpy as np
    result = {}
    for layer_id in args.ple_layer_ids:
        layer = layer_id - 1
        prefix = f"language_model.model.layers.{layer}.self_attn."
        # Suffix spelling and values both come from the canonical module.
        for suffix in rules.NGRAM_BUFFER_SUFFIXES:
            key = prefix + suffix
            result[key] = np.asarray(rules.ngram_buffer_expected(args, key), dtype="<i8")
    return result


def artifact_plan(config, profile, group_size=64, shard_bytes=converter.SHARD_BYTES):
    """Return converter-derived rules, args, tensor/shard and n-gram plans."""
    rules = converter.load_rules()
    text = converter._text_config(config)
    expected, args = converter.expected_parameters(rules, text)
    quantizers = {key: rules.quantization_for(key[:-len(".weight")], shape, profile, group_size)
                  for key, shape in expected.items() if key.endswith(".weight")}
    plan = []
    dtype = "BF16"
    for key, shape in sorted(expected.items()):
        quant = quantizers.get(key)
        tensors = {key: (shape, dtype)}
        if quant:
            base = key[:-len("weight")]
            tensors = {key: ((*shape[:-1], shape[-1] * quant["bits"] // 32), "U32"),
                       base + "scales": ((*shape[:-1], shape[-1] // group_size), "BF16"),
                       base + "biases": ((*shape[:-1], shape[-1] // group_size), "BF16")}
        plan.append((key, shape, quant, tensors,
                     sum(converter.tensor_bytes(*spec) for spec in tensors.values())))
    shards, current, size = [], [], 0
    for item in plan:
        if current and size + item[4] > shard_bytes:
            shards.append(current)
            current, size = [], 0
        current.append(item)
        size += item[4]
    if current:
        shards.append(current)
    storage = rules.ple_storage_for(profile, None, group_size)
    specs = {lid - 1: rules.NgramHashSpec(args, i) for i, lid in enumerate(args.ple_layer_ids)}
    return rules, text, args, plan, shards, storage, specs


def predicted_bytes(config, profile, shard_bytes=converter.SHARD_BYTES):
    """Exact payload bytes (headers excluded), useful before allocating disk."""
    rules, _, _, plan, _, storage, specs = artifact_plan(config, profile, shard_bytes=shard_bytes)
    weights = sum(item[4] for item in plan)
    ngrams = sum(s.padded_vocab_size * rules.ngram_record_layout(storage, s.head_dim, 32)["record_bytes"]
                 for s in specs.values())
    return weights + ngrams


def _write_random(writer, name, shape, dtype, rng):
    import numpy as np
    count = math.prod(shape)
    itemsize = converter._TENSOR_ITEMSIZE[dtype]
    per = max(1, BLOCK_BYTES // itemsize)
    for start in range(0, count, per):
        n = min(per, count - start)
        if dtype == "U32":
            data = rng.integers(0, 2**32, n, dtype="<u4")
        else:
            data = _bf16(rng.standard_normal(n, dtype=np.float32) * np.float32(0.02))
        writer.write(name, data.tobytes())


def build(config_path, small_files, output, profile="maxfit", seed=0,
          shard_bytes=converter.SHARD_BYTES):
    import numpy as np
    config_path, small_files, output = map(Path, (config_path, small_files, output))
    if output.exists():
        raise ValueError("output directory must not exist")
    config = json.loads(config_path.read_text())
    rules, text, args, plan, shards, storage, specs = artifact_plan(
        config, profile, shard_bytes=shard_bytes)
    # Exercise/validate the hash contract even though canonical artifacts do
    # not carry source-only buffers.
    hash_buffers(rules, args)
    output.mkdir(parents=True)
    rng = np.random.default_rng(seed)
    weight_map, quant_cfg = {}, {}
    for number, shard in enumerate(shards, 1):
        filename = f"model-{number:05d}-of-{len(shards):05d}.safetensors"
        writer = converter.TensorFile(output / filename,
                                      {name: spec for item in shard for name, spec in item[3].items()})
        for key, _, quant, tensors, _ in shard:
            for name, (shape, dtype) in tensors.items():
                _write_random(writer, name, shape, dtype, rng)
                weight_map[name] = filename
            if quant:
                quant_cfg[key[:-len(".weight")]] = quant
        writer.close()

    ngram_layers, ngram_manifest = {}, {}
    for layer, spec in sorted(specs.items()):
        layout = rules.ngram_record_layout(storage, spec.head_dim, 32)
        name = f"ngram-L{layer:03d}.{storage}.bin"
        total = spec.padded_vocab_size * layout["record_bytes"]
        with (output / name).open("xb") as stream:
            remaining = total
            while remaining:
                n = min(BLOCK_BYTES, remaining)
                stream.write(rng.integers(0, 256, n, dtype=np.uint8).tobytes())
                remaining -= n
        descriptor = dict(file=name, rows=spec.padded_vocab_size, dim=spec.head_dim,
                          format=storage, group_size=32)
        ngram_layers[str(layer)] = descriptor
        ngram_manifest[str(layer)] = dict(descriptor, size_bytes=total, source_shards=[])

    config_out = dict(model_type="qwen4_exp", architectures=["Qwen4ExpForConditionalGeneration"],
                      model_file="qwen4_exp.py", jw_format=converter.FORMAT, text_config=text,
                      ngram_tables=dict(dir=".", io="mmap", layers=ngram_layers),
                      eos_token_id=text.get("eos_token_id"),
                      tie_word_embeddings=bool(text.get("tie_word_embeddings")))
    if quant_cfg:
        first = next(iter(quant_cfg.values()))
        config_out["quantization"] = dict(group_size=64, bits=first["bits"], mode="affine", **quant_cfg)
    (output / "config.json").write_text(json.dumps(config_out, indent=2) + "\n")
    (output / "model.safetensors.index.json").write_text(json.dumps({"weight_map": weight_map}, indent=2) + "\n")
    shutil.copyfile(converter.MODULE_FILE, output / "qwen4_exp.py")
    for name in COPY_FILES:
        source = small_files / name
        if source.is_file():
            shutil.copyfile(source, output / name)
    outputs = converter.hash_files(sorted(p for p in output.iterdir() if p.is_file()), nofollow=True)
    manifest = dict(format=converter.FORMAT, pins=converter.PINS, profile=profile, group_size=64,
                    ngram_storage=storage, ngram_tables=ngram_manifest,
                    module_sha256=outputs[output / "qwen4_exp.py"],
                    norm_representation="raw HF zero-centered; runtime 1 + w", omitted_keys=[],
                    quantized=sorted(quant_cfg), digest=converter.digest_scheme(), inputs={},
                    files={p.name: digest for p, digest in outputs.items()}, synthetic=True, seed=seed)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    converter._verify(output, known_digests=manifest["files"])
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("build")
    command.add_argument("--profile", choices=("maxfit", "maxfit5"), required=True)
    command.add_argument("--config", type=Path, required=True)
    command.add_argument("--small-files", type=Path, required=True)
    command.add_argument("--out", type=Path, required=True)
    command.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)
    build(args.config, args.small_files, args.out, args.profile, args.seed)
    print(json.dumps({"artifact": str(args.out), "manifest_sha256": converter.sha256(args.out / "manifest.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
