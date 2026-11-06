"""T3 (P2): Gated DeltaNet long-context drift in bf16.

Layer 0 of config B (2 key heads, 6 value heads) on identical bf16 inputs,
T = 8192 tokens fed in 512-token chunks through each implementation's cache.
Truth = transformers reference in fp32 on the same (bf16-representable)
weights and inputs. Error of each bf16 implementation vs truth is measured on
the recurrent state (relative Frobenius) at T = 512, 2048, 8192 and on the
layer output per 512-token window. Growth with T beyond the reference's own
bf16 error would indicate a defect.

Modes (each in its own venv):
  ref   WORK   (torch/transformers; writes t3/ref_fp32.npz, t3/ref_bf16.npz, t3/x.npy)
  vlm   WORK   (mlx-vlm; writes t3/vlm_bf16.npz, t3/vlm_fp32.npz, t3/vlmP2_bf16.npz)
  port  WORK CLONE  (Sol port, pinned mlx; writes t3/port_bf16.npz)
  cmp   WORK
"""
import json
import sys
from pathlib import Path

import numpy as np

T, CHUNK, MARKS = 8192, 512, (512, 2048, 8192)


def ref(work):
    import torch
    from transformers import Qwen4ExpForConditionalGeneration, DynamicCache
    torch.set_num_threads(2)
    d = Path(work) / "t3"
    d.mkdir(exist_ok=True)
    rng = np.random.default_rng(3)
    x = torch.tensor(rng.normal(size=(1, T, 64)), dtype=torch.bfloat16)
    np.save(d / "x.npy", x.float().numpy())
    for dt in ("fp32", "bf16"):
        m = Qwen4ExpForConditionalGeneration.from_pretrained(
            Path(work) / "B_bf16" / "hf", dtype=torch.float32 if dt == "fp32" else torch.bfloat16).eval()
        lm = m.model.language_model
        layer = lm.layers[0].linear_attn
        cache = DynamicCache(config=lm.config)
        outs, states = [], {}
        with torch.inference_mode():
            for s in range(0, T, CHUNK):
                o = layer(x[:, s:s + CHUNK].to(layer.out_proj.weight.dtype), cache_params=cache)
                outs.append(o.float().numpy())
                if s + CHUNK in MARKS:
                    # clone: the cache updates its fp32 state in place. Reference
                    # layout is [B, Hv, Dk, Dv]; stored as MLX's [B, Hv, Dv, Dk].
                    states[f"state{s + CHUNK}"] = cache.get_recurrent_state(0).float().clone().transpose(-1, -2).numpy()
        np.savez(d / f"ref_{dt}.npz", out=np.concatenate(outs, 1), **states)


def vlm(work):
    import mlx.core as mx
    from mlx_vlm.utils import load_model
    from mlx_vlm.models.cache import ArraysCache
    d = Path(work) / "t3"
    x = np.load(d / "x.npy")

    def run(case, name):
        lm = load_model(Path(work) / case / "vlm_hf_fused").language_model
        layer = lm.model.layers[0].linear_attn
        dtype = layer.out_proj.weight.dtype
        c = ArraysCache(size=2)
        outs, states = [], {}
        for s in range(0, T, CHUNK):
            o = layer(mx.array(x[:, s:s + CHUNK]).astype(dtype), mask=None, cache=c)
            mx.eval(o, c[1])
            outs.append(np.array(o.astype(mx.float32)))
            if s + CHUNK in MARKS:
                states[f"state{s + CHUNK}"] = np.array(c[1].astype(mx.float32))
        np.savez(d / f"{name}.npz", out=np.concatenate(outs, 1), **states)

    run("B_bf16", "vlm_bf16")
    # P2 fix draft: fp32 softplus(a + dt_bias) and fp32 q/k L2 norm.
    sys.path.insert(0, str(Path(__file__).parent))
    import p2_patch
    p2_patch.apply()
    run("B_bf16", "vlmP2_bf16")


def port(work, clone):
    sys.path.insert(0, str(clone))
    import mlx.core as mx
    from scripts.align_convert_qwen4_exp import sha256, load_verified_model
    d = Path(work) / "t3"
    x = np.load(d / "x.npy")
    out = Path(work) / "B_bf16" / "port_mlx"
    model, _ = load_verified_model(out, sha256(out / "manifest.json"))
    layer = model.model.layers[0].linear_attn
    c = model.make_cache()[0]
    outs, states = [], {}
    mask = mx.ones((1, CHUNK), dtype=mx.bool_)
    for s in range(0, T, CHUNK):
        o = layer(mx.array(x[:, s:s + CHUNK]).astype(mx.bfloat16), mask, c)
        c.advance(CHUNK)
        mx.eval(o, c[1])
        outs.append(np.array(o.astype(mx.float32)))
        if s + CHUNK in MARKS:
            states[f"state{s + CHUNK}"] = np.array(c[1].astype(mx.float32))
    np.savez(d / "port_bf16.npz", out=np.concatenate(outs, 1), **states)


def cmp(work):
    d = Path(work) / "t3"
    truth = np.load(d / "ref_fp32.npz")
    rows = {}
    for name in ("ref_bf16", "vlm_bf16", "vlmP2_bf16", "port_bf16"):
        if not (d / f"{name}.npz").exists():
            continue
        r = np.load(d / f"{name}.npz")
        st = {m: float(np.linalg.norm(r[f"state{m}"] - truth[f"state{m}"]) / np.linalg.norm(truth[f"state{m}"]))
              for m in MARKS}
        o, t = r["out"][0], truth["out"][0]
        win = [float(np.abs(o[s:s + CHUNK] - t[s:s + CHUNK]).max() / np.sqrt((t[s:s + CHUNK] ** 2).mean()))
               for s in range(0, T, CHUNK)]
        rows[name] = dict(state_rel_frob=st, out_maxabs_over_rms_first=win[0], out_maxabs_over_rms_last=win[-1],
                          out_maxabs_over_rms_max=max(win))
    print(json.dumps(rows, indent=1))
    (d / "t3.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "ref":
        ref(sys.argv[2])
    elif mode == "vlm":
        vlm(sys.argv[2])
    elif mode == "port":
        port(sys.argv[2], sys.argv[3])
    else:
        cmp(sys.argv[2])
