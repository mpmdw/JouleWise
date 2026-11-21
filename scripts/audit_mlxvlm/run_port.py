"""Our port's side of the mlx-vlm audit: run the Sol port (pinned mlx 0.31.2 /
mlx-lm 0.31.3) on the same real-layout tiny checkpoints written by ref_gen.py.

Usage: python run_port.py WORKDIR PORT_CLONE
"""
import json
import sys
from pathlib import Path

import numpy as np

STEPS = 3
NEXT = [5, 6, 7]


def main(work, clone):
    sys.path.insert(0, str(clone))
    import mlx.core as mx
    from scripts.align_convert_qwen4_exp import convert, sha256, load_verified_model
    work = Path(work)
    for d in sorted(p for p in work.iterdir() if p.is_dir() and (p / "ref.npz").exists()):
        dtype = d.name.split("_")[1]
        out = d / "port_mlx"
        if not out.exists():
            convert(d / "hf", out, dtype, 32, dtype)
        model, _ = load_verified_model(out, sha256(out / "manifest.json"))
        model.eval()
        ref = np.load(d / "ref.npz")
        ids = ref["ids"].astype(np.int32)
        L = len(ids)
        x = mx.array(ids[None])

        def f(v):
            mx.eval(v)
            return np.array(v.astype(mx.float32))

        r = {"prefill": f(model(x))}
        cache, steps = model.make_cache(), []
        for i in range(L):
            steps.append(f(model(x[:, i:i + 1], cache=cache)))
        r["stepwise"] = np.concatenate(steps, 1)
        cache, chunks = model.make_cache(), []
        P = L // 2 + 1
        chunks.append(f(model(x[:, :P], cache=cache)))
        for s in range(P, L, 4):
            chunks.append(f(model(x[:, s:s + 4], cache=cache)))
        r["chunked"] = np.concatenate(chunks, 1)
        mask = ref["padded_mask"].astype(bool)
        batch = np.zeros(mask.shape, dtype=np.int32)
        for b in range(mask.shape[0]):
            pad = int((~mask[b]).sum())
            batch[b, pad:] = ids[:L - pad]
        cache = model.make_cache()
        r["padded_batch"] = f(model(mx.array(batch), cache=cache, attention_mask=mx.array(mask)))
        cont = []
        for t in range(STEPS):
            cont.append(f(model(mx.full((mask.shape[0], 1), NEXT[t], dtype=mx.int32), cache=cache)))
        r["padded_continuation"] = np.concatenate(cont, 1)
        for b in range(mask.shape[0]):
            n = int(mask[b].sum())
            r[f"single_row{b}"] = f(model(mx.array(np.array([list(ids[:n]) + NEXT], dtype=np.int32))))
        np.savez(d / "port.npz", **r)
        print(json.dumps(dict(case=d.name, mlx=mx.__version__)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
