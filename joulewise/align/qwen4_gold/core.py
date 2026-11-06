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
        return {"final.norm", "output"} | norm_auxiliary(config, unit)
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
    return names | norm_auxiliary(config, unit)


# Gate amendment A1 (docs/align/qwen4_exp_port/gold_parity.md): every traced
# normalization output is gated input-conditioned. Each worker also exports the
# exact tensor(s) its norm consumed; the coordinator recomputes the official
# formula in float64 from each side's OWN input and the checkpoint weight.
# Untraced norms (QSA indexer q/k_layernorm, DeltaNet in-kernel l2norm) are out
# of scope: they are covered only through downstream traces.
GATE_AMENDMENTS = ["A1-input-conditioned-norms", "A2-bf16-router-boundary-swaps"]
# Supremum of |activation'(z)|: sigmoid 1/4; silu 1.0998 (rounded up).
ACTIVATION_LIPSCHITZ = {"sigmoid": 0.25, "silu": 1.1}


def norm_specs(config, unit):
    """Traced RMSNorm-like outputs: official formula parameters per trace.

    kind "offset": Qwen4ExpTextRMSNorm, y = x/sqrt(mean_G(x^2)+eps) * (1+w),
    mean over contiguous groups of G channels of the last axis (G == len(w)
    when ungrouped). kind "gated": Qwen4ExpTextRMSNormGated,
    y = w * x/sqrt(mean(x^2)+eps) * act(gate). Weight names are relative to the
    checkpoint text prefix.
    """
    c = text_config(config)
    if unit != "final" and not unit.isdigit():
        return {}
    eps = float(c.get("rms_norm_eps", 1e-6))  # Qwen4ExpTextConfig default
    hidden = c.get("hidden_size")  # Missing sizes fail closed in compare_norm.

    def offset(weight, group):
        return {"kind": "offset", "weight": weight, "group": group, "eps": eps}
    if unit == "final":
        specs = {"final.norm": offset("hyper_connection_mixer.hc_norm.weight", hidden)}
    else:
        i = int(unit)
        p = f"layers.{i}."
        specs = {"attn.norm": offset(p + "attn_hyper_connection.hc_norm.weight", hidden),
                 "mlp.norm": offset(p + "mlp_hyper_connection.hc_norm.weight", hidden)}
        if c["layer_types"][i] == "linear_attention":
            activation = c.get("output_gate_type") or c.get("hidden_act", "silu")
            if activation not in ACTIVATION_LIPSCHITZ:
                raise ValueError(f"unsupported gated-norm activation: {activation}")
            specs["attention.gated_norm"] = {"kind": "gated", "weight": p + "linear_attn.norm.weight",
                                             "group": c.get("linear_value_head_dim"), "eps": eps,
                                             "activation": activation}
        else:
            specs["attention.q_norm"] = offset(p + "self_attn.q_norm.weight", c.get("head_dim"))
            specs["attention.k_norm"] = offset(p + "self_attn.k_norm.weight", c.get("head_dim"))
        if i + 1 in c.get("ple_layer_ids", []):
            for stem in ("norm_key", "norm_query", "norm_conv"):
                specs["ple." + stem] = offset(p + f"ple.{stem}.weight", hidden)
    for name, spec in specs.items():
        spec["input"] = name + ".input"
        if spec["kind"] == "gated":
            spec["gate"] = name + ".gate"
    return specs


def norm_auxiliary(config, unit):
    """Extra required traces: the exact input (and gate) each traced norm consumed."""
    return {v for spec in norm_specs(config, unit).values() for k, v in spec.items() if k in ("input", "gate")}


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


def router_boundary_swaps(reference_experts, candidate_experts, reference_logits, candidate_logits, dtype):
    """Gate amendment A2 (bf16 only; see gold_parity.md): classify expert-set differences.

    A row passes if both sides select the same set, or if the differing experts
    pair up one-to-one as boundary swaps: for each pair (a only in the
    reference set, b only in the candidate set), with allowance
    A = atol + rtol * min(|l_ref[a]|, |l_ref[b]|) (the router.logits gate),
    |l_ref[a] - l_ref[b]| <= A and |l_mlx[a] - l_mlx[b]| <= A, and a and b both
    lie within A of the k-th selected logit on each side.  Every other expert
    must match exactly.  The caller must then gate router.weights and moe of the
    swapped rows under teacher-forced routing.
    """
    import numpy as np
    if dtype != "bf16":
        return {"pass": False, "reason": "A2 applies to bf16 only"}
    t = TOLERANCES[dtype]
    ref_ids, mlx_ids = (np.asarray(_comparable(v)) for v in (reference_experts, candidate_experts))
    ref_logits, mlx_logits = (np.asarray(_comparable(v), dtype=np.float64) for v in (reference_logits, candidate_logits))
    if ref_ids.shape != mlx_ids.shape or ref_ids.ndim < 1 or ref_logits.shape != mlx_logits.shape:
        return {"pass": False, "reason": "shape_mismatch"}
    k, experts = ref_ids.shape[-1], ref_logits.shape[-1]
    ref_ids, mlx_ids = ref_ids.reshape(-1, k).astype(np.int64), mlx_ids.reshape(-1, k).astype(np.int64)
    ref_logits, mlx_logits = ref_logits.reshape(-1, experts), mlx_logits.reshape(-1, experts)
    if ref_logits.shape[0] != ref_ids.shape[0] or min(ref_ids.min(), mlx_ids.min()) < 0 or max(
            ref_ids.max(), mlx_ids.max()) >= experts or not (np.isfinite(ref_logits).all() and np.isfinite(mlx_logits).all()):
        return {"pass": False, "reason": "invalid_router_arrays"}
    rows, admissible, failed = [], [], []
    for r in range(ref_ids.shape[0]):
        ref_set, mlx_set = set(ref_ids[r].tolist()), set(mlx_ids[r].tolist())
        if ref_set == mlx_set:
            continue
        only_ref, only_mlx = sorted(ref_set - mlx_set), sorted(mlx_set - ref_set)
        kth = {"reference": ref_logits[r, ref_ids[r]].min(), "mlx": mlx_logits[r, mlx_ids[r]].min()}

        def pair(a, b):
            allow = t["atol"] + t["rtol"] * min(abs(ref_logits[r, a]), abs(ref_logits[r, b]))
            margins = (abs(ref_logits[r, a] - ref_logits[r, b]), abs(mlx_logits[r, a] - mlx_logits[r, b]))
            boundary = all(abs(logits[r, e] - kth[side]) <= allow for side, logits in
                           (("reference", ref_logits), ("mlx", mlx_logits)) for e in (a, b))
            return margins[0] <= allow and margins[1] <= allow and boundary, allow, margins

        match = {}

        def augment(a, seen):
            for b in only_mlx:
                if b not in seen and pair(a, b)[0]:
                    seen.add(b)
                    if b not in match or augment(match[b], seen):
                        match[b] = a
                        return True
            return False
        ok = (len(ref_set) == len(mlx_set) == k and len(only_ref) == len(only_mlx)
              and all(augment(a, set()) for a in only_ref))
        detail = {"row": r, "reference_only": only_ref, "candidate_only": only_mlx, "admissible": bool(ok)}
        if ok:
            detail["pairs"] = []
            for b, a in sorted(match.items(), key=lambda item: item[1]):
                _, allow, margins = pair(a, b)
                detail["pairs"].append({"reference": a, "candidate": b, "allowance": allow,
                                        "reference_margin": margins[0], "candidate_margin": margins[1],
                                        "exact_reference_tie": bool(margins[0] == 0.0)})
            admissible.append(r)
        else:
            failed.append(r)
        rows.append(detail)
    return {"pass": not failed, "gate": "A2-boundary-swap", "exact_set_agreement": not rows,
            "mismatched_rows": len(rows), "admissible_rows": admissible, "non_admissible_rows": failed,
            "admissible_swaps": sum(len(d.get("pairs", [])) for d in rows), "rows": rows}

class _Gate:
    """Streaming elementwise + cosine accumulator for one pair of arrays.

    ``left`` is the side whose magnitude scales rtol; ``allowance`` adds a
    per-element absolute allowance (A1 propagated bound) to atol.
    """
    def __init__(self, dtype):
        self.t = TOLERANCES[dtype]
        self.max_abs = self.max_relative = self.squared_a = self.squared_b = self.squared_diff = self.dot = 0.0
        self.within = self.size = 0

    def add(self, left, right, allowance=0.0):
        import numpy as np
        diff = np.abs(left-right)
        self.size += left.size
        self.max_abs = max(self.max_abs, float(diff.max()))
        self.max_relative = max(self.max_relative, float((diff/np.maximum(np.abs(left), 1e-12)).max()))
        self.within += int((diff <= self.t["atol"] + self.t["rtol"]*np.abs(left) + allowance).sum())
        self.squared_a += float(np.dot(left.ravel(), left.ravel()))
        self.squared_b += float(np.dot(right.ravel(), right.ravel()))
        self.squared_diff += float(np.dot(diff.ravel(), diff.ravel()))
        self.dot += float(np.dot(left.ravel(), right.ravel()))

    def result(self):
        a, b = self.squared_a, self.squared_b
        cosine = self.dot / max(math.sqrt(a)*math.sqrt(b), 1e-300) if a and b else float(a == b)
        return {"pass": bool(self.within == self.size and cosine >= self.t["cosine_min"]),
                "max_abs": self.max_abs, "max_relative": self.max_relative,
                "relative_l2": math.sqrt(self.squared_diff)/max(math.sqrt(a), 1e-12),
                "cosine": min(1.0, max(-1.0, cosine)), "fraction_within": self.within/self.size}


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
    gate = _Gate(dtype)
    for first in range(0, a.size, 262144):
        # .flat slices preserve C-order without materializing a noncontiguous
        # whole array. fp64 temporaries stay bounded to a few MiB each.
        left = a.flat[first:first+262144].astype(np.float64)
        right = b.flat[first:first+262144].astype(np.float64)
        if not np.isfinite(left).all() or not np.isfinite(right).all():
            return {"pass": False, "reason": "nonfinite"}
        gate.add(left, right)
    return gate.result()


def round_bf16(values):
    """IEEE round-to-nearest-even float32 -> bfloat16, returned as float32."""
    import numpy as np
    bits = np.ascontiguousarray(values, dtype=np.float32).view(np.uint32).astype(np.uint64)
    bits = (bits + 0x7FFF + ((bits >> 16) & 1)) & 0xFFFF0000
    return bits.astype(np.uint32).view(np.float32)


def norm_reference(x, weight, spec, gate=None):
    """Official norm formula in float64 on rows of shape (rows, len(weight)).

    Returns (y, r, mean_abs): per-element output and the per-element broadcast
    group RMS sqrt(mean(x^2)+eps) and group mean |x| of the input.
    """
    import numpy as np
    rows, width = x.shape
    g = x.reshape(rows, width // spec["group"], spec["group"])
    r = np.sqrt((g*g).mean(-1, keepdims=True) + spec["eps"])
    mean_abs = np.abs(g).mean(-1, keepdims=True)
    normed = (g / r).reshape(rows, width)
    r = np.broadcast_to(r, g.shape).reshape(rows, width)
    mean_abs = np.broadcast_to(mean_abs, g.shape).reshape(rows, width)
    if spec["kind"] == "offset":
        return normed * (1.0 + weight), r, mean_abs
    return normed * weight * gate_activation(gate, spec["activation"]), r, mean_abs


def gate_activation(gate, name):
    import numpy as np
    sigmoid = 0.5 * (1.0 + np.tanh(0.5 * gate))  # Overflow-free logistic.
    return sigmoid if name == "sigmoid" else gate * sigmoid


def norm_allowance(x_ref, x_mlx, weight, spec, z_ref=None, z_mlx=None):
    """Gate amendment A1's propagated allowance P, per element (float64 rows).

    A rigorous bound on |f(x_ref) - f(x_mlx)| for the official norm f, whose
    first-order expansion is P_c = |s_c| (|dx_c|/r + |x_c| mean_g|x_j dx_j| / r^3)
    (gold_parity.md). With n = x/r over the element's own RMS group g of G
    channels, r' the candidate input's RMS, and d = x_mlx - x_ref:
    n'_c - n_c = d_c/r' + x_c (r - r')/(r r'), and
    |r' - r| = |r'^2 - r^2|/(r + r') = |mean_g(2 x d + d^2)|/(r + r')
             <= (2 mean_g|x d| + mean_g d^2)/(r + r'),
    so no second-order remainder is neglected. Gated: f = w act(z) n, and
    |act(z') n' - act(z) n| <= |act(z')| |n' - n| + |n| L |z' - z|.
    Only the element's own row and group contribute.
    """
    import numpy as np
    rows, width = x_ref.shape
    group = spec["group"]
    shape = (rows, width // group, group)

    def per_group(value):
        return np.broadcast_to(value.reshape(shape).mean(-1, keepdims=True), shape).reshape(rows, width)
    d = x_mlx - x_ref
    r = np.sqrt(per_group(x_ref * x_ref) + spec["eps"])
    r_mlx = np.sqrt(per_group(x_mlx * x_mlx) + spec["eps"])
    rms_shift = (2.0 * per_group(np.abs(x_ref * d)) + per_group(d * d)) / (r + r_mlx)
    norm_delta = np.abs(d) / r_mlx + np.abs(x_ref) * rms_shift / (r * r_mlx)
    if spec["kind"] == "gated":
        lipschitz = ACTIVATION_LIPSCHITZ[spec["activation"]]
        return (np.abs(weight) * np.abs(gate_activation(z_mlx, spec["activation"])) * norm_delta
                + np.abs(weight) * np.abs(x_ref) / r * lipschitz * np.abs(z_mlx - z_ref))
    return np.abs(1.0 + weight) * norm_delta

def compare_norm(reference, candidate, reference_input, candidate_input, weight, spec, dtype,
                 reference_gate=None, candidate_gate=None):
    """Gate amendment A1 for a normalization-output trace (see gold_parity.md).

    PASS requires all of:
    - mlx_op: |y_mlx - f(x_mlx)| within the unchanged dtype gate (atol+rtol*|f|,
      cosine), f the official formula in float64 with checkpoint weights;
    - reference_op: the same for |y_ref - f(x_ref)| (reference self-consistency,
      which also validates this harness's transcription of f);
    - input (and gate): the two sides' norm inputs within the unchanged gate;
    - chained y_ref vs y_mlx: cosine floor unchanged, and elementwise
      |dy| <= atol + rtol*|y_ref| + P, P = norm_allowance(): a rigorous
      per-element bound on |f(x_ref) - f(x_mlx)| whose first-order term is
      P_c = |s_c| * (|dx_c|/r + |x_c| * mean_{j in group(c)} |x_j||dx_j| / r^3)
            [+ |w_c||n_c| L |dz_c| gated],
      computed from the element's own RMS group only (no error from another
      row or group is borrowed, and a group's cross term is never diluted).
    """
    import numpy as np
    arrays = [_comparable(v) for v in (reference, candidate, reference_input, candidate_input)]
    gated = spec["kind"] == "gated"
    if gated:
        if reference_gate is None or candidate_gate is None:
            return {"pass": False, "reason": "missing_gate_input"}
        arrays += [_comparable(reference_gate), _comparable(candidate_gate)]
    weight = np.asarray(weight, dtype=np.float32).ravel()
    if dtype == "bf16":
        weight = round_bf16(weight)  # The official module holds bf16 parameters.
    weight = weight.astype(np.float64)
    shapes = [tuple(a.shape) for a in arrays]
    width = weight.size
    if type(spec.get("group")) is not int or spec["group"] <= 0:
        return {"pass": False, "reason": "invalid_norm_spec", "group": spec.get("group")}
    if len(set(shapes)) != 1 or not shapes[0] or shapes[0][-1] != width or width % spec["group"]:
        return {"pass": False, "reason": "shape_mismatch", "shapes": [list(s) for s in shapes],
                "weight": width, "group": spec["group"]}
    if not arrays[0].size:
        return {"pass": False, "reason": "empty"}
    inputs = {"input": compare_arrays(arrays[2], arrays[3], dtype)}
    if gated:
        inputs["gate_input"] = compare_arrays(arrays[4], arrays[5], dtype)
    if any("max_abs" not in m for m in inputs.values()):
        return {"pass": False, "reason": "input_" + next(m.get("reason", "invalid") for m in inputs.values()
                                                         if "max_abs" not in m), **inputs}
    e_x = inputs["input"]["max_abs"]
    e_z = inputs["gate_input"]["max_abs"] if gated else 0.0
    lipschitz = ACTIVATION_LIPSCHITZ[spec["activation"]] if gated else 0.0
    chained, unpropagated, mlx_op, reference_op = (_Gate(dtype) for _ in range(4))
    max_allowance = 0.0
    step = width * max(1, 262144 // width)
    for first in range(0, arrays[0].size, step):
        y_ref, y_mlx, x_ref, x_mlx, *z = (a.flat[first:first+step].astype(np.float64).reshape(-1, width)
                                          for a in arrays)
        if not all(np.isfinite(v).all() for v in (y_ref, y_mlx, x_ref, x_mlx, *z)):
            return {"pass": False, "reason": "nonfinite"}
        z_ref, z_mlx = z if gated else (None, None)
        f_ref, _, _ = norm_reference(x_ref, weight, spec, z_ref)
        f_mlx, _, _ = norm_reference(x_mlx, weight, spec, z_mlx)
        reference_op.add(f_ref, y_ref)
        mlx_op.add(f_mlx, y_mlx)
        allowance = norm_allowance(x_ref, x_mlx, weight, spec, z_ref, z_mlx)
        max_allowance = max(max_allowance, float(allowance.max()))
        chained.add(y_ref, y_mlx, allowance)
        unpropagated.add(y_ref, y_mlx)
    result = chained.result()
    plain = unpropagated.result()
    result.update(
        gate="A1-input-conditioned",
        chained_pass=result["pass"],
        fraction_within_unpropagated=plain["fraction_within"],
        unpropagated_pass=plain["pass"],
        propagation={"input_max_abs": e_x, "gate_max_abs": e_z, "max_allowance": max_allowance,
                     "lipschitz": lipschitz},
        mlx_op=mlx_op.result(), reference_op=reference_op.result(), **inputs)
    result["pass"] = bool(result["chained_pass"] and result["mlx_op"]["pass"] and result["reference_op"]["pass"]
                          and all(m["pass"] for m in inputs.values()))
    return result
