"""Dequantize D (mlx affine 8-bit, gs 64) linear weights via range reads and compare to upstream bf16."""
import sys, numpy as np
sys.path.insert(0, "/private/tmp/jwd8diag/scripts")
from st_remote import tensor, index
D = ("mlx-community/Qwen3.8-27B-8bit", "815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9")
U = ("Qwen/Qwen3.8-27B", "8c0b3d30f3ae96f5c7f774de704bf0ada83e422a")
di, ui = index(*D), index(*U)
def deq(prefix):
    w = tensor(*D, di, prefix + ".weight"); s = tensor(*D, di, prefix + ".scales"); b = tensor(*D, di, prefix + ".biases")
    q = w.view(np.uint8).reshape(w.shape[0], -1).astype(np.float32)  # little endian: low byte first
    g = q.reshape(q.shape[0], -1, 64)
    return (g * s[..., None] + b[..., None]).reshape(q.shape[0], -1)
mods = sys.argv[1:] or ["layers.0.linear_attn.in_proj_qkv", "layers.0.linear_attn.in_proj_z", "layers.0.linear_attn.in_proj_a",
        "layers.0.linear_attn.in_proj_b", "layers.0.linear_attn.out_proj", "layers.3.self_attn.q_proj", "layers.3.self_attn.k_proj",
        "layers.3.self_attn.v_proj", "layers.3.self_attn.o_proj", "layers.0.mlp.down_proj"]
for m in mods:
    d = deq("language_model.model." + m); u = tensor(*U, ui, "model.language_model." + m + ".weight")
    if d.shape != u.shape: print(m, "SHAPE", d.shape, u.shape); continue
    err = np.linalg.norm(d - u) / np.linalg.norm(u)
    # per-row relative error, to localise any permuted / corrupted block
    rr = np.linalg.norm(d - u, axis=1) / (np.linalg.norm(u, axis=1) + 1e-12)
    print(f"{m:40s} shape {d.shape} rel_err {err:.4f} row_rel_err max {rr.max():.4f} p99 {np.quantile(rr,0.99):.4f}", flush=True)
