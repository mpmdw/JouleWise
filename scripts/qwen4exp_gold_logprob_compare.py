#!/usr/bin/env python3
"""Build and compare the Qwen4 experimental-port gold log-probability set.

The command is deliberately split at the expensive boundary.  ``prepare`` is
the only command that loads an MLX artifact; ``prompts-json`` and ``compare``
are offline, standard-library operations.  Gold work products are immutable:
every file consumed by ``compare`` must be named and SHA-256 pinned by the
work-folder manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from scripts import qwen4exp_e2e_eval as e2e
    from scripts import qwen4exp_hosted_reference as hosted
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts import qwen4exp_e2e_eval as e2e
    from scripts import qwen4exp_hosted_reference as hosted

SCHEMA = "qwen4exp-gold-logprobs/v1"
REFERENCE = "gold-stream-bf16 (official transformers 5.22.1)"
TOKENIZER_REVISION = "Qwen/Qwen3.8-Flash-Next"
POSITION_BUCKETS = ((0, 127), (128, 511), (512, 2047), (2048, None))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def logsumexp(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("logsumexp requires at least one value")
    maximum = max(values)
    return maximum + math.log(sum(math.exp(value - maximum) for value in values))


def distribution_metrics(reference_logits: Sequence[float], candidate_logits: Sequence[float],
                         *, top_k: int = 64, target_id: int | None = None) -> dict[str, float | bool]:
    """Exact, numerically stable full-vocabulary comparison for one position."""
    if len(reference_logits) != len(candidate_logits) or not reference_logits:
        raise ValueError("logit vectors must have the same non-zero vocabulary size")
    zr, zc = logsumexp(reference_logits), logsumexp(candidate_logits)
    lr = [float(x) - zr for x in reference_logits]
    lc = [float(x) - zc for x in candidate_logits]
    pr = [math.exp(x) for x in lr]
    pc = [math.exp(x) for x in lc]
    k = min(top_k, len(lr))
    rt = set(sorted(range(len(lr)), key=lr.__getitem__, reverse=True)[:k])
    ct = set(sorted(range(len(lc)), key=lc.__getitem__, reverse=True)[:k])
    result: dict[str, float | bool] = {
        "kl_bf16_quant": sum(p * (a - b) for p, a, b in zip(pr, lr, lc)),
        "kl_quant_bf16": sum(p * (a - b) for p, a, b in zip(pc, lc, lr)),
        "top1_agreement": max(range(len(lr)), key=lr.__getitem__) == max(range(len(lc)), key=lc.__getitem__),
        "topk_overlap": len(rt & ct) / k,
    }
    if target_id is not None:
        if not 0 <= target_id < len(lr):
            raise ValueError("target token is outside the vocabulary")
        result["nll_difference"] = (-lc[target_id]) - (-lr[target_id])
    return result


def _mean(rows: Sequence[Mapping[str, Any]], key: str) -> float:
    values = [float(row[key]) for row in rows if key in row]
    return sum(values) / len(values) if values else 0.0


def aggregate(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {"positions": len(rows), "kl_bf16_quant": _mean(rows, "kl_bf16_quant"),
            "kl_quant_bf16": _mean(rows, "kl_quant_bf16"),
            "top1_agreement": _mean(rows, "top1_agreement"),
            "topk_overlap": _mean(rows, "topk_overlap"),
            "nll_difference": _mean(rows, "nll_difference")}


def prompt_specs() -> list[dict[str, Any]]:
    prompts = hosted.load_prompts()["prompts"]
    nll = e2e.load_items()["nll"][:6]
    answer = [{"name": f"hosted-{p['id']}", "messages": p["messages"], "tools": p.get("tools")}
              for p in prompts]
    answer.extend({"name": f"nll-{p['id']}", "text": p["text"]} for p in nll)
    if len({row["name"] for row in answer}) != len(answer):
        raise ValueError("gold prompt names are not unique")
    return answer


def prepare(args: argparse.Namespace, adapter: Any | None = None) -> int:
    """Generate fixed continuations and retain sufficient distribution data."""
    if adapter is None:
        if sys.platform != "darwin" or not args.validation_only:
            raise ValueError("prepare requires macOS and --validation-only (never a measurement window)")
        from scripts import qwen4exp_mbp_live as live
        if live.measurement_agents_loaded():
            raise ValueError("measurement agents are loaded; prepare is forbidden")
        adapter = live.load_adapter(args)
    template = e2e.ChatTemplate(args.chat_template)
    records = []
    for spec in prompt_specs():
        text = spec.get("text")
        if text is None:
            text = template.render(spec["messages"], spec.get("tools"), add_generation_prompt=True,
                                   enable_thinking=False)
        input_ids = list(map(int, adapter.encode(text)))
        generated = adapter.generate(input_ids, max_tokens=128, stop_ids=(), top_k=64)
        token_ids = list(map(int, generated.token_ids))
        scored = adapter.score(input_ids, token_ids, top_k=64)
        # Adapters may expose exact normalizers separately; deriving them from
        # normalized top-k values would be wrong, so absence fails closed.
        normalizers = getattr(scored, "logsumexp", None)
        if normalizers is None:
            raise ValueError("validated adapter score result lacks full-vocabulary logsumexp")
        records.append({"name": spec["name"], "text": text, "input_ids": input_ids,
                        "continuation_ids": token_ids, "token_ids": input_ids + token_ids,
                        "top_logprobs": scored.top_logprobs, "logsumexp": list(map(float, normalizers)),
                        "tokenizer_revision": args.tokenizer_revision})
    output = {"schema": SCHEMA, "profile": args.profile, "tokens_per_prompt": 128,
              "top_k": 64, "tokenizer_revision": args.tokenizer_revision, "prompts": records}
    args.out.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    return 0


def prompts_json(args: argparse.Namespace) -> int:
    source = json.loads(args.prepared.read_text())
    if source.get("schema") != SCHEMA:
        raise ValueError("unexpected prepared-file schema")
    rows = [{"name": row["name"], "input_ids": row["token_ids"], "text": row["text"],
             "tokenizer_revision": row["tokenizer_revision"]} for row in source["prompts"]]
    if len({row["name"] for row in rows}) != len(rows):
        raise ValueError("prompt names must be unique")
    args.out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    return 0


def _verified_artifacts(folder: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    artifacts = manifest.get("artifacts", manifest.get("files", {}))
    verified = {}
    for name, entry in artifacts.items():
        rel, digest = (entry["path"], entry["sha256"]) if isinstance(entry, Mapping) else (name, entry)
        path = folder / rel
        if not path.is_file() or sha256(path) != digest:
            raise ValueError(f"manifest hash mismatch: {rel}")
        verified[name] = path
    return manifest, verified


def _load_logits(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    return {row["name"]: row for row in data.get("prompts", data)}


def compare(args: argparse.Namespace) -> int:
    manifest, files = _verified_artifacts(args.work_folder)
    cases = manifest.get("cases", {})
    needed = {"bf16", "fp32", args.quant_profile}
    if not needed <= set(cases):
        raise ValueError(f"head-unit manifest lacks cases: {sorted(needed - set(cases))}")
    loaded = {case: _load_logits(files[cases[case]]) for case in needed}
    per_case = {}
    for case in ("fp32", args.quant_profile):
        per_prompt = []
        all_rows = []
        buckets: dict[str, list[dict[str, Any]]] = {}
        if set(loaded[case]) != set(loaded["bf16"]):
            raise ValueError(f"prompt coverage mismatch in {case}")
        for name, ref in loaded["bf16"].items():
            candidate = loaded[case][name]
            targets = ref.get("continuation_ids", [])
            if len(ref["logits"]) != len(candidate["logits"]):
                raise ValueError(f"position count mismatch: {case}/{name}")
            rows = []
            for pos, (rlogits, clogits) in enumerate(zip(ref["logits"], candidate["logits"])):
                row = {"position": pos, **distribution_metrics(rlogits, clogits,
                       target_id=targets[pos] if pos < len(targets) else None)}
                rows.append(row); all_rows.append(row)
                for lo, hi in POSITION_BUCKETS:
                    if pos >= lo and (hi is None or pos <= hi):
                        buckets.setdefault(f"{lo}-{hi if hi is not None else 'end'}", []).append(row)
                        break
            per_prompt.append({"name": name, **aggregate(rows)})
        summary = aggregate(all_rows)
        tolerance = e2e.THRESHOLDS["profiles"][args.quant_profile]
        verdict = (summary["kl_bf16_quant"] <= tolerance["hosted_kl_max"] and
                   summary["top1_agreement"] >= tolerance["hosted_top1_min"] and
                   summary["topk_overlap"] >= tolerance["hosted_topk_overlap_min"] and
                   abs(summary["nll_difference"]) <= tolerance["nll_rel_max"])
        per_case[case] = {"summary": summary, "prompts": per_prompt,
                          "position_buckets": {key: aggregate(value) for key, value in buckets.items()},
                          "verdict": "pass" if verdict else "fail", "thresholds": tolerance}
    report = {"schema": "qwen4exp-gold-logprob-comparison/v1", "reference": REFERENCE,
              "unit": "head", "manifest_sha256": sha256(args.work_folder / "manifest.json"),
              "quant_profile": args.quant_profile, "cases": per_case}
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0 if per_case[args.quant_profile]["verdict"] == "pass" else 1


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--artifact", type=Path, required=True); p.add_argument("--manifest-sha256", required=True)
    p.add_argument("--profile", choices=("maxfit", "maxfit5"), required=True)
    p.add_argument("--chat-template", type=Path, required=True); p.add_argument("--out", type=Path, required=True)
    p.add_argument("--tokenizer-revision", default=TOKENIZER_REVISION); p.add_argument("--validation-only", action="store_true")
    p.add_argument("--prefill-step", type=int, default=512); p.add_argument("--metal-cap-gb", type=float, default=115.4)
    p.set_defaults(func=prepare)
    p = sub.add_parser("prompts-json")
    p.add_argument("--prepared", type=Path, required=True); p.add_argument("--out", type=Path, required=True); p.set_defaults(func=prompts_json)
    p = sub.add_parser("compare")
    p.add_argument("--work-folder", type=Path, required=True); p.add_argument("--quant-profile", choices=("maxfit", "maxfit5"), required=True)
    p.add_argument("--out", type=Path, required=True); p.set_defaults(func=compare)
    return root


def main(argv: Sequence[str] | None = None, *, adapter: Any | None = None) -> int:
    args = parser().parse_args(argv)
    return args.func(args, adapter) if args.command == "prepare" else args.func(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr); raise SystemExit(2)
