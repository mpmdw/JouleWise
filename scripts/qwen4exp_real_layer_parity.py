#!/usr/bin/env python3
"""Real-weight layer parity: JouleWise MLX qwen4_exp port vs transformers 5.22.1.

GOAL item 5 (docs/align/qwen4_exp_port/GOAL.md), early laptop pass for one
GatedDeltaNet layer (2) and one QSA layer (3) of Qwen3.8-Flash-Next.

Both sides get identical official bf16 tensors read with safetensors
``safe_open`` through the checkpoint index. The reference is the official
``Qwen4ExpTextDecoderLayer`` (eager attention, eager experts) driven through the
official ``Qwen4ExpTextModel.forward`` so that positions, masks, the indexer
position history and the hybrid cache are produced by transformers itself; the
other 47 layers are pass-throughs and the layer before the one under test
injects the input streams. The port side is ``DecoderLayer`` from
``joulewise/align/models/qwen4_exp.py`` with weights mapped by the port's own
``Model.sanitize``.

Routed experts are never materialized in full. The reference experts module
runs its unmodified eager forward over a lazy weight object that reads one
selected expert at a time; the port's ``switch_mlp`` is replaced by a wrapper
that receives the port router's indices, reads only those experts, builds a
compact ``SwitchGLU`` from them (via the port's sanitize), and remaps indices.

Memory guard: ``memory_pressure`` is checked before every heavy step (stop if
free < --min-free-pct) and a watchdog aborts if the process phys_footprint
(includes Metal buffers, unlike RSS) exceeds --limit-gb.

Run (one layer per process):
  nice -n 10 env OMP_NUM_THREADS=2 TMPDIR=/private/tmp/jwrealparity \\
      HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \\
      /private/tmp/jwsol/venv-both/bin/python -B scripts/qwen4exp_real_layer_parity.py \\
      --weights /private/tmp/jwflash-weights --layer 2 --out /private/tmp/jwrealparity/L2.json
"""
import argparse
import ctypes
import gc
import importlib.util
import json
import os
import re
import resource
import subprocess
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PORT_FILE = ROOT / "joulewise/align/models/qwen4_exp.py"

# Special ids from the official tokenizer_config.json (added_tokens_decoder).
EOS, IM_START, IM_END, THINK, END_THINK = 248044, 248045, 248046, 248068, 248069
PROMPT_LENGTHS = (8, 9, 10)

# ---------------------------------------------------------------- guard ----


class Guard:
    """memory_pressure gate plus a phys_footprint watchdog."""

    def __init__(self, limit_gb, min_free_pct):
        self.limit = limit_gb * 2**30
        self.min_free = min_free_pct
        self.events = []
        self.peak_fp = 0
        self._libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
        self._buf = (ctypes.c_uint64 * 64)()
        threading.Thread(target=self._watch, daemon=True).start()

    def footprint(self):
        # rusage_info_v4: 16-byte uuid then uint64 fields; ri_phys_footprint is field 7.
        if self._libc.proc_pid_rusage(os.getpid(), 4, ctypes.byref(self._buf)):
            return 0
        return self._buf[2 + 7]

    @staticmethod
    def peak_rss():
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss  # bytes on Darwin

    def _watch(self):
        while True:
            fp = self.footprint()
            self.peak_fp = max(self.peak_fp, fp)
            if fp > self.limit or self.peak_rss() > self.limit:
                sys.stderr.write(f"ABORT: footprint {fp / 2**30:.2f} GB / peak RSS "
                                 f"{self.peak_rss() / 2**30:.2f} GB over limit\n")
                sys.stderr.flush()
                os._exit(3)
            time.sleep(0.2)

    def free_pct(self):
        out = subprocess.run(["memory_pressure"], capture_output=True, text=True, timeout=180).stdout
        return int(re.search(r"free percentage:\s*(\d+)%", out)[1])

    def check(self, step):
        pct = self.free_pct()
        event = dict(step=step, free_pct=pct, footprint_gb=round(self.footprint() / 2**30, 3),
                     peak_footprint_gb=round(self.peak_fp / 2**30, 3),
                     peak_rss_gb=round(self.peak_rss() / 2**30, 3))
        self.events.append(event)
        print(f"[guard] {json.dumps(event)}", flush=True)
        if pct < self.min_free:
            raise SystemExit(f"memory_pressure free {pct}% < {self.min_free}% before {step}; stopping")


# ----------------------------------------------------------- checkpoint ----


class Checkpoint:
    def __init__(self, root):
        self.root = Path(root)
        self.map = json.loads((self.root / "model.safetensors.index.json").read_text())["weight_map"]
        self.config = json.loads((self.root / "config.json").read_text())
        self.bytes_read = 0

    def layer_names(self, layer):
        prefix = f"model.language_model.layers.{layer}."
        return sorted(k for k in self.map if k.startswith(prefix))

    def read(self, names):
        """Official tensors as torch bf16, one short-lived safe_open per shard."""
        from safetensors import safe_open
        out, files = {}, defaultdict(list)
        for name in names:
            files[self.map[name]].append(name)
        for file, group in files.items():
            with safe_open(self.root / file, framework="pt") as handle:
                for name in group:
                    out[name] = handle.get_tensor(name).clone()
                    self.bytes_read += out[name].numel() * out[name].element_size()
        return out

    def rows(self, name, ids):
        import torch
        from safetensors import safe_open
        with safe_open(self.root / self.map[name], framework="pt") as handle:
            sl = handle.get_slice(name)
            out = torch.cat([sl[int(i):int(i) + 1] for i in ids]).clone()
        self.bytes_read += out.numel() * out.element_size()
        return out


class ExpertReader:
    """Reads single routed experts of one layer from the fused official tensors."""

    def __init__(self, ckpt, layer):
        prefix = f"model.language_model.layers.{layer}.mlp.experts."
        self.ckpt, self.names = ckpt, (prefix + "gate_up_proj", prefix + "down_proj")
        self.expert_reads = 0
        self.max_stack = 0

    def one(self, expert):
        from safetensors import safe_open
        out = []
        for name in self.names:
            with safe_open(self.ckpt.root / self.ckpt.map[name], framework="pt") as handle:
                out.append(handle.get_slice(name)[expert:expert + 1][0].clone())
        self.expert_reads += 1
        return out

    def stacks_u16(self, experts):
        """bf16 bit patterns of the selected experts only: [U,1280,2560], [U,2560,640]."""
        import torch
        from safetensors import safe_open
        self.max_stack = max(self.max_stack, len(experts))
        out = []
        for name in self.names:
            with safe_open(self.ckpt.root / self.ckpt.map[name], framework="pt") as handle:
                sl = handle.get_slice(name)
                shape = sl.get_shape()[1:]
                stack = np.empty((len(experts), *shape), dtype=np.uint16)
                for i, e in enumerate(experts):
                    stack[i] = sl[int(e):int(e) + 1][0].contiguous().view(torch.int16).numpy().view(np.uint16)
            out.append(stack)
        self.expert_reads += len(experts)
        return out


def bf16_bits(t):
    import torch
    assert t.dtype == torch.bfloat16
    return t.contiguous().view(torch.int16).numpy().view(np.uint16)


# ------------------------------------------------------------ reference ----


def reference_modules():
    import torch
    from transformers import Qwen4ExpTextConfig
    from transformers.cache_utils import DynamicCache
    from transformers.models.qwen4_exp import modeling_qwen4_exp as M

    class Pass(torch.nn.Module):
        def forward(self, hidden_states, *args, **kwargs):
            return hidden_states

    class Injector(torch.nn.Module):
        value = None

        def forward(self, hidden_states, *args, **kwargs):
            return self.value

    class AttnOnly(torch.nn.Module):
        def __init__(self, attn):
            super().__init__()
            self.attn = attn

        def forward(self, hidden_states, position_embeddings=None, attention_mask=None,
                    past_key_values=None, **kwargs):
            return self.attn(hidden_states, position_embeddings, attention_mask=attention_mask,
                             past_key_values=past_key_values)[0]

    class LazyExpertWeights:
        """Stands in for experts.gate_up_proj / down_proj in the official eager loop."""

        def __init__(self, holder, part):
            self.holder, self.part = holder, part

        def __getitem__(self, index):
            return self.holder.get(int(index))[self.part]

    class LazyHolder:
        def __init__(self, reader, dtype):
            self.reader, self.dtype, self.last, self.hits = reader, dtype, None, set()

        def get(self, expert):
            if self.last is None or self.last[0] != expert:
                self.last = (expert, [t.to(self.dtype) for t in self.reader.one(expert)])
            self.hits.add(expert)
            return self.last[1]

    return SimpleNamespace(torch=torch, M=M, Config=Qwen4ExpTextConfig, DynamicCache=DynamicCache,
                           Pass=Pass, Injector=Injector, AttnOnly=AttnOnly,
                           LazyExpertWeights=LazyExpertWeights, LazyHolder=LazyHolder)


class RefLayer:
    def __init__(self, R, ckpt, layer, dtype_name, reader, attn_only=False):
        torch = R.torch
        self.R, self.layer = R, layer
        self.dtype = dict(fp32=torch.float32, bf16=torch.bfloat16)[dtype_name]
        cfg = R.Config(**ckpt.config["text_config"])
        cfg._attn_implementation = "eager"
        cfg._experts_implementation = "eager"
        self.cfg = cfg
        with torch.device("meta"):
            tm = R.M.Qwen4ExpTextModel(cfg)
        real = tm.layers[layer]
        experts = real.mlp.experts
        del experts.gate_up_proj
        del experts.down_proj
        real.to_empty(device="cpu")
        real.to(self.dtype)
        prefix = f"model.language_model.layers.{layer}."
        names = [n for n in ckpt.layer_names(layer) if ".mlp.experts." not in n]
        state = {k[len(prefix):]: v.to(self.dtype) for k, v in ckpt.read(names).items()}
        result = real.load_state_dict(state, strict=False)
        if result.missing_keys or result.unexpected_keys:
            raise RuntimeError(f"reference load: missing={result.missing_keys} unexpected={result.unexpected_keys}")
        self.holder = R.LazyHolder(reader, self.dtype)
        experts.gate_up_proj = R.LazyExpertWeights(self.holder, 0)
        experts.down_proj = R.LazyExpertWeights(self.holder, 1)
        self.injector = R.Injector()
        layers = [R.Pass() for _ in range(cfg.num_hidden_layers)]
        layers[layer - 1] = self.injector
        layers[layer] = R.AttnOnly(real.self_attn) if attn_only else real
        tm.layers = torch.nn.ModuleList(layers)
        tm.hyper_connection_mixer = R.Pass()
        tm.rotary_emb = R.M.Qwen4ExpTextRotaryEmbedding(cfg)
        self.tm, self.real = tm.eval(), real.eval()
        self.rec = defaultdict(list)
        self._hooks(attn_only)

    def _hooks(self, attn_only):
        real, rec = self.real, self.rec

        def f(t):
            return t.detach().float().numpy().copy()

        def add(module, fn):
            def hook(m, a, o):
                fn(o)  # a hook returning non-None would replace the module output
            module.register_forward_hook(hook)
        if not attn_only:
            add(real.attn_hyper_connection, lambda o: (rec["attn_hc_mixed"].append(f(o[0])),
                                                      rec["attn_hc_inject"].append(f(o[2]))))
            add(real.mlp_hyper_connection, lambda o: (rec["mid_stream"].append(f(o[1])),
                                                     rec["mlp_hc_mixed"].append(f(o[0])),
                                                     rec["mlp_hc_inject"].append(f(o[2]))))
            add(real.mlp.gate, lambda o: (rec["router_logits"].append(f(o[0])),
                                          rec["router_weights"].append(f(o[1])),
                                          rec["experts"].append(o[2].numpy().copy())))
            add(real.mlp, lambda o: rec["moe_out"].append(f(o)))
        if hasattr(real, "linear_attn"):
            add(real.linear_attn, lambda o: rec["attn_out"].append(f(o)))
        else:
            add(real.self_attn, lambda o: rec["attn_out"].append(f(o[0])))
            add(real.self_attn.indexer, lambda o: rec["indexer_selected"].append(
                (o == 0).numpy().copy() if o.is_floating_point() else o.numpy().copy()))

    def cache(self):
        return self.R.DynamicCache(config=self.cfg)

    def __call__(self, stream, cache=None):
        torch = self.R.torch
        self.injector.value = stream
        b, s = stream.shape[:2]
        with torch.inference_mode():
            out = self.tm(inputs_embeds=torch.zeros(b, s, self.cfg.hidden_size, dtype=self.dtype),
                          ple_input_ids=torch.zeros(b, s, dtype=torch.long),
                          past_key_values=cache, use_cache=cache is not None)
        return out.last_hidden_state.float().numpy().copy()

    def take(self):
        # The hooks close over this dict object: hand out its lists, then empty it in place.
        out = dict(self.rec)
        self.rec.clear()
        return out


# ------------------------------------------------------------------ port ----


def port_modules():
    import mlx.core as mx
    import mlx.nn as nn
    spec = importlib.util.spec_from_file_location("jw_qwen4_exp_port_under_test", PORT_FILE)
    Q = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(Q)

    class Rec(nn.Module):
        def __init__(self, inner, name, sink):
            super().__init__()
            self.inner = inner
            self._meta = SimpleNamespace(name=name, sink=sink)

        def __call__(self, *args, **kwargs):
            out = self.inner(*args, **kwargs)
            self._meta.sink[self._meta.name].append((args, out))
            return out

    class LazySwitch(nn.Module):
        """Receives the port router's indices; loads only those experts."""

        def __init__(self, args, reader, layer, dtype, bits=None, group_size=64):
            super().__init__()
            self._meta = SimpleNamespace(args=args, reader=reader, layer=layer, dtype=dtype, log=[],
                                         bits=bits, group_size=group_size)

        def __call__(self, x, indices):
            m = self._meta
            idx = np.array(indices).astype(np.int64)
            uniq = np.unique(idx)
            lut = np.full(m.args.num_experts, -1, dtype=np.int64)
            lut[uniq] = np.arange(len(uniq))
            gu16, dn16 = m.reader.stacks_u16(uniq)
            gu = mx.array(gu16).view(mx.bfloat16)
            dn = mx.array(dn16).view(mx.bfloat16)
            del gu16, dn16
            p = f"model.language_model.layers.{m.layer}.mlp.experts."
            san = Q.Model.sanitize(SimpleNamespace(args=m.args), {p + "gate_up_proj": gu, p + "down_proj": dn})
            q = f"model.layers.{m.layer}.mlp.switch_mlp."
            if sorted(san) != sorted(q + n for n in ("gate_proj.weight", "up_proj.weight", "down_proj.weight")):
                raise RuntimeError(f"unexpected sanitize output {sorted(san)}")
            switch = Q.SwitchGLU(m.args.hidden_size, m.args.moe_intermediate_size, len(uniq))
            switch.load_weights([(k[len(q):], v.astype(m.dtype)) for k, v in san.items()], strict=True)
            if m.bits:
                # MLX's own affine quantization (as the converter's mx.quantize on bf16 rows).
                # Groups run along each expert row, so quantizing the selected experts alone
                # is identical to quantizing the full 512-expert stack and slicing.
                for name in ("gate_proj", "up_proj", "down_proj"):
                    setattr(switch, name, getattr(switch, name).to_quantized(
                        group_size=m.group_size, bits=m.bits, mode="affine"))
            mx.eval(switch.parameters())
            del gu, dn, san
            out = switch(x, mx.array(lut[idx].astype(np.uint32)))
            mx.eval(out)
            m.log.append(idx)
            return out

    return SimpleNamespace(mx=mx, nn=nn, Q=Q, Rec=Rec, LazySwitch=LazySwitch)


class PortLayer:
    def __init__(self, P, ckpt, layer, dtype_name, reader, attn_only=False, expert_bits=None):
        mx, Q = P.mx, P.Q
        self.P, self.layer = P, layer
        self.dtype = dict(fp32=mx.float32, bf16=mx.bfloat16)[dtype_name]
        self.args = Q.ModelArgs.from_dict(ckpt.config)
        dl = Q.DecoderLayer(self.args, layer)
        dl.mlp.switch_mlp = P.LazySwitch(self.args, reader, layer, self.dtype, bits=expert_bits)
        names = [n for n in ckpt.layer_names(layer) if ".mlp.experts." not in n]
        weights = {n: mx.array(bf16_bits(t)).view(mx.bfloat16).astype(self.dtype)
                   for n, t in ckpt.read(names).items()}
        san = Q.Model.sanitize(SimpleNamespace(args=self.args), weights)
        prefix = f"model.layers.{layer}."
        if not all(k.startswith(prefix) for k in san):
            raise RuntimeError("sanitize produced keys outside the layer")
        dl.load_weights([(k[len(prefix):], v) for k, v in san.items()], strict=True)
        mx.eval(dl.parameters())
        dl.eval()
        self.linear = dl._linear
        self.rec = defaultdict(list)
        if not attn_only:
            for name in ("attn_hyper_connection", "mlp_hyper_connection", "mlp"):
                setattr(dl, name, P.Rec(getattr(dl, name), name, self.rec))
            dl.mlp.inner.gate = P.Rec(dl.mlp.inner.gate, "gate", self.rec)
        if self.linear:
            dl.linear_attn = P.Rec(dl.linear_attn, "attn", self.rec)
        else:
            dl.self_attn.indexer = P.Rec(dl.self_attn.indexer, "indexer", self.rec)
            dl.self_attn = P.Rec(dl.self_attn, "attn", self.rec)
        self.dl = dl
        self.switch = dl.mlp.inner.switch_mlp if not attn_only else None

    def cache(self):
        Q = self.P.Q
        return Q.Qwen4ExpRecurrentCache() if self.linear else Q.Qwen4ExpAttentionCache()

    def __call__(self, stream, cache=None):
        mx = self.P.mx
        b, s = stream.shape[:2]
        x = mx.array(stream) if stream.dtype != np.uint16 else mx.array(stream).view(mx.bfloat16)
        out = self.dl(x.astype(self.dtype), mx.zeros((b, s), dtype=mx.int32), mx.ones((b, s), dtype=mx.bool_), cache)
        mx.eval(out)
        return np.array(out.astype(mx.float32))

    def attention(self, x, mask, cache):
        return self.dl.self_attn(x, mask, cache)

    def take(self):
        mx = self.P.mx
        f = lambda a: np.array(a.astype(mx.float32))  # noqa: E731
        rec = defaultdict(list)
        for args, out in self.rec.pop("attn_hyper_connection", []):
            rec["attn_hc_mixed"].append(f(out[0]))
            rec["attn_hc_inject"].append(f(out[1]))
        for args, out in self.rec.pop("mlp_hyper_connection", []):
            rec["mid_stream"].append(f(args[0]))
            rec["mlp_hc_mixed"].append(f(out[0]))
            rec["mlp_hc_inject"].append(f(out[1]))
        for args, out in self.rec.pop("gate", []):
            rec["router_logits"].append(f(out))
        for args, out in self.rec.pop("mlp", []):
            rec["moe_out"].append(f(out))
        for args, out in self.rec.pop("attn", []):
            rec["attn_out"].append(f(out))
        for args, out in self.rec.pop("indexer", []):
            rec["indexer_raw"].append(None if out is None else (np.array(out[0]), np.array(out[1])))
        if self.switch is not None:
            rec["experts"] = list(self.switch._meta.log)
            self.switch._meta.log.clear()
        self.rec.clear()
        return rec


# --------------------------------------------------------------- metrics ----


def metrics(port, ref):
    a = np.asarray(port, dtype=np.float64).ravel()
    b = np.asarray(ref, dtype=np.float64).ravel()
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch {a.shape} vs {b.shape}")
    d = np.abs(a - b)
    ref_max = float(np.abs(b).max())
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return dict(max_abs=float(d.max()), max_rel=float(d.max() / ref_max) if ref_max else float("nan"),
                rel_l2=float(np.linalg.norm(a - b) / max(np.linalg.norm(b), 1e-300)),
                cos=float(a @ b / denom) if denom else float("nan"), ref_max_abs=ref_max)


def cat(parts, axis):
    return np.concatenate(parts, axis=axis) if len(parts) > 1 else parts[0]


def normalize(rec, side, n_tokens):
    """Concatenate per-call captures along the sequence and flatten tokens."""
    out = {}
    for name in ("attn_hc_mixed", "attn_hc_inject", "attn_out", "mid_stream", "mlp_hc_mixed",
                 "mlp_hc_inject", "moe_out"):
        if rec.get(name):
            out[name] = cat(rec[name], 1).reshape(n_tokens, -1)
    if rec.get("router_logits"):
        axis = 0 if side == "ref" else 1
        out["router_logits"] = cat(rec["router_logits"], axis).reshape(n_tokens, -1)
    if rec.get("router_weights"):
        out["router_weights"] = cat(rec["router_weights"], 0).reshape(n_tokens, -1)
    if rec.get("experts"):
        axis = 0 if side == "ref" else 1
        out["experts"] = cat(rec["experts"], axis).reshape(n_tokens, -1)
    for name in ("indexer_selected", "indexer_raw"):
        if name in rec:
            out[name] = rec[name]
    return out


def expert_agreement(port_sets, ref_sets, ref_logits):
    agree = 0
    mismatches = []
    for t, (p, r) in enumerate(zip(port_sets, ref_sets)):
        if set(p.tolist()) == set(r.tolist()):
            agree += 1
        else:
            order = np.sort(ref_logits[t])[::-1]
            mismatches.append(dict(token=t, port_only=sorted(set(p.tolist()) - set(r.tolist())),
                                   ref_only=sorted(set(r.tolist()) - set(p.tolist())),
                                   ref_logit_margin_k_vs_k1=float(order[len(r) - 1] - order[len(r)])))
    return dict(tokens=len(ref_sets), agree=agree, mismatches=mismatches)


def boundary_margin(logits, k):
    order = np.sort(logits, axis=-1)[:, ::-1]
    return order[:, k - 1] - order[:, k]


# ---------------------------------------------------------------- inputs ----


def make_prompts():
    rng = np.random.default_rng(20261105)
    prompts = []
    for i, n in enumerate(PROMPT_LENGTHS):
        body = rng.integers(0, EOS, size=n - 3).tolist()
        if i == 0:
            ids = [IM_START, *body, IM_END, IM_START]
        elif i == 1:
            ids = [IM_START, *body[:3], body[1], *body[3:], THINK][:n]
            ids = (ids + [END_THINK] * n)[:n]
        else:
            ids = [EOS, IM_START, *body[:-1], body[0], END_THINK][:n]
            ids = (ids + [IM_END] * n)[:n]
        prompts.append(ids)
    return prompts


def build_inputs(ckpt, args_hc, hidden):
    import torch
    prompts = make_prompts()
    emb_name = "model.language_model.embed_tokens.weight"
    sets = []
    rms = []
    for i, ids in enumerate(prompts):
        rows = ckpt.rows(emb_name, ids).float()  # bf16 values, exact in fp32
        rms.append(rows.pow(2).mean().sqrt().item())
        sets.append(dict(name=f"real_prompt{i}", kind="real-embedding (tiled x hc_count, as the official forward)",
                         ids=ids, stream=rows.repeat(1, args_hc).unsqueeze(0).numpy()))
    scale = float(np.sqrt(np.mean(np.square(rms))))
    for i, n in enumerate(PROMPT_LENGTHS):
        g = np.random.default_rng(7000 + i)
        sets.append(dict(name=f"random{i}", kind=f"seeded N(0, {scale:.4g}^2), independent per stream",
                         ids=None, seed=7000 + i,
                         stream=(g.standard_normal((1, n, args_hc * hidden)) * scale).astype(np.float32)))
    return sets, scale


def to_dtype_stream(stream, dtype_name):
    """Identical bits for both sides: fp32 as is, bf16 rounded once by torch (RNE)."""
    import torch
    t = torch.from_numpy(stream)
    if dtype_name == "bf16":
        t = t.to(torch.bfloat16)
    return t


# ---------------------------------------------------------------- driver ----


def run_layer_cases(args, ckpt, guard, layer, dtype_name, sets, R, P, results, store):
    import torch
    mx = P.mx
    reader = ExpertReader(ckpt, layer)
    guard.check(f"L{layer} {dtype_name}: build reference + port layers")
    ref = RefLayer(R, ckpt, layer, dtype_name, reader)
    port = PortLayer(P, ckpt, layer, dtype_name, reader)
    k = port.args.num_experts_per_tok
    for case in sets:
        guard.check(f"L{layer} {dtype_name} {case['name']}")
        t_in = to_dtype_stream(case["stream"], dtype_name)
        np_in = bf16_bits(t_in) if dtype_name == "bf16" else t_in.numpy()
        n = t_in.shape[1]
        runs = {}
        t0 = time.time()
        runs["ref_prefill"] = (ref(t_in), normalize(ref.take(), "ref", n))
        runs["port_prefill"] = (port(np_in), normalize(port.take(), "port", n))
        cache = ref.cache()
        outs = [ref(t_in[:, i:i + 1], cache) for i in range(n)]
        runs["ref_step"] = (cat(outs, 1), normalize(ref.take(), "ref", n))
        cache = port.cache()
        outs = [port(np_in[:, i:i + 1], cache) for i in range(n)]
        runs["port_step"] = (cat(outs, 1), normalize(port.take(), "port", n))
        elapsed = time.time() - t0
        store[(layer, dtype_name, case["name"])] = runs
        for mode in ("prefill", "step"):
            (p_out, p), (r_out, r) = runs[f"port_{mode}"], runs[f"ref_{mode}"]
            entry = dict(layer=layer, dtype=dtype_name, input=case["name"], mode=mode, tokens=n, seconds=elapsed,
                         tensors={"layer_out": metrics(p_out.reshape(n, -1), r_out.reshape(n, -1))})
            for name in ("attn_hc_mixed", "attn_hc_inject", "attn_out", "mid_stream", "mlp_hc_mixed",
                         "mlp_hc_inject", "router_logits", "moe_out"):
                entry["tensors"][name] = metrics(p[name], r[name])
            entry["experts"] = expert_agreement(p["experts"], r["experts"], r["router_logits"])
            agree = np.array([set(a.tolist()) == set(b.tolist()) for a, b in zip(p["experts"], r["experts"])])
            if not agree.all() and agree.any():
                entry["tensors_agreeing_tokens"] = {
                    "moe_out": metrics(p["moe_out"][agree], r["moe_out"][agree]),
                    "layer_out": metrics(p_out.reshape(n, -1)[agree], r_out.reshape(n, -1)[agree])}
            entry["ref_boundary_margin_min"] = float(boundary_margin(r["router_logits"], k).min())
            if not port.linear:
                entry["indexer"] = indexer_short_check(r["indexer_selected"], p["indexer_raw"], n)
            results["cases"].append(entry)
        # self-consistency: prefill == stepwise inside each framework
        for side in ("port", "ref"):
            results["self"].append(dict(layer=layer, dtype=dtype_name, input=case["name"], side=side,
                                        layer_out=metrics(runs[f"{side}_step"][0], runs[f"{side}_prefill"][0]),
                                        experts_equal=bool(np.array_equal(
                                            np.sort(runs[f"{side}_step"][1]["experts"], -1),
                                            np.sort(runs[f"{side}_prefill"][1]["experts"], -1)))))
        print(f"[case] L{layer} {dtype_name} {case['name']} n={n} {elapsed:.1f}s "
              f"out max_rel={results['cases'][-2]['tensors']['layer_out']['max_rel']:.3g} "
              f"experts {results['cases'][-2]['experts']['agree']}/{n}", flush=True)
        del runs
        gc.collect()
        mx.clear_cache()
    results["reader"][f"L{layer}_{dtype_name}"] = dict(expert_reads=reader.expert_reads,
                                                        max_port_expert_stack=reader.max_stack,
                                                        ref_distinct_experts_touched=len(ref.holder.hits))
    del ref, port
    gc.collect()
    mx.clear_cache()


def run_quant_cases(args, ckpt, guard, layer, sets, P, results, store):
    """bf16 port with routed experts in MLX affine 6-bit (group 64) vs bf16 port and vs fp32 truth."""
    mx = P.mx
    bits, gs = args.expert_bits, 64
    reader = ExpertReader(ckpt, layer)
    guard.check(f"L{layer} q{bits} experts: build port layer")
    port = PortLayer(P, ckpt, layer, "bf16", reader, expert_bits=bits)
    for case in sets:
        key16, key32 = (layer, "bf16", case["name"]), (layer, "fp32", case["name"])
        if key16 not in store or key32 not in store:
            continue
        guard.check(f"L{layer} q{bits} {case['name']}")
        t_in = to_dtype_stream(case["stream"], "bf16")
        np_in = bf16_bits(t_in)
        n = t_in.shape[1]
        runs = {"prefill": (port(np_in), normalize(port.take(), "port", n))}
        cache = port.cache()
        outs = [port(np_in[:, i:i + 1], cache) for i in range(n)]
        runs["step"] = (cat(outs, 1), normalize(port.take(), "port", n))
        for mode in ("prefill", "step"):
            q_out, q = runs[mode]
            b_out, b = store[key16][f"port_{mode}"]
            f_out, f = store[key32][f"ref_{mode}"]
            row = dict(layer=layer, input=case["name"], mode=mode, bits=bits, group_size=gs,
                       experts_equal_to_bf16=bool(np.array_equal(np.sort(q["experts"], -1), np.sort(b["experts"], -1))),
                       attn_out_identical_to_bf16=bool(np.array_equal(q["attn_out"], b["attn_out"])))
            for name in ("moe_out", "layer_out"):
                qa = q_out.reshape(n, -1) if name == "layer_out" else q[name]
                ba = b_out.reshape(n, -1) if name == "layer_out" else b[name]
                fa = f_out.reshape(n, -1) if name == "layer_out" else f[name]
                row[name] = dict(q_vs_bf16=metrics(qa, ba), q_vs_fp32_truth=metrics(qa, fa),
                                 bf16_vs_fp32_truth=metrics(ba, fa))
            results["quant"].append(row)
        print(f"[quant] L{layer} {case['name']} moe_out rel_l2 q{bits}-vs-bf16 "
              f"{results['quant'][-2]['moe_out']['q_vs_bf16']['rel_l2']:.3g}", flush=True)
        gc.collect()
        mx.clear_cache()
    del port
    gc.collect()
    mx.clear_cache()


def indexer_short_check(ref_selected, port_raw, n):
    """Below the token budget the official indexer must select every causal key,
    which is exactly the port's dense shortcut (it returns None)."""
    sel = selected_matrix_ref(ref_selected, n)
    return dict(ref_selection_equals_causal=bool((sel == np.tril(np.ones((n, n), dtype=bool))).all()),
                port_dense_shortcut_every_call=all(raw is None for raw in port_raw))


def cross_dtype(results, store, layer, sets):
    """bf16 port and bf16 reference, each against the fp32 reference (ground truth)."""
    for case in sets:
        key32, key16 = (layer, "fp32", case["name"]), (layer, "bf16", case["name"])
        if key32 not in store or key16 not in store:
            continue
        truth_pair = store[key32]["ref_prefill"]
        truth = truth_pair[1]
        n = case["stream"].shape[1]
        row = dict(layer=layer, input=case["name"], tensors={})
        for name in ("layer_out", "attn_out", "router_logits", "moe_out", "mlp_hc_mixed", "attn_hc_mixed"):
            def get(run):
                return run[0].reshape(n, -1) if name == "layer_out" else run[1][name]
            port_err = metrics(get(store[key16]["port_prefill"]), get(store[key32]["ref_prefill"]))
            ref_err = metrics(get(store[key16]["ref_prefill"]), get(store[key32]["ref_prefill"]))
            row["tensors"][name] = dict(port_bf16_vs_ref_fp32=port_err, ref_bf16_vs_ref_fp32=ref_err,
                                        ratio_max_abs=port_err["max_abs"] / max(ref_err["max_abs"], 1e-30),
                                        ratio_rel_l2=port_err["rel_l2"] / max(ref_err["rel_l2"], 1e-30))
        sets32 = truth["experts"]
        row["expert_sets_vs_fp32_truth"] = dict(
            port_bf16=sum(set(a.tolist()) == set(b.tolist()) for a, b in zip(store[key16]["port_prefill"][1]["experts"], sets32)),
            ref_bf16=sum(set(a.tolist()) == set(b.tolist()) for a, b in zip(store[key16]["ref_prefill"][1]["experts"], sets32)),
            tokens=n)
        row["bf16_flips"] = classify_flips(store, key32, key16, n)
        # Accuracy vs the fp32 truth on consensus tokens (bf16 port, bf16 reference and fp32
        # truth route to the same experts): excludes discontinuous near-tie routing flips.
        p16, r16 = store[key16]["port_prefill"], store[key16]["ref_prefill"]
        cons = np.array([set(a.tolist()) == set(b.tolist()) == set(c.tolist()) for a, b, c in
                         zip(p16[1]["experts"], r16[1]["experts"], sets32)])
        row["consensus_tokens"] = dict(count=int(cons.sum()), tokens=n, tensors={})
        if cons.any():
            for name in ("attn_out", "router_logits", "moe_out", "layer_out"):
                def get(run):
                    return (run[0].reshape(n, -1) if name == "layer_out" else run[1][name])[cons]
                pe, re_ = metrics(get(p16), get(truth_pair)), metrics(get(r16), get(truth_pair))
                row["consensus_tokens"]["tensors"][name] = dict(
                    port_bf16_vs_ref_fp32=pe, ref_bf16_vs_ref_fp32=re_,
                    ratio_rel_l2=pe["rel_l2"] / max(re_["rel_l2"], 1e-30),
                    ratio_max_abs=pe["max_abs"] / max(re_["max_abs"], 1e-30),
                    per_token_rel_l2_port=[float(np.linalg.norm(a - b) / np.linalg.norm(b)) for a, b in zip(get(p16), get(truth_pair))],
                    per_token_rel_l2_ref=[float(np.linalg.norm(a - b) / np.linalg.norm(b)) for a, b in zip(get(r16), get(truth_pair))])
        results["cross_dtype"].append(row)


def classify_flips(store, key32, key16, n, k=10):
    """Each token where bf16 port and bf16 reference pick different expert sets:
    is it a near tie in the fp32 truth? Criterion: every swapped expert's fp32
    logit lies within 2x the token's bf16 router-logit error (max over both
    implementations, vs fp32 truth) of the fp32 top-k boundary."""
    out = []
    for mode in ("prefill", "step"):
        truth = store[key32][f"ref_{mode}"][1]["router_logits"]
        p16, r16 = store[key16][f"port_{mode}"][1], store[key16][f"ref_{mode}"][1]
        for t in range(n):
            a, b = set(p16["experts"][t].tolist()), set(r16["experts"][t].tolist())
            if a == b:
                continue
            order = np.argsort(-truth[t])
            rank = {int(e): int(np.where(order == e)[0][0]) + 1 for e in a ^ b}
            boundary = 0.5 * (truth[t, order[k - 1]] + truth[t, order[k]])
            err = max(np.abs(p16["router_logits"][t] - truth[t]).max(), np.abs(r16["router_logits"][t] - truth[t]).max())
            dist = {e: float(abs(truth[t, e] - boundary)) for e in a ^ b}
            out.append(dict(mode=mode, token=t, port_only=sorted(a - b), ref_only=sorted(b - a),
                            fp32_ranks=rank, fp32_dist_to_boundary=dist, bf16_logit_err=float(err),
                            fp32_boundary_margin=float(truth[t, order[k - 1]] - truth[t, order[k]]),
                            near_tie=bool(all(d <= 2 * err for d in dist.values()))))
    return out


# --------------------------------------------------------- long QSA test ----


def selected_matrix_ref(parts, total):
    """Reference indexer masks [1,1,s,kv] (bool selected) -> [total, total] bool."""
    out = np.zeros((total, total), dtype=bool)
    row = 0
    for m in parts:
        m = m[0, 0]
        out[row:row + m.shape[0], :m.shape[1]] = m
        row += m.shape[0]
    return out


def selected_matrix_port(parts, chunk_sizes, total):
    out = np.zeros((total, total), dtype=bool)
    row = 0
    for raw, s in zip(parts, chunk_sizes):
        if raw is None:  # dense path: every causal key visible
            for q in range(row, row + s):
                out[q, :q + 1] = True
        else:
            idx, keep = raw
            for j in range(s):
                out[row + j, idx[0, j][keep[0, j]]] = True
        row += s
    return out


def long_qsa(args, ckpt, guard, R, P, results):
    import torch
    mx = P.mx
    layer, total = 3, args.long_tokens
    rng = np.random.default_rng(424242)
    ids = rng.integers(0, EOS, size=total)
    emb = ckpt.rows("model.language_model.embed_tokens.weight", ids.tolist()).float()
    reader = ExpertReader(ckpt, layer)
    out = dict(tokens=total, budget=None, sparse_from_query=None, runs={})
    truth = {}
    for dtype_name in args.dtypes:
        guard.check(f"long QSA {dtype_name}: build attention-only layers")
        ref = RefLayer(R, ckpt, layer, dtype_name, reader, attn_only=True)
        port = PortLayer(P, ckpt, layer, dtype_name, reader, attn_only=True)
        budget, ratio = port.args.indexer_budget, port.args.indexer_compress_ratio
        out["budget"], out["compress_ratio"] = budget, ratio
        # Sparse selection drops a block once complete blocks exceed budget/ratio.
        out["sparse_from_query"] = (budget // ratio + 1) * ratio - 1
        stream = emb.repeat(1, ref.cfg.hc_count).unsqueeze(0)
        if "attn_in" not in truth:
            # Realistic attention input: official attn hyper-connection of layer 3 on tiled real embeddings (fp32).
            with torch.inference_mode():
                truth["attn_in"] = ref.real.attn_hyper_connection.float()(stream)[0].numpy().copy()
            ref.real.attn_hyper_connection.to(ref.dtype)
        t_in = to_dtype_stream(truth["attn_in"], dtype_name)
        np_in = bf16_bits(t_in) if dtype_name == "bf16" else t_in.numpy()
        x_mx = (mx.array(np_in).view(mx.bfloat16) if dtype_name == "bf16" else mx.array(np_in))
        mask = mx.ones((1, total), dtype=mx.bool_)
        run = {}
        guard.check(f"long QSA {dtype_name}: reference prefill")
        t0 = time.time()
        run["ref_prefill"] = ref(t_in)
        sel_ref_pre = selected_matrix_ref(ref.take()["indexer_selected"], total)
        run["t_ref_prefill"] = time.time() - t0
        guard.check(f"long QSA {dtype_name}: reference stepwise")
        t0 = time.time()
        cache = ref.cache()
        run["ref_step"] = cat([ref(t_in[:, i:i + 1], cache) for i in range(total)], 1)
        sel_ref_step = selected_matrix_ref(ref.take()["indexer_selected"], total)
        run["t_ref_step"] = time.time() - t0
        del cache
        guard.check(f"long QSA {dtype_name}: port chunked prefill")
        t0 = time.time()
        chunk = port.args.jw_max_prefill_tokens
        cache, outs, sizes = port.cache(), [], []
        for i in range(0, total, chunk):
            o = port.attention(x_mx[:, i:i + chunk], mask[:, i:i + chunk], cache)
            mx.eval(o)
            outs.append(np.array(o.astype(mx.float32)))
            sizes.append(min(chunk, total - i))
        run["port_prefill"] = cat(outs, 1)
        sel_port_pre = selected_matrix_port(port.take()["indexer_raw"], sizes, total)
        run["t_port_prefill"] = time.time() - t0
        guard.check(f"long QSA {dtype_name}: port stepwise")
        t0 = time.time()
        cache, outs = port.cache(), []
        for i in range(total):
            o = port.attention(x_mx[:, i:i + 1], mask[:, i:i + 1], cache)
            mx.eval(o)
            outs.append(np.array(o.astype(mx.float32)))
        run["port_step"] = cat(outs, 1)
        sel_port_step = selected_matrix_port(port.take()["indexer_raw"], [1] * total, total)
        run["t_port_step"] = time.time() - t0
        del cache, outs
        sparse = out["sparse_from_query"]
        res = {}
        for a, b in (("port_prefill", "ref_prefill"), ("port_step", "ref_step"), ("port_step", "port_prefill"),
                     ("ref_step", "ref_prefill")):
            pa, pb = run[a][0], run[b][0]
            res[f"{a}_vs_{b}"] = dict(all=metrics(pa, pb), dense_queries=metrics(pa[:sparse], pb[:sparse]),
                                      sparse_queries=metrics(pa[sparse:], pb[sparse:]))
        causal = np.tril(np.ones((total, total), dtype=bool))
        sel = dict(ref_prefill=sel_ref_pre, ref_step=sel_ref_step, port_prefill=sel_port_pre, port_step=sel_port_step)
        res["selection"] = {}
        for a, b in (("port_prefill", "ref_prefill"), ("port_step", "ref_step"), ("port_step", "port_prefill"),
                     ("ref_step", "ref_prefill")):
            rows = np.where((sel[a] != sel[b]).any(axis=1))[0]
            res["selection"][f"{a}_vs_{b}"] = dict(rows_differing=int(len(rows)), first_rows=rows[:10].tolist())
        guard.check(f"long QSA {dtype_name}: official block scores + forced-selection reference prefill")
        scores = official_block_scores(R, ref, t_in, port.args)
        res["selection"]["tie_analysis_port_prefill_vs_ref_prefill"] = classify_selection_rows(
            sel_port_pre, sel_ref_pre, scores, port.args, sparse)
        res["selection"]["tie_analysis_port_step_vs_ref_step"] = classify_selection_rows(
            sel_port_step, sel_ref_step, scores, port.args, sparse)
        # Official attention with the official indexer replaced by the port's selection:
        # isolates everything downstream of top-k (gather, tail, GQA, masks, gate, o_proj).
        ind = ref.real.self_attn.indexer
        forced = torch.where(torch.from_numpy(sel_port_pre)[None, None], torch.zeros((), dtype=ref.dtype),
                             torch.tensor(torch.finfo(ref.dtype).min, dtype=ref.dtype))
        ind.forward = lambda *a_, **k_: forced
        t0 = time.time()
        forced_out = ref(t_in)
        del ind.forward
        ref.take()
        run["t_ref_forced_prefill"] = time.time() - t0
        res["port_prefill_vs_ref_forced_port_selection"] = dict(
            all=metrics(run["port_prefill"][0], forced_out[0]),
            dense_queries=metrics(run["port_prefill"][0][:sparse], forced_out[0][:sparse]),
            sparse_queries=metrics(run["port_prefill"][0][sparse:], forced_out[0][sparse:]))
        del forced, forced_out
        res["selection"]["ref_dense_rows_equal_causal"] = bool((sel_ref_pre[:sparse] == causal[:sparse]).all())
        res["selection"]["ref_sparse_rows_proper_subset"] = bool(
            ((sel_ref_pre[sparse:] & ~causal[sparse:]).sum() == 0) and (sel_ref_pre[sparse:].sum(1) < causal[sparse:].sum(1)).all())
        res["selection"]["ref_selected_per_sparse_query"] = [int(sel_ref_pre[sparse:].sum(1).min()),
                                                             int(sel_ref_pre[sparse:].sum(1).max())]
        res["timing_s"] = {k: round(v, 1) for k, v in run.items() if k.startswith("t_")}
        out["runs"][dtype_name] = res
        truth[dtype_name] = run
        print(f"[long] {dtype_name}: " + json.dumps({k: v["all"]["max_rel"] for k, v in res.items()
                                                    if isinstance(v, dict) and "all" in v}), flush=True)
        print(f"[long] {dtype_name} selection: {json.dumps(res['selection'])}", flush=True)
        del ref, port
        gc.collect()
        mx.clear_cache()
    if "fp32" in truth and "bf16" in truth:
        out["cross_dtype"] = dict(
            port_bf16_vs_ref_fp32=metrics(truth["bf16"]["port_prefill"], truth["fp32"]["ref_prefill"]),
            ref_bf16_vs_ref_fp32=metrics(truth["bf16"]["ref_prefill"], truth["fp32"]["ref_prefill"]))
    out["rope_tables"] = rope_check(P, R, ckpt, total)
    results["long_qsa"] = out


def rope_check(P, R, ckpt, total):
    """Port rope() cos/sin (extracted through the port function) vs official rotary tables, fp32."""
    mx, Q, torch = P.mx, P.Q, R.torch
    args = Q.ModelArgs.from_dict(ckpt.config)
    dim = int(args.head_dim * args.rope_parameters["partial_rotary_factor"])
    probe = np.zeros((1, total, 1, args.head_dim), dtype=np.float32)
    probe[..., :dim // 2] = 1.0
    rotated = np.array(Q.rope(mx.array(probe), mx.arange(total)[None], args))[0, :, 0]
    cos_p, sin_p = rotated[:, :dim // 2], rotated[:, dim // 2:dim]
    cfg = R.Config(**ckpt.config["text_config"])
    rot = R.M.Qwen4ExpTextRotaryEmbedding(cfg)
    pos = torch.arange(total).view(1, 1, -1).expand(3, 1, -1)
    cos_r, sin_r = rot(torch.zeros(1, dtype=torch.float32), pos)
    cos_r, sin_r = cos_r[0, :, :dim // 2].numpy(), sin_r[0, :, :dim // 2].numpy()
    inv_ref = rot.inv_freq.numpy()
    inv_port = np.array(args.rope_parameters["rope_theta"] ** (-mx.arange(0, dim, 2) / dim))
    exact = np.cos(np.arange(total)[:, None] * inv_ref.astype(np.float64)[None])
    return dict(rotary_dim=dim, inv_freq_max_abs=float(np.abs(inv_port - inv_ref).max()),
                inv_freq_ulps_differing=int((inv_port != inv_ref).sum()),
                cos_max_abs=float(np.abs(cos_p - cos_r).max()), sin_max_abs=float(np.abs(sin_p - sin_r).max()),
                port_cos_vs_fp64_max_abs=float(np.abs(cos_p - exact).max()),
                ref_cos_vs_fp64_max_abs=float(np.abs(cos_r - exact).max()))


def official_block_scores(R, ref, x, a):
    """Per-query, per-block official indexer scores [T, blocks], computed with the
    official modules in the run dtype exactly as Qwen4ExpTextQSAIndexer.forward
    does for one query (q_layernorm + rope, block mean in fp32 cast back,
    k_layernorm + rope at block starts, fp32 dot, relu, sum over heads, / sqrt d).
    Unpadded input: the blocks of every query are the same global blocks."""
    torch, M = R.torch, R.M
    ind = ref.real.self_attn.indexer
    total = x.shape[1]
    r = a.indexer_compress_ratio
    with torch.inference_mode():
        pos = torch.arange(total).view(1, 1, -1).expand(3, 1, -1)
        cos, sin = ref.tm.rotary_emb(x, pos)
        qk = ind.index_qk_proj(x)
        q, kraw = torch.split(qk, [a.indexer_n_heads * a.indexer_head_dim, a.indexer_head_dim], dim=-1)
        q = M.apply_rotary_pos_emb(ind.q_layernorm(q.reshape(1, total, -1, a.indexer_head_dim)),
                                   cos=cos, sin=sin, unsqueeze_dim=2)[0]
        nb = total // r
        starts = torch.arange(nb) * r
        pooled = kraw[0, :nb * r].reshape(nb, r, -1).float().mean(1).to(kraw.dtype)
        bk = M.apply_rotary_pos_emb(ind.k_layernorm(pooled).unsqueeze(1), cos=cos[0].index_select(0, starts),
                                    sin=sin[0].index_select(0, starts)).squeeze(1)
        return (torch.relu(torch.einsum("thd,nd->tnh", q.float(), bk.float())).sum(-1)
                / a.indexer_head_dim ** 0.5).numpy()


def classify_selection_rows(sel_a, sel_b, scores, a, sparse_from):
    """A differing row is tie-explained iff every block chosen by only one side
    has exactly the top-k boundary score and the query-local tails agree."""
    r, kmax = a.indexer_compress_ratio, a.indexer_budget // a.indexer_compress_ratio
    rows = np.where((sel_a != sel_b).any(axis=1))[0]
    out = dict(rows_differing=int(len(rows)), tie_explained=0, not_tie_explained=[],
               boundary_score_values=[], examples=[])
    boundary_values = set()
    for qi in rows:
        vis = (qi + 1) // r
        ba = {int(t) // r for t in np.where(sel_a[qi, :vis * r])[0]}
        bb = {int(t) // r for t in np.where(sel_b[qi, :vis * r])[0]}
        diff = sorted(ba ^ bb)
        kth = float(np.sort(scores[qi, :vis])[::-1][kmax - 1]) if vis > kmax else None
        tails = bool((sel_a[qi, vis * r:] == sel_b[qi, vis * r:]).all())
        ok = qi >= sparse_from and kth is not None and tails and all(scores[qi, b] == kth for b in diff)
        if ok:
            out["tie_explained"] += 1
            boundary_values.add(kth)
        else:
            out["not_tie_explained"].append(dict(query=int(qi), blocks=diff, scores=[float(scores[qi, b]) for b in diff],
                                                 kth=kth, tails_equal=tails))
        if len(out["examples"]) < 5:
            out["examples"].append(dict(query=int(qi), only_first=sorted(ba - bb), only_second=sorted(bb - ba),
                                        their_scores=[float(scores[qi, b]) for b in diff], kth=kth))
    out["boundary_score_values"] = sorted(boundary_values)
    zero = [int((scores[q, :(q + 1) // r] == 0).sum()) for q in range(sparse_from, scores.shape[0])]
    out["zero_score_blocks_per_sparse_query"] = dict(min=min(zero), max=max(zero), mean=round(float(np.mean(zero)), 2))
    return out


def diagnose_indexer(args, ckpt, guard, R, P):
    """Root-cause evidence for QSA selection mismatches (layer 3, fp32, prefill).

    Recomputes the official indexer's per-block scores exactly as the reference
    does (official modules and apply_rotary_pos_emb, fp32), runs the official
    indexer and the port indexer on the same attention input as the long test,
    and for every query whose selected key set differs reports the scores of
    the blocks only one side selected and the top-k boundary scores.
    """
    torch, mx, M = R.torch, P.mx, R.M
    total, layer = args.long_tokens, 3
    ids = np.random.default_rng(424242).integers(0, EOS, size=total)
    emb = ckpt.rows("model.language_model.embed_tokens.weight", ids.tolist()).float()
    reader = ExpertReader(ckpt, layer)
    guard.check("diagnose: build fp32 attention-only layers")
    ref = RefLayer(R, ckpt, layer, "fp32", reader, attn_only=True)
    port = PortLayer(P, ckpt, layer, "fp32", reader, attn_only=True)
    a = port.args
    r, kmax = a.indexer_compress_ratio, a.indexer_budget // a.indexer_compress_ratio
    ind = ref.real.self_attn.indexer
    with torch.inference_mode():
        x = ref.real.attn_hyper_connection(emb.repeat(1, ref.cfg.hc_count).unsqueeze(0))[0]
        pos = torch.arange(total).view(1, 1, -1).expand(3, 1, -1)
        cos, sin = ref.tm.rotary_emb(x, pos)
        mask = torch.full((total, total), torch.finfo(torch.float32).min).triu(1)[None, None]
        guard.check("diagnose: official indexer")
        sel_ref = (ind(x, (cos, sin), mask, None) == 0)[0, 0].numpy()
    scores = official_block_scores(R, ref, x, a)
    guard.check("diagnose: port indexer")
    xm = mx.array(x.numpy())
    raw = port.dl.self_attn.inner.indexer.inner(xm, mx.arange(total)[None], mx.ones((1, total), dtype=mx.bool_), None)
    mx.eval(raw)
    sel_port = selected_matrix_port([(np.array(raw[0]), np.array(raw[1]))], [total], total)
    sparse_from = (kmax + 1) * r - 1
    rows = np.where((sel_ref != sel_port).any(axis=1))[0]
    report = dict(tokens=total, sparse_from_query=sparse_from, rows_differing=int(len(rows)),
                  sparse_rows=int(total - sparse_from), rows=[])
    zero_counts = []
    for qi in range(sparse_from, total):
        vis = (qi + 1) // r
        zero_counts.append(int((scores[qi, :vis] == 0).sum()))
    report["zero_score_blocks_per_sparse_query"] = dict(min=min(zero_counts), max=max(zero_counts),
                                                       mean=float(np.mean(zero_counts)))
    for qi in rows:
        vis = (qi + 1) // r
        blocks_ref = sorted({int(t) // r for t in np.where(sel_ref[qi, :vis * r])[0]})
        blocks_port = sorted({int(t) // r for t in np.where(sel_port[qi, :vis * r])[0]})
        only_ref = sorted(set(blocks_ref) - set(blocks_port))
        only_port = sorted(set(blocks_port) - set(blocks_ref))
        srt = np.sort(scores[qi, :vis])[::-1]
        report["rows"].append(dict(
            query=int(qi), visible_blocks=int(vis), kept=len(blocks_ref),
            boundary_scores=[float(srt[kmax - 1]), float(srt[kmax])] if vis > kmax else None,
            zero_score_blocks=int((scores[qi, :vis] == 0).sum()),
            ref_only_blocks=only_ref, ref_only_scores=[float(scores[qi, b]) for b in only_ref],
            port_only_blocks=only_port, port_only_scores=[float(scores[qi, b]) for b in only_port],
            tail_equal=bool((sel_ref[qi, vis * r:] == sel_port[qi, vis * r:]).all())))
    return report


def bf16_op_microtest():
    """Relative error vs fp64 of single bf16 ops, MLX vs torch CPU (same bf16 inputs)."""
    import torch
    import torch.nn.functional as F
    import mlx.core as mx
    import mlx.nn as nn
    from mlx_lm.models.activations import swiglu
    rng = np.random.default_rng(0)

    def bf(a):
        return torch.from_numpy(a.astype(np.float32)).to(torch.bfloat16)

    def tomx(t):
        return mx.array(bf16_bits(t)).view(mx.bfloat16)

    def err(a, truth):
        a = np.asarray(a, np.float64)
        return float(np.linalg.norm(a - truth) / np.linalg.norm(truth))

    def mxf(a):
        return np.array(a.astype(mx.float32))
    x, u = bf(rng.standard_normal((4096, 640)) * 2), bf(rng.standard_normal((4096, 640)))
    xd, ud = x.double().numpy(), u.double().numpy()
    sig = 1 / (1 + np.exp(-xd))
    s = bf(rng.standard_normal((512, 4, 2560)))
    a, w = bf(rng.standard_normal((64, 10240))), bf(rng.standard_normal((320, 10240)) * 0.01)
    rows = {
        "sigmoid": (err(torch.sigmoid(x).float(), sig), err(mxf(mx.sigmoid(tomx(x))), sig)),
        "silu": (err(F.silu(x).float(), xd * sig), err(mxf(nn.silu(tomx(x))), xd * sig)),
        "silu(g)*u": (err((F.silu(x) * u).float(), xd * sig * ud), err(mxf(swiglu(tomx(x), tomx(u))), xd * sig * ud)),
        "mean over 4 streams": (err(s.mean(1).float(), s.double().numpy().mean(1)),
                                err(mxf(tomx(s).mean(axis=1)), s.double().numpy().mean(1))),
        "matmul K=10240": (err(F.linear(a, w).float(), a.double().numpy() @ w.double().numpy().T),
                           err(mxf(tomx(a) @ tomx(w).T), a.double().numpy() @ w.double().numpy().T)),
    }
    return {k: dict(torch=v[0], mlx=v[1], ratio=v[1] / v[0]) for k, v in rows.items()}


TENSOR_ORDER = ("attn_hc_mixed", "attn_hc_inject", "attn_out", "mid_stream", "mlp_hc_mixed", "mlp_hc_inject",
                "router_logits", "moe_out", "layer_out")


def summarize(paths):
    """Markdown tables (worst case over all inputs) from one or more result files."""
    lines = []
    for path in paths:
        r = json.loads(Path(path).read_text())
        m = r["meta"]
        lines.append(f"### Layer {m['layer']} ({m['layer_type']})\n")
        lines.append("| dtype | mode | tensor | max abs | max rel | max (1 - cos) |")
        lines.append("|---|---|---|---|---|---|")
        for dtype in m["dtypes"]:
            for mode in ("prefill", "step"):
                cases = [c for c in r["cases"] if c["dtype"] == dtype and c["mode"] == mode]
                if not cases:
                    continue
                for name in TENSOR_ORDER:
                    vals = [c["tensors"][name] for c in cases if name in c["tensors"]]
                    if vals:
                        lines.append(f"| {dtype} | {mode} | {name} | {max(v['max_abs'] for v in vals):.2e} | "
                                     f"{max(v['max_rel'] for v in vals):.2e} | {max(1 - v['cos'] for v in vals):.1e} |")
                agree = sum(c["experts"]["agree"] for c in cases)
                total = sum(c["experts"]["tokens"] for c in cases)
                lines.append(f"| {dtype} | {mode} | expert sets (exact, per token) | {agree}/{total} | | |")
        lines.append("")
        idx = [c["indexer"] for c in r["cases"] if c.get("indexer")]
        if idx:
            lines.append(f"Short-prompt indexer: official selection == causal on {sum(i['ref_selection_equals_causal'] for i in idx)}"
                         f"/{len(idx)} runs; port dense shortcut on {sum(i['port_dense_shortcut_every_call'] for i in idx)}/{len(idx)}.\n")
        if r["cross_dtype"]:
            lines.append("| bf16 vs fp32 reference (truth) | port bf16 max rel | ref bf16 max rel | worst ratio max abs | worst ratio rel L2 |")
            lines.append("|---|---|---|---|---|")
            for name in ("attn_hc_mixed", "attn_out", "mlp_hc_mixed", "router_logits", "moe_out", "layer_out"):
                rows = [x["tensors"][name] for x in r["cross_dtype"]]
                lines.append(f"| {name} | {max(x['port_bf16_vs_ref_fp32']['max_rel'] for x in rows):.2e} | "
                             f"{max(x['ref_bf16_vs_ref_fp32']['max_rel'] for x in rows):.2e} | "
                             f"{max(x['ratio_max_abs'] for x in rows):.2f} | {max(x['ratio_rel_l2'] for x in rows):.2f} |")
            e = [x["expert_sets_vs_fp32_truth"] for x in r["cross_dtype"]]
            lines.append(f"| expert sets equal to fp32 truth | port {sum(x['port_bf16'] for x in e)}/{sum(x['tokens'] for x in e)} | "
                         f"ref {sum(x['ref_bf16'] for x in e)}/{sum(x['tokens'] for x in e)} | | |\n")
        cons = [x["consensus_tokens"] for x in r["cross_dtype"] if x.get("consensus_tokens", {}).get("tensors")]
        if cons:
            lines.append(f"Consensus tokens (bf16 port, bf16 ref and fp32 truth route identically): "
                         f"{sum(c['count'] for c in cons)}/{sum(c['tokens'] for c in cons)}\n")
            lines.append("| consensus tokens, vs fp32 truth | port bf16 rel L2 | ref bf16 rel L2 | worst ratio rel L2 | port bf16 max abs | ref bf16 max abs |")
            lines.append("|---|---|---|---|---|---|")
            for name in ("attn_out", "router_logits", "moe_out", "layer_out"):
                rows = [c["tensors"][name] for c in cons]
                lines.append(f"| {name} | {max(x['port_bf16_vs_ref_fp32']['rel_l2'] for x in rows):.2e} | "
                             f"{max(x['ref_bf16_vs_ref_fp32']['rel_l2'] for x in rows):.2e} | "
                             f"{max(x['ratio_rel_l2'] for x in rows):.2f} | "
                             f"{max(x['port_bf16_vs_ref_fp32']['max_abs'] for x in rows):.2e} | "
                             f"{max(x['ref_bf16_vs_ref_fp32']['max_abs'] for x in rows):.2e} |")
            lines.append("")
        flips = [f for x in r["cross_dtype"] for f in x.get("bf16_flips", [])]
        if flips:
            lines.append(f"bf16 expert-set differences between port and reference: {len(flips)} token-mode pairs; "
                         f"near-ties in the fp32 truth: {sum(f['near_tie'] for f in flips)}/{len(flips)}; swapped experts' "
                         f"fp32 ranks {sorted({v for f in flips for v in f['fp32_ranks'].values()})}; max fp32 distance to "
                         f"boundary {max(d for f in flips for d in f['fp32_dist_to_boundary'].values()):.3g} vs bf16 logit "
                         f"error up to {max(f['bf16_logit_err'] for f in flips):.3g}.\n")
        agreeing = [c for c in r["cases"] if c.get("tensors_agreeing_tokens")]
        if agreeing:
            lines.append("| bf16 cases with expert flips: agreeing tokens only | mode | moe_out max rel | layer_out max rel | layer_out 1 - cos |")
            lines.append("|---|---|---|---|---|")
            for c in agreeing:
                t = c["tensors_agreeing_tokens"]
                lines.append(f"| {c['input']} ({c['experts']['agree']}/{c['tokens']} tokens) | {c['mode']} | "
                             f"{t['moe_out']['max_rel']:.2e} | {t['layer_out']['max_rel']:.2e} | {1 - t['layer_out']['cos']:.1e} |")
            lines.append("")
        if r.get("quant"):
            q = r["quant"]
            lines.append(f"| q{q[0]['bits']} routed experts (group {q[0]['group_size']}) | mode | rel L2 vs bf16 | max rel vs bf16 | "
                         "1 - cos vs bf16 | rel L2 vs fp32 truth (q) | rel L2 vs fp32 truth (bf16) |")
            lines.append("|---|---|---|---|---|---|---|")
            for name in ("moe_out", "layer_out"):
                for mode in ("prefill", "step"):
                    rows = [x[name] for x in q if x["mode"] == mode]
                    lines.append(f"| {name} | {mode} | {max(x['q_vs_bf16']['rel_l2'] for x in rows):.2e} | "
                                 f"{max(x['q_vs_bf16']['max_rel'] for x in rows):.2e} | "
                                 f"{max(1 - x['q_vs_bf16']['cos'] for x in rows):.1e} | "
                                 f"{max(x['q_vs_fp32_truth']['rel_l2'] for x in rows):.2e} | "
                                 f"{max(x['bf16_vs_fp32_truth']['rel_l2'] for x in rows):.2e} |")
            lines.append(f"Routing unchanged by expert quantization: {all(x['experts_equal_to_bf16'] for x in q)}; "
                         f"attention output bit-identical: {all(x['attn_out_identical_to_bf16'] for x in q)}.\n")
        lines.append("| self-consistency (stepwise vs prefill, layer out) | dtype | max abs | max rel | expert sets equal |")
        lines.append("|---|---|---|---|---|")
        for side in ("port", "ref"):
            for dtype in m["dtypes"]:
                rows = [x for x in r["self"] if x["side"] == side and x["dtype"] == dtype]
                if rows:
                    lines.append(f"| {side} | {dtype} | {max(x['layer_out']['max_abs'] for x in rows):.2e} | "
                                 f"{max(x['layer_out']['max_rel'] for x in rows):.2e} | {all(x['experts_equal'] for x in rows)} |")
        lines.append("")
        lq = r.get("long_qsa")
        if lq:
            lines.append(f"Long sparse-QSA test: T={lq['tokens']}, budget {lq['budget']}, ratio {lq['compress_ratio']}; "
                         f"queries >= {lq['sparse_from_query']} drop blocks.\n")
            lines.append("| dtype | comparison | rows | max abs | max rel | 1 - cos | selection rows differing |")
            lines.append("|---|---|---|---|---|---|---|")
            for dtype, res in lq["runs"].items():
                for key, val in res.items():
                    if isinstance(val, dict) and "all" in val:
                        for rows in ("dense_queries", "sparse_queries"):
                            v = val[rows]
                            lines.append(f"| {dtype} | {key} | {rows} | {v['max_abs']:.2e} | {v['max_rel']:.2e} | "
                                         f"{1 - v['cos']:.1e} | {res['selection'].get(key, {}).get('rows_differing', 'forced equal')} |")
            lines.append("")
            for dtype, res in lq["runs"].items():
                sel = res["selection"]
                lines.append(f"- {dtype}: official dense rows == causal: {sel['ref_dense_rows_equal_causal']}; "
                             f"sparse rows proper subsets: {sel['ref_sparse_rows_proper_subset']}; "
                             f"selected keys per sparse query: {sel['ref_selected_per_sparse_query']}; timing {res['timing_s']}")
                for name in ("tie_analysis_port_prefill_vs_ref_prefill", "tie_analysis_port_step_vs_ref_step"):
                    t = sel[name]
                    lines.append(f"  - {name}: {t['rows_differing']} rows differ, {t['tie_explained']} explained by exact "
                                 f"ties at the top-k boundary (boundary scores {t['boundary_score_values']}), "
                                 f"not explained: {len(t['not_tie_explained'])}; zero-score blocks per sparse query "
                                 f"{t['zero_score_blocks_per_sparse_query']}")
            if "cross_dtype" in lq:
                c = lq["cross_dtype"]
                lines.append(f"- bf16 vs fp32 reference prefill: port max rel {c['port_bf16_vs_ref_fp32']['max_rel']:.2e} "
                             f"(1-cos {1 - c['port_bf16_vs_ref_fp32']['cos']:.1e}), reference max rel "
                             f"{c['ref_bf16_vs_ref_fp32']['max_rel']:.2e} (1-cos {1 - c['ref_bf16_vs_ref_fp32']['cos']:.1e})")
            lines.append(f"- RoPE tables (fp32, positions 0..{lq['tokens'] - 1}): {json.dumps(lq['rope_tables'])}")
            lines.append("")
        lines.append(f"Run: {m['seconds']} s; peak phys_footprint {m['peak_footprint_gb']} GB (peak RSS "
                     f"{m['peak_rss_gb']} GB, MLX peak {m['mlx_peak_gb']} GB); checkpoint bytes read "
                     f"{m['checkpoint_bytes_read_gb']} GB; min memory_pressure free {min(e['free_pct'] for e in m['guard'])}%; "
                     f"expert reads {json.dumps(r['reader'])}.\n")
    return "\n".join(lines)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--bf16-op-microtest":
        print(json.dumps(bf16_op_microtest(), indent=1))
        return
    if len(sys.argv) > 1 and sys.argv[1] == "--summarize":
        print(summarize(sys.argv[2:]))
        return
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--weights", type=Path, default=Path("/private/tmp/jwflash-weights"))
    p.add_argument("--layer", type=int, choices=(2, 3), required=True)
    p.add_argument("--dtypes", default="fp32,bf16")
    p.add_argument("--inputs", default="all", help="comma list of input names, or all")
    p.add_argument("--long-tokens", type=int, default=2304, help="layer 3 sparse-QSA test length; 0 disables")
    p.add_argument("--limit-gb", type=float, default=6.0)
    p.add_argument("--min-free-pct", type=int, default=20)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--expert-bits", type=int, default=6, help="routed-expert bits for the quantized "
                   "(experts only, group 64, everything else bf16) comparison; 0 disables")
    p.add_argument("--diagnose-indexer", action="store_true",
                   help="only run the layer 3 QSA selection root-cause diagnostic (fp32)")
    args = p.parse_args()
    args.dtypes = args.dtypes.split(",")
    if "restricted" in Path(args.weights).resolve().parts:
        raise SystemExit("restricted paths are not inputs")
    if os.environ.get("OMP_NUM_THREADS") != "2":
        raise SystemExit("run with OMP_NUM_THREADS=2 (and nice -n 10)")
    guard = Guard(args.limit_gb, args.min_free_pct)
    guard.check("start")
    started = time.time()
    R = reference_modules()
    R.torch.set_num_threads(2)
    R.torch.manual_seed(0)
    P = port_modules()
    P.mx.set_cache_limit(256 * 2**20)
    ckpt = Checkpoint(args.weights)
    tc = ckpt.config["text_config"]
    if args.diagnose_indexer:
        report = diagnose_indexer(args, ckpt, guard, R, P)
        guard.check("end")
        report["peak_footprint_gb"] = round(guard.peak_fp / 2**30, 3)
        args.out.write_text(json.dumps(report, indent=1, default=float) + "\n")
        print(json.dumps({k: v for k, v in report.items() if k != "rows"}))
        for row in report["rows"][:20]:
            print(json.dumps(row))
        return
    sets, scale = build_inputs(ckpt, tc["hc_count"], tc["hidden_size"])
    if args.inputs != "all":
        keep = set(args.inputs.split(","))
        sets = [s for s in sets if s["name"] in keep]
    import mlx.core as mx
    import torch
    import transformers
    import mlx_lm
    results = dict(meta=dict(layer=args.layer, layer_type=tc["layer_types"][args.layer], dtypes=args.dtypes,
                             versions=dict(torch=torch.__version__, transformers=transformers.__version__,
                                           mlx=mx.__version__, mlx_lm=mlx_lm.__version__, numpy=np.__version__),
                             port_file=str(PORT_FILE.relative_to(ROOT)),
                             port_sha256=__import__("hashlib").sha256(PORT_FILE.read_bytes()).hexdigest(),
                             weights=str(args.weights), random_scale=scale,
                             inputs=[dict(name=s["name"], kind=s["kind"], ids=s.get("ids"), seed=s.get("seed"),
                                          tokens=int(s["stream"].shape[1])) for s in sets],
                             tokenizer="official tokenizer.json not available offline: fixed token ids"),
                   cases=[], self=[], cross_dtype=[], reader={}, quant=[])
    store = {}
    for dtype_name in args.dtypes:
        run_layer_cases(args, ckpt, guard, args.layer, dtype_name, sets, R, P, results, store)
    cross_dtype(results, store, args.layer, sets)
    if args.expert_bits:
        run_quant_cases(args, ckpt, guard, args.layer, sets, P, results, store)
    store.clear()
    if args.layer == 3 and args.long_tokens:
        long_qsa(args, ckpt, guard, R, P, results)
    guard.check("end")
    results["meta"].update(seconds=round(time.time() - started, 1), guard=guard.events,
                           peak_footprint_gb=round(guard.peak_fp / 2**30, 3),
                           peak_rss_gb=round(guard.peak_rss() / 2**30, 3),
                           mlx_peak_gb=round(mx.get_peak_memory() / 2**30, 3),
                           checkpoint_bytes_read_gb=round(ckpt.bytes_read / 2**30, 3))
    args.out.write_text(json.dumps(results, indent=1, default=float) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
