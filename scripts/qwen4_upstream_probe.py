#!/usr/bin/env python3
"""Isolate qwen4_exp config, router and BF16 arithmetic using tiny fixture A."""
import argparse
import json
from pathlib import Path

import mlx.core as mx
import numpy as np

from qwen4_upstream_parity import load_python, metrics, upstream_module


def probe(fixture, module):
    config = json.loads((fixture / "config.json").read_text())
    config["text_config"]["layer_types"][-1] = "indexed_attention"
    try:
        module.Model(module.ModelArgs.from_dict(config))
    except ValueError as exc:
        indexed_attention = {"loaded": False, "error": str(exc)}
    else:
        indexed_attention = {"loaded": True}
    config["text_config"]["layer_types"][-1] = "full_attention"
    config["text_config"]["norm_topk_prob"] = False
    model = module.Model(module.ModelArgs.from_dict(config))
    weights = mx.load(str(fixture / "hf.safetensors"))
    model.load_weights(list(model.sanitize(weights).items()), strict=True)
    model.eval()
    moe = model.model.layers[0].mlp
    rng = np.random.default_rng(1105)
    x = mx.array(rng.normal(size=(1, 3, 64)).astype(np.float32))
    scores = mx.softmax(moe.gate(x), axis=-1)
    idx = mx.argsort(-scores, axis=-1)[..., :moe.top_k]
    selected = mx.take_along_axis(scores, idx, axis=-1)
    experts = moe.switch_mlp(x, idx)
    shared = mx.sigmoid(moe.shared_expert_gate(x)) * moe.shared_expert(x)
    expected = (experts * selected[..., None]).sum(axis=-2) + shared
    observed = moe(x)
    mx.eval(selected, expected, observed)
    return {"indexed_attention": indexed_attention,
            "norm_topk_prob_false": {
                "selected_probability_sums": selected.sum(axis=-1).tolist(),
                **metrics(np.array(observed), np.array(expected), 1e-4),
            }}


def probe_bf16(fixture, module):
    from mlx_lm.models.gated_delta import compute_g

    config = json.loads((fixture / "config.json").read_text())
    model = module.Model(module.ModelArgs.from_dict(config))
    weights = mx.load(str(fixture / "hf.safetensors"))
    model.load_weights(list(model.sanitize(weights).items()), strict=True)
    text = config["text_config"]
    width = text["hidden_size"]
    x = model.model.embed_tokens(mx.array([config["ids"]]))
    h = mx.tile(x, (1, 1, text["hc_count"]))
    rms = model.layers[0].attn_hyper_connection.hc_norm
    key = "model.language_model.layers.0.attn_hyper_connection.hc_norm.weight"
    raw_scale = weights[key].astype(mx.float32) + 1
    ref_norm = mx.fast.rms_norm(h.astype(mx.float32).reshape(1, -1, width), None, rms.eps)
    ref_norm = (ref_norm.reshape(h.shape) * raw_scale).astype(mx.bfloat16)

    a = mx.array([0.127, 0.111, 0.334], dtype=mx.bfloat16)
    dt = mx.array([0.923, 0.297, 0.915], dtype=mx.bfloat16)
    log_a = mx.array([1.0, 1.5, 0.75], dtype=mx.bfloat16)
    # Transformers forms a + dt_bias and softplus in FP32 before exponentiating.
    ref_g = mx.exp(-mx.exp(log_a.astype(mx.float32))
                   * mx.logaddexp(mx.array(0.0), a.astype(mx.float32) + dt))
    return {
        "folded_scale": metrics(np.array(rms.weight.astype(mx.float32)), np.array(raw_scale), 0.0),
        "grouped_rms": metrics(np.array(rms(h).astype(mx.float32)),
                               np.array(ref_norm.astype(mx.float32)), 0.0),
        "delta_decay_factor": metrics(np.array(compute_g(log_a, a, dt)), np.array(ref_g), 0.0),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--candidate", type=Path, help="locally patched upstream source")
    parser.add_argument("--bf16", action="store_true", help="check BF16 RMSNorm and decay rounding")
    args = parser.parse_args()
    module = (load_python(args.candidate, "mlx_lm.models.qwen4_exp_candidate")
              if args.candidate else upstream_module())
    check = probe_bf16 if args.bf16 else probe
    print(json.dumps(check(args.fixture, module), indent=2))
