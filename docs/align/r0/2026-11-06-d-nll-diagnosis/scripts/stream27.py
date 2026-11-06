"""Layer-streamed teacher-forced NLL of Qwen/Qwen3.8-27B on the pinned R0 SHADE ids, with
weights range-read from the HF hub into RAM one decoder layer at a time (no disk copy).

Variants, run side by side on identical inputs, one layer at a time:
  hf32  : transformers 5.22.1 Qwen3_5DecoderLayer, float32 weights + activations (torch, MPS or CPU)
  mlx16 : mlx_lm 0.31.3 qwen3_5 DecoderLayer, upstream bf16 weights sanitized as mlx_lm would
  mlxq8 : same, then nn.quantize(group_size=64, bits=8, affine) -- the recipe of the D artifact
  mlxD  : (optional, --with-d) the actual D artifact tensors (mlx-community/Qwen3.8-27B-8bit @ 815b83c0)
Per layer it prints the relative hidden-state difference of each MLX variant vs hf32 by region;
at the end the NLL per variant (mean, 256-token bins, tail-from-900 by prefix start).
usage: stream27.py IDS_JSON CONFIG_JSON OUT_JSON [--starts 0,100,900] [--device mps] [--with-d] [--layers N]
"""
import argparse, json, os, sys, time, struct, subprocess, threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("ids"); ap.add_argument("config"); ap.add_argument("out")
ap.add_argument("--starts", default="0,100,900"); ap.add_argument("--device", default="mps")
ap.add_argument("--with-d", action="store_true"); ap.add_argument("--layers", type=int, default=None)
ap.add_argument("--threads", type=int, default=8); ap.add_argument("--nothink", action="store_true")
ap.add_argument("--repo", default="Qwen/Qwen3.8-27B"); ap.add_argument("--rev", default="8c0b3d30f3ae96f5c7f774de704bf0ada83e422a")
a = ap.parse_args()

import torch
import mlx.core as mx
import mlx.nn as mnn
from transformers.models.qwen3_5.configuration_qwen3_5 import Qwen3_5TextConfig
from transformers.models.qwen3_5 import modeling_qwen3_5 as hfm
from mlx_lm.models import qwen3_5 as mlm

U = (a.repo, a.rev)
D = ("mlx-community/Qwen3.8-27B-8bit", "815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9")
HDR = "/private/tmp/jwd8diag/hdr"; os.makedirs(HDR, exist_ok=True)

def curl(url, s, e):
    for attempt in range(5):
        r = subprocess.run(["curl", "-sfL", "--retry", "3", "-r", f"{s}-{e}", url], capture_output=True)
        if r.returncode == 0 and len(r.stdout) == e - s + 1:
            return r.stdout
        time.sleep(2 + attempt * 3)
    raise RuntimeError(f"range read failed {url} {s}-{e}")

def index(repo, rev):
    r = subprocess.run(["curl", "-sfL", f"https://huggingface.co/{repo}/resolve/{rev}/model.safetensors.index.json"],
                       capture_output=True, check=True)
    return json.loads(r.stdout)["weight_map"]

_hlock = threading.Lock(); _hcache = {}
def header(repo, rev, fname):
    key = (repo, fname)
    with _hlock:
        if key in _hcache: return _hcache[key]
    p = os.path.join(HDR, f"{repo.replace('/', '__')}__{rev[:8]}__{fname}.hdr.json")
    url = f"https://huggingface.co/{repo}/resolve/{rev}/{fname}"
    if os.path.exists(p):
        h, n = json.load(open(p))
    else:
        n = struct.unpack("<Q", curl(url, 0, 7))[0]
        h = json.loads(curl(url, 8, 8 + n - 1)); json.dump([h, n], open(p, "w"))
    with _hlock: _hcache[key] = (h, n, url)
    return h, n, url

NP = {"BF16": np.uint16, "F32": np.float32, "F16": np.float16, "U32": np.uint32}
def fetch(repo, rev, wmap, key):
    h, n, url = header(repo, rev, wmap[key]); m = h[key]; s, e = m["data_offsets"]
    CH = 64 << 20  # split big tensors into 64 MB ranges
    CH = 32 << 20
    buf = np.empty(e - s, dtype=np.uint8)
    def put(o):
        buf[o - s:min(e, o + CH) - s] = np.frombuffer(curl(url, 8 + n + o, 8 + n + min(e, o + CH) - 1), dtype=np.uint8)
    for f in [chunk_pool.submit(put, o) for o in range(s, e, CH)]: f.result()
    return buf.view(NP[m["dtype"]]).reshape(m["shape"]), m["dtype"]

pool = ThreadPoolExecutor(a.threads)
chunk_pool = ThreadPoolExecutor(12)
def fetch_many(repo, rev, wmap, keys):
    futs = {k: pool.submit(fetch, repo, rev, wmap, k) for k in keys}
    return {k: f.result() for k, f in futs.items()}

def bf16_to_f32(u16):
    return (u16.astype(np.uint32) << 16).view(np.float32)

def to_mx(arr, dt):
    if dt == "BF16": return mx.array(arr.view(np.uint16)).view(mx.bfloat16)
    return mx.array(arr)

def to_torch32(arr, dt):
    return torch.from_numpy(bf16_to_f32(arr) if dt == "BF16" else arr.astype(np.float32))

# ---------------------------------------------------------------- setup
ids = json.load(open(a.ids)); starts = [int(s) for s in a.starts.split(",")]
seqs = {s: ids[s:] for s in starts}  # inputs seq[:-1], targets seq[1:]
SH = {s: s for s in starts}
if a.nothink:  # ablation (a): native template with enable_thinking=False == pinned ids minus the 38 reasoning tokens 3..40
    seqs["nothink"] = ids[:3] + ids[41:]; SH["nothink"] = 38
tc = json.load(open(a.config))["text_config"]
import copy
hcfg = Qwen3_5TextConfig(**copy.deepcopy(tc)); hcfg._attn_implementation = "sdpa"
margs = mlm.TextModelArgs.from_dict(copy.deepcopy(tc))
NL = a.layers or tc["num_hidden_layers"]
dev = torch.device(a.device)
ui = index(*U); di = index(*D) if a.with_d else None
UP = "model.language_model."; DP = "language_model."
variants = ["hf32", "mlx16", "mlxq8"] + (["mlxD"] if a.with_d else [])
t0 = time.time()
mx.set_cache_limit(256 << 20)
def memstr():
    fp = subprocess.run(["ps", "-o", "rss=", "-p", str(os.getpid())], capture_output=True, text=True).stdout.strip()
    tm = torch.mps.driver_allocated_memory() >> 20 if dev.type == "mps" else 0
    return f"rss={int(fp)>>10}MB mlx_active={mx.get_active_memory()>>20}MB mlx_cache={mx.get_cache_memory()>>20}MB mlx_peak={mx.get_peak_memory()>>20}MB torch_mps={tm}MB"
def log(*x): print(f"[{time.time()-t0:7.1f}s]", *x, memstr(), flush=True)

# embeddings: fetch the full table once, gather the rows we need, free it
emb, edt = fetch(*U, ui, UP + "embed_tokens.weight")
log("embed fetched", emb.shape, edt)
H = {}
for s, seq in seqs.items():
    rows = emb[np.array(seq[:-1])]
    e16 = to_mx(rows, edt)
    eq = mx.dequantize(*mx.quantize(e16, group_size=64, bits=8), group_size=64, bits=8).astype(mx.bfloat16)
    H[s] = {"hf32": torch.from_numpy(bf16_to_f32(rows))[None].to(dev), "mlx16": e16[None], "mlxq8": eq[None]}
if not tc.get("tie_word_embeddings"): del emb
if a.with_d:
    dw = fetch_many(*D, di, [DP + "model.embed_tokens." + x for x in ("weight", "scales", "biases")])
    for s, seq in seqs.items():
        sel = np.array(seq[:-1])
        w, s_, b = (to_mx(dw[DP + "model.embed_tokens." + x][0][sel], dw[DP + "model.embed_tokens." + x][1]) for x in ("weight", "scales", "biases"))
        H[s]["mlxD"] = mx.dequantize(w, s_, b, group_size=64, bits=8)[None].astype(mx.bfloat16)
    del dw
for s in H: mx.eval(*[v for k, v in H[s].items() if k != "hf32"])
log("embeddings ready")

rot = hfm.Qwen3_5TextRotaryEmbedding(hcfg).to(dev)
pe = {}
for s, seq in seqs.items():
    L = len(seq) - 1
    pos = torch.arange(L, device=dev).view(1, 1, -1).expand(3, 1, -1)
    pe[s] = rot(H[s]["hf32"], pos)

SHIFT = (".input_layernorm.weight", ".post_attention_layernorm.weight", ".q_norm.weight", ".k_norm.weight")
def layer_keys(wmap, prefix, i):
    p = f"{prefix}layers.{i}."; return [k for k in wmap if k.startswith(p)]

def regions(L, s):
    # absolute token regions of the original sequence: [0,40) [40,100) [100,900) [900,end)
    out = {}
    for name, lo, hi in (("0-40", 0, 40), ("40-100", 40, 100), ("100-900", 100, 900), ("900-", 900, 10**9)):
        lo2, hi2 = max(lo - s, 0), min(hi - s, L)
        if hi2 > lo2: out[name] = (lo2, hi2)
    return out

def mlx_layer(i, tensors, quant):
    layer = mlm.DecoderLayer(margs, i)
    ws = []
    for k, (arr, dt) in tensors.items():
        name = k.split(f"layers.{i}.", 1)[1]
        v = to_mx(arr, dt)
        if "conv1d.weight" in name and v.shape[-1] != 1: v = v.moveaxis(2, 1)
        if any(("." + name).endswith(sfx) for sfx in SHIFT) and v.ndim == 1: v = v + 1.0
        if not name.endswith("A_log") and v.dtype == mx.float32: v = v.astype(mx.bfloat16)
        ws.append((name, v))
    layer.load_weights(ws, strict=True)
    if quant: mnn.quantize(layer, group_size=64, bits=8)
    mx.eval(layer.parameters()); return layer

def mlx_layer_D(i, tensors):
    layer = mlm.DecoderLayer(margs, i)
    mnn.quantize(layer, group_size=64, bits=8)
    ws = [(k.split(f"layers.{i}.", 1)[1], to_mx(arr, dt)) for k, (arr, dt) in tensors.items()]
    layer.load_weights(ws, strict=True); mx.eval(layer.parameters()); return layer

def hf_layer(i, tensors):
    with torch.device("meta"):
        layer = hfm.Qwen3_5DecoderLayer(hcfg, i)
    sd = {k.split(f"layers.{i}.", 1)[1]: to_torch32(arr, dt).to(dev) for k, (arr, dt) in tensors.items()}
    layer.load_state_dict(sd, strict=True, assign=True); del sd
    return layer.to(dev).float().eval()

per_layer = []
nxt = pool.submit(lambda: fetch_many(*U, ui, layer_keys(ui, UP, 0)))
nxtD = pool.submit(lambda: fetch_many(*D, di, layer_keys(di, DP + "model.", 0))) if a.with_d else None
for i in range(NL):
    ut = nxt.result(); dt_ = nxtD.result() if nxtD else None
    if i + 1 < NL:
        nxt = pool.submit(lambda j=i + 1: fetch_many(*U, ui, layer_keys(ui, UP, j)))
        if a.with_d: nxtD = pool.submit(lambda j=i + 1: fetch_many(*D, di, layer_keys(di, DP + "model.", j)))
    is_lin = tc["layer_types"][i] == "linear_attention"
    mask = None if is_lin else "causal"
    row = {"layer": i, "type": "lin" if is_lin else "attn"}
    # one variant at a time to bound peak memory
    hl = hf_layer(i, ut)
    with torch.no_grad():
        for s in seqs: H[s]["hf32"] = hl(H[s]["hf32"], position_embeddings=pe[s], attention_mask=None)
    del hl
    if dev.type == "mps": torch.mps.synchronize(); torch.mps.empty_cache()
    builders = [("mlx16", lambda: mlx_layer(i, ut, False)), ("mlxq8", lambda: mlx_layer(i, ut, True))]
    if a.with_d: builders.append(("mlxD", lambda: mlx_layer_D(i, dt_)))
    for v, build in builders:
        m = build()
        for s in seqs: H[s][v] = m(H[s][v], mask=mask)
        mx.eval(*[H[s][v] for s in seqs]); del m; mx.clear_cache()
    for s in seqs:
        h = H[s]
        ref = h["hf32"][0].float().cpu().numpy(); L = ref.shape[0]
        d = {"hf_rms": round(float(np.sqrt((ref ** 2).mean())), 3)}
        for v in variants[1:]:
            x = np.array(h[v][0].astype(mx.float32))
            d[v] = {rn: round(float(np.linalg.norm(x[lo:hi] - ref[lo:hi]) / (np.linalg.norm(ref[lo:hi]) + 1e-9)), 4)
                    for rn, (lo, hi) in regions(L, SH[s]).items()}
        row[f"s{s}"] = d
    per_layer.append(row); log(json.dumps(row))
    mx.clear_cache()
    del ut, dt_

# ---------------------------------------------------------------- head
fin = fetch_many(*U, ui, [UP + "norm.weight"] + ([] if tc.get("tie_word_embeddings") else ["lm_head.weight"]))
nw, _ = fin[UP + "norm.weight"]; lmw, lmdt = (emb, edt) if tc.get("tie_word_embeddings") else fin["lm_head.weight"]
nw32 = torch.from_numpy(bf16_to_f32(nw)).to(dev)
nw_m = (to_mx(nw, "BF16") + 1.0)
lm16 = lmq = None
if a.with_d:
    dh = fetch_many(*D, di, [DP + "model.norm.weight"] + [DP + "lm_head." + x for x in ("weight", "scales", "biases")])
    nw_D = to_mx(*dh[DP + "model.norm.weight"]); lmD = tuple(to_mx(*dh[DP + "lm_head." + x]) for x in ("weight", "scales", "biases"))
    del dh
del fin
VCH = 32768

def nll_hf(h, tgt):
    x = h[0].float(); x = x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + 1e-6) * (1.0 + nw32)
    lse = None; tl = torch.zeros(x.shape[0], device=dev)
    t = torch.tensor(tgt, device=dev)
    for v0 in range(0, lmw.shape[0], VCH):
        W = torch.from_numpy(bf16_to_f32(lmw[v0:v0 + VCH])).to(dev)
        lg = x @ W.T
        c = torch.logsumexp(lg, -1); lse = c if lse is None else torch.logaddexp(lse, c)
        inr = (t >= v0) & (t < v0 + W.shape[0])
        tl[inr] = lg[inr, (t[inr] - v0)]
    return (lse - tl).cpu().numpy()

def nll_mx(h, w_norm, head):
    x = mx.fast.rms_norm(h[0], w_norm, 1e-6)
    lg = (x @ head.T) if not isinstance(head, tuple) else mx.quantized_matmul(x, *head, transpose=True, group_size=64, bits=8)
    lg = lg.astype(mx.float32)
    return lg

res = {"variants": {}, "per_layer": per_layer}
for v in variants:
    res["variants"][v] = {}
    full = None
    for s, seq in seqs.items():
        tgt = seq[1:]
        if v == "hf32": l = nll_hf(H[s]["hf32"], tgt)
        else:
            if v == "mlx16" and lm16 is None:
                lm16 = to_mx(lmw, lmdt); mx.eval(lm16); del lmw
            if v == "mlxq8" and lmq is None:
                lmq = tuple(mx.quantize(lm16, group_size=64, bits=8)); mx.eval(*lmq); lm16 = None; mx.clear_cache()
            head = lm16 if v == "mlx16" else (lmq if v == "mlxq8" else lmD)
            wn = nw_m if v != "mlxD" else nw_D
            lg = nll_mx(H[s][v], wn, head); t = mx.array(tgt)
            l = mx.logsumexp(lg, -1) - mx.take_along_axis(lg, t[:, None], -1).squeeze(-1); mx.eval(l)
            l = np.array(l); del lg
        tail = l[900 - SH[s] - 1:] if SH[s] < 900 else l
        r = {"mean": round(float(l.mean()), 4), "tail_from_900": round(float(tail.mean()), 4)}
        if s == 0: r["bins256"] = [round(float(l[i:i + 256].mean()), 2) for i in range(0, len(l), 256)]
        if s in (0, "nothink"): r["per_token"] = [round(float(x), 3) for x in l]
        res["variants"][v][f"start_{s}"] = r
    log(v, json.dumps({k: {kk: vv for kk, vv in r.items() if kk != "per_token"} for k, r in res["variants"][v].items()}))
    json.dump(res, open(a.out, "w"))
json.dump(res, open(a.out, "w"), indent=1)
log("done")
