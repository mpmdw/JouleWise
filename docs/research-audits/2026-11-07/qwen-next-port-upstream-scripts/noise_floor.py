"""Score the L3 fp32 reference chain against the bf16 top-64 reference with the
exact formula of joulewise.align.qwen4_quant_quality.score (92042869a), to
measure the reference's own bf16 noise floor under the POLICY metrics.
Also full-vocabulary KL(bf16 || fp32) for comparison. Read-only."""
import json
import sys
import numpy as np

ref_npz, ref_json, head_dir = sys.argv[1], sys.argv[2], sys.argv[3]
man = json.load(open(ref_json))
CH = 64


def lse(x):
    m = np.max(x, axis=-1, keepdims=True)
    return m[..., 0] + np.log(np.exp(x - m).sum(axis=-1))


rows = []
full = []
per_prompt = {}
with np.load(ref_npz, allow_pickle=False) as saved:
    for p in man["prompts"]:
        name = p["name"]
        short = name[len("hosted-"):] if name.startswith("hosted-") else name
        q_all = np.load(f"{head_dir}/{name}-fp32-real/reference/output.npy", mmap_mode="r")
        b_all = np.load(f"{head_dir}/{name}-bf16-real/reference/output.npy", mmap_mode="r")
        q_all = q_all.reshape(-1, q_all.shape[-1])
        b_all = b_all.reshape(-1, b_all.shape[-1])
        assert list(q_all.shape) == p["shape"], (name, q_all.shape, p["shape"])
        idx_all, ptop_all = saved[f"{name}__indices"], saved[f"{name}__logits"]
        plse_all, ptarget = saved[f"{name}__logsumexp"], saved[f"{name}__target_logits"]
        targets = np.asarray(list(p["input_ids"][1:]) + [-1], dtype=np.int64)
        kls = []
        for s in range(0, q_all.shape[0], CH):
            q = np.asarray(q_all[s:s + CH], dtype=np.float32)
            b = np.asarray(b_all[s:s + CH], dtype=np.float32)
            idx, ptop, plse = idx_all[s:s + CH], ptop_all[s:s + CH], plse_all[s:s + CH]
            qlse = lse(q)
            qtop = np.take_along_axis(q, idx, axis=-1)
            pp = np.exp(ptop - plse[:, None]); qp = np.exp(qtop - qlse[:, None])
            ptail = np.maximum(0., 1. - pp.sum(-1)); qtail = np.maximum(0., 1. - qp.sum(-1))
            kl = (pp * ((ptop - plse[:, None]) - (qtop - qlse[:, None]))).sum(-1)
            kl += np.where(ptail > 0, ptail * (np.log(np.maximum(ptail, 1e-45)) - np.log(np.maximum(qtail, 1e-45))), 0.)
            q5 = np.argsort(-q, axis=-1, kind="stable")[:, :5]
            overlap = (idx[:, :5, None] == q5[:, None, :]).any(-1).sum(-1) / 5
            # full-vocab KL(bf16 || fp32)
            blse = lse(b)
            lb = b - blse[:, None]; lq = q - qlse[:, None]
            fk = (np.exp(lb) * (lb - lq)).sum(-1)
            for o in range(len(q)):
                pos = s + o
                r = {"prompt": short, "kl": float(kl[o]), "top1": bool(idx[o, 0] == q5[o, 0]),
                     "top5": float(overlap[o]), "full_kl": float(fk[o])}
                t = int(targets[pos])
                if t >= 0:
                    r["nll"] = float(-(q[o, t] - qlse[o]) + (ptarget[pos] - plse[o]))
                rows.append(r)
                kls.append(float(kl[o]))
        per_prompt[short] = (len(kls), float(np.mean(kls)), float(np.max(kls)))

v = lambda k: np.asarray([r[k] for r in rows if k in r], dtype=np.float64)
summary = {"positions": len(rows),
           "mean_projected_kl": v("kl").mean(), "p99_projected_kl": float(np.quantile(v("kl"), .99)),
           "max_projected_kl": v("kl").max(),
           "top1_agreement": v("top1").mean(), "top5_overlap": v("top5").mean(),
           "mean_nll_delta": v("nll").mean(), "mean_full_kl_bf16_vs_fp32": v("full_kl").mean(),
           "p99_full_kl": float(np.quantile(v("full_kl"), .99))}
for k, x in summary.items():
    print(f"{k}: {x:.5f}" if isinstance(x, float) else f"{k}: {x}")
for k, (n, m, mx) in per_prompt.items():
    print(f"  {k:22s} n={n:4d} mean_proj_kl={m:.5f} max={mx:.4f}")
