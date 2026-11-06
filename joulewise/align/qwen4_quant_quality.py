"""Compact, reusable teacher-forced quantization-quality measurements.

The compact reference preserves the reference top-k distribution, its tail as
one probability bucket, and next-token logits.  Consequently ``projected_kl``
is the exact KL after mapping the vocabulary to top-k + OTHER; it is a lower
bound on full-vocabulary KL, not a mislabeled reconstruction of unavailable
tail probabilities.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
from pathlib import Path

from .qwen4_gold.runner import DEFAULT_PROMPTS

SCHEMA = "qwen4-quant-quality/v1"
POLICY = {
    "acceptable": {"mean_projected_kl_max": .02, "p99_projected_kl_max": .10,
                   "top1_agreement_min": .90, "top5_overlap_min": .90,
                   "mean_nll_delta_max": .05},
    "marginal": {"mean_projected_kl_max": .05, "p99_projected_kl_max": .25,
                 "top1_agreement_min": .80, "top5_overlap_min": .80,
                 "mean_nll_delta_max": .15},
}


def _sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _lse(x):
    import numpy as np
    maximum = np.max(x, axis=-1, keepdims=True)
    return (maximum[..., 0] + np.log(np.exp(x - maximum).sum(axis=-1)))


def _prompts(path):
    value = DEFAULT_PROMPTS if path is None else json.loads(Path(path).read_text())
    if not value or any(not p.get("input_ids") for p in value):
        raise ValueError("empty prompt set")
    return value


def capture(logits_by_prompt, prompts, output, top_k=64, source=None):
    """Write an atomic compact reference without retaining inputs afterward."""
    import numpy as np
    if top_k < 5:
        raise ValueError("top-k must be at least five")
    arrays, manifest = {}, {"schema": SCHEMA, "kind": "reference", "top_k": top_k,
                            "prompts": [], "source": source or {}}
    for prompt in prompts:
        name, ids = prompt["name"], prompt["input_ids"]
        logits = np.asarray(logits_by_prompt[name], dtype=np.float32)
        if logits.ndim == 3 and logits.shape[0] == 1:
            logits = logits[0]
        if logits.ndim != 2 or logits.shape[0] != len(ids) or logits.shape[1] <= top_k:
            raise ValueError(f"invalid logits shape for {name}: {logits.shape}")
        # Stable descending order gives a deterministic lowest-id tie rule.
        order = np.argsort(-logits, axis=-1, kind="stable")[:, :top_k]
        top = np.take_along_axis(logits, order, axis=-1)
        targets = np.asarray(ids[1:], dtype=np.int64)
        arrays[f"{name}__indices"] = order.astype(np.int32)
        arrays[f"{name}__logits"] = top
        arrays[f"{name}__logsumexp"] = _lse(logits).astype(np.float32)
        arrays[f"{name}__target_logits"] = logits[:-1][np.arange(len(targets)), targets]
        manifest["prompts"].append({"name": name, "input_ids": ids,
                                    "shape": list(logits.shape)})
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    with temp.open("wb") as stream:
        np.savez_compressed(stream, **arrays)
    temp.replace(output)
    manifest["arrays_sha256"] = _sha(output)
    Path(str(output) + ".json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def score(reference, logits_by_prompt, output=None, variant=None):
    import numpy as np
    reference = Path(reference)
    manifest = json.loads(Path(str(reference) + ".json").read_text())
    if manifest.get("schema") != SCHEMA or manifest.get("kind") != "reference" or _sha(reference) != manifest["arrays_sha256"]:
        raise ValueError("reference identity/integrity failure")
    per_token = []
    with np.load(reference, allow_pickle=False) as saved:
        for prompt in manifest["prompts"]:
            name = prompt["name"]
            q = np.asarray(logits_by_prompt[name], dtype=np.float32)
            if q.ndim == 3 and q.shape[0] == 1: q = q[0]
            if list(q.shape) != prompt["shape"] or not np.isfinite(q).all():
                raise ValueError(f"invalid quantized logits for {name}")
            idx, ptop, plse = saved[f"{name}__indices"], saved[f"{name}__logits"], saved[f"{name}__logsumexp"]
            qlse = _lse(q); qtop = np.take_along_axis(q, idx, axis=-1)
            pp = np.exp(ptop - plse[:, None]); qp = np.exp(qtop - qlse[:, None])
            ptail = np.maximum(0., 1. - pp.sum(-1)); qtail = np.maximum(0., 1. - qp.sum(-1))
            kl = (pp * ((ptop-plse[:, None])-(qtop-qlse[:, None]))).sum(-1)
            kl += np.where(ptail > 0, ptail * (np.log(np.maximum(ptail, 1e-45))-np.log(np.maximum(qtail, 1e-45))), 0.)
            q5 = np.argsort(-q, axis=-1, kind="stable")[:, :5]
            overlap = (idx[:, :5, None] == q5[:, None, :]).any(-1).sum(-1) / 5
            target = np.asarray(prompt["input_ids"][1:])
            q_target = q[:-1][np.arange(len(target)), target]
            nll_delta = -(q_target-qlse[:-1]) + (saved[f"{name}__target_logits"]-plse[:-1])
            for pos in range(len(q)):
                row = {"prompt": name, "position": pos, "projected_kl": float(kl[pos]),
                       "top1_agreement": bool(idx[pos, 0] == q5[pos, 0]),
                       "top5_overlap": float(overlap[pos])}
                if pos < len(nll_delta): row["nll_delta"] = float(nll_delta[pos])
                per_token.append(row)
    values = lambda key: np.asarray([r[key] for r in per_token if key in r], dtype=np.float64)
    summary = {"mean_projected_kl": float(values("projected_kl").mean()),
               "p99_projected_kl": float(np.quantile(values("projected_kl"), .99)),
               "top1_agreement": float(values("top1_agreement").mean()),
               "top5_overlap": float(values("top5_overlap").mean()),
               "mean_nll_delta": float(values("nll_delta").mean())}
    def passes(g):
        return (summary["mean_projected_kl"] <= g["mean_projected_kl_max"] and
                summary["p99_projected_kl"] <= g["p99_projected_kl_max"] and
                summary["top1_agreement"] >= g["top1_agreement_min"] and
                summary["top5_overlap"] >= g["top5_overlap_min"] and
                summary["mean_nll_delta"] <= g["mean_nll_delta_max"])
    label = "acceptable" if passes(POLICY["acceptable"]) else "marginal" if passes(POLICY["marginal"]) else "reject"
    result = {"schema": SCHEMA, "kind": "score", "variant": variant or {}, "reference_sha256": _sha(reference),
              "metric_note": "projected_kl is exact on reference-top-k plus one OTHER bucket and lower-bounds full-vocabulary KL",
              "summary": summary, "classification": label, "policy": POLICY, "tokens": per_token}
    if output: Path(output).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return result


def load_npz(path, prompts):
    import numpy as np
    with np.load(path, allow_pickle=False) as data:
        return {p["name"]: np.array(data[p["name"]], dtype=np.float32) for p in prompts}


def load_gold(root, prompts):
    import numpy as np
    root = Path(root); result = {}
    for p in prompts:
        matches = list(root.glob(f"head/{p['name']}-bf16-real/reference/output.npy"))
        if len(matches) != 1: raise ValueError(f"missing unique gold head output for {p['name']}")
        result[p["name"]] = np.load(matches[0], allow_pickle=False)
    return result


def load_adapter(spec, model, prompts):
    import numpy as np
    module, _, function = spec.partition(":")
    if not function: function = "teacher_forced_logits"
    call = getattr(importlib.import_module(module), function)
    return {p["name"]: np.asarray(call(model, p["input_ids"]), np.float32) for p in prompts}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="command", required=True)
    for name in ("capture", "score"):
        p = sub.add_parser(name); p.add_argument("--prompts-json"); p.add_argument("--logits-npz")
        p.add_argument("--adapter"); p.add_argument("--model"); p.add_argument("--output", required=True)
        if name == "capture": p.add_argument("--gold-root"); p.add_argument("--top-k", type=int, default=64)
        else: p.add_argument("--reference", required=True); p.add_argument("--variant-name", required=True)
    args = parser.parse_args(argv); prompts = _prompts(args.prompts_json)
    sources = sum(bool(x) for x in (args.logits_npz, getattr(args, "gold_root", None), args.adapter))
    if sources != 1: parser.error("select exactly one of --logits-npz, --gold-root, or --adapter")
    logits = load_npz(args.logits_npz, prompts) if args.logits_npz else load_gold(args.gold_root, prompts) if getattr(args, "gold_root", None) else load_adapter(args.adapter, args.model, prompts)
    result = capture(logits, prompts, args.output, args.top_k, {"gold_root": args.gold_root} if getattr(args, "gold_root", None) else {}) if args.command == "capture" else score(args.reference, logits, args.output, {"name": args.variant_name, "model": args.model})
    print(json.dumps(result.get("summary", result), indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
