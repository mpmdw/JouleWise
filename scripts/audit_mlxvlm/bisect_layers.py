"""Localize an mlx-vlm vs transformers divergence: per-layer and per-submodule
outputs on identical weights (one tiny real-layout checkpoint, fp32).

Usage: python bisect_layers.py CASE_DIR   (e.g. WORK/B_fp32)
"""
import json
import sys
from pathlib import Path

import numpy as np
import torch


def main(case):
    import mlx.core as mx
    from mlx_vlm.utils import load_model
    from transformers import Qwen4ExpForConditionalGeneration
    case = Path(case)
    ids = [int(t) for t in np.load(case / "ref.npz")["ids"]]
    ref = Qwen4ExpForConditionalGeneration.from_pretrained(case / "hf", dtype=torch.float32).eval()
    ref.config.text_config._attn_implementation = "eager"
    lm_ref = ref.model.language_model
    cap = {}

    def hook(name):
        def fn(_m, args, kwargs, out):
            cap[name] = (args[0] if args else next(iter(kwargs.values()))).detach().float().numpy(), (
                out[0] if isinstance(out, tuple) else out).detach().float().numpy()
        return fn

    for i, layer in enumerate(lm_ref.layers):
        layer.register_forward_hook(hook(f"L{i}"), with_kwargs=True)
        for sub in ("ple", "linear_attn", "self_attn", "mlp", "attn_hyper_connection", "mlp_hyper_connection"):
            if getattr(layer, sub, None) is not None:
                getattr(layer, sub).register_forward_hook(hook(f"L{i}.{sub}"), with_kwargs=True)
    with torch.inference_mode():
        ref(torch.tensor([ids]), use_cache=False)

    model = load_model(case / "vlm_hf_fused")
    lm = model.language_model
    inner = lm.model
    x = mx.array(np.array([ids], dtype=np.int32))
    h = mx.tile(inner.embed_tokens(x), (1, 1, lm.args.hc_count))
    pos = mx.arange(len(ids))[None]
    report = {}
    for i, layer in enumerate(inner.layers):
        h_in = h
        # Feed the REFERENCE layer input so each layer is judged in isolation.
        h_ref_in, h_ref_out = cap[f"L{i}"]
        h = mx.array(h_ref_in)
        if "ple" in layer:
            p = layer.ple(h, x, None, None)
            report[f"L{i}.ple"] = float(np.abs(np.array(p) - cap[f"L{i}.ple"][1]).max())
            h = h + p
        mixed, hyper, inj = layer.attn_hyper_connection(h)
        report[f"L{i}.attn_hc_mixed"] = float(np.abs(np.array(mixed) - cap[f"L{i}.attn_hyper_connection"][1]).max())
        if layer.is_linear:
            br = layer.linear_attn(mixed, mask=None, cache=None)
            name = "linear_attn"
            # Isolate: feed the reference input of linear_attn.
            br_iso = layer.linear_attn(mx.array(cap[f"L{i}.linear_attn"][0]), mask=None, cache=None)
        else:
            br = layer.self_attn(mixed, mask=None, cache=None, position_ids=pos)
            name = "self_attn"
            br_iso = layer.self_attn(mx.array(cap[f"L{i}.self_attn"][0]), mask=None, cache=None, position_ids=pos)
        report[f"L{i}.{name}_isolated"] = float(np.abs(np.array(br_iso) - cap[f"L{i}.{name}"][1]).max())
        h = hyper + (br[..., None, :] * inj[..., None]).reshape(hyper.shape)
        mixed, hyper, inj = layer.mlp_hyper_connection(h)
        mo = layer.mlp(mx.array(cap[f"L{i}.mlp"][0]))
        report[f"L{i}.mlp_isolated"] = float(np.abs(np.array(mo) - cap[f"L{i}.mlp"][1]).max())
        h = layer(mx.array(h_ref_in), x, mask=None, cache=None, position_ids=pos)
        report[f"L{i}.layer_isolated"] = float(np.abs(np.array(h) - h_ref_out).max())
    for k, v in report.items():
        print(f"{k:28s} {v:.3e}")


if __name__ == "__main__":
    main(sys.argv[1])
