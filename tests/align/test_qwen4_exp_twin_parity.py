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
        _run(VENV_MLX, me, "mlx", str(cls.work))
        cls.ref_meta = json.loads((cls.work / "ref_meta.json").read_text())
        cls.res = json.loads((cls.work / "mlx_results.json").read_text())
        summary = {"work": str(cls.work), "ref_meta": {k: v for k, v in cls.ref_meta.items()
                                                       if not k.startswith(("seq", "ext", "trim"))},
                   "results": cls.res}
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


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] in ("ref", "mlx"):
        {"ref": stage_ref, "mlx": stage_mlx}[sys.argv[1]](Path(sys.argv[2]))
    else:
        unittest.main()
