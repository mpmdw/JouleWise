#!/usr/bin/env python3
"""Build the RL-182 Flash-Next MLX artifact with one authenticated source shard on disk."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.metadata
import json
import math
import os
import re
import stat
import struct
import urllib.request
from dataclasses import dataclass
from pathlib import Path


REPO_ID = "Qwen/Qwen3.8-Flash-Next"
REVISION = "de4b8e4d43b917e7706784d8bb445c9af86a3540"
CONVERTER_SHA = "18eed9d2843e7f981dc22f8c8de3daa52e766bee23af29af88a81541192e965f"
MODULE_SHA = "f4ec75d16f0af0517b63e202abeef704c9a775e9111949ab003250d51d982c37"
INDEX = "model.safetensors.index.json"
TOKENIZER_FILES = ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json",
                   "generation_config.json", "chat_template.jinja", "vocab.json", "merges.txt")
REQUIRED = {"config.json", INDEX, "tokenizer.json", "tokenizer_config.json", "chat_template.jinja"}
RESERVE = 40_000_000_000 + 30_000_000_000
CONTROL_HEADROOM = 64 * 2**20
BLOCK = 8 * 2**20
PLACEHOLDER = "0" * 64


def json_bytes(value):
    return (json.dumps(value, indent=2) + "\n").encode()


def unique_object(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON key")
    return value


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def is_digest(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def range_sha(path, start, size):
    with path.open("rb") as f:
        f.seek(start)
        digest = hashlib.sha256()
        while size:
            block = f.read(min(BLOCK, size))
            if not block:
                raise ValueError(f"short read in {path.name} at {f.tell()}")
            digest.update(block)
            size -= len(block)
    return digest.hexdigest()


def prefix_length(raw, size):
    length, = struct.unpack("<Q", raw)
    if not 2 <= length <= min(100_000_000, size - 8):
        raise ValueError("invalid safetensors header length")
    return length


@dataclass(frozen=True)
class Input:
    name: str
    size: int
    checksum: str


class HubSource:
    """Read pinned metadata and bounded HTTP ranges, with no Hub/Xet disk cache."""

    identity = {"repo": REPO_ID, "revision": REVISION}

    def __init__(self):
        from huggingface_hub import HfApi

        info = HfApi().model_info(REPO_ID, revision=REVISION, files_metadata=True)
        if info.sha != REVISION:
            raise ValueError("Hub did not resolve the pinned revision")
        metadata = {item.rfilename: item for item in info.siblings}
        self.small = {}
        for name in sorted(REQUIRED | (set(TOKENIZER_FILES) & metadata.keys())):
            item = metadata.get(name)
            if item is None or type(item.size) is not int or not 0 < item.size <= 64 * 2**20:
                raise ValueError(f"missing or oversized Hub metadata file: {name}")
            with self.request(name) as response:
                raw = response.read(item.size + 1)
            if item.lfs:
                valid = sha(raw) == item.lfs.sha256
            else:
                valid = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == item.blob_id
            if len(raw) != item.size or not valid:
                raise ValueError(f"Hub metadata authentication failed: {name}")
            self.small[name] = raw
        names = sorted(set(parse(self.small[INDEX])["weight_map"].values()))
        if len(names) != 131 or any(not re.fullmatch(r"model-[0-9]+-of-[0-9]+\.safetensors", n) for n in names):
            raise ValueError("unexpected official shard inventory")
        self.inputs = []
        for name in names:
            item = metadata.get(name)
            if (item is None or not item.lfs or not is_digest(item.lfs.sha256)
                    or type(item.size) is not int or not 8 < item.size == item.lfs.size):
                raise ValueError(f"missing Hub LFS identity: {name}")
            self.inputs.append(Input(name, item.size, item.lfs.sha256))

    @staticmethod
    def request(name, start=None, stop=None, total=None):
        headers = {"Accept-Encoding": "identity"}
        if start is not None:
            headers["Range"] = f"bytes={start}-{stop - 1}"
        url = f"https://huggingface.co/{REPO_ID}/resolve/{REVISION}/{name}"
        response = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=90)
        if start is not None and (response.status != 206 or response.headers.get("Content-Range")
                                  != f"bytes {start}-{stop - 1}/{total}"):
            response.close()
            raise ValueError(f"server did not honor the exact byte range for {name}")
        return response

    def header(self, item):
        with self.request(item.name, 0, 8, item.size) as response:
            prefix = response.read(8)
        size = prefix_length(prefix, item.size)
        with self.request(item.name, 8, 8 + size, item.size) as response:
            raw = response.read(size)
        if len(raw) != size:
            raise ValueError(f"short Hub header: {item.name}")
        return prefix + raw

    def download(self, item, start):
        if start:
            return self.request(item.name, start, item.size, item.size)
        return self.request(item.name)


@dataclass(frozen=True)
class Span:
    file: str
    start: int
    size: int


@dataclass(frozen=True)
class Piece:
    source: str
    key: str
    shape: tuple
    kind: str
    ordinal: int = 0

    def canonical(self, staged):
        return self.ordinal, staged, self.key, self.shape, self.kind


@dataclass(frozen=True)
class Write:
    piece: Piece
    spans: tuple
    bits: int = 0


def safetensors_header(tensors):
    """Match the pinned converter's TensorFile header and payload order."""
    header = {"__metadata__": {"format": "mlx"}}
    offset = 0
    for name, shape, dtype, size in tensors:
        header[name] = dict(dtype=dtype, shape=list(shape), data_offsets=[offset, offset + size])
        offset += size
    raw = json.dumps(header, separators=(",", ":")).encode()
    raw += b" " * (-len(raw) % 8)
    return struct.pack("<Q", len(raw)) + raw


def source_layout(source, canonical, rules):
    """Make a header-only inventory. Recheck each header after full LFS authentication."""
    index = parse(source.small[INDEX])["weight_map"]
    indexed = {item.name: set() for item in source.inputs}
    for key, name in index.items():
        indexed[name].add(key)
    weights, tables, constants, headers, omitted = {}, {}, {}, {}, []
    for item in source.inputs:
        raw = source.header(item)
        if prefix_length(raw[:8], item.size) != len(raw) - 8:
            raise ValueError(f"bad header size: {item.name}")
        headers[item.name] = len(raw), sha(raw)
        info = parse(raw[8:])
        info.pop("__metadata__", None)
        if info.keys() != indexed[item.name]:
            raise ValueError(f"source header and index disagree: {item.name}")
        end = 0
        for key, meta in sorted(info.items(), key=lambda entry: entry[1]["data_offsets"][0]):
            start, stop = meta["data_offsets"]
            if any(type(dim) is not int or dim < 1 for dim in meta["shape"]):
                raise ValueError(f"invalid source shape: {key}")
            if type(start) is not int or type(stop) is not int or start != end or stop < start:
                raise ValueError(f"invalid source offsets: {key}")
            end = stop
        if end + len(raw) != item.size:
            raise ValueError(f"source header does not cover file: {item.name}")
        for key, meta in info.items():
            name = rules.hf_to_mlx_key(key)
            if name is None:
                omitted.append(key)
                continue
            shape, dtype = tuple(meta["shape"]), meta["dtype"]
            kind = "plain"
            if rules.is_ngram_buffer_key(name):
                constants.setdefault(item.name, []).append((key, name))
                if dtype != "I64":
                    raise ValueError(f"unsupported hash-buffer dtype: {key}")
            elif dtype not in ("BF16", "F16", "F32"):
                raise ValueError(f"unsupported weight dtype: {key}")
            start, stop = meta["data_offsets"]
            if stop - start != math.prod(shape) * {"BF16": 2, "F16": 2, "F32": 4, "I64": 8}[dtype]:
                raise ValueError(f"source tensor byte count mismatch: {key}")
            if rules.is_ngram_buffer_key(name):
                continue
            table = canonical.SHARD_RE.search(name)
            expert = canonical.EXPERT_RE.match(name)
            if table:
                layer = int(name.split(".layers.", 1)[1].split(".", 1)[0])
                tables.setdefault(layer, []).append(Piece(item.name, key, shape, "ngram", int(table[1])))
                continue
            ordinal = 0
            if expert:
                head, e, proj = expert["head"], int(expert["e"]), expert["proj"]
                target = "down" if proj == "down" else "gate_up"
                ordinal = e if proj == "down" else 2 * e + (proj == "up")
                name, kind = f"{head}.mlp.switch_mlp.{target}_proj.weight", "expert"
            else:
                for suffix in ("gate_up_proj", "down_proj"):
                    if name.endswith(f".mlp.experts.{suffix}"):
                        name = name.removesuffix(f"experts.{suffix}") + f"switch_mlp.{suffix}.weight"
                if name.endswith("conv1d.weight") and len(shape) == 3 and shape[-1] != 1:
                    kind = "conv"
            weights.setdefault(name, []).append(Piece(item.name, key, shape, kind, ordinal))
    for name, pieces in [*weights.items(), *tables.items()]:
        pieces.sort(key=lambda piece: piece.ordinal)
        if [piece.ordinal for piece in pieces] != list(range(len(pieces))) or len({p.kind for p in pieces}) != 1:
            raise ValueError(f"missing, duplicate or incompatible tensor pieces: {name}")
    return weights, tables, constants, headers, omitted


class Plan:
    def __init__(self, source, canonical, rules, module, profile, shard_bytes):
        self.source, self.canonical, self.rules = source, canonical, rules
        self.group_size, self.ngram_group = 64, 32
        self.profile = profile
        self.writes = {item.name: [] for item in source.inputs}
        self.tensors, self.files = {}, {}
        self.headers, self.sizes = {}, {}
        self.ple = rules.ple_storage_for(profile, None, self.group_size)
        if self.ple != "bf16" or shard_bytes < 1:
            raise ValueError("this converter requires bf16 PLE and a positive output shard size")
        config = canonical._text_config(parse(source.small["config.json"]))
        expected, self.args = canonical.expected_parameters(rules, config)
        weights, tables, self.constants, self.source_headers, self.omitted = source_layout(source, canonical, rules)
        if self.args.tie_word_embeddings:
            weights.pop("language_model.lm_head.weight", None)
        if weights.keys() != expected.keys():
            raise ValueError(f"canonical inventory mismatch: missing={sorted(expected.keys() - weights.keys())[:8]}, "
                             f"unexpected={sorted(weights.keys() - expected.keys())[:8]}")
        quant, weight_map = self.model_files(weights, expected, shard_bytes)
        ngram_layers, self.ngram_manifest = self.table_files(tables)
        config_out = dict(model_type="qwen4_exp", architectures=["Qwen4ExpForConditionalGeneration"],
                          model_file="qwen4_exp.py", jw_format=canonical.FORMAT, text_config=config,
                          ngram_tables=dict(dir=".", io="mmap", layers=ngram_layers),
                          eos_token_id=config.get("eos_token_id"),
                          tie_word_embeddings=bool(config.get("tie_word_embeddings")))
        if quant:
            config_out["quantization"] = dict(group_size=self.group_size, bits=next(iter(quant.values()))["bits"],
                                              mode="affine", **quant)
        self.files.update({"config.json": json_bytes(config_out), INDEX: json_bytes(dict(weight_map=weight_map)),
                           "qwen4_exp.py": module})
        self.files.update({name: source.small[name] for name in TOKENIZER_FILES if name in source.small})
        self.sizes.update({name: len(raw) for name, raw in self.files.items()})
        self.quant = sorted(quant)
        self.input_names = [item.name for item in source.inputs]
        placeholder_rows = [[PLACEHOLDER] * (1 + sum(len(w.spans) for w in self.writes[item.name]))
                            for item in source.inputs]
        placeholder = self.manifest(dict.fromkeys(self.sizes, PLACEHOLDER), placeholder_rows,
                                    dict.fromkeys(self.tensors, PLACEHOLDER))
        self.plan_id = sha(json_bytes([placeholder, self.source_headers, self.sizes,
                                       {name: sha(raw) for name, raw in (self.headers | self.files).items()}]))
        self.manifest_size = len(json_bytes(placeholder))
        self.journal_size = len(json_bytes(self.journal(placeholder_rows)))

    def model_files(self, weights, expected, shard_bytes):
        quant, weight_map = {}, {}
        groups, group, group_size = [], [], 0
        for key, pieces in sorted(weights.items()):
            shape = self.canonical.target_shape([piece.canonical(None) for piece in pieces])
            if shape != expected[key]:
                raise ValueError(f"canonical shape mismatch: {key}: {shape} != {expected[key]}")
            stem = key.removesuffix(".weight")
            q = self.rules.quantization_for(stem, shape, self.profile, self.group_size) if stem != key else None
            bits = q["bits"] if q else 0
            specs = [(key, shape, "BF16")]
            if q:
                quant[stem] = q
                side = (*shape[:-1], shape[-1] // self.group_size)
                specs = [(key, (*shape[:-1], shape[-1] * bits // 32), "U32"),
                         (stem + ".scales", side, "BF16"), (stem + ".biases", side, "BF16")]
            specs = [(name, dims, dtype, self.canonical.tensor_bytes(dims, dtype)) for name, dims, dtype in specs]
            size = sum(spec[3] for spec in specs)
            if group and group_size + size > shard_bytes:
                groups.append(group)
                group, group_size = [], 0
            group.append((pieces, bits, specs))
            group_size += size
        if group:
            groups.append(group)
        for number, group in enumerate(groups, 1):
            filename = f"model-{number:05d}-of-{len(groups):05d}.safetensors"
            raw = safetensors_header(spec for _, _, specs in group for spec in specs)
            self.headers[filename] = raw
            position = len(raw)
            for pieces, bits, specs in group:
                # Split-expert pieces have equal dimensions and tile each of the three packed tensors.
                spans = []
                for name, shape, dtype, size in specs:
                    weight_map[name] = filename
                    self.tensors[name] = (shape, dtype, Span(filename, position, size))
                    step, remainder = divmod(size, len(pieces))
                    if remainder:
                        raise ValueError(f"unaligned tensor pieces: {name}")
                    spans.append([Span(filename, position + step * i, step) for i in range(len(pieces))])
                    position += size
                for piece, targets in zip(pieces, zip(*spans)):
                    self.writes[piece.source].append(Write(piece, targets, bits))
            self.sizes[filename] = position
        return quant, weight_map

    def table_files(self, tables):
        specs = {lid - 1: self.rules.NgramHashSpec(self.args, i) for i, lid in enumerate(self.args.ple_layer_ids)}
        if specs.keys() != tables.keys():
            raise ValueError("canonical PLE table inventory mismatch")
        layers, manifest = {}, {}
        for layer, pieces in sorted(tables.items()):
            spec = specs[layer]
            rows, dim = spec.padded_vocab_size, spec.head_dim
            record = self.rules.ngram_record_layout(self.ple, dim, self.ngram_group)["record_bytes"]
            if any(len(p.shape) != 2 or p.shape[1] != dim for p in pieces) or sum(p.shape[0] for p in pieces) != rows:
                raise ValueError(f"canonical PLE shape mismatch: layer {layer}")
            filename = f"ngram-L{layer:03d}.{self.ple}.bin"
            layers[str(layer)] = dict(file=filename, rows=rows, dim=dim, format=self.ple, group_size=self.ngram_group)
            self.headers[filename] = b""
            self.sizes[filename] = rows * record
            key = f"language_model.model.layers.{layer}.ple.ple_embedding.ngram_embedding.weight"
            self.tensors[key] = ((rows, dim), "BF16", Span(filename, 0, rows * record))
            row, source_spans = 0, []
            for piece in pieces:
                count = piece.shape[0]
                target = Span(filename, row * record, count * record)
                self.writes[piece.source].append(Write(piece, (target,)))
                source_spans.append(dict(input_file=piece.source, tensor=piece.key, row_start=row, row_stop=row + count,
                                         byte_start=target.start, byte_stop=target.start + target.size))
                row += count
            manifest[str(layer)] = dict(layers[str(layer)], size_bytes=rows * record, source_shards=source_spans)
        return layers, manifest

    def manifest(self, files, rows, digests):
        inputs = {"config.json": sha(self.source.small["config.json"])}
        inputs.update({name: row[0] for name, row in zip(self.input_names, rows)})
        tensors = {key: dict(name=key, shape=list(shape), dtype=dtype, sha256=digests[key],
                             file=span.file, byte_offset=span.start, byte_length=span.size)
                   for key, (shape, dtype, span) in sorted(self.tensors.items())}
        source = dict(self.source.identity, sha256={item.name: item.checksum for item in self.source.inputs},
                      metadata_sha256={name: sha(raw) for name, raw in sorted(self.source.small.items())})
        return dict(format=self.canonical.FORMAT, pins=self.canonical.PINS, profile=self.profile,
                    group_size=self.group_size, ngram_storage=self.ple, ngram_tables=self.ngram_manifest,
                    module_sha256=files["qwen4_exp.py"], norm_representation="raw HF zero-centered; runtime 1 + w",
                    omitted_keys=self.omitted, quantized=self.quant, digest=self.canonical.digest_scheme(),
                    inputs=inputs, files=dict(sorted(files.items())), source=source, tensors=tensors)

    def journal(self, rows):
        return dict(schema=1, plan_sha256=self.plan_id, committed=rows)

    def span_list(self, name):
        return [span for write in self.writes[name] for span in write.spans]


def mlx_encoding(canonical, rules, write, stage):
    import mlx.core as mx
    import numpy as np

    raw_bf16 = not write.bits
    for chunk in canonical.tensor_chunks([write.piece.canonical(stage)], raw_bf16=raw_bf16):
        if write.bits:
            arr = mx.array(chunk).astype(mx.bfloat16).reshape(-1, chunk.shape[-1])
            packed, scales, biases = mx.quantize(arr, group_size=64, bits=write.bits)
            mx.eval(packed, scales, biases)
            yield (np.array(packed).astype("<u4").tobytes(),
                   np.array(scales.view(mx.uint16)).astype("<u2").tobytes(),
                   np.array(biases.view(mx.uint16)).astype("<u2").tobytes())
        elif chunk.dtype == np.dtype("<u2"):
            yield (chunk.tobytes(),)
        elif write.piece.kind == "ngram":
            yield (rules.encode_ngram_rows(chunk, "bf16", 32).tobytes(),)
        else:
            yield (rules._f32_to_bf16_bits(chunk).tobytes(),)


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write(pending, path, raw):
    with pending.open("xb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    pending.replace(path)
    sync_dir(path.parent)
    if pending.parent != path.parent:
        sync_dir(pending.parent)


def regular(path):
    attrs = path.lstat()
    if not stat.S_ISREG(attrs.st_mode) or attrs.st_nlink != 1:
        raise ValueError(f"expected a private regular file: {path.name}")
    return attrs


def existing(path):
    try:
        return regular(path)
    except FileNotFoundError:
        return None


class Budget:
    def __init__(self, path, plan, reserve):
        unit = os.statvfs(path).f_frsize
        if unit <= 0 or reserve < 0:
            raise ValueError("invalid disk allocation unit or reserve")
        def rounded(size):
            return ((size + unit - 1) // unit) * unit

        self.artifact = sum(rounded(size) for size in [*plan.sizes.values(), plan.manifest_size])
        self.stage = max(rounded(item.size) for item in plan.source.inputs)
        self.control = 2 * rounded(plan.journal_size) + CONTROL_HEADROOM
        self.peak = self.artifact + self.stage + self.control
        self.reserve = reserve

    def check(self, path, credit=0):
        need = self.peak - credit + self.reserve
        fs = os.statvfs(path)
        free = fs.f_bavail * fs.f_frsize
        if free < need:
            raise ValueError(f"short disk: {free} free bytes, {need} required with reserve and resume credit")

    def report(self):
        return dict(peak_extra_disk_bytes=self.peak, artifact_allocation_bytes=self.artifact,
                    one_source_allocation_bytes=self.stage, control_allocation_bytes=self.control,
                    reserve_bytes=self.reserve, fresh_free_required_bytes=self.peak + self.reserve)


class Conversion:
    def __init__(self, root, plan, budget, encode):
        self.root, self.plan, self.budget, self.encode = root, plan, budget, encode
        self.artifact = root / "artifact"
        self.journal = root / "journal.json"
        self.pending = root / "journal.new"
        self.manifest_pending = root / "manifest.new"
        self.manifest = self.artifact / "manifest.json"
        self.stages = [root / f"source-{i:03d}.part" for i in range(len(plan.source.inputs))]

    def validate_job(self):
        device = self.root.stat().st_dev
        expected = {self.journal, self.pending, self.manifest_pending, *self.stages}
        root_entries = set(self.root.iterdir())
        if root_entries - expected - {self.artifact}:
            raise ValueError("unexpected entry in conversion directory")
        if self.artifact in root_entries:
            attrs = self.artifact.lstat()
            if not stat.S_ISDIR(attrs.st_mode) or attrs.st_dev != device:
                raise ValueError("artifact must share the staging volume and be a real directory")
            files = set(self.artifact.iterdir())
            if any(file.name not in self.plan.sizes and file != self.manifest for file in files):
                raise ValueError("unexpected entry in artifact")
        else:
            files = set()
        limits = {self.journal: self.plan.journal_size, self.pending: self.plan.journal_size,
                  self.manifest: self.plan.manifest_size, self.manifest_pending: self.plan.manifest_size}
        limits.update(zip(self.stages, (item.size for item in self.plan.source.inputs)))
        limits.update({self.artifact / name: size for name, size in self.plan.sizes.items()})
        allocation = 0
        for path in (root_entries & expected) | files:
            attrs = regular(path)
            if attrs.st_dev != device or attrs.st_size > limits[path]:
                raise ValueError(f"file exceeds planned disk extent or is on another volume: {path.name}")
            allocation += attrs.st_blocks * 512
        if allocation > self.budget.peak:
            raise ValueError("conversion allocation exceeds the disk budget")
        return allocation

    def read_journal(self):
        if not self.journal.exists():
            if set(self.root.iterdir()) - {self.pending}:
                raise ValueError("conversion directory has payloads but no committed journal")
            return []
        data = parse(self.journal.read_bytes())
        rows = data["committed"]
        if (data != self.plan.journal(rows) or not isinstance(rows, list) or len(rows) > len(self.stages)
                or self.manifest.exists() and len(rows) != len(self.stages)):
            raise ValueError("journal does not match the conversion plan")
        for item, row in zip(self.plan.source.inputs, rows):
            spans = self.plan.span_list(item.name)
            if not isinstance(row, list) or len(row) != len(spans) + 1 or any(not is_digest(d) for d in row):
                raise ValueError(f"malformed journal row: {item.name}")
            self.verify_spans(spans, row[1:])
        return rows

    def prepare_artifact(self, started):
        self.artifact.mkdir(mode=0o700, exist_ok=True)
        sync_dir(self.root)
        for name, raw in (self.plan.files | self.plan.headers).items():
            path = self.artifact / name
            attrs = existing(path)
            if attrs is None and started:
                raise ValueError(f"missing output on resume: {name}")
            current = b""
            if attrs is not None:
                with path.open("rb") as f:
                    current = f.read(len(raw))
                if current != raw[:len(current)] or (started and current != raw):
                    raise ValueError(f"output header or metadata changed: {name}")
            if attrs is None or len(current) < len(raw):
                mode = "xb" if attrs is None else "ab"
                with path.open(mode) as f:
                    f.write(raw[len(current):])
                    f.flush()
                    os.fsync(f.fileno())
        sync_dir(self.artifact)

    def download(self, item, stage):
        attrs = existing(stage)
        start = attrs.st_size if attrs else 0
        if start != item.size:
            with self.plan.source.download(item, start) as response, stage.open("ab" if attrs else "xb") as f:
                remaining = item.size - start
                while remaining:
                    raw = response.read(min(BLOCK, remaining))
                    if not raw:
                        raise ValueError(f"short download: {item.name}")
                    f.write(raw)
                    remaining -= len(raw)
                if response.read(1):
                    stage.unlink()
                    raise ValueError(f"download exceeded the pinned byte count: {item.name}")
                f.flush()
                os.fsync(f.fileno())
        if range_sha(stage, 0, item.size) != item.checksum:
            stage.unlink()
            sync_dir(self.root)
            raise ValueError(f"source sha256 mismatch: {item.name}")
        size, checksum = self.plan.source_headers[item.name]
        if range_sha(stage, 0, size) != checksum:
            raise ValueError(f"authenticated source disagrees with the planned header: {item.name}")

    def verify_spans(self, spans, hashes):
        for span, checksum in zip(spans, hashes, strict=True):
            if range_sha(self.artifact / span.file, span.start, span.size) != checksum:
                raise ValueError(f"output span sha256 mismatch: {span.file}@{span.start}")

    def convert_shard(self, item, stage):
        plan = self.plan
        for key, mapped in plan.constants.get(item.name, []):
            values, dtype = plan.canonical.tensor_array(stage, key)
            try:
                if dtype != "I64" or values.tolist() != plan.rules.ngram_buffer_expected(plan.args, mapped):
                    raise ValueError(f"n-gram hash buffer mismatch: {key}")
            finally:
                values._mmap.close()
        hashes, files = [], {}
        try:
            for write in plan.writes[item.name]:
                name = write.spans[0].file
                if name not in files:
                    files[name] = os.open(self.artifact / name, os.O_RDWR | os.O_NOFOLLOW)
                fd = files[name]
                offsets = [span.start for span in write.spans]
                digests = [hashlib.sha256() for span in write.spans]
                for chunk in self.encode(plan.canonical, plan.rules, write, stage):
                    for i, (raw, span) in enumerate(zip(chunk, write.spans, strict=True)):
                        if offsets[i] + len(raw) > span.start + span.size:
                            raise ValueError(f"encoder exceeded planned span: {write.piece.key}")
                        # A replay can encounter data already written before interruption.
                        if os.pread(fd, len(raw), offsets[i]) != raw:
                            if os.pwrite(fd, raw, offsets[i]) != len(raw):
                                raise OSError(f"short output write: {span.file}")
                        offsets[i] += len(raw)
                        digests[i].update(raw)
                if offsets != [span.start + span.size for span in write.spans]:
                    raise ValueError(f"encoder left an incomplete span: {write.piece.key}")
                hashes.extend(digest.hexdigest() for digest in digests)
            for fd in files.values():
                os.fsync(fd)
        finally:
            for fd in files.values():
                os.close(fd)
        self.verify_spans(plan.span_list(item.name), hashes)
        return [plan.canonical.sha256(stage), *hashes]

    def finish(self, rows):
        plan = self.plan
        for name, size in plan.sizes.items():
            if regular(self.artifact / name).st_size != size:
                raise ValueError(f"incomplete final output: {name}")
        digests = {name: range_sha(self.artifact / span.file, span.start, span.size)
                   for name, (_, _, span) in plan.tensors.items()}
        files = {p.name: d for p, d in plan.canonical.hash_files(
            [self.artifact / name for name in plan.sizes], nofollow=True).items()}
        raw = json_bytes(plan.manifest(files, rows, digests))
        if len(raw) != plan.manifest_size:
            raise ValueError("manifest exceeds its planned extent")
        if self.manifest.exists():
            if raw != self.manifest.read_bytes():
                raise ValueError("completed manifest disagrees with verified payload or journal")
        else:
            atomic_write(self.manifest_pending, self.manifest, raw)
        return sha(raw)

    def run(self):
        credit = self.validate_job()
        self.budget.check(self.root, credit)
        rows = self.read_journal()
        for pending in (self.pending, self.manifest_pending):
            pending.unlink(missing_ok=True)
        staged = [i for i, path in enumerate(self.stages) if path.exists()]
        if len(staged) > 1 or any(i > len(rows) for i in staged):
            raise ValueError("unexpected staging inventory")
        for i in staged:
            if i < len(rows):
                self.stages[i].unlink()
                sync_dir(self.root)
        if not self.journal.exists():
            atomic_write(self.pending, self.journal, json_bytes(self.plan.journal(rows)))
        self.prepare_artifact(bool(rows))
        for i in range(len(rows), len(self.stages)):
            item, stage = self.plan.source.inputs[i], self.stages[i]
            self.budget.check(self.root, self.validate_job())
            self.download(item, stage)
            rows.append(self.convert_shard(item, stage))
            raw = json_bytes(self.plan.journal(rows))
            if len(raw) > self.plan.journal_size:
                raise ValueError("journal exceeds its planned extent")
            atomic_write(self.pending, self.journal, raw)
            self.validate_job()
            stage.unlink()
            sync_dir(self.root)
            print(f"Verified and released source shard {i + 1}/{len(self.stages)}: {item.name}", flush=True)
        self.budget.check(self.root, self.validate_job())
        return self.finish(rows)


def stream(root, plan, *, reserve=RESERVE, plan_only=False, encode=mlx_encoding):
    root = Path(root).absolute()
    if "restricted" in root.resolve().parts or root.is_symlink():
        raise ValueError("use a private, non-symlink conversion directory")
    budget = Budget(root.parent, plan, reserve)
    print(json.dumps(budget.report()), flush=True)
    if plan_only:
        return None
    if not root.exists():
        budget.check(root.parent)
        root.mkdir(mode=0o700)
        sync_dir(root.parent)
    lock = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if os.fstat(lock).st_dev != root.parent.stat().st_dev:
            raise ValueError("conversion directory must share its parent's volume")
        return Conversion(root, plan, budget, encode).run()
    finally:
        os.close(lock)


def load_port(port):
    converter = port / "scripts" / "align_convert_qwen4_exp.py"
    model = port / "joulewise" / "align" / "models" / "qwen4_exp.py"
    if any("restricted" in p.resolve().parts for p in (converter, model)):
        raise ValueError("use a public canonical port checkout")
    raw, module = converter.read_bytes(), model.read_bytes()
    if sha(raw) != CONVERTER_SHA or sha(module) != MODULE_SHA:
        raise ValueError("use the canonical converter and model pinned at PR #683 head 97d780d59")
    import types

    canonical = types.ModuleType("align_convert_qwen4_exp")
    canonical.__file__ = str(converter)
    exec(compile(raw, str(converter), "exec", dont_inherit=True), canonical.__dict__)
    for package, version in canonical.PINS.items():
        if importlib.metadata.version(package) != version:
            raise ValueError(f"conversion requires {package}=={version}")
    rules = canonical._module_from_source(module, model)
    return canonical, rules, module


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="new or resumable work directory; artifact is under root/artifact")
    parser.add_argument("--port-checkout", type=Path, required=True, help="canonical port checkout at 97d780d59")
    parser.add_argument("--execution", choices=("engineering", "off-mbp"), required=True,
                        help="execution context declared by the operator")
    parser.add_argument("--profile", choices=("maxfit", "maxfit5", "bf16"), default="maxfit")
    auth = parser.add_mutually_exclusive_group(required=True)
    auth.add_argument("--plan-only", action="store_true", help="fetch only Hub metadata and safetensors headers")
    auth.add_argument("--allow-official-download", action="store_true", help="owner-authorized transfer of official weights")
    args = parser.parse_args(argv)
    try:
        canonical, rules, module = load_port(args.port_checkout)
        plan = Plan(HubSource(), canonical, rules, module, args.profile, canonical.SHARD_BYTES)
        manifest = stream(args.root, plan, plan_only=args.plan_only)
    except (OSError, ValueError, KeyError, TypeError, struct.error) as exc:
        parser.exit(1, f"Conversion refused: {exc}\n")
    if manifest:
        print(json.dumps(dict(artifact=str(args.root / "artifact"), manifest_sha256=manifest)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
