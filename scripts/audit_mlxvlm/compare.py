"""Three-way logits comparison: transformers reference (ref), our Sol port
(port) and mlx-vlm (vlm). Prints a markdown table and writes compare.json.

Usage: python compare.py WORKDIR
"""
import json
import sys
from pathlib import Path

import numpy as np

STEPS = 3


def metrics(a, b):
    """max abs; rel = max abs / max |truth|; cosine over all logits; p50 =
    median over positions of the per-position max abs (robust to a single
    discrete flip); top1 = argmax agreement rate over positions."""
    a2 = np.asarray(a, dtype=np.float64).reshape(-1, np.shape(a)[-1])
    b2 = np.asarray(b, dtype=np.float64).reshape(-1, np.shape(b)[-1])
    a, b = a2.ravel(), b2.ravel()
    d = np.abs(a - b)
    denom = max(np.abs(b).max(), 1e-12)
    cos = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-300))
    per_pos = np.abs(a2 - b2).max(-1)
    return dict(max_abs=float(d.max()), rel=float(d.max() / denom), cos=cos,
                p50=float(np.median(per_pos)), top1=float((a2.argmax(-1) == b2.argmax(-1)).mean()))


def valid_padded(batch, mask):
    """Rows' valid positions of a left-padded batch, as a list of [n, V]."""
    return [batch[b][mask[b].astype(bool)] for b in range(batch.shape[0])]


def views(r, ref):
    """Scenario name -> array (flattened views comparable across sources)."""
    out = {}
    for k in ("prefill", "stepwise", "chunked", "prefill_nocache", "prefill_perexpert", "spec_rollback"):
        if k in r:
            out[k] = r[k]
    mask = ref["padded_mask"]
    if "padded_batch" in r:
        out["padded_batch_valid"] = np.concatenate(valid_padded(r["padded_batch"], mask))
    if "padded_continuation" in r:
        out["padded_continuation"] = r["padded_continuation"]
    return out


def truth(ref):
    """What every scenario must equal: single-row unpadded prefill logits."""
    t = {k: ref["prefill"] for k in ("prefill", "stepwise", "chunked", "prefill_nocache",
                                      "prefill_perexpert")}
    # run_vlm.speculative_rollback: prefill L//2, speculate 5, commit 2, continue.
    L = ref["prefill"].shape[1]
    t["spec_rollback"] = np.delete(ref["prefill"], range(L // 2, L // 2 + 2), axis=1)
    rows = [ref[f"single_row{b}"][0] for b in range(ref["padded_mask"].shape[0])]
    t["padded_batch_valid"] = np.concatenate([row[:-STEPS] for row in rows])
    t["padded_continuation"] = np.stack([row[-STEPS:] for row in rows])
    return t


def main(work):
    work = Path(work)
    rows, result = [], {}
    for d in sorted(p for p in work.iterdir() if p.is_dir() and (p / "ref.npz").exists()):
        ref = dict(np.load(d / "ref.npz"))
        srcs = {"ref": ref}
        for name in ("port", "vlm", "vlmP"):
            if (d / f"{name}.npz").exists():
                srcs[name] = dict(np.load(d / f"{name}.npz"))
        T = truth(ref)
        V = {k: views(v, ref) for k, v in srcs.items()}
        for scen in T:
            for a, b in (("ref", "truth"), ("port", "ref"), ("vlm", "ref"), ("vlm", "port"), ("vlmP", "ref")):
                left = V.get(a, {}).get(scen)
                right = T[scen] if b in ("truth", "ref") else V.get(b, {}).get(scen)
                # Reference scenario entries are compared to the unpadded truth;
                # implementation entries are compared to the reference's own
                # scenario output AND (vs ref) to the truth.
                if left is None or right is None:
                    continue
                if a != "ref" and b == "ref":
                    right = T[scen]
                m = metrics(left, right)
                key = f"{d.name}/{scen}/{a}-vs-{b if b != 'ref' else 'ref'}"
                result[key] = m
                rows.append((d.name, scen, f"{a} vs {b}", m))
        # bf16 noise floor: every source's bf16 output vs the fp32 reference truth.
        if d.name.endswith("_bf16") and (work / d.name.replace("_bf16", "_fp32") / "ref.npz").exists():
            T32 = truth(dict(np.load(work / d.name.replace("_bf16", "_fp32") / "ref.npz")))
            for scen in T32:
                for a in ("ref", "port", "vlm", "vlmP"):
                    left = V.get(a, {}).get(scen)
                    if left is None:
                        continue
                    m = metrics(left, T32[scen])
                    result[f"{d.name}/{scen}/{a}-vs-ref_fp32"] = m
                    rows.append((d.name, scen, f"{a} vs ref_fp32", m))
    print("| case | scenario | pair | max abs | rel | cosine | p50 pos | top-1 |")
    print("|---|---|---|---|---|---|---|---|")
    for case, scen, pair, m in rows:
        print(f"| {case} | {scen} | {pair} | {m['max_abs']:.2e} | {m['rel']:.2e} | {m['cos']:.7f} | {m['p50']:.2e} | {m['top1']:.3f} |")
    (work / "compare.json").write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
