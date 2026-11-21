"""mlx-vlm's own quantization path on config C (all Linear in-dims multiples
of 64), bf16 source: which modules get quantized (indexer, router,
shared-expert gate, hyper-connections, PLE...), and logits error vs the
unquantized mlx-vlm bf16 model and the fp32 reference.

Uses mlx_vlm.convert.convert(quantize=True) if it can run without a
tokenizer; otherwise the identical quantize_model() call with convert's
predicate (skip_multimodal_module + model.quant_predicate).

Usage: python t_quant.py WORKDIR [bits] [group]
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np


def main(work, bits=4, group=64):
    import mlx.core as mx
    import mlx.nn as nn
    from mlx.utils import tree_flatten
    from mlx_vlm.utils import load_model
    work = Path(work)
    case = work / "C_bf16"
    out = work / f"C_bf16_vlm_q{bits}g{group}"
    shutil.rmtree(out, ignore_errors=True)
    how = "mlx_vlm.convert.convert"
    try:
        from mlx_vlm.convert import convert
        convert(str(case / "vlm_hf_fused"), str(out), quantize=True, q_bits=bits, q_group_size=group)
        qmodel = load_model(out)
    except Exception as e:  # noqa: BLE001
        how = f"quantize_model fallback (convert failed: {type(e).__name__}: {str(e)[:120]})"
        from mlx_vlm.quant_utils import quantize_model
        from mlx_vlm.utils import skip_multimodal_module, load_config
        qmodel = load_model(case / "vlm_hf_fused")
        pred = qmodel.quant_predicate

        def base(path, module):
            if skip_multimodal_module(path):
                return False
            return pred(path, module)
        qmodel, _ = quantize_model(qmodel, load_config(case / "vlm_hf_fused"), group, bits, quant_predicate=base)
    lm = qmodel.language_model
    quantized, float_linear = {}, []
    for name, m in lm.named_modules():
        if hasattr(m, "bits") and hasattr(m, "group_size"):
            quantized[name] = f"{type(m).__name__} {m.bits}b g{m.group_size}"
        elif isinstance(m, (nn.Linear, nn.Embedding)):
            float_linear.append(name)

    def pick(sub):
        return {k: v for k, v in quantized.items() if sub in k and "layers.3" in k or (sub in k and "layers.1.ple" in k)}
    ref = np.load(case / "ref.npz")
    ref32 = np.load(work / "C_fp32" / "ref.npz")["prefill"]
    vlm16 = np.load(case / "vlm.npz")["prefill"]
    ids = mx.array(ref["ids"].astype(np.int32)[None])
    lm._position_ids = lm._rope_deltas = None
    q = np.array(lm(ids, cache=lm.make_cache()).logits.astype(mx.float32))
    c = lm.make_cache()
    steps = []
    for i in range(ids.shape[1]):
        steps.append(np.array(lm(ids[:, i:i + 1], cache=c).logits.astype(mx.float32)))
    steps = np.concatenate(steps, 1)

    def m(a, b):
        return dict(max_abs=float(np.abs(a - b).max()), p50_pos=float(np.median(np.abs(a - b).max(-1))),
                    top1=float((a.argmax(-1) == b.argmax(-1)).mean()))
    rep = dict(path=how, bits=bits, group=group,
               n_quantized=len(quantized), float_linear_or_embedding_left=float_linear,
               indexer=[f"{k}: {v}" for k, v in quantized.items() if "indexer" in k],
               router=[f"{k}: {v}" for k, v in quantized.items() if k.endswith("mlp.gate")],
               shared_expert_gate=[f"{k}: {v}" for k, v in quantized.items() if k.endswith("shared_expert_gate")],
               hyper_connections=sorted({v for k, v in quantized.items() if "hyper_connection" in k}),
               experts=sorted({v for k, v in quantized.items() if "switch_mlp" in k}),
               deltanet=sorted({v for k, v in quantized.items() if "linear_attn" in k}),
               ple=[f"{k}: {v}" for k, v in quantized.items() if ".ple." in k],
               embed_and_head=[f"{k}: {v}" for k, v in quantized.items() if "embed_tokens" in k or "lm_head" in k],
               prefill_vs_vlm_bf16=m(q, vlm16), prefill_vs_ref_fp32=m(q, ref32),
               vlm_bf16_vs_ref_fp32=m(vlm16, ref32), stepwise_vs_quant_prefill=m(steps, q))
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], int(a[1]) if len(a) > 1 else 4, int(a[2]) if len(a) > 2 else 64)
