#!/usr/bin/env python3
"""Resident-memory model for the MLX Qwen3.8-Flash-Next twin.

Run with the pinned MLX venv (the port is instantiated with lazy arrays to
enumerate exact parameter shapes; nothing is allocated)::

    /path/to/venv-mlx/bin/python scripts/align_qwen4_exp_twin_memory.py \
        [--config .engine/hf-flashnext/config.json] [--context 40960] [--json out.json]

    # validate the byte formulas against a real converter output
    /path/to/venv-mlx/bin/python scripts/align_qwen4_exp_twin_memory.py \
        --check-manifest /path/to/converted_dir

Reports, per component, weight bytes at bf16, uniform 8/6/4/3-bit and the
mixed recipes; KV/QSA-indexer and DeltaNet/PLE state at ``--context``; an
estimate of prefill transients; and the off-GPU n-gram table (disk and
page-cache bounds, never MLX-resident). Affine quantization bytes:
``n*bits/8 + (n/group)*2*2`` (bf16 scale and bias per group).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / ".engine" / "hf-flashnext" / "config.json"
GB, GIB = 1e9, 2 ** 30
PAGE_BYTES = 16384  # Apple Silicon VM page


def _converter_module():
    spec = importlib.util.spec_from_file_location(
        "align_convert_qwen4_exp_twin", REPO_ROOT / "scripts" / "align_convert_qwen4_exp_twin.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def quant_bytes(n: int, bits: int, group: int, scale_bytes: int = 2) -> int:
    return n * bits // 8 + (n // group) * 2 * scale_bytes


def enumerate_params(cfg: dict):
    sys.path.insert(0, str(REPO_ROOT))
    from mlx.utils import tree_flatten
    from joulewise.align.models import qwen4_exp_twin as tw

    model = tw.Model(tw.ModelArgs.from_dict(cfg))  # lazy: shapes only
    out = []
    for key, arr in tree_flatten(model.parameters()):
        out.append((key, tuple(arr.shape), int(math.prod(arr.shape))))
    return tw, model, out


def weight_bytes(tw, params, category, expert_bits, dense_bits, group, float_bytes=2):
    """Bytes per category under the converter's policy (``tw.quant_policy``)."""
    per = {}
    for key, shape, n in params:
        cat = category(key)
        bits = None
        quantizable = key.endswith(".weight") and (len(shape) == 2 or ".switch_mlp." in key)
        if quantizable:
            bits = tw.quant_policy(key[: -len(".weight")], shape, expert_bits, dense_bits, group)
        b = quant_bytes(n, bits, group, float_bytes) if bits else n * float_bytes
        per[cat] = per.get(cat, 0) + b
    return per


def uniform_bytes(params, category, bits, group):
    """Every Linear/Embedding/expert weight at ``bits`` (mlx_lm.convert -q style)."""
    per = {}
    for key, shape, n in params:
        quantizable = key.endswith(".weight") and (len(shape) == 2 or ".switch_mlp." in key)
        b = quant_bytes(n, bits, group) if (bits and quantizable and shape[-1] % group == 0) else 2 * n
        per[category(key)] = per.get(category(key), 0) + b
    return per


def runtime_state(args, context: int, batch: int = 1):
    n_attn = args.layer_types.count("indexed_attention")
    n_lin = args.layer_types.count("linear_attention")
    L = int(math.ceil(context / 256) * 256)                     # KVCache step growth
    nb = int(math.ceil((context // args.indexer_compress_ratio) / 64) * 64)
    conv_dim = 2 * args.linear_num_key_heads * args.linear_key_head_dim \
        + args.linear_num_value_heads * args.linear_value_head_dim
    hc_width = args.hc_count * args.hidden_size
    ple_hist = (args.ple_conv_kernel_size - 1) * args.ngram_size
    return {
        "kv_cache": n_attn * 2 * batch * args.num_key_value_heads * L * args.head_dim * 2,
        "qsa_indexer_raw_keys": n_attn * batch * L * args.indexer_head_dim * 2,
        "qsa_block_keys": n_attn * batch * nb * args.indexer_head_dim * 2,
        "deltanet_recurrent_fp32": n_lin * batch * args.linear_num_value_heads
        * args.linear_value_head_dim * args.linear_key_head_dim * 4,
        "deltanet_conv": n_lin * batch * (args.linear_conv_kernel_dim - 1) * conv_dim * 2,
        "ple_conv_and_context": len(args.ple_layer_ids) * batch * (ple_hist * hc_width * 2 + 8),
    }


def transient_estimate(args, context: int, prefill: int, query_chunk: int):
    """Peak per-layer temporaries during a prefill chunk (estimate, bf16)."""
    L, P, Q = context, prefill, min(query_chunk, prefill)
    nb = context // args.indexer_compress_ratio
    sdpa_fallback = 1.05 * args.num_attention_heads * Q * L * 2      # measured factor 1.03-1.05
    qsa = P * nb * 4 * 3 + P * L * 5                                  # fp32 scores x3, 5 bool masks
    hidden = P * args.hc_count * args.hidden_size * 2 * 8             # ~8 live stream tensors
    moe = P * args.num_experts_per_tok * (args.hidden_size + 2 * args.moe_intermediate_size) * 2 * 2
    decode_logits = args.vocab_size * 4
    return {"sdpa_fallback_scores": int(sdpa_fallback), "qsa_indexer_scores_masks": int(qsa),
            "hidden_streams": int(hidden), "moe_activations": int(moe),
            "decode_logits": int(decode_logits)}


def ngram_model(tw, args):
    spec = tw.NgramHashSpec(args, 0)
    out = {"rows_per_layer": spec.padded_vocab_size, "dim": spec.head_dim,
           "ple_layers": len(args.ple_layer_ids), "lookups_per_token": spec.ngram_heads}
    for fmt, group in (("bf16", 32), ("q8", 32), ("q4", 32)):
        rec = tw.ngram_record_layout(fmt, spec.head_dim, group)["record_bytes"]
        out[f"disk_bytes_{fmt}"] = rec * spec.padded_vocab_size * len(args.ple_layer_ids)
    out["page_cache_upper_bound_per_token"] = spec.ngram_heads * len(args.ple_layer_ids) * PAGE_BYTES
    return out


def check_manifest(out_dir: Path):
    tw_mod = None
    manifest = json.loads((out_dir / "twin_manifest.json").read_text())
    cfg = json.loads((out_dir / "config.json").read_text())
    pol = cfg["twin"]["policy"]
    float_bytes = {"bfloat16": 2, "float16": 2, "float32": 4}[cfg["twin"]["dtype"]]
    conv = _converter_module()
    tw_mod, _, params = enumerate_params({k: v for k, v in cfg.items() if k != "twin"})
    predicted = weight_bytes(tw_mod, params, conv._category, pol["expert_bits"], pol["dense_bits"],
                             pol["group_size"], float_bytes)
    measured = manifest["category_bytes"]
    rows = {k: {"predicted": predicted.get(k, 0), "measured": measured.get(k, 0)}
            for k in sorted(set(predicted) | set(measured))}
    ok = all(v["predicted"] == v["measured"] for v in rows.values())
    return {"dir": str(out_dir), "exact_match": ok, "categories": rows}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--context", type=int, default=40960)
    ap.add_argument("--prefill-step", type=int, default=2048)
    ap.add_argument("--query-chunk", type=int, default=512)
    ap.add_argument("--group-size", type=int, default=64)
    ap.add_argument("--target-gb", type=float, default=80.0)
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--check-manifest", type=Path, default=None)
    opts = ap.parse_args(argv)

    if opts.check_manifest:
        print(json.dumps(check_manifest(opts.check_manifest), indent=2))
        return

    cfg = json.loads(opts.config.read_text())
    tw, model, params = enumerate_params(cfg)
    args = model.language_model.args
    category = _converter_module()._category
    gs = opts.group_size
    schemes = {
        "bf16": uniform_bytes(params, category, None, gs),
        "uniform_q8": uniform_bytes(params, category, 8, gs),
        "uniform_q6": uniform_bytes(params, category, 6, gs),
        "uniform_q4": uniform_bytes(params, category, 4, gs),
        "uniform_q3": uniform_bytes(params, category, 3, gs),
        "mixed_e4_d8 (default)": weight_bytes(tw, params, category, 4, 8, gs),
        "mixed_e3_d8": weight_bytes(tw, params, category, 3, 8, gs),
        "mixed_e3_d6": weight_bytes(tw, params, category, 3, 6, gs),
    }
    n_params = {}
    for key, _, n in params:
        n_params[category(key)] = n_params.get(category(key), 0) + n
    state = runtime_state(args, opts.context)
    transient = transient_estimate(args, opts.context, opts.prefill_step, opts.query_chunk)
    transient_peak = transient["sdpa_fallback_scores"] + transient["qsa_indexer_scores_masks"] \
        + transient["hidden_streams"] + transient["moe_activations"]
    state_total = sum(state.values())
    totals = {}
    for name, per in schemes.items():
        w = sum(per.values())
        resident = w + state_total + transient_peak
        totals[name] = {"weights": w, "state": state_total, "transient_peak_est": transient_peak,
                        "resident_est": resident, "fits_target": resident <= opts.target_gb * GB}
    result = {
        "config": str(opts.config), "context": opts.context, "prefill_step": opts.prefill_step,
        "query_chunk": opts.query_chunk, "group_size": gs, "target_gb": opts.target_gb,
        "params_by_component": dict(sorted(n_params.items())),
        "params_total": sum(n_params.values()),
        "weights_by_scheme": {k: dict(sorted(v.items())) for k, v in schemes.items()},
        "runtime_state": state, "transient_estimate": transient, "totals": totals,
        "ngram_off_gpu": ngram_model(tw, args),
        "excluded": {"mtp": "not loaded (reference ignores mtp.* for next-token logits)",
                     "vision": "not loaded (text path only)"},
    }
    if opts.json:
        opts.json.write_text(json.dumps(result, indent=2) + "\n")

    def g(b):
        return f"{b / GB:7.2f}"

    comps = sorted(n_params)
    print(f"params: {result['params_total'] / 1e9:.2f} B (text decoder, MTP/vision excluded)")
    print("component".ljust(18) + "".join(k.split(" ")[0].rjust(13) for k in schemes) + "   params(B)")
    for c in comps:
        print(c.ljust(18) + "".join(g(schemes[k].get(c, 0)).rjust(13) for k in schemes)
              + f"   {n_params[c] / 1e9:8.3f}")
    print("WEIGHTS".ljust(18) + "".join(g(totals[k]["weights"]).rjust(13) for k in schemes))
    print(f"\nstate at {opts.context} tokens (GB):",
          {k: round(v / GB, 3) for k, v in state.items()}, f"total {state_total / GB:.3f}")
    print(f"transient estimate (prefill {opts.prefill_step}, query chunk {opts.query_chunk}) GB:",
          {k: round(v / GB, 3) for k, v in transient.items()})
    print("\nresident estimate (GB):")
    for k, v in totals.items():
        flag = "OK" if v["fits_target"] else "OVER"
        print(f"  {k:24s} {v['resident_est'] / GB:7.2f} GB ({v['resident_est'] / GIB:6.2f} GiB)  "
              f"target {opts.target_gb:.0f} GB: {flag}")
    ng = result["ngram_off_gpu"]
    print("\nn-gram table (off-GPU, file-backed):",
          {k: (round(v / GB, 2) if k.startswith("disk") else v) for k, v in ng.items()})


if __name__ == "__main__":
    main()
