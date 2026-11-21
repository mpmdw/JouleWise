#!/usr/bin/env python3
"""Offline Flash-Next tiny parity and pinned model_file regression."""
import argparse
from contextlib import contextmanager, ExitStack
from hashlib import sha256
import importlib.util
from importlib.metadata import version
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

import numpy as np

UPSTREAM_SHA = "78273eb38ba4d1be065086b555417222ec2a5aafef48436134b31401a94cb669"
PORT_SHA = "f4ec75d16f0af0517b63e202abeef704c9a775e9111949ab003250d51d982c37"
CASES = {"A": 1105, "B": 2116, "C": 3217}
DTYPES = ("fp32", "bf16")
PAIRS = (("hf", "upstream"), ("hf", "port"), ("upstream", "port"))
VENDOR_MODEL_FILE = (Path(__file__).resolve().parents[1]
                     / "joulewise/align/models/qwen4_exp_upstream.py")


def load_python(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def upstream_module():
    from mlx_lm.models import qwen4_exp

    if sha256(Path(qwen4_exp.__file__).read_bytes()).hexdigest() != UPSTREAM_SHA:
        raise ValueError("upstream module differs from c4c9c76")
    return qwen4_exp


def port_module(checkout):
    path = checkout / "joulewise/align/models/qwen4_exp.py"
    if sha256(path.read_bytes()).hexdigest() != PORT_SHA:
        raise ValueError("canonical module differs from 97d780d59")
    return load_python(path, "parity_canonical")


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n")


def components(model):
    for i, layer in enumerate(model.layers):
        yield f"L{i}.hidden", layer
        for name, attr in (("delta", "linear_attn"), ("qsa", "self_attn"),
                           ("attn_hc", "attn_hyper_connection"), ("mlp_hc", "mlp_hyper_connection"),
                           ("moe", "mlp"), ("ple", "ple")):
            module = getattr(layer, attr, None)
            if module is not None:
                yield f"L{i}.{name}", module
        if getattr(layer, "self_attn", None) is not None:
            yield f"L{i}.indexer", layer.self_attn.indexer
        if getattr(layer, "ple", None) is not None and hasattr(layer.ple, "ple_embedding"):
            yield f"L{i}.ngram", layer.ple.ple_embedding
        yield f"L{i}.shared", layer.mlp.shared_expert
        if hasattr(layer.mlp, "switch_mlp"):
            yield f"L{i}.router", layer.mlp.switch_mlp
        else:
            yield f"L{i}.router", layer.mlp.gate
    yield "mixer", model.hyper_connection_mixer


def record(out, name, value, as_numpy):
    if name.endswith("_hc"):
        out[name + ".mix"] = as_numpy(value[0])
        out[name + ".inject"] = as_numpy(value[-1])
    elif name.endswith(".shared"):
        array = as_numpy(value)
        out[name] = array.reshape(1, -1, array.shape[-1])
    elif name.endswith(".router"):
        indices = as_numpy(value)
        out[name] = np.sort(indices.reshape(-1, indices.shape[-1]), axis=-1)
    elif isinstance(value, tuple):
        out[name] = as_numpy(value[0])
    else:
        out[name] = as_numpy(value)


def reference(directory, checkout, case, dtype, key_head_dim=None):
    import torch
    import transformers
    from safetensors.torch import save_file
    from transformers import DynamicCache

    if transformers.__version__ != "5.22.1":
        raise ValueError("expected transformers 5.22.1")
    prior = load_python(checkout / "scripts/audit_mlxvlm/ref_gen.py", "parity_prior")
    gold = load_python(checkout / "tests/align/test_qwen4_exp_canonical.py", "parity_gold")
    config = getattr(prior, f"config_{case.lower()}")()
    # Serialize the official spelling. HF canonicalizes it to indexed_attention.
    config["layer_types"] = ["full_attention" if t == "indexed_attention" else t
                             for t in config["layer_types"]]
    config.update(rms_norm_eps=1e-6, tie_word_embeddings=False, norm_topk_prob=True)
    if key_head_dim is not None:
        config["linear_key_head_dim"] = key_head_dim
    model = prior.build_model(config, CASES[case])
    gold.randomize(model, torch, CASES[case])
    model.to(device="cpu", dtype=getattr(torch, {"fp32": "float32", "bf16": "bfloat16"}[dtype]))
    ids = prior.ids_for(case)
    # Export the actual in-memory state, including hash buffers. Preserve bf16 bits.
    weights = {}
    for name, value in model.state_dict().items():
        if name.startswith("model."):
            name = "model.language_model." + name.removeprefix("model.")
        if name.endswith(".ngram_embedding.weight"):
            shards = value.chunk(config["split_ngram_parts"], dim=0)
            if len(shards) != config["split_ngram_parts"] or len({s.shape for s in shards}) != 1:
                raise ValueError("expected equal HF n-gram row shards")
            for j, shard in enumerate(shards):
                weights[name.replace(".weight", f".shard_{j}.weight")] = shard.contiguous()
        else:
            weights[name] = value.contiguous()
    save_file(weights, directory / "hf.safetensors")
    write_json(directory / "config.json", dict(model_type="qwen4_exp", text_config=config,
                                                ids=ids, seed=CASES[case]))
    out = {}
    as_numpy = lambda value: value.detach().float().numpy().copy()
    def capture(name, value):
        if name.endswith(".indexer"):
            value = value == 0 if value.is_floating_point() else value
        if name.endswith(".router"):
            value = value[2]
        record(out, name, value, as_numpy)

    with ExitStack() as stack, torch.inference_mode():
        for name, module in components(model.model):
            handle = module.register_forward_hook(
                lambda _m, _a, value, key=name: capture(key, value))
            stack.callback(handle.remove)
        ids = torch.tensor([ids])
        out["logits"] = as_numpy(model(ids, use_cache=False).logits)
    with torch.inference_mode():
        cache = DynamicCache(config=model.config)
        out["stepwise"] = np.concatenate([
            as_numpy(model(ids[:, i:i + 1], past_key_values=cache, use_cache=True).logits)
            for i in range(ids.shape[1])], axis=1)
        cache = DynamicCache(config=model.config)
        tokens = []
        for _ in range(8):
            value = model(ids, past_key_values=cache, use_cache=True).logits
            ids = value[:, -1].argmax(-1, keepdim=True)
            tokens.append(int(ids.item()))
        out["greedy"] = np.asarray(tokens)
    np.savez_compressed(directory / "hf.npz", **out)


def canonical_weights(module, config, weights, directory, dtype):
    import mlx.core as mx

    tables = {}
    storage = "f32" if dtype == "fp32" else "bf16"
    args = module.TextModelArgs.from_dict(config["text_config"])
    for i, lid in enumerate(args.ple_layer_ids):
        prefix = f"model.language_model.layers.{lid - 1}.ple.ple_embedding.ngram_embedding.shard_"
        spec = module.NgramHashSpec(args, i)
        shards = [weights[f"{prefix}{j}.weight"] for j in range(args.split_ngram_parts)]
        gathered = mx.concatenate(shards, axis=0).astype(mx.float32)
        if gathered.shape != (spec.padded_vocab_size, spec.head_dim):
            raise ValueError("unexpected canonical PLE table shape")
        name = f"ngram-{lid - 1}.bin"
        (directory / name).write_bytes(module.encode_ngram_rows(np.asarray(gathered), storage, 32).tobytes())
        tables[str(lid - 1)] = dict(file=name, rows=spec.padded_vocab_size,
                                   dim=spec.head_dim, format=storage)
    cfg = dict(config, ngram_tables=dict(dir=str(directory.resolve()), layers=tables))
    model = module.Model(module.ModelArgs.from_dict(cfg))
    return model, model.sanitize(weights)


def capture_mlx(model, body, ids, port):
    import mlx.core as mx

    targets = {id(layer): name for name, layer in components(body)}
    by_class = {type(layer) for _, layer in components(body)}
    out = {}

    def as_numpy(value):
        value = value.astype(mx.float32)
        mx.eval(value)
        return np.array(value)

    def tracer(method):
        def traced(layer, *args, **kwargs):
            value = method(layer, *args, **kwargs)
            name = targets.get(id(layer))
            if name is not None:
                if port and name.endswith(".indexer"):
                    value_to_record = value.mask
                elif name.endswith(".router"):
                    value_to_record = args[1]
                else:
                    value_to_record = value
                record(out, name, value_to_record, as_numpy)
                if port and name.endswith(".ple"):
                    out[name.replace(".ple", ".ngram")] = as_numpy(args[1])
            return value
        return traced

    with ExitStack() as stack:
        for cls in by_class:
            stack.enter_context(patch.object(cls, "__call__", tracer(cls.__call__)))
        out["logits"] = as_numpy(model(ids))
    cache = model.make_cache()
    out["stepwise"] = np.concatenate([
        as_numpy(model(ids[:, i:i + 1], cache=cache))
        for i in range(ids.shape[1])], axis=1)
    cache = model.make_cache()
    greedy = []
    for _ in range(8):
        logits = model(ids, cache=cache)
        ids = logits[:, -1].argmax(-1, keepdims=True)
        greedy.append(int(ids.item()))
    out["greedy"] = np.asarray(greedy)
    return out


def mlx(directory, checkout, dtype, which):
    import mlx.core as mx

    config = json.loads((directory / "config.json").read_text())
    weights = mx.load(str(directory / "hf.safetensors"))
    if which == "upstream":
        module = upstream_module()
        model = module.Model(module.ModelArgs.from_dict(config))
        weights = model.sanitize(weights)
        body = model.model
    else:
        module = port_module(checkout)
        model, weights = canonical_weights(module, config, weights, directory, dtype)
        body = model.language_model.model
    model.load_weights(list(weights.items()), strict=True)
    model.eval()
    out = capture_mlx(model, body, mx.array([config["ids"]]), port=which == "port")
    np.savez_compressed(directory / f"{which}.npz", **out)


@contextmanager
def vendored_checkpoint(directory, config, weights):
    with TemporaryDirectory(dir=directory) as tmp:
        checkpoint = Path(tmp)
        (checkpoint / VENDOR_MODEL_FILE.name).write_bytes(VENDOR_MODEL_FILE.read_bytes())
        (checkpoint / "model.safetensors").symlink_to(weights.resolve())
        write_json(checkpoint / "config.json", dict(config, model_file=VENDOR_MODEL_FILE.name))
        yield checkpoint


def vendor(directory):
    """Check the pinned model_file loader against the FP32 reference and upstream."""
    import mlx.core as mx
    from mlx_lm.utils import load_model

    if (version("mlx"), version("mlx-lm")) != ("0.31.2", "0.31.3"):
        raise ValueError("vendor regression requires mlx 0.31.2 and mlx-lm 0.31.3")
    if not mx.metal.is_available():
        raise RuntimeError("vendor regression requires Metal")
    config = json.loads((directory / "config.json").read_text())
    with vendored_checkpoint(directory, config, directory / "hf.safetensors") as checkpoint, mx.stream(mx.gpu):
        model, _ = load_model(checkpoint)
        out = capture_mlx(model, model.model, mx.array([config["ids"]]), port=False)

    result = {}
    for source in ("hf", "upstream"):
        with np.load(directory / f"{source}.npz") as expected:
            result[f"{source}/vendor"] = {
                key: metrics(expected[key], out[key], 0.0 if key == "greedy" else 1e-4)
                for key in ("logits", "stepwise", "greedy")
            }
    write_json(directory / "vendor-results.json", result)
    if not all(row["pass"] for pair in result.values() for row in pair.values()):
        raise SystemExit(f"Pinned model_file parity failed: {directory / 'vendor-results.json'}")


def metrics(a, b, atol):
    if a.shape != b.shape:
        return {"pass": False, "shapes": [a.shape, b.shape]}
    if not (np.isfinite(a).all() and np.isfinite(b).all()):
        return {"pass": False, "nonfinite": True}
    delta = np.abs(a.astype(np.float64) - b)
    index = np.unravel_index(delta.argmax(), delta.shape)
    return {"pass": bool(delta.max() <= atol), "max_abs": float(delta.max()),
            "rms": float(np.sqrt((delta ** 2).mean())), "atol": atol,
            "first_max_index": [int(i) for i in index], "values": [float(a[index]), float(b[index])],
            "unequal": int(np.count_nonzero(delta))}


def compare(root, cases, dtypes, row):
    result = {}
    for case in cases:
        hf32 = np.load(root / f"{case}-fp32" / "hf.npz")
        for dtype in dtypes:
            directory = root / f"{case}-{dtype}"
            arrays = {src: np.load(directory / f"{src}.npz") for src in ("hf", "upstream", "port")}
            keys = sorted(set.union(*(set(data.files) for data in arrays.values())))
            if row:
                if row not in keys:
                    raise ValueError(f"{directory.name} has no row {row}")
                keys = [row]
            rows = {}
            for key in keys:
                if key.endswith((".indexer", ".router")) or key == "greedy":
                    atol = 0.0
                elif dtype == "fp32":
                    atol = 1e-4
                else:
                    # Historical gold bound vs the reference's own dtype drift.
                    noise = np.max(np.abs(arrays["hf"][key] - hf32[key]))
                    atol = float(max(1e-4, 1.5 * noise))
                rows[key] = {f"{a}/{b}": metrics(arrays[a][key], arrays[b][key], atol)
                             if key in arrays[a] and key in arrays[b] else
                             {"pass": False, "missing": [s for s in (a, b) if key not in arrays[s]]}
                             for a, b in PAIRS}
            for src, array in arrays.items():
                for key in (k for k in array.files if k.endswith(".indexer")):
                    selected = array[key].astype(bool).sum(axis=-1)
                    visible = np.arange(1, selected.shape[-1] + 1)
                    if not np.any(selected < visible):
                        raise ValueError(f"{case}-{dtype} {src} {key} did not prune visible tokens")
            result[directory.name] = rows
    if row:
        print(json.dumps(result, indent=2, allow_nan=False))
    else:
        write_json(root / "tiny-results.json", result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["reference", "upstream", "port", "compare", "vendor"])
    parser.add_argument("root", type=Path)
    parser.add_argument("--port", type=Path)
    parser.add_argument("--case", choices=CASES)
    parser.add_argument("--dtype", choices=DTYPES)
    parser.add_argument("--row", help="print metrics for one comparison row")
    parser.add_argument("--linear-key-head-dim", type=int, choices=range(1, 257),
                        metavar="WIDTH", help="override one reference fixture's DeltaNet key width")
    args = parser.parse_args()
    if args.linear_key_head_dim is not None and (args.stage != "reference" or not args.case):
        parser.error("--linear-key-head-dim requires the reference stage and one --case")
    if args.stage == "vendor":
        if args.dtype not in (None, "fp32"):
            parser.error("the vendor regression requires fp32 fixtures")
        args.dtype = "fp32"
    cases = (args.case,) if args.case else CASES
    dtypes = (args.dtype,) if args.dtype else DTYPES
    if args.stage == "compare":
        compare(args.root, cases, dtypes, args.row)
        return
    if args.stage in ("reference", "port") and args.port is None:
        parser.error("this stage requires --port")
    if args.stage == "reference":
        import torch

        torch.set_num_threads(2)
        torch.set_num_interop_threads(1)
    for case in cases:
        for dtype in dtypes:
            directory = args.root / f"{case}-{dtype}"
            directory.mkdir(parents=True, exist_ok=True)
            print(args.stage, case, dtype, flush=True)
            if args.stage == "reference":
                reference(directory, args.port, case, dtype, args.linear_key_head_dim)
            elif args.stage == "vendor":
                vendor(directory)
            else:
                mlx(directory, args.port, dtype, args.stage)


if __name__ == "__main__":
    main()
