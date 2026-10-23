#!/usr/bin/env python3
"""Format-derived BYTES accounting. Headers need only stdlib; kv is a Mac desk task.

Nothing in headers/merge loads a model. ``kv`` explicitly performs inference and
must only be run separately on the Mac, without power capture. All sizes are
bytes (GB fields use 10**9), never memory-controller traffic measurements.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DTYPE_BYTES = {"BOOL": 1, "U8": 1, "I8": 1, "F8_E4M3": 1, "F8_E5M2": 1,
               "I16": 2, "U16": 2, "F16": 2, "BF16": 2, "I32": 4, "U32": 4,
               "F32": 4, "I64": 8, "U64": 8, "F64": 8}
FAMILIES = {"qwen3", "qwen3_moe", "qwen3_next", "qwen3_5_moe", "qwen3_5_moe_text", "llama"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def config_at(directory):
    cfg = json.loads((directory / "config.json").read_bytes())
    return {**cfg, **cfg.get("text_config", {})}


def identity(directory, cfg, revision=None):
    tok = directory / "tokenizer.json"
    tok_cfg = directory / "tokenizer_config.json"
    model_name = directory.name
    if directory.parent.name == "snapshots" and directory.parent.parent.name.startswith("models--"):
        model_name = directory.parent.parent.name.split("--")[-1]
    return {"model_dir": str(directory.resolve()), "model_name": model_name,
            "revision": revision or cfg.get("_commit_hash") or (
                directory.name if directory.parent.name == "snapshots" else None),
            "config_sha256": digest((directory / "config.json").read_bytes()),
            "tokenizer": {"tokenizer_json_sha256": digest(tok.read_bytes()) if tok.exists() else None,
                          "tokenizer_config_sha256": digest(tok_cfg.read_bytes()) if tok_cfg.exists() else None}}


def read_headers(directory):
    """Validate stored spans against dtype/shape, across every shard, without data reads."""
    tensors, shards = {}, {}
    files = sorted(directory.glob("*.safetensors"))
    if not files:
        raise ValueError("no safetensors files")
    for path in files:
        with path.open("rb") as stream:
            raw = stream.read(8)
            if len(raw) != 8:
                raise ValueError(f"truncated safetensors prefix: {path.name}")
            length = struct.unpack("<Q", raw)[0]
            if length > 100_000_000 or length > path.stat().st_size - 8:
                raise ValueError(f"invalid safetensors header length: {path.name}")
            def unique(pairs):
                obj = {}
                for key, value in pairs:
                    if key in obj:
                        raise ValueError(f"duplicate header key: {key}")
                    obj[key] = value
                return obj
            header = json.loads(stream.read(length), object_pairs_hook=unique)
        end = 0
        for name, item in sorted(((n, v) for n, v in header.items() if n != "__metadata__"),
                                 key=lambda row: row[1]["data_offsets"][0]):
            if name in tensors:
                raise ValueError(f"duplicate tensor across shards: {name}")
            dtype, shape, offsets = item["dtype"], item["shape"], item["data_offsets"]
            if dtype not in DTYPE_BYTES or not isinstance(shape, list) or any(type(x) is not int or x < 0 for x in shape):
                raise ValueError(f"unsupported dtype/shape: {name}")
            size = math.prod(shape) * DTYPE_BYTES[dtype]
            if (len(offsets) != 2 or any(type(x) is not int for x in offsets)
                    or offsets != [end, end + size] or 8 + length + offsets[1] > path.stat().st_size):
                raise ValueError(f"invalid stored span: {name}")
            tensors[name] = {"dtype": dtype, "shape": shape, "stored_bytes": size}
            shards[name] = path.name
            end = offsets[1]
        if 8 + length + end != path.stat().st_size:
            raise ValueError(f"unaccounted safetensors payload: {path.name}")
    index = directory / "model.safetensors.index.json"
    if index.exists():
        expected = json.loads(index.read_bytes())["weight_map"]
        if expected != shards:
            raise ValueError("safetensors index/header tensor inventory mismatch")
    return tensors


def classify(name):
    """Closed language-model naming vocabulary; unknown tensors require review."""
    # Match the discarded namespaces before stripping language-model prefixes.
    if name.startswith(("vision_tower.", "model.visual.")) or re.search(r"(?:^|\.)mtp\.", name):
        return "not_loaded"
    n = name
    for prefix in ("model.language_model.", "language_model.model.", "language_model.", "model."):
        if n.startswith(prefix):
            n = n[len(prefix):]
            break
    leaf = r"(?:weight|bias|scales|biases)"
    if re.fullmatch(r"embed_tokens\." + leaf, n):
        return "embed"
    if re.fullmatch(r"lm_head\." + leaf, n):
        return "lm_head"
    if re.fullmatch(r"norm\." + leaf, n):
        return "always_active"
    match = re.fullmatch(r"layers\.\d+\.(.+)", n)
    if not match:
        raise ValueError(f"unclassified tensor: {name}")
    n = match[1]
    if re.fullmatch(r"(?:input_layernorm|post_attention_layernorm|pre_mlp_layernorm|post_mlp_layernorm)\." + leaf, n):
        return "always_active"
    if re.fullmatch(r"self_attn\.(?:q_proj|k_proj|v_proj|o_proj|qkv_proj|q_norm|k_norm)\." + leaf, n):
        return "always_active"
    if re.fullmatch(r"linear_attn\.(?:(?:in_proj_qkvz|in_proj_ba|in_proj_qkv|in_proj_z|in_proj_b|in_proj_a|conv1d|norm|out_proj)\." + leaf + r"|dt_bias|A_log)", n):
        return "always_active"
    if re.fullmatch(r"mlp\.(?:switch_mlp|experts)(?:\.\d+)?\.(?:gate_proj|up_proj|down_proj|gate_up_proj)\." + leaf, n):
        return "routed_experts"
    if re.fullmatch(r"mlp\.(?:shared_expert|shared_experts)\.(?:gate_proj|up_proj|down_proj)\." + leaf, n):
        return "shared_experts"
    if re.fullmatch(r"mlp\.(?:gate_proj|up_proj|down_proj|gate|router|shared_expert_gate)\." + leaf, n):
        return "always_active"
    raise ValueError(f"unclassified tensor: {name}")


def headers(model_dir, revision=None):
    directory = Path(model_dir)
    cfg = config_at(directory)
    if cfg.get("model_type") not in FAMILIES:
        raise ValueError(f"unsupported architecture: {cfg.get('model_type')}")
    vocab = cfg.get("vocab_size")
    if type(vocab) is not int or vocab <= 0:
        raise ValueError("positive vocab_size required")
    tensors = read_headers(directory)
    cats = dict.fromkeys(("embed", "lm_head", "always_active", "routed_experts", "shared_experts", "not_loaded"), 0)
    for name, tensor in tensors.items():
        cat = classify(name)
        if cat == "embed" and (not tensor["shape"] or tensor["shape"][0] != vocab):
            raise ValueError(f"embedding rows disagree with vocab_size: {name}")
        tensor["category"] = cat
        cats[cat] += tensor["stored_bytes"]
    if not cats["embed"]:
        raise ValueError("embedding storage missing")
    experts = cfg.get("num_experts") or cfg.get("num_local_experts") or cfg.get("n_routed_experts")
    k = cfg.get("num_experts_per_tok") or cfg.get("experts_per_token") or cfg.get("num_experts_per_token")
    if cats["routed_experts"] and (type(experts) is not int or type(k) is not int or not 0 < k <= experts):
        raise ValueError("routed experts require valid k/E")
    tied = not cats["lm_head"]
    if "tie_word_embeddings" in cfg and bool(cfg["tie_word_embeddings"]) != tied:
        raise ValueError("tie_word_embeddings disagrees with stored output projection")
    fraction = k / experts if cats["routed_experts"] else 0
    w = (cats["always_active"] + cats["shared_experts"] + cats["embed"] / vocab
         + (cats["embed"] if tied else cats["lm_head"]) + cats["routed_experts"] * fraction)
    return {"schema_version": "joulewise.bytes_headers.v1", **identity(directory, cfg, revision),
            "model_type": cfg["model_type"], "num_experts": experts, "experts_per_tok": k,
            "routed_fraction": fraction, "shared_experts": {"stored_bytes": cats["shared_experts"],
                "intermediate_size": cfg.get("shared_expert_intermediate_size")},
            "tied_embeddings": tied, "categories": cats, "tensors": tensors,
            "W_bytes": w, "R_bytes": sum(cats.values()) - cats["not_loaded"]}


def arrays(state):
    if isinstance(state, dict):
        for item in state.values():
            yield from arrays(item)
    elif isinstance(state, (tuple, list)):
        for item in state:
            yield from arrays(item)
    elif hasattr(state, "nbytes") and hasattr(state, "shape"):
        yield state


def cache_snapshot(cache):
    layers = []
    for c in cache:
        state = list(arrays(c.state))
        keys, values = getattr(c, "keys", None), getattr(c, "values", None)
        backing = list(arrays([keys, values])) if keys is not None else state
        offset = getattr(c, "offset", None)
        if offset is not None:
            offset = int(offset)
        capacity = int(keys.shape[-2]) if keys is not None and len(keys.shape) >= 3 else None
        layers.append({"cache_class": type(c).__name__, "cache_bytes": sum(int(a.nbytes) for a in state),
                       "allocated_bytes": sum(int(a.nbytes) for a in backing),
                       "occupied_length": offset, "allocated_capacity": capacity,
                       "state_shapes": [list(a.shape) for a in state]})
    return {"cache_bytes": sum(x["cache_bytes"] for x in layers), "layers": layers}


def kv_record(start, end):
    if len(start["layers"]) != len(end["layers"]):
        raise ValueError("cache layer count changed")
    return {"after_prefill": start, "after_last_token": end,
            "KV_bytes": (start["cache_bytes"] + end["cache_bytes"]) / 2,
            "prompt_tokens": 2048, "output_tokens": 512, "decode_forward_passes": 512}


def generate_cache(model, prompt, mx, make_prompt_cache, output_tokens=512):
    """Match the pinned runtime's prefill and N decode forwards, look-ahead included.

    stream_generate(max_tokens=512) dispatches 512 decode forward passes, one
    of which yields no returned token. Addendum 5 requires that measured work:
    snapshots at 2,048 and 2,560 occupied positions, not 2,559.
    Greedy argmax never terminates early at an EOS id.
    """
    cache = make_prompt_cache(model)
    logits = model(prompt[None], cache=cache)
    token = mx.argmax(logits[:, -1, :], axis=-1)
    mx.eval(token, [a for c in cache for a in arrays(c.state)])
    start = cache_snapshot(cache)
    for _ in range(output_tokens):
        logits = model(token[:, None], cache=cache)
        token = mx.argmax(logits[:, -1, :], axis=-1)
        mx.eval(token, [a for c in cache for a in arrays(c.state)])
    return start, cache_snapshot(cache)


def kv(model_dir, revision=None):
    if platform.system() != "Darwin":
        raise RuntimeError("kv requires Mac MLX; headers and merge run anywhere")
    # Imports stay below the explicit Mac command gate; tests use fake caches.
    import mlx.core as mx
    from mlx_lm import load
    from mlx_lm.models.cache import make_prompt_cache
    sys.path.insert(0, str(ROOT))
    from joulewise.adapters.mlx_runtime import _synthetic_prompt_tokens
    directory = Path(model_dir)
    model, tokenizer = load(str(directory))
    mx.eval(model.parameters())
    prompt = mx.array(_synthetic_prompt_tokens(tokenizer, 2048))
    generate_cache(model, prompt, mx, make_prompt_cache, output_tokens=4)
    import time
    time.sleep(5.0)  # existing warmup settle, outside the request
    start, end = generate_cache(model, prompt, mx, make_prompt_cache)
    return {"schema_version": "joulewise.bytes_kv.v1", **identity(directory, config_at(directory), revision),
            **kv_record(start, end)}


def registered_config_key(model_name):
    """Public export identity, derived from the registered run configurations."""
    from joulewise.b6.blinding import configuration_key
    directories = set()
    for path in (ROOT / "configs/b6/packs").glob("*/registration.json"):
        registration = json.loads(path.read_bytes())
        if registration.get("blinding_group") == "bytes":
            directories.update(directory for module in registration.get("modules", [])
                               for directory in module.get("config_dirs", []))
    keys = set()
    for directory in sorted(directories):
        for path in (ROOT / directory).glob("*.json"):
            config = json.loads(path.read_bytes())
            if (config.get("model") or {}).get("name") == model_name:
                keys.add(configuration_key(config))
    if len(keys) != 1:
        raise ValueError("manifest requires one registered configuration identity per model")
    return keys.pop()


def merge(header_records, kv_records, pilot_rows):
    by_dir = {r["model_dir"]: r for r in kv_records}
    if len(by_dir) != len(kv_records):
        raise ValueError("duplicate KV model")
    rows, differences = [], []
    if len({h["model_dir"] for h in header_records}) != len(header_records):
        raise ValueError("duplicate header model")
    for h in header_records:
        k = by_dir.pop(h["model_dir"])
        for key in ("revision", "tokenizer", "config_sha256"):
            if h[key] != k[key]:
                raise ValueError(f"header/KV identity mismatch: {key}")
        if not h["revision"] or not h["tokenizer"]["tokenizer_json_sha256"]:
            raise ValueError("manifest requires revision and tokenizer pins")
        for value in (h["W_bytes"], h["R_bytes"], k["KV_bytes"]):
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError("nonfinite or negative byte count")
        b = h["W_bytes"] + k["KV_bytes"]
        row = {**h, "config_key": registered_config_key(
                   h.get("model_name", Path(h["model_dir"]).name)), "kv": k, "KV_bytes": k["KV_bytes"], "b_bytes": b,
               "W_GB": h["W_bytes"] / 1e9, "KV_GB": k["KV_bytes"] / 1e9,
               "b_GB": b / 1e9, "R_GB": h["R_bytes"] / 1e9}
        name = h.get("model_name", Path(h["model_dir"]).name).lower()
        pilot = next((p for p in pilot_rows if Path(p["repo"]).name.lower() == name
                      or (name == "qwen3-1.7b-4bit" and Path(p["repo"]).name == "qwen3-1.7b")), None)
        delta = {"model": name, "pilot_read_meas_GB": pilot["read_meas_GB"] if pilot else None,
                 "W_minus_pilot_bytes": h["W_bytes"] - pilot["read_meas_GB"] * 1e9 if pilot else None,
                 "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)"}
        row["pilot_difference"] = delta
        differences.append(delta)
        rows.append(row)
    if by_dir:
        raise ValueError("unmatched KV models")
    return {"schema_version": "joulewise.bytes_manifest.v1", "units": "bytes; GB = 1e9 bytes",
            "quantity": "format-derived bytes", "models": rows}, differences


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for command in ("headers", "kv"):
        sub = subs.add_parser(command)
        sub.add_argument("--model-dir", required=True, type=Path)
        sub.add_argument("--out", required=True, type=Path)
        sub.add_argument("--revision", help="explicit pinned revision for a local model directory")
    sub = subs.add_parser("merge")
    sub.add_argument("--headers", nargs="+", required=True, type=Path)
    sub.add_argument("--kv", nargs="+", required=True, type=Path)
    sub.add_argument("--pilot", type=Path, default=ROOT / "docs/design/bytes_pilot/summary_rows.json")
    sub.add_argument("--out", type=Path, default=ROOT / "configs/bytes/bytes_manifest.json")
    args = parser.parse_args(argv)
    if args.command == "merge":
        result, differences = merge([json.loads(p.read_bytes()) for p in args.headers],
                                    [json.loads(p.read_bytes()) for p in args.kv], json.loads(args.pilot.read_bytes()))
        for delta in differences:
            print(json.dumps(delta, sort_keys=True))
    else:
        result = (headers if args.command == "headers" else kv)(args.model_dir, args.revision)
    write_json(args.out, result)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        raise SystemExit(f"bytes manifest failed: {exc}") from exc
