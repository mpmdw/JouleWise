#!/usr/bin/env python3
"""Three-way differential for the qwen4_exp (Qwen3.8-Flash-Next) MLX ports.

GOAL item 3 (docs/align/qwen4_exp_port/GOAL.md): the Sol port
(lane/2026-11-05-align-flashnext-port, joulewise/align/models/qwen4_exp.py)
and the Opus twin (lane/2026-11-05-align-flashnext-twin,
joulewise/align/models/qwen4_exp_twin.py) are compared with each other and
with the official transformers 5.22.1 reference on ONE shared tiny random
checkpoint.

Stages, each in its own process (``all`` runs them in order):

  ref      torch + transformers. Build the tiny checkpoint (every text layer
           type, PLE at two ple_layer_index values, an indexer budget that
           drops blocks), save_pretrained it in bf16 in the released
           ConditionalGeneration layout, run every scenario in fp32 and bf16,
           capture each component's input and output, and run a forced-tie
           QSA probe. Exact top-k ties at the QSA cut are counted. The primary
           reference ("REF") breaks those ties lowest-block-first, the rule
           both ports implement; torch.topk's own CPU order is kept as
           "REFdefault". The MoE router's topk is never touched.
  convert  Each port's OWN converter, from its own worktree: fp32 and bf16,
           unquantized, n-gram table in the matching precision.
  mlx      mlx 0.31.2 / mlx-lm 0.31.3. Load the four conversions with
           mlx_lm.utils.load_model (the model_file hook) and run the same
           scenarios. Sol bf16 runs twice: jw_bf16_fp32_ops on (default) and
           off. A third load of Sol carries the prototype canonical numerics
           (apply_canonical). Then per-layer traces (free-running), isolated
           components (each port's module fed the reference's exact input)
           and a forced exact-tie QSA probe.
  diag     Op-level evidence cited by the doc (bf16 rounding of MLX vs
           torch ops, RoPE inverse frequencies, the twin converter's bf16 read
           path, the QSA attention core on identical bf16 q/k/v).
  report   Markdown tables from results.json.

Resource rules (shared laptop): ``all`` runs every stage under
``nice -n 20 taskpolicy -b`` with 2 threads and TMPDIR=/private/tmp/jwdiff.
Peak RSS is reported per stage. Community PR #1788 code is never imported.

Usage:
  python scripts/qwen4exp_differential.py all --work /private/tmp/jwdiff/run1
"""

import argparse
import copy
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SOL_REPO = Path("/Users/edr/code/CapstoneProject/jw-wt/sol-flashnext-port")
TWIN_REPO = Path("/Users/edr/code/CapstoneProject/jw-wt/opus-flashnext-twin")
PY_BOTH = Path("/private/tmp/jwsol/venv-both/bin/python")
TMPDIR = Path("/private/tmp/jwdiff")

EOS = 1
# hidden_size 96: sqrt(96) is not bf16-representable (as sqrt(2560) is not
# in the released model), so a bf16-rounded PLE gate divisor is visible.
TEXT = {
    "vocab_size": 256, "hidden_size": 96, "num_hidden_layers": 8,
    "num_attention_heads": 4, "num_key_value_heads": 2, "head_dim": 64,
    "linear_num_key_heads": 2, "linear_num_value_heads": 4,
    "linear_key_head_dim": 32, "linear_value_head_dim": 32, "linear_conv_kernel_dim": 4,
    "moe_intermediate_size": 64, "shared_expert_intermediate_size": 64,
    "num_experts": 8, "num_experts_per_tok": 3,
    "hc_count": 4, "hc_lowrank": 32,
    "ple_layer_ids": [2, 5], "ple_embed_dim": 64, "ple_conv_kernel_size": 4,
    "ngram_size": 3, "heads_per_ngram": 2, "ngram_vocab_size_base": 101,
    "make_ngram_vocab_size_divisible_by": 8, "split_ngram_parts": 4,
    # budget 16 / ratio 4 = top-4 blocks: a 40-token prompt has up to 10
    # complete blocks, the 320-token context 80, so most queries drop blocks.
    "indexer_n_heads": 4, "indexer_kv_heads": 1, "indexer_head_dim": 32,
    "indexer_budget": 16, "indexer_compress_ratio": 4,
    "output_gate_type": "sigmoid", "eos_token_id": EOS, "bos_token_id": EOS,
    "rms_norm_eps": 1e-6, "full_attention_interval": 4,
    "rope_parameters": {"mrope_interleaved": True, "mrope_section": [4, 2, 2],
                        "partial_rotary_factor": 0.25, "rope_theta": 10000000,
                        "rope_type": "default"},
    "layer_types": ["linear_attention"] * 3 + ["full_attention"]
                   + ["linear_attention"] * 3 + ["full_attention"],
}
VISION = {"depth": 1, "hidden_size": 16, "intermediate_size": 32, "num_heads": 2,
          "out_hidden_size": 96, "patch_size": 16, "spatial_merge_size": 2,
          "temporal_patch_size": 2, "num_position_embeddings": 16}
N_LAYERS = TEXT["num_hidden_layers"]
QSA_LAYERS = [i for i, t in enumerate(TEXT["layer_types"]) if t == "full_attention"]
PLE_LAYERS = [i - 1 for i in TEXT["ple_layer_ids"]]
RATIO, TOPK = TEXT["indexer_compress_ratio"], TEXT["indexer_budget"] // TEXT["indexer_compress_ratio"]

LEN_A, LEN_B, PAD_B, N_EXT = 40, 32, 8, 4
CHUNK = 7
LONG_LEN, LONG_PREFIX, LONG_CHUNK = 320, 304, 64
N_GREEDY = 32
TIE_LAYER = QSA_LAYERS[0]
SOL_OVERRIDES = {"jw_max_prefill_tokens": 1 << 20, "jw_context_cap": 1 << 20}


def tokens(seed, n, eos_at=()):
    import numpy as np
    ids = np.random.default_rng(seed).integers(2, TEXT["vocab_size"], n).tolist()
    for i in eos_at:
        ids[i] = EOS
    return [int(x) for x in ids]


def sequences():
    return dict(seq_a=tokens(7, LEN_A, (5, 21)), seq_b=tokens(8, LEN_B, (11,)),
                ext_a=tokens(9, N_EXT), ext_b=tokens(10, N_EXT, (1,)),
                long=tokens(11, LONG_LEN, (37, 150, 151, 260)))


def peak_rss():
    import resource
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


# ===========================================================================
# Stage: reference (torch + transformers 5.22.1)
# ===========================================================================


def randomize(model, torch, seed):
    """Nonzero random values everywhere, including the pieces the reference
    zero-initialises (PLE conv, norm offsets), so none goes untested."""
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
            elif p.ndim == 1:
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


class TopkSpy:
    """Wraps every QSA indexer forward: counts top-k calls and the calls whose
    K-th and (K+1)-th scores are exactly equal (a tie straddling the cut,
    where torch.topk's choice is implementation-defined). With
    ``force_lowest_index`` the indexer instead selects score-descending,
    block-index-ascending (stable sort), the rule both ports implement."""

    def __init__(self, model, torch, force_lowest_index=False):
        self.model, self.torch, self.force = model, torch, force_lowest_index
        self.calls = self.straddling = 0
        self._saved = []

    def __enter__(self):
        from unittest.mock import patch
        torch = self.torch
        original_topk = torch.Tensor.topk
        spy = self

        def topk(input, k, dim=-1, largest=True, sorted=True):
            assert largest and dim == 0
            spy.calls += 1
            order = torch.sort(-input, dim=0, stable=True).indices
            if k < input.shape[0] and input[order[k - 1]] == input[order[k]]:
                spy.straddling += 1
            if spy.force:
                idx = order[:k]
                return torch.return_types.topk((input.gather(0, idx), idx))
            return original_topk(input, k, dim=dim, largest=largest, sorted=sorted)

        for module in self.model.modules():
            if type(module).__name__ != "Qwen4ExpTextQSAIndexer":
                continue
            original = module.forward

            def forward(*a, _orig=original, **kw):
                with patch.object(torch.Tensor, "topk", topk):
                    return _orig(*a, **kw)

            module.forward = forward
            self._saved.append((module, original))
        return self

    def __exit__(self, *exc):
        for module, original in self._saved:
            module.forward = original
        return False


def stage_ref(work):
    import numpy as np
    import torch
    from transformers import Qwen4ExpConfig, Qwen4ExpForCausalLM, Qwen4ExpForConditionalGeneration

    torch.set_num_threads(2)
    torch.manual_seed(0)
    work.mkdir(parents=True, exist_ok=True)
    cfg = Qwen4ExpConfig(text_config=copy.deepcopy(TEXT), vision_config=dict(VISION))
    full = Qwen4ExpForConditionalGeneration(cfg).eval()
    randomize(full, torch, 1234)
    # The released checkpoint is bf16; fp32 runs upcast it exactly.
    full = full.to(torch.bfloat16)
    ckpt = work / "hf"
    if not ckpt.exists():
        full.save_pretrained(ckpt, max_shard_size="200KB")

    tcfg = copy.deepcopy(full.config.text_config)
    tcfg._attn_implementation = "sdpa"
    # The reference loads its weights FROM the saved checkpoint files (the
    # bytes both converters read) through transformers' own loader, which
    # applies the serialized-layout conversions (per-expert keys, n-gram
    # shards). The round trip must reproduce the in-memory model exactly.
    loaded = Qwen4ExpForConditionalGeneration.from_pretrained(ckpt, dtype=torch.bfloat16).eval()
    mem = full.state_dict()
    state, mismatched = {}, []
    for k, v in loaded.state_dict().items():
        if not torch.equal(v, mem[k]):
            mismatched.append(k)
        if k.startswith("model.language_model."):
            state["model." + k[len("model.language_model."):]] = v
        elif k.startswith("lm_head."):
            state[k] = v
    if mismatched:
        raise RuntimeError(f"checkpoint round trip changed {mismatched[:5]}")
    del loaded

    def text_model(dtype):
        m = Qwen4ExpForCausalLM(tcfg).eval()
        missing, unexpected = m.load_state_dict(state, strict=False)
        if [k for k in missing if "rotary_emb" not in k] or unexpected:
            raise RuntimeError(f"reference load: missing={missing} unexpected={unexpected}")
        return m.to(dtype)

    seqs = sequences()
    out, meta = {}, dict(seqs=seqs, ties={}, torch=torch.__version__,
                         transformers=__import__("transformers").__version__,
                         attn_implementation="sdpa", n_shards=len(list(ckpt.glob("*.safetensors"))))

    def fwd(m, ids, **kw):
        with torch.no_grad():
            return m(input_ids=torch.tensor(ids), use_cache=True, **kw)

    def prefill(m, ids):
        return fwd(m, [ids]).logits[0].float().numpy()

    def chunked(m, ids, n, prefix=None):
        pkv, rows, start = None, [], 0
        if prefix is not None:
            r = fwd(m, [ids[:prefix]])
            pkv, start = r.past_key_values, prefix
        for s in range(start, len(ids), n):
            r = fwd(m, [ids[s:s + n]], past_key_values=pkv)
            pkv = r.past_key_values
            rows.append(r.logits[0].float())
        return torch.cat(rows).numpy()

    def scenarios(m, tag):
        sa, sb = seqs["seq_a"], seqs["seq_b"]
        res = {}
        res["prefill"] = prefill(m, sa)
        res["stepwise"] = chunked(m, sa, 1)
        res["chunked"] = chunked(m, sa, CHUNK)
        # Left-padded batch, positions as generate() builds them.
        mask = torch.tensor([[1] * LEN_A, [0] * PAD_B + [1] * LEN_B])
        pos = (mask.cumsum(-1) - 1).clamp_min(0)
        r = fwd(m, [sa, [EOS] * PAD_B + sb], attention_mask=mask, position_ids=pos)
        pkv, rows = r.past_key_values, [r.logits.float()]
        for i in range(N_EXT):
            mask = torch.cat([mask, torch.ones(2, 1, dtype=mask.dtype)], dim=1)
            r = fwd(m, [[seqs["ext_a"][i]], [seqs["ext_b"][i]]], past_key_values=pkv,
                    attention_mask=mask, position_ids=pos[:, -1:] + 1 + i)
            pkv = r.past_key_values
            rows.append(r.logits.float())
        res["padded"] = torch.cat(rows, dim=1).numpy()
        res["single_a"] = chunked(m, sa + seqs["ext_a"], 1, prefix=LEN_A)
        res["single_b"] = chunked(m, sb + seqs["ext_b"], 1, prefix=LEN_B)
        res["long_prefill"] = prefill(m, seqs["long"])
        res["long_decode"] = chunked(m, seqs["long"], 1, prefix=LONG_PREFIX)
        # Greedy: logits row i produced token i.
        r = fwd(m, [sa])
        pkv, toks, rows = r.past_key_values, [], [r.logits[0, -1].float()]
        for i in range(N_GREEDY):
            toks.append(int(rows[-1].argmax()))
            if i == N_GREEDY - 1:
                break
            r = fwd(m, [[toks[-1]]], past_key_values=pkv)
            pkv = r.past_key_values
            rows.append(r.logits[0, -1].float())
        res["greedy_logits"] = torch.stack(rows).numpy()
        meta[f"greedy_tokens_{tag}"] = toks
        # Teacher-forced along this greedy path (one prefill), for margins.
        res["greedy_tf"] = prefill(m, sa + toks)[LEN_A - 1:LEN_A - 1 + N_GREEDY]
        return res

    for tag, dtype in (("f32", torch.float32), ("b16", torch.bfloat16)):
        m = text_model(dtype)
        meta["experts_implementation"] = m.config._experts_implementation
        # Primary reference ("f32"/"b16"): QSA exact ties broken toward the
        # lowest block index, a deterministic instance of the reference's
        # unspecified torch.topk tie order (the rule both ports implement).
        # Secondary ("f32D"/"b16D"): torch.topk's own CPU tie order.
        for run_tag, force in ((tag, True), (tag + "D", False)):
            part = work / f"ref_{run_tag}.npz"
            if part.exists():
                # Resume: results of an interrupted run (same seeds, same checkpoint).
                saved = np.load(part)
                res = {k: saved[k] for k in saved.files}
                part_meta = json.loads((work / f"ref_{run_tag}_meta.json").read_text())
            else:
                with TopkSpy(m, torch, force_lowest_index=force) as spy:
                    res = scenarios(m, run_tag)
                part_meta = {"ties": {run_tag: dict(topk_calls=spy.calls, straddling_ties=spy.straddling)},
                             f"greedy_tokens_{run_tag}": meta[f"greedy_tokens_{run_tag}"]}
                np.savez(part, **res)
                (work / f"ref_{run_tag}_meta.json").write_text(json.dumps(part_meta))
            meta["ties"].update(part_meta.pop("ties"))
            meta.update(part_meta)
            print(f"[ref] {run_tag} scenarios done", flush=True)
            for k, v in res.items():
                out[f"{run_tag}.{k}"] = v
        with TopkSpy(m, torch, force_lowest_index=True):
            capture(m, torch, seqs["seq_a"], tag, out)
        print(f"[ref] {tag} capture done", flush=True)
        if tag == "f32":
            # Forced exact ties: zero one QSA indexer projection, so every
            # visible block scores exactly 0.
            w = m.model.layers[TIE_LAYER].self_attn.indexer.index_qk_proj.weight
            saved = w.detach().clone()
            with torch.no_grad():
                w.zero_()
            with TopkSpy(m, torch) as spy:
                out["f32.tie_default"] = prefill(m, seqs["seq_a"])
            meta["ties"]["probe_default"] = dict(topk_calls=spy.calls, straddling_ties=spy.straddling)
            with TopkSpy(m, torch, force_lowest_index=True):
                out["f32.tie_lowest_index"] = prefill(m, seqs["seq_a"])
            with torch.no_grad():
                w.copy_(saved)
        del m
    np.savez(work / "ref.npz", **out)
    meta["peak_rss"] = peak_rss()
    (work / "ref_meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps({k: meta[k] for k in ("ties", "peak_rss", "n_shards")}))


def capture(m, torch, ids, tag, out):
    """Inputs and outputs of every component on a full prefill of ``ids``."""
    hooks = []

    def f32(t):
        return t.detach().float().numpy()

    def add(module, name, fn):
        def hook(mod, args, kwargs, o):
            fn(args, kwargs, o)
            return None  # never replace the module's output

        hooks.append(module.register_forward_hook(hook, with_kwargs=True))

    def put(key, value):
        out[f"{tag}.cap.{key}"] = value

    for i, layer in enumerate(m.model.layers):
        p = f"L{i}."
        if layer.ple is not None:
            add(layer.ple, "ple", lambda a, k, o, p=p: (put(p + "ple.in", f32(a[0])),
                                                       put(p + "ple.ids", a[1].numpy()),
                                                       put(p + "ple.out", f32(o))))
        for hc in ("attn_hc", "mlp_hc"):
            mod = layer.attn_hyper_connection if hc == "attn_hc" else layer.mlp_hyper_connection
            add(mod, hc, lambda a, k, o, p=p, hc=hc: (put(p + hc + ".in", f32(a[0])),
                                                     put(p + hc + ".mixed", f32(o[0])),
                                                     put(p + hc + ".weights", f32(o[2]))))
        if layer.layer_type == "linear_attention":
            add(layer.linear_attn, "mix", lambda a, k, o, p=p: (put(p + "mix.in", f32(a[0])),
                                                               put(p + "mix.out", f32(o))))
        else:
            add(layer.self_attn, "mix", lambda a, k, o, p=p: (put(p + "mix.in", f32(a[0])),
                                                             put(p + "mix.out", f32(o[0]))))
            add(layer.self_attn.indexer, "sel",
                lambda a, k, o, p=p: put(p + "sel", o[:, 0].numpy()))
        add(layer.mlp, "moe", lambda a, k, o, p=p: (put(p + "moe.in", f32(a[0])),
                                                   put(p + "moe.out", f32(o))))
        add(layer.mlp.gate, "router", lambda a, k, o, p=p: (put(p + "router.logits", f32(o[0])),
                                                           put(p + "router.experts", o[2].numpy())))
        add(layer, "layer", lambda a, k, o, p=p: put(p + "streams", f32(o)))
    add(m.model.hyper_connection_mixer, "mixer",
        lambda a, k, o: (put("mixer.in", f32(a[0])), put("mixer.out", f32(o))))
    add(m.lm_head, "head", lambda a, k, o: (put("head.in", f32(a[0])), put("head.out", f32(o))))
    try:
        with torch.no_grad():
            m(input_ids=torch.tensor([ids]), use_cache=False)
    finally:
        for h in hooks:
            h.remove()


# ===========================================================================
# Stage: convert (each port's own converter, from its own worktree)
# ===========================================================================


def upcast_checkpoint(src, dst):
    """Exact fp32 copy of a bf16 safetensors checkpoint (same names, same
    shards, integer buffers untouched): the twin converter's fallback input."""
    import shutil
    import torch
    from safetensors.torch import load_file, save_file
    dst.mkdir()
    for f in src.iterdir():
        if f.suffix == ".safetensors":
            t = load_file(str(f))
            save_file({k: (v.float() if v.is_floating_point() else v) for k, v in t.items()},
                      str(dst / f.name), metadata={"format": "pt"})
        else:
            shutil.copy2(f, dst / f.name)


def stage_convert(work, sol_repo, twin_repo, python):
    env = child_env()
    hf = work / "hf"
    issues = {}
    for dtype, twin_dtype, twin_ngram in (("fp32", "float32", "f32"), ("bf16", "bfloat16", "bf16")):
        for name in ("sol", "twin"):
            out = work / f"{name}_{dtype}"
            if out.exists():
                continue
            src = hf
            for attempt in range(2):
                if name == "sol":
                    repo = sol_repo
                    cmd = [str(python), "-B", "scripts/align_convert_qwen4_exp.py", str(src), str(out),
                           "--profile", dtype, "--group-size", "64", "--ple-storage", dtype]
                else:
                    repo = twin_repo
                    cmd = [str(python), "-B", "scripts/align_convert_qwen4_exp_twin.py", "--src", str(src),
                           "--out", str(out), "--dtype", twin_dtype, "--no-quantize",
                           "--ngram-format", twin_ngram]
                proc = subprocess.run(cmd, cwd=repo, env=dict(env, PYTHONPATH=str(repo)),
                                      capture_output=True, text=True, timeout=1800)
                if not proc.returncode:
                    break
                tail = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else ""
                if name == "twin" and attempt == 0 and "bfloat16" in tail:
                    # The twin reads shards with safetensors framework="mlx",
                    # which goes through numpy (no bfloat16): a bf16
                    # checkpoint, like the released one, cannot be read.
                    issues["twin_cannot_read_bf16_checkpoint"] = tail
                    import shutil
                    shutil.rmtree(out, ignore_errors=True)
                    src = work / "hf_f32"
                    if not src.exists():
                        upcast_checkpoint(hf, src)
                    continue
                raise RuntimeError(f"{name} {dtype} convert failed\n{proc.stdout[-3000:]}\n{proc.stderr[-6000:]}")
            issues[f"{name}_{dtype}_source"] = src.name
            print(f"[convert] {name} {dtype}: ok (source {src.name})")
    path = work / "convert_issues.json"
    old = json.loads(path.read_text()) if path.exists() else {}
    path.write_text(json.dumps(dict(old, **issues), indent=2))


# ===========================================================================
# Stage: MLX (both ports)
# ===========================================================================


def diff(a, b):
    """max abs, max-abs relative to the comparand's scale, cosine, top-1 agreement."""
    import numpy as np
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch {a.shape} vs {b.shape}")
    d = np.abs(a - b)
    scale = float(np.abs(b).max())
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    res = dict(max_abs=float(d.max()), rel=float(d.max() / scale) if scale else 0.0,
               cos=float((a * b).sum() / (na * nb)) if na and nb else 1.0,
               n=int(d.size))
    if a.ndim >= 2:
        res["top1"] = float((a.argmax(-1) == b.argmax(-1)).mean())
    return res


def bitwise(a, b):
    """Fraction of elements identical after rounding both to bf16."""
    import numpy as np
    to16 = lambda x: (np.ascontiguousarray(x, dtype=np.float32).view(np.uint32) >> 16)
    return float((to16(a) == to16(b)).mean())


class Port:
    """Uniform driver over the two ports' different call conventions."""

    def __init__(self, kind, path, dtype):
        import mlx.core as mx
        from mlx_lm.utils import load_model
        self.mx, self.kind, self.dtype = mx, kind, dtype
        self.model, _ = load_model(path, model_config=SOL_OVERRIDES if kind == "sol" else None)
        self.model.eval()
        self.g = type(self.model).__init__.__globals__  # the anonymous custom_model module

    def run(self, ids, cache=None, mask=None):
        mx = self.mx
        kw = {}
        if mask is not None and self.kind == "sol":
            kw["attention_mask"] = mx.array(mask)
        out = self.model(mx.array(ids), cache=cache, **kw)
        mx.eval(out)
        import numpy as np
        return np.array(out.astype(mx.float32))

    def make_cache(self, left_padding=None):
        if self.kind == "twin":
            return self.model.make_cache(left_padding=left_padding)
        return self.model.make_cache()

    def set_promote(self, on):
        assert self.kind == "sol"
        self.model.args.jw_bf16_fp32_ops = bool(on)


def apply_canonical(port):
    """Prototype of the recommended canonical numerics, applied to a FRESH
    Sol instance (its own module object; the plain Sol ports are untouched).

    Union of each port's reference-exact choices, plus fixes for the places
    where BOTH ports differ from transformers 5.22.1:
      1. RoPE inv_freq bit-identical to the reference (twin rope_inv_freq).
      2. Short-conv silu evaluated in fp32 and rounded once (twin), after
         mx conv1d (Sol; fp32-accumulated, rounded once).
      3. Hyper-connection silu AND sigmoids rounded once; fp32 stream mean.
      4. PLE gate: fp32 sum, fp32 division by sqrt(hidden), each rounded once
         (MLX rounds a Python scalar divisor to bf16; torch does not).
      5. MoE: expert and shared-expert silu rounded once; routed outputs
         summed in fp32 and rounded once (twin; the reference's default
         grouped_mm experts path); shared gate sigmoid rounded once.
      6. QSA indexer scores divided by sqrt(indexer_head_dim) as the reference
         (rank-preserving, but it decides which near-equal scores tie).
    Everything else is Sol with jw_bf16_fp32_ops on. FP32 casts are identity.
    """
    import math
    import numpy as np
    mx, g, m = port.mx, port.g, port.model
    nn = g["nn"]
    F32 = mx.float32
    a = m.args

    def once(fn, x):
        return fn(x.astype(F32)).astype(x.dtype)

    dim = int(a.head_dim * a.rope_parameters.get("partial_rotary_factor", 1))
    base = np.float64(np.float32(a.rope_parameters.get("rope_theta", 10000000)))
    expo = np.arange(0, dim, 2, dtype=np.float32) / np.float32(dim)
    inv = mx.array(np.float32(1.0) / np.power(base, expo.astype(np.float64)).astype(np.float32))

    def rope(x, positions, args):
        angles = positions[..., None].astype(F32) * inv
        cos = mx.concatenate([mx.cos(angles)] * 2, axis=-1).astype(x.dtype)
        sin = mx.concatenate([mx.sin(angles)] * 2, axis=-1).astype(x.dtype)
        while cos.ndim < x.ndim:
            cos, sin = mx.expand_dims(cos, -2), mx.expand_dims(sin, -2)
        lo, hi = x[..., :dim // 2], x[..., dim // 2:dim]
        rotated = x[..., :dim] * cos + mx.concatenate([-hi, lo], axis=-1) * sin
        return mx.concatenate([rotated, x[..., dim:]], axis=-1)

    def short_conv(conv, x, previous, dilation=1):
        history = (conv.weight.shape[1] - 1) * dilation
        if previous is None:
            previous = mx.zeros((x.shape[0], history, x.shape[-1]), dtype=x.dtype)
        full = mx.concatenate([previous, x], axis=1)
        return once(nn.silu, conv(full)), mx.contiguous(full[:, -history:]) if history else full[:, :0]

    g["rope"], g["short_conv"] = rope, short_conv
    L = m.layers

    def hc_call(self, x):
        n = self.hc_norm(x)
        w = once(mx.sigmoid, self.input_mix_weight_up(once(nn.silu, self.input_mix_weight_down(n) / self.h)))
        mixed = (w * n).reshape(*x.shape[:-1], self.h, self.d).astype(F32).mean(axis=-2).astype(x.dtype)
        if self.block_inject_weight is None:
            return mixed
        return mixed, 2 * once(mx.sigmoid, self.block_inject_weight(n) / self.h)

    type(L[0].attn_hyper_connection).__call__ = hc_call

    def ple_call(self, x, ids, mask, cache):
        a = self._args
        emb = self.ple_embedding(ids, cache).astype(x.dtype)
        shape = (*ids.shape, a.hc_count, a.hidden_size)
        key = self.norm_key(self.key_proj(emb)).reshape(shape)
        query = self.norm_query(x).reshape(shape)
        gate = (key * query).astype(F32).sum(axis=-1, keepdims=True).astype(x.dtype)
        gate = (gate.astype(F32) / math.sqrt(a.hidden_size)).astype(x.dtype)
        gate = mx.sqrt(mx.maximum(mx.abs(gate), 1e-6)) * mx.sign(gate)
        value = (once(mx.sigmoid, gate) * self.value_proj(emb)[..., None, :]).reshape(x.shape)
        normed = mx.where(mask[..., None], self.norm_conv(value), 0)
        conv, state = short_conv(self.conv1d, normed, cache[2] if cache else None, a.ngram_size)
        if cache is not None:
            cache[2] = state
        return mx.where(mask[..., None], value, 0) + conv

    type(L[PLE_LAYERS[0]].ple).__call__ = ple_call

    def swiglu(x_up, x_gate):
        return once(nn.silu, x_gate) * x_up

    for layer in L:
        sw = layer.mlp.switch_mlp
        if "activation" in sw:
            del sw["activation"]
        object.__setattr__(sw, "activation", swiglu)

    def mlp_call(self, x):
        return self.down_proj(once(nn.silu, self.gate_proj(x)) * self.up_proj(x))

    type(L[0].mlp.shared_expert).__call__ = mlp_call

    def moe_call(self, x):
        k = self._args.num_experts_per_tok
        probs = mx.softmax(self.gate(x).astype(F32), axis=-1)
        inds = mx.argpartition(-probs, k - 1, axis=-1)[..., :k]
        w = mx.take_along_axis(probs, inds, axis=-1)
        if self._args.norm_topk_prob:
            w = w / w.sum(axis=-1, keepdims=True)
        y = self.switch_mlp(x, inds) * w.astype(x.dtype)[..., None]
        # The reference's default experts path (transformers moe.py
        # grouped_mm_experts_forward) sums the k weighted bf16 rows in fp32
        # and rounds once (the twin's choice), not its eager index_add_.
        routed = y.astype(F32).sum(axis=-2).astype(x.dtype)
        return routed + once(mx.sigmoid, self.shared_expert_gate(x)) * self.shared_expert(x)

    type(L[0].mlp).__call__ = moe_call

    qsa_topk = g["qsa_topk"]

    def indexer_call(self, x, positions, valid, cache):
        # Sol QSAIndexer.__call__ (qwen4_exp.py:382-418) with the reference's
        # 1/sqrt(indexer_head_dim) score scale.
        a = self._args
        b, s, _ = x.shape
        qk = self.index_qk_proj(x)
        split = a.indexer_n_heads * a.indexer_head_dim
        q = rope(self.q_layernorm(qk[..., :split].reshape(b, s, a.indexer_n_heads, a.indexer_head_dim)), positions, a)
        raw = qk[..., split:]
        if cache is not None:
            if cache.raw_keys is not None:
                raw = mx.concatenate([cache.raw_keys, raw], axis=1)
            cache.raw_keys = raw
        t = raw.shape[1]
        if t <= a.indexer_budget:
            return None
        r = a.indexer_compress_ratio
        blocks = t // r
        left = t - valid.sum(axis=1)
        cols = left[:, None, None] + mx.arange(blocks)[None, :, None] * r + mx.arange(r)[None, None, :]
        cols = mx.minimum(cols.reshape(b, -1), t - 1)
        pooled = raw[mx.arange(b)[:, None], cols].reshape(b, blocks, r, a.indexer_head_dim)
        pooled = pooled.astype(F32).mean(axis=2).astype(raw.dtype)
        pooled = rope(self.k_layernorm(pooled), mx.broadcast_to(mx.arange(blocks)[None] * r, (b, blocks)), a)
        scores = mx.maximum(mx.einsum("bshd,bnd->bsnh", q.astype(F32), pooled.astype(F32)), 0).sum(axis=-1)
        scores = scores / math.sqrt(a.indexer_head_dim)
        complete = mx.maximum(positions + 1, 0) // r
        visible = mx.arange(blocks)[None, None] < complete[..., None]
        scores = mx.where(visible, scores, -mx.inf)
        top = qsa_topk(scores, min(a.indexer_budget // r, blocks))
        picked = mx.take_along_axis(visible, top, axis=-1)
        tok = left[:, None, None, None] + top[..., None] * r + mx.arange(r)[None, None, None]
        good = mx.broadcast_to(picked[..., None], tok.shape)
        tail = left[:, None, None] + complete[..., None] * r + mx.arange(r - 1)[None, None]
        tail_good = tail <= (left[:, None] + positions)[..., None]
        return (mx.concatenate([tok.reshape(b, s, -1), tail], axis=-1),
                mx.concatenate([good.reshape(b, s, -1), tail_good], axis=-1))

    type(L[QSA_LAYERS[0]].self_attn.indexer).__call__ = indexer_call
    port.set_promote(True)
    return port


def scenarios(port, seqs):
    import numpy as np
    sa, sb = seqs["seq_a"], seqs["seq_b"]
    res = {}

    def chunked(ids, n, prefix=None):
        cache, rows, start = port.make_cache(), [], 0
        if prefix is not None:
            port.run([ids[:prefix]], cache)
            start = prefix
        for s in range(start, len(ids), n):
            rows.append(port.run([ids[s:s + n]], cache)[0])
        return np.concatenate(rows)

    res["prefill"] = port.run([sa])[0]
    res["stepwise"] = chunked(sa, 1)
    res["chunked"] = chunked(sa, CHUNK)
    cache = port.make_cache(left_padding=[0, PAD_B])
    mask = np.array([[True] * LEN_A, [False] * PAD_B + [True] * LEN_B])
    rows = [port.run([sa, [EOS] * PAD_B + sb], cache, mask=mask)]
    for i in range(N_EXT):
        rows.append(port.run([[seqs["ext_a"][i]], [seqs["ext_b"][i]]], cache))
    res["padded"] = np.concatenate(rows, axis=1)
    res["single_a"] = chunked(sa + seqs["ext_a"], 1, prefix=LEN_A)
    res["single_b"] = chunked(sb + seqs["ext_b"], 1, prefix=LEN_B)
    res["long_prefill"] = port.run([seqs["long"]])[0]
    res["long_decode"] = chunked(seqs["long"], 1, prefix=LONG_PREFIX)
    res["long_chunked"] = chunked(seqs["long"], LONG_CHUNK)
    cache = port.make_cache()
    rows = [port.run([sa], cache)[0, -1]]
    toks = []
    for i in range(N_GREEDY):
        toks.append(int(rows[-1].argmax()))
        if i == N_GREEDY - 1:
            break
        rows.append(port.run([[toks[-1]]], cache)[0, -1])
    res["greedy_logits"] = np.stack(rows)
    res["greedy_tokens"] = np.array(toks)
    return res


def compare_scenarios(a, b, ref_side):
    """``ref_side``: b is a reference result dict (keys without 'greedy_tokens'
    as an array) when True. Padded rows compare valid positions only."""
    out = {}
    for key in ("prefill", "stepwise", "chunked", "long_prefill", "long_decode", "greedy_logits"):
        out[key] = diff(a[key], b[key])
    out["padded_row0"] = diff(a["padded"][0], b["padded"][0])
    out["padded_row1"] = diff(a["padded"][1, PAD_B:], b["padded"][1, PAD_B:])
    out["long_chunked"] = diff(a["long_chunked"], b["long_prefill" if ref_side else "long_chunked"])
    return out


def first_divergence(t1, t2):
    for i, (x, y) in enumerate(zip(t1, t2)):
        if int(x) != int(y):
            return i
    return None


class Tracer:
    """Class-level __call__ wrappers that record per-layer component outputs
    while a port runs normally (the free-running trace)."""

    def __init__(self, port):
        import numpy as np
        self.port, self.np, self.data, self.patches = port, np, {}, []
        m, mx = port.model, port.mx
        self.mx = mx
        self.where = {}
        for i, layer in enumerate(m.layers):
            self.where[id(layer)] = (i, "streams")
            self.where[id(layer.attn_hyper_connection)] = (i, "attn_hc")
            self.where[id(layer.mlp_hyper_connection)] = (i, "mlp_hc")
            self.where[id(layer.mlp)] = (i, "moe")
            mixer = layer.linear_attn if i not in QSA_LAYERS else layer.self_attn
            self.where[id(mixer)] = (i, "mix")
            if i in QSA_LAYERS:
                self.where[id(layer.self_attn.indexer)] = (i, "sel")
            if i in PLE_LAYERS:
                self.where[id(layer.ple)] = (i, "ple")

    def arr(self, x):
        self.mx.eval(x)
        return self.np.array(x.astype(self.mx.float32))

    def put(self, key, value):
        self.data[key] = value

    def __enter__(self):
        m = self.port.model
        L = m.layers
        q, lin, ple = L[QSA_LAYERS[0]], L[0], L[PLE_LAYERS[0]]
        classes = {type(lin): self._streams, type(lin.attn_hyper_connection): self._hc,
                   type(lin.mlp): self._moe, type(lin.linear_attn): self._mix,
                   type(q.self_attn): self._mix, type(q.self_attn.indexer): self._sel,
                   type(ple.ple): self._ple}
        for cls, post in classes.items():
            orig = cls.__call__

            def wrapper(this, *a, _orig=orig, _post=post, **k):
                o = _orig(this, *a, **k)
                if id(this) in self.where:
                    _post(this, a, k, o)
                return o

            cls.__call__ = wrapper
            self.patches.append((cls, orig))
        if self.port.kind == "twin":
            cls = type(lin.mlp)
            orig = cls.route

            def route(this, x, _orig=orig):
                o = _orig(this, x)
                if id(this) in self.where:
                    i, _ = self.where[id(this)]
                    self.put(f"L{i}.router.logits", self.arr(o[0]).reshape(-1, o[0].shape[-1]))
                    self.put(f"L{i}.router.experts", self.np.sort(self.np.array(o[1]).reshape(-1, o[1].shape[-1]), -1))
                return o

            cls.route = route
            self.patches.append((cls, orig, "route"))
        return self

    def __exit__(self, *exc):
        for p in self.patches:
            if len(p) == 3:
                setattr(p[0], p[2], p[1])
            else:
                p[0].__call__ = p[1]
        return False

    def _key(self, this):
        i, c = self.where[id(this)]
        return f"L{i}.{c}"

    def _streams(self, this, a, k, o):
        self.put(self._key(this), self.arr(o))

    def _hc(self, this, a, k, o):
        key = self._key(this)
        self.put(key + ".mixed", self.arr(o[0]))
        self.put(key + ".weights", self.arr(o[-1]))

    def _mix(self, this, a, k, o):
        self.put(self._key(this) + ".out", self.arr(o))

    def _ple(self, this, a, k, o):
        self.put(self._key(this) + ".out", self.arr(o))

    def _moe(self, this, a, k, o):
        mx, np = self.mx, self.np
        key = self._key(this)
        self.put(key + ".out", self.arr(o))
        if self.port.kind == "sol":
            # Recompute Sol's router exactly as SparseMoE.__call__ does.
            x = a[0]
            logits = this.gate(x)
            probs = mx.softmax(logits.astype(mx.float32), axis=-1)
            k_ = this._args.num_experts_per_tok
            inds = mx.argpartition(-probs, k_ - 1, axis=-1)[..., :k_]
            i = key.split(".")[0]
            self.put(f"{i}.router.logits", self.arr(logits).reshape(-1, logits.shape[-1]))
            self.put(f"{i}.router.experts", np.sort(np.array(inds).reshape(-1, k_), -1))

    def _sel(self, this, a, k, o):
        """Token-level selection mask [B, S, L] (incl. the query-local tail)."""
        np = self.np
        key = self._key(this)
        if self.port.kind == "sol":
            x, positions, valid = a[0], a[1], a[2]
            B, S = x.shape[:2]
            L = int(valid.shape[1])
            pos = np.array(positions)
            causal = np.arange(L)[None, None, :] <= (L - S + np.arange(S))[None, :, None]
            dense = causal & np.array(valid)[:, None, :]
            if o is None:
                self.put(key, dense)
                return
            tok, good = np.array(o[0]), np.array(o[1])
            m = np.zeros((B, S, L), dtype=bool)
            b_, s_, j_ = np.nonzero(good)
            m[b_, s_, tok[b_, s_, j_]] = True
            self.put(key, m)
        else:
            step, cache = a[1], a[2]
            L, S = cache.offset, step.S
            if isinstance(o, str) or o is None:
                t = L - S + np.arange(S)
                self.put(key, np.broadcast_to(np.arange(L)[None, None, :] <= t[None, :, None], (step.B, S, L)).copy())
            else:
                self.put(key, np.array(o[:, 0]))
            sel = getattr(this, "_last_selection", None)
            if sel is not None:
                self.put(key + ".scores", self.arr(sel.scores))


def block_selection(mask, n_queries):
    """Token mask [S, L] -> per-query selected complete blocks (unpadded row)."""
    import numpy as np
    out = []
    for t in range(n_queries):
        nt = (t + 1) // RATIO
        out.append(frozenset(j for j in range(nt) if mask[t, j * RATIO]))
    return out


def selection_agreement(m1, m2, scores=None):
    """Per-query block-set agreement; disagreements classified as exact ties
    (every differing block scores exactly the K-th score) when scores given."""
    import numpy as np
    S = m1.shape[0]
    b1, b2 = block_selection(m1, S), block_selection(m2, S)
    differ = [t for t in range(S) if b1[t] != b2[t]]
    ties = 0
    for t in differ:
        if scores is None:
            continue
        nt = (t + 1) // RATIO
        if nt <= TOPK:
            continue
        s = scores[t, :nt]
        kth = np.sort(s)[::-1][TOPK - 1]
        if all(s[j] == kth for j in (b1[t] ^ b2[t])):
            ties += 1
    sparse = sum(1 for t in range(S) if (t + 1) // RATIO > TOPK)
    return dict(queries=S, sparse_queries=sparse, differ=len(differ),
                differ_exact_ties=ties if scores is not None else None,
                token_mask_equal=bool(np.array_equal(m1, m2)))


def isolated(port, ref, tag):
    """Each component fed the reference's exact captured input."""
    import numpy as np
    mx = port.mx
    m = port.model
    dt = mx.float32 if tag == "f32" else mx.bfloat16
    cap = lambda k: ref[f"{tag}.cap.{k}"]
    to = lambda a: mx.array(np.asarray(a, dtype=np.float32)).astype(dt)

    def arr(x):
        mx.eval(x)
        return np.array(x.astype(mx.float32))

    res = {}
    B, S = 1, LEN_A
    mask = mx.ones((B, S), dtype=mx.bool_)
    step = None
    if port.kind == "twin":
        step = port.g["_Step"](B, S, 0, np.zeros((B,), np.int64), m.language_model._inv_freq)
    tracer = Tracer(port)
    with tracer:
        for i, layer in enumerate(m.layers):
            p = f"L{i}."
            if i in PLE_LAYERS:
                h, ids = to(cap(p + "ple.in")), cap(p + "ple.ids")
                if port.kind == "sol":
                    y = layer.ple(h, mx.array(ids.astype(np.int32)), mask, None)
                else:
                    st = port.g["_Step"](B, S, 0, np.zeros((B,), np.int64), m.language_model._inv_freq)
                    m.language_model._gather_ngrams(ids.astype(np.int64), st, m.make_cache(), dt)
                    y = layer.ple(h, st.ngram_emb[i], st, None)
                res[p + "ple"] = arr(y)
            for hc in ("attn_hc", "mlp_hc"):
                mod = layer.attn_hyper_connection if hc == "attn_hc" else layer.mlp_hyper_connection
                o = mod(to(cap(p + hc + ".in")))
                res[p + hc + ".mixed"], res[p + hc + ".weights"] = arr(o[0]), arr(o[-1])
            x = to(cap(p + "mix.in"))
            if i in QSA_LAYERS:
                if port.kind == "sol":
                    y = layer.self_attn(x, mask, None)
                else:
                    y = layer.self_attn(x, step, m.make_cache()[i])
            else:
                y = layer.linear_attn(x, mask, None) if port.kind == "sol" else layer.linear_attn(x, step, None)
            res[p + "mix"] = arr(y)
            res[p + "moe"] = arr(layer.mlp(to(cap(p + "moe.in"))))
        res["mixer"] = arr(m.model.hyper_connection_mixer(to(cap("mixer.in"))) if port.kind == "sol"
                           else m.language_model.model.hyper_connection_mixer(to(cap("mixer.in"))))
        head = m.lm_head if port.kind == "sol" else m.language_model.lm_head
        res["head"] = arr(head(to(cap("head.in"))))
    # Router logits/experts and QSA selections come from the tracer.
    for k, v in tracer.data.items():
        if ".router." in k or k.endswith(".sel") or k.endswith(".sel.scores"):
            res[k] = v
    return res


def stage_mlx(work):
    import mlx.core as mx
    import numpy as np
    from mlx.utils import tree_flatten

    ref_npz = np.load(work / "ref.npz")
    ref = {k: ref_npz[k] for k in ref_npz.files}
    meta = json.loads((work / "ref_meta.json").read_text())
    seqs = meta["seqs"]
    R = {"versions": dict(mlx=mx.__version__, mlx_lm=__import__("mlx_lm").__version__,
                          device=str(mx.default_device())),
         "ref_meta": {k: meta.get(k) for k in ("ties", "torch", "transformers", "attn_implementation",
                                               "experts_implementation", "n_shards")}}
    t0 = time.time()

    def refs(tag):
        d = {k.split(".", 1)[1]: v for k, v in ref.items() if k.startswith(tag + ".") and ".cap." not in k}
        return d

    ports = {f"{kind}_{tag}": Port(kind, work / f"{kind}_{'fp32' if tag == 'f32' else 'bf16'}", tag)
             for kind in ("sol", "twin") for tag in ("f32", "b16")}
    for tag in ("f32", "b16"):
        ports[f"canon_{tag}"] = apply_canonical(Port("sol", work / f"sol_{'fp32' if tag == 'f32' else 'bf16'}", tag))

    # --- identical weights? -------------------------------------------------
    weights = {}
    for tag in ("f32", "b16"):
        ps = dict(tree_flatten(ports[f"sol_{tag}"].model.parameters()))
        pt = {k.replace("language_model.", "", 1): v
              for k, v in tree_flatten(ports[f"twin_{tag}"].model.parameters())}
        common = sorted(set(ps) & set(pt))
        unequal = [k for k in common if ps[k].dtype != pt[k].dtype or ps[k].shape != pt[k].shape
                   or not bool(mx.array_equal(ps[k], pt[k]).item())]
        weights[tag] = dict(sol_params=len(ps), twin_params=len(pt), common=len(common),
                            only_sol=sorted(set(ps) - set(pt)), only_twin=sorted(set(pt) - set(ps)),
                            bitwise_unequal=unequal)
    R["weights"] = weights

    # --- scenarios ------------------------------------------------------------
    runs = {}
    for name, port in ports.items():
        runs[name] = scenarios(port, seqs)
    ports["sol_b16"].set_promote(False)
    runs["solOff_b16"] = scenarios(ports["sol_b16"], seqs)
    ports["sol_b16"].set_promote(True)
    rf32, rb16 = refs("f32"), refs("b16")
    pairs = {
        "f32": [("sol_f32", "twin_f32"), ("sol_f32", "REF_f32"), ("twin_f32", "REF_f32"),
                ("canon_f32", "REF_f32")],
        "b16": [("sol_b16", "twin_b16"), ("solOff_b16", "twin_b16"),
                ("sol_b16", "REF_b16"), ("solOff_b16", "REF_b16"), ("twin_b16", "REF_b16"),
                ("canon_b16", "REF_b16"),
                ("sol_b16", "REF_f32"), ("solOff_b16", "REF_f32"), ("twin_b16", "REF_f32"),
                ("canon_b16", "REF_f32"), ("REF_b16", "REF_f32")],
    }
    named = dict(runs, REF_f32=rf32, REF_b16=rb16)
    R["scenarios"] = {}
    for tag, plist in pairs.items():
        for a, b in plist:
            if a.startswith("REF"):
                # Reference noise floor: bf16 reference vs fp32 reference.
                ra, rb = named[a], named[b]
                R["scenarios"][f"{a}|{b}"] = {k: diff(ra[k], rb[k]) for k in
                                             ("prefill", "stepwise", "chunked", "long_prefill",
                                              "long_decode", "greedy_logits")}
                R["scenarios"][f"{a}|{b}"]["padded_row0"] = diff(ra["padded"][0], rb["padded"][0])
                R["scenarios"][f"{a}|{b}"]["padded_row1"] = diff(ra["padded"][1, PAD_B:], rb["padded"][1, PAD_B:])
                continue
            R["scenarios"][f"{a}|{b}"] = compare_scenarios(named[a], named[b], b.startswith("REF"))
    # Greedy: first divergent token for every pair.
    greedy = {}
    toks = {k: [int(t) for t in v["greedy_tokens"]] for k, v in runs.items()}
    toks["REF_f32"], toks["REF_b16"] = meta["greedy_tokens_f32"], meta["greedy_tokens_b16"]
    for a, b in [p for plist in pairs.values() for p in plist]:
        fd = first_divergence(toks[a], toks[b])
        entry = dict(first_divergent_token=fd, equal=fd is None)
        if fd is not None and b.startswith("REF"):
            # Margin of the reference's own top-2 at the divergence point.
            row = np.sort(named[b]["greedy_tf"][fd])[::-1]
            entry["ref_top2_margin_at_divergence"] = float(row[0] - row[1])
        greedy[f"{a}|{b}"] = entry
    R["greedy"] = dict(pairs=greedy, tokens=toks)
    # Teacher-forced along the reference's greedy path (isolates generation
    # divergence from logit disagreement).
    tf = {}
    for name, port in ports.items():
        tag = name.split("_")[1]
        path = seqs["seq_a"] + meta[f"greedy_tokens_{tag}"]
        rows = port.run([path])[0][LEN_A - 1:LEN_A - 1 + N_GREEDY]
        tf[name] = diff(rows, ref[f"{tag}.greedy_tf"])
    ports["sol_b16"].set_promote(False)
    rows = ports["sol_b16"].run([seqs["seq_a"] + meta["greedy_tokens_b16"]])[0][LEN_A - 1:LEN_A - 1 + N_GREEDY]
    tf["solOff_b16"] = diff(rows, ref["b16.greedy_tf"])
    ports["sol_b16"].set_promote(True)
    R["greedy"]["teacher_forced_vs_ref"] = tf
    # Tie effect: the same ports against the reference with torch.topk's own
    # CPU tie order, and the two reference tie orders against each other.
    tie_effect = {}
    for tag in ("f32", "b16"):
        rd = refs(tag + "D")
        r0 = rf32 if tag == "f32" else rb16
        tie_effect[f"REF_{tag}|REFdefault_{tag}"] = {
            k: diff(r0[k], rd[k]) for k in ("prefill", "stepwise", "chunked", "long_prefill", "long_decode")}
        tie_effect[f"REF_{tag}|REFdefault_{tag}"]["padded_row0"] = diff(r0["padded"][0], rd["padded"][0])
        tie_effect[f"REF_{tag}|REFdefault_{tag}"]["padded_row1"] = diff(r0["padded"][1, PAD_B:], rd["padded"][1, PAD_B:])
        for n in (f"sol_{tag}", f"twin_{tag}"):
            tie_effect[f"{n}|REFdefault_{tag}"] = compare_scenarios(runs[n], rd, True)
        tie_effect[f"greedy REF_{tag}|REFdefault_{tag}"] = first_divergence(
            meta[f"greedy_tokens_{tag}"], meta[f"greedy_tokens_{tag}D"])
    R["tie_effect"] = tie_effect
    # Port-internal invariants.
    R["internal"] = {}
    for name, r in runs.items():
        R["internal"][name] = dict(
            prefill_vs_stepwise=diff(r["stepwise"], r["prefill"]),
            prefill_vs_chunked=diff(r["chunked"], r["prefill"]),
            long_prefill_vs_chunked=diff(r["long_chunked"], r["long_prefill"]),
            padded_row0_vs_batch1=diff(r["padded"][0], np.concatenate([r["prefill"], r["single_a"]])),
            padded_row1_vs_batch1=diff(r["padded"][1, PAD_B:], np.concatenate(
                [port_prefill_b(ports, name, seqs), r["single_b"]])),
        )

    # --- per-layer traces (free-running prefill of seq_a) ---------------------
    traces = {}
    for name, port in list(ports.items()) + [("solOff_b16", ports["sol_b16"])]:
        if name == "solOff_b16":
            port.set_promote(False)
        if port.kind == "twin":
            type(port.model.layers[QSA_LAYERS[0]].self_attn.indexer).record_selection = True
        tr = Tracer(port)
        with tr:
            port.run([seqs["seq_a"]])
        traces[name] = tr.data
        if port.kind == "twin":
            type(port.model.layers[QSA_LAYERS[0]].self_attn.indexer).record_selection = False
        if name == "solOff_b16":
            port.set_promote(True)
    R["trace"] = trace_tables(traces, ref)

    # --- isolated components (identical, reference-captured inputs) ----------
    iso = {}
    for name, port in list(ports.items()) + [("solOff_b16", ports["sol_b16"])]:
        tag = name.split("_")[1]
        if name == "solOff_b16":
            port.set_promote(False)
        if port.kind == "twin":
            type(port.model.layers[QSA_LAYERS[0]].self_attn.indexer).record_selection = True
        iso[name] = isolated(port, ref, tag)
        if port.kind == "twin":
            type(port.model.layers[QSA_LAYERS[0]].self_attn.indexer).record_selection = False
        if name == "solOff_b16":
            port.set_promote(True)
    R["isolated"] = isolated_tables(iso, ref)

    # --- forced exact-tie QSA probe (fp32) --------------------------------------
    tie = {}
    for kind in ("sol", "twin"):
        port = ports[f"{kind}_f32"]
        mod = port.model.layers[TIE_LAYER].self_attn.indexer.index_qk_proj
        saved = mod.weight
        mod.weight = mx.zeros_like(saved)
        if kind == "twin":
            type(port.model.layers[TIE_LAYER].self_attn.indexer).record_selection = True
        tr = Tracer(port)
        with tr:
            tie[kind] = port.run([seqs["seq_a"]])[0]
        tie[kind + "_sel"] = tr.data[f"L{TIE_LAYER}.sel"][0]
        mod.weight = saved
        if kind == "twin":
            type(port.model.layers[TIE_LAYER].self_attn.indexer).record_selection = False
    R["tie_probe"] = {
        "sol|twin": diff(tie["sol"], tie["twin"]),
        "sol|twin_selection": selection_agreement(tie["sol_sel"], tie["twin_sel"]),
        "sol|REF_lowest_index": diff(tie["sol"], ref["f32.tie_lowest_index"]),
        "twin|REF_lowest_index": diff(tie["twin"], ref["f32.tie_lowest_index"]),
        "sol|REF_default_topk": diff(tie["sol"], ref["f32.tie_default"]),
        "twin|REF_default_topk": diff(tie["twin"], ref["f32.tie_default"]),
        "REF_default|REF_lowest_index": diff(ref["f32.tie_default"], ref["f32.tie_lowest_index"]),
        "ref_ties": meta["ties"].get("probe_default"),
    }
    R["elapsed_s"] = time.time() - t0
    R["peak_rss"] = peak_rss()
    (work / "results.json").write_text(json.dumps(R, indent=2))
    np.savez(work / "mlx_runs.npz", **{f"{n}.{k}": v for n, r in runs.items() for k, v in r.items()})
    print(json.dumps({"elapsed_s": R["elapsed_s"], "peak_rss": R["peak_rss"]}))


def port_prefill_b(ports, name, seqs):
    """Batch-1 prefill logits of seq_b on the same port configuration."""
    port = ports[name if name in ports else "sol_b16"]
    if name == "solOff_b16":
        port.set_promote(False)
    try:
        return port.run([seqs["seq_b"]])[0]
    finally:
        if name == "solOff_b16":
            port.set_promote(True)


def trace_tables(traces, ref):
    """Per layer and component: port vs port, port vs reference (same run)."""
    import numpy as np
    out = {}
    for tag in ("f32", "b16"):
        names = [n for n in traces if n.endswith(tag)]
        r = {k.split(".cap.", 1)[1]: v for k, v in ref.items() if k.startswith(f"{tag}.cap.")}
        rows = []
        for i in range(N_LAYERS):
            p = f"L{i}."
            comps = []
            if i in PLE_LAYERS:
                comps.append(("PLE", p + "ple.out", p + "ple.out"))
            comps.append(("attn HC mix", p + "attn_hc.mixed", p + "attn_hc.mixed"))
            comps.append(("attn HC weights", p + "attn_hc.weights", p + "attn_hc.weights"))
            comps.append(("QSA out" if i in QSA_LAYERS else "DeltaNet out", p + "mix.out", p + "mix.out"))
            comps.append(("router logits", p + "router.logits", p + "router.logits"))
            comps.append(("MoE out", p + "moe.out", p + "moe.out"))
            comps.append(("streams", p + "streams", p + "streams"))
            for label, kp, kr in comps:
                row = dict(layer=i, component=label)
                for n in names:
                    a = traces[n][kp].reshape(r[kr].shape)
                    row[f"{n}|REF"] = diff(a, r[kr])
                for n1, n2 in (("sol_" + tag, "twin_" + tag), ("solOff_" + tag, "twin_" + tag)):
                    if n1 in traces and n2 in traces:
                        row[f"{n1}|{n2}"] = diff(traces[n1][kp], traces[n2][kp])
                rows.append(row)
            # Chosen experts: fraction of tokens with identical expert sets.
            row = dict(layer=i, component="experts (set agreement)")
            ref_e = np.sort(r[p + "router.experts"], -1)
            for n in names:
                row[f"{n}|REF"] = float((traces[n][p + "router.experts"] == ref_e).all(-1).mean())
            for n1, n2 in (("sol_" + tag, "twin_" + tag), ("solOff_" + tag, "twin_" + tag)):
                if n1 in traces and n2 in traces:
                    row[f"{n1}|{n2}"] = float((traces[n1][p + "router.experts"] ==
                                               traces[n2][p + "router.experts"]).all(-1).mean())
            rows.append(row)
            if i in QSA_LAYERS:
                row = dict(layer=i, component="QSA block selection")
                tw = traces["twin_" + tag]
                scores = tw.get(p + "sel.scores")
                scores = None if scores is None else scores[0]
                for n in names:
                    row[f"{n}|REF"] = selection_agreement(traces[n][p + "sel"][0], r[p + "sel"][0], scores)
                for n1, n2 in (("sol_" + tag, "twin_" + tag), ("solOff_" + tag, "twin_" + tag)):
                    if n1 in traces and n2 in traces:
                        row[f"{n1}|{n2}"] = selection_agreement(traces[n1][p + "sel"][0],
                                                                traces[n2][p + "sel"][0], scores)
                rows.append(row)
        out[tag] = rows
    return out


def isolated_tables(iso, ref):
    import numpy as np
    out = {}
    for tag in ("f32", "b16"):
        names = [n for n in iso if n.endswith(tag)]
        r = {k.split(".cap.", 1)[1]: v for k, v in ref.items() if k.startswith(f"{tag}.cap.")}
        rows = []

        def add(label, layer, key, rkey):
            row = dict(layer=layer, component=label)
            for n in names:
                a = iso[n][key].reshape(r[rkey].shape)
                row[f"{n}|REF"] = diff(a, r[rkey])
                row[f"{n}|REF"]["bf16_bitwise_equal"] = bitwise(a, r[rkey])
            for n1, n2 in (("sol_" + tag, "twin_" + tag), ("solOff_" + tag, "twin_" + tag)):
                if n1 in iso and n2 in iso:
                    row[f"{n1}|{n2}"] = diff(iso[n1][key], iso[n2][key])
                    row[f"{n1}|{n2}"]["bf16_bitwise_equal"] = bitwise(iso[n1][key], iso[n2][key])
            rows.append(row)

        for i in range(N_LAYERS):
            p = f"L{i}."
            if i in PLE_LAYERS:
                add("PLE", i, p + "ple", p + "ple.out")
            add("attn HC mix", i, p + "attn_hc.mixed", p + "attn_hc.mixed")
            add("attn HC weights", i, p + "attn_hc.weights", p + "attn_hc.weights")
            add("QSA" if i in QSA_LAYERS else "DeltaNet", i, p + "mix", p + "mix.out")
            add("mlp HC mix", i, p + "mlp_hc.mixed", p + "mlp_hc.mixed")
            add("mlp HC weights", i, p + "mlp_hc.weights", p + "mlp_hc.weights")
            add("router logits", i, p + "router.logits", p + "router.logits")
            add("MoE", i, p + "moe", p + "moe.out")
            row = dict(layer=i, component="experts (set agreement)")
            ref_e = np.sort(r[p + "router.experts"], -1)
            for n in names:
                row[f"{n}|REF"] = float((iso[n][p + "router.experts"] == ref_e).all(-1).mean())
            rows.append(row)
            if i in QSA_LAYERS:
                row = dict(layer=i, component="QSA block selection")
                scores = iso["twin_" + tag].get(p + "sel.scores")
                scores = None if scores is None else scores[0]
                for n in names:
                    row[f"{n}|REF"] = selection_agreement(iso[n][p + "sel"][0], r[p + "sel"][0], scores)
                for n1, n2 in (("sol_" + tag, "twin_" + tag), ("solOff_" + tag, "twin_" + tag)):
                    if n1 in iso and n2 in iso:
                        row[f"{n1}|{n2}"] = selection_agreement(iso[n1][p + "sel"][0], iso[n2][p + "sel"][0], scores)
                rows.append(row)
        add("final mixer", "final", "mixer", "mixer.out")
        add("lm_head", "final", "head", "head.out")
        out[tag] = rows
    return out


# ===========================================================================
# Diagnostics (op-level evidence behind the resolutions; torch + MLX)
# ===========================================================================


def stage_diag(work):
    """Op-level probes cited in the doc: bf16 rounding of MLX vs torch ops,
    RoPE inverse frequencies, the twin converter's bf16 read path, and the
    QSA attention core on identical bf16 q/k/v (layer 7, no ties)."""
    import math
    import numpy as np
    import torch
    import mlx.core as mx
    import mlx.nn as nn
    torch.set_num_threads(2)
    out = {}
    u = np.arange(0, 1 << 16, dtype=np.uint32)
    f = (u << 16).view(np.float32)
    f = f[np.isfinite(f) & (np.abs(f) <= 20)]
    t, m = torch.from_numpy(f).to(torch.bfloat16), mx.array(f).astype(mx.bfloat16)

    def frac(a, b):
        a = a.float().numpy() if isinstance(a, torch.Tensor) else np.array(a.astype(mx.float32))
        return float(np.mean(a != np.array(b.astype(mx.float32))))

    F32 = mx.float32
    out["ops_mismatch_vs_torch_all_bf16_in_[-20,20]"] = {
        "sigmoid native": frac(torch.sigmoid(t), mx.sigmoid(m)),
        "sigmoid fp32 then round": frac(torch.sigmoid(t), mx.sigmoid(m.astype(F32)).astype(mx.bfloat16)),
        "silu native": frac(torch.nn.functional.silu(t), nn.silu(m)),
        "silu fp32 then round": frac(torch.nn.functional.silu(t), nn.silu(m.astype(F32)).astype(mx.bfloat16)),
    }
    rng = np.random.default_rng(0)
    red = {}
    for name, shape in (("mean over 4", (20000, 4)), ("sum over 64", (20000, 64))):
        x = rng.normal(size=shape).astype(np.float32)
        tx, mxx = torch.from_numpy(x).to(torch.bfloat16), mx.array(x).astype(mx.bfloat16)
        op = (lambda a: a.mean(-1)) if "mean" in name else (lambda a: a.sum(-1))
        red[name + " native"] = frac(op(tx), op(mxx))
        red[name + " fp32 then round"] = frac(op(tx), op(mxx.astype(F32)).astype(mx.bfloat16))
    x = rng.normal(size=200000).astype(np.float32) * 4
    tx, mxx = torch.from_numpy(x).to(torch.bfloat16), mx.array(x).astype(mx.bfloat16)
    for H in (96, 2560):
        red[f"bf16 / sqrt({H}) python scalar"] = frac(tx / math.sqrt(H), mxx / math.sqrt(H))
        red[f"bf16 / sqrt({H}) in fp32 then round"] = frac(tx / math.sqrt(H), (mxx.astype(F32) / math.sqrt(H)).astype(mx.bfloat16))
    out["reductions_and_scalars_mismatch_vs_torch"] = red
    rope = {}
    for theta, dim in ((1e7, 16), (1e7, 64)):
        ref = (1.0 / (theta ** (torch.arange(0, dim, 2, dtype=torch.float) / dim))).numpy()
        sol = np.array(theta ** (-mx.arange(0, dim, 2) / dim))
        base = np.float64(np.float32(theta))
        e = np.arange(0, dim, 2, dtype=np.float32) / np.float32(dim)
        twin = np.float32(1.0) / np.power(base, e.astype(np.float64)).astype(np.float32)
        entry = {"sol_entries_differing": int((sol != ref).sum()), "twin_entries_differing": int((twin != ref).sum()),
                 "entries": len(ref)}
        for P in (320, 8192, 40960):
            pos = np.arange(P, dtype=np.float32)[:, None]
            entry[f"sol_max_angle_error_rad_pos<{P}"] = float(np.abs((pos * ref).astype(np.float64) - (pos * sol).astype(np.float64)).max())
        rope[f"theta={theta:g},rotary_dim={dim}"] = entry
    out["rope_inv_freq"] = rope
    from safetensors import safe_open
    from safetensors.torch import save_file
    probe = TMPDIR / "diag_bf16.safetensors"
    save_file({"w": torch.ones(2, 2, dtype=torch.bfloat16)}, str(probe))
    try:
        with safe_open(str(probe), framework="mlx") as fh:
            fh.get_tensor("w")
        out["safetensors_framework_mlx_reads_bf16"] = True
    except Exception as exc:
        out["safetensors_framework_mlx_reads_bf16"] = f"{type(exc).__name__}: {exc}"
    out["mx_load_reads_bf16"] = str(mx.load(str(probe))["w"].dtype)
    # QSA attention core, layer 7 (no exact ties), identical bf16 inputs.
    from transformers import Qwen4ExpForConditionalGeneration
    from transformers.integrations.sdpa_attention import sdpa_attention_forward
    from transformers.models.qwen4_exp.modeling_qwen4_exp import apply_rotary_pos_emb
    refz = np.load(work / "ref.npz")
    L = QSA_LAYERS[1]
    model = Qwen4ExpForConditionalGeneration.from_pretrained(work / "hf", dtype=torch.bfloat16,
                                                             attn_implementation="sdpa").eval()
    lm = model.model.language_model
    attn = lm.layers[L].self_attn
    x = torch.from_numpy(refz[f"b16.cap.L{L}.mix.in"]).to(torch.bfloat16)
    S = x.shape[1]
    with torch.no_grad():
        cos, sin = lm.rotary_emb(x, torch.arange(S)[None, None].expand(3, 1, S))
        q, gate = torch.chunk(attn.q_proj(x).view(1, S, -1, attn.head_dim * 2), 2, dim=-1)
        q = attn.q_norm(q).transpose(1, 2)
        k = attn.k_norm(attn.k_proj(x).view(1, S, -1, attn.head_dim)).transpose(1, 2)
        v = attn.v_proj(x).view(1, S, -1, attn.head_dim).transpose(1, 2)
        q, k = apply_rotary_pos_emb(q, k, cos, sin)
        mask = (torch.from_numpy(refz[f"b16.cap.L{L}.sel"][0]) & torch.tril(torch.ones(S, S, dtype=torch.bool)))[None, None]
        o_t, _ = sdpa_attention_forward(attn, q, k, v, mask, dropout=0.0, scaling=attn.scaling)
        o_t = o_t.reshape(1, S, -1)
        y_t = attn.o_proj(o_t * torch.sigmoid(gate.reshape(1, S, -1)))
    o_m = mx.fast.scaled_dot_product_attention(
        mx.array(q.float().numpy()).astype(mx.bfloat16), mx.array(k.float().numpy()).astype(mx.bfloat16),
        mx.array(v.float().numpy()).astype(mx.bfloat16), scale=attn.scaling, mask=mx.array(mask.numpy()))
    o_m = np.array(o_m.transpose(0, 2, 1, 3).reshape(1, S, -1).astype(F32))
    out[f"qsa_L{L}_attention_core_bf16"] = {
        "mlx_sdpa_vs_torch_sdpa_identical_qkv_bitwise": bitwise(o_m, o_t.float().numpy()),
        "torch_layer_recomputed_vs_its_own_capture_bitwise": bitwise(y_t.float().numpy(),
                                                                     refz[f"b16.cap.L{L}.mix.out"]),
    }
    (work / "diag.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


# ===========================================================================
# Report
# ===========================================================================


def fmt(x):
    if x is None:
        return "-"
    if isinstance(x, float):
        if x == 0:
            return "0"
        return f"{x:.2e}" if abs(x) < 1e-2 or abs(x) >= 1e3 else f"{x:.4f}"
    return str(x)


def compact_tables(R):
    """Doc-ready summary tables: one row per scenario, one column per pair,
    each cell 'max abs / cosine'."""
    lines = []
    w = lines.append
    keys = ["prefill", "stepwise", "chunked", "padded_row0", "padded_row1", "long_prefill",
            "long_decode", "long_chunked"]
    groups = {
        "fp32": ["sol_f32|twin_f32", "sol_f32|REF_f32", "twin_f32|REF_f32", "canon_f32|REF_f32"],
        "bf16 port vs port": ["sol_b16|twin_b16", "solOff_b16|twin_b16"],
        "bf16 vs bf16 reference": ["sol_b16|REF_b16", "solOff_b16|REF_b16", "twin_b16|REF_b16",
                                   "canon_b16|REF_b16"],
        "bf16 vs fp32 reference": ["sol_b16|REF_f32", "solOff_b16|REF_f32", "twin_b16|REF_f32",
                                   "canon_b16|REF_f32", "REF_b16|REF_f32"],
    }
    for title, cols in groups.items():
        w(f"\n#### {title}: max abs / cosine\n")
        w("| scenario | " + " | ".join(c.replace("|", " vs ") for c in cols) + " |")
        w("|---|" + "---:|" * len(cols))
        for k in keys:
            cells = []
            for c in cols:
                e = R["scenarios"].get(c, {}).get(k)
                cells.append("-" if e is None else f"{fmt(e['max_abs'])} / {e['cos']:.6f}")
            w(f"| {k} | " + " | ".join(cells) + " |")
    if "tie_effect" in R:
        w("\n#### Against torch.topk's own CPU tie order (REFdefault): max abs\n")
        cols = [c for c in R["tie_effect"] if not c.startswith("greedy")]
        w("| scenario | " + " | ".join(c.replace("|", " vs ") for c in cols) + " |")
        w("|---|" + "---:|" * len(cols))
        for k in keys:
            cells = [fmt(R["tie_effect"][c][k]["max_abs"]) if k in R["tie_effect"][c] else "-" for c in cols]
            w(f"| {k} | " + " | ".join(cells) + " |")
        w("\n" + ", ".join(f"{c}: first divergent greedy token {v}" for c, v in R["tie_effect"].items()
                           if c.startswith("greedy")))
    return "\n".join(lines) + "\n"


def stage_report(work):
    R = json.loads((work / "results.json").read_text())
    lines = []
    w = lines.append
    w(compact_tables(R))
    sc = R["scenarios"]
    w("### Scenario logits (max abs / rel / cosine / top-1)\n")
    keys = ["prefill", "stepwise", "chunked", "padded_row0", "padded_row1", "long_prefill",
            "long_decode", "long_chunked", "greedy_logits"]
    for pair, d in sc.items():
        w(f"\n**{pair.replace('|', ' vs ')}**\n")
        w("| scenario | max abs | rel | cosine | top-1 |")
        w("|---|---:|---:|---:|---:|")
        for k in keys:
            if k in d:
                e = d[k]
                w(f"| {k} | {fmt(e['max_abs'])} | {fmt(e['rel'])} | {e['cos']:.9f} | {fmt(e.get('top1'))} |")
    w("\n### Greedy 32 tokens\n")
    w("| pair | first divergent token | ref top-2 margin there |")
    w("|---|---:|---:|")
    for pair, e in R["greedy"]["pairs"].items():
        w(f"| {pair.replace('|', ' vs ')} | {fmt(e['first_divergent_token']) if not e['equal'] else 'none (32/32 equal)'} | "
          f"{fmt(e.get('ref_top2_margin_at_divergence'))} |")
    w("\n### Teacher-forced along the reference greedy path\n")
    w("| port | max abs | cosine | top-1 |")
    w("|---|---:|---:|---:|")
    for n, e in R["greedy"]["teacher_forced_vs_ref"].items():
        w(f"| {n} | {fmt(e['max_abs'])} | {e['cos']:.9f} | {fmt(e.get('top1'))} |")
    w("\n### Port-internal invariants (max abs)\n")
    w("| run | prefill vs stepwise | prefill vs chunked | long prefill vs chunked | padded row0 vs batch-1 | padded row1 vs batch-1 |")
    w("|---|---:|---:|---:|---:|---:|")
    for n, e in R["internal"].items():
        w(f"| {n} | " + " | ".join(fmt(e[k]["max_abs"]) for k in
                                   ("prefill_vs_stepwise", "prefill_vs_chunked", "long_prefill_vs_chunked",
                                    "padded_row0_vs_batch1", "padded_row1_vs_batch1")) + " |")
    for kind in ("trace", "isolated"):
        for tag in ("f32", "b16"):
            rows = R[kind][tag]
            cols = sorted({k for r in rows for k in r if "|" in k})
            w(f"\n### {kind} {tag}: max abs (bf16-bitwise-equal fraction for isolated b16)\n")
            w("| layer | component | " + " | ".join(c.replace("|", " vs ") for c in cols) + " |")
            w("|---|---|" + "---:|" * len(cols))
            for r in rows:
                cells = []
                for c in cols:
                    v = r.get(c)
                    if isinstance(v, dict) and "max_abs" in v:
                        s = fmt(v["max_abs"])
                        if tag == "b16" and kind == "isolated":
                            s += f" ({v['bf16_bitwise_equal']:.3f})"
                        cells.append(s)
                    elif isinstance(v, dict):
                        s = f"{v['differ']}/{v['sparse_queries']} differ"
                        if v.get("differ_exact_ties") is not None and v["differ"]:
                            s += f", {v['differ_exact_ties']} ties"
                        cells.append(s)
                    else:
                        cells.append(fmt(v))
                w(f"| {r['layer']} | {r['component']} | " + " | ".join(cells) + " |")
    w("\n### Forced exact-tie QSA probe (fp32)\n")
    for k, v in R["tie_probe"].items():
        w(f"- {k}: {json.dumps(v)}")
    w(f"\n### Weights\n\n```\n{json.dumps(R['weights'], indent=1)}\n```")
    w(f"\nversions {R['versions']}; reference {R['ref_meta']}; elapsed {R['elapsed_s']:.1f}s; peak RSS {R['peak_rss']/1e6:.0f} MB")
    text = "\n".join(lines) + "\n"
    (work / "report.md").write_text(text)
    print(text)


# ===========================================================================
# Driver
# ===========================================================================


def child_env():
    TMPDIR.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", VECLIB_MAXIMUM_THREADS="2",
               OPENBLAS_NUM_THREADS="2", TOKENIZERS_PARALLELISM="false", TMPDIR=str(TMPDIR),
               HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", PYTHONDONTWRITEBYTECODE="1")
    return env


def run_stage(python, stage, work, *extra):
    cmd = ["nice", "-n", "20", "taskpolicy", "-b", str(python), "-B", __file__, stage,
           "--work", str(work), *extra]
    t = time.time()
    proc = subprocess.run(cmd, env=child_env(), capture_output=True, text=True, timeout=7200)
    sys.stdout.write(proc.stdout[-4000:])
    if proc.returncode:
        raise RuntimeError(f"stage {stage} failed\n{proc.stderr[-8000:]}")
    print(f"[{stage}] {time.time() - t:.1f}s")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("stage", choices=("all", "ref", "convert", "mlx", "diag", "report"))
    ap.add_argument("--work", type=Path, default=TMPDIR / "run")
    ap.add_argument("--sol-repo", type=Path, default=SOL_REPO)
    ap.add_argument("--twin-repo", type=Path, default=TWIN_REPO)
    ap.add_argument("--python", type=Path, default=PY_BOTH)
    a = ap.parse_args()
    if a.stage == "ref":
        stage_ref(a.work)
    elif a.stage == "convert":
        stage_convert(a.work, a.sol_repo, a.twin_repo, a.python)
    elif a.stage == "mlx":
        stage_mlx(a.work)
    elif a.stage == "diag":
        stage_diag(a.work)
    elif a.stage == "report":
        stage_report(a.work)
    else:
        if a.work.exists() and (a.work / "ref.npz").exists():
            print("[ref] reusing", a.work)
        else:
            run_stage(a.python, "ref", a.work)
        run_stage(a.python, "convert", a.work, "--sol-repo", str(a.sol_repo),
                  "--twin-repo", str(a.twin_repo), "--python", str(a.python))
        run_stage(a.python, "mlx", a.work)
        run_stage(a.python, "diag", a.work)
        run_stage(a.python, "report", a.work)


if __name__ == "__main__":
    main()
