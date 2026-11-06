"""Fixed-prompt PLE storage. Hashing belongs exclusively to the official HF code."""
from __future__ import annotations

import inspect
import json
import math
import os
import struct
from pathlib import Path

from .core import IndexedCheckpoint, REFERENCE_VERSION, digest, sha256, write_json

BUFFER_SUFFIXES = ("layer_multipliers", "ngram_heads_vocab_sizes", "ngram_heads_offsets")


def is_table(name):
    return ".ple.ple_embedding.ngram_embedding." in name


def header(path):
    with Path(path).open("rb") as f:
        size = struct.unpack("<Q", f.read(8))[0]
        if size > 100_000_000:
            raise ValueError("safetensors header too large")
        return json.loads(f.read(size)), size + 8


def atomic_npy(path, value):
    import numpy as np
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(".tmp").open("wb") as f:
        np.save(f, value, allow_pickle=False)
        f.flush()
        os.fsync(f.fileno())
    path.with_suffix(".tmp").replace(path)


def copy_tensors(source, names, target):
    """Byte-exact safetensors subset; caller authenticates the full source first.

    No cast, layout change, or tensor-sized allocation. This is a local storage
    view with its own digest, never claimed to have the original LFS digest.
    """
    tensors, offset = header(source)
    output, cursor = {}, 0
    for name in sorted(names):
        value = tensors[name]
        lo, hi = value["data_offsets"]
        if lo < 0 or hi < lo or offset + hi > Path(source).stat().st_size:
            raise ValueError("invalid tensor subset source bounds")
        output[name] = {**value, "data_offsets": [cursor, cursor + hi - lo]}
        cursor += hi - lo
    raw = json.dumps(output, separators=(",", ":")).encode()
    raw += b" " * (-len(raw) % 8)
    target = Path(target)
    temp = target.with_suffix(".tmp")
    with Path(source).open("rb") as f, temp.open("wb") as out:
        out.write(struct.pack("<Q", len(raw)))
        out.write(raw)
        for name in sorted(names):
            lo, hi = tensors[name]["data_offsets"]
            f.seek(offset + lo)
            left = hi - lo
            while left:
                value = f.read(min(left, 4*1024**2))
                if not value:
                    raise ValueError("short subset source read")
                out.write(value)
                left -= len(value)
        out.flush()
        os.fsync(out.fileno())
    temp.replace(target)


def official_plan(request, checkpoint):
    """Run official NGramEmbedding.forward, substituting only its final gather.

    Meta construction avoids allocating the 102 GB table. All three checkpoint
    I64 buffers are loaded before forward; no hash or EOS logic is duplicated.
    """
    import torch
    import transformers
    from transformers.models.qwen4_exp import modeling_qwen4_exp as ref
    from transformers.models.qwen4_exp.configuration_qwen4_exp import Qwen4ExpTextConfig
    if transformers.__version__ != REFERENCE_VERSION:
        raise ValueError(f"requires transformers {REFERENCE_VERSION}")
    torch.set_num_threads(2)
    config = Qwen4ExpTextConfig(**checkpoint.text)
    plans = {}
    for ple_index, layer_id in enumerate(config.ple_layer_ids):
        base = checkpoint.prefix + f"layers.{layer_id - 1}.ple.ple_embedding."
        with torch.device("meta"):
            module = ref.Qwen4ExpTextNGramEmbedding(config, config.ple_embed_dim, layer_id - 1, ple_index)
        shape = tuple(module.ngram_embedding.weight.shape)
        for suffix in BUFFER_SUFFIXES:
            value = checkpoint.read(base + suffix, framework="torch", dtype="native")
            if value.dtype != torch.int64 or value.shape != getattr(module, suffix).shape:
                raise ValueError(f"invalid PLE buffer {base + suffix}")
            setattr(module, suffix, value)
        seen = set()

        class Recorder(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.register_buffer("weight", torch.empty(0))

            def forward(self, indices):
                seen.update(indices.flatten().tolist())
                return torch.zeros((*indices.shape, shape[1]))

        module.ngram_embedding = Recorder()
        with torch.inference_mode():
            for prompt in request["prompts"]:
                module(torch.tensor([prompt["input_ids"]]), past_key_values=None)
        if not seen or min(seen) < 0 or max(seen) >= shape[0]:
            raise ValueError("official PLE hash outside table")
        parts = checkpoint.ngram_parts(base + "ngram_embedding")
        # HF checkpoint split uses torch.chunk, not array_split.
        part_rows = math.ceil(shape[0] / len(parts))
        plans[base + "ngram_embedding"] = {"ids": sorted(seen), "shape": list(shape),
                                            "parts": parts, "part_rows": part_rows}
    return {"plans": plans, "transformers": transformers.__version__,
            "reference_source_sha256": sha256(inspect.getfile(ref))}


def extract_part(path, tensor, plan, output, shard_sha256):
    """Copy exact stored row bytes, with bounded pread and no table mmap."""
    import numpy as np
    tensors, start = header(path)
    info = tensors[tensor]
    index = plan["parts"].index(tensor)
    offset = index * plan["part_rows"]
    expected_rows = min(plan["part_rows"], plan["shape"][0] - offset)
    if info["shape"] != [expected_rows, plan["shape"][1]]:
        raise ValueError(f"unexpected PLE partition shape: {tensor}")
    dtype = {"BF16": "<u2", "F32": "<f4", "F16": "<f2"}[info["dtype"]]
    row_bytes = np.dtype(dtype).itemsize * info["shape"][1]
    lo, hi = info["data_offsets"]
    if hi - lo != row_bytes * expected_rows or start + hi > Path(path).stat().st_size:
        raise ValueError("invalid PLE data offsets")
    ids = [i for i in plan["ids"] if offset <= i < offset + expected_rows]
    values = np.empty((len(ids), plan["shape"][1]), dtype=dtype)
    with Path(path).open("rb") as f:
        for n, i in enumerate(ids):
            raw = os.pread(f.fileno(), row_bytes, start + lo + (i - offset) * row_bytes)
            if len(raw) != row_bytes:
                raise ValueError("short PLE row read")
            values[n] = np.frombuffer(raw, dtype=dtype)
    filename = digest(tensor) + ".npy"
    atomic_npy(Path(output) / filename, values)
    return {"tensor": tensor, "shard_sha256": shard_sha256, "ids": ids, "shape": info["shape"],
            "storage": info["dtype"], "file": filename, "sha256": sha256(Path(output) / filename)}


def valid_entry(root, entry):
    if Path(entry["file"]).name != entry["file"]:
        raise ValueError("sparse row filename must be a basename")
    path = Path(root) / entry["file"]
    return path.is_file() and not path.is_symlink() and sha256(path) == entry["sha256"]


class SparseCheckpoint(IndexedCheckpoint):
    """Same gather contract for Torch and MLX; any unplanned row fails closed."""
    def __init__(self, root, guards, store, expected_digest):
        super().__init__(root, guards)
        self.sparse_root = Path(store)
        manifest = self.sparse_root / "store.json"
        if sha256(manifest) != expected_digest:
            raise ValueError("sparse store manifest changed")
        self.sparse = json.loads(manifest.read_text())
        expected_tensors = {tensor for plan in self.sparse.get("plans", {}).values() for tensor in plan["parts"]}
        if set(self.sparse.get("entries", {})) != expected_tensors:
            raise ValueError("sparse entries do not match official plan")
        seen_ids = set()
        for base, plan in self.sparse["plans"].items():
            if base not in self.weight_map and not all(p in self.weight_map for p in plan["parts"]):
                raise ValueError("sparse plan tensor is absent from checkpoint")
            if plan["ids"] != sorted(set(plan["ids"])):
                raise ValueError("sparse plan ids must be sorted and unique")
            if len(plan["shape"]) != 2 or plan["part_rows"] != math.ceil(plan["shape"][0] / len(plan["parts"])):
                raise ValueError("invalid sparse plan shape")
            for index, tensor in enumerate(plan["parts"]):
                entry = self.sparse["entries"][tensor]
                if entry.get("tensor") != tensor:
                    raise ValueError("sparse tensor association changed")
                offset = index * plan["part_rows"]
                rows = min(plan["part_rows"], plan["shape"][0] - offset)
                expected_ids = [i for i in plan["ids"] if offset <= i < offset + rows]
                if entry.get("ids") != expected_ids or entry.get("shape") != [rows, plan["shape"][1]]:
                    raise ValueError("sparse row contract changed")
                source = self.weight_map.get(tensor)
                if source is None:
                    raise ValueError("sparse tensor missing from weight map")
                if entry.get("shard_sha256") != self.sparse.get("source_shards", {}).get(source):
                    raise ValueError("sparse source shard identity changed")
                if entry.get("storage") not in {"BF16", "F16", "F32"}:
                    raise ValueError("unsupported sparse storage dtype")
                seen_ids.update((base, i) for i in expected_ids)
        for entry in self.sparse["entries"].values():
            if not valid_entry(self.sparse_root, entry):
                raise ValueError("sparse row bytes changed")
            import numpy as np
            value = np.load(self.sparse_root / entry["file"], allow_pickle=False, mmap_mode="r")
            dtype = {"BF16": np.dtype("<u2"), "F16": np.dtype("<f2"), "F32": np.dtype("<f4")}[entry["storage"]]
            if value.shape != (len(entry["ids"]), entry["shape"][1]) or value.dtype != dtype:
                raise ValueError("sparse row file shape/dtype changed")

    def info(self, name):
        if is_table(name):
            entry = self.sparse["entries"][name]
            return tuple(entry["shape"]), entry["storage"]
        return super().info(name)

    def read(self, name, *args, **kwargs):
        if is_table(name):
            raise ValueError("sparse PLE requires ngram_rows; full table access refused")
        return super().read(name, *args, **kwargs)

    def ngram_rows(self, base, ids, framework="numpy", dtype="fp32"):
        import numpy as np
        ids = np.asarray(ids, dtype=np.int64)
        unique, inverse = np.unique(ids, return_inverse=True)
        if not unique.size:
            raise ValueError("empty PLE lookup")
        found = {}
        for tensor in self.sparse["plans"][base]["parts"]:
            entry = self.sparse["entries"][tensor]
            wanted = set(unique.tolist()) & set(entry["ids"])
            if not wanted:
                continue
            values = np.load(self.sparse_root / entry["file"], allow_pickle=False)
            if entry["storage"] == "BF16":
                values = (values.astype(np.uint32) << 16).view(np.float32)
            for row in wanted:
                found[row] = values[entry["ids"].index(row)]
        if set(found) != set(unique.tolist()):
            raise ValueError(f"PLE lookup outside sparse store: {sorted(set(unique.tolist()) - set(found))[:8]}")
        result = np.stack([found[int(i)] for i in unique])[inverse].reshape(*ids.shape, -1)
        if framework == "torch":
            import torch
            return torch.from_numpy(result.copy()).to(torch.float32 if dtype == "fp32" else torch.bfloat16)
        if framework == "mlx":
            import mlx.core as mx
            return mx.array(result).astype(mx.float32 if dtype == "fp32" else mx.bfloat16)
        if framework != "numpy":
            raise ValueError(framework)
        return result
