#!/usr/bin/env python3
"""Offline, streaming HF -> canonical MLX ``qwen4_exp`` (Qwen3.8-Flash-Next).

Converts a local HF checkpoint (the released bf16 ``Qwen4ExpForConditional
Generation`` serialization, or an fp32 one) into the format loaded by
``joulewise/align/models/qwen4_exp.py`` through mlx-lm 0.31.3's
``model_file`` hook. Started from the Sol port's converter
(lane/2026-11-05-align-flashnext-port, scripts/align_convert_qwen4_exp.py):

* Streaming. Shard headers are inventoried first; every tensor is then read
  as bounded row slices of a read-only memmap and written into output shards
  of at most ``--shard-gb`` (4 GiB). Nothing materialises the checkpoint or
  builds a second model copy.
* Raw bf16 passthrough. bf16 sources are copied as their uint16 bit patterns
  (no fp32 expansion, no re-rounding). The reader parses safetensors headers
  itself; it never uses ``safetensors.safe_open(framework="mlx")``, which goes
  through numpy and cannot read bf16 (differential D1, the twin converter's
  bug). The parity test cross-checks the bytes against ``mx.load``.
* Precision profiles (``quantization_for`` in the module): ``maxfit`` (the
  GOAL target: 6-bit group-64 routed experts, everything else native bf16,
  the n-gram table bf16 on disk), ``maxfit5`` (5-bit fallback), ``bf16``,
  ``fp32``, ``mixed``.
* The n-gram PLE table is never an MLX weight: its shards are appended into one
  memory-mappable record file per PLE layer (``NgramTable`` format).
* Routed experts become the fused ``switch_mlp.gate_up_proj`` [E, 2I, H] (gate
  rows first) and ``down_proj`` [E, H, I].
* ``manifest.json``: sha256 of every input and output file; a failed
  conversion has no manifest. The shared name/shape/precision rules are the
  module's own (one source of truth), so this script imports mlx.
"""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import stat
import struct
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MODULE_FILE = REPO / "joulewise" / "align" / "models" / "qwen4_exp.py"
FORMAT = "joulewise-qwen4-exp-canonical-v2"
PINS = {"mlx": "0.31.2", "mlx-lm": "0.31.3"}
# sha256 of joulewise/align/models/qwen4_exp.py that load_verified_model runs by
# default. Rebind it with every module change (the canonical test checks it
# against the file; canonical.md records it under "Pin").
MODULE_SHA256 = "ce0800b90be398d49b5561539e987d347ae05a11b2ae3cef7f05ba6c612081d6"
EXPERT_RE = re.compile(r"^(?P<head>.+)\.mlp\.experts\.(?P<e>\d+)\.(?P<proj>gate|up|down)_proj\.weight$")
SHARD_RE = re.compile(r"\.ngram_embedding\.shard_(\d+)\.weight$")
DTYPES = {"BF16": "<u2", "F32": "<f4", "F16": "<f2", "I64": "<i8"}


def load_rules(module_file=MODULE_FILE):
    spec = importlib.util.spec_from_file_location("qwen4_exp_canonical_rules", module_file)
    rules = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rules)
    return rules


# Manifest digests (validation round 1: one thread re-hashed ~210 GB per
# verified load, ~136 s, pulling the 102 GB n-gram table through the page cache
# right before a 108 GB weight load). Files and fixed-size chunks of large files
# are hashed on a thread pool (hashlib releases the GIL), reading with
# F_NOCACHE. A file of at most HASH_CHUNK_BYTES gets its plain sha256; a larger
# one the sha256 of its consecutive chunk digests concatenated, so one huge
# file still hashes in parallel. The manifest records the scheme.
HASH_CHUNK_BYTES = 256 * 2 ** 20
HASH_WORKERS = max(1, min(8, os.cpu_count() or 1))
_F_NOCACHE = getattr(fcntl, "F_NOCACHE", 48 if sys.platform == "darwin" else None)
_READ_BYTES = 8 * 2 ** 20
_PLAIN = 1 << 62  # chunk size of pre-round-1 manifests: plain sha256 for every file


def _range_digest(path, start, length, nofollow=False):
    """Raw sha256 of ``length`` bytes at ``start``, bypassing the file cache."""
    fd = os.open(path, os.O_RDONLY | (getattr(os, "O_NOFOLLOW", 0) if nofollow else 0))
    try:
        if _F_NOCACHE is not None:
            try:
                fcntl.fcntl(fd, _F_NOCACHE, 1)
            except OSError:
                pass
        h, pos, end = hashlib.sha256(), start, start + length
        while pos < end:
            block = os.pread(fd, min(_READ_BYTES, end - pos), pos)
            if not block:
                raise ValueError(f"file shrank while hashing: {path}")
            h.update(block)
            pos += len(block)
        return h.digest()
    finally:
        os.close(fd)


def hash_files(paths, chunk_bytes=HASH_CHUNK_BYTES, workers=HASH_WORKERS, nofollow=False):
    """Manifest digests (hex) of ``paths``: {Path: digest}. ``nofollow``
    refuses symlinks (artifact payloads); conversion inputs may be links
    into a hub cache."""
    paths = [Path(p) for p in paths]
    sizes = {p: os.stat(p, follow_symlinks=not nofollow).st_size for p in paths}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = {p: [pool.submit(_range_digest, p, start, min(chunk_bytes, sizes[p] - start), nofollow)
                    for start in range(0, max(sizes[p], 1), chunk_bytes)] for p in paths}
        out = {}
        for p in paths:
            digests = [job.result() for job in jobs[p]]
            out[p] = digests[0].hex() if sizes[p] <= chunk_bytes else hashlib.sha256(b"".join(digests)).hexdigest()
    return out


def sha256(path, chunk_bytes=HASH_CHUNK_BYTES):
    """Manifest digest of one file (its plain sha256 up to ``chunk_bytes``)."""
    return hash_files([path], chunk_bytes)[Path(path)]


def digest_scheme(chunk_bytes=HASH_CHUNK_BYTES):
    return dict(algorithm="sha256", chunk_bytes=chunk_bytes,
                large_files="sha256 of the concatenated sha256 digests of consecutive chunk_bytes ranges")


def tensor_header(path):
    with Path(path).open("rb") as f:
        length = struct.unpack("<Q", f.read(8))[0]
        if length > 100_000_000:
            raise ValueError("safetensors header too large")
        return json.loads(f.read(length)), 8 + length


def tensor_array(path, key):
    """Read-only memmap of one tensor (bf16 as raw uint16 bits)."""
    import numpy as np
    header, offset = tensor_header(path)
    info = header[key]
    dtype = DTYPES[info["dtype"]]
    start, end = info["data_offsets"]
    if end - start != math.prod(info["shape"]) * np.dtype(dtype).itemsize or offset + end > path.stat().st_size:
        raise ValueError(f"invalid safetensors bounds: {key}")
    return np.memmap(path, mode="r", offset=offset + start, dtype=dtype, shape=tuple(info["shape"])), info["dtype"]


SHARD_BYTES = 4 * 2 ** 30
_TENSOR_ITEMSIZE = dict(F32=4, BF16=2, U32=4)


def tensor_bytes(shape, dtype):
    return math.prod(shape) * _TENSOR_ITEMSIZE[dtype]


class TensorFile:
    """Small safetensors writer accepting sequential slices of large tensors (S)."""

    def __init__(self, path, tensors):
        offset, header, self.offsets = 0, {"__metadata__": {"format": "mlx"}}, {}
        for key, (shape, dtype) in tensors.items():
            length = tensor_bytes(shape, dtype)
            header[key] = dict(dtype=dtype, shape=list(shape), data_offsets=[offset, offset + length])
            self.offsets[key] = (offset, offset + length)
            offset += length
        raw = json.dumps(header, separators=(",", ":")).encode()
        raw += b" " * (-len(raw) % 8)
        self.base = len(raw) + 8
        self.file = Path(path).open("xb")
        self.file.write(struct.pack("<Q", len(raw)))
        self.file.write(raw)
        self.file.truncate(self.base + offset)
        self.written = {k: 0 for k in tensors}

    def write(self, key, data):
        start, end = self.offsets[key]
        position = start + self.written[key]
        if position + len(data) > end:
            raise ValueError(f"tensor overflow: {key}")
        self.file.seek(self.base + position)
        self.file.write(data)
        self.written[key] += len(data)

    def close(self):
        self.file.close()
        for key, (start, end) in self.offsets.items():
            if self.written[key] != end - start:
                raise ValueError(f"incomplete tensor: {key}")


def sources(checkpoint, rules):
    """Header-only inventory: target name -> ordered source pieces.

    A piece is (ordinal, path, source key, shape, kind) with kind ``plain``,
    ``conv`` (HF [C,1,K] -> [C,K,1]), ``expert`` (one expert's [rows, cols],
    stacked along a new leading axis or, for gate/up, along rows), or
    ``ngram`` (a row shard of an n-gram table)."""
    found, tables, constants, omitted = {}, {}, [], []
    files = sorted(Path(checkpoint).glob("*.safetensors"))
    if not files:
        raise ValueError("no local HF safetensors files")
    for path in files:
        header, _ = tensor_header(path)
        for original, info in header.items():
            if original == "__metadata__":
                continue
            key = rules.hf_to_mlx_key(original)
            if key is None:
                omitted.append(original)
                continue
            shape = tuple(info["shape"])
            if rules.is_ngram_buffer_key(key):
                constants.append((path, original, key))
                continue
            if info["dtype"] not in ("BF16", "F32", "F16"):
                raise ValueError(f"non-floating weight: {original}")
            match = SHARD_RE.search(key)
            if match:
                layer = int(key.split(".layers.", 1)[1].split(".", 1)[0])
                tables.setdefault(layer, []).append((int(match[1]), path, original, shape, "ngram"))
                continue
            expert = EXPERT_RE.match(key)
            if expert:
                head, e, proj = expert["head"], int(expert["e"]), expert["proj"]
                if proj == "down":
                    name, ordinal = f"{head}.mlp.switch_mlp.down_proj.weight", e
                else:
                    name, ordinal = f"{head}.mlp.switch_mlp.gate_up_proj.weight", 2 * e + (proj == "up")
                found.setdefault(name, []).append((ordinal, path, original, shape, "expert"))
                continue
            if key.endswith(".mlp.experts.gate_up_proj"):
                name = key[:-len("experts.gate_up_proj")] + "switch_mlp.gate_up_proj.weight"
            elif key.endswith(".mlp.experts.down_proj"):
                name = key[:-len("experts.down_proj")] + "switch_mlp.down_proj.weight"
            else:
                name = key
            if name in found:
                raise ValueError(f"duplicate mapped tensor: {name}")
            kind = "conv" if name.endswith("conv1d.weight") and len(shape) == 3 and shape[-1] != 1 else "plain"
            found[name] = [(0, path, original, shape, kind)]
    for key, entries in list(found.items()) + [(f"ngram:{k}", v) for k, v in tables.items()]:
        entries.sort(key=lambda e: e[0])
        if [e[0] for e in entries] != list(range(len(entries))):
            raise ValueError(f"missing / duplicate pieces: {key}")
    return found, tables, constants, omitted, files


def target_shape(entries):
    kind, shape = entries[0][4], list(entries[0][3])
    if kind == "conv":
        return (shape[0], shape[2], shape[1])
    if kind != "expert":
        return tuple(shape)
    if any(e[3] != tuple(shape) for e in entries):
        raise ValueError("inconsistent expert dimensions")
    n = len(entries)
    # gate/up pieces interleave per expert: [E, 2I, H]; down pieces: [E, H, I].
    gate_up = n % 2 == 0 and entries[0][2].endswith("gate_proj.weight")
    return (n // 2, 2 * shape[0], shape[1]) if gate_up else (n, *shape)


def tensor_chunks(entries, max_bytes=32 * 1024 * 1024, raw_bf16=False):
    """Bounded row slices of each piece, in output order. bf16 sources stay
    raw uint16 when ``raw_bf16``; otherwise they are upcast exactly to fp32."""
    import numpy as np
    for _, path, original, shape, kind in entries:
        source, dtype = tensor_array(path, original)
        try:
            raw = raw_bf16 and dtype == "BF16"
            rows = max(1, max_bytes // (math.prod(shape[1:]) * (2 if raw else 4)))
            for start in range(0, shape[0], rows):
                piece = source[start:min(start + rows, shape[0])]
                if raw:
                    value = np.array(piece, copy=True)
                elif dtype == "BF16":
                    value = (piece.astype(np.uint32) << 16).view(np.float32)
                else:
                    value = piece.astype(np.float32)
                if kind == "conv":
                    value = value.transpose(0, 2, 1)
                yield np.ascontiguousarray(value)
        finally:
            source._mmap.close()


def write_ngram_table(rules, output, layer, entries, spec, fmt, group_size, max_bytes=32 * 1024 * 1024):
    """Append the n-gram row shards into one record file; never concatenate.

    bf16 -> bf16 passes the source bits through unchanged (S's raw path); the
    manifest records each source shard's output row and byte span."""
    import numpy as np
    name = f"ngram-L{layer:03d}.{fmt}.bin"
    rows_total = sum(e[3][0] for e in entries)
    dim = entries[0][3][1]
    if rows_total != spec.padded_vocab_size or dim != spec.head_dim or any(e[3][1] != dim for e in entries):
        raise ValueError(f"n-gram table layer {layer}: {rows_total}x{dim}, expected "
                         f"{spec.padded_vocab_size}x{spec.head_dim}")
    record = rules.ngram_record_layout(fmt, dim, group_size)["record_bytes"]
    shards, row = [], 0
    with (Path(output) / name).open("xb") as f:
        for entry in entries:
            start = f.tell()
            for chunk in tensor_chunks([entry], max_bytes, raw_bf16=fmt == "bf16"):
                if chunk.dtype == np.dtype("<u2"):
                    f.write(chunk.tobytes())
                else:
                    f.write(rules.encode_ngram_rows(chunk, fmt, group_size).tobytes())
            n = entry[3][0]
            if f.tell() - start != n * record:
                raise ValueError(f"incomplete n-gram shard: {entry[2]}")
            shards.append(dict(input_file=entry[1].name, tensor=entry[2], row_start=row, row_stop=row + n,
                               byte_start=start, byte_stop=f.tell()))
            row += n
        size = f.tell()
    if size != rows_total * record:
        raise ValueError(f"incomplete n-gram table layer {layer}")
    descriptor = dict(file=name, rows=rows_total, dim=dim, format=fmt, group_size=group_size)
    return descriptor, dict(descriptor, size_bytes=size, source_shards=shards)


# Bytecode a plain mlx-lm load (sys.dont_write_bytecode False) leaves behind.
# Never read by load_verified_model, which compiles the module from its hashed
# source bytes, so it is tolerated outside the inventory and reported.
PYCACHE_RE = re.compile(r"^qwen4_exp\.[A-Za-z0-9_.-]+\.pyc$")
_READ_ONCE = ("manifest.json", "config.json", "qwen4_exp.py")


def _lstat_regular(path):
    st = os.lstat(path)
    if not stat.S_ISREG(st.st_mode):
        raise ValueError(f"artifact entries must be regular files, not links or devices: {Path(path).name}")
    return st


def _entries(path):
    with os.scandir(path) as it:
        return list(it)


def _stamp(st):
    return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)


def _verify(directory, expected_manifest_sha256=None, known_digests=None):
    """Verification core: (manifest, verified bytes of manifest/config/module,
    file stamps). Every payload entry must be a regular file inside the
    directory (no symlinks); the small files are read once and the bytes
    that were hashed are the bytes returned for use."""
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("artifact must be a real directory")
    _lstat_regular(directory / "manifest.json")
    raw = (directory / "manifest.json").read_bytes()
    if expected_manifest_sha256 is not None and hashlib.sha256(raw).hexdigest() != expected_manifest_sha256:
        raise ValueError("manifest pin mismatch")
    manifest = json.loads(raw)
    if any(Path(name).name != name or name in (".", "..") for name in manifest["files"]):
        raise ValueError("manifest payload names must be flat filenames")
    files, ignored = set(), []
    for entry in _entries(directory):
        if entry.is_symlink():
            raise ValueError(f"symlink in artifact: {entry.name}")
        if entry.is_dir(follow_symlinks=False):
            inner = _entries(entry.path) if entry.name == "__pycache__" else None
            if inner is None or any(e.is_symlink() or not e.is_file(follow_symlinks=False)
                                    or not PYCACHE_RE.match(e.name) for e in inner):
                raise ValueError(f"unexpected directory in artifact: {entry.name}")
            ignored += [f"__pycache__/{e.name}" for e in inner]
        elif entry.is_file(follow_symlinks=False):
            files.add(entry.name)
        else:
            raise ValueError(f"unexpected entry in artifact: {entry.name}")
    if files != set(manifest["files"]) | {"manifest.json"}:
        raise ValueError("manifest file inventory mismatch")
    chunk = int(manifest.get("digest", {}).get("chunk_bytes", _PLAIN))
    stamps, blobs = {"manifest.json": _stamp(_lstat_regular(directory / "manifest.json"))}, {"manifest.json": raw}
    for name in _READ_ONCE[1:]:
        if name in manifest["files"]:
            st = _lstat_regular(directory / name)
            blobs[name] = (directory / name).read_bytes()
            if len(blobs[name]) > chunk or hashlib.sha256(blobs[name]).hexdigest() != manifest["files"][name]:
                raise ValueError(f"manifest sha256 mismatch: {name}")
            stamps[name] = _stamp(st)
    rest = [name for name in manifest["files"] if name not in blobs]
    for name in rest:
        stamps[name] = _stamp(_lstat_regular(directory / name))
    todo = [name for name in rest if name not in (known_digests or {})]
    digests = {p.name: d for p, d in hash_files([directory / n for n in todo], chunk, nofollow=True).items()}
    digests.update({n: known_digests[n] for n in rest if n not in digests})
    for name in rest:
        if digests[name] != manifest["files"][name]:
            raise ValueError(f"manifest sha256 mismatch: {name}")
    manifest["ignored_bytecode"] = sorted(ignored)
    return manifest, blobs, stamps


def verify_manifest(directory, expected_manifest_sha256=None):
    """Check the artifact against its manifest (and the pin, if given).
    Inspection only: loading goes through ``load_verified_model``."""
    return _verify(directory, expected_manifest_sha256)[0]


def _check_unchanged(directory, stamps):
    for name, stamp in stamps.items():
        if _stamp(_lstat_regular(Path(directory) / name)) != stamp:
            raise ValueError(f"artifact file changed after verification: {name}")


def _module_from_source(source, path):
    """The model module, compiled from the verified source bytes: no path-based
    import, so no stale or planted ``__pycache__`` bytecode can run instead."""
    import types
    module = types.ModuleType("custom_model")  # mlx-lm's own (unregistered) name
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec", dont_inherit=True), module.__dict__)
    return module


def _is_sha256(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def load_verified_model(directory, expected_manifest_sha256, lazy=False, *, expected_module_sha256=MODULE_SHA256,
                        model_config=None):
    """Verify the externally pinned manifest before executing its Python.

    Both pins are required and fail closed: ``expected_manifest_sha256`` (the
    sha256 of the artifact's ``manifest.json``, recorded when it was
    converted) and ``expected_module_sha256`` (default: the canonical
    module this converter pins, ``MODULE_SHA256``). The manifest's
    ``module_sha256`` must equal its own ``qwen4_exp.py`` entry and the pin.

    This is the only supported way to load an artifact. The module runs from
    the bytes that were hashed, config.json is taken from its hashed bytes,
    the n-gram tables are opened before returning, and every payload file's
    (device, inode, size, mtime) is re-checked after loading. Residual window:
    with ``lazy=True`` weight bytes are read at first use, after the check."""
    if not _is_sha256(expected_manifest_sha256):
        raise ValueError("load_verified_model requires the artifact's pinned manifest sha256 (64 lowercase hex)")
    if not _is_sha256(expected_module_sha256):
        raise ValueError("load_verified_model requires a pinned qwen4_exp.py sha256 (64 lowercase hex)")
    directory = Path(directory)
    manifest, blobs, stamps = _verify(directory, expected_manifest_sha256)
    module_entry = manifest["files"].get("qwen4_exp.py")
    if module_entry is None or manifest.get("module_sha256") != module_entry:
        raise ValueError("manifest module_sha256 disagrees with its qwen4_exp.py entry")
    if module_entry != expected_module_sha256:
        raise ValueError(f"artifact module {module_entry[:12]} is not the pinned module {expected_module_sha256[:12]}")
    import importlib.metadata
    for package, version in PINS.items():
        if importlib.metadata.version(package) != version:
            raise ValueError(f"pinned stack mismatch: {package}")
    if manifest["format"] != FORMAT:
        raise ValueError("unsupported artifact format")
    config = json.loads(blobs["config.json"])
    if config.get("model_file") != "qwen4_exp.py":
        raise ValueError("artifact config.json must load qwen4_exp.py")
    module = _module_from_source(blobs["qwen4_exp.py"], directory / "qwen4_exp.py")
    from mlx_lm.utils import load_model
    # The verified config overrides load_model's own read of config.json, and
    # model_file=None routes class lookup to the module compiled above.
    overrides = {**config, **(model_config or {}), "model_file": None}
    model, loaded_config = load_model(directory, lazy=lazy, strict=True, model_config=overrides,
                                      get_model_classes=lambda config: (module.Model, module.ModelArgs))
    model.ngram_tables()
    _check_unchanged(directory, stamps)
    return model, loaded_config


def _text_config(config):
    c = dict(config.get("text_config", config))
    if c.get("eos_token_id") is None and config.get("eos_token_id") is not None:
        c["eos_token_id"] = config["eos_token_id"]
    return c


def expected_parameters(rules, text_config):
    """Parameter names and shapes of the canonical module itself (lazy MLX
    arrays: shapes only, nothing is materialised)."""
    from mlx.utils import tree_flatten
    model = rules.Model(rules.ModelArgs.from_dict({"model_type": "qwen4_exp", "text_config": text_config}))
    return {k: tuple(v.shape) for k, v in tree_flatten(model.parameters())}, model.language_model.args


def convert(checkpoint, output, profile="maxfit", group_size=64, ple_storage=None, ngram_group_size=32,
            module_file=MODULE_FILE, shard_bytes=SHARD_BYTES):
    import numpy as np
    rules = load_rules(module_file)
    ple_storage = rules.ple_storage_for(profile, ple_storage, group_size)
    checkpoint, output = Path(checkpoint), Path(output)
    if "restricted" in checkpoint.parts or "restricted" in output.parts:
        raise ValueError("restricted paths are not conversion inputs/outputs")
    if output.exists():
        raise ValueError("output directory must not exist")
    config = json.loads((checkpoint / "config.json").read_text())
    c = _text_config(config)
    expected, targs = expected_parameters(rules, c)
    inventory, tables, constants, omitted, input_files = sources(checkpoint, rules)
    if targs.tie_word_embeddings:
        inventory.pop("language_model.lm_head.weight", None)
    if set(inventory) != set(expected):
        raise ValueError(f"text tensor inventory mismatch: missing={sorted(set(expected) - set(inventory))[:8]}; "
                         f"unexpected={sorted(set(inventory) - set(expected))[:8]}")
    for key, entries in inventory.items():
        if target_shape(entries) != expected[key]:
            raise ValueError(f"shape mismatch: {key}: {target_shape(entries)} != {expected[key]}")
    for path, original, key in constants:
        value, dtype = tensor_array(path, original)
        if dtype != "I64" or value.tolist() != rules.ngram_buffer_expected(targs, key):
            raise ValueError(f"n-gram hash buffer mismatch: {original}")
        value._mmap.close()
    specs = {lid - 1: rules.NgramHashSpec(targs, i) for i, lid in enumerate(targs.ple_layer_ids)}
    if set(tables) != set(specs):
        raise ValueError(f"n-gram tables for layers {sorted(tables)}, config expects {sorted(specs)}")
    for spec in specs.values():  # refuse an unusable record format before writing anything
        rules.ngram_record_layout(ple_storage, spec.head_dim, ngram_group_size)

    quantizers = {k: rules.quantization_for(k[:-len(".weight")], shape, profile, group_size)
                  for k, shape in expected.items() if k.endswith(".weight")}
    import importlib.metadata
    for package, version in PINS.items():
        if importlib.metadata.version(package) != version:
            raise ValueError(f"conversion requires the pinned stack: {package} {version}")
    import mlx.core as mx
    output.mkdir(parents=True)
    dtype_name = "F32" if profile == "fp32" else "BF16"
    out_np = np.dtype("<f4") if profile == "fp32" else np.dtype("<u2")
    weight_map, quant_cfg, ngram_layers, ngram_manifest = {}, {}, {}, {}
    # Tensors packed into shards of at most shard_bytes (one file per tensor
    # meant 1163 files for the released structure, all held open by mlx-lm's
    # load_model until the first eval; validation round 1).
    plan = []
    for key, entries in sorted(inventory.items()):
        shape, quant = expected[key], quantizers.get(key)
        tensors = {key: (shape, dtype_name)}
        if quant:
            base = key[:-len("weight")]
            tensors = {key: ((*shape[:-1], shape[-1] * quant["bits"] // 32), "U32"),
                       base + "scales": ((*shape[:-1], shape[-1] // group_size), "BF16"),
                       base + "biases": ((*shape[:-1], shape[-1] // group_size), "BF16")}
            quant_cfg[key[:-len(".weight")]] = quant
        plan.append((key, entries, quant, tensors, sum(tensor_bytes(*t) for t in tensors.values())))
    shards, current, size = [], [], 0
    for item in plan:
        if current and size + item[4] > shard_bytes:
            shards.append(current)
            current, size = [], 0
        current.append(item)
        size += item[4]
    shards += [current] if current else []
    for number, shard in enumerate(shards, 1):
        name = f"model-{number:05d}-of-{len(shards):05d}.safetensors"
        writer = TensorFile(output / name, {t: spec for item in shard for t, spec in item[3].items()})
        for key, entries, quant, tensors, _ in shard:
            base = key[:-len("weight")]
            for chunk in tensor_chunks(entries, raw_bf16=not quant and dtype_name == "BF16"):
                if quant:
                    arr = mx.array(chunk).astype(mx.bfloat16)
                    arr = arr.reshape(-1, arr.shape[-1])
                    packed, scales, biases = mx.quantize(arr, group_size=group_size, bits=quant["bits"])
                    mx.eval(packed, scales, biases)
                    writer.write(key, np.array(packed).astype("<u4").tobytes())
                    writer.write(base + "scales", np.array(scales.view(mx.uint16)).astype("<u2").tobytes())
                    writer.write(base + "biases", np.array(biases.view(mx.uint16)).astype("<u2").tobytes())
                elif chunk.dtype == out_np:
                    writer.write(key, chunk.tobytes())
                elif out_np == np.dtype("<u2"):
                    writer.write(key, rules._f32_to_bf16_bits(chunk).tobytes())
                else:
                    writer.write(key, chunk.astype("<f4").tobytes())
            for tensor in tensors:
                weight_map[tensor] = name
        writer.close()
    for layer, entries in sorted(tables.items()):
        ngram_layers[str(layer)], ngram_manifest[str(layer)] = write_ngram_table(
            rules, output, layer, entries, specs[layer], ple_storage, ngram_group_size)

    config_out = dict(model_type="qwen4_exp", architectures=["Qwen4ExpForConditionalGeneration"],
                      model_file="qwen4_exp.py", jw_format=FORMAT, text_config=c,
                      ngram_tables=dict(dir=".", io="mmap", layers=ngram_layers),
                      eos_token_id=c.get("eos_token_id"), tie_word_embeddings=bool(c.get("tie_word_embeddings")))
    if quant_cfg:
        first = next(iter(quant_cfg.values()))
        config_out["quantization"] = dict(group_size=group_size, bits=first["bits"], mode="affine", **quant_cfg)
    (output / "config.json").write_text(json.dumps(config_out, indent=2) + "\n")
    (output / "model.safetensors.index.json").write_text(json.dumps(dict(weight_map=weight_map), indent=2) + "\n")
    shutil.copyfile(module_file, output / "qwen4_exp.py")
    for name in ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "generation_config.json",
                 "chat_template.jinja", "vocab.json", "merges.txt"):
        if (checkpoint / name).is_file():
            shutil.copyfile(checkpoint / name, output / name)
    inputs = hash_files([checkpoint / "config.json", *input_files])
    outputs = hash_files([p for p in sorted(output.iterdir()) if p.is_file()], nofollow=True)
    manifest = dict(format=FORMAT, pins=PINS, profile=profile, group_size=group_size, ngram_storage=ple_storage,
                    ngram_tables=ngram_manifest, module_sha256=outputs[output / "qwen4_exp.py"],
                    norm_representation="raw HF zero-centered; runtime 1 + w",
                    omitted_keys=omitted, quantized=sorted(quant_cfg), digest=digest_scheme(),
                    inputs={p.name: d for p, d in inputs.items()},
                    files={p.name: d for p, d in outputs.items()})
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    # Structure check of what was just written; its bytes were hashed above.
    _verify(output, known_digests=manifest["files"])
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("checkpoint", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--profile", choices=("fp32", "bf16", "mixed", "maxfit", "maxfit5"), default="maxfit")
    p.add_argument("--group-size", type=int, choices=(32, 64, 128), default=64)
    p.add_argument("--ple-storage", choices=("f32", "bf16", "q8", "q4"),
                   help="n-gram table format (default: bf16 for maxfit*/bf16, f32 for fp32, q4 for mixed)")
    p.add_argument("--ngram-group-size", type=int, default=32,
                   help="q8/q4 n-gram record group size (must divide the n-gram head dim)")
    p.add_argument("--shard-gb", type=float, default=SHARD_BYTES / 2 ** 30,
                   help="maximum weight shard size in GiB (a larger single tensor gets its own shard)")
    a = p.parse_args()
    manifest = convert(a.checkpoint, a.output, a.profile, a.group_size, a.ple_storage, a.ngram_group_size,
                       shard_bytes=int(a.shard_gb * 2 ** 30))
    print(json.dumps(dict(output=str(a.output), payload_files=len(manifest["files"]),
                          manifest_sha256=sha256(a.output / "manifest.json"))))


if __name__ == "__main__":
    main()
