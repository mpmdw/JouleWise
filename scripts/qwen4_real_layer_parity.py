#!/usr/bin/env python3
"""Compare a single converted Flash-Next layer in two MLX implementations."""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import resource
import struct
from unittest.mock import patch

import numpy as np

from qwen4_upstream_parity import metrics, port_module, upstream_module, write_json

MANIFEST_SHA = "6b481f145fcd3ab0242251be30ca460cc67e484652de11553332605833a1c3f9"
LAYER_BYTE_LIMIT = 3 * 2**30


def tensor_headers(file):
    with file.open("rb") as stream:
        size, = struct.unpack("<Q", stream.read(8))
        if size > 2**20:
            raise ValueError(f"unexpected safetensors header size in {file.name}")
        return json.loads(stream.read(size)), size + 8


def layer_weights(root, index):
    import mlx.core as mx

    mapping = json.loads((root / "model.safetensors.index.json").read_text())["weight_map"]
    prefix = f"language_model.model.layers.{index}."
    files, slices, total = {}, {}, 0
    for key, shard in mapping.items():
        if not key.startswith(prefix):
            continue
        path = root / shard
        if path not in files:
            files[path] = tensor_headers(path)
        header, base = files[path]
        info = header[key]
        begin, end = info["data_offsets"]
        itemsize = {"BF16": 2, "F32": 4, "U32": 4}[info["dtype"]]
        if not (0 <= begin < end <= path.stat().st_size - base
                and end - begin == math.prod(info["shape"]) * itemsize):
            raise ValueError(f"invalid tensor offsets for {key}")
        total += end - begin
        slices[key.removeprefix(prefix)] = (path, base + begin, info)
    if not 0 < total <= LAYER_BYTE_LIMIT:
        raise ValueError(f"selected layer byte count {total} is outside the read budget")
    weights = {}
    for key, (path, offset, info) in slices.items():
        dtype = {"BF16": "<u2", "F32": "<f4", "U32": "<u4"}[info["dtype"]]
        raw = np.memmap(path, mode="r", offset=offset, shape=tuple(info["shape"]), dtype=dtype)
        value = mx.array(raw)
        weights[key] = value.view(mx.bfloat16) if info["dtype"] == "BF16" else value
    mx.eval(weights)
    return weights, total


def upstream_weights(weights, upstream):
    import mlx.core as mx

    result = {}
    for key, value in weights.items():
        if ".switch_mlp.gate_up_proj." in key:
            gate, up = mx.split(value, 2, axis=-2)
            result[key.replace("gate_up_proj", "gate_proj")] = gate
            result[key.replace("gate_up_proj", "up_proj")] = up
        elif key.endswith(upstream._FOLD_ONE):
            result[key] = 1.0 + value
        else:
            result[key] = value
    for connection in ("attn_hyper_connection", "mlp_hyper_connection"):
        upstream._merge_linears(result, [connection + ".input_mix_weight_down",
                                        connection + ".block_inject_weight"],
                                target=connection + ".input_mix_weight_down")
    return result


def run(root, checkout, index, length, output):
    import mlx.core as mx
    import mlx.nn as nn

    upstream = upstream_module()

    if sha256((root / "manifest.json").read_bytes()).hexdigest() != MANIFEST_SHA:
        raise ValueError("unexpected converted artifact manifest")
    if not 1 <= length <= 2060:
        raise ValueError("sequence length must be 1 to 2060")
    mx.set_cache_limit(256 * 2**20)
    config = json.loads((root / "config.json").read_text())
    text = config["text_config"]
    canonical = port_module(checkout)
    a = upstream.TextArgs.from_dict(text)
    b = canonical.TextModelArgs.from_dict(text)
    if not 0 <= index < b.num_hidden_layers:
        raise ValueError("layer index is outside the checkpoint")
    for part in ("gate_up_proj", "down_proj"):
        key = f"language_model.model.layers.{index}.mlp.switch_mlp.{part}"
        if config["quantization"][key] != {"bits": 6, "group_size": 64, "mode": "affine"}:
            raise ValueError(f"unexpected quantization layout for {key}")
    layer_b = canonical.DecoderLayer(b, index)
    tables = config["ngram_tables"]["layers"]
    table = None
    if layer_b.has_ple:
        meta = tables[str(index)]
        table = canonical.NgramTable(root / meta["file"], meta["rows"], meta["dim"],
                                    meta["format"], meta["group_size"], io="pread")

    class PagedHead(nn.Module):
        """Map one upstream head's local rows to the same artifact row file."""

        def __init__(self, rows, dim):
            super().__init__()
            self.start = sum(head_sizes)
            head_sizes.append(rows)
            if dim != table.dim or self.start + rows > table.rows:
                raise ValueError("unexpected n-gram head shape")

        def __call__(self, ids):
            return mx.array(table.gather(np.array(ids) + self.start)).astype(mx.bfloat16)

    head_sizes = []
    try:
        if table is None:
            layer_a = upstream.DecoderLayer(a, layer_idx=index)
        else:
            with patch.object(upstream.nn, "Embedding", PagedHead):
                layer_a = upstream.DecoderLayer(a, layer_idx=index)
        weights, byte_count = layer_weights(root, index)
        for layer, layout in ((layer_a, upstream_weights(weights, upstream)), (layer_b, weights)):
            nn.quantize(layer, group_size=64, bits=6,
                        class_predicate=lambda path, _: f"{path}.scales" in layout)
            layer.load_weights(list(layout.items()), strict=True)
            layer.eval()
            mx.eval(layer.parameters())
        del weights, layout

        rng = np.random.default_rng(20261121 + index)
        ids = rng.integers(3, b.vocab_size, size=(1, length), dtype=np.int32)
        ids[0, length // 2] = b.eos_id
        h = mx.array(rng.normal(0, 0.25, size=(1, length, b.hidden_size * b.hc_count))
                     .astype(np.float32)).astype(mx.bfloat16)
        x = mx.array(rng.normal(0, 0.25, size=(1, length, b.hidden_size))
                     .astype(np.float32)).astype(mx.bfloat16)
        ctx = canonical._Context(1, length, 0, np.zeros(1, np.int64),
                                 canonical.rope_inv_freq(b), None, 4096, 4096)
        cache = canonical.make_layer_caches(b)[index]
        device_ids = mx.array(ids)
        pairs = {}
        sparse_queries = None
        if table is not None:
            spec = canonical.NgramHashSpec(b, b.ple_layer_ids.index(index + 1))
            history = np.concatenate([np.full((1, spec.context_len), spec.eos), ids], axis=1)
            rows = spec.ngram_ids(history, length)
            emb_b = mx.array(table.gather(rows).reshape(1, length, -1)).astype(mx.bfloat16)
            ctx.ngram_emb[index] = emb_b
            pairs["ngram"] = (layer_a.ple.ple_embedding(device_ids), emb_b)
            pairs["ple"] = (layer_a.ple(h, device_ids), layer_b.ple(h, emb_b, ctx, cache))
            cache = canonical.make_layer_caches(b)[index]
        pairs["attn_hc"] = (layer_a.attn_hyper_connection(h)[0], layer_b.attn_hyper_connection(h)[0])
        up_moe, port_moe = layer_a.mlp, layer_b.mlp
        pairs["moe"] = (up_moe(x), port_moe(x))
        pairs["shared"] = (up_moe.shared_expert(x), port_moe.shared_expert(x))
        up_logits = up_moe.gate(x.astype(mx.float32))
        port_logits, port_indices, _ = port_moe.route(x)
        top_k = up_moe.top_k
        up_indices = mx.argpartition(-up_logits, top_k - 1, axis=-1)[..., :top_k]
        pairs["router"] = (mx.sort(up_indices, axis=-1), mx.sort(port_indices, axis=-1))
        pairs["experts_same_indices"] = (up_moe.switch_mlp(x, port_indices),
                                         port_moe.switch_mlp(x, port_indices))
        ordered_logits = mx.sort(port_logits, axis=-1)
        ties = (ordered_logits[..., -top_k] == ordered_logits[..., -top_k - 1])
        changed = mx.any(pairs["router"][0] != pairs["router"][1], axis=-1)
        router_counts = {"changed_rows": int(changed.sum().item()),
                         "bf16_cutoff_ties": int(ties.sum().item()),
                         "changed_on_tied_rows": int((changed & ties).sum().item())}
        if layer_b.is_linear:
            pairs["delta"] = (layer_a.linear_attn(x), layer_b.linear_attn(x, ctx,
                                       canonical.make_layer_caches(b)[index]))
        else:
            qsa_a = layer_a.self_attn(x, "causal")
            idx_cache = canonical.make_layer_caches(b)[index]
            if length >= b.indexer_budget + b.indexer_compress_ratio:
                # Observe the mask consumed by the full attention call.
                captures = []
                original = canonical.QSAIndexer.__call__

                def record_indexer(indexer, *args):
                    selection = original(indexer, *args)
                    captures.append(selection.mask)
                    return selection

                with patch.object(canonical.QSAIndexer, "__call__", record_indexer):
                    qsa_b = layer_b.self_attn(x, ctx, idx_cache)
                pairs["indexer"] = (layer_a.self_attn.indexer(x), captures[0])
                visible = mx.arange(1, length + 1)
                sparse_queries = [int((mask.sum(axis=-1) < visible).sum().item())
                                  for mask in pairs["indexer"]]
                if min(sparse_queries) < 1:
                    raise ValueError("sparse control did not prune visible tokens")
            else:
                qsa_b = layer_b.self_attn(x, ctx, idx_cache)
            pairs["qsa"] = (qsa_a, qsa_b)
        pairs["hidden"] = (layer_a(h, mask="causal", conv_mask=None, cache=None, ids=device_ids),
                           layer_b(h, ctx, cache))

        result = {}
        for name, (lhs, rhs) in pairs.items():
            lhs, rhs = lhs.astype(mx.float32), rhs.astype(mx.float32)
            mx.eval(lhs, rhs)
            lhs, rhs = np.asarray(lhs), np.asarray(rhs)
            # Agreement screen, relative to the isolated canonical output range.
            atol = 0.0 if name in ("ngram", "indexer", "router") else max(1e-4, .02 * np.max(np.abs(rhs)).item())
            result[name] = metrics(lhs, rhs, atol)
        write_json(output, {"purpose": "MLX-vs-MLX on converted weights", "manifest": MANIFEST_SHA,
                           "layer": index, "tokens": length, "tensor_bytes": byte_count,
                           "ple_heads": len(head_sizes), "seed": 20261121 + index,
                           "router": router_counts, "sparse_queries": sparse_queries, "metrics": result,
                           "max_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                           "mlx_peak_bytes": mx.get_peak_memory()})
    finally:
        if table is not None:
            table.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("port", type=Path)
    parser.add_argument("layer", type=int)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tokens", type=int, default=16)
    args = parser.parse_args()
    run(args.artifact, args.port, args.layer, args.tokens, args.output)
