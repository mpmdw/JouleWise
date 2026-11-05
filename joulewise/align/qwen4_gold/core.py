"""Offline, indexed tensor access and parity policy (no framework imports)."""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

SCHEMA = "qwen4-gold/v1"
REFERENCE_VERSION = "5.22.1"
# A component must satisfy elementwise atol+rtol AND the cosine floor.
# These are engineering gates, not accuracy/quality claims. Never auto-widen.
TOLERANCES = {
    "fp32": {"atol": 1e-4, "rtol": 1e-4, "cosine_min": 0.999999},
    "bf16": {"atol": 0.03125, "rtol": 0.03125, "cosine_min": 0.999},
}


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def file_stamp(path):
    value = Path(path).stat()
    return [value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns]


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temp.replace(path)


def text_config(config):
    return config.get("text_config", config)


class IndexedCheckpoint:
    """safe_open slicing only. No load_file, from_pretrained, or full state_dict.

    Adapters receive this object. Names are canonical HF checkpoint names, with
    model.language_model / model prefixes discovered from embed_tokens.
    Expert matrices must be sliced on axis 0; embedding tables must use rows().
    """

    def __init__(self, root, shard_guards=None):
        self.shard_guards = shard_guards
        self.root = Path(root).resolve()
        if "restricted" in self.root.parts:
            raise ValueError("restricted checkpoint path refused")
        self.config = json.loads(self.path("config.json").read_text())
        self.text = text_config(self.config)
        index = self.path("model.safetensors.index.json")
        if index.exists():
            self.weight_map = json.loads(index.read_text())["weight_map"]
        else:
            # save_pretrained's unsharded tiny checkpoint.
            from safetensors import safe_open
            with safe_open(self.path("model.safetensors"), framework="np") as f:
                self.weight_map = dict.fromkeys(f.keys(), "model.safetensors")
        candidates = [k[:-len("embed_tokens.weight")] for k in self.weight_map
                      if k.endswith("embed_tokens.weight") and not k.startswith("mtp.")]
        if len(candidates) != 1:
            raise ValueError("expected exactly one text embedding prefix")
        self.prefix = candidates[0]
        self.reads = []

    def path(self, filename):
        if Path(filename).name != filename or filename in ("", ".", "..", "restricted"):
            raise ValueError("index shard must be a basename")
        path = self.root / filename
        if path.is_symlink():
            raise ValueError("checkpoint shard symlinks refused")
        if self.shard_guards is not None and filename.endswith(".safetensors"):
            expected = self.shard_guards.get(filename)
            if expected is None:
                raise FileNotFoundError(f"shard was absent from the hashed invocation: {filename}")
            if file_stamp(path) != expected:
                raise ValueError(f"checkpoint shard changed after hashing: {filename}")
        return path

    def info(self, name):
        if name not in self.weight_map and ".experts." in name:
            base, leaf = name.rsplit(".", 1)
            source = base + (".0.gate_proj.weight" if leaf == "gate_up_proj" else ".0.down_proj.weight")
            shape, dtype = self.info(source)
            return (self.text["num_experts"], shape[0] * (2 if leaf == "gate_up_proj" else 1), shape[1]), dtype
        from safetensors import safe_open
        with safe_open(self.path(self.weight_map[name]), framework="np") as f:
            s = f.get_slice(name)
            return tuple(s.get_shape()), s.get_dtype()

    def read(self, name, selection=None, framework="numpy", dtype="fp32"):
        """Read a bounded tensor/slice, casting BF16 identically in both workers.

        NumPy lacks BF16 in the supplied MLX venv. safetensors uses NumPy's dtype
        registry: temporarily decode BF16 as its raw uint16 storage, then shift
        into IEEE float32. This is lossless, without a torch dependency in MLX.
        """
        from safetensors import safe_open
        if name not in self.weight_map and ".experts." in name:
            if not selection or not isinstance(selection[0], int):
                raise ValueError("unpacked experts require a single expert index")
            base, leaf = name.rsplit(".", 1)
            index = selection[0]
            leaves = ["gate_proj", "up_proj"] if leaf == "gate_up_proj" else ["down_proj"]
            values = [self.read(f"{base}.{index}.{part}.weight", tuple(selection[1:]), framework, dtype) for part in leaves]
            if len(values) == 1:
                return values[0]
            if framework == "torch":
                import torch
                return torch.cat(values, dim=0)
            if framework == "mlx":
                import mlx.core as mx
                return mx.concatenate(values, axis=0)
            import numpy as np
            return np.concatenate(values, axis=0)
        shape, storage = self.info(name)
        if selection is None and (".experts." in name or "embed_tokens" in name or
                                  "ngram_embedding" in name or name == "lm_head.weight"):
            raise ValueError("large tables require explicit slicing")
        if selection is None:
            selection = tuple(slice(None) for _ in shape)
        if not isinstance(selection, tuple) or len(selection) != len(shape):
            raise ValueError("explicit one-selector-per-axis tuple required")
        if ".experts." in name and len(shape) == 3 and not isinstance(selection[0], int):
            raise ValueError("packed experts require one expert index")
        extents = []
        for size, selected in zip(shape, selection):
            if isinstance(selected, int):
                if selected < 0 or selected >= size:
                    raise ValueError("tensor index outside bounds")
            elif isinstance(selected, slice):
                start, stop, step = selected.indices(size)
                if step != 1:
                    raise ValueError("only contiguous tensor slices are supported")
                extents.append(max(0, stop-start))
            else:
                raise ValueError("only integer indices and contiguous slices are supported")
        if math.prod(extents) * 4 > 256 * 1024**2:
            raise ValueError("slice exceeds 256 MiB fp32 allocation guard")
        if ("embed_tokens" in name or "ngram_embedding" in name or name == "lm_head.weight") and isinstance(selection[0], slice):
            if len(range(*selection[0].indices(shape[0]))) > 1024:
                raise ValueError("embedding/head slices are limited to 1024 rows")
        self.reads.append({"name": name, "shard": self.weight_map[name],
                           "slice": repr(selection)})
        if framework == "torch":
            import torch
            with safe_open(self.path(self.weight_map[name]), framework="pt") as f:
                result = f.get_slice(name)[selection]
            # Clone releases the mmap; only the requested slice remains resident.
            if dtype == "native":
                return result.clone()
            return result.to(dtype=torch.float32 if dtype == "fp32" else torch.bfloat16).clone()
        import numpy as np
        previous = np.sctypeDict.get("bfloat16")
        if storage == "BF16":
            np.sctypeDict["bfloat16"] = np.uint16
        try:
            with safe_open(self.path(self.weight_map[name]), framework="np") as f:
                result = f.get_slice(name)[selection].copy()
        finally:
            if storage == "BF16":
                if previous is None:
                    np.sctypeDict.pop("bfloat16", None)
                else:
                    np.sctypeDict["bfloat16"] = previous
        if storage == "BF16":
            result = (result.astype(np.uint32) << 16).view(np.float32)
        if framework == "mlx":
            import mlx.core as mx
            array = mx.array(result)
            return array if dtype == "native" else array.astype(mx.float32 if dtype == "fp32" else mx.bfloat16)
        if framework != "numpy":
            raise ValueError(framework)
        return result

    def rows(self, name, ids, framework="numpy", dtype="fp32"):
        """Only unique requested rows; return rows in original ids shape/order."""
        import numpy as np
        ids = np.asarray(ids, dtype=np.int64)
        shape, _ = self.info(name)
        if ids.size == 0 or ids.min() < 0 or ids.max() >= shape[0]:
            raise ValueError("invalid/empty embedding row ids")
        unique, inverse = np.unique(ids, return_inverse=True)
        values = [self.read(name, (slice(int(i), int(i) + 1), slice(None)),
                            framework, dtype)[0] for i in unique]
        if framework == "torch":
            import torch
            return torch.stack(values)[torch.tensor(inverse)].reshape(*ids.shape, shape[1])
        if framework == "mlx":
            import mlx.core as mx
            return mx.stack(values)[mx.array(inverse)].reshape(*ids.shape, shape[1])
        return np.stack(values)[inverse].reshape(*ids.shape, shape[1])

    def ngram_parts(self, base):
        pattern = re.compile(re.escape(base) + r"\.shard_(\d+)\.weight$")
        parts = sorted((int(m[1]), k) for k in self.weight_map if (m := pattern.fullmatch(k)))
        if parts:
            if [i for i, _ in parts] != list(range(len(parts))):
                raise ValueError("ngram shard numbers are not contiguous")
            return [k for _, k in parts]
        return [base + ".weight"]

    def ngram_rows(self, base, ids, framework="numpy", dtype="fp32"):
        import numpy as np
        # Checkpoint parts are contiguous row partitions, in numeric shard order.
        parts = self.ngram_parts(base)
        ids = np.asarray(ids, dtype=np.int64)
        unique, inverse = np.unique(ids, return_inverse=True)
        output = {}
        # HF reverses Concatenate using torch.chunk: equal-sized partitions,
        # with a potentially shorter final partition. Inspect part 0 once and
        # only open the parts containing requested rows thereafter.
        part_rows = self.info(parts[0])[0][0]
        for part_index in np.unique(unique // part_rows):
            if part_index < 0 or part_index >= len(parts):
                raise ValueError("ngram ids outside sharded table")
            part = parts[int(part_index)]
            rows, _ = self.info(part)[0]
            if rows > part_rows or (part_index < len(parts)-1 and rows != part_rows):
                raise ValueError("nonuniform ngram partition layout")
            offset = int(part_index) * part_rows
            for i in unique[(unique >= offset) & (unique < offset + rows)]:
                output[int(i)] = self.read(part, (slice(int(i-offset), int(i-offset)+1), slice(None)),
                                           framework, dtype)[0]
        if len(output) != len(unique):
            raise ValueError("ngram ids outside sharded table")
        values = [output[int(i)] for i in unique]
        width = values[0].shape[-1]
        if framework == "torch":
            import torch
            return torch.stack(values)[torch.tensor(inverse)].reshape(*ids.shape, width)
        if framework == "mlx":
            import mlx.core as mx
            return mx.stack(values)[mx.array(inverse)].reshape(*ids.shape, width)
        return np.stack(values)[inverse].reshape(*ids.shape, width)


def required_traces(config, unit):
    c = text_config(config)
    if unit == "embed":
        return {"embedding", "output"}
    if unit == "final":
        return {"final.norm", "output"}
    if unit == "head":
        return {"output"}
    i = int(unit)
    names = {"output", "attention", "router.logits", "router.experts", "router.weights", "moe",
             "attn.mix", "attn.norm", "attn.residual", "attn.inject", "attn.streams",
             "mlp.mix", "mlp.norm", "mlp.residual", "mlp.inject", "mlp.streams"}
    if c["layer_types"][i] != "linear_attention":
        names |= {"qsa.mask", "attention.q_norm", "attention.k_norm"}
    else:
        names.add("attention.gated_norm")
    if i + 1 in c.get("ple_layer_ids", []):
        names |= {"ple", "ple.ngram_ids", "ple.embedding", "ple.norm_key", "ple.norm_query", "ple.norm_conv"}
    return names


class TraceFile:
    """Stream contiguous numeric .npy traces; never retain mapped file pages."""
    def __init__(self, path):
        import numpy as np
        self.path = Path(path)
        with self.path.open("rb") as f:
            version = np.lib.format.read_magic(f)
            if version == (1, 0):
                self.shape, fortran, self.dtype = np.lib.format.read_array_header_1_0(f)
            elif version == (2, 0):
                self.shape, fortran, self.dtype = np.lib.format.read_array_header_2_0(f)
            else:
                raise ValueError("unsupported trace NPY version")
            self.offset = f.tell()
        if fortran or self.dtype.kind not in "biuf":
            raise ValueError("trace must be contiguous C-order numeric data")
        self.size = math.prod(self.shape)
        self.ndim = len(self.shape)
        self.flat = self
        if self.path.stat().st_size != self.offset + self.size * self.dtype.itemsize:
            raise ValueError("trace file length mismatch")

    def __getitem__(self, selection):
        import numpy as np
        start, stop, step = selection.indices(self.size)
        if step != 1:
            raise ValueError("trace reads must be contiguous")
        with self.path.open("rb") as f:
            f.seek(self.offset + start*self.dtype.itemsize)
            return np.frombuffer(f.read((stop-start)*self.dtype.itemsize), dtype=self.dtype)


def _comparable(value):
    import numpy as np
    return value if isinstance(value, TraceFile) else np.asarray(value)


def compare_exact(reference, candidate):
    """Bounded exact equality, including multi-GiB masks stored as memmaps."""
    import numpy as np
    a, b = _comparable(reference), _comparable(candidate)
    if a.shape != b.shape:
        return False
    for start in range(0, a.size, 262144):
        if not np.array_equal(a.flat[start:start+262144], b.flat[start:start+262144]):
            return False
    return True


def compare_arrays(reference, candidate, dtype, exact=False):
    import numpy as np
    a, b = _comparable(reference), _comparable(candidate)
    if a.shape != b.shape:
        return {"pass": False, "reason": "shape_mismatch", "reference": list(a.shape), "candidate": list(b.shape)}
    if not a.size:
        return {"pass": False, "reason": "empty"}
    if exact:
        # Router arrays are small relative to head logits; process token chunks.
        if a.ndim < 1 or a.shape[-1] == 0:
            return {"pass": False, "reason": "empty_experts"}
        token_count = a.size // a.shape[-1]
        width = a.shape[-1]
        matching = 0
        ordered = True
        for first in range(0, token_count, 4096):
            left = a.flat[first*width:min(token_count, first+4096)*width].reshape(-1, width)
            right = b.flat[first*width:min(token_count, first+4096)*width].reshape(-1, width)
            if not np.isfinite(left).all() or not np.isfinite(right).all():
                return {"pass": False, "reason": "nonfinite"}
            ordered &= np.array_equal(left, right)
            matching += int(np.all(np.sort(left, axis=-1) == np.sort(right, axis=-1), axis=-1).sum())
        return {"pass": matching == token_count, "exact_set_agreement": matching == token_count,
                "ordered_agreement": bool(ordered), "token_set_agreement": matching/token_count}
    t = TOLERANCES[dtype]
    max_abs = max_relative = squared_a = squared_b = squared_diff = dot = 0.0
    within_count = 0
    for first in range(0, a.size, 262144):
        # .flat slices preserve C-order without materializing a noncontiguous
        # whole array. fp64 temporaries stay bounded to a few MiB each.
        left = a.flat[first:first+262144].astype(np.float64)
        right = b.flat[first:first+262144].astype(np.float64)
        if not np.isfinite(left).all() or not np.isfinite(right).all():
            return {"pass": False, "reason": "nonfinite"}
        diff = np.abs(left-right)
        max_abs = max(max_abs, float(diff.max()))
        max_relative = max(max_relative, float((diff/np.maximum(np.abs(left), 1e-12)).max()))
        within_count += int((diff <= t["atol"] + t["rtol"]*np.abs(left)).sum())
        squared_a += float(np.dot(left, left)); squared_b += float(np.dot(right, right))
        squared_diff += float(np.dot(diff, diff)); dot += float(np.dot(left, right))
    cosine = dot / max(math.sqrt(squared_a)*math.sqrt(squared_b), 1e-300) if squared_a and squared_b else float(squared_a == squared_b)
    return {"pass": bool(within_count == a.size and cosine >= t["cosine_min"]),
            "max_abs": max_abs, "max_relative": max_relative,
            "relative_l2": math.sqrt(squared_diff)/max(math.sqrt(squared_a), 1e-12),
            "cosine": min(1.0, max(-1.0, cosine)), "fraction_within": within_count/a.size}
