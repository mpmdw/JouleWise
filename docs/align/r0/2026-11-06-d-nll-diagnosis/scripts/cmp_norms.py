import sys, numpy as np
sys.path.insert(0, "/private/tmp/jwd8diag/scripts")
from st_remote import tensor, index
D = ("mlx-community/Qwen3.8-27B-8bit", "815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9")
U = ("Qwen/Qwen3.8-27B", "8c0b3d30f3ae96f5c7f774de704bf0ada83e422a")
di, ui = index(*D), index(*U)
print("upstream keys sample", [k for k in ui if "layers.0." in k][:40])
pairs = []
for L in (0, 3, 30, 63):
    for suf in ("input_layernorm.weight", "post_attention_layernorm.weight", "linear_attn.norm.weight",
                "self_attn.q_norm.weight", "self_attn.k_norm.weight", "linear_attn.A_log", "linear_attn.dt_bias", "linear_attn.conv1d.weight"):
        dk = f"language_model.model.layers.{L}.{suf}"; uk = f"model.language_model.layers.{L}.{suf}"
        if dk in di and uk in ui: pairs.append((dk, uk))
pairs.append(("language_model.model.norm.weight", "model.language_model.norm.weight"))
for dk, uk in pairs:
    d = tensor(*D, di, dk); u = tensor(*U, ui, uk)
    if d.shape != u.shape:
        print(dk, "shape", d.shape, u.shape); 
        if d.size == u.size: d = d.reshape(u.shape) if "conv1d" not in dk else np.moveaxis(d, 2, 1)
        else: continue
    print(f"{dk:70s} D mean {d.mean():+.4f}  U mean {u.mean():+.4f}  max|D-U| {np.abs(d-u).max():.4g}  max|D-(U+1)| {np.abs(d-u-1).max():.4g}")
