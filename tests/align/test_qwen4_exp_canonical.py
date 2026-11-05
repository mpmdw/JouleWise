"""Canonical qwen4_exp MLX module vs the official transformers 5.22.1 reference.

GOAL items 2-4 (docs/align/qwen4_exp_port/GOAL.md), phase P3. One shared tiny
random checkpoint, saved in bf16 in the released serialized layout
(``Qwen4ExpForConditionalGeneration``: ``model.language_model.*``, per-expert
``mlp.experts.{e}.*``, n-gram ``shard_*`` pieces plus hash buffers, a vision
tower and a fake ``mtp.*`` file the converter must drop), converted with
``scripts/align_convert_qwen4_exp.py`` and loaded through mlx-lm 0.31.3's
``model_file`` hook. Every text layer type is present (GatedDeltaNet, QSA with
an indexer that really drops blocks, PLE at two ``ple_layer_index`` values,
hyper-connections, MoE + shared expert). hidden_size 192: sqrt(192) is not
bf16-representable, as sqrt(2560) is not, so the PLE gate divisor (D8) is
exercised; 192 is also a multiple of 64, so the maxfit recipe (6-bit group-64
experts) runs unchanged.

Tests (letters follow the P3 brief):
  (a) fp32 gold parity, max abs logit diff <= 1e-4, every scenario;
  (b) bf16 bound from the differential: port vs fp32 REF <= 1.25x the
      reference's own bf16 error, port vs bf16 REF <= 1.5x;
  (c) bitwise isolated-component bf16 checks (each component fed the
      reference's exact captured input);
  (d) prefill == stepwise, chunked, left-padded batch, trim + re-prefill,
      DeltaNet snapshot/restore, prompt-cache save/load;
  (e) tie-aware comparisons, logging the QSA and router tie counts;
  (f) maxfit (6-bit experts) vs bf16, within the bound: the quantized model
      must match the fp32 reference run with the same dequantized experts;
  (g) a 4101-token sparse prefill through the block-sparse Metal kernel vs the
      dense reference paths (transformers, and MLX dense-masked SDPA);
  plus a 32-token greedy identity check vs the fp32 reference, and converter
  checks (manifest, determinism, bf16 bytes vs ``mx.load``, sanitize).

"REF" breaks exact QSA top-k ties score-descending, block-ascending (the
port's rule, a deterministic member of torch.topk's unspecified tie order);
"REFdefault" is torch's own order (differential D0). The MoE router's topk is
never touched.

Runs natively in one venv with torch + transformers + mlx (venv-both). The
reference results and conversions are cached under ``JW_CANON_WORK`` (default
``$TMPDIR/qwen4exp_canonical``), keyed by the config, the reference code
version and the module/converter sha256. Results are written to
``results.json`` there. Set ``JW_SKIP_CANONICAL=1`` to skip.
"""

import copy
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE_FILE = REPO / "joulewise" / "align" / "models" / "qwen4_exp.py"
CONVERTER_FILE = REPO / "scripts" / "align_convert_qwen4_exp.py"
WORK_ROOT = Path(os.environ.get("JW_CANON_WORK", Path(os.environ.get("TMPDIR", "/tmp")) / "qwen4exp_canonical"))
REF_VERSION = "canonical-ref-v3"

EOS = 1
TEXT = {
    "vocab_size": 256, "hidden_size": 192, "num_hidden_layers": 8,
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
    # complete blocks, so most of its queries drop blocks.
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
          "out_hidden_size": 192, "patch_size": 16, "spatial_merge_size": 2,
          "temporal_patch_size": 2, "num_position_embeddings": 16}
N_LAYERS = TEXT["num_hidden_layers"]
QSA_LAYERS = [i for i, t in enumerate(TEXT["layer_types"]) if t == "full_attention"]
PLE_LAYERS = [i - 1 for i in TEXT["ple_layer_ids"]]
RATIO = TEXT["indexer_compress_ratio"]
TOPK = TEXT["indexer_budget"] // RATIO
LEN_A, LEN_B, PAD_B, N_EXT, CHUNK = 40, 32, 8, 4, 7
LONG_LEN, LONG_PREFIX, LONG_CHUNK = 320, 304, 64
LONGK_LEN, LONGK_CHUNK = 4101, 1024
N_GREEDY = 32
TIE_LAYER = QSA_LAYERS[0]

# Bounds. fp32: the GOAL's 1e-4 on logits (scale ~4). bf16: ratios to the
# reference's own bf16-vs-fp32 error ("noise"), the differential's bound.
FP32_TOL = 1e-4
INTERNAL_FP32_TOL = 2e-5
BF16_VS_F32_RATIO = 1.25
BF16_VS_B16_RATIO = 1.5
# Isolated components, bf16: minimum fraction of output elements bitwise
# equal to the reference (differential prototype: 1.000 HC / PLE / mixer /
# head / router, 0.999 MoE, 0.969 DeltaNet whose fp32 state recurrence is
# ordered differently from torch's chunked rule). At hidden 192 the HC stream
# mix keeps ~0.1% one-ulp flips from the fp32 reduction order of the 192-wide
# RMS (fused and explicit norms alike; the prototype's 1.000 was at hidden 96).
# The QSA attention core is not bitwise reproducible even inside torch (D9):
# reported, not gated, but its block selection must be identical.
BITWISE_MIN = {"attn_hc.mixed": 0.998, "attn_hc.weights": 0.999, "mlp_hc.mixed": 0.998,
               "mlp_hc.weights": 0.999, "ple": 0.999, "mix.linear": 0.95, "moe": 0.99,
               "mixer": 0.999, "head": 0.999, "router.logits": 1.0}


def _skip_reason():
    if os.environ.get("JW_SKIP_CANONICAL"):
        return "JW_SKIP_CANONICAL set"
    try:
        import mlx.core as mx
        import mlx_lm
        import torch  # noqa: F401
        import transformers
    except Exception as exc:  # pragma: no cover - environment dependent
        return f"needs torch + transformers + mlx in one venv ({exc})"
    if (mx.__version__, mlx_lm.__version__, transformers.__version__) != ("0.31.2", "0.31.3", "5.22.1"):
        return f"pinned stack required, found mlx {mx.__version__} mlx-lm {mlx_lm.__version__} " \
               f"transformers {transformers.__version__}"
    if not mx.metal.is_available():
        return "Metal unavailable"
    return None


SKIP = _skip_reason()


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _peak_rss_mb():
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 20  # macOS: bytes


def tokens(seed, n, eos_at=()):
    import numpy as np
    ids = np.random.default_rng(seed).integers(2, TEXT["vocab_size"], n).tolist()
    for i in eos_at:
        ids[i] = EOS
    return [int(x) for x in ids]


def sequences():
    return dict(seq_a=tokens(7, LEN_A, (5, 21)), seq_b=tokens(8, LEN_B, (11,)),
                ext_a=tokens(9, N_EXT), ext_b=tokens(10, N_EXT, (1,)),
                long=tokens(11, LONG_LEN, (37, 150, 151, 260)),
                longk=tokens(12, LONGK_LEN, (100, 2000, 2001, 3333)))


def diff(a, b):
    import numpy as np
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch {a.shape} vs {b.shape}")
    d = np.abs(a - b)
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    out = dict(max_abs=float(d.max()), scale=float(np.abs(b).max()),
               cos=float((a * b).sum() / (na * nb)) if na and nb else 1.0)
    if a.ndim >= 2:
        out["top1"] = float((a.argmax(-1) == b.argmax(-1)).mean())
    return out


def bitwise(a, b):
    """Fraction of elements identical after rounding both to bf16 (bit view)."""
    import numpy as np
    to16 = lambda x: (np.ascontiguousarray(x, dtype=np.float32).view(np.uint32) >> 16)
    return float((to16(a) == to16(b)).mean())


# ===========================================================================
# Reference (torch + transformers 5.22.1)
# ===========================================================================


def randomize(model, torch, seed):
    """Nonzero random values everywhere, including what the reference
    zero-initialises (PLE conv, norm offsets), so nothing goes untested."""
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
    """Wrap every QSA indexer forward: count top-k calls, straddling exact ties
    (K-th == (K+1)-th score) and, with ``force_lowest_index``, select
    score-descending / block-ascending (stable sort), the port's rule."""

    def __init__(self, model, torch, force_lowest_index=False):
        self.model, self.torch, self.force = model, torch, force_lowest_index
        self.calls = self.straddling = 0
        self._saved = []

    def __enter__(self):
        from unittest.mock import patch
        torch, spy = self.torch, self
        original_topk = torch.Tensor.topk

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


class RouterTieSpy:
    """Count MoE router rows whose k-th and (k+1)-th fp32 probabilities are
    exactly equal (``torch.topk`` and ``argpartition`` may then differ)."""

    def __init__(self, model, torch):
        self.model, self.torch = model, torch
        self.rows = self.ties = 0
        self.hooks = []

    def __enter__(self):
        torch = self.torch
        k = TEXT["num_experts_per_tok"]

        def hook(mod, args, out):
            probs = torch.softmax(out[0].float(), dim=-1)
            s = torch.sort(probs, dim=-1, descending=True).values
            self.rows += s.shape[0]
            self.ties += int((s[:, k - 1] == s[:, k]).sum())

        for name, module in self.model.named_modules():
            if type(module).__name__ == "Qwen4ExpTextTopKRouter":
                self.hooks.append(module.register_forward_hook(hook))
        return self

    def __exit__(self, *exc):
        for h in self.hooks:
            h.remove()
        return False


def capture(m, torch, ids, tag, out):
    """Inputs and outputs of every component on a full prefill of ``ids``."""
    hooks = []
    f32 = lambda t: t.detach().float().numpy()

    def add(module, fn):
        def hook(mod, args, kwargs, o):
            fn(args, kwargs, o)
            return None

        hooks.append(module.register_forward_hook(hook, with_kwargs=True))

    def put(key, value):
        out[f"{tag}.cap.{key}"] = value

    for i, layer in enumerate(m.model.layers):
        p = f"L{i}."
        if layer.ple is not None:
            add(layer.ple, lambda a, k, o, p=p: (put(p + "ple.in", f32(a[0])), put(p + "ple.ids", a[1].numpy()),
                                                put(p + "ple.out", f32(o))))
        for hc in ("attn_hc", "mlp_hc"):
            mod = layer.attn_hyper_connection if hc == "attn_hc" else layer.mlp_hyper_connection
            add(mod, lambda a, k, o, p=p, hc=hc: (put(p + hc + ".in", f32(a[0])), put(p + hc + ".mixed", f32(o[0])),
                                                  put(p + hc + ".weights", f32(o[2]))))
        if layer.layer_type == "linear_attention":
            add(layer.linear_attn, lambda a, k, o, p=p: (put(p + "mix.in", f32(a[0])), put(p + "mix.out", f32(o))))
        else:
            add(layer.self_attn, lambda a, k, o, p=p: (put(p + "mix.in", f32(a[0])), put(p + "mix.out", f32(o[0]))))
            add(layer.self_attn.indexer, lambda a, k, o, p=p: put(p + "sel", o[:, 0].numpy()))
        add(layer.mlp, lambda a, k, o, p=p: (put(p + "moe.in", f32(a[0])), put(p + "moe.out", f32(o))))
        add(layer.mlp.gate, lambda a, k, o, p=p: (put(p + "router.logits", f32(o[0])),
                                                 put(p + "router.experts", o[2].numpy())))
    add(m.model.hyper_connection_mixer, lambda a, k, o: (put("mixer.in", f32(a[0])), put("mixer.out", f32(o))))
    add(m.lm_head, lambda a, k, o: (put("head.in", f32(a[0])), put("head.out", f32(o))))
    try:
        with torch.no_grad():
            m(input_ids=torch.tensor([ids]), use_cache=False)
    finally:
        for h in hooks:
            h.remove()


class Reference:
    """Builds the checkpoint and every reference result once (disk-cached)."""

    def __init__(self, work):
        self.work = work
        self.ckpt = work / "hf"

    def _torch(self):
        import torch
        torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "2")))
        return torch

    def build_checkpoint(self):
        if (self.ckpt / "config.json").exists():
            return
        torch = self._torch()
        from transformers import Qwen4ExpConfig, Qwen4ExpForConditionalGeneration
        torch.manual_seed(0)
        cfg = Qwen4ExpConfig(text_config=copy.deepcopy(TEXT), vision_config=dict(VISION))
        full = Qwen4ExpForConditionalGeneration(cfg).eval()
        randomize(full, torch, 1234)
        full = full.to(torch.bfloat16)  # the released checkpoint is bf16
        tmp = self.work / "hf.tmp"
        full.save_pretrained(tmp, max_shard_size="200KB")
        # The released checkpoint also carries MTP weights the text path ignores.
        from safetensors.torch import save_file
        save_file({"mtp.fc.weight": torch.zeros(4, 4, dtype=torch.bfloat16)}, str(tmp / "mtp-extra.safetensors"),
                  metadata={"format": "pt"})
        tmp.rename(self.ckpt)

    def text_models(self):
        """fp32 and bf16 ``Qwen4ExpForCausalLM`` loaded FROM the saved files
        through transformers' own loader (serialized-layout conversions)."""
        torch = self._torch()
        from transformers import Qwen4ExpForCausalLM, Qwen4ExpForConditionalGeneration
        loaded = Qwen4ExpForConditionalGeneration.from_pretrained(self.ckpt, dtype=torch.bfloat16).eval()
        state = {}
        for k, v in loaded.state_dict().items():
            if k.startswith("model.language_model."):
                state["model." + k[len("model.language_model."):]] = v
            elif k.startswith("lm_head."):
                state[k] = v
        tcfg = copy.deepcopy(loaded.config.text_config)
        tcfg._attn_implementation = "sdpa"
        del loaded

        def make(dtype):
            m = Qwen4ExpForCausalLM(tcfg).eval()
            missing, unexpected = m.load_state_dict(state, strict=False)
            if [k for k in missing if "rotary_emb" not in k] or unexpected:
                raise RuntimeError(f"reference load: missing={missing} unexpected={unexpected}")
            return m.to(dtype)

        return make

    @staticmethod
    def _fwd(torch, m, ids, **kw):
        with torch.no_grad():
            return m(input_ids=torch.tensor(ids), use_cache=True, **kw)

    def scenarios(self, m, seqs, meta, tag, full=True):
        torch = self._torch()
        fwd = lambda ids, **kw: self._fwd(torch, m, ids, **kw)

        def prefill(ids):
            return fwd([ids]).logits[0].float().numpy()

        def chunked(ids, n, prefix=None):
            pkv, rows, start = None, [], 0
            if prefix is not None:
                pkv, start = fwd([ids[:prefix]]).past_key_values, prefix
            for s in range(start, len(ids), n):
                r = fwd([ids[s:s + n]], past_key_values=pkv)
                pkv = r.past_key_values
                rows.append(r.logits[0].float())
            return torch.cat(rows).numpy()

        sa, sb = seqs["seq_a"], seqs["seq_b"]
        res = {"prefill": prefill(sa), "long_prefill": prefill(seqs["long"])}
        if not full:
            res["stepwise"] = chunked(sa, 1)
            return res
        res["stepwise"] = chunked(sa, 1)
        res["chunked"] = chunked(sa, CHUNK)
        mask = torch.tensor([[1] * LEN_A, [0] * PAD_B + [1] * LEN_B])
        pos = (mask.cumsum(-1) - 1).clamp_min(0)
        r = fwd([sa, [EOS] * PAD_B + sb], attention_mask=mask, position_ids=pos)
        pkv, rows = r.past_key_values, [r.logits.float()]
        for i in range(N_EXT):
            mask = torch.cat([mask, torch.ones(2, 1, dtype=mask.dtype)], dim=1)
            r = fwd([[seqs["ext_a"][i]], [seqs["ext_b"][i]]], past_key_values=pkv, attention_mask=mask,
                    position_ids=pos[:, -1:] + 1 + i)
            pkv = r.past_key_values
            rows.append(r.logits.float())
        res["padded"] = torch.cat(rows, dim=1).numpy()
        res["long_decode"] = chunked(seqs["long"], 1, prefix=LONG_PREFIX)
        r = fwd([sa])
        pkv, toks, rows = r.past_key_values, [], [r.logits[0, -1].float()]
        for i in range(N_GREEDY):
            toks.append(int(rows[-1].argmax()))
            if i == N_GREEDY - 1:
                break
            r = fwd([[toks[-1]]], past_key_values=pkv)
            pkv = r.past_key_values
            rows.append(r.logits[0, -1].float())
        res["greedy_logits"] = torch.stack(rows).numpy()
        meta[f"greedy_tokens_{tag}"] = toks
        res["greedy_tf"] = prefill(sa + toks)[LEN_A - 1:LEN_A - 1 + N_GREEDY]
        return res

    def compute(self):
        """Every reference array the tests need (one npz + meta json)."""
        import numpy as np
        path, meta_path = self.work / "ref.npz", self.work / "ref_meta.json"
        if path.exists() and meta_path.exists():
            data = np.load(path)
            return {k: data[k] for k in data.files}, json.loads(meta_path.read_text())
        self.build_checkpoint()
        torch = self._torch()
        import transformers
        make = self.text_models()
        seqs = sequences()
        out, meta = {}, dict(seqs=seqs, ties={}, router_ties={}, torch=torch.__version__,
                             transformers=transformers.__version__, attn_implementation="sdpa")
        t0 = time.time()
        for tag, dtype in (("f32", torch.float32), ("b16", torch.bfloat16)):
            m = make(dtype)
            meta["experts_implementation"] = m.config._experts_implementation
            with TopkSpy(m, torch, force_lowest_index=True) as spy, RouterTieSpy(m, torch) as rspy:
                res = self.scenarios(m, seqs, meta, tag)
            meta["ties"][tag] = dict(topk_calls=spy.calls, straddling_ties=spy.straddling)
            meta["router_ties"][tag] = dict(rows=rspy.rows, ties=rspy.ties)
            out.update({f"{tag}.{k}": v for k, v in res.items()})
            # torch.topk's own CPU tie order (REFdefault): prefill + stepwise.
            with TopkSpy(m, torch) as spy:
                res = self.scenarios(m, seqs, meta, tag + "D", full=False)
            meta["ties"][tag + "D"] = dict(topk_calls=spy.calls, straddling_ties=spy.straddling)
            out.update({f"{tag}D.{k}": v for k, v in res.items()})
            with TopkSpy(m, torch, force_lowest_index=True):
                capture(m, torch, seqs["seq_a"], tag, out)
            if tag == "f32":
                # Forced exact ties: zero one indexer projection, so every
                # visible block scores exactly 0.
                w = m.model.layers[TIE_LAYER].self_attn.indexer.index_qk_proj.weight
                saved = w.detach().clone()
                with torch.no_grad():
                    w.zero_()
                with TopkSpy(m, torch) as spy:
                    out["f32.tie_default"] = self._fwd(torch, m, [seqs["seq_a"]]).logits[0].float().numpy()
                meta["ties"]["probe_default"] = dict(topk_calls=spy.calls, straddling_ties=spy.straddling)
                with TopkSpy(m, torch, force_lowest_index=True):
                    out["f32.tie_lowest_index"] = self._fwd(torch, m, [seqs["seq_a"]]).logits[0].float().numpy()
                with torch.no_grad():
                    w.copy_(saved)
                # (g) long context: one 4101-token prefill (dense SDPA under the
                # QSA mask), use_cache off to bound memory.
                with TopkSpy(m, torch, force_lowest_index=True) as spy, torch.no_grad():
                    out["f32.longk_prefill"] = m(input_ids=torch.tensor([seqs["longk"]]),
                                                 use_cache=False).logits[0].float().numpy()
                meta["ties"]["longk"] = dict(topk_calls=spy.calls, straddling_ties=spy.straddling)
            del m
            print(f"[ref] {tag} done ({time.time() - t0:.0f}s)", flush=True)
        meta["elapsed_s"] = time.time() - t0
        meta["peak_rss_mb"] = _peak_rss_mb()
        np.savez(path, **out)
        meta_path.write_text(json.dumps(meta, indent=2))
        return out, meta

    def compute_dequantized(self, dequant, tag):
        """fp32 reference with the routed experts replaced by ``dequant``
        (layer -> (gate_up [E, 2I, H], down [E, H, I]) fp32 arrays)."""
        import numpy as np
        path = self.work / f"ref_{tag}.npz"
        if path.exists():
            data = np.load(path)
            return {k: data[k] for k in data.files}
        torch = self._torch()
        m = self.text_models()(torch.float32)
        with torch.no_grad():
            for i, (gu, dn) in dequant.items():
                ex = m.model.layers[i].mlp.experts
                ex.gate_up_proj.copy_(torch.from_numpy(gu))
                ex.down_proj.copy_(torch.from_numpy(dn))
        seqs = sequences()
        with TopkSpy(m, torch, force_lowest_index=True):
            res = self.scenarios(m, seqs, {}, tag, full=False)
        np.savez(path, **res)
        return res


# ===========================================================================
# MLX side
# ===========================================================================


class Fixture:
    """Process-wide state: reference, conversions and loaded MLX models."""

    def __init__(self):
        key = json.dumps([TEXT, VISION, REF_VERSION], sort_keys=True)
        self.ref_dir = WORK_ROOT / ("ref-" + hashlib.sha256(key.encode()).hexdigest()[:12])
        self.ref_dir.mkdir(parents=True, exist_ok=True)
        code = _sha(MODULE_FILE)[:10] + _sha(CONVERTER_FILE)[:10]
        self.conv_dir = self.ref_dir / ("conv-" + code)
        self.conv_dir.mkdir(exist_ok=True)
        self.reference = Reference(self.ref_dir)
        self._ref = self._meta = None
        self.seqs = sequences()
        self._models = {}
        self.results = {}

    def _reference(self):
        # Lazy: tests that need only a converted model never start torch's
        # reference stage (minutes on a CPU shared with the analysis job).
        if self._ref is None:
            self._ref, self._meta = self.reference.compute()
            if self._meta["seqs"] != self.seqs:
                raise RuntimeError("cached reference was built from different token sequences")
        return self._ref, self._meta

    @property
    def ref(self):
        return self._reference()[0]

    @property
    def meta(self):
        return self._reference()[1]

    def text_config(self, profile="fp32", **changes):
        """The converted artifact's text_config with ``changes`` applied (for
        ``model(profile, text_config=...)`` overrides)."""
        cfg = json.loads((self.converted(profile) / "config.json").read_text())["text_config"]
        return dict(cfg, **changes)

    def converter(self):
        spec = importlib.util.spec_from_file_location("qwen4_exp_converter", CONVERTER_FILE)
        conv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conv)
        return conv

    def converted(self, profile, **options):
        """Convert once; the manifest's sha256 is recorded next to the artifact
        at conversion time and is the pin every later load must present."""
        name = profile + "".join(f"-{k}{v}" for k, v in sorted(options.items()))
        out, pin = self.conv_dir / name, self.conv_dir / f"{name}.manifest.sha256"
        if not (out / "manifest.json").exists() or not pin.exists():
            if out.exists():
                import shutil
                shutil.rmtree(out)
            self.reference.build_checkpoint()
            self.converter().convert(self.reference.ckpt, out, profile=profile, **options)
            pin.write_text(_sha(out / "manifest.json") + "\n")
        return out

    def manifest_pin(self, profile, **options):
        name = profile + "".join(f"-{k}{v}" for k, v in sorted(options.items()))
        self.converted(profile, **options)
        return (self.conv_dir / f"{name}.manifest.sha256").read_text().strip()

    def model(self, profile, convert_options=None, **overrides):
        """Load through ``load_verified_model`` (both pins: the manifest sha256
        recorded at conversion, the converter's module pin) and mlx-lm's
        ``model_file`` hook; ``overrides`` are mlx-lm ``model_config`` keys."""
        options = convert_options or {}
        key = (profile, json.dumps(options, sort_keys=True), json.dumps(overrides, sort_keys=True))
        if key not in self._models:
            path = self.converted(profile, **options)
            model, _ = self.converter().load_verified_model(path, self.manifest_pin(profile, **options),
                                                            model_config=overrides or None)
            model.eval()
            self._models[key] = model
        return self._models[key]

    def record(self, name, value):
        self.results[name] = value
        path = self.ref_dir / "results.json"
        old = json.loads(path.read_text()) if path.exists() else {}
        old[name] = value
        path.write_text(json.dumps(old, indent=2, default=float))


_FIXTURE = None


def fixture():
    global _FIXTURE
    if _FIXTURE is None:
        _FIXTURE = Fixture()
    return _FIXTURE


def g(model, name):
    """A global of the anonymous ``custom_model`` module mlx-lm loaded the
    model from (never registered in sys.modules)."""
    return type(model).__init__.__globals__[name]


def run(model, ids, cache=None):
    import mlx.core as mx
    import numpy as np
    out = model(mx.array(ids), cache=cache)
    mx.eval(out)
    return np.array(out.astype(mx.float32))


def port_scenarios(model, seqs, long_chunk=LONG_CHUNK):
    import numpy as np
    sa, sb = seqs["seq_a"], seqs["seq_b"]

    def chunked(ids, n, prefix=None):
        cache, rows, start = model.make_cache(), [], 0
        if prefix is not None:
            run(model, [ids[:prefix]], cache)
            start = prefix
        for s in range(start, len(ids), n):
            rows.append(run(model, [ids[s:s + n]], cache)[0])
        return np.concatenate(rows)

    res = {"prefill": run(model, [sa])[0], "stepwise": chunked(sa, 1), "chunked": chunked(sa, CHUNK)}
    cache = model.make_cache(left_padding=[0, PAD_B])
    rows = [run(model, [sa, [EOS] * PAD_B + sb], cache)]
    for i in range(N_EXT):
        rows.append(run(model, [[seqs["ext_a"][i]], [seqs["ext_b"][i]]], cache))
    res["padded"] = np.concatenate(rows, axis=1)
    res["single_a"] = chunked(sa + seqs["ext_a"], 1, prefix=LEN_A)
    res["single_b"] = chunked(sb + seqs["ext_b"], 1, prefix=LEN_B)
    res["prefill_b"] = run(model, [sb])[0]
    res["long_prefill"] = run(model, [seqs["long"]])[0]
    res["long_decode"] = chunked(seqs["long"], 1, prefix=LONG_PREFIX)
    res["long_chunked"] = chunked(seqs["long"], long_chunk)
    cache = model.make_cache()
    rows, toks = [run(model, [sa], cache)[0, -1]], []
    for i in range(N_GREEDY):
        toks.append(int(rows[-1].argmax()))
        if i == N_GREEDY - 1:
            break
        rows.append(run(model, [[toks[-1]]], cache)[0, -1])
    res["greedy_logits"] = np.stack(rows)
    res["greedy_tokens"] = np.array(toks)
    return res


def compare(port, ref):
    """Scenario -> diff, valid positions only; long_chunked vs one-shot REF."""
    out = {}
    for key in ("prefill", "stepwise", "chunked", "long_prefill", "long_decode", "greedy_logits"):
        if key in ref:
            out[key] = diff(port[key], ref[key])
    if "padded" in ref:
        out["padded_row0"] = diff(port["padded"][0], ref["padded"][0])
        out["padded_row1"] = diff(port["padded"][1, PAD_B:], ref["padded"][1, PAD_B:])
    out["long_chunked"] = diff(port["long_chunked"], ref["long_prefill"])
    return out


def refs(fx, tag):
    return {k.split(".", 1)[1]: v for k, v in fx.ref.items() if k.startswith(tag + ".") and ".cap." not in k}


def noise_table(fx):
    """The reference's own bf16 error per scenario (REF bf16 vs REF fp32).

    Greedy logits are excluded: bf16 and fp32 greedy paths may legitimately
    part at an exact bf16 logit tie (differential), after which rows compare
    different contexts. The greedy tokens are checked on their own."""
    r32, r16 = refs(fx, "f32"), refs(fx, "b16")
    n = {k: diff(r16[k], r32[k])["max_abs"]
         for k in ("prefill", "stepwise", "chunked", "long_prefill", "long_decode")}
    n["long_chunked"] = n["long_prefill"]
    n["padded_row0"] = diff(r16["padded"][0], r32["padded"][0])["max_abs"]
    n["padded_row1"] = diff(r16["padded"][1, PAD_B:], r32["padded"][1, PAD_B:])["max_abs"]
    return n


# ===========================================================================
# Tests
# ===========================================================================


@unittest.skipIf(SKIP, SKIP)
class CanonicalParityTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fx = fixture()
        cls.runs = {}

    def port(self, profile):
        if profile not in self.runs:
            self.runs[profile] = port_scenarios(self.fx.model(profile), self.fx.seqs)
        return self.runs[profile]

    # ---------------------------------------------------------------- (a)
    def test_a_config_exercises_every_path(self):
        """Every layer type, two PLE layers, an inexact bf16 sqrt(hidden), and a
        QSA budget that really drops blocks (in the reference and the port)."""
        import mlx.core as mx
        fx = self.fx
        self.assertEqual(sorted(set(TEXT["layer_types"])), ["full_attention", "linear_attention"])
        self.assertEqual(len(PLE_LAYERS), 2)
        s = math.sqrt(TEXT["hidden_size"])
        self.assertNotEqual(float(mx.array(s, dtype=mx.bfloat16).item()), s)
        sparse = sum(1 for t in range(LEN_A) if (t + 1) // RATIO > TOPK)
        self.assertGreater(sparse, 10)
        sel = fx.ref[f"f32.cap.L{QSA_LAYERS[0]}.sel"][0]
        causal = sum(t + 1 for t in range(LEN_A))
        self.assertLess(int(sel.sum()), causal, "reference selection must drop tokens")
        model = fx.model("fp32")
        cls = type(model.layers[QSA_LAYERS[0]].self_attn)
        before = cls.paths.mask
        run(model, [fx.seqs["seq_a"]])
        self.assertEqual(cls.paths.mask - before, len(QSA_LAYERS), "port must take the sparse path")
        self.assertEqual(fx.meta["experts_implementation"], "grouped_mm")
        fx.record("a_sparse_queries_seq_a", sparse)

    def test_a_fp32_gold_parity(self):
        fx = self.fx
        cmp = compare(self.port("fp32"), refs(fx, "f32"))
        fx.record("a_fp32_vs_ref", cmp)
        for name, d in cmp.items():
            with self.subTest(scenario=name):
                self.assertLessEqual(d["max_abs"], FP32_TOL, f"{name}: {d}")
                self.assertEqual(d.get("top1", 1.0), 1.0)

    def test_greedy_32_tokens_identical_to_fp32_reference(self):
        fx = self.fx
        port = [int(t) for t in self.port("fp32")["greedy_tokens"]]
        ref = fx.meta["greedy_tokens_f32"]
        fx.record("greedy_fp32", dict(port=port, ref=ref))
        self.assertEqual(len(port), N_GREEDY)
        self.assertEqual(port, ref)
        b16 = [int(t) for t in self.port("bf16")["greedy_tokens"]]
        rb = fx.meta["greedy_tokens_b16"]
        first = next((i for i, (x, y) in enumerate(zip(b16, rb)) if x != y), None)
        margin = None
        if first is not None:
            row = sorted(fx.ref["b16.greedy_tf"][first].tolist(), reverse=True)
            margin = row[0] - row[1]
        fx.record("greedy_bf16", dict(port=b16, ref=rb, first_divergence=first, ref_top2_margin=margin))

    # ---------------------------------------------------------------- (b)
    def test_b_bf16_within_reference_noise(self):
        fx = self.fx
        noise = noise_table(fx)
        vs32 = compare(self.port("bf16"), refs(fx, "f32"))
        vs16 = compare(self.port("bf16"), refs(fx, "b16"))
        table = {k: dict(noise=noise[k], vs_ref_f32=vs32[k]["max_abs"], ratio_f32=vs32[k]["max_abs"] / noise[k],
                         vs_ref_b16=vs16[k]["max_abs"], ratio_b16=vs16[k]["max_abs"] / noise[k],
                         cos_f32=vs32[k]["cos"]) for k in noise}
        fx.record("b_bf16_bound", table)
        for k, row in table.items():
            with self.subTest(scenario=k):
                self.assertLessEqual(row["ratio_f32"], BF16_VS_F32_RATIO, f"{k}: {row}")
                self.assertLessEqual(row["ratio_b16"], BF16_VS_B16_RATIO, f"{k}: {row}")

    # ---------------------------------------------------------------- (c)
    def _isolated(self, profile, tag):
        """Each component fed the reference's exact captured input."""
        import mlx.core as mx
        import numpy as np
        fx = self.fx
        model = fx.model(profile)
        tm = model.language_model
        dt = mx.float32 if tag == "f32" else mx.bfloat16
        cap = lambda k: fx.ref[f"{tag}.cap.{k}"]
        to = lambda a: mx.array(np.asarray(a, dtype=np.float32)).astype(dt)
        arr = lambda x: np.array(x.astype(mx.float32))
        Context = g(model, "_Context")

        def ctx(B, S):
            return Context(B, S, 0, np.zeros((B,), np.int64), tm._inv_freq, None, tm._prefill_min_kv,
                           tm._decode_min_kv, tm._kernel_ok)

        res = {}
        idx_cls = type(model.layers[QSA_LAYERS[0]].self_attn.indexer)
        idx_cls.record_selection = True
        try:
            for i, layer in enumerate(model.layers):
                p = f"L{i}."
                caches = model.make_cache()
                if i in PLE_LAYERS:
                    h, ids = to(cap(p + "ple.in")), cap(p + "ple.ids").astype(np.int64)
                    c = ctx(1, LEN_A)
                    tm._gather_ngrams(ids, c, caches, dt)
                    res[p + "ple"] = arr(layer.ple(h, c.ngram_emb[i], c, caches[i]))
                for hc in ("attn_hc", "mlp_hc"):
                    mod = layer.attn_hyper_connection if hc == "attn_hc" else layer.mlp_hyper_connection
                    o = mod(to(cap(p + hc + ".in")))
                    res[p + hc + ".mixed"], res[p + hc + ".weights"] = arr(o[0]), arr(o[-1])
                x = to(cap(p + "mix.in"))
                if i in QSA_LAYERS:
                    res[p + "mix"] = arr(layer.self_attn(x, ctx(1, LEN_A), caches[i]))
                    last = layer.self_attn.indexer.last
                    res[p + "sel_blocks"] = np.array(last.blocks)[0]
                    res[p + "sel_scores"] = np.array(last.scores)[0]
                else:
                    res[p + "mix"] = arr(layer.linear_attn(x, ctx(1, LEN_A), caches[i]))
                xm = to(cap(p + "moe.in"))
                logits, inds, _ = layer.mlp.route(xm)
                res[p + "router.logits"] = arr(logits).reshape(-1, logits.shape[-1])
                res[p + "router.experts"] = np.sort(np.array(inds).reshape(-1, inds.shape[-1]), -1)
                res[p + "moe"] = arr(layer.mlp(xm))
            res["mixer"] = arr(tm.model.hyper_connection_mixer(to(cap("mixer.in"))))
            res["head"] = arr(tm.lm_head(to(cap("head.in"))))
        finally:
            idx_cls.record_selection = False
        return res

    @staticmethod
    def _ref_blocks(sel_tokens):
        """Reference token mask [S, L] -> per-query selected complete blocks."""
        out = []
        for t in range(sel_tokens.shape[0]):
            nt = (t + 1) // RATIO
            out.append(frozenset(j for j in range(nt) if sel_tokens[t, j * RATIO]))
        return out

    def test_c_isolated_components_bitwise_bf16(self):
        import numpy as np
        fx = self.fx
        iso = self._isolated("bf16", "b16")
        cap = lambda k: fx.ref[f"b16.cap.{k}"]
        rows, worst = {}, {}
        for i in range(N_LAYERS):
            p = f"L{i}."
            pairs = [("attn_hc.mixed", p + "attn_hc.mixed"), ("attn_hc.weights", p + "attn_hc.weights"),
                     ("mlp_hc.mixed", p + "mlp_hc.mixed"), ("mlp_hc.weights", p + "mlp_hc.weights"),
                     ("moe", p + "moe.out")]
            pairs.append(("mix.qsa" if i in QSA_LAYERS else "mix.linear", p + "mix.out"))
            if i in PLE_LAYERS:
                pairs.append(("ple", p + "ple.out"))
            for comp, rkey in pairs:
                key = p + ("mix" if comp.startswith("mix") else comp)
                a = iso[key].reshape(cap(rkey).shape)
                frac = bitwise(a, cap(rkey))
                rows[f"L{i}.{comp}"] = dict(bitwise=frac, max_abs=diff(a, cap(rkey))["max_abs"])
                worst[comp] = min(worst.get(comp, 1.0), frac)
            logits = cap(p + "router.logits")
            frac = bitwise(iso[p + "router.logits"], logits)
            worst["router.logits"] = min(worst.get("router.logits", 1.0), frac)
            ref_e = np.sort(cap(p + "router.experts").reshape(-1, TEXT["num_experts_per_tok"]), -1)
            same = float((iso[p + "router.experts"] == ref_e).all(-1).mean())
            worst["router.experts"] = min(worst.get("router.experts", 1.0), same)
            if i in QSA_LAYERS:
                ref_sel = self._ref_blocks(cap(p + "sel")[0])
                port_sel = [frozenset(np.nonzero(iso[p + "sel_blocks"][t])[0].tolist()) for t in range(LEN_A)]
                diffs = sum(1 for t in range(LEN_A) if (t + 1) // RATIO > TOPK and ref_sel[t] != port_sel[t])
                worst[f"qsa_selection_rows_differing.L{i}"] = diffs
        for comp, rkey in (("mixer", "mixer.out"), ("head", "head.out")):
            worst[comp] = bitwise(iso[comp].reshape(cap(rkey).shape), cap(rkey))
        fx.record("c_isolated_bf16", dict(min_over_layers=worst, per_layer=rows))
        for comp, floor in BITWISE_MIN.items():
            with self.subTest(component=comp):
                self.assertGreaterEqual(worst[comp], floor, f"{comp}: {worst[comp]:.4f} < {floor}")
        self.assertEqual(worst["router.experts"], 1.0)
        for i in QSA_LAYERS:
            self.assertEqual(worst[f"qsa_selection_rows_differing.L{i}"], 0)

    def test_c_isolated_components_fp32(self):
        fx = self.fx
        iso = self._isolated("fp32", "f32")
        cap = lambda k: fx.ref[f"f32.cap.{k}"]
        worst = 0.0
        for i in range(N_LAYERS):
            p = f"L{i}."
            keys = [("attn_hc.mixed", "attn_hc.mixed"), ("mlp_hc.mixed", "mlp_hc.mixed"),
                    ("moe", "moe.out"), ("mix", "mix.out")] + ([("ple", "ple.out")] if i in PLE_LAYERS else [])
            for k, rk in keys:
                worst = max(worst, diff(iso[p + k].reshape(cap(p + rk).shape), cap(p + rk))["max_abs"])
        fx.record("c_isolated_fp32_max_abs", worst)
        self.assertLessEqual(worst, 1e-5)

    # ---------------------------------------------------------------- (d)
    def test_d_internal_invariants(self):
        import numpy as np
        fx = self.fx
        out = {}
        for profile, tol in (("fp32", INTERNAL_FP32_TOL), ("bf16", None)):
            r = self.port(profile)
            inv = dict(
                prefill_vs_stepwise=diff(r["stepwise"], r["prefill"]),
                prefill_vs_chunked=diff(r["chunked"], r["prefill"]),
                long_prefill_vs_chunked=diff(r["long_chunked"], r["long_prefill"]),
                padded_row0_vs_batch1=diff(r["padded"][0], np.concatenate([r["prefill"], r["single_a"]])),
                padded_row1_vs_batch1=diff(r["padded"][1, PAD_B:], np.concatenate([r["prefill_b"],
                                                                                   r["single_b"]])))
            out[profile] = inv
            noise = noise_table(fx)
            for name, d in inv.items():
                with self.subTest(profile=profile, invariant=name):
                    bound = tol if tol is not None else 1.5 * noise["long_prefill" if "long" in name else "prefill"]
                    self.assertLessEqual(d["max_abs"], bound, f"{profile} {name}: {d}")
        fx.record("d_internal", out)

    def test_d_trim_reprefill_and_deltanet_snapshot_restore(self):
        """Hybrid prefix rewrite: snapshot (DeltaNet states by reference, QSA
        offsets), run a detour, restore (QSA trim), re-prefill: bitwise equal
        to never having taken the detour. Short (dense) and long (sparse
        QSA, partial blocks trimmed) prefixes."""
        import mlx.core as mx
        import numpy as np
        fx = self.fx
        out = {}
        for profile in ("fp32", "bf16"):
            model = fx.model(profile)
            for label, ids, cut, detour in (("short", fx.seqs["seq_a"], 30, fx.seqs["seq_b"][:10]),
                                            ("long", fx.seqs["long"], 301, fx.seqs["seq_b"][:17])):
                fresh = model.make_cache()
                run(model, [ids[:cut]], fresh)
                want = run(model, [ids[cut:cut + 19]], fresh)
                cache = model.make_cache()
                run(model, [ids[:cut]], cache)
                snap = model.snapshot_cache(cache)
                states_before = [np.array(c[1]) for c in cache if hasattr(c, "cache")]
                run(model, [detour], cache)
                run(model, [detour[:3]], cache)
                model.restore_cache(cache, snap)
                states_after = [np.array(c[1]) for c in cache if hasattr(c, "cache")]
                got = run(model, [ids[cut:cut + 19]], cache)
                exact_state = all(np.array_equal(a, b) for a, b in zip(states_before, states_after))
                d = float(np.abs(got - want).max())
                out[f"{profile}.{label}"] = dict(max_abs=d, deltanet_state_bitwise=exact_state,
                                                 offsets=sorted({c.offset for c in cache}))
                with self.subTest(profile=profile, prefix=label):
                    self.assertTrue(exact_state)
                    self.assertEqual(d, 0.0)
                # QSA trim alone (the KV, raw-key and block-key buffers), with
                # the DeltaNet states re-derived: trim back 7 tokens, re-feed.
                c2 = model.make_cache()
                run(model, [ids[:cut]], c2)
                snap2 = model.snapshot_cache(c2)
                a = run(model, [ids[cut:cut + 7]], c2)
                model.restore_cache(c2, snap2)
                b = run(model, [ids[cut:cut + 7]], c2)
                with self.subTest(profile=profile, prefix=label, check="trim"):
                    self.assertEqual(float(np.abs(a - b).max()), 0.0)
        mx.eval()
        fx.record("d_trim_snapshot", out)

    def test_d_prompt_cache_save_load_roundtrip(self):
        """Sol's serializable caches: save_prompt_cache / load_prompt_cache
        (classes registered in mlx_lm.models.cache) reproduce decoding exactly,
        including a left-padded batch."""
        import numpy as np
        from mlx_lm.models.cache import load_prompt_cache, save_prompt_cache
        fx = self.fx
        model = fx.model("bf16")
        sa, sb = fx.seqs["seq_a"], fx.seqs["seq_b"]
        path = str(fx.ref_dir / "prompt_cache.safetensors")
        cases = ((None, [fx.seqs["long"][:300]]), ([0, PAD_B], [sa, [EOS] * PAD_B + sb]),
                 # fewer real tokens than one QSA block: no complete block yet
                 (None, [sa[:3]]), ([0, 2], [sa[:3], [EOS, EOS, sb[0]]]))
        for lp, batch in cases:
            cache = model.make_cache(left_padding=lp)
            run(model, batch, cache)
            save_prompt_cache(path, cache)
            loaded = load_prompt_cache(path)
            nxt = [[5], [6]][:len(batch)]
            a = run(model, nxt, cache)
            b = run(model, nxt, loaded)
            self.assertEqual(type(loaded[0]).__name__, "Qwen4ExpLinearCache")
            self.assertEqual(float(np.abs(a - b).max()), 0.0)

    def test_legacy_rope_keys_fold_or_fail(self):
        """Top-level rope_theta / partial_rotary_factor (older configs) fold into
        rope_parameters as HF does; conflicts and rope_scaling fail loudly."""
        import numpy as np
        model = self.fx.model("fp32")
        Args, inv = g(model, "TextModelArgs"), g(model, "rope_inv_freq")
        base = {k: v for k, v in TEXT.items() if k != "rope_parameters"}
        legacy = Args.from_dict(dict(base, rope_theta=10000000, partial_rotary_factor=0.25))
        modern = Args.from_dict(TEXT)
        self.assertEqual(legacy.rotary_dim, modern.rotary_dim)
        self.assertTrue(np.array_equal(np.array(inv(legacy)), np.array(inv(modern))))
        with self.assertRaises(ValueError):
            Args.from_dict(dict(TEXT, rope_theta=10000))
        with self.assertRaises(ValueError):
            Args.from_dict(dict(TEXT, rope_scaling={"type": "yarn", "factor": 4.0}))

    def test_d_mlx_lm_generate_step(self):
        """End to end through mlx-lm's generate_step (chunked prefill)."""
        import mlx.core as mx
        from mlx_lm.generate import generate_step
        fx = self.fx
        model = fx.model("fp32")
        toks = []
        for tok, _ in generate_step(mx.array(fx.seqs["seq_a"]), model, max_tokens=N_GREEDY,
                                    prefill_step_size=16):
            toks.append(int(tok))
        self.assertEqual(toks, fx.meta["greedy_tokens_f32"])

    def test_d_padded_batch_through_kernel_and_gather_paths(self):
        """Left-padded batch with both sparse thresholds at 0: prefill through
        the block-sparse kernel (per-row token lists) and decode through the
        gather path. Still the reference's function, row by row (the mlx-vlm
        D1 failure mode is a ragged decode that drops the selection)."""
        import numpy as np
        fx = self.fx
        model = fx.model("fp32", qsa_sparse_prefill_min_kv=0, qsa_sparse_decode_min_kv=0)
        cls = type(model.layers[QSA_LAYERS[0]].self_attn)
        k0, g0 = cls.paths.kernel, cls.paths.gather
        sa, sb = fx.seqs["seq_a"], fx.seqs["seq_b"]
        cache = model.make_cache(left_padding=[0, PAD_B])
        rows = [run(model, [sa, [EOS] * PAD_B + sb], cache)]
        for i in range(N_EXT):
            rows.append(run(model, [[fx.seqs["ext_a"][i]], [fx.seqs["ext_b"][i]]], cache))
        got = np.concatenate(rows, axis=1)
        ref = refs(fx, "f32")["padded"]
        d0, d1 = diff(got[0], ref[0]), diff(got[1, PAD_B:], ref[1, PAD_B:])
        paths = dict(kernel=cls.paths.kernel - k0, gather=cls.paths.gather - g0)
        fx.record("d_padded_sparse_paths", dict(row0=d0, row1=d1, paths=paths))
        self.assertEqual(paths, dict(kernel=len(QSA_LAYERS), gather=N_EXT * len(QSA_LAYERS)))
        self.assertLessEqual(d0["max_abs"], FP32_TOL)
        self.assertLessEqual(d1["max_abs"], FP32_TOL)

    # ---------------------------------------------------------------- (e)
    def test_e_tie_aware_comparisons(self):
        """QSA top-k ties: the reference's tie counts are logged; the port's
        selection matches REF (same rule); against torch's own CPU order every
        difference is an exact tie; a forced all-ties probe matches REF."""
        import mlx.core as mx
        import numpy as np
        fx = self.fx
        meta = fx.meta
        model = fx.model("fp32")
        idx_cls = type(model.layers[QSA_LAYERS[0]].self_attn.indexer)
        # Port-side tie count on the same prompt (record_selection diagnostics).
        idx_cls.record_selection = True
        try:
            run(model, [fx.seqs["seq_a"]])
            port_ties = {i: model.layers[i].self_attn.indexer.last.straddling_ties for i in QSA_LAYERS}
            port_sparse = {i: model.layers[i].self_attn.indexer.last.sparse_queries for i in QSA_LAYERS}
        finally:
            idx_cls.record_selection = False
        r = self.port("fp32")
        rd = refs(fx, "f32D")
        effect = {k: diff(r[k], rd[k])["max_abs"] for k in ("prefill", "stepwise", "long_prefill")}
        ref_effect = {k: diff(refs(fx, "f32")[k], rd[k])["max_abs"] for k in effect}
        # Forced exact ties at TIE_LAYER.
        lin = model.layers[TIE_LAYER].self_attn.indexer.index_qk_proj
        saved = lin.weight
        lin.weight = mx.zeros_like(saved)
        try:
            probe = run(model, [fx.seqs["seq_a"]])[0]
        finally:
            lin.weight = saved
        probe_vs_lowest = diff(probe, fx.ref["f32.tie_lowest_index"])
        probe_vs_default = diff(probe, fx.ref["f32.tie_default"])
        rec = dict(ref_qsa_ties=meta["ties"], ref_router_ties=meta["router_ties"],
                   port_qsa_straddling_ties_seq_a=port_ties, port_sparse_queries_seq_a=port_sparse,
                   port_vs_REFdefault=effect, REF_vs_REFdefault=ref_effect,
                   probe_vs_REF_lowest_index=probe_vs_lowest, probe_vs_REF_default=probe_vs_default)
        fx.record("e_ties", rec)
        print("\n[ties]", json.dumps({k: rec[k] for k in ("ref_qsa_ties", "ref_router_ties",
                                                          "port_qsa_straddling_ties_seq_a")}), flush=True)
        self.assertLessEqual(probe_vs_lowest["max_abs"], FP32_TOL)
        self.assertGreater(meta["ties"]["probe_default"]["straddling_ties"], 0)
        # Wherever the port departs from torch's own order, so does REF by the
        # same amount: every such difference is an exact-tie effect.
        for k in effect:
            self.assertLessEqual(abs(effect[k] - ref_effect[k]), FP32_TOL, k)

    # ---------------------------------------------------------------- (f)
    def test_f_maxfit_quantized_within_bound(self):
        """maxfit = 6-bit group-64 routed experts, everything else bf16.
        Bound: the quantized port must match the fp32 REFERENCE run with the
        same dequantized expert weights within the bf16 bound of (b): the only
        remaining difference is bf16 compute. The quantization effect itself
        (maxfit vs bf16 port, vs fp32 REF) is measured and recorded."""
        import mlx.core as mx
        import numpy as np
        fx = self.fx
        model = fx.model("maxfit")
        bits = {}
        dequant = {}
        from mlx.utils import tree_flatten
        for i, layer in enumerate(model.layers):
            sw = layer.mlp.switch_mlp
            for name in ("gate_up_proj", "down_proj"):
                lin = getattr(sw, name)
                bits[f"L{i}.{name}"] = (type(lin).__name__, lin.bits, lin.group_size)
            gu = mx.dequantize(sw.gate_up_proj.weight, sw.gate_up_proj.scales, sw.gate_up_proj.biases,
                               group_size=64, bits=6)
            dn = mx.dequantize(sw.down_proj.weight, sw.down_proj.scales, sw.down_proj.biases,
                               group_size=64, bits=6)
            dequant[i] = (np.array(gu.astype(mx.float32)), np.array(dn.astype(mx.float32)))
        quantized = sorted({k.rsplit(".", 1)[0] for k, v in tree_flatten(model.parameters())
                            if k.endswith(".scales")})
        self.assertTrue(all(v == ("QuantizedSwitchLinear", 6, 64) for v in bits.values()), bits)
        self.assertTrue(all(".switch_mlp." in k for k in quantized), quantized)
        self.assertEqual(len(quantized), 2 * N_LAYERS)
        ref_q = fx.reference.compute_dequantized(dequant, "q6-" + fx.conv_dir.name)
        r = port_scenarios(model, fx.seqs)
        noise = noise_table(fx)
        table = {}
        for k in ("prefill", "stepwise", "long_prefill"):
            d = diff(r[k], ref_q[k])
            table[k] = dict(vs_ref_q6_f32=d["max_abs"], ratio=d["max_abs"] / noise[k], cos=d["cos"],
                            quant_effect_vs_bf16_port=diff(r[k], self.port("bf16")[k])["max_abs"],
                            quant_effect_vs_ref_f32=diff(r[k], refs(fx, "f32")[k])["max_abs"],
                            ref_q6_vs_ref_f32=diff(ref_q[k], refs(fx, "f32")[k])["max_abs"],
                            noise=noise[k])
        fx.record("f_maxfit", table)
        for k, row in table.items():
            with self.subTest(scenario=k):
                self.assertLessEqual(row["ratio"], BF16_VS_F32_RATIO, f"{k}: {row}")

    # ---------------------------------------------------------------- (g)
    def test_g_long_context_sparse_kernel_prefill(self):
        """4101 tokens (>= 4096). The kernel threshold is lowered so the
        one-shot prefill runs both QSA layers through the block-sparse Metal
        kernel; references: transformers fp32 (dense SDPA under the QSA mask,
        REF tie rule), the port's dense-masked SDPA path, and chunked
        prefills (1024-token chunks: kernel for every chunk past the
        threshold)."""
        import numpy as np
        fx = self.fx
        ids = fx.seqs["longk"]
        out = {}
        for profile in ("fp32", "bf16"):
            kern = fx.model(profile, qsa_sparse_prefill_min_kv=1024)
            dense = fx.model(profile, qsa_sparse_prefill_min_kv=1 << 30)
            cls = type(kern.layers[QSA_LAYERS[0]].self_attn)
            k0 = cls.paths.kernel
            a = run(kern, [ids])[0]
            used = cls.paths.kernel - k0
            m0 = type(dense.layers[QSA_LAYERS[0]].self_attn).paths.mask
            b = run(dense, [ids])[0]
            used_mask = type(dense.layers[QSA_LAYERS[0]].self_attn).paths.mask - m0
            cache, rows = kern.make_cache(), []
            for s in range(0, len(ids), LONGK_CHUNK):
                rows.append(run(kern, [ids[s:s + LONGK_CHUNK]], cache)[0])
            c = np.concatenate(rows)
            out[profile] = dict(kernel_calls=used, mask_calls=used_mask,
                                kernel_vs_dense_mlx=diff(a, b), chunked_kernel_vs_oneshot=diff(c, a))
            if profile == "fp32":
                out[profile]["kernel_vs_transformers"] = diff(a, fx.ref["f32.longk_prefill"])
                out[profile]["dense_vs_transformers"] = diff(b, fx.ref["f32.longk_prefill"])
                f32_kernel = a
            else:
                out[profile]["bf16_vs_fp32_port"] = diff(a, f32_kernel)
        out["ref_ties_longk"] = fx.meta["ties"]["longk"]
        fx.record("g_long_context", out)
        f, h = out["fp32"], out["bf16"]
        self.assertEqual(f["kernel_calls"], len(QSA_LAYERS))
        self.assertEqual(f["mask_calls"], len(QSA_LAYERS))
        self.assertLessEqual(f["kernel_vs_transformers"]["max_abs"], FP32_TOL)
        self.assertLessEqual(f["kernel_vs_dense_mlx"]["max_abs"], INTERNAL_FP32_TOL)
        self.assertLessEqual(f["chunked_kernel_vs_oneshot"]["max_abs"], INTERNAL_FP32_TOL)
        # bf16: the kernel's departure from the dense path is well inside the
        # model's own bf16 error at this length.
        self.assertLessEqual(h["kernel_vs_dense_mlx"]["max_abs"], h["bf16_vs_fp32_port"]["max_abs"])
        self.assertGreaterEqual(h["kernel_vs_dense_mlx"]["cos"], 0.9999)

    # ---------------------------------------------------------- converter
    def test_converter_manifest_bf16_reads_and_sanitize(self):
        """Manifest verifies; conversion is deterministic; every converted bf16
        tensor equals ``mx.load`` of the source after the module's own
        ``sanitize`` (D1: bf16 sources read bit-exactly); mtp/vision dropped."""
        import mlx.core as mx
        import numpy as np
        fx = self.fx
        spec = importlib.util.spec_from_file_location("qwen4_exp_converter", CONVERTER_FILE)
        conv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conv)
        out = fx.converted("bf16")
        fx.model("bf16")  # loading must leave the artifact byte-identical
        manifest = conv.verify_manifest(out)
        self.assertEqual(manifest["module_sha256"], _sha(MODULE_FILE))
        self.assertIn("mtp.fc.weight", manifest["omitted_keys"])
        self.assertTrue(any(k.startswith("model.visual.") for k in manifest["omitted_keys"]))
        again = fx.ref_dir / "conv-repeat"
        if again.exists():
            import shutil
            shutil.rmtree(again)
        m2 = conv.convert(fx.reference.ckpt, again, profile="bf16")
        same = {k: v for k, v in m2["files"].items() if manifest["files"].get(k) == v}
        self.assertEqual(set(same), set(manifest["files"]), "conversion must be deterministic")
        raw = {}
        for f in sorted(fx.reference.ckpt.glob("*.safetensors")):
            raw.update(mx.load(str(f)))
        model = fx.model("bf16")
        sanitized = model.sanitize(raw)
        converted = {}
        for f in sorted(out.glob("model-*.safetensors")):
            converted.update(mx.load(str(f)))
        self.assertEqual(set(sanitized), set(converted))
        bad = [k for k in converted if converted[k].dtype != sanitized[k].dtype
               or not bool(mx.array_equal(converted[k], sanitized[k]).item())]
        self.assertEqual(bad, [])
        self.assertTrue(all(v.dtype == mx.bfloat16 for v in converted.values()))
        # n-gram table bytes == the bf16 source shards, in order.
        for layer in PLE_LAYERS:
            pieces = [raw[f"model.language_model.layers.{layer}.ple.ple_embedding.ngram_embedding.shard_{s}.weight"]
                      for s in range(TEXT["split_ngram_parts"])]
            want = np.concatenate([np.array(p.view(mx.uint16)) for p in pieces]).tobytes()
            got = (out / f"ngram-L{layer:03d}.bf16.bin").read_bytes()
            self.assertEqual(got, want)


# ===========================================================================
# Validation round 1 regressions (docs/align/qwen4_exp_port/canonical.md)
# ===========================================================================


def graph_nodes(*arrays):
    """Unevaluated graph nodes behind ``arrays`` (0 once they are evaluated)."""
    import tempfile
    import mlx.core as mx
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "g.dot"
        mx.export_to_dot(str(f), *arrays)
        return sum(1 for line in f.read_text().splitlines() if "->" not in line and "[" in line)


def cache_bytes(cache):
    return sum(c.nbytes for c in cache)


def decode_trace(model, cache, rows, steps, checkpoints, probe):
    """Decode ``steps`` tokens per row evaluating only the logits (mlx-lm's
    generate_step contract); at each checkpoint record active memory, the
    caches' own bytes and ``probe(cache)``."""
    import gc
    import mlx.core as mx
    trace = []
    for i in range(1, steps + 1):
        out = model(mx.array([[5 + (i + r) % 200] for r in range(rows)]), cache=cache)
        mx.eval(out)
        del out
        if i in checkpoints:
            gc.collect()
            trace.append(dict(step=i, active=mx.get_active_memory(), cache=cache_bytes(cache), **probe(cache)))
    return trace


@unittest.skipIf(SKIP, SKIP)
class ValidationRound1Test(unittest.TestCase):
    """One regression per validation-round-1 finding that has a code fix."""

    @classmethod
    def setUpClass(cls):
        cls.fx = fixture()

    # ------------------------------------------------- systems HIGH (indexer)
    def test_r1_dense_regime_indexer_writes_run_with_their_token(self):
        """While every QSA block is selected (fewer than budget + ratio tokens)
        the indexer's raw-key and block-key writes reach no output. Evaluating
        only the logits each step (as mlx-lm's generate_step does) must still
        run them with their own token: no deferred graph, no residual memory
        growth beyond the caches' own buffers."""
        import mlx.core as mx
        fx = self.fx
        model = fx.model("bf16", text_config=fx.text_config("bf16", indexer_budget=1024))
        qsa = lambda c: [c[i] for i in QSA_LAYERS]
        cache = model.make_cache()
        run(model, [fx.seqs["seq_a"][:12]], cache)
        mx.eval([c.state for c in cache])
        probe = lambda c: dict(nodes=max(graph_nodes(*[a for a in (q.raw_keys, q.block_keys) if a is not None])
                                         for q in qsa(c)))
        trace = decode_trace(model, cache, 1, 400, (100, 200, 400), probe)
        self.assertTrue(all(q.offset == 412 for q in qsa(cache)))
        self.assertLess(412, 1024 + RATIO, "the run must stay in the dense regime")
        growth = (trace[-1]["active"] - trace[0]["active"]) - (trace[-1]["cache"] - trace[0]["cache"])
        fx.record("r1_dense_indexer", dict(trace=trace, residual_growth_bytes=growth))
        self.assertEqual([t["nodes"] for t in trace], [0, 0, 0], trace)
        self.assertLessEqual(growth, 16 * 1024, trace)

    # --------------------------------------- systems MEDIUM (mlx-lm #1632)
    def test_r1_long_padded_decode_memory_does_not_grow(self):
        """mlx-lm 0.31.3's ArraysCache.advance did a lazy ``left_padding -= n``
        on every linear cache; only the first is ever read, so in a left-padded
        batch the others grew one graph node and one Metal buffer per decode
        step (the upstream crash: ``[metal::malloc] Resource limit``). A
        1024-step padded decode, active memory measured at intervals: no
        chain, and no growth beyond the caches' own buffers."""
        import mlx.core as mx
        import numpy as np
        fx = self.fx
        model = fx.model("bf16")
        sa, sb = fx.seqs["seq_a"], fx.seqs["seq_b"]
        cache = model.make_cache(left_padding=[0, PAD_B])
        run(model, [sa, [EOS] * PAD_B + sb], cache)
        mx.eval([c.state for c in cache])
        linear = [c for c in cache if type(c).__name__ == "Qwen4ExpLinearCache"]
        probe = lambda c: dict(nodes=max(graph_nodes(lc.left_padding) for lc in linear))
        trace = decode_trace(model, cache, 2, 1024, range(32, 1025, 32), probe)
        growth = (trace[-1]["active"] - trace[0]["active"]) - (trace[-1]["cache"] - trace[0]["cache"])
        # Between cache-capacity steps (KV / raw keys every 256 tokens, block
        # keys every 64 blocks) active memory must not grow (transients move it
        # by +-2 KB either way); the chain grew 4 bytes per padded linear layer
        # per step, ~17 KB over these steps.
        flat = sum(b["active"] - a["active"] for a, b in zip(trace, trace[1:]) if a["cache"] == b["cache"])
        flat_steps = sum(b["step"] - a["step"] for a, b in zip(trace, trace[1:]) if a["cache"] == b["cache"])
        fx.record("r1_padded_decode_memory", dict(trace=trace, residual_growth_bytes=growth,
                                                  growth_between_capacity_steps=flat, flat_steps=flat_steps))
        self.assertTrue(all(t["nodes"] == 0 for t in trace), trace)
        self.assertGreaterEqual(flat_steps, 512)
        self.assertLessEqual(flat, 4096, trace)
        self.assertLessEqual(growth, 32 * 1024, trace)
        # The derived value is the protocol's: pad tokens still ahead.
        self.assertEqual(np.array(linear[1].left_padding).tolist(), [0 - linear[1].offset, PAD_B - linear[1].offset])

    # ------------------------------------ systems MEDIUM (verified loading)
    def test_r1_load_verified_model_requires_both_pins(self):
        """A missing manifest pin fails closed, and the manifest's module sha256
        must equal its own qwen4_exp.py entry and the converter's module pin:
        a module edited and re-signed (manifest recomputed, even re-pinned)
        is refused before any of its code runs."""
        import shutil
        import tempfile
        fx = self.fx
        conv = fx.converter()
        self.assertEqual(getattr(conv, "MODULE_SHA256", None), _sha(MODULE_FILE),
                         "rebind MODULE_SHA256 in scripts/align_convert_qwen4_exp.py")
        src, pin = fx.converted("bf16"), fx.manifest_pin("bf16")
        marker = "JW_R1_TAMPERED_MODULE_RAN"

        def resign(d, **fields):
            man = json.loads((d / "manifest.json").read_text())
            man["files"] = {k: _sha(d / k) for k in man["files"]}
            man["module_sha256"] = man["files"]["qwen4_exp.py"]
            man.update(fields)
            (d / "manifest.json").write_text(json.dumps(man, indent=2) + "\n")
            return _sha(d / "manifest.json")

        with tempfile.TemporaryDirectory(dir=fx.ref_dir) as tmp:
            evil = Path(tmp) / "evil"
            shutil.copytree(src, evil)
            mod = evil / "qwen4_exp.py"
            mod.write_text(mod.read_text() + f"\nimport os\nos.environ['{marker}'] = '1'\n")
            evil_pin = resign(evil)
            os.environ.pop(marker, None)
            for label, manifest_pin in (("no pin", None), ("empty pin", ""), ("re-pinned", evil_pin)):
                with self.subTest(case=label):
                    try:
                        conv.load_verified_model(evil, manifest_pin)
                        loaded = True
                    except ValueError:
                        loaded = False
                    self.assertFalse(loaded, "a tampered module was loaded")
                    self.assertNotIn(marker, os.environ, "tampered module code ran")
                    os.environ.pop(marker, None)
            # A module_sha256 field that disagrees with the file entry.
            liar = Path(tmp) / "liar"
            shutil.copytree(src, liar)
            liar_pin = resign(liar, module_sha256="0" * 64)
            with self.assertRaises(ValueError):
                conv.load_verified_model(liar, liar_pin)
            # No module pin at all.
            with self.assertRaises((ValueError, TypeError)):
                conv.load_verified_model(src, pin, expected_module_sha256=None)
        model, _ = conv.load_verified_model(src, pin)
        self.assertEqual(type(model).__name__, "Model")

    # ------------------------------------------- systems LOW (artifact)
    def test_r1_verified_artifact_survives_plain_load_and_refuses_links(self):
        """A plain mlx-lm load writes __pycache__ into the artifact. That
        bytecode is never read by load_verified_model (it compiles the module
        from its hashed source bytes), so verification survives it and a
        planted .pyc does not run. Payload symlinks (even to identical bytes),
        nested files, and files changed after verification are refused."""
        import importlib.util as iu
        import marshal
        import shutil
        import tempfile
        from mlx_lm.utils import load_model
        fx = self.fx
        conv = fx.converter()
        src, pin = fx.converted("bf16"), fx.manifest_pin("bf16")
        marker = "JW_R1_PLANTED_PYC_RAN"
        with tempfile.TemporaryDirectory(dir=fx.ref_dir) as tmp:
            tmp = Path(tmp)
            plain = tmp / "plain"
            shutil.copytree(src, plain)
            previous, sys.dont_write_bytecode = sys.dont_write_bytecode, False
            try:
                load_model(plain)  # ordinary mlx-lm use: writes __pycache__/qwen4_exp.*.pyc
            finally:
                sys.dont_write_bytecode = previous
            pyc = sorted((plain / "__pycache__").glob("qwen4_exp.*.pyc"))
            self.assertEqual(len(pyc), 1)
            # Plant bytecode with the genuine header (source mtime and size), so
            # a path-based import trusts it.
            evil = (plain / "qwen4_exp.py").read_text() + f"\nimport os\nos.environ['{marker}'] = '1'\n"
            pyc[0].write_bytes(pyc[0].read_bytes()[:16] + marshal.dumps(compile(evil, "qwen4_exp.py", "exec")))
            os.environ.pop(marker, None)
            spec = iu.spec_from_file_location("custom_model", plain / "qwen4_exp.py")
            spec.loader.exec_module(iu.module_from_spec(spec))
            self.assertEqual(os.environ.pop(marker, None), "1", "the planted bytecode must be live for this check")
            manifest = conv.verify_manifest(plain, pin)
            self.assertEqual(manifest["ignored_bytecode"], [f"__pycache__/{pyc[0].name}"])
            model, _ = conv.load_verified_model(plain, pin)
            self.assertNotIn(marker, os.environ, "planted bytecode ran under load_verified_model")
            self.assertEqual(run(model, [fx.seqs["seq_a"][:5]]).shape, (1, 5, TEXT["vocab_size"]))
            # A payload file replaced by a symlink to identical bytes outside.
            sym = tmp / "sym"
            shutil.copytree(src, sym)
            victim = sorted(sym.glob("model-*.safetensors"))[0]
            outside = tmp / "outside.bin"
            shutil.copyfile(victim, outside)
            victim.unlink()
            victim.symlink_to(outside)
            with self.assertRaises(ValueError):
                conv.verify_manifest(sym, pin)
            with self.assertRaises(ValueError):
                conv.load_verified_model(sym, pin)
            # Anything nested other than mlx-lm's own bytecode.
            nested = tmp / "nested"
            shutil.copytree(src, nested)
            (nested / "extra").mkdir()
            (nested / "extra" / "notes.txt").write_text("x")
            with self.assertRaises(ValueError):
                conv.verify_manifest(nested, pin)
            # Changed between verification and use.
            changed = tmp / "changed"
            shutil.copytree(src, changed)
            _, _, stamps = conv._verify(changed, pin)
            f = sorted(changed.glob("model-*.safetensors"))[0]
            st = f.stat()
            os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns + 1000))
            with self.assertRaises(ValueError):
                conv._check_unchanged(changed, stamps)

    # ------------------------------------------- systems LOW (cache API)
    def test_r1_refused_restore_leaves_the_cache_untouched(self):
        """restore_cache used to overwrite the linear caches in layer order and
        only then meet a QSA entry from the future, leaving a half-restored
        hybrid cache. Every entry is now checked first."""
        import numpy as np
        fx = self.fx
        model = fx.model("fp32")
        ids = fx.seqs["seq_a"]
        later = model.make_cache()
        run(model, [ids[:42 if len(ids) >= 42 else len(ids)]], later)
        late = model.snapshot_cache(later)
        fresh = model.make_cache()
        run(model, [ids[:20]], fresh)
        want = run(model, [ids[20:23]], fresh)
        cache = model.make_cache()
        run(model, [ids[:20]], cache)
        padded = model.make_cache(left_padding=[0, PAD_B])
        run(model, [ids[:PAD_B + 4], [EOS] * PAD_B + ids[:4]], padded)
        for label, snap in (("future", late), ("other padding", model.snapshot_cache(padded)),
                            ("layer count", late[:-1])):
            with self.subTest(case=label):
                with self.assertRaises(ValueError):
                    model.restore_cache(cache, snap)
                self.assertEqual([c.offset for c in cache], [20] * N_LAYERS)
        got = run(model, [ids[20:23]], cache)
        self.assertEqual(float(np.abs(got - want).max()), 0.0)

    def test_r1_batch_generator_protocol_fails_loudly(self):
        """filter / extend / extract / merge / prepare / finalize raise on both
        cache classes, so the 'unsupported, failing loudly' contract does not
        depend on mlx-lm's _make_cache refusing KVCache subclasses."""
        fx = self.fx
        model = fx.model("fp32")
        cache = model.make_cache(left_padding=[0, 2])
        run(model, [fx.seqs["seq_a"][:6], [EOS, EOS] + fx.seqs["seq_a"][:4]], cache)
        for c in (cache[0], cache[QSA_LAYERS[0]]):
            calls = dict(filter=lambda: c.filter([0]), extend=lambda: c.extend(c), extract=lambda: c.extract(0),
                         merge=lambda: type(c).merge([c, c]), prepare=lambda: c.prepare(lengths=[1, 1]),
                         finalize=lambda: c.finalize())
            for name, call in calls.items():
                with self.subTest(cache=type(c).__name__, method=name):
                    with self.assertRaises(NotImplementedError):
                        call()
        self.assertEqual(sorted({c.offset for c in cache}), [6])
        self.assertEqual(cache[0].padding, (0, 2))

    def test_r1_caches_work_across_two_loaded_module_copies(self):
        """Every load runs the module as a fresh anonymous module and rebinds
        mlx_lm.models.cache.Qwen4Exp*Cache, so load_prompt_cache returns the
        last-loaded copy's classes. Another model's snapshot / restore /
        forward must accept them (dispatch on the format marker)."""
        import numpy as np
        from mlx_lm.models.cache import load_prompt_cache, save_prompt_cache
        fx = self.fx
        ids = fx.seqs["seq_a"]
        model = fx.model("fp32")
        cache = model.make_cache()
        run(model, [ids[:30]], cache)
        path = fx.ref_dir / "r1_cross_module_cache.safetensors"
        save_prompt_cache(str(path), cache)
        other, _ = fx.converter().load_verified_model(fx.converted("fp32"), fx.manifest_pin("fp32"))
        loaded = load_prompt_cache(str(path))
        self.assertIsNot(type(loaded[0]), type(cache[0]), "precondition: classes of another module copy")
        self.assertIs(type(loaded[0]), type(other.make_cache()[0]))
        snap = model.snapshot_cache(loaded)
        a = run(model, [ids[30:33]], loaded)
        model.restore_cache(loaded, snap)
        b = run(model, [ids[30:33]], loaded)
        want = run(model, [ids[30:33]], cache)
        self.assertEqual(float(np.abs(a - want).max()), 0.0)
        self.assertEqual(float(np.abs(b - want).max()), 0.0)

    # ----------------------------------------- systems LOW (sparse kernel)
    def test_r1_sparse_kernel_with_fewer_than_8_indices(self):
        """mx.fast.metal_kernel passes inputs of fewer than 8 elements in the
        constant address space; the kernel declared the token list `device`
        and failed to build. Direct calls with 3, 7 and 8 indices against an
        explicit softmax over the listed tokens, and the model path that
        reaches it (ratio 2, top-1 block, a 2-token chunk through the kernel)
        against the dense-masked path."""
        import mlx.core as mx
        import numpy as np
        fx = self.fx
        model = fx.model("fp32")
        attn = g(model, "qsa_sparse_attention")
        rng = np.random.default_rng(5)
        for width in (3, 7, 8):
            with self.subTest(indices=width):
                q = rng.standard_normal((1, 2, 1, 32)).astype(np.float32)
                k = rng.standard_normal((1, 1, 16, 32)).astype(np.float32)
                v = rng.standard_normal((1, 1, 16, 32)).astype(np.float32)
                idx = np.full((1, 1, width), -1, np.int32)
                idx[0, 0, :min(width, 5)] = rng.choice(16, min(width, 5), replace=False)
                out = np.array(attn(mx.array(q), mx.array(k), mx.array(v), mx.array(idx), 0.25))
                t = idx[0, 0][idx[0, 0] >= 0]
                sc = (q[0, :, 0] @ k[0, 0, t].T) * 0.25
                p = np.exp(sc - sc.max(-1, keepdims=True))
                want = (p / p.sum(-1, keepdims=True)) @ v[0, 0, t]
                self.assertLessEqual(float(np.abs(out[0, :, 0] - want).max()), 1e-5)
        tc = fx.text_config("fp32", indexer_compress_ratio=2, indexer_budget=2)
        kern = fx.model("fp32", text_config=tc, qsa_sparse_prefill_min_kv=0)
        dense = fx.model("fp32", text_config=tc)
        cls = type(kern.layers[QSA_LAYERS[0]].self_attn)
        ids = fx.seqs["seq_a"][:12]
        outs = {}
        for name, m in (("kernel", kern), ("dense", dense)):
            cache = m.make_cache()
            run(m, [ids[:10]], cache)
            k0 = cls.paths.kernel
            outs[name] = run(m, [ids[10:12]], cache)
            outs[name + "_calls"] = cls.paths.kernel - k0
        self.assertEqual(outs["kernel_calls"], len(QSA_LAYERS), "the 2-token chunk must take the kernel")
        self.assertEqual(outs["dense_calls"], 0)
        self.assertLessEqual(diff(outs["kernel"], outs["dense"])["max_abs"], INTERNAL_FP32_TOL)


if __name__ == "__main__":
    unittest.main()
