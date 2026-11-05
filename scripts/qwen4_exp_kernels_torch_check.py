#!/usr/bin/env python3
"""Cross-check joulewise/align/models/qwen4_exp_kernels.py against the official
transformers qwen4_exp reference, with real per-layer dimensions where they fit.

Two venvs, two steps (the pinned MLX venv has no torch, and the reference venv
has no mlx):

  # 1. reference (transformers 5.22.1 + torch, CPU, fp32): writes inputs/outputs
  /private/tmp/jwsol/venv-ref/bin/python scripts/qwen4_exp_kernels_torch_check.py gen OUT.npz
  # 2. MLX kernels on the same inputs: compares and exits non-zero on failure
  /private/tmp/jwsol/venv-mlx/bin/python scripts/qwen4_exp_kernels_torch_check.py check OUT.npz

Cases:
  gdn_layer   Qwen4ExpTextGatedDeltaNet at real dims (hidden 2560, 16/48 heads,
              128/128), random weights, T=48, no cache (HF chunked path),
              compared with the kernel composition. The HF recurrent rule is
              also run with an initial state, against gated_delta.
  qsa_indexer Qwen4ExpTextQSAIndexer at real indexer dims (4 x 128, hidden
              2560) with budget 64 (16 blocks), so selection is sparse at
              T=160. Masks are compared modulo exact top-k ties.
  moe_block   Qwen4ExpTextSparseMoeBlock (64 experts, top-10, 1 shared,
              hidden 256, moe/shared intermediate 64): router semantics, fused
              gate_up order, shared expert.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".engine" / "hf-flashnext" / "config.json"


def _text_config(**over):
    cfg = json.loads(CONFIG.read_text())["text_config"]
    cfg.update(over)
    cfg.pop("mtp", None)
    if "num_hidden_layers" in over:
        cfg["layer_types"] = cfg["layer_types"][: over["num_hidden_layers"]]
    return cfg


def gen(out: Path) -> None:
    import numpy as np
    import torch
    from transformers.models.qwen4_exp import modeling_qwen4_exp as M
    from transformers.models.qwen4_exp.configuration_qwen4_exp import Qwen4ExpTextConfig

    torch.set_num_threads(2)
    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    arrays = {}

    def put(name, t):
        arrays[name] = t.detach().to(torch.float32).cpu().numpy() if isinstance(t, torch.Tensor) else np.asarray(t)

    # ---- Gated DeltaNet layer at real dims -------------------------------
    cfg = Qwen4ExpTextConfig(**_text_config(num_hidden_layers=4, ple_layer_ids=None))
    gdn = M.Qwen4ExpTextGatedDeltaNet(cfg, layer_idx=0).float()
    with torch.no_grad():
        for name, p in gdn.named_parameters():
            if name == "A_log":
                p.copy_(torch.log(torch.empty_like(p).uniform_(0.01, 16)))
            elif name == "dt_bias":
                p.copy_(torch.randn_like(p) * 0.5)
            elif name == "norm.weight":
                p.copy_(1 + 0.1 * torch.randn_like(p))
            elif name == "conv1d.weight":
                p.copy_(torch.randn_like(p) * 0.3)
            else:
                p.copy_(torch.randn_like(p) * p.shape[-1] ** -0.5)
        x = torch.randn(1, 48, cfg.hidden_size)
        y = gdn(x)
    for name, p in gdn.named_parameters():
        put(f"gdn.{name}", p)
    put("gdn.x", x)
    put("gdn.y", y)

    # Recurrent rule with an initial state (decode path), real head dims.
    B, T, Hk, Hv, D = 1, 5, 16, 48, 128
    q, k = torch.randn(B, T, Hk, D), torch.randn(B, T, Hk, D)
    v = torch.randn(B, T, Hv, D)
    a, b = torch.randn(B, T, Hv), torch.randn(B, T, Hv)
    A_log, dt_bias = torch.log(torch.empty(Hv).uniform_(0.01, 16)), torch.randn(Hv)
    s0 = torch.randn(B, Hv, D, D) * 0.1
    beta = b.sigmoid()
    g = -A_log.exp() * torch.nn.functional.softplus(a + dt_bias)
    qr, kr = q.repeat_interleave(Hv // Hk, dim=2), k.repeat_interleave(Hv // Hk, dim=2)
    yr, sr = M.torch_recurrent_gated_delta_rule(
        qr, kr, v, g=g, beta=beta, initial_state=s0, output_final_state=True, use_qk_l2norm_in_kernel=True
    )
    yc, sc = M.torch_chunk_gated_delta_rule(
        qr, kr, v, g=g, beta=beta, initial_state=s0, output_final_state=True, use_qk_l2norm_in_kernel=True
    )
    for n_, t_ in dict(q=q, k=k, v=v, a=a, b=b, A_log=A_log, dt_bias=dt_bias, s0=s0, yr=yr, sr=sr, yc=yc, sc=sc).items():
        put(f"rec.{n_}", t_)

    # ---- QSA indexer at real indexer dims, budget 64 -----------------------
    cfgq = Qwen4ExpTextConfig(**_text_config(num_hidden_layers=4, ple_layer_ids=None, indexer_budget=64))
    idxr = M.Qwen4ExpTextQSAIndexer(cfgq, layer_idx=3).float()
    with torch.no_grad():
        idxr.index_qk_proj.weight.copy_(torch.randn_like(idxr.index_qk_proj.weight) * cfgq.hidden_size**-0.5)
        idxr.q_layernorm.weight.copy_(0.1 * torch.randn(cfgq.indexer_head_dim))
        idxr.k_layernorm.weight.copy_(0.1 * torch.randn(cfgq.indexer_head_dim))
        Tq = 160
        hq = torch.randn(2, Tq, cfgq.hidden_size)
        rot = M.Qwen4ExpTextRotaryEmbedding(cfgq)
        pos = torch.arange(Tq).view(1, 1, -1).expand(3, 2, -1)
        cos, sin = rot(hq, pos)
        causal = torch.ones(Tq, Tq, dtype=torch.bool).tril()[None, None].expand(2, 1, Tq, Tq)
        mask = idxr(hq, (cos, sin), causal, None)
    put("qsa.w", idxr.index_qk_proj.weight)
    put("qsa.qn", idxr.q_layernorm.weight)
    put("qsa.kn", idxr.k_layernorm.weight)
    put("qsa.x", hq)
    arrays["qsa.mask"] = mask.cpu().numpy()
    arrays["qsa.budget"] = np.array(64)

    # ---- MoE block --------------------------------------------------------
    cfgm = Qwen4ExpTextConfig(
        **_text_config(num_hidden_layers=4, ple_layer_ids=None, hidden_size=256, num_experts=64,
                       moe_intermediate_size=64, shared_expert_intermediate_size=64)
    )
    moe = M.Qwen4ExpTextSparseMoeBlock(cfgm).float()
    with torch.no_grad():
        moe.gate.weight.copy_(torch.randn_like(moe.gate.weight))
        moe.experts.gate_up_proj.copy_(torch.randn_like(moe.experts.gate_up_proj) * 256**-0.5)
        moe.experts.down_proj.copy_(torch.randn_like(moe.experts.down_proj) * 64**-0.5)
        for p in moe.shared_expert.parameters():
            p.copy_(torch.randn_like(p) * p.shape[-1] ** -0.5)
        moe.shared_expert_gate.weight.copy_(torch.randn_like(moe.shared_expert_gate.weight) * 0.1)
        xm = torch.randn(1, 37, 256)
        ym = moe(xm)
    put("moe.router", moe.gate.weight)
    put("moe.gate_up", moe.experts.gate_up_proj)
    put("moe.down", moe.experts.down_proj)
    put("moe.s_gate", moe.shared_expert.gate_proj.weight)
    put("moe.s_up", moe.shared_expert.up_proj.weight)
    put("moe.s_down", moe.shared_expert.down_proj.weight)
    put("moe.s_gate_w", moe.shared_expert_gate.weight)
    put("moe.x", xm)
    put("moe.y", ym)
    arrays["meta.rng"] = np.array(rng.integers(0, 1))
    np.savez(out, **arrays)
    print(f"wrote {out} ({len(arrays)} arrays)")


def check(path: Path) -> int:
    import mlx.core as mx
    import mlx.nn as nn
    import numpy as np

    sys.path.insert(0, str(ROOT))
    from joulewise.align.models import qwen4_exp_kernels as K

    z = np.load(path)
    A = {k: mx.array(z[k]) for k in z.files}
    tc = _text_config()
    ok = True

    def report(name, got, ref, tol):
        nonlocal ok
        err = mx.abs(got.astype(mx.float32) - ref.astype(mx.float32)).max().item()
        scale = mx.abs(ref).max().item()
        status = "PASS" if err <= tol else "FAIL"
        ok &= err <= tol
        print(f"{status} {name}: max|diff| = {err:.3e} (max|ref| = {scale:.3e}, tol {tol:.0e})")

    # ---- GDN layer ----
    Hk, Hv = tc["linear_num_key_heads"], tc["linear_num_value_heads"]
    Dk, Dv = tc["linear_key_head_dim"], tc["linear_value_head_dim"]
    key_dim, value_dim = Hk * Dk, Hv * Dv
    x = A["gdn.x"]
    B, T, _ = x.shape
    qkv = x @ A["gdn.in_proj_qkv.weight"].T
    z_ = (x @ A["gdn.in_proj_z.weight"].T).reshape(B, T, Hv, Dv)
    b = x @ A["gdn.in_proj_b.weight"].T
    a = x @ A["gdn.in_proj_a.weight"].T
    conv, _ = K.depthwise_causal_conv1d(qkv, A["gdn.conv1d.weight"][:, 0, :])
    conv = nn.silu(conv)
    q = conv[..., :key_dim].reshape(B, T, Hk, Dk)
    k = conv[..., key_dim : 2 * key_dim].reshape(B, T, Hk, Dk)
    v = conv[..., 2 * key_dim :].reshape(B, T, Hv, Dv)
    y, _ = K.gated_delta(q, k, v, a, b, A["gdn.A_log"], A["gdn.dt_bias"])
    o = K.rms_norm_gated(y, z_, A["gdn.norm.weight"], tc["rms_norm_eps"])
    out = o.reshape(B, T, -1) @ A["gdn.out_proj.weight"].T
    report("gdn_layer (HF chunked prefill vs MLX kernel), fp32", out, A["gdn.y"], 2e-5)
    # The mlx-lm qwen3_next normalization (eps 1.28e-4) for contrast.
    yn, _ = K.gated_delta_native_mlx_lm(q, k, v, a, b, A["gdn.A_log"], A["gdn.dt_bias"])
    on = K.rms_norm_gated(yn.astype(mx.float32), z_, A["gdn.norm.weight"], tc["rms_norm_eps"])
    err_native = mx.abs(on.reshape(B, T, -1) @ A["gdn.out_proj.weight"].T - A["gdn.y"]).max().item()
    print(f"INFO gdn_layer with mlx-lm qwen3_next normalization: max|diff| = {err_native:.3e}")

    # ---- recurrent rule with initial state ----
    yk, sk = K.gated_delta(
        A["rec.q"], A["rec.k"], A["rec.v"], A["rec.a"], A["rec.b"], A["rec.A_log"], A["rec.dt_bias"],
        K.gdn_state_from_hf(A["rec.s0"]),
    )
    report("gated_delta vs HF recurrent (y)", yk, A["rec.yr"], 2e-5)
    report("gated_delta vs HF recurrent (state)", K.gdn_state_to_hf(sk), A["rec.sr"], 2e-5)
    report("gated_delta vs HF chunked (y)", yk, A["rec.yc"], 2e-5)

    # ---- QSA indexer ----
    cfg = K.QSAConfig.from_text_config({**tc, "indexer_budget": int(z["qsa.budget"])})
    xq = A["qsa.x"]
    qk = xq @ A["qsa.w"].T
    iq, raw = K.qsa_split_qk(qk, A["qsa.qn"], cfg)
    Tq = raw.shape[1]
    nb = Tq // cfg.compress_ratio
    bk = K.qsa_block_keys(raw[:, : nb * cfg.compress_ratio], A["qsa.kn"], cfg)
    mask = K.qsa_prefill_mask(iq, bk, 0, cfg)
    ref = mx.array(z["qsa.mask"])
    diff = mask != ref
    n_diff = int(diff.sum().item())
    if n_diff:
        # Every differing token must sit in a block tied with the K-th score.
        _, scores = K.qsa_reference_mask(iq, raw, A["qsa.kn"], cfg, return_scores=True)
        bad = 0
        for bi in range(diff.shape[0]):
            for qi in range(diff.shape[2]):
                row = diff[bi, 0, qi]
                if not row.any().item():
                    continue
                sc = scores[bi][qi]
                kth = mx.sort(sc)[-cfg.block_topk].item()
                for t in [t for t in range(Tq) if row[t].item()]:
                    if abs(sc[t // cfg.compress_ratio].item() - kth) > 1e-6:
                        bad += 1
        status = "PASS" if bad == 0 else "FAIL"
        ok &= bad == 0
        print(f"{status} qsa_indexer mask: {n_diff} differing entries, all on exact K-th ties: {bad == 0}")
    else:
        print(f"PASS qsa_indexer mask: identical to HF ({int(ref.sum().item())} selected entries, sparse rows from T>{cfg.dense_limit})")

    # ---- MoE block ----
    gate_up, down = A["moe.gate_up"], A["moe.down"]
    sgu = mx.concatenate([A["moe.s_gate"], A["moe.s_up"]], axis=0)
    xm = A["moe.x"]
    experts = K.FusedSwitchGLU(gate_up, down)
    ysplit = K.moe_block_split(xm, A["moe.router"], experts, K.DenseGLU(sgu, A["moe.s_down"]), A["moe.s_gate_w"], 10)
    report("moe_block split (HF structure)", ysplit, A["moe.y"], 2e-5)
    fgu, fdn = K.fold_shared_expert(gate_up, down, sgu, A["moe.s_down"])
    yfold = K.moe_block_folded(
        xm, mx.concatenate([A["moe.router"], A["moe.s_gate_w"]]), K.FusedSwitchGLU(fgu, fdn), 10, gate_up.shape[0]
    )
    report("moe_block folded shared expert", yfold, A["moe.y"], 2e-5)
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    mode, path = sys.argv[1], Path(sys.argv[2])
    if mode == "gen":
        gen(path)
    elif mode == "check":
        raise SystemExit(check(path))
    else:
        raise SystemExit(f"unknown mode {mode}")
