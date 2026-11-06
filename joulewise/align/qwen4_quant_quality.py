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
from collections.abc import Mapping
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
# The single pass-rule table (POLICY primary; e2e profile screens secondary).
PASS_RULES_DOC = "docs/align/qwen4_exp_port/quant_quality.md#pass-rules"
CHUNK_ROWS = 64  # rows of a [positions, vocab] array materialized at once


def classify(summary):
    """POLICY label for a summary; only ``acceptable`` admits a variant."""
    def passes(g):
        return (summary["mean_projected_kl"] <= g["mean_projected_kl_max"] and
                summary["p99_projected_kl"] <= g["p99_projected_kl_max"] and
                summary["top1_agreement"] >= g["top1_agreement_min"] and
                summary["top5_overlap"] >= g["top5_overlap_min"] and
                summary["mean_nll_delta"] <= g["mean_nll_delta_max"])
    return "acceptable" if passes(POLICY["acceptable"]) else "marginal" if passes(POLICY["marginal"]) else "reject"


def policy_record():
    """What every quality report embeds to point at the primary pass rule."""
    return {"primary": "joulewise.align.qwen4_quant_quality.POLICY", "doc": PASS_RULES_DOC,
            "schema": SCHEMA, "policy": POLICY, "admits": ["acceptable"]}


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


def _rows2d(array):
    """``[positions, vocab]`` view of a logits array (memory maps stay maps)."""
    import numpy as np
    array = array if isinstance(array, np.ndarray) else np.asarray(array, dtype=np.float32)
    if array.ndim == 3 and array.shape[0] == 1:
        array = array[0]
    if array.ndim != 2:
        raise ValueError(f"logits must be [positions, vocab], got {array.shape}")
    return array


def capture(logits_by_prompt, prompts, output, top_k=64, source=None):
    """Write an atomic compact reference without retaining inputs afterward."""
    import numpy as np
    if top_k < 5:
        raise ValueError("top-k must be at least five")
    arrays, manifest = {}, {"schema": SCHEMA, "kind": "reference", "top_k": top_k,
                            "prompts": [], "source": source or {}}
    for prompt in prompts:
        name, ids = prompt["name"], prompt["input_ids"]
        # One prompt at a time, and at most CHUNK_ROWS rows of it in float32:
        # a gold head output is [positions, 248320] (about 0.5 GB at 512
        # positions) and arrives as a read-only memory map.
        logits = _rows2d(logits_by_prompt[name])
        if logits.shape[0] != len(ids) or logits.shape[1] <= top_k:
            raise ValueError(f"invalid logits shape for {name}: {logits.shape}")
        targets = np.asarray(list(ids[1:]) + [-1], dtype=np.int64)
        order, top, lse, target = [], [], [], []
        for start in range(0, logits.shape[0], CHUNK_ROWS):
            block = np.asarray(logits[start:start + CHUNK_ROWS], dtype=np.float32)
            if not np.isfinite(block).all():
                raise ValueError(f"non-finite reference logits for {name}")
            # Stable descending order gives a deterministic lowest-id tie rule.
            rows = np.argsort(-block, axis=-1, kind="stable")[:, :top_k]
            order.append(rows.astype(np.int32))
            top.append(np.take_along_axis(block, rows, axis=-1))
            lse.append(_lse(block).astype(np.float32))
            want = targets[start:start + CHUNK_ROWS]
            keep = np.flatnonzero(want >= 0)
            target.append(block[keep, want[keep]])
            del block, rows
        arrays[f"{name}__indices"] = np.concatenate(order)
        arrays[f"{name}__logits"] = np.concatenate(top)
        arrays[f"{name}__logsumexp"] = np.concatenate(lse)
        arrays[f"{name}__target_logits"] = np.concatenate(target)
        manifest["prompts"].append({"name": name, "input_ids": ids,
                                    "shape": list(logits.shape)})
        del logits
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
            q_all = _rows2d(logits_by_prompt[name])
            if list(q_all.shape) != prompt["shape"]:
                raise ValueError(f"invalid quantized logits for {name}")
            idx_all, ptop_all = saved[f"{name}__indices"], saved[f"{name}__logits"]
            plse_all, ptarget = saved[f"{name}__logsumexp"], saved[f"{name}__target_logits"]
            targets = np.asarray(list(prompt["input_ids"][1:]) + [-1], dtype=np.int64)
            for start in range(0, q_all.shape[0], CHUNK_ROWS):
                stop = start + CHUNK_ROWS
                q = np.asarray(q_all[start:stop], dtype=np.float32)
                if not np.isfinite(q).all():
                    raise ValueError(f"invalid quantized logits for {name}")
                idx, ptop, plse = idx_all[start:stop], ptop_all[start:stop], plse_all[start:stop]
                qlse = _lse(q); qtop = np.take_along_axis(q, idx, axis=-1)
                pp = np.exp(ptop - plse[:, None]); qp = np.exp(qtop - qlse[:, None])
                ptail = np.maximum(0., 1. - pp.sum(-1)); qtail = np.maximum(0., 1. - qp.sum(-1))
                kl = (pp * ((ptop-plse[:, None])-(qtop-qlse[:, None]))).sum(-1)
                kl += np.where(ptail > 0, ptail * (np.log(np.maximum(ptail, 1e-45))-np.log(np.maximum(qtail, 1e-45))), 0.)
                q5 = np.argsort(-q, axis=-1, kind="stable")[:, :5]
                overlap = (idx[:, :5, None] == q5[:, None, :]).any(-1).sum(-1) / 5
                for offset in range(len(q)):
                    pos = start + offset
                    row = {"prompt": name, "position": pos, "projected_kl": float(kl[offset]),
                           "top1_agreement": bool(idx[offset, 0] == q5[offset, 0]),
                           "top5_overlap": float(overlap[offset])}
                    target = int(targets[pos])
                    if target >= 0:  # the final input token has no pinned target
                        row["nll_delta"] = float(-(q[offset, target] - qlse[offset]) + (ptarget[pos] - plse[offset]))
                    per_token.append(row)
                del q
            del q_all
    values = lambda key: np.asarray([r[key] for r in per_token if key in r], dtype=np.float64)
    summary = {"mean_projected_kl": float(values("projected_kl").mean()),
               "p99_projected_kl": float(np.quantile(values("projected_kl"), .99)),
               "top1_agreement": float(values("top1_agreement").mean()),
               "top5_overlap": float(values("top5_overlap").mean()),
               "mean_nll_delta": float(values("nll_delta").mean())}
    result = {"schema": SCHEMA, "kind": "score", "variant": variant or {}, "reference_sha256": _sha(reference),
              "reference_manifest_sha256": _sha(str(reference) + ".json"),
              "metric_note": "projected_kl is exact on reference-top-k plus one OTHER bucket and lower-bounds full-vocabulary KL",
              "summary": summary, "classification": classify(summary), "policy": POLICY,
              "pass_rule": policy_record(), "tokens": per_token}
    if output: Path(output).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return result


class LazyLogits(Mapping):
    """Prompt name -> logits, produced only when that prompt is read.

    Nothing is cached, so a consumer that walks prompts in order holds one
    prompt's ``[positions, vocab]`` array at a time.
    """
    def __init__(self, names, produce):
        self._names, self._produce = list(names), produce

    def __getitem__(self, name):
        if name not in self._names:
            raise KeyError(name)
        return self._produce(name)

    def __iter__(self):
        return iter(self._names)

    def __len__(self):
        return len(self._names)


def load_npz(path, prompts):
    import numpy as np
    names = [p["name"] for p in prompts]

    def produce(name):
        with np.load(path, allow_pickle=False) as data:
            return np.array(data[name], dtype=np.float32)
    with np.load(path, allow_pickle=False) as data:
        missing = [n for n in names if n not in data.files]
    if missing:
        raise ValueError(f"--logits-npz lacks prompts: {missing}")
    return LazyLogits(names, produce)


def _same_prompts(a, b):
    return [(p["name"], list(p["input_ids"])) for p in a] == [(p["name"], list(p["input_ids"])) for p in b]


def manifest_relative(work, raw, artifacts):
    """The manifest-relative key of a recorded chain path.

    The stream driver records chain outputs as absolute paths of the folder it
    ran in, while ``units.<unit>.artifacts`` pins them relative to that folder.
    A gold work folder that was moved or copied (or reached through a symlink
    such as /tmp -> /private/tmp) is therefore resolved against the manifest's
    own folder: the key is the unique pinned artifact that the recorded path
    ends with.
    """
    path = Path(raw)
    if not path.is_absolute():
        rel = path.as_posix()
    else:
        rel = None
        for base in (Path(work), Path(work).resolve()):
            try:
                rel = path.relative_to(base).as_posix()
                break
            except ValueError:
                continue
        if rel is None or rel not in artifacts:
            parts = path.parts
            matches = [key for key in artifacts
                       if len(Path(key).parts) <= len(parts) and parts[-len(Path(key).parts):] == Path(key).parts]
            if len(matches) != 1:
                raise ValueError(f"recorded path is not a unique pinned artifact of this work folder: {raw}")
            rel = matches[0]
    if Path(rel).is_absolute() or ".." in Path(rel).parts or rel not in artifacts:
        raise ValueError(f"gold head output is not pinned by the manifest: {rel}")
    return rel


def gold_head(work):
    """(manifest, unit row, chain, prompts, provenance) of a finished gold head unit."""
    from .qwen4_gold.stream import STREAM_SCHEMA
    work = Path(work)
    manifest_path = work / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"not a gold stream work folder (no manifest.json): {work}")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema") != STREAM_SCHEMA:
        raise ValueError("gold work manifest has an unexpected schema")
    unit, chain = manifest.get("units", {}).get("head"), manifest.get("chain", {}).get("head")
    if not unit or unit.get("state") != "done" or not chain:
        raise ValueError("gold head unit has not completed")
    provenance = json.loads((work / "parity" / "provenance.json").read_text())
    prompts = [{"name": p["name"], "input_ids": [int(i) for i in p["input_ids"]]} for p in provenance["prompts"]]
    return manifest, unit, chain, prompts, provenance


def head_output(work, unit, chain, key):
    """(path, manifest-relative key, sha256) of one gold head output, hash-checked on every open."""
    from .qwen4_gold.core import sha256 as file_sha
    raw = chain.get(key)
    if raw is None:
        raise ValueError(f"missing gold head output for {key}")
    artifacts = unit.get("artifacts", {})
    rel = manifest_relative(work, raw, artifacts)
    path = Path(work) / rel
    if not path.is_file() or file_sha(path) != artifacts[rel]:
        raise ValueError(f"gold head output is not pinned by the manifest or changed: {rel}")
    return path, rel, artifacts[rel]


def load_gold(work, prompts=None):
    """Read bf16 head logits from a ``qwen4-gold-stream/v1`` work folder.

    The work folder (not its ``parity`` subdirectory) is required: its
    manifest is the only record of which head outputs completed and of their
    SHA-256.  Prompts come from the run's own provenance, so next-token
    targets cannot be paired with a different prompt pin.  ``prompts`` is an
    optional cross-check and must match exactly.

    Logits are streamed: each prompt's head output is hash-verified and
    memory-mapped only when that prompt is read, never all at once.
    """
    import numpy as np
    from .qwen4_gold.stream import STREAM_SCHEMA
    work = Path(work)
    manifest, unit, chain, run_prompts, provenance = gold_head(work)
    if prompts is not None and not _same_prompts(prompts, run_prompts):
        raise ValueError("--prompts-json differs from the prompts pinned by the gold run")
    outputs = {}
    for p in run_prompts:  # Fail before any work if a pin is missing (hashing waits).
        key = "bf16:" + p["name"]
        if key not in chain:
            raise ValueError(f"missing gold bf16 head output for {p['name']}")
        rel = manifest_relative(work, chain[key], unit.get("artifacts", {}))
        outputs[p["name"]] = {"path": rel, "sha256": unit["artifacts"][rel]}

    def produce(name):
        path, _, _ = head_output(work, unit, chain, "bf16:" + name)
        return np.load(path, mmap_mode="r", allow_pickle=False)
    source = {"gold_work": str(work), "gold_fingerprint": manifest.get("fingerprint"),
              "gold_manifest_schema": STREAM_SCHEMA, "head_status": unit.get("status"),
              "head_result_sha256": unit.get("result_sha256"), "head_outputs": outputs,
              "provenance_fingerprint": provenance.get("fingerprint")}
    return LazyLogits([p["name"] for p in run_prompts], produce), run_prompts, source


def load_adapter(spec, model, prompts, manifest_sha256=None):
    """Load the model once, then score every prompt teacher-forced, lazily.

    An adapter module may define ``load(model_path, manifest_sha256=...)``;
    its handle is passed to the scoring function for every prompt, so a
    ~200 GB model is opened exactly once per score run.  Each prompt's logits
    are computed when the scorer reads that prompt, so at most one prompt's
    ``[positions, vocab]`` array is alive.
    """
    import numpy as np
    module, _, function = spec.partition(":")
    if not function: function = "teacher_forced_logits"
    module = importlib.import_module(module)
    call = getattr(module, function)
    loader = getattr(module, "load", None)
    handle = loader(model, manifest_sha256=manifest_sha256) if loader is not None else model
    ids = {p["name"]: p["input_ids"] for p in prompts}
    return LazyLogits(list(ids), lambda name: np.asarray(call(handle, ids[name]), np.float32))


def reference_prompts(reference):
    manifest = json.loads(Path(str(reference) + ".json").read_text())
    return [{"name": p["name"], "input_ids": p["input_ids"]} for p in manifest["prompts"]]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="command", required=True)
    for name in ("capture", "score"):
        p = sub.add_parser(name); p.add_argument("--prompts-json"); p.add_argument("--logits-npz")
        p.add_argument("--adapter"); p.add_argument("--model"); p.add_argument("--output", required=True)
        if name == "capture": p.add_argument("--gold-root", help="gold stream work folder (contains manifest.json)"); p.add_argument("--top-k", type=int, default=64)
        else:
            p.add_argument("--reference", required=True); p.add_argument("--variant-name", required=True)
            p.add_argument("--manifest-sha256", help="pinned manifest.json sha256 of the assembled artifact")
    args = parser.parse_args(argv)
    gold = getattr(args, "gold_root", None)
    sources = sum(bool(x) for x in (args.logits_npz, gold, args.adapter))
    if sources != 1: parser.error("select exactly one of --logits-npz, --gold-root, or --adapter")
    if args.adapter and not args.model: parser.error("--adapter requires --model")
    explicit = _prompts(args.prompts_json) if args.prompts_json else None
    source = {}
    if args.command == "score":
        # Score exactly the sequences the reference pinned; a different prompt
        # file would pair quantized logits with the wrong targets.
        prompts = reference_prompts(args.reference)
        if explicit is not None and not _same_prompts(explicit, prompts):
            parser.error("--prompts-json differs from the prompts pinned by --reference")
    else:
        prompts = explicit if explicit is not None else _prompts(None)
    if gold:
        logits, prompts, source = load_gold(gold, explicit)
    elif args.logits_npz:
        logits = load_npz(args.logits_npz, prompts)
        source = {"logits_npz": str(args.logits_npz), "logits_npz_sha256": _sha(args.logits_npz)}
    else:
        logits = load_adapter(args.adapter, args.model, prompts, getattr(args, "manifest_sha256", None))
    if args.command == "capture":
        result = capture(logits, prompts, args.output, args.top_k, source)
    else:
        result = score(args.reference, logits, args.output,
                       {"name": args.variant_name, "model": args.model, "adapter": args.adapter,
                        "manifest_sha256": args.manifest_sha256, **source})
    print(json.dumps(result.get("summary", result), indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
