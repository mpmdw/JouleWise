"""Optional per-unit maxfit exports using the separately supplied canonical converter.

These are unit fragments, not a loadable full-model artifact. Full PLE bytes are
exported separately after parity; a fixed-prompt sparse store is never labelled
as a converted full table.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import resource
import shutil
import sys
from pathlib import Path

from .core import digest, file_stamp, sha256, write_json
from .runner import execute
from .stream_ple import is_table


def load_converter(path):
    spec = importlib.util.spec_from_file_location("gold_stream_canonical_converter", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_unit(request, checkpoint):
    """Worker: canonical mapping, shape/chunk/writer helpers and precision policy.

    The canonical whole-model convert() requires all shards; this bounded
    inventory selects one unit and calls its same lower-level conversion code.
    """
    import numpy as np
    import mlx.core as mx
    converter = load_converter(request["canonical_converter"])
    rules = converter.load_rules(request["canonical_module"])
    import importlib.metadata
    for package, version in converter.PINS.items():
        if importlib.metadata.version(package) != version:
            raise ValueError(f"canonical conversion requires {package} {version}")
    mx.set_memory_limit(request["max_memory_bytes"] // 2)
    mx.set_cache_limit(32 * 1024**2)
    output = Path(request["convert_out"])
    output.mkdir(parents=True, exist_ok=True)
    inventory, constants = {}, []
    for original in request["unit_keys"]:
        key = rules.hf_to_mlx_key(original)
        if key is None or is_table(original):
            raise ValueError("unit inventory must contain only used non-table text tensors")
        path = checkpoint.path(checkpoint.weight_map[original])
        tensors, _ = converter.tensor_header(path)
        info = tensors[original]
        shape = tuple(info["shape"])
        if rules.is_ngram_buffer_key(key):
            constants.append({"name": original, "values": checkpoint.read(original, dtype="native").tolist()})
            continue
        expert = converter.EXPERT_RE.match(key)
        if expert:
            head, e, proj = expert["head"], int(expert["e"]), expert["proj"]
            name = f"{head}.mlp.switch_mlp.{'down_proj' if proj == 'down' else 'gate_up_proj'}.weight"
            ordinal = e if proj == "down" else 2*e + (proj == "up")
            inventory.setdefault(name, []).append((ordinal, path, original, shape, "expert"))
        else:
            if key.endswith(".mlp.experts.gate_up_proj"):
                key = key[:-len("experts.gate_up_proj")] + "switch_mlp.gate_up_proj.weight"
            elif key.endswith(".mlp.experts.down_proj"):
                key = key[:-len("experts.down_proj")] + "switch_mlp.down_proj.weight"
            kind = "conv" if key.endswith("conv1d.weight") and len(shape) == 3 and shape[-1] != 1 else "plain"
            inventory[key] = [(0, path, original, shape, kind)]
    progress_path = output / "dense-progress.json"
    identity = digest([request["unit_keys"], sha256(request["canonical_converter"]), sha256(request["canonical_module"]),
                       request["config_digest"], request["weight_map_digest"]])
    progress = json.loads(progress_path.read_text()) if progress_path.exists() else {"identity": identity, "files": {}}
    if progress["identity"] != identity:
        raise ValueError("conversion progress belongs to different sources/rules")
    if not progress_path.exists():
        if any(output.glob("tensor-*")):
            raise ValueError("unowned converted tensor files in output directory")
        write_json(progress_path, progress)
    files, weight_map, quantization = {}, {}, {}
    for number, (key, entries) in enumerate(sorted(inventory.items())):
        entries.sort(key=lambda e: e[0])
        if [e[0] for e in entries] != list(range(len(entries))):
            raise ValueError(f"missing expert pieces: {key}")
        shape = converter.target_shape(entries)
        quant = rules.quantization_for(key.removesuffix(".weight"), shape, "maxfit", 64)
        tensors = {key: (shape, "BF16")}
        base = key.removesuffix("weight")
        if quant:
            tensors = {key: ((*shape[:-1], shape[-1]*6//32), "U32"),
                       base+"scales": ((*shape[:-1], shape[-1]//64), "BF16"),
                       base+"biases": ((*shape[:-1], shape[-1]//64), "BF16")}
            quantization[key.removesuffix(".weight")] = quant
        filename = f"tensor-{number:04d}.safetensors"
        if filename in progress["files"]:
            if sha256(output / filename) != progress["files"][filename]:
                raise ValueError("committed converted tensor changed")
            files[filename] = progress["files"][filename]
            weight_map.update(dict.fromkeys(tensors, filename))
            continue
        size = sum(converter.tensor_bytes(*value) for value in tensors.values()) + 65536
        temp = output / (filename + ".tmp")
        temp.unlink(missing_ok=True)
        (output / filename).unlink(missing_ok=True)  # not in committed progress
        if shutil.disk_usage(output).free - size < request["min_free_gb"]*1024**3:
            raise RuntimeError("free-disk guard: converted tensor would breach reserve")
        writer = converter.TensorFile(temp, tensors)
        for chunk in converter.tensor_chunks(entries, raw_bf16=not quant):
            if quant:
                arr = mx.array(chunk).astype(mx.bfloat16).reshape(-1, chunk.shape[-1])
                packed, scales, biases = mx.quantize(arr, group_size=64, bits=6)
                mx.eval(packed, scales, biases)
                writer.write(key, np.array(packed).astype("<u4").tobytes())
                writer.write(base+"scales", np.array(scales.view(mx.uint16)).astype("<u2").tobytes())
                writer.write(base+"biases", np.array(biases.view(mx.uint16)).astype("<u2").tobytes())
                del arr, packed, scales, biases
            else:
                raw = chunk if chunk.dtype == np.dtype("<u2") else rules._f32_to_bf16_bits(chunk)
                writer.write(key, raw.tobytes())
        writer.close()
        temp.replace(output / filename)
        files[filename] = sha256(output / filename)
        progress["files"][filename] = files[filename]
        write_json(progress_path, progress)
        weight_map.update(dict.fromkeys(tensors, filename))
        mx.clear_cache()
    write_json(output / "model.safetensors.index.json", {"weight_map": weight_map})
    write_json(output / "unit.json", {"unit": request["unit"], "quantization": quantization,
                                      "hash_buffers": constants, "profile": "maxfit", "group_size": 64,
                                      "scope": "unit fragment; assemble and validate before full-model loading"})
    for name in ("model.safetensors.index.json", "unit.json"):
        files[name] = sha256(output / name)
    for filename in {checkpoint.weight_map[k] for k in request["unit_keys"]}:
        checkpoint.path(filename)
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {"files": files, "module_sha256": sha256(request["canonical_module"]),
            "converter_sha256": sha256(request["canonical_converter"]), "profile": "maxfit",
            "metadata": {"adapter_kind": "mlx", "peak_mlx_bytes": mx.get_peak_memory(),
                         "peak_rss_bytes": peak if sys.platform == "darwin" else peak*1024}}


def range_sha256(path, start, length):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        f.seek(start)
        while length:
            value = f.read(min(length, 4*1024**2))
            if not value:
                raise ValueError("short converted PLE file")
            h.update(value)
            length -= len(value)
    return h.hexdigest()


def convert_unit(driver, unit):
    args = driver.args
    output = Path(args.convert_out).resolve() / (f"layer-{int(unit):03d}" if unit.isdigit() else unit)
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / "conversion.json"
    if not state_path.exists() and any(output.iterdir()):
        raise ValueError("conversion unit directory is nonempty and has no owner manifest")
    state = json.loads(state_path.read_text()) if state_path.exists() else {
        "stream_fingerprint": driver.state["fingerprint"], "ple_parts": {}}
    if state["stream_fingerprint"] != driver.state["fingerprint"]:
        raise ValueError("converted unit belongs to another invocation")
    write_json(state_path, state)
    if "dense" not in state:
        active = driver.harness.checkpoint
        request = {"backend": "convert_unit", "checkpoint": str(active.root), "unit": unit,
                   "hf_home": str(driver.staging / "hf"),
                   "unit_keys": driver.plan["keys"][unit],
                   "shard_guards": {p.name: file_stamp(p)
                                    for p in active.root.glob("*.safetensors")},
                   "config_digest": digest(driver.checkpoint.config),
                   "weight_map_digest": digest(driver.checkpoint.weight_map),
                   "canonical_converter": args.canonical_converter, "canonical_module": args.canonical_module,
                   "min_free_gb": args.min_free_gb, "convert_out": str(output)}
        result = execute(args.mlx_python, request, driver.work / "convert-workers" / unit, args.max_gb, args.timeout)
        if "error" in result:
            raise RuntimeError(f"conversion failed: {result}")
        state["dense"] = result
        write_json(state_path, state)
    for name, checksum in state["dense"]["files"].items():
        if sha256(output / name) != checksum:
            raise ValueError("converted unit changed")
    # Full table export requires its real output capacity. Never fill missing
    # rows with zeros or label the parity sparse store a full converted table.
    from .stream_ple import header
    for base, plan in driver.state["ple"].get("plans", {}).items():
        if not base.startswith(driver.checkpoint.prefix + f"layers.{unit}."):
            continue
        filename = f"ngram-L{int(unit):03d}.bf16.bin"
        table = output / filename
        committed = 0
        for tensor in plan["parts"]:
            entry = state["ple_parts"].get(tensor)
            if entry:
                if range_sha256(table, committed, entry["bytes"]) != entry["sha256"]:
                    raise ValueError("converted PLE span changed")
                committed += entry["bytes"]
        with table.open("r+b" if table.exists() else "w+b") as f:
            f.truncate(committed)  # discard only uncommitted generated bytes
        for tensor in plan["parts"]:
            if tensor in state["ple_parts"]:
                continue
            shard = driver.checkpoint.weight_map[tensor]
            path = driver.stage(shard)
            tensors, start = header(path)
            info = tensors[tensor]
            if info["dtype"] != "BF16":
                raise ValueError("full PLE export expects official bf16 storage")
            lo, hi = info["data_offsets"]
            size = hi - lo
            if shutil.disk_usage(output).free - size < args.min_free_gb*1024**3:
                raise RuntimeError("free-disk guard: full PLE export needs more output capacity")
            h = hashlib.sha256()
            with path.open("rb") as source, table.open("ab") as target:
                source.seek(start + lo)
                left = size
                while left:
                    value = source.read(min(left, 4*1024**2))
                    if not value:
                        raise ValueError("short PLE source")
                    target.write(value)
                    h.update(value)
                    left -= len(value)
                target.flush()
                os.fsync(target.fileno())
            state["ple_parts"][tensor] = {"bytes": size, "sha256": h.hexdigest(), "source_sha256": driver.metadata[shard]["sha256"]}
            write_json(state_path, state)
            remaining = any(t not in state["ple_parts"] and driver.checkpoint.weight_map[t] == shard for t in plan["parts"])
            if not remaining:
                if args.shared_shards == "restage":
                    driver.delete(shard)
                else:
                    driver.release()
        state.setdefault("tables", {})[filename] = {"sha256": sha256(table), "shape": plan["shape"], "format": "bf16"}
    state["done"] = True
    write_json(state_path, state)
    write_json(output / "manifest.json", {"schema": "qwen4-gold-unit-maxfit/v1", "unit": unit,
               "files": {**state["dense"]["files"], **{k: v["sha256"] for k, v in state.get("tables", {}).items()}},
               "source": driver.source_info, "canonical_module_sha256": sha256(args.canonical_module),
               "canonical_converter_sha256": sha256(args.canonical_converter),
               "stream_fingerprint": driver.state["fingerprint"], "complete_model": False})
    return {"manifest": str(output / "manifest.json"), "sha256": sha256(output / "manifest.json")}
