"""Reverse direction: fp32 chain as the reference (top-64 + OTHER), bf16 chain
as the variant, same projected-KL formula. Plus the worst positions of the
bf16-reference direction. Read-only."""
import json
import sys
import numpy as np

ref_json, head_dir = sys.argv[1], sys.argv[2]
man = json.load(open(ref_json))
K = 64


def lse(x):
    m = np.max(x, axis=-1, keepdims=True)
    return m[..., 0] + np.log(np.exp(x - m).sum(axis=-1))


def proj_kl(p, q):
    """KL(p || q) on p's top-64 + OTHER, p,q logits [n, V]."""
    idx = np.argsort(-p, axis=-1, kind="stable")[:, :K]
    plse, qlse = lse(p), lse(q)
    ptop = np.take_along_axis(p, idx, -1); qtop = np.take_along_axis(q, idx, -1)
    pp = np.exp(ptop - plse[:, None]); qp = np.exp(qtop - qlse[:, None])
    pt = np.maximum(0., 1 - pp.sum(-1)); qt = np.maximum(0., 1 - qp.sum(-1))
    kl = (pp * ((ptop - plse[:, None]) - (qtop - qlse[:, None]))).sum(-1)
    kl += np.where(pt > 0, pt * (np.log(np.maximum(pt, 1e-45)) - np.log(np.maximum(qt, 1e-45))), 0.)
    top1 = idx[:, 0] == np.argmax(q, -1)
    gap = np.sort(pp, -1)[:, ::-1]
    return kl, top1, pp[:, 0], (gap[:, 0] - gap[:, 1])


allkl, alltop1, worst = [], [], []
names = []
for p in man["prompts"]:
    name = p["name"]
    f = np.load(f"{head_dir}/{name}-fp32-real/reference/output.npy", mmap_mode="r")
    b = np.load(f"{head_dir}/{name}-bf16-real/reference/output.npy", mmap_mode="r")
    f = f.reshape(-1, f.shape[-1]); b = b.reshape(-1, b.shape[-1])
    for s in range(0, f.shape[0], 64):
        F = np.asarray(f[s:s + 64], np.float32); B = np.asarray(b[s:s + 64], np.float32)
        kl, t1, _, _ = proj_kl(F, B)
        allkl.append(kl); alltop1.append(t1)
        kl2, _, pmax, gap = proj_kl(B, F)
        for o in np.argsort(-kl2)[:2]:
            worst.append((float(kl2[o]), name, s + int(o), float(pmax[o]), float(gap[o])))
kl = np.concatenate(allkl); t1 = np.concatenate(alltop1)
print(f"fp32-referenced: n={kl.size} mean_proj_kl={kl.mean():.5f} median={np.median(kl):.5f} "
      f"p99={np.quantile(kl, .99):.4f} max={kl.max():.3f} top1={t1.mean():.4f}")
worst.sort(reverse=True)
print("worst bf16-referenced positions (kl, prompt, pos, bf16 top-1 prob, bf16 top1-top2 gap):")
for w in worst[:8]:
    print("  %.3f %s pos=%d ptop=%.3f gap=%.3f" % w)
