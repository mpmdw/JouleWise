"""gold/v1 storage and trace adapter for the separately supplied canonical port.

Declare both qwen4_exp.py and canonical_converter.py (or
align_convert_qwen4_exp.py) with --adapter-dependency. Nothing imports the model
from the package tree. No Torch, converted checkpoint, quantization, or full
embedding/expert/PLE table is needed in this worker.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
from pathlib import Path

GOLD_ADAPTER_VERSION = 1
GOLD_ADAPTER_KIND = "mlx"


def dependency_sources(request):
    """Resolve roles only among declared dependencies; hash before executing.

    Return the exact bytes whose digests were frozen by the coordinator. This
    also avoids executing a stale sibling __pycache__ file through importlib.
    """
    dependencies = request.get("adapter_dependencies", {})
    roles = {"module": {"qwen4_exp.py"},
             "converter": {"canonical_converter.py", "align_convert_qwen4_exp.py"}}
    sources, provenance = {}, {}
    for role, names in roles.items():
        paths = [Path(p) for p in dependencies if Path(p).name in names]
        if len(paths) != 1:
            raise ValueError(f"declare exactly one canonical {role} using --adapter-dependency ({sorted(names)})")
        path = paths[0]
        if "restricted" in path.parts:
            raise ValueError("restricted dependency path refused")
        source = path.read_bytes()
        actual = hashlib.sha256(source).hexdigest()
        if actual != dependencies[str(path)]:
            raise ValueError(f"adapter dependency changed after fingerprinting: {path.name}")
        sources[role] = (path, source)
        provenance[role] = {"path": str(path), "sha256": actual}
    return sources, provenance


def import_source(name, path, source):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses needs its defining module registered
    exec(compile(source, str(path), "exec", dont_inherit=True), module.__dict__)
    return module


def unit_inventory(checkpoint, converter, rules, unit):
    """Use the converter's inventory, expert packing and conv shape rules.

    sources() reads headers of selected shards only. Actual data always goes
    through checkpoint.read/rows/ngram_rows and its guards. A temporary header
    inventory view lets the unmodified converter ignore unrelated, un-hashed
    shards in a full offline checkpoint. It contains links, never copied weights.
    """
    stem = "language_model.model."
    if unit == "final":
        prefix = stem + "hyper_connection_mixer."
        original_prefix = checkpoint.prefix + "hyper_connection_mixer."
    elif unit.isdigit():
        prefix = stem + f"layers.{int(unit)}."
        original_prefix = checkpoint.prefix + f"layers.{int(unit)}."
    else:
        raise ValueError(f"no dense inventory for {unit}")
    shards = {checkpoint.weight_map[k] for k in checkpoint.weight_map if k.startswith(original_prefix)
              and not rules.is_ngram_table_key(rules.hf_to_mlx_key(k))}
    with tempfile.TemporaryDirectory(prefix="qwen4-gold-inventory-") as directory:
        for shard in sorted(shards):
            (Path(directory) / shard).symlink_to(checkpoint.path(shard))
        inventory, _, _, _, _ = converter.sources(directory, rules)
        for shard in shards:
            checkpoint.path(shard)
    return {k[len(prefix):]: v for k, v in inventory.items()
            if k.startswith(prefix) and not rules.is_ngram_table_key(k)}


def checkpoint_hash_spec(checkpoint, rules, args, layer):
    """Canonical hashing, with all three persistent buffers from the checkpoint.

    Replace both host representations: NgramHashSpec has a scalar decode path
    as well as a vector prefill path. Config defaults never replace saved bits.
    """
    import numpy as np
    spec = rules.NgramHashSpec(args, args.ple_layer_ids.index(layer + 1))
    prefix = checkpoint.prefix + f"layers.{layer}.ple.ple_embedding."
    for suffix, field, internal, count in (
        ("layer_multipliers", "multipliers", "_mult", args.ngram_size),
        ("ngram_heads_vocab_sizes", "head_vocab_sizes", "_sizes", spec.ngram_heads),
        ("ngram_heads_offsets", "head_offsets", "_offsets", spec.ngram_heads),
    ):
        name = prefix + suffix
        if checkpoint.info(name) != ((count,), "I64"):
            raise ValueError(f"persistent PLE buffer shape/dtype mismatch: {name}")
        value = checkpoint.read(name, dtype="native")
        setattr(spec, field, value.tolist())
        setattr(spec, internal, np.asarray(value, dtype=np.int64))
    if np.any(spec._sizes <= 0) or np.any(spec._offsets < 0):
        raise ValueError("invalid PLE hash sizes/offsets")
    return spec, prefix + "ngram_embedding"


def run_gold(request, checkpoint):
    sources, provenance = dependency_sources(request)
    import numpy as np
    import mlx.core as mx
    from mlx.utils import tree_flatten
    import importlib.metadata

    # Leave RSS headroom: the coordinator counts RSS plus the Metal peak.
    mx.set_memory_limit(request["max_memory_bytes"] // 2)
    mx.set_cache_limit(32 * 1024**2)
    mx.reset_peak_memory()
    converter = import_source("gold_canonical_converter", *sources["converter"])
    if provenance["module"]["sha256"] != converter.MODULE_SHA256:
        raise ValueError("canonical module disagrees with converter's MODULE_SHA256 pin")
    for package, version in converter.PINS.items():
        if importlib.metadata.version(package) != version:
            raise ValueError(f"canonical adapter requires {package} {version}")
    rules = import_source("gold_canonical_qwen4_exp", *sources["module"])
    args = rules.TextModelArgs.from_dict(checkpoint.text)
    dtype = mx.float32 if request["dtype"] == "fp32" else mx.bfloat16
    traces = {}
    trace_suffix = [""]  # ".forced" during the A2 teacher-forced re-run

    def capture(name, value):
        mx.eval(value)
        if mx.issubdtype(value.dtype, mx.floating):
            value = value.astype(mx.float32)
        traces[name + trace_suffix[0]] = np.array(value)

    class Observe(rules.nn.Module):
        def __init__(self, inner, callback):
            super().__init__()
            self.inner = inner
            self.callback = callback

        def __call__(self, *a, **kw):
            out = self.inner(*a, **kw)
            self.callback(a, out)
            return out

    def observe(owner, attr, name, transform=lambda x: x):
        setattr(owner, attr, Observe(getattr(owner, attr), lambda a, o: capture(name, transform(o))))

    def observe_norm(owner, attr, name, transform=lambda x: x):
        # Gate amendment A1: also export the exact input (and gate) consumed.
        def callback(a, o):
            capture(name + ".input", transform(a[0]))
            if len(a) > 1:
                capture(name + ".gate", transform(a[1]))
            capture(name, transform(o))
        setattr(owner, attr, Observe(getattr(owner, attr), callback))

    unit = request["unit"]
    ids = np.asarray(request["input_ids"], dtype=np.int64)
    B, S = ids.shape
    hidden = None if request.get("hidden") is None else mx.array(
        np.load(request["hidden"], allow_pickle=False)).astype(dtype)

    def read(name, selection=None):
        return checkpoint.read(name, selection, "mlx", request["dtype"])

    def load_dense(module, inventory):
        expected = dict(tree_flatten(module.parameters()))
        if set(expected) != set(inventory):
            raise ValueError(f"canonical unit inventory mismatch: missing={sorted(set(expected)-set(inventory))}; "
                             f"unexpected={sorted(set(inventory)-set(expected))}")
        weights = []
        for name, parameter in expected.items():
            entries = inventory[name]
            if len(entries) != 1 or converter.target_shape(entries) != tuple(parameter.shape):
                raise ValueError(f"canonical parameter shape mismatch: {name}")
            _, _, original, _, kind = entries[0]
            value = read(original)
            if kind == "conv":
                value = value.transpose(0, 2, 1)
            weights.append((name, value))
        module.load_weights(weights, strict=True)
        module.eval()

    class SlicedExperts(rules.nn.Module):
        """Storage dispatch only: each selected expert uses canonical GLU math.

        The canonical switch module needs resident [E,2I,H] weights. Invoke that
        same module with E=1 on each expert's selected rows, evaluate, and release
        its weights before the next read. Never concatenate the expert axis.
        """
        def __init__(self, inventory):
            super().__init__()
            self._inventory = inventory
            expected = {"gate_up_proj.weight": (args.num_experts, 2*args.moe_intermediate_size, args.hidden_size),
                        "down_proj.weight": (args.num_experts, args.hidden_size, args.moe_intermediate_size)}
            if set(inventory) != set(expected):
                raise ValueError("missing/unexpected canonical routed expert tensors")
            for name, shape in expected.items():
                if converter.target_shape(inventory[name]) != shape:
                    raise ValueError(f"canonical expert shape mismatch: {name}")

        def __call__(self, x, indices):
            choices = np.array(indices).reshape(-1, args.num_experts_per_tok)
            flat = x.reshape(-1, args.hidden_size)
            result = np.empty((*choices.shape, args.hidden_size), dtype=np.float32)
            for expert in np.unique(choices):
                tokens, slots = np.nonzero(choices == expert)
                block = rules.FusedSwitchGLU(args.hidden_size, args.moe_intermediate_size, 1)
                weights = []
                for name, entries in self._inventory.items():
                    if entries[0][4] == "expert":
                        count = 2 if name.startswith("gate_up") else 1
                        pieces = entries[count*int(expert):count*(int(expert)+1)]
                        value = mx.concatenate([read(e[2], (slice(None), slice(None))) for e in pieces], axis=0)
                    else:
                        value = read(entries[0][2], (int(expert), slice(None), slice(None)))
                    weights.append((name, value[None]))
                block.load_weights(weights, strict=True)
                block.eval()
                y = block(flat[mx.array(tokens.astype(np.int32))], mx.zeros((len(tokens), 1), mx.int32))
                mx.eval(y)
                result[tokens, slots] = np.array(y[:, 0].astype(mx.float32))
                del block, weights, value, y
                mx.clear_cache()
            return mx.array(result.reshape(*indices.shape, args.hidden_size)).astype(x.dtype)

    if unit == "embed":
        out = checkpoint.rows(checkpoint.prefix + "embed_tokens.weight", ids, "mlx", request["dtype"])
        capture("embedding", out)
        # TextModel.__call__: flattened (stream, hidden), not per-element repeat.
        out = mx.tile(out, (1, 1, args.hc_count))
    elif unit == "head":
        name = "lm_head.weight"
        if name not in checkpoint.weight_map and args.tie_word_embeddings:
            name = checkpoint.prefix + "embed_tokens.weight"
        rows, width = checkpoint.info(name)[0]
        if hidden.shape != (B, S, width):
            raise ValueError("head hidden shape mismatch")
        outputs = []
        for start in range(0, rows, 1024):
            stop = min(rows, start + 1024)
            head = rules.nn.Linear(width, stop-start, bias=False)
            head.weight = read(name, (slice(start, stop), slice(None)))
            y = head(hidden)
            mx.eval(y)
            outputs.append(y)
            del head
        out = mx.concatenate(outputs, axis=-1)
    elif unit == "final":
        module = rules.GatedResidual(args, use_combine=False)
        load_dense(module, unit_inventory(checkpoint, converter, rules, unit))
        observe_norm(module, "hc_norm", "final.norm")
        out = module(hidden)
    else:
        layer = int(unit)
        module = rules.DecoderLayer(args, layer)
        inventory = unit_inventory(checkpoint, converter, rules, unit)
        expert_prefix = "mlp.switch_mlp."
        expert_inventory = {k[len(expert_prefix):]: v for k, v in inventory.items() if k.startswith(expert_prefix)}
        module.mlp.switch_mlp = SlicedExperts(expert_inventory)
        load_dense(module, {k: v for k, v in inventory.items() if not k.startswith(expert_prefix)})
        # Force the canonical mask path so gold/v1 can export the full selection.
        # These fresh caches are discarded after this cache-free prefill call.
        fresh = lambda: (rules._Context(B, S, 0, np.zeros(B, np.int64), rules.rope_inv_freq(args),
                                        None, S+1, S+1, False), rules.make_layer_caches(args)[layer])
        ctx, cache = fresh()
        emb = None
        if module.has_ple:
            spec, base = checkpoint_hash_spec(checkpoint, rules, args, layer)
            history = np.concatenate([np.full((B, spec.context_len), spec.eos, np.int64), ids], axis=1)
            ngram_ids = spec.ngram_ids(history, S)
            traces["ple.ngram_ids"] = ngram_ids
            emb = checkpoint.ngram_rows(base, ngram_ids, "mlx", request["dtype"]).reshape(B, S, -1)
            capture("ple.embedding", emb)
            ctx.ngram_emb[layer] = emb
            for stem in ("norm_key", "norm_query", "norm_conv"):
                observe_norm(module.ple, stem, "ple." + stem)
            observe(module, "ple", "ple")
        for stem in ("attn", "mlp"):
            attr = stem + "_hyper_connection"
            hc = getattr(module, attr)
            observe_norm(hc, "hc_norm", stem + ".norm")
            def hyper_trace(a, o, stem=stem):
                for suffix, value in zip(("mix", "residual", "inject"), o):
                    capture(stem + "." + suffix, value)
                if stem == "mlp":
                    capture("attn.streams", a[0])
            setattr(module, attr, Observe(hc, hyper_trace))
        attention = module.linear_attn if module.is_linear else module.self_attn
        if module.is_linear:
            observe_norm(attention, "norm", "attention.gated_norm", lambda o: o.reshape(-1, args.linear_value_head_dim))
        else:
            observe_norm(attention, "q_norm", "attention.q_norm")
            observe_norm(attention, "k_norm", "attention.k_norm")
            def selection_trace(a, selection):
                mask = selection.mask
                if selection.kind == "dense":
                    # No padding; all visible tokens are selected in dense mode.
                    mask = mx.broadcast_to(mx.array(np.tri(S, dtype=bool))[None, None], (B, 1, S, S))
                elif selection.kind != "mask":
                    raise ValueError("gold prefill requires canonical dense/mask selection")
                capture("qsa.mask", mask)
            attention.indexer = Observe(attention.indexer, selection_trace)
        observe(module, "linear_attn" if module.is_linear else "self_attn", "attention")
        route = module.mlp.route
        routed = {}
        def traced_route(x):
            if "forced" in routed:
                # Gate amendment A2 teacher forcing: the canonical route itself,
                # with only its top-k selection replaced by the reference's.
                forced = routed["forced"]
                original = mx.argpartition
                mx.argpartition = lambda a, kth, axis=-1: forced
                try:
                    logits, indices, scores = route(x)
                finally:
                    mx.argpartition = original
            else:
                logits, indices, scores = route(x)
                routed.update(shape=indices.shape)
            capture("router.logits", logits.reshape(-1, args.num_experts))
            capture("router.experts", indices.reshape(-1, args.num_experts_per_tok))
            capture("router.weights", scores.reshape(-1, args.num_experts_per_tok))
            return logits, indices, scores
        module.mlp.route = traced_route
        observe(module, "mlp", "moe")
        out = module(hidden, ctx, cache)
        capture("mlp.streams", out)
        forced_path = request.get("forced_experts")
        if forced_path:
            if hashlib.sha256(Path(forced_path).read_bytes()).hexdigest() != request.get("forced_experts_sha256"):
                raise ValueError("reference router.experts changed after the reference worker")
            reference = np.load(forced_path, allow_pickle=False)
            mine = traces["router.experts"]
            if reference.shape != mine.shape:
                raise ValueError("reference router.experts shape mismatch")
            if any(set(r.tolist()) != set(m.tolist()) for r, m in zip(reference, mine)):
                # Only when the expert sets differ: the whole canonical layer
                # again, on the same input with fresh caches, under the
                # reference's expert selection (A2). Every trace it emits is
                # recorded as <trace>.forced; the unforced traces stay as they are.
                routed["forced"] = mx.array(reference.astype(np.uint32)).reshape(routed["shape"])
                trace_suffix[0] = ".forced"
                ctx, cache = fresh()
                if emb is not None:
                    # Token-id functions, computed before the layer: identical.
                    traces["ple.ngram_ids.forced"] = traces["ple.ngram_ids"]
                    capture("ple.embedding", emb)
                    ctx.ngram_emb[layer] = emb
                forced_out = module(hidden, ctx, cache)
                capture("mlp.streams", forced_out)
                capture("output", forced_out)
                trace_suffix[0] = ""
    capture("output", out)
    return traces, {"device": str(mx.default_device()), "mlx_version": importlib.metadata.version("mlx"),
                    "peak_mlx_bytes": mx.get_peak_memory(), "canonical_sources": provenance,
                    "module_sha256": provenance["module"]["sha256"],
                    "converter_sha256": provenance["converter"]["sha256"],
                    "experts": "canonical FusedSwitchGLU with one checkpoint expert resident"}
