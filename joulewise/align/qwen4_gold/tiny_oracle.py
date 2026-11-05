"""Independent end-to-end check of streamed reference vs the tiny full HF model.

This module deliberately permits from_pretrained ONLY for the bounded tiny
fixture. It is never used to load official weights or produce MLX parity.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import IndexedCheckpoint, REFERENCE_VERSION, compare_arrays, write_json
from .runner import DEFAULT_PROMPTS


def verify(checkpoint_root, report_root, prompts, dtypes):
    import numpy as np
    import torch
    import transformers
    from transformers.models.qwen4_exp.modeling_qwen4_exp import Qwen4ExpForCausalLM
    if transformers.__version__ != REFERENCE_VERSION:
        raise ValueError("wrong reference version")
    checkpoint = IndexedCheckpoint(checkpoint_root)
    c = checkpoint.text
    # Before any full model allocation, prove this is a small synthetic fixture.
    if (c["hidden_size"] > 64 or c["num_hidden_layers"] > 4 or c["num_experts"] > 8 or
            c.get("ngram_vocab_size_base", 20_000_000) > 128 or c["vocab_size"] > 256):
        raise ValueError("full-model oracle is restricted to tiny fixtures")
    total_bytes = sum(checkpoint.path(f).stat().st_size for f in set(checkpoint.weight_map.values()))
    if total_bytes > 16 * 1024**2:
        raise ValueError("tiny checkpoint exceeds 16 MiB")
    torch.set_num_threads(2)
    results = []
    for dtype_name in dtypes:
        dtype = torch.float32 if dtype_name == "fp32" else torch.bfloat16
        model = Qwen4ExpForCausalLM.from_pretrained(checkpoint_root, dtype=dtype, attn_implementation="eager", local_files_only=True).eval()
        captures = {}
        def hook(name):
            def record(m, a, o):
                captures[name] = o.detach().float().numpy().copy()
            return record
        handles = [layer.register_forward_hook(hook(str(i))) for i, layer in enumerate(model.model.layers)]
        handles.append(model.model.hyper_connection_mixer.register_forward_hook(hook("final")))
        handles.append(model.lm_head.register_forward_hook(hook("head")))
        for prompt in prompts:
            captures.clear()
            with torch.inference_mode():
                model(input_ids=torch.tensor([prompt["input_ids"]]), use_cache=False)
            for unit, full in captures.items():
                name = f"layer-{int(unit):03d}" if unit.isdigit() else unit
                path = Path(report_root) / name / f"{prompt['name']}-{dtype_name}-real" / "reference/output.npy"
                streamed = np.load(path, allow_pickle=False)
                metric = compare_arrays(full, streamed, dtype_name)
                results.append({"prompt": prompt["name"], "dtype": dtype_name, "unit": unit,
                                "bitwise_equal": bool(np.array_equal(full, streamed)), **metric})
        for handle in handles:
            handle.remove()
        del model
    result = {"purpose": "streamed reference self-test; no MLX parity claim",
              "status": "PASS" if all(r["pass"] for r in results) else "FAIL", "cases": results}
    write_json(Path(report_root) / "tiny-oracle.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--prompts-json")
    parser.add_argument("--dtypes", default="fp32,bf16")
    args = parser.parse_args()
    prompts = json.loads(Path(args.prompts_json).read_text()) if args.prompts_json else DEFAULT_PROMPTS
    result = verify(args.checkpoint, args.output, prompts, args.dtypes.split(","))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
