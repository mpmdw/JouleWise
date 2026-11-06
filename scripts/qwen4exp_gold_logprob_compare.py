#!/usr/bin/env python3
"""Build and compare the Qwen4 experimental-port gold log-probability set.

The command is deliberately split at the expensive boundary.  ``prepare`` is
the only command that loads an MLX artifact; ``prompts-json`` and ``compare``
are offline.  Gold work products are immutable: ``compare`` reads a
``qwen4-gold-stream/v1`` work folder, requires its ``head`` unit to be done,
and SHA-256 verifies every ``chain.head`` output it consumes against
``units.head.artifacts``.  Prompts (and therefore next-token targets) come
from the run's ``parity/provenance.json``.

Composition with ``joulewise.align.qwen4_quant_quality``: that harness is the
primary scorer (compact top-k reference, adapter-driven teacher-forced
scoring, projected-KL lower bound), and its ``POLICY`` is the primary pass
rule here too (one table: docs/align/qwen4_exp_port/quant_quality.md#pass-rules).
This tool adds an exact full-vocabulary cross-check (KL both directions plus
the bf16-vs-fp32 reference floor) when full quantized logits are available as
an NPZ.  The e2e profile thresholds are reported as a secondary screen only.

The bf16 quality reference prompts come from
``scripts/qwen4exp_quality_ref_prompts.py`` (lead ruling L3: fixed natural-text
continuations, never maxfit output).  ``prepare`` (maxfit greedy
continuations) remains only for diagnostics and must not feed the gold pass:
``prepare`` and ``prompts-json`` refuse an ``--out`` in or beside a gold-stream
work folder or over a quality-reference prompts file.
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
from joulewise.align import qwen4_quant_quality as qq

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


STREAM_SCHEMA = "qwen4-gold-stream/v1"
CHUNK = 128


def batch_metrics(reference_logits: Any, candidate_logits: Any, *, top_k: int = 64,
                  targets: Any = None) -> dict[str, Any]:
    """Exact full-vocabulary per-position metrics for ``[positions, vocab]``.

    ``targets[i]`` is the token that position ``i`` predicts (``-1``: none).
    Top-k uses a stable descending sort (lowest id wins ties) on both sides.
    """
    import numpy as np
    ref = np.asarray(reference_logits, dtype=np.float64)
    cand = np.asarray(candidate_logits, dtype=np.float64)
    if ref.ndim != 2 or ref.shape != cand.shape or ref.shape[1] == 0:
        raise ValueError("logit vectors must have the same non-zero vocabulary size")
    if not (np.isfinite(ref).all() and np.isfinite(cand).all()):
        raise ValueError("non-finite logits")
    def log_softmax(x):
        m = x.max(axis=1, keepdims=True)
        return x - (m + np.log(np.exp(x - m).sum(axis=1, keepdims=True)))
    lr, lc = log_softmax(ref), log_softmax(cand)
    pr, pc = np.exp(lr), np.exp(lc)
    k = min(top_k, ref.shape[1])
    k5 = min(5, ref.shape[1])  # POLICY's top-5 overlap, independent of --top-k
    ro = np.argsort(-lr, axis=1, kind="stable")[:, :max(k, k5)]
    co = np.argsort(-lc, axis=1, kind="stable")[:, :max(k, k5)]
    rt, ct = ro[:, :k], co[:, :k]
    overlap = np.array([len(set(a.tolist()) & set(b.tolist())) for a, b in zip(rt, ct)]) / k
    top5 = np.array([len(set(a[:k5].tolist()) & set(b[:k5].tolist())) for a, b in zip(ro, co)]) / k5
    result = {"kl_bf16_quant": (pr * (lr - lc)).sum(axis=1), "kl_quant_bf16": (pc * (lc - lr)).sum(axis=1),
              "top1_agreement": rt[:, 0] == ct[:, 0], "topk_overlap": overlap, "top5_overlap": top5}
    if targets is not None:
        targets = np.asarray(targets, dtype=np.int64)
        if targets.shape != (ref.shape[0],) or (targets >= ref.shape[1]).any() or (targets < -1).any():
            raise ValueError("target token is outside the vocabulary")
        rows = np.flatnonzero(targets >= 0)
        result["nll_reference"] = np.full(ref.shape[0], np.nan)
        result["nll_candidate"] = np.full(ref.shape[0], np.nan)
        result["nll_reference"][rows] = -lr[rows, targets[rows]]
        result["nll_candidate"][rows] = -lc[rows, targets[rows]]
    return result


def distribution_metrics(reference_logits: Sequence[float], candidate_logits: Sequence[float],
                         *, top_k: int = 64, target_id: int | None = None) -> dict[str, float | bool]:
    """Single-position convenience wrapper over :func:`batch_metrics`."""
    if len(reference_logits) != len(candidate_logits) or not reference_logits:
        raise ValueError("logit vectors must have the same non-zero vocabulary size")
    if target_id is not None and not 0 <= target_id < len(reference_logits):
        raise ValueError("target token is outside the vocabulary")
    m = batch_metrics([reference_logits], [candidate_logits], top_k=top_k,
                      targets=None if target_id is None else [target_id])
    result: dict[str, float | bool] = {"kl_bf16_quant": float(m["kl_bf16_quant"][0]),
                                       "kl_quant_bf16": float(m["kl_quant_bf16"][0]),
                                       "top1_agreement": bool(m["top1_agreement"][0]),
                                       "topk_overlap": float(m["topk_overlap"][0])}
    if target_id is not None:
        result["nll_difference"] = float(m["nll_candidate"][0] - m["nll_reference"][0])
    return result


def aggregate(columns: Mapping[str, Any]) -> dict[str, Any]:
    import numpy as np
    out: dict[str, Any] = {"positions": int(len(columns["kl_bf16_quant"]))}
    for key in ("kl_bf16_quant", "kl_quant_bf16", "top1_agreement", "topk_overlap", "top5_overlap"):
        values = np.asarray(columns[key], dtype=np.float64)
        out[key] = float(values.mean()) if values.size else None
    kl = np.asarray(columns["kl_bf16_quant"], dtype=np.float64)
    out["kl_bf16_quant_p99"] = float(np.quantile(kl, .99)) if kl.size else None
    ref = np.asarray(columns.get("nll_reference", []), dtype=np.float64)
    cand = np.asarray(columns.get("nll_candidate", []), dtype=np.float64)
    keep = np.isfinite(ref) & np.isfinite(cand)
    out["nll_positions"] = int(keep.sum())
    out["nll_reference"] = float(ref[keep].mean()) if keep.any() else None
    out["nll_candidate"] = float(cand[keep].mean()) if keep.any() else None
    out["nll_difference"] = (out["nll_candidate"] - out["nll_reference"]) if keep.any() else None
    return out


def prompt_specs() -> list[dict[str, Any]]:
    prompts = hosted.load_prompts()["prompts"]
    nll = e2e.load_items()["nll"][:6]
    answer = [{"name": f"hosted-{p['id']}", "messages": p["messages"], "tools": p.get("tools")}
              for p in prompts]
    answer.extend({"name": f"nll-{p['id']}", "text": p["text"]} for p in nll)
    if len({row["name"] for row in answer}) != len(answer):
        raise ValueError("gold prompt names are not unique")
    return answer


def load_live_adapter(args: argparse.Namespace) -> Any:
    """Load maxfit with the live kit's guards (as its native worker does).

    The Metal memory/cache limits are set before any weight is allocated so a
    ~128 GB-class model cannot push the laptop into swap, and the PLE tables
    must page from the external volume within the operational cap.
    """
    from scripts import qwen4exp_mbp_live as live
    if agents := live.measurement_agents_loaded():
        raise ValueError("measurement agents are loaded; prepare is forbidden: " + ", ".join(agents))
    live.external(args.artifact)
    import mlx.core as mx
    device = mx.device_info() if hasattr(mx, "device_info") else mx.metal.device_info()
    args.metal_cap_gb = min(args.metal_cap_gb, int(device["max_recommended_working_set_size"]) / 1e9)
    mx.set_cache_limit(256 * 2**20)
    mx.set_memory_limit(int(args.metal_cap_gb * 1e9))
    adapter = live.load_adapter(args)
    stats = live.table_stats(adapter.model)
    for row in stats.values():
        live.external(row["path"])
    live.check_tables(stats)
    return adapter


def _gold_work_folder(directory: Path) -> bool:
    """True for a ``qwen4-gold-stream/v1`` work folder, finished or not.

    The stream creates ``staging/checkpoint`` before its first manifest
    write, so either marker identifies the folder.
    """
    manifest = directory / "manifest.json"
    if manifest.is_file():
        try:
            if json.loads(manifest.read_text()).get("schema") == STREAM_SCHEMA:
                return True
        except (OSError, ValueError, AttributeError):
            pass
    return (directory / "staging" / "checkpoint").is_dir()


def refuse_gold_pass_destination(out: Path) -> None:
    """``prepare`` output (maxfit greedy continuations) never feeds the gold pass.

    Refuses an ``--out`` inside a gold-stream work folder, beside one (the
    pass root, e.g. ``$QREF`` holding ``work/`` and ``prompts.json``), or
    over a quality-reference ``--prompts-json`` (it has a
    ``.provenance.json`` sidecar).
    """
    target = Path(out).expanduser().resolve()
    if target.with_name(target.name + ".provenance.json").exists():
        raise ValueError(f"refusing to overwrite a quality-reference prompts file: {target}")
    for directory in (target.parent, *target.parent.parents):
        if _gold_work_folder(directory):
            raise ValueError(f"refusing to write prepare output into a gold-pass work folder: {directory}")
    try:
        children = list(target.parent.iterdir())
    except OSError:
        children = []
    for child in children:
        if child.is_dir() and _gold_work_folder(child):
            raise ValueError(f"refusing to write prepare output beside a gold-pass work folder: {child}")


def prepare(args: argparse.Namespace, adapter: Any | None = None) -> int:
    """Generate fixed continuations and retain sufficient distribution data."""
    refuse_gold_pass_destination(args.out)
    if adapter is None:
        if sys.platform != "darwin" or not args.validation_only:
            raise ValueError("prepare requires macOS and --validation-only (never a measurement window)")
        adapter = load_live_adapter(args)
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
    refuse_gold_pass_destination(args.out)
    source = json.loads(args.prepared.read_text())
    if source.get("schema") != SCHEMA:
        raise ValueError("unexpected prepared-file schema")
    rows = [{"name": row["name"], "input_ids": row["token_ids"], "text": row["text"],
             "tokenizer_revision": row["tokenizer_revision"]} for row in source["prompts"]]
    if len({row["name"] for row in rows}) != len(rows):
        raise ValueError("prompt names must be unique")
    args.out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    return 0


def load_gold_head(work: Path) -> tuple[dict[str, Any], list[dict[str, Any]], Any]:
    """Return (manifest, prompts, opener) for a completed gold-stream head unit.

    Chain paths resolve against the manifest's own folder, so a moved or
    copied work folder still opens (``qq.manifest_relative``).
    """
    try:
        manifest, unit, chain, prompts, _ = qq.gold_head(work)
    except ValueError as exc:
        raise ValueError(str(exc).replace("gold work manifest has an unexpected schema",
                                          "work folder manifest is not qwen4-gold-stream/v1")) from exc

    def opener(dtype: str, name: str) -> tuple[Path, str]:
        if f"{dtype}:{name}" not in chain:
            raise ValueError(f"gold head output missing: {dtype}:{name}")
        try:
            path, _, digest = qq.head_output(work, unit, chain, f"{dtype}:{name}")
        except ValueError as exc:
            raise ValueError(f"manifest hash mismatch: {exc}") from exc
        return path, digest
    return manifest, prompts, opener


def _rows(array: Any, length: int, label: str) -> Any:
    import numpy as np
    array = np.asarray(array)
    if array.ndim == 3 and array.shape[0] == 1:
        array = array[0]
    if array.ndim != 2 or array.shape[0] != length:
        raise ValueError(f"logits shape mismatch for {label}: {array.shape}")
    return array


def _bucket(pos: int) -> str:
    for lo, hi in POSITION_BUCKETS:
        if pos >= lo and (hi is None or pos <= hi):
            return f"{lo}-{hi if hi is not None else 'end'}"
    raise AssertionError(pos)


def compare(args: argparse.Namespace) -> int:
    import numpy as np
    work = args.work_folder
    manifest, prompts, opener = load_gold_head(work)
    continuation_from: dict[str, int] = {}
    if args.prepared is not None:
        prepared = json.loads(args.prepared.read_text())
        pinned = [(p["name"], p["input_ids"]) for p in prompts]
        if isinstance(prepared, list):
            # scripts/qwen4exp_quality_ref_prompts.py output (the gold --prompts-json).
            if [(r["name"], r["input_ids"]) for r in prepared] != pinned:
                raise ValueError("prepared prompts differ from the prompts pinned by the gold run")
            continuation_from = {r["name"]: int(r["continuation_from"]) - 1 for r in prepared}
        else:
            if prepared.get("schema") != SCHEMA:
                raise ValueError("unexpected prepared-file schema")
            if [(r["name"], r["token_ids"]) for r in prepared["prompts"]] != pinned:
                raise ValueError("prepared prompts differ from the prompts pinned by the gold run")
            # Position t predicts token t+1: continuation targets start at len(input_ids)-1.
            continuation_from = {r["name"]: len(r["input_ids"]) - 1 for r in prepared["prompts"]}
    quant_sha = sha256(args.quant_logits)
    head_outputs: dict[str, Any] = {}
    columns = {case: {} for case in ("fp32", args.quant_profile)}
    per_prompt: dict[str, list[dict[str, Any]]] = {case: [] for case in columns}
    with np.load(args.quant_logits, allow_pickle=False) as quant:
        for prompt in prompts:
            name, ids = prompt["name"], prompt["input_ids"]
            n = len(ids)
            ref_path, ref_sha = opener("bf16", name)
            fp32_path, fp32_sha = opener("fp32", name)
            head_outputs[name] = {"bf16": ref_sha, "fp32": fp32_sha}
            ref = _rows(np.load(ref_path, mmap_mode="r", allow_pickle=False), n, f"bf16/{name}")
            candidates = {"fp32": _rows(np.load(fp32_path, mmap_mode="r", allow_pickle=False), n, f"fp32/{name}"),
                          args.quant_profile: _rows(quant[name], n, f"{args.quant_profile}/{name}")}
            targets = np.asarray(ids[1:] + [-1], dtype=np.int64)
            for case, cand in candidates.items():
                if cand.shape != ref.shape:
                    raise ValueError(f"vocabulary mismatch for {case}/{name}")
                prompt_cols: dict[str, list[Any]] = {}
                for start in range(0, n, CHUNK):
                    m = batch_metrics(ref[start:start + CHUNK], cand[start:start + CHUNK],
                                      top_k=args.top_k, targets=targets[start:start + CHUNK])
                    for key, value in m.items():
                        prompt_cols.setdefault(key, []).extend(np.asarray(value).tolist())
                positions = list(range(n))
                groups = {"all": positions, **{"bucket:" + _bucket(p): [] for p in positions}}
                for p in positions:
                    groups["bucket:" + _bucket(p)].append(p)
                if name in continuation_from:
                    groups["continuation"] = positions[continuation_from[name]:]
                for group, members in groups.items():
                    dest = columns[case].setdefault(group, {})
                    for key, value in prompt_cols.items():
                        dest.setdefault(key, []).extend(value[p] for p in members)
                per_prompt[case].append({"name": name, **aggregate(prompt_cols)})
    screen = e2e.THRESHOLDS["profiles"][args.quant_profile]
    per_case: dict[str, Any] = {}
    for case, groups in columns.items():
        summary = aggregate(groups["all"])
        per_case[case] = {"summary": summary, "prompts": per_prompt[case],
                          "groups": {g: aggregate(v) for g, v in groups.items() if g != "all"}}
    quant = per_case[args.quant_profile]["summary"]
    # PRIMARY: the quant-quality POLICY (one table, quant_quality.md#pass-rules).
    # Exact full-vocabulary KL >= the projected KL that POLICY bounds, so
    # applying the same bars to it is the conservative reading.
    classification = qq.classify({"mean_projected_kl": quant["kl_bf16_quant"],
                                  "p99_projected_kl": quant["kl_bf16_quant_p99"],
                                  "top1_agreement": quant["top1_agreement"],
                                  "top5_overlap": quant["top5_overlap"],
                                  "mean_nll_delta": quant["nll_difference"] if quant["nll_difference"] is not None
                                  else math.inf})
    passed = classification == "acceptable"
    # SECONDARY screen (reported, never decisive): the e2e profile bounds,
    # with the e2e NLL stage's relative rule plus a 0.02-nat floor.
    nll_ok = (quant["nll_reference"] is None or
              quant["nll_candidate"] <= quant["nll_reference"] * (1 + screen["nll_rel_max"]) + 0.02)
    screened = (quant["kl_bf16_quant"] <= screen["hosted_kl_max"] and
                quant["top1_agreement"] >= screen["hosted_top1_min"] and
                quant["topk_overlap"] >= screen["hosted_topk_overlap_min"] and nll_ok)
    per_case[args.quant_profile].update(verdict="pass" if passed else "fail", classification=classification,
                                        pass_rule=qq.policy_record(),
                                        e2e_screen={"profile": args.quant_profile, "thresholds": screen,
                                                    "pass": screened, "role": "secondary; not decisive"})
    per_case["fp32"]["role"] = "reference precision floor (official fp32 vs bf16); no verdict"
    report = {"schema": "qwen4exp-gold-logprob-comparison/v2", "reference": REFERENCE, "unit": "head",
              "work_folder": str(work), "manifest_sha256": sha256(work / "manifest.json"),
              "gold_fingerprint": manifest.get("fingerprint"), "head_status": manifest["units"]["head"].get("status"),
              "head_outputs": head_outputs, "quant_logits": str(args.quant_logits), "quant_logits_sha256": quant_sha,
              "prepared_sha256": sha256(args.prepared) if args.prepared is not None else None,
              "quant_profile": args.quant_profile, "top_k": args.top_k, "cases": per_case}
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return 0 if passed else 1


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
    p.add_argument("--work-folder", type=Path, required=True, help="gold stream work folder (holds manifest.json)")
    p.add_argument("--quant-logits", type=Path, required=True,
                   help="NPZ: prompt name -> teacher-forced [positions, vocab] logits of the quantized model")
    p.add_argument("--prepared", type=Path, help="quality-ref --prompts-json (or legacy prepare output); "
                   "adds the continuation-only group")
    p.add_argument("--quant-profile", choices=("maxfit", "maxfit5"), required=True)
    p.add_argument("--top-k", type=int, default=64)
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
