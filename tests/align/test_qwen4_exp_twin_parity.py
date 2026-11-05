"""Gold parity test: JouleWise MLX port of ``qwen4_exp`` vs the official reference.

The unittest driver (stdlib only) orchestrates three stages in the two pinned
environments and asserts on the numbers they report:

1. ``ref``  (venv-ref: torch 2.15.0 + transformers 5.22.1). Build a tiny
   random ``Qwen4ExpForConditionalGeneration`` with every text layer type
   (GatedDeltaNet, QSA with an indexer that actually sparsifies, PLE n-gram
   layers at two ``ple_layer_index`` values, hyper-connections, MoE + shared
   expert), ``save_pretrained`` it in many small shards (experts and n-gram
   parts straddle shards) plus a fake ``mtp.*`` shard, and record reference
   logits from the pinned authority copy
   ``.engine/transformers-qwen4_exp/modeling_qwen4_exp.py``.
2. ``scripts/align_convert_qwen4_exp_twin.py`` (venv-mlx) converts the
   checkpoint three ways: fp32, bf16, and mixed (q4 experts / q8 dense / q8
   n-gram table); four single-component quantized variants for error
   attribution; and a re-run of the mixed recipe from a staged copy whose
   shards are deleted as they are consumed (must be byte-identical).
3. ``mlx`` (venv-mlx: mlx 0.31.2 + mlx-lm 0.31.3) loads each conversion with
   ``mlx_lm.utils.load_model`` (the ``model_file`` path) and runs: full
   prefill and cached stepwise decode (fp32, bf16), a left-padded batch with
   decode, batch-1 vs left-padded, KV trim + re-prefill vs fresh, DeltaNet
   snapshot/restore, query-chunked attention, ``mlx_lm.generate_step``
   greedy decoding with chunked prefill, ``sanitize()`` on raw HF tensors,
   and quantized vs unquantized.

Every assertion bound is stated in ``TOL`` with its rationale. The reference
also computes two ablations (indexer made dense; n-gram table zeroed) to show
the fp32 tolerance is orders of magnitude below what a missing QSA indexer or
PLE path would produce.

Resource rules (shared laptop): every process runs under ``nice -n 10`` with
2 threads and ``TMPDIR=/private/tmp/jwtwin-tmp``; each stage reports its peak
RSS. Set ``JW_SKIP_TWIN_PARITY=1`` to skip; the test also skips when either
venv is missing (e.g. on the measurement Mac).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ENGINE_MODELING = REPO / ".engine" / "transformers-qwen4_exp" / "modeling_qwen4_exp.py"
CONVERTER = REPO / "scripts" / "align_convert_qwen4_exp_twin.py"
VENV_REF = Path(os.environ.get("JW_TWIN_VENV_REF", "/private/tmp/jwsol/venv-ref")) / "bin" / "python"
VENV_MLX = Path(os.environ.get("JW_TWIN_VENV_MLX", "/private/tmp/jwsol/venv-mlx")) / "bin" / "python"
TMP_ROOT = Path(os.environ.get("JW_TWIN_TMPDIR", "/private/tmp/jwtwin-tmp"))
RSS_LIMIT_BYTES = 2 * 1024 ** 3

EOS = 1
TINY_TEXT_CONFIG = {
    "vocab_size": 256, "hidden_size": 64, "num_hidden_layers": 8,
    "num_attention_heads": 4, "num_key_value_heads": 2, "head_dim": 64,
    "linear_num_key_heads": 2, "linear_num_value_heads": 4,
    "linear_key_head_dim": 32, "linear_value_head_dim": 32, "linear_conv_kernel_dim": 4,
    "moe_intermediate_size": 64, "shared_expert_intermediate_size": 64,
    "num_experts": 8, "num_experts_per_tok": 3,
    "hc_count": 4, "hc_lowrank": 32,
    "ple_layer_ids": [2, 5], "ple_embed_dim": 64, "ple_conv_kernel_size": 4,
    "ngram_size": 3, "heads_per_ngram": 2, "ngram_vocab_size_base": 101,
    "make_ngram_vocab_size_divisible_by": 8, "split_ngram_parts": 4,
    "indexer_n_heads": 4, "indexer_kv_heads": 1, "indexer_head_dim": 32,
    "indexer_budget": 8, "indexer_compress_ratio": 4,
    "output_gate_type": "sigmoid", "eos_token_id": EOS, "bos_token_id": EOS,
    "rms_norm_eps": 1e-6, "full_attention_interval": 4,
    "rope_parameters": {"mrope_interleaved": True, "mrope_section": [4, 2, 2],
                        "partial_rotary_factor": 0.25, "rope_theta": 10000000,
                        "rope_type": "default"},
    # The released config spells QSA layers "full_attention".
    "layer_types": ["linear_attention"] * 3 + ["full_attention"]
                   + ["linear_attention"] * 3 + ["full_attention"],
}
TINY_VISION_CONFIG = {
    "depth": 1, "hidden_size": 16, "intermediate_size": 32, "num_heads": 2,
    "out_hidden_size": 64, "patch_size": 16, "spatial_merge_size": 2,
    "temporal_patch_size": 2, "num_position_embeddings": 16,
}

# Scenario geometry (QSA: ratio 4, budget 8 -> top-2 blocks; a 37-token
# prompt has up to 9 complete blocks, so most queries are sparse).
LEN_A, LEN_B, PREFIX, PAD_B, N_EXT = 37, 29, 20, 8, 4
TRIM_A, TRIM_B, TRIM_C = 18, 13, 11

N_GREEDY, GREEDY_PREFILL_STEP = 8, 16

# Tolerances on max |logit diff| (logit scale ~3.6-4.3 is reported per row).
# * fp32: both engines in fp32; residual differences are kernel reorderings
#   (recurrent vs chunked DeltaNet, fused SDPA, fp32 conv accumulation).
# * bf16: there is no exact bf16 target -- the reference's own bf16 run is
#   itself ~0.29 from its fp32 run. Criterion: MLX-bf16 must be no further
#   from the fp32 reference than the reference's bf16 run is (max and RMS),
#   and within 1.5x that noise floor of the reference's bf16 run.
# * quantized: q4 experts + q8 dense + q8 n-gram vs the unquantized bf16 port.
TOL = {
    "fp32_vs_ref": 2e-4,
    "mlx_internal_fp32": 1e-4,
    "bf16_vs_ref_bf16_over_noise": 1.5,
    "bf16_vs_ref_fp32_over_noise": 1.0,
    "quant_vs_unquant_rel": 0.15,
    "quant_top1_min": 0.85,
}


def _env():
    env = dict(os.environ)
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    env.update({"OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2", "VECLIB_MAXIMUM_THREADS": "2",
                "OPENBLAS_NUM_THREADS": "2", "TOKENIZERS_PARALLELISM": "false",
                "TMPDIR": str(TMP_ROOT), "PYTHONPATH": str(REPO),
                "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"})
    return env


def _run(python: Path, *args: str, timeout: int = 1800) -> str:
    cmd = ["nice", "-n", "10", str(python), *args]
    proc = subprocess.run(cmd, cwd=str(REPO), env=_env(), capture_output=True, text=True,
                          timeout=timeout)
    if proc.returncode:
        raise RuntimeError(f"stage failed ({proc.returncode}): {' '.join(cmd)}\n"
                           f"--- stdout ---\n{proc.stdout[-4000:]}\n--- stderr ---\n{proc.stderr[-8000:]}")
    return proc.stdout


def _peak_rss() -> int:
    import resource
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)


# ===========================================================================
# Stage 1: reference (venv-ref)
# ===========================================================================


def _load_engine_module():
    """Import the pinned authority copy inside the installed transformers
    package namespace so its relative imports resolve."""
    import importlib.util
    import transformers.models.qwen4_exp  # noqa: F401  (package must exist)

    name = "transformers.models.qwen4_exp.modeling_qwen4_exp_engine_pin"
    spec = importlib.util.spec_from_file_location(name, ENGINE_MODELING)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _randomize(model, torch, seed: int):
    """Every float parameter gets a nonzero random value (zero-initialised
    pieces such as PLE convs and norm offsets would otherwise go untested)."""
    gen = torch.Generator().manual_seed(seed)

    def normal(shape, std):
        return torch.randn(*shape, generator=gen) * std

    with torch.no_grad():
        for name, p in model.named_parameters():
            if not p.is_floating_point():
                continue
            shape = tuple(p.shape)
            if "visual" in name:
                v = normal(shape, 0.02)
            elif name.endswith("A_log"):
                v = torch.log(torch.rand(*shape, generator=gen) * 15 + 1)
            elif name.endswith("dt_bias"):
                v = torch.rand(*shape, generator=gen) + 0.5
            elif name.endswith("linear_attn.norm.weight"):
                v = 1 + normal(shape, 0.2)
            elif p.ndim == 1:                       # (1 + w) RMSNorms
                v = normal(shape, 0.2)
            elif "conv1d" in name:
                v = normal(shape, 0.3)
            elif "ngram_embedding" in name or "embed_tokens" in name:
                v = normal(shape, 1.0)
            elif name.endswith("mlp.gate.weight"):
                v = normal(shape, 3.0 / shape[-1] ** 0.5)
            elif name.endswith("lm_head.weight"):
                v = normal(shape, 2.0 / shape[-1] ** 0.5)
            else:
                v = normal(shape, 1.0 / shape[-1] ** 0.5)
            p.copy_(v.to(p.dtype))


def _tokens(seed: int, n: int, eos_at=()):
    import random
    rng = random.Random(seed)
    ids = [rng.randrange(2, TINY_TEXT_CONFIG["vocab_size"]) for _ in range(n)]
    for i in eos_at:
        ids[i] = EOS
    return ids


def _write_pins(ckpt: Path, shards):
    """Pins in the lane's source-pins schema (repos.<name>.files[])."""
    import hashlib
    files = []
    for name in shards:
        data = (ckpt / name).read_bytes()
        files.append({"path": name, "sha256": hashlib.sha256(data).hexdigest(),
                      "size_bytes": len(data)})
    (ckpt.parent / "pins.json").write_text(json.dumps({"repos": {"tiny": {"files": files}}}))


def _write_fused_expert_checkpoint(src: Path, dst: Path, config) -> Path:
    """Re-save the checkpoint with experts fused as ``mlp.experts.gate_up_proj``
    [E, 2I, H] (gate rows first) and ``mlp.experts.down_proj`` [E, H, I]: the
    layout of the released Flash-Next shards."""
    import re
    import torch
    from safetensors.torch import load_file, save_file

    dst.mkdir(parents=True, exist_ok=True)
    tensors = {}
    for f in sorted(src.glob("*.safetensors")):
        tensors.update(load_file(str(f)))
    pat = re.compile(r"^(.*\.mlp\.experts)\.(\d+)\.(gate_proj|up_proj|down_proj)\.weight$")
    experts, rest = {}, {}
    for k, v in tensors.items():
        m = pat.match(k)
        if m:
            experts.setdefault(m.group(1), {}).setdefault(m.group(3), {})[int(m.group(2))] = v
        else:
            rest[k] = v
    for head, projs in experts.items():
        n = len(projs["gate_proj"])
        rest[f"{head}.gate_up_proj"] = torch.stack(
            [torch.cat([projs["gate_proj"][e], projs["up_proj"][e]], dim=0) for e in range(n)])
        rest[f"{head}.down_proj"] = torch.stack([projs["down_proj"][e] for e in range(n)])
    keys = sorted(rest)
    weight_map, half = {}, len(keys) // 2
    for i, part in enumerate((keys[:half], keys[half:])):
        name = f"model-{i + 1:05d}-of-00002.safetensors"
        save_file({k: rest[k].contiguous() for k in part}, str(dst / name), metadata={"format": "pt"})
        weight_map.update({k: name for k in part})
    total = sum(v.numel() * v.element_size() for v in rest.values())
    (dst / "model.safetensors.index.json").write_text(json.dumps(
        {"metadata": {"total_size": total}, "weight_map": weight_map}))
    config.save_pretrained(dst)
    return dst


def _engine_text_model(engine, full, text_cfg):
    """The engine copy's text decoder + lm_head, loaded with ``full``'s weights."""
    m = engine.Qwen4ExpForCausalLM(text_cfg).eval()
    sd = {}
    for k, v in full.state_dict().items():
        if k.startswith("model.language_model."):
            sd["model." + k[len("model.language_model."):]] = v
        elif k.startswith("lm_head."):
            sd[k] = v
    missing, unexpected = m.load_state_dict(sd, strict=False)
    real_missing = [k for k in missing if "rotary_emb" not in k]
    if real_missing or unexpected:
        raise RuntimeError(f"engine load: missing={real_missing} unexpected={unexpected}")
    return m


def stage_ref(work: Path):
    import numpy as np
    import torch
    from safetensors.torch import save_file
    from transformers import Qwen4ExpConfig, Qwen4ExpForConditionalGeneration

    torch.set_num_threads(2)
    torch.manual_seed(0)
    work.mkdir(parents=True, exist_ok=True)
    engine = _load_engine_module()

    cfg = Qwen4ExpConfig(text_config=dict(TINY_TEXT_CONFIG), vision_config=dict(TINY_VISION_CONFIG))
    cfg._attn_implementation = "sdpa"
    cfg.text_config._attn_implementation = "sdpa"
    full = Qwen4ExpForConditionalGeneration(cfg).eval()
    _randomize(full, torch, seed=1234)

    ckpt = work / "hf_ckpt"
    full.save_pretrained(ckpt, max_shard_size="40KB")
    # A fake MTP head in its own shard: the converter must drop it.
    save_file({"mtp.layers.0.eh_proj.weight": torch.randn(64, 128)},
              str(ckpt / "model-mtp-00001.safetensors"), metadata={"format": "pt"})
    index_path = ckpt / "model.safetensors.index.json"
    index = json.loads(index_path.read_text())
    index["weight_map"]["mtp.layers.0.eh_proj.weight"] = "model-mtp-00001.safetensors"
    index_path.write_text(json.dumps(index, indent=2))
    shards = sorted(set(index["weight_map"].values()))
    _write_pins(ckpt, shards)
    fused_dir = _write_fused_expert_checkpoint(ckpt, work / "hf_ckpt_fused", full.config)

    # Authority model: the engine copy's text decoder + lm_head, same weights.
    tcfg = full.config.text_config
    tcfg._attn_implementation = "sdpa"

    def engine_model(text_cfg):
        return _engine_text_model(engine, full, text_cfg)

    ref = engine_model(tcfg)
    seq_a = _tokens(7, LEN_A, eos_at=(5, 21))
    seq_b = _tokens(8, LEN_B, eos_at=(11,))
    ext_a = _tokens(9, N_EXT)
    ext_b = _tokens(10, N_EXT, eos_at=(1,))
    trim_c = _tokens(11, TRIM_C, eos_at=(4,))
    out = {}

    def logits(model, ids, **kw):
        with torch.no_grad():
            return model(input_ids=torch.tensor(ids), use_cache=True, **kw)

    def prefill(model, ids):
        return logits(model, [ids]).logits[0].float().numpy()

    def stepwise(model, ids, prefix):
        res = logits(model, [ids[:prefix]])
        pkv, rows = res.past_key_values, [res.logits[0].float()]
        for t in ids[prefix:]:
            res = logits(model, [[t]], past_key_values=pkv)
            pkv = res.past_key_values
            rows.append(res.logits[0].float())
        return torch.cat(rows).numpy()

    out["prefill_fp32"] = prefill(ref, seq_a)
    out["stepwise_fp32"] = stepwise(ref, seq_a, PREFIX)
    # bf16 reference from a FRESH copy (casting ``ref`` down and back up would
    # silently round the fp32 reference weights used below).
    ref_bf16 = engine_model(tcfg).to(torch.bfloat16)
    out["prefill_bf16"] = prefill(ref_bf16, seq_a)
    out["stepwise_bf16"] = stepwise(ref_bf16, seq_a, PREFIX)
    del ref_bf16

    # Left-padded batch (padding-aware positions, as generate() builds them),
    # continued for N_EXT decode steps; plus the unpadded single-row run.
    pad_b = [EOS] * PAD_B + seq_b
    mask = torch.tensor([[1] * LEN_A, [0] * PAD_B + [1] * LEN_B])
    pos = (mask.cumsum(-1) - 1).clamp_min(0)
    res = logits(ref, [seq_a, pad_b], attention_mask=mask, position_ids=pos)
    pkv, rows = res.past_key_values, [res.logits.float()]
    for i in range(N_EXT):
        mask = torch.cat([mask, torch.ones(2, 1, dtype=mask.dtype)], dim=1)
        step_pos = pos[:, -1:] + 1 + i
        res = logits(ref, [[ext_a[i]], [ext_b[i]]], past_key_values=pkv,
                     attention_mask=mask, position_ids=step_pos)
        pkv = res.past_key_values
        rows.append(res.logits.float())
    out["padded_fp32"] = torch.cat(rows, dim=1).numpy()
    out["single_b_fp32"] = stepwise(ref, seq_b + ext_b, LEN_B)
    out["trim_fresh_fp32"] = prefill(ref, seq_a[:TRIM_A] + trim_c)

    # Greedy continuation (for the end-to-end mlx_lm.generate_step check).
    res = logits(ref, [seq_a])
    pkv, greedy, greedy_rows = res.past_key_values, [], []
    nxt = int(res.logits[0, -1].argmax())
    for _ in range(N_GREEDY):
        greedy.append(nxt)
        res = logits(ref, [[nxt]], past_key_values=pkv)
        pkv = res.past_key_values
        greedy_rows.append(res.logits[0, -1].float())
        nxt = int(res.logits[0, -1].argmax())
    out["greedy_logits_fp32"] = torch.stack(greedy_rows).numpy()

    # Ablations: prove the test is sensitive to QSA sparsity and to PLE.
    dense_cfg = Qwen4ExpConfig(text_config=dict(TINY_TEXT_CONFIG, indexer_budget=4096),
                               vision_config=dict(TINY_VISION_CONFIG)).text_config
    dense_cfg._attn_implementation = "sdpa"
    out["ablate_dense_fp32"] = prefill(engine_model(dense_cfg), seq_a)
    nople = engine_model(tcfg)
    with torch.no_grad():
        for name, p in nople.named_parameters():
            if "ngram_embedding" in name:
                p.zero_()
    out["ablate_nople_fp32"] = prefill(nople, seq_a)

    # Sanity: the installed transformers class agrees with the pinned copy,
    # and both checkpoint layouts (per-expert as saved, fused gate_up as in
    # the released checkpoint) load to the same logits in the reference.
    with torch.no_grad():
        installed = full(input_ids=torch.tensor([seq_a])).logits[0].float().numpy()
        layout_diff = {}
        for name, path in (("per_expert", ckpt), ("fused", fused_dir)):
            loaded = Qwen4ExpForConditionalGeneration.from_pretrained(
                path, attn_implementation="sdpa").eval()
            got = loaded(input_ids=torch.tensor([seq_a])).logits[0].float().numpy()
            layout_diff[name] = float(np.abs(got - installed).max())
            del loaded
    np.savez(work / "ref.npz", **out)
    meta = {
        "seq_a": seq_a, "seq_b": seq_b, "ext_a": ext_a, "ext_b": ext_b, "trim_c": trim_c,
        "greedy_tokens_fp32": greedy,
        "engine_vs_installed_max_abs": float(np.abs(installed - out["prefill_fp32"]).max()),
        "reference_reload_max_abs": layout_diff,
        "n_source_shards": len(shards),
        "torch": torch.__version__,
        "transformers": __import__("transformers").__version__,
        "peak_rss_bytes": _peak_rss(),
    }
    (work / "ref_meta.json").write_text(json.dumps(meta, indent=2))


# ===========================================================================
# Stage 3: MLX (venv-mlx)
# ===========================================================================


def _diff(a, b, scale_ref=None):
    import numpy as np
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch {a.shape} vs {b.shape}")
    d = np.abs(a - b)
    scale = float(np.abs(b if scale_ref is None else scale_ref).max())
    return {"max_abs": float(d.max()), "mean_abs": float(d.mean()),
            "rms": float(np.sqrt((d ** 2).mean())), "logit_scale": scale,
            "rel": float(d.max() / scale) if scale else 0.0,
            "top1_agree": float((a.argmax(-1) == b.argmax(-1)).mean()), "n": int(d.size)}


def stage_mlx(work: Path):
    import mlx.core as mx
    import numpy as np
    from mlx_lm.utils import load_model

    ref = dict(np.load(work / "ref.npz"))
    meta = json.loads((work / "ref_meta.json").read_text())
    seq_a, seq_b = meta["seq_a"], meta["seq_b"]
    ext_a, ext_b, trim_c = meta["ext_a"], meta["ext_b"], meta["trim_c"]
    res = {}

    def run(model, ids, cache=None):
        out = model(mx.array(ids), cache=cache)
        mx.eval(out)
        return np.array(out.astype(mx.float32))

    def prefill(model, ids):
        return run(model, [ids])[0]

    def stepwise(model, ids, prefix):
        cache = model.make_cache()
        rows = [run(model, [ids[:prefix]], cache)[0]]
        for t in ids[prefix:]:
            rows.append(run(model, [[t]], cache)[0])
        return np.concatenate(rows)

    fp32, _ = load_model(work / "mlx_fp32")
    bf16, _ = load_model(work / "mlx_bf16")
    quant, qcfg = load_model(work / "mlx_q")
    res["ref_bf16_vs_ref_fp32_noise"] = _diff(ref["prefill_bf16"], ref["prefill_fp32"])
    res["ref_bf16_vs_ref_fp32_noise_stepwise"] = _diff(ref["stepwise_bf16"], ref["stepwise_fp32"])

    # --- vs reference --------------------------------------------------------
    mlx_prefill = prefill(fp32, seq_a)
    res["prefill_fp32_vs_ref"] = _diff(mlx_prefill, ref["prefill_fp32"])
    mlx_step = stepwise(fp32, seq_a, PREFIX)
    res["stepwise_fp32_vs_ref"] = _diff(mlx_step, ref["stepwise_fp32"])
    res["prefill_bf16_vs_ref_bf16"] = _diff(prefill(bf16, seq_a), ref["prefill_bf16"])
    bf16_step = stepwise(bf16, seq_a, PREFIX)
    res["stepwise_bf16_vs_ref_bf16"] = _diff(bf16_step, ref["stepwise_bf16"])
    res["prefill_bf16_vs_ref_fp32"] = _diff(prefill(bf16, seq_a), ref["prefill_fp32"])
    res["stepwise_bf16_vs_ref_fp32"] = _diff(bf16_step, ref["stepwise_fp32"])

    # End to end through mlx-lm's own generation loop (chunked prefill of
    # GREEDY_PREFILL_STEP tokens, cache-state evals, argmax sampling).
    from mlx_lm.generate import generate_step
    toks, lps = [], []
    for (tok, logprobs), _ in zip(generate_step(mx.array(seq_a), fp32, max_tokens=N_GREEDY,
                                                prefill_step_size=GREEDY_PREFILL_STEP),
                                  range(N_GREEDY)):
        toks.append(int(tok))
        lps.append(np.array(logprobs.astype(mx.float32)))
    ref_greedy = ref["greedy_logits_fp32"]
    ref_lp = ref_greedy - np.log(np.exp(ref_greedy - ref_greedy.max(-1, keepdims=True)).sum(
        -1, keepdims=True)) - ref_greedy.max(-1, keepdims=True)
    res["generate_step_greedy"] = {
        "tokens": toks, "ref_tokens": meta["greedy_tokens_fp32"],
        "tokens_equal": toks == meta["greedy_tokens_fp32"],
        # logprobs at step i score the token after greedy token i
        "logprob_max_abs": float(np.abs(np.stack(lps[1:]) - ref_lp[:-1]).max()),
    }

    # Left-padded batch vs reference, and batch-1 vs left-padded (MLX only).
    cache = fp32.make_cache(left_padding=[0, PAD_B])
    rows = [run(fp32, [seq_a, [EOS] * PAD_B + seq_b], cache)]
    for i in range(N_EXT):
        rows.append(run(fp32, [[ext_a[i]], [ext_b[i]]], cache))
    padded = np.concatenate(rows, axis=1)
    ref_pad = ref["padded_fp32"]
    res["padded_row0_fp32_vs_ref"] = _diff(padded[0], ref_pad[0])
    res["padded_row1_fp32_vs_ref"] = _diff(padded[1, PAD_B:], ref_pad[1, PAD_B:])
    single_b = stepwise(fp32, seq_b + ext_b, LEN_B)
    res["batch1_vs_leftpadded_fp32"] = _diff(padded[1, PAD_B:], single_b)
    # Short batch: <= budget complete blocks, so QSA takes its dense path
    # (padded prefill and padded decode), still matching batch-1 runs.
    short_a, short_b, pad_s = seq_a[:10], seq_b[:7], 3
    cache = fp32.make_cache(left_padding=[0, pad_s])
    rows = [run(fp32, [short_a, [EOS] * pad_s + short_b], cache)]
    for i in range(2):
        rows.append(run(fp32, [[ext_a[i]], [ext_b[i]]], cache))
    short_pad = np.concatenate(rows, axis=1)
    res["batch1_vs_leftpadded_dense_fp32"] = {
        "row0": _diff(short_pad[0], stepwise(fp32, short_a + ext_a[:2], len(short_a))),
        "row1": _diff(short_pad[1, pad_s:], stepwise(fp32, short_b + ext_b[:2], len(short_b))),
    }
    res["single_b_fp32_vs_ref"] = _diff(single_b, ref["single_b_fp32"])

    # --- MLX-internal invariants ---------------------------------------------
    res["mlx_prefill_vs_stepwise_fp32"] = _diff(mlx_step, mlx_prefill)
    # Query-chunked attention (bounds the head_dim-256 SDPA fallback) is exact
    # up to kernel reordering: force tiny chunks on both the sparse (array
    # mask) and the padded path.
    attn_cls = type(next(l for l in fp32.layers if not l.is_linear).self_attn)
    default_chunk = attn_cls.query_chunk
    short_unchunked = prefill(fp32, seq_a[:11])     # <= budget: dense "causal" path
    attn_cls.query_chunk = 5
    try:
        res["query_chunked_vs_unchunked_fp32"] = _diff(prefill(fp32, seq_a), mlx_prefill)
        res["query_chunked_dense_vs_unchunked_fp32"] = _diff(prefill(fp32, seq_a[:11]),
                                                             short_unchunked)
        cache = fp32.make_cache(left_padding=[0, PAD_B])
        chunked_pad = run(fp32, [seq_a, [EOS] * PAD_B + seq_b], cache)
        res["query_chunked_padded_vs_ref"] = _diff(chunked_pad[1, PAD_B:],
                                                   ref_pad[1, PAD_B:LEN_A])
    finally:
        attn_cls.query_chunk = default_chunk

    # KV trim + re-prefill == fresh. A then B, restore to A (QSA KV trimmed by
    # len(B), DeltaNet/PLE states restored), then C; vs fresh A then C.
    A, B, C = seq_a[:TRIM_A], seq_a[TRIM_A:TRIM_A + TRIM_B], trim_c
    cache = fp32.make_cache()
    run(fp32, [A], cache)
    snap = fp32.snapshot_cache(cache)
    run(fp32, [B], cache)
    fp32.restore_cache(cache, snap)
    offsets = sorted({c.offset for c in cache if hasattr(c, "offset")})
    trimmed = run(fp32, [C], cache)[0]
    fresh_cache = fp32.make_cache()
    run(fp32, [A], fresh_cache)
    fresh_two_call = run(fp32, [C], fresh_cache)[0]
    res["trim_reprefill_vs_fresh_exact"] = _diff(trimmed, fresh_two_call)
    res["trim_reprefill_vs_fresh_exact"]["offsets_after_restore"] = offsets
    res["trim_reprefill_vs_fresh_one_call"] = _diff(trimmed, prefill(fp32, A + C)[TRIM_A:])
    res["trim_reprefill_vs_ref"] = _diff(trimmed, ref["trim_fresh_fp32"][TRIM_A:])

    # DeltaNet recurrent-state snapshot / restore exactness.
    cache = fp32.make_cache()
    run(fp32, [seq_a[:PREFIX]], cache)
    snap = fp32.snapshot_cache(cache)
    first = run(fp32, [seq_a[PREFIX:PREFIX + 10]], cache)
    states_1 = [np.array(c[1]) for c in cache if not hasattr(c, "offset")]
    fp32.restore_cache(cache, snap)
    restored = [np.array(c[1]) for c in cache if not hasattr(c, "offset")]
    snapped = [np.array(s[1][1]) for s in snap if s[0] == "arrays"]
    second = run(fp32, [seq_a[PREFIX:PREFIX + 10]], cache)
    states_2 = [np.array(c[1]) for c in cache if not hasattr(c, "offset")]
    res["deltanet_snapshot_restore"] = {
        "logits_bitwise_equal": bool(np.array_equal(first, second)),
        "state_after_restore_bitwise_equal": all(np.array_equal(a, b) for a, b in zip(restored, snapped)),
        "state_rerun_bitwise_equal": all(np.array_equal(a, b) for a, b in zip(states_1, states_2)),
        "max_abs": float(np.abs(first - second).max()),
        "n_recurrent_layers": len(states_1),
    }

    # sanitize() on raw HF tensors reproduces the converter's fp32 output.
    from mlx.utils import tree_flatten
    raw = {}
    for shard in sorted((work / "hf_ckpt").glob("*.safetensors")):
        raw.update(mx.load(str(shard)))
    sanitized = fp32.sanitize(raw)
    params = dict(tree_flatten(fp32.parameters()))
    res["sanitize_raw_hf"] = {
        "same_keys": sorted(sanitized) == sorted(params),
        "bitwise_equal": all(np.array_equal(np.array(sanitized[k]), np.array(params[k]))
                             for k in params if k in sanitized),
        "n_params": len(params),
    }

    # Converting the fused-expert layout yields the same MLX weights.
    def load_weights(d):
        w = {}
        for f in sorted((work / d).glob("model-*.safetensors")):
            w.update(mx.load(str(f)))
        return w
    wa, wb = load_weights("mlx_q"), load_weights("mlx_q_fused")
    res["fused_vs_per_expert_conversion"] = {
        "same_keys": sorted(wa) == sorted(wb),
        "bitwise_equal": all(bool(mx.array_equal(wa[k], wb[k]).item()) for k in wa if k in wb),
        "n_tensors": len(wa),
    }

    # --- quantization ---------------------------------------------------------
    q_prefill = prefill(quant, seq_a)
    bf_prefill = prefill(bf16, seq_a)
    res["quant_vs_unquant_bf16"] = _diff(q_prefill, bf_prefill)
    res["quant_vs_ref_fp32"] = _diff(q_prefill, ref["prefill_fp32"])
    # Attribution: one quantized component at a time vs unquantized bf16.
    for name in ("mlx_q_experts4", "mlx_q_dense8", "mlx_q_ngram8", "mlx_q_ngram4"):
        model, _ = load_model(work / name)
        res[f"attr_{name}_vs_unquant_bf16"] = _diff(prefill(model, seq_a), bf_prefill)
        del model
    q_step = stepwise(quant, seq_a, PREFIX)
    res["quant_stepwise_vs_quant_prefill"] = _diff(q_step, q_prefill)
    q = qcfg.get("quantization", {})
    res["quant_config"] = {"default_bits": q.get("bits"), "group_size": q.get("group_size"),
                           "n_overrides": sum(1 for v in q.values() if isinstance(v, dict))}

    # --- sensitivity: the comparison would catch a missing indexer / PLE ------
    res["sensitivity_ref_dense_vs_ref"] = _diff(ref["ablate_dense_fp32"], ref["prefill_fp32"])
    res["sensitivity_ref_nople_vs_ref"] = _diff(ref["ablate_nople_fp32"], ref["prefill_fp32"])
    attn = [l.self_attn.indexer for l in fp32.layers if not l.is_linear]
    mx.eval(fp32(mx.array([seq_a])))
    res["qsa_last_prefill_stats"] = [vars(ix._last_stats) for ix in attn]
    tables = fp32.ngram_tables()
    res["ngram"] = {str(k): {"lookups": t.lookups, "unique_rows": t.unique_rows,
                             "format": t.fmt, "io": t.io} for k, t in tables.items()}
    res["mlx_peak_rss_bytes"] = _peak_rss()
    res["mlx"] = mx.__version__
    (work / "mlx_results.json").write_text(json.dumps(res, indent=2))


# ===========================================================================
# Review regressions (2026-11-05 review of the port). Each probe reproduces a
# confirmed finding against the pinned reference, so reintroducing the bug
# fails here. Stages ``ref_regress`` (venv-ref) and ``mlx_regress``
# (venv-mlx); artifacts live under ``<work>/regress``.
# ===========================================================================

# Config validation: (TINY_TEXT_CONFIG overrides). The reference rejects every
# case except "valid"; the port must agree case by case.
REG_VALIDATION = {
    "valid": {},
    "experts_per_tok_0": {"num_experts_per_tok": 0},
    "experts_per_tok_gt_experts": {"num_experts_per_tok": 9},
    "experts_0": {"num_experts": 0},
    "moe_intermediate_0": {"moe_intermediate_size": 0},
    "shared_intermediate_0": {"shared_expert_intermediate_size": 0},
    "indexer_budget_0": {"indexer_budget": 0},
    "indexer_heads_0": {"indexer_n_heads": 0},
}


# Layer-level probes: a 2-layer text config (DeltaNet + QSA) whose single
# layer under test is built from the engine copy and from the port.
REG_LAYER_BASE = {
    "vocab_size": 64, "hidden_size": 64, "num_hidden_layers": 2,
    "num_attention_heads": 2, "num_key_value_heads": 1, "head_dim": 32,
    "linear_num_key_heads": 2, "linear_num_value_heads": 6,
    "linear_key_head_dim": 32, "linear_value_head_dim": 32, "linear_conv_kernel_dim": 4,
    "moe_intermediate_size": 16, "shared_expert_intermediate_size": 16,
    "num_experts": 4, "num_experts_per_tok": 2, "hc_count": 2, "hc_lowrank": 8,
    "ple_layer_ids": [], "indexer_n_heads": 2, "indexer_kv_heads": 1, "indexer_head_dim": 32,
    "indexer_budget": 8, "indexer_compress_ratio": 4, "output_gate_type": "sigmoid",
    "eos_token_id": EOS, "rms_norm_eps": 1e-6,
    "layer_types": ["linear_attention", "full_attention"],
}
# GatedDeltaNet with a cache, fed in segments (multi-token and single-token
# calls). Defaults: dtypes ("fp32",), devices ("gpu",).
REG_GDN = {
    # control at the released kernel size
    "k4_segments": {"over": {}, "segments": [2, 70, 1, 1, 64, 3, 1], "seed": 0},
    # kernel 1: zero-length conv history (the cache kept the whole sequence)
    "k1_segments": {"over": {"linear_conv_kernel_dim": 1}, "segments": [3, 1, 1, 4], "seed": 0},
    # key head dims that are not a multiple of 32 (the Metal kernel's simdgroup
    # split): 48 silently covered 32 of 48 dims, 16 failed to compile
    "dk48": {"over": {"linear_key_head_dim": 48}, "segments": [9, 1], "seed": 0,
             "devices": ("gpu", "cpu")},
    "dk16": {"over": {"linear_key_head_dim": 16}, "segments": [9, 1], "seed": 0,
             "devices": ("gpu", "cpu")},
}
# Released DeltaNet head geometry, fp32 and bf16 from the same weights: the
# bf16 fidelity probe for the conv activation's rounding.
GDN_REAL_DIMS = {"hidden_size": 256, "linear_num_key_heads": 16, "linear_num_value_heads": 48,
                 "linear_key_head_dim": 128, "linear_value_head_dim": 128}
for _seed in (1, 2, 3):
    REG_GDN[f"real_dims_s{_seed}"] = {"over": GDN_REAL_DIMS, "segments": [200, 1, 1, 1],
                                      "seed": _seed, "dtypes": ("fp32", "bf16")}
# QSA attention layer (indexer included) vs the engine copy, prefill + cached
# decode. "P" shifts every absolute RoPE position (queries, keys, block keys)
# to emulate a long context without a P-token prefill.
REG_QSA_REAL = {"head_dim": 256, "indexer_head_dim": 128, "num_attention_heads": 2,
                "num_key_value_heads": 1, "indexer_budget": 32}
REG_QSA = {
    "real_far_fp32": {"over": REG_QSA_REAL, "chunks": [300, 1, 1], "seed": 7, "P": 200000},
    "real_near_bf16": {"over": REG_QSA_REAL, "chunks": [300, 1, 1], "seed": 8, "P": 0,
                       "dtype": "bf16"},
    "real_far_bf16": {"over": REG_QSA_REAL, "chunks": [300, 1, 1], "seed": 8, "P": 250000,
                      "dtype": "bf16"},
    # Top-k ties. relu-zero block scores straddle the boundary on some rows
    # (seed 3: query 36 has two 0.0 blocks for one slot); and a degenerate
    # construction where many blocks score exactly the same.
    "ties_relu_zero": {"over": {"indexer_budget": 32}, "chunks": [300, 1, 1], "seed": 3},
    "ties_degenerate": {"over": {"indexer_budget": 16}, "chunks": [64, 1], "seed": 0,
                        "tie": "partial"},
}
# Router at the released expert geometry (512 experts, top-10) in bf16.
REG_ROUTER = {"hidden_size": 256, "num_experts": 512, "num_experts_per_tok": 10, "tokens": 64,
              "seed": 8}
# RoPE inverse frequencies: (rope_theta, rotary_dim). The first two (released
# config, test config) must be bit-identical; the rest are informational.
REG_ROPE_EXACT = [(10000000, 64), (10000000, 16)]
REG_ROPE_SWEEP = [(t, d) for t in (10000, 1000000, 10000000) for d in (16, 32, 64, 128, 256)]
REG_ROPE_POSITIONS = (0, 262144, 7)      # arange: the released max_position_embeddings
REG_TOL = {
    # rms(MLX bf16 - ref fp32) / rms(ref bf16 - ref fp32) for one DeltaNet layer
    # at the released head dims. Single-rounding silu measures 1.003-1.007;
    # the double-rounding nn.silu on bf16 measured 1.075-1.094.
    "gdn_bf16_rms_over_noise": 1.04,
    # Elementwise bf16 silu vs torch: the port's mismatches must stay below
    # half of stock nn.silu's (measured 508 vs 1844 on GPU, 252 vs 1296 CPU).
    "silu_mismatch_vs_stock": 0.5,
    # bf16 cos/sin over positions 0-262k vs the reference: fraction of entries
    # that differ (torch-identical inv_freq: 9e-6; mlx pow: 2.65e-2).
    "rope_bf16_mismatch_frac": 1e-4,
    # QSA layer in bf16 at position ~250k vs the same layer at position 0
    # (torch-identical inv_freq: 1.0x; mlx pow: 15x).
    "qsa_bf16_far_over_near": 2.0,
}


def _qsa_cfg(over):
    c = {"vocab_size": 64, "hidden_size": 64, "num_hidden_layers": 4,
         "num_attention_heads": 4, "num_key_value_heads": 2, "head_dim": 64,
         "linear_num_key_heads": 2, "linear_num_value_heads": 4,
         "linear_key_head_dim": 16, "linear_value_head_dim": 16,
         "moe_intermediate_size": 16, "shared_expert_intermediate_size": 16,
         "num_experts": 4, "num_experts_per_tok": 2, "hc_count": 2, "hc_lowrank": 8,
         "ple_layer_ids": [], "eos_token_id": EOS, "indexer_n_heads": 4, "indexer_kv_heads": 1,
         "indexer_head_dim": 32, "indexer_budget": 8, "indexer_compress_ratio": 4,
         "layer_types": ["linear_attention"] * 3 + ["full_attention"]}
    c.update(over)
    rot = int(c["head_dim"] * 0.25)
    c["rope_parameters"] = {"mrope_interleaved": True,
                            "mrope_section": {16: [4, 2, 2], 32: [8, 4, 4], 64: [11, 11, 10]}[rot],
                            "partial_rotary_factor": 0.25, "rope_theta": 10000000,
                            "rope_type": "default"}
    return c
# Tiny full model at the edges of the config space, converted like the main
# checkpoint. Reference logits are an UNCACHED prefill: with
# ple_conv_kernel_size 1 the reference's own cached PLE path raises.
# split_ngram_parts 28 over 424 padded rows: torch.chunk saves 27 pieces.
REG_EDGE_TEXT = dict(
    TINY_TEXT_CONFIG, num_hidden_layers=4, ple_layer_ids=[2],
    layer_types=["linear_attention"] * 3 + ["full_attention"],
    linear_conv_kernel_dim=1, ple_conv_kernel_size=1, split_ngram_parts=28)
REG_EDGE_CUTS = [0, 2, 3, 4, 9, 10, 11, 12, 18, 19, 20, 35, 36, 37, 38, 39, 40, 41]


def _ref_validation():
    from transformers.models.qwen4_exp.configuration_qwen4_exp import Qwen4ExpTextConfig
    out = {}
    for name, over in REG_VALIDATION.items():
        try:
            Qwen4ExpTextConfig(**dict(TINY_TEXT_CONFIG, **over))
            out[name] = None
        except Exception as exc:  # noqa: BLE001 -- recorded, compared case by case
            out[name] = f"{type(exc).__name__}: {exc}"
    return out


def _ref_gdn(engine, reg: Path):
    import copy

    import numpy as np
    import torch
    from transformers.cache_utils import DynamicCache
    from transformers.models.qwen4_exp.configuration_qwen4_exp import Qwen4ExpTextConfig

    for name, case in REG_GDN.items():
        cfgd = dict(REG_LAYER_BASE, **case["over"])
        cfg = Qwen4ExpTextConfig(**cfgd)
        layer = engine.Qwen4ExpTextGatedDeltaNet(cfg, 0).eval()
        gen = torch.Generator().manual_seed(case["seed"])
        with torch.no_grad():
            for n, p in layer.named_parameters():
                shape = tuple(p.shape)
                if n == "A_log":
                    v = torch.log(torch.rand(*shape, generator=gen) * 15 + 1)
                elif n == "dt_bias":
                    v = torch.rand(*shape, generator=gen) + 0.5
                elif n == "norm.weight":
                    v = 1 + torch.randn(*shape, generator=gen) * 0.2
                elif "conv1d" in n:
                    v = torch.randn(*shape, generator=gen) * 0.3
                else:
                    v = torch.randn(*shape, generator=gen) / shape[-1] ** 0.5
                p.copy_(v)
        segments = case["segments"]
        x = torch.randn(1, sum(segments), cfgd["hidden_size"], generator=gen)
        arrays = {"x": x.numpy(), "cfg": np.array(json.dumps(cfgd)), "segments": np.array(segments)}
        arrays.update({"w::" + n: p.detach().numpy().copy() for n, p in layer.named_parameters()})
        for dt_name in case.get("dtypes", ("fp32",)):
            dt = torch.bfloat16 if dt_name == "bf16" else torch.float32
            m = copy.deepcopy(layer).to(dt)
            cache = DynamicCache(config=cfg)
            off = 0
            with torch.no_grad():
                for i, s in enumerate(segments):
                    o = m(x[:, off:off + s].to(dt), cache_params=cache, attention_mask=None)
                    arrays[f"{dt_name}::out{i}"] = o.float().numpy()
                    off += s
        np.savez(reg / f"gdn_{name}.npz", **arrays)


def _ref_silu(reg: Path):
    """torch silu on every finite bf16 value with |x| < 50."""
    import numpy as np
    import torch

    f = (np.arange(0, 1 << 16, dtype=np.uint32) << 16).view(np.float32)
    f = f[np.isfinite(f) & (np.abs(f) < 50)]
    t = torch.from_numpy(f).to(torch.bfloat16)          # exact: f holds bf16 values
    np.savez(reg / "silu_ref.npz", x=t.float().numpy(),
             y=torch.nn.functional.silu(t).float().numpy())


def _ref_qsa(engine, reg: Path):
    import numpy as np
    import torch
    from transformers.cache_utils import DynamicCache
    from transformers.models.qwen4_exp.configuration_qwen4_exp import Qwen4ExpTextConfig

    for name, case in REG_QSA.items():
        cfgd = _qsa_cfg(case["over"])
        cfg = Qwen4ExpTextConfig(**cfgd)
        cfg._attn_implementation = "sdpa"
        att = engine.Qwen4ExpTextAttention(cfg, 3).eval()
        rot = engine.Qwen4ExpTextRotaryEmbedding(cfg)
        gen = torch.Generator().manual_seed(case["seed"])
        with torch.no_grad():
            for _, p in att.named_parameters():
                p.copy_(torch.randn(p.shape, generator=gen) * 0.2 if p.ndim == 1
                        else torch.randn(p.shape, generator=gen) / p.shape[-1] ** 0.5)
            if case.get("tie"):
                # Indexer q.k < 0 on every non-RoPE dim and 0 on the RoPE dims
                # -> relu-zero scores; "partial": head 0 random, so some blocks
                # score > 0 and the rest tie exactly.
                d, h, rd = cfgd["indexer_head_dim"], cfgd["indexer_n_heads"], int(cfgd["head_dim"] * 0.25)
                w = att.indexer.index_qk_proj.weight
                a = torch.randn(cfgd["hidden_size"], generator=gen)
                w.zero_()
                for head in range(h):
                    w[head * d + rd:(head + 1) * d] = -a / a.norm()
                w[h * d + rd:(h + 1) * d] = a / a.norm()
                att.indexer.q_layernorm.weight.zero_()
                att.indexer.k_layernorm.weight.zero_()
                if case["tie"] == "partial":
                    w[0:d] = torch.randn(d, cfgd["hidden_size"], generator=gen) / cfgd["hidden_size"] ** 0.5
        dt = torch.bfloat16 if case.get("dtype") == "bf16" else torch.float32
        att = att.to(dt)
        chunks, P = case["chunks"], case.get("P", 0)
        x_all = torch.randn(1, sum(chunks), cfgd["hidden_size"], generator=gen)
        if case.get("tie"):
            x_all = x_all + 3 * a / a.norm()
        x_all = x_all.to(dt)
        captured = {}
        indexer_forward = att.indexer.forward

        def hook(*a, _f=indexer_forward, **k):
            captured["sel"] = _f(*a, **k)
            return captured["sel"]

        att.indexer.forward = hook
        cache = DynamicCache(config=cfg)
        arrays = {"x": x_all.float().numpy(), "cfg": np.array(json.dumps(cfgd))}
        arrays.update({"w::" + k: v.float().numpy() for k, v in att.state_dict().items()})
        off = 0
        for i, s in enumerate(chunks):
            end = off + s
            mask = (torch.arange(end)[None, :] <= torch.arange(off, end)[:, None])[None, None]
            pos = torch.arange(end)[None, :] + P
            cos, sin = rot(x_all[:, off:end], pos[None].expand(3, -1, -1))
            with torch.no_grad():
                o, _ = att(x_all[:, off:end], (cos, sin), mask, past_key_values=cache)
            arrays[f"out{i}"] = o.float().numpy()
            arrays[f"sel{i}"] = (captured["sel"] & mask).numpy()[0, 0]          # (S, L)
            off = end
        np.savez(reg / f"qsa_{name}.npz", **arrays)


def _ref_router(engine, reg: Path):
    import numpy as np
    import torch
    from transformers.models.qwen4_exp.configuration_qwen4_exp import Qwen4ExpTextConfig

    c = REG_ROUTER
    cfg = Qwen4ExpTextConfig(**dict(REG_LAYER_BASE, hidden_size=c["hidden_size"],
                                    num_experts=c["num_experts"],
                                    num_experts_per_tok=c["num_experts_per_tok"]))
    router = engine.Qwen4ExpTextTopKRouter(cfg)
    gen = torch.Generator().manual_seed(c["seed"])
    with torch.no_grad():
        router.weight.copy_(torch.randn(c["num_experts"], c["hidden_size"], generator=gen)
                            * 3.0 / c["hidden_size"] ** 0.5)
    router = router.to(torch.bfloat16)
    x = torch.randn(c["tokens"], c["hidden_size"], generator=gen).to(torch.bfloat16)
    with torch.no_grad():
        logits, scores, idx = router(x)
    np.savez(reg / "router_ref.npz", x=x.float().numpy(), w=router.weight.detach().float().numpy(),
             logits=logits.float().numpy(), scores=scores.float().numpy(), idx=idx.numpy())


def _ref_topk_tie_order():
    """torch.topk on zero ties (one positive entry, k=2): which zero it keeps."""
    import torch

    s = torch.zeros(20)
    gen = torch.Generator().manual_seed(0)
    s[torch.randperm(20, generator=gen)[:1]] = torch.rand(1, generator=gen) + 0.1
    kept = sorted(i for i in s.topk(2).indices.tolist() if s[i] == 0)
    return {"scores": s.tolist(), "k": 2, "zero_kept": kept,
            "lowest_zero": [i for i in range(20) if s[i] == 0][:len(kept)]}


def _ref_rope(engine, reg: Path):
    import types

    import numpy as np
    import torch
    from transformers.models.qwen4_exp.configuration_qwen4_exp import Qwen4ExpTextConfig

    arrays = {}
    for theta, dim in REG_ROPE_EXACT + REG_ROPE_SWEEP:
        cfg = types.SimpleNamespace(
            rope_parameters={"rope_type": "default", "rope_theta": theta}, head_dim=dim,
            hidden_size=dim, num_attention_heads=1)
        inv, _ = engine.Qwen4ExpTextRotaryEmbedding.compute_default_rope_parameters(cfg)
        arrays[f"inv::{theta}::{dim}"] = inv.numpy()
    rot = engine.Qwen4ExpTextRotaryEmbedding(Qwen4ExpTextConfig(**_qsa_cfg(REG_QSA_REAL)))
    pos = torch.arange(*REG_ROPE_POSITIONS)
    cos, sin = rot(torch.zeros(1, 1, dtype=torch.bfloat16), pos[None, None].expand(3, 1, -1))
    arrays.update(pos=pos.numpy(), cos_bf16=cos[0].float().numpy(), sin_bf16=sin[0].float().numpy())
    np.savez(reg / "rope_ref.npz", **arrays)


def _ref_edge(engine, reg: Path):
    import numpy as np
    import torch
    from transformers import Qwen4ExpConfig, Qwen4ExpForConditionalGeneration

    cfg = Qwen4ExpConfig(text_config=dict(REG_EDGE_TEXT), vision_config=dict(TINY_VISION_CONFIG))
    cfg._attn_implementation = "sdpa"
    cfg.text_config._attn_implementation = "sdpa"
    full = Qwen4ExpForConditionalGeneration(cfg).eval()
    _randomize(full, torch, seed=99)
    full.save_pretrained(reg / "edge_ckpt", max_shard_size="30KB")
    tcfg = full.config.text_config
    tcfg._attn_implementation = "sdpa"
    ref = _engine_text_model(engine, full, tcfg)
    ids = _tokens(3, REG_EDGE_CUTS[-1], eos_at=(4, 17))
    with torch.no_grad():
        logits = ref(input_ids=torch.tensor([ids]), use_cache=False).logits[0].float().numpy()
        # The checkpoint as saved is valid for the reference itself.
        installed = full(input_ids=torch.tensor([ids]), use_cache=False).logits[0].float().numpy()
        reloaded = Qwen4ExpForConditionalGeneration.from_pretrained(
            reg / "edge_ckpt", attn_implementation="sdpa").eval()
        again = reloaded(input_ids=torch.tensor([ids]), use_cache=False).logits[0].float().numpy()
    np.savez(reg / "edge_ref.npz", logits=logits, ids=np.array(ids))
    weight_map = json.loads((reg / "edge_ckpt" / "model.safetensors.index.json").read_text())["weight_map"]
    return {"ngram_shards_saved": sum(".ngram_embedding.shard_" in k for k in weight_map),
            "split_ngram_parts": REG_EDGE_TEXT["split_ngram_parts"],
            "reference_reload_max_abs": float(np.abs(again - installed).max()),
            "engine_vs_installed_max_abs": float(np.abs(logits - installed).max())}


def stage_ref_regress(work: Path):
    import torch

    torch.set_num_threads(2)
    torch.manual_seed(0)
    reg = work / "regress"
    reg.mkdir(parents=True, exist_ok=True)
    engine = _load_engine_module()
    meta = {"validation": _ref_validation()}
    _ref_gdn(engine, reg)
    _ref_silu(reg)
    _ref_qsa(engine, reg)
    _ref_rope(engine, reg)
    _ref_router(engine, reg)
    meta["torch_topk_tie_order"] = _ref_topk_tie_order()
    meta["edge"] = _ref_edge(engine, reg)
    meta["peak_rss_bytes"] = _peak_rss()
    (reg / "ref_meta.json").write_text(json.dumps(meta, indent=2))


def _mlx_validation(tw):
    out = {}
    for name, over in REG_VALIDATION.items():
        try:
            tw.TextModelArgs.from_dict(dict(TINY_TEXT_CONFIG, **over))
            out[name] = None
        except ValueError as exc:
            out[name] = str(exc)
    return out


def _mlx_gdn(tw, reg: Path):
    """Run each REG_GDN case through the port's GatedDeltaNet with an
    ArraysCache, segment by segment, on each requested device."""
    import mlx.core as mx
    import numpy as np
    from mlx_lm.models.cache import ArraysCache

    dts = {"fp32": mx.float32, "bf16": mx.bfloat16}
    out, outs = {}, {}
    prev_device = mx.default_device()
    for name, case in REG_GDN.items():
        z = np.load(reg / f"gdn_{name}.npz")
        cfgd = json.loads(str(z["cfg"]))
        segments = [int(s) for s in z["segments"]]
        args = tw.TextModelArgs.from_dict(cfgd)
        for dt_name in case.get("dtypes", ("fp32",)):
            dt = dts[dt_name]
            for dev in case.get("devices", ("gpu",)):
                key = f"{name}/{dt_name}/{dev}"
                mx.set_default_device(mx.gpu if dev == "gpu" else mx.cpu)
                try:
                    layer = tw.GatedDeltaNet(args)
                    weights = []
                    for k in z.files:
                        if k.startswith("w::"):
                            a = z[k]
                            if k == "w::conv1d.weight":
                                a = np.moveaxis(a, 2, 1)        # torch (C, 1, K) -> (C, K, 1)
                            weights.append((k[3:], mx.array(a).astype(dt)))
                    layer.load_weights(weights, strict=True)
                    cache = ArraysCache(size=2)
                    x = mx.array(z["x"]).astype(dt)
                    inv = tw.rope_inv_freq(args)
                    off, seg_max, rows = 0, [], []
                    for i, s in enumerate(segments):
                        step = tw._Step(1, s, off, np.zeros((1,), np.int64), inv)
                        o = layer(x[:, off:off + s], step, cache)
                        mx.eval(o, cache[0], cache[1])
                        o = np.array(o.astype(mx.float32))
                        rows.append(o)
                        seg_max.append(float(np.abs(o - z[f"{dt_name}::out{i}"]).max()))
                        off += s
                    out[key] = {"seg_max_abs": seg_max, "max_abs": max(seg_max),
                                "ref_scale": float(max(np.abs(z[f"{dt_name}::out{i}"]).max()
                                                       for i in range(len(segments)))),
                                "conv_cache_len": int(cache[0].shape[1]),
                                "kernel": args.linear_conv_kernel_dim}
                    outs[key] = rows
                except Exception as exc:  # noqa: BLE001 -- a crash is a recorded failure
                    out[key] = {"error": f"{type(exc).__name__}: {str(exc)[:300]}"}
                finally:
                    mx.set_default_device(prev_device)
    return out, outs


def _mlx_gdn_bf16_noise(reg: Path, outs):
    """bf16 fidelity of the port relative to the reference's own bf16 noise."""
    import numpy as np

    def rms(a):
        return float(np.sqrt(np.mean(np.square(a.astype(np.float64)))))

    out = {}
    for name, case in REG_GDN.items():
        if "bf16" not in case.get("dtypes", ()):
            continue
        z = np.load(reg / f"gdn_{name}.npz")
        n = len(z["segments"])
        ref32 = np.concatenate([z[f"fp32::out{i}"].ravel() for i in range(n)])
        ref16 = np.concatenate([z[f"bf16::out{i}"].ravel() for i in range(n)])
        mlx16 = np.concatenate([o.ravel() for o in outs[f"{name}/bf16/gpu"]])
        out[name] = {"rms_ratio": rms(mlx16 - ref32) / rms(ref16 - ref32),
                     "max_ratio": float(np.abs(mlx16 - ref32).max() / np.abs(ref16 - ref32).max()),
                     "ref_bf16_noise_rms": rms(ref16 - ref32)}
    return out


def _mlx_silu(tw, reg: Path):
    import mlx.core as mx
    import mlx.nn as nn
    import numpy as np

    z = np.load(reg / "silu_ref.npz")
    x, y = mx.array(z["x"]).astype(mx.bfloat16), z["y"]
    out = {"n": int(y.size)}
    prev_device = mx.default_device()
    for dev in ("gpu", "cpu"):
        mx.set_default_device(mx.gpu if dev == "gpu" else mx.cpu)
        try:
            port = np.array(tw.silu_rounded_once(x).astype(mx.float32))
            stock = np.array(nn.silu(x).astype(mx.float32))
        finally:
            mx.set_default_device(prev_device)
        out[dev] = {"port_mismatch": int((port != y).sum()), "stock_mismatch": int((stock != y).sum())}
    return out


def _classify_mask_row(m_tw, m_ref, scores, t, r, k):
    """Compare one query row's token masks. Returns "same", "tie" (they differ
    only in complete blocks whose port score ties the k-th score, and the
    reference keeps exactly k blocks) or "other"; plus whether a tie
    straddles the top-k boundary on this row."""
    import numpy as np

    n_t = (t + 1) // r
    tied, boundary = set(), False
    if scores is not None and n_t > k:
        sc = scores[:n_t]
        kth = np.sort(sc)[::-1][k - 1]
        tol = 1e-5 * max(1.0, abs(float(kth)))
        is_tied = np.abs(sc - kth) <= tol
        above = int((sc > kth + tol).sum())
        boundary = bool(is_tied.sum() > 1 and above < k < above + is_tied.sum())
        tied = set(np.nonzero(is_tied)[0].tolist())
    diff = np.nonzero(m_tw != m_ref)[0]
    if diff.size == 0:
        return "same", boundary
    ref_blocks = int(m_ref[:n_t * r].reshape(n_t, r)[:, 0].sum()) if n_t else 0
    if diff.max() < n_t * r and set((diff // r).tolist()) <= tied and ref_blocks == min(k, n_t):
        return "tie", boundary
    return "other", boundary


def _mlx_qsa(tw, reg: Path):
    """Run each REG_QSA case through the port's QSAAttention + QSACache and
    compare outputs and per-query token masks with the reference, tie-aware:
    torch.topk's tie order is unspecified, so rows may legitimately keep a
    different one of several exactly tied blocks."""
    import mlx.core as mx
    import numpy as np

    out = {}
    orig_cos_sin, orig_mask = tw.rope_cos_sin, tw.QSAIndexer._mask
    captured = {}

    def mask_hook(self, iq, step, cache):
        captured["mask"] = orig_mask(self, iq, step, cache)
        return captured["mask"]

    tw.QSAIndexer._mask = mask_hook
    try:
        for name, case in REG_QSA.items():
            z = np.load(reg / f"qsa_{name}.npz")
            args = tw.TextModelArgs.from_dict(json.loads(str(z["cfg"])))
            dt = mx.bfloat16 if case.get("dtype") == "bf16" else mx.float32
            att = tw.QSAAttention(args)
            att.load_weights([(k[3:], mx.array(z[k]).astype(dt)) for k in z.files
                              if k.startswith("w::")], strict=True)
            att.indexer.record_selection = True                 # block scores, for ties
            P = case.get("P", 0)
            tw.rope_cos_sin = lambda pos, inv, _p=P: orig_cos_sin(pos + _p, inv)
            cache, inv = tw.QSACache(), tw.rope_inv_freq(args)
            x_all = mx.array(z["x"]).astype(dt)
            r, k = args.indexer_compress_ratio, args.block_topk
            kinds = {"same": 0, "tie": 0, "other": 0}
            off, n_rows, n_boundary, max_abs, max_abs_same = 0, 0, 0, 0.0, 0.0
            for i, s in enumerate(case["chunks"]):
                end = off + s
                step = tw._Step(1, s, off, np.zeros((1,), np.int64), inv)
                o = np.array(att(x_all[:, off:end], step, cache).astype(mx.float32))[0]
                m = captured["mask"]
                if m is None or isinstance(m, str):            # dense: plain causal
                    m = np.arange(end)[None, :] <= np.arange(off, end)[:, None]
                else:
                    m = np.array(m)[0, 0]
                sel = att.indexer._last_selection
                scores = None if sel is None else np.array(sel.scores)[0]
                d = np.abs(o - z[f"out{i}"][0]).max(axis=-1)    # (S,)
                for q in range(s):
                    kind, boundary = _classify_mask_row(m[q], z[f"sel{i}"][q],
                                                        None if scores is None else scores[q],
                                                        off + q, r, k)
                    kinds[kind] += 1
                    n_boundary += boundary
                    if kind == "same":
                        max_abs_same = max(max_abs_same, float(d[q]))
                n_rows += s
                max_abs = max(max_abs, float(d.max()))
                off = end
            out[name] = {"rows": n_rows, "mask_rows_mismatched": kinds["tie"] + kinds["other"],
                         "mask_rows_tie_only": kinds["tie"], "mask_rows_non_tie": kinds["other"],
                         "rows_with_boundary_tie": n_boundary, "max_abs": max_abs,
                         "max_abs_same_mask_rows": max_abs_same}
    finally:
        tw.rope_cos_sin, tw.QSAIndexer._mask = orig_cos_sin, orig_mask
    return out


def _mlx_router(tw, reg: Path):
    """Router selection vs the reference, tie-aware: every expert chosen by
    one engine and not the other must tie the k-th reference logit exactly."""
    import types

    import mlx.core as mx
    import numpy as np

    z = np.load(reg / "router_ref.npz")
    c = REG_ROUTER
    k = c["num_experts_per_tok"]
    blk = tw.SparseMoeBlock(types.SimpleNamespace(
        hidden_size=c["hidden_size"], moe_intermediate_size=16, shared_expert_intermediate_size=16,
        num_experts=c["num_experts"], num_experts_per_tok=k, norm_topk_prob=True))
    blk.load_weights([("gate.weight", mx.array(z["w"]).astype(mx.bfloat16))], strict=False)
    logits, inds, scores = blk.route(mx.array(z["x"]).astype(mx.bfloat16))
    lg, ids = np.array(logits.astype(mx.float32)), np.array(inds)
    sc = np.array(scores.astype(mx.float32))
    ref_lg, ref_ids, ref_sc = z["logits"], z["idx"], z["scores"]
    n_boundary = n_differ = n_non_tie = 0
    for t in range(len(ids)):
        kth = np.sort(ref_lg[t])[::-1][k - 1]
        above, tied = int((ref_lg[t] > kth).sum()), int((ref_lg[t] == kth).sum())
        n_boundary += above < k < above + tied
        diff = set(ids[t].tolist()) ^ set(ref_ids[t].tolist())
        n_differ += bool(diff)
        n_non_tie += any(ref_lg[t, e] != kth or lg[t, e] != ref_lg[t, e] for e in diff)
    return {"tokens": int(len(ids)), "logits_bitwise_frac": float((lg == ref_lg).mean()),
            "tokens_with_boundary_tie": n_boundary, "tokens_expert_set_differs": n_differ,
            "tokens_non_tie_difference": n_non_tie,
            "sorted_weights_max_abs": float(np.abs(np.sort(sc, -1) - np.sort(ref_sc, -1)).max())}


def _mlx_topk_tie_order(tw, ref_meta):
    import mlx.core as mx
    import numpy as np

    r = ref_meta["torch_topk_tie_order"]
    scores = np.array(r["scores"], np.float32)
    m = np.array(tw.topk_mask_lowest_index(mx.array(scores[None]), r["k"]))[0]
    return {"port_zero_kept": [i for i in np.nonzero(m)[0].tolist() if scores[i] == 0],
            "torch_zero_kept": r["zero_kept"], "lowest_zero": r["lowest_zero"]}


def _mlx_selection_retention(tw):
    """A sparse prefill must not leave its (B, S, NB) block selection on the
    module unless diagnostics are switched on."""
    import mlx.core as mx
    import numpy as np

    args = tw.TextModelArgs.from_dict(_qsa_cfg(REG_QSA_REAL))
    att = tw.QSAAttention(args)
    x = mx.random.normal((1, 1024, args.hidden_size), key=mx.random.key(0))
    out = {}
    for label, record in (("default", None), ("recorded", True)):
        if record is not None:
            att.indexer.record_selection = record
        step = tw._Step(1, 1024, 0, np.zeros((1,), np.int64), tw.rope_inv_freq(args))
        mx.eval(att(x, step, tw.QSACache()))
        sel = att.indexer._last_selection
        held = [] if sel is None else [sel] if isinstance(sel, mx.array) else [sel.blocks, sel.scores]
        out[label] = {
            "sparse_queries": att.indexer._last_stats.sparse_queries,
            "retained": sel is not None or "_last_selection" in att.indexer,
            "blocks_shape": list(held[0].shape) if held else None,
            "retained_bytes": int(sum(a.nbytes for a in held)),
        }
    return out


def _mlx_rope(tw, reg: Path):
    import types

    import mlx.core as mx
    import numpy as np

    z = np.load(reg / "rope_ref.npz")

    def inv_of(theta, dim):
        ns = types.SimpleNamespace(rope_parameters={"rope_theta": theta}, rotary_dim=dim)
        return np.array(tw.rope_inv_freq(ns))

    def ulps(a, b):
        return np.abs(a.view(np.int32).astype(np.int64) - b.view(np.int32).astype(np.int64))

    exact = {}
    for theta, dim in REG_ROPE_EXACT:
        exact[f"{theta}/{dim}"] = int((ulps(inv_of(theta, dim), z[f"inv::{theta}::{dim}"]) > 0).sum())
    sweep = {f"{t}/{d}": int(ulps(inv_of(t, d), z[f"inv::{t}::{d}"]).max()) for t, d in REG_ROPE_SWEEP}
    args = tw.TextModelArgs.from_dict(_qsa_cfg(REG_QSA_REAL))
    cos, sin = tw.rope_cos_sin(mx.array(z["pos"].astype(np.int32)), tw.rope_inv_freq(args))
    got = np.stack([np.array(cos.astype(mx.bfloat16).astype(mx.float32)),
                    np.array(sin.astype(mx.bfloat16).astype(mx.float32))])
    ref = np.stack([z["cos_bf16"], z["sin_bf16"]])
    return {"exact_differing_entries": exact, "sweep_max_ulps": sweep,
            "cos_sin_bf16_mismatch_frac": float((got != ref).mean()),
            "cos_sin_max_abs": float(np.abs(got - ref).max())}


def _mlx_edge(reg: Path):
    import mlx.core as mx
    import numpy as np
    from mlx_lm.models.cache import ArraysCache
    from mlx_lm.utils import load_model

    model, _ = load_model(reg / "edge_mlx_fp32")
    z = np.load(reg / "edge_ref.npz")
    ids, ref = [int(t) for t in z["ids"]], z["logits"]

    def run(chunk, cache=None):
        o = model(mx.array([chunk]), cache=cache)
        mx.eval(o)
        return np.array(o.astype(mx.float32))[0]

    prefill = run(ids)
    cache = model.make_cache()
    stepped = np.concatenate([run(ids[a:b], cache)
                              for a, b in zip(REG_EDGE_CUTS[:-1], REG_EDGE_CUTS[1:])])
    ple = {lid - 1 for lid in REG_EDGE_TEXT["ple_layer_ids"]}
    arrays = [(i, c) for i, c in enumerate(cache) if isinstance(c, ArraysCache)]
    return {
        "prefill_vs_ref_uncached": _diff(prefill, ref),
        "cached_segments_vs_ref_uncached": _diff(stepped, ref),
        "deltanet_conv_cache_lens": sorted({int(c[0].shape[1]) for _, c in arrays}),
        "ple_conv_cache_lens": sorted({int(c[2].shape[1]) for i, c in arrays if i in ple}),
    }


def stage_mlx_regress(work: Path):
    from joulewise.align.models import qwen4_exp_twin as tw

    reg = work / "regress"
    res = {"validation": _mlx_validation(tw)}
    res["gdn"], gdn_outs = _mlx_gdn(tw, reg)
    res["gdn_bf16_noise"] = _mlx_gdn_bf16_noise(reg, gdn_outs)
    res["silu"] = _mlx_silu(tw, reg)
    res["qsa"] = _mlx_qsa(tw, reg)
    res["rope"] = _mlx_rope(tw, reg)
    res["selection_retention"] = _mlx_selection_retention(tw)
    res["router"] = _mlx_router(tw, reg)
    ref_meta = json.loads((reg / "ref_meta.json").read_text())
    res["topk_tie_order"] = _mlx_topk_tie_order(tw, ref_meta)
    res["edge"] = _mlx_edge(reg)
    res["peak_rss_bytes"] = _peak_rss()
    (reg / "mlx_results.json").write_text(json.dumps(res, indent=2))


# ===========================================================================
# Driver (system python, stdlib only)
# ===========================================================================


def _convert(src: Path, out: Path, *extra: str) -> dict:
    _run(VENV_MLX, str(CONVERTER), "--src", str(src), "--out", str(out), *extra)
    return json.loads((out / "twin_manifest.json").read_text())


@unittest.skipIf(os.environ.get("JW_SKIP_TWIN_PARITY") == "1", "JW_SKIP_TWIN_PARITY=1")
@unittest.skipUnless(VENV_REF.exists() and VENV_MLX.exists(),
                     "pinned venv-ref / venv-mlx not present on this machine")
class Qwen4ExpTwinParityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TMP_ROOT.mkdir(parents=True, exist_ok=True)
        cls.work = Path(tempfile.mkdtemp(prefix="qwen4_exp_twin_", dir=str(TMP_ROOT)))
        me = str(Path(__file__).resolve())
        _run(VENV_REF, me, "ref", str(cls.work))
        _run(VENV_REF, me, "ref_regress", str(cls.work))
        ckpt = cls.work / "hf_ckpt"
        cls.manifests = {
            "fp32": _convert(ckpt, cls.work / "mlx_fp32", "--dtype", "float32", "--no-quantize",
                             "--ngram-format", "f32"),
            "bf16": _convert(ckpt, cls.work / "mlx_bf16", "--dtype", "bfloat16", "--no-quantize",
                             "--ngram-format", "bf16"),
            "q": _convert(ckpt, cls.work / "mlx_q", "--dtype", "bfloat16", "--expert-bits", "4",
                          "--dense-bits", "8", "--group-size", "32", "--ngram-format", "q8",
                          "--ngram-group-size", "16"),
        }
        cls.manifests["q_fused"] = _convert(
            cls.work / "hf_ckpt_fused", cls.work / "mlx_q_fused", "--dtype", "bfloat16",
            "--expert-bits", "4", "--dense-bits", "8", "--group-size", "32",
            "--ngram-format", "q8", "--ngram-group-size", "16")
        staged = cls.work / "hf_ckpt_staged"
        shutil.copytree(ckpt, staged)
        # Determinism of the quantized recipe (CPU-pinned mx.quantize), run
        # from a staged copy whose shards are deleted as they are consumed.
        cls.manifests["q_rerun"] = _convert(
            staged, cls.work / "mlx_q_rerun", "--dtype", "bfloat16", "--expert-bits", "4",
            "--dense-bits", "8", "--group-size", "32", "--ngram-format", "q8",
            "--ngram-group-size", "16", "--delete-source-shards", "--hash-sources",
            "--pins", str(cls.work / "pins.json"), "--pins-repo", "tiny")
        # A wrong pin must stop the conversion before anything is used.
        pins = json.loads((cls.work / "pins.json").read_text())
        pins["repos"]["tiny"]["files"][0]["sha256"] = "0" * 64
        (cls.work / "pins_bad.json").write_text(json.dumps(pins))
        try:
            _convert(ckpt, cls.work / "mlx_badpin", "--no-quantize", "--ngram-format", "bf16",
                     "--pins", str(cls.work / "pins_bad.json"), "--pins-repo", "tiny")
            cls.bad_pin_error = None
        except RuntimeError as exc:
            cls.bad_pin_error = str(exc)
        cls.staged_left = sorted(p.name for p in staged.glob("*.safetensors"))
        attribution = {
            "mlx_q_experts4": ("--expert-bits", "4", "--dense-bits", "none", "--ngram-format", "bf16"),
            "mlx_q_dense8": ("--expert-bits", "none", "--dense-bits", "8", "--ngram-format", "bf16"),
            "mlx_q_ngram8": ("--no-quantize", "--ngram-format", "q8", "--ngram-group-size", "16"),
            "mlx_q_ngram4": ("--no-quantize", "--ngram-format", "q4", "--ngram-group-size", "16"),
        }
        for name, extra in attribution.items():
            _convert(ckpt, cls.work / name, "--dtype", "bfloat16", "--group-size", "32", *extra)
        reg = cls.work / "regress"
        cls.manifests["edge"] = _convert(reg / "edge_ckpt", reg / "edge_mlx_fp32", "--dtype", "float32",
                                         "--no-quantize", "--ngram-format", "f32")
        _run(VENV_MLX, me, "mlx", str(cls.work))
        _run(VENV_MLX, me, "mlx_regress", str(cls.work))
        cls.ref_meta = json.loads((cls.work / "ref_meta.json").read_text())
        cls.res = json.loads((cls.work / "mlx_results.json").read_text())
        cls.reg_ref = json.loads((cls.work / "regress" / "ref_meta.json").read_text())
        cls.reg = json.loads((cls.work / "regress" / "mlx_results.json").read_text())
        summary = {"work": str(cls.work), "ref_meta": {k: v for k, v in cls.ref_meta.items()
                                                       if not k.startswith(("seq", "ext", "trim"))},
                   "results": cls.res, "regressions": cls.reg}
        (cls.work / "summary.json").write_text(json.dumps(summary, indent=2))
        print(f"\n[qwen4_exp_twin parity] summary: {cls.work / 'summary.json'}", file=sys.stderr)

    @classmethod
    def tearDownClass(cls):
        if os.environ.get("JW_TWIN_KEEP") != "1" and hasattr(cls, "work"):
            for sub in ("hf_ckpt_staged", "mlx_q_rerun", "mlx_badpin", "mlx_q_experts4", "mlx_q_dense8",
                        "mlx_q_ngram8", "mlx_q_ngram4"):
                shutil.rmtree(cls.work / sub, ignore_errors=True)

    def _max(self, name):
        return self.res[name]["max_abs"]

    # --- reference fidelity ----------------------------------------------------
    def test_reference_copy_matches_installed_transformers(self):
        self.assertEqual(self.ref_meta["engine_vs_installed_max_abs"], 0.0)
        self.assertEqual(self.ref_meta["reference_reload_max_abs"], {"per_expert": 0.0, "fused": 0.0})

    def test_fused_expert_checkpoint_converts_identically(self):
        r = self.res["fused_vs_per_expert_conversion"]
        self.assertTrue(r["same_keys"])
        self.assertTrue(r["bitwise_equal"])

    def test_source_pins_enforced(self):
        self.assertTrue(all(s.get("pin_verified") for s in self.manifests["q_rerun"]["source"]["shards"]))
        self.assertIsNotNone(self.bad_pin_error)
        self.assertIn("!= pinned", self.bad_pin_error)

    def test_fp32_prefill_matches_reference(self):
        self.assertLessEqual(self._max("prefill_fp32_vs_ref"), TOL["fp32_vs_ref"])

    def test_fp32_stepwise_decode_matches_reference(self):
        self.assertLessEqual(self._max("stepwise_fp32_vs_ref"), TOL["fp32_vs_ref"])

    def test_bf16_within_reference_bf16_noise(self):
        for kind, noise_key in (("prefill", "ref_bf16_vs_ref_fp32_noise"),
                                ("stepwise", "ref_bf16_vs_ref_fp32_noise_stepwise")):
            noise = self.res[noise_key]
            vs_fp32 = self.res[f"{kind}_bf16_vs_ref_fp32"]
            vs_bf16 = self.res[f"{kind}_bf16_vs_ref_bf16"]
            with self.subTest(kind=kind):
                self.assertLessEqual(vs_fp32["max_abs"],
                                     TOL["bf16_vs_ref_fp32_over_noise"] * noise["max_abs"])
                self.assertLessEqual(vs_fp32["rms"], TOL["bf16_vs_ref_fp32_over_noise"] * noise["rms"])
                self.assertLessEqual(vs_bf16["max_abs"],
                                     TOL["bf16_vs_ref_bf16_over_noise"] * noise["max_abs"])
                self.assertEqual(vs_fp32["top1_agree"], 1.0)
                self.assertEqual(vs_bf16["top1_agree"], 1.0)

    def test_mlx_lm_generate_step_end_to_end(self):
        g = self.res["generate_step_greedy"]
        self.assertTrue(g["tokens_equal"], g)
        self.assertLessEqual(g["logprob_max_abs"], TOL["fp32_vs_ref"])

    def test_left_padded_batch_matches_reference(self):
        for name in ("padded_row0_fp32_vs_ref", "padded_row1_fp32_vs_ref", "single_b_fp32_vs_ref"):
            with self.subTest(name=name):
                self.assertLessEqual(self._max(name), TOL["fp32_vs_ref"])

    def test_trimmed_cache_matches_reference(self):
        self.assertLessEqual(self._max("trim_reprefill_vs_ref"), TOL["fp32_vs_ref"])

    # --- engine invariants -------------------------------------------------------
    def test_mlx_prefill_vs_stepwise(self):
        self.assertLessEqual(self._max("mlx_prefill_vs_stepwise_fp32"), TOL["mlx_internal_fp32"])

    def test_query_chunked_attention_is_exact(self):
        self.assertLessEqual(self._max("query_chunked_vs_unchunked_fp32"), TOL["mlx_internal_fp32"])
        self.assertLessEqual(self._max("query_chunked_dense_vs_unchunked_fp32"),
                             TOL["mlx_internal_fp32"])
        self.assertLessEqual(self._max("query_chunked_padded_vs_ref"), TOL["fp32_vs_ref"])

    def test_batch1_vs_left_padded(self):
        self.assertLessEqual(self._max("batch1_vs_leftpadded_fp32"), TOL["mlx_internal_fp32"])
        for row in ("row0", "row1"):
            with self.subTest(dense_path_row=row):
                self.assertLessEqual(self.res["batch1_vs_leftpadded_dense_fp32"][row]["max_abs"],
                                     TOL["mlx_internal_fp32"])

    def test_kv_trim_reprefill_equals_fresh(self):
        self.assertEqual(self._max("trim_reprefill_vs_fresh_exact"), 0.0)
        self.assertEqual(self.res["trim_reprefill_vs_fresh_exact"]["offsets_after_restore"], [TRIM_A])
        self.assertLessEqual(self._max("trim_reprefill_vs_fresh_one_call"), TOL["mlx_internal_fp32"])

    def test_deltanet_snapshot_restore_is_exact(self):
        r = self.res["deltanet_snapshot_restore"]
        self.assertTrue(r["logits_bitwise_equal"])
        self.assertTrue(r["state_after_restore_bitwise_equal"])
        self.assertTrue(r["state_rerun_bitwise_equal"])
        self.assertEqual(r["n_recurrent_layers"], 6)

    def test_quantized_within_tolerance_of_unquantized(self):
        r = self.res["quant_vs_unquant_bf16"]
        self.assertLessEqual(r["rel"], TOL["quant_vs_unquant_rel"])
        self.assertGreaterEqual(r["top1_agree"], TOL["quant_top1_min"])
        self.assertEqual(self.res["quant_config"]["default_bits"], 4)
        self.assertGreater(self.res["quant_config"]["n_overrides"], 0)

    # --- the test has teeth ---------------------------------------------------
    def test_scenarios_exercise_qsa_and_ple(self):
        for stats in self.res["qsa_last_prefill_stats"]:
            self.assertEqual(stats["queries"], LEN_A)
            self.assertGreater(stats["sparse_queries"], 20)
            self.assertGreater(stats["excluded_block_tokens"], 0)
        self.assertGreater(self._max("sensitivity_ref_dense_vs_ref"), 100 * TOL["fp32_vs_ref"])
        self.assertGreater(self._max("sensitivity_ref_nople_vs_ref"), 100 * TOL["fp32_vs_ref"])
        self.assertTrue(all(v["lookups"] > 0 for v in self.res["ngram"].values()))
        self.assertEqual(len(self.res["ngram"]), 2)

    # --- converter ----------------------------------------------------------------
    def test_converter_streams_drops_mtp_and_is_deterministic(self):
        a, b = self.manifests["q"], self.manifests["q_rerun"]
        self.assertGreater(len(a["source"]["shards"]), 20)
        self.assertEqual(a["dropped_tensors"]["mtp"], 1)
        self.assertEqual(len(a["ngram_buffer_checks"]), 6)
        self.assertEqual(a["quantize_device"], "cpu")
        strip = lambda m: {f["path"]: f["sha256"] for f in m["files"]
                           if f["path"] != "config.json"}
        self.assertEqual(strip(a), strip(b))
        self.assertEqual(self.staged_left, [])
        self.assertTrue(all("sha256" in s for s in b["source"]["shards"]))

    def test_sanitize_raw_hf_matches_converter(self):
        r = self.res["sanitize_raw_hf"]
        self.assertTrue(r["same_keys"])
        self.assertTrue(r["bitwise_equal"])

    def test_mixed_precision_policy(self):
        m = self.manifests["q"]
        n_layers = TINY_TEXT_CONFIG["num_hidden_layers"]
        n_attn = TINY_TEXT_CONFIG["layer_types"].count("full_attention")
        n_ple = len(TINY_TEXT_CONFIG["ple_layer_ids"])
        # 4-bit: gate/up/down expert stacks per layer.
        self.assertEqual(m["quantized_modules"]["4"], 3 * n_layers)
        # 8-bit: embed, lm_head; per layer 3 shared-expert + 2x2 hyper-connection
        # projections; DeltaNet qkv/z/out; attention q/k/v/o; PLE key/value; mixer 2.
        expected_8 = (2 + n_layers * (3 + 4) + (n_layers - n_attn) * 3 + n_attn * 4
                      + n_ple * 2 + 2)
        self.assertEqual(m["quantized_modules"]["8"], expected_8)
        self.assertIn("qsa_indexer", m["category_bytes"])
        self.assertIn("router", m["category_bytes"])

    def test_stage_memory_under_budget(self):
        self.assertLess(self.ref_meta["peak_rss_bytes"], RSS_LIMIT_BYTES)
        self.assertLess(self.res["mlx_peak_rss_bytes"], RSS_LIMIT_BYTES)
        self.assertLess(self.reg_ref["peak_rss_bytes"], RSS_LIMIT_BYTES)
        self.assertLess(self.reg["peak_rss_bytes"], RSS_LIMIT_BYTES)

    # --- review regressions -------------------------------------------------------
    def test_regress_config_validation_matches_reference(self):
        ref, got = self.reg_ref["validation"], self.reg["validation"]
        self.assertIsNone(ref["valid"])
        for name in REG_VALIDATION:
            with self.subTest(case=name):
                if name != "valid":
                    self.assertIsNotNone(ref[name], "reference accepted a case it should reject")
                self.assertEqual(got[name] is None, ref[name] is None, (got[name], ref[name]))

    def _gdn(self, key):
        r = self.reg["gdn"][key]
        self.assertNotIn("error", r, r.get("error"))
        return r

    def test_regress_deltanet_conv_cache_kernel_sizes(self):
        # Cached segments at kernel 4 (control) and kernel 1 (zero-length
        # history): outputs match the reference and the conv cache holds
        # exactly K-1 positions.
        for name in ("k4_segments", "k1_segments"):
            with self.subTest(case=name):
                r = self._gdn(f"{name}/fp32/gpu")
                self.assertLessEqual(r["max_abs"], TOL["fp32_vs_ref"], r["seg_max_abs"])
                self.assertEqual(r["conv_cache_len"], r["kernel"] - 1)

    def test_regress_deltanet_key_dims_not_multiple_of_32(self):
        for key in ("dk48/fp32/gpu", "dk48/fp32/cpu", "dk16/fp32/gpu", "dk16/fp32/cpu"):
            with self.subTest(case=key):
                self.assertLessEqual(self._gdn(key)["max_abs"], TOL["fp32_vs_ref"])

    def test_regress_conv_silu_rounds_once(self):
        s = self.reg["silu"]
        for dev in ("gpu", "cpu"):
            with self.subTest(device=dev):
                self.assertLess(s[dev]["port_mismatch"],
                                REG_TOL["silu_mismatch_vs_stock"] * s[dev]["stock_mismatch"], s[dev])
        for name, r in self.reg["gdn_bf16_noise"].items():
            with self.subTest(case=name):
                self.assertLessEqual(self._gdn(f"{name}/fp32/gpu")["max_abs"], TOL["fp32_vs_ref"])
                self.assertLessEqual(r["rms_ratio"], REG_TOL["gdn_bf16_rms_over_noise"], r)
        self.assertEqual(len(self.reg["gdn_bf16_noise"]), 3)

    def test_regress_rope_inv_freq_matches_reference(self):
        r = self.reg["rope"]
        self.assertEqual(r["exact_differing_entries"], {f"{t}/{d}": 0 for t, d in REG_ROPE_EXACT})
        self.assertLessEqual(max(r["sweep_max_ulps"].values()), 1, r["sweep_max_ulps"])
        self.assertLessEqual(r["cos_sin_bf16_mismatch_frac"], REG_TOL["rope_bf16_mismatch_frac"])

    def test_regress_qsa_at_long_context_positions(self):
        # Mask comparisons are tie-aware (see test_regress_qsa_mask_differences_are_ties);
        # output bounds apply to rows whose masks agree.
        q = self.reg["qsa"]
        far = q["real_far_fp32"]
        self.assertEqual(far["mask_rows_non_tie"], 0)
        self.assertLessEqual(far["max_abs_same_mask_rows"], TOL["fp32_vs_ref"])
        near, far = q["real_near_bf16"], q["real_far_bf16"]
        self.assertEqual(far["mask_rows_non_tie"], 0)
        self.assertLessEqual(far["max_abs_same_mask_rows"],
                             REG_TOL["qsa_bf16_far_over_near"] * near["max_abs_same_mask_rows"])

    def test_regress_qsa_mask_differences_are_ties(self):
        # torch.topk's tie order is unspecified (and not lowest-index even for
        # small CPU inputs), so the port's lowest-index rule may keep a
        # different one of several exactly tied blocks. Every other mask
        # difference is a bug, and rows with equal masks must match tightly.
        for name, r in self.reg["qsa"].items():
            with self.subTest(case=name):
                self.assertEqual(r["mask_rows_non_tie"], 0, r)
                self.assertLessEqual(r["mask_rows_tie_only"], r["rows_with_boundary_tie"], r)
                if "bf16" not in name:
                    self.assertLessEqual(r["max_abs_same_mask_rows"], TOL["fp32_vs_ref"])
        for name in ("ties_relu_zero", "ties_degenerate"):
            self.assertGreater(self.reg["qsa"][name]["rows_with_boundary_tie"], 0)
        t = self.reg["topk_tie_order"]
        self.assertEqual(t["port_zero_kept"], t["lowest_zero"])

    def test_regress_router_selection_differences_are_ties(self):
        # bf16 router logits tie exactly at the top-10 boundary on some tokens
        # at 512 experts; mx.argpartition and torch.topk may keep different
        # tied experts (same weight). Anything else is a bug.
        r = self.reg["router"]
        self.assertGreaterEqual(r["logits_bitwise_frac"], 0.999)
        self.assertGreater(r["tokens_with_boundary_tie"], 0)
        self.assertEqual(r["tokens_non_tie_difference"], 0, r)
        self.assertLessEqual(r["sorted_weights_max_abs"], 1e-3)

    def test_regress_qsa_selection_not_retained_by_default(self):
        r = self.reg["selection_retention"]
        self.assertEqual(r["default"]["sparse_queries"], 1024 - 4 * 8 - 3)
        self.assertFalse(r["default"]["retained"])
        self.assertTrue(r["recorded"]["retained"])
        self.assertEqual(r["recorded"]["blocks_shape"], [1, 1024, 256])

    def test_regress_uneven_ngram_chunks_convert(self):
        # torch.chunk saved fewer pieces than split_ngram_parts; the reference
        # reloads them, so the converter must accept them too.
        e = self.reg_ref["edge"]
        self.assertEqual(e["ngram_shards_saved"], 27)
        self.assertLess(e["ngram_shards_saved"], e["split_ngram_parts"])
        self.assertEqual(e["reference_reload_max_abs"], 0.0)
        self.assertEqual(e["engine_vs_installed_max_abs"], 0.0)
        self.assertEqual(len(self.manifests["edge"]["ngram_buffer_checks"]), 3)
        self.assertLessEqual(self.reg["edge"]["prefill_vs_ref_uncached"]["max_abs"], TOL["fp32_vs_ref"])

    def test_regress_kernel1_convs_cached_decode(self):
        # DeltaNet and PLE short convs with kernel 1, cached decode in uneven
        # segments vs the reference's uncached prefill.
        r = self.reg["edge"]
        self.assertLessEqual(r["prefill_vs_ref_uncached"]["max_abs"], TOL["fp32_vs_ref"])
        self.assertLessEqual(r["cached_segments_vs_ref_uncached"]["max_abs"], TOL["fp32_vs_ref"])
        self.assertEqual(r["deltanet_conv_cache_lens"], [0])
        self.assertEqual(r["ple_conv_cache_lens"], [0])


STAGES ={"ref": stage_ref, "mlx": stage_mlx,
          "ref_regress": stage_ref_regress, "mlx_regress": stage_mlx_regress}

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] in STAGES:
        STAGES[sys.argv[1]](Path(sys.argv[2]))
    else:
        unittest.main()
