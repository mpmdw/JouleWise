"""BYTES feasibility pilot: load, memory, prefill/decode throughput, bytes-per-token accounting.

No power capture. Usage: bench.py <repo_id> <out_json> [reps]
"""
import gc
import json
import os
import resource
import subprocess
import sys
import time

import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_flatten

from huggingface_hub import snapshot_download
from mlx_lm import load
from mlx_lm.generate import generate_step
from mlx_lm.models.cache import make_prompt_cache
from mlx_lm.sample_utils import make_sampler

PROMPT_TOKENS = 2048
GEN_TOKENS = 512
TEXT_FILES = [
    "/Users/edr/code/JouleWise/README.md",
    "/Users/edr/code/JouleWise/docs/orchestration.md",
    "/Users/edr/code/JouleWise/docs/agent_playbook.md",
]


def rss_now_bytes():
    out = subprocess.run(["ps", "-o", "rss=", "-p", str(os.getpid())], capture_output=True, text=True).stdout
    return int(out.strip()) * 1024


def build_prompt(tokenizer):
    text = ""
    for p in TEXT_FILES:
        try:
            with open(p) as f:
                text += f.read() + "\n\n"
        except OSError:
            pass
    ids = tokenizer.encode(text)
    while len(ids) < PROMPT_TOKENS:
        ids = ids + ids
    return ids[:PROMPT_TOKENS]


def accounting(model, cfg):
    params = dict(tree_flatten(model.parameters()))
    mods = dict(model.named_modules())
    E = cfg.get("num_experts") or cfg.get("num_local_experts") or cfg.get("n_routed_experts")
    k = cfg.get("num_experts_per_tok") or cfg.get("experts_per_token") or cfg.get("num_experts_per_token")
    vocab = cfg.get("vocab_size")
    cats = {}
    bits_seen = {}
    for name, arr in params.items():
        modname, _, leaf = name.rpartition(".")
        m = mods.get(modname)
        stored = arr.nbytes
        logical = arr.size
        qbits = getattr(m, "bits", None) if m is not None else None
        if qbits is not None and leaf == "weight" and arr.dtype == mx.uint32:
            logical = arr.size * 32 // qbits
            mode = getattr(m, "mode", "affine")
            bits_seen[f"{qbits}b/{getattr(m,'group_size',None)}g/{mode}"] = bits_seen.get(f"{qbits}b/{getattr(m,'group_size',None)}g/{mode}", 0) + logical
        elif qbits is not None and leaf in ("scales", "biases"):
            logical = 0
        lname = name.lower()
        if "embed_tokens" in lname or lname.endswith("wte.weight") or ".embed." in lname or "embedding" in lname:
            cat = "embed"
        elif "lm_head" in lname:
            cat = "lm_head"
        elif "switch_mlp" in lname or ".experts." in lname:
            cat = "routed_experts"
        else:
            cat = "always_active"
        c = cats.setdefault(cat, {"logical_params": 0, "stored_bytes": 0})
        c["logical_params"] += logical
        c["stored_bytes"] += stored
    total_params = sum(c["logical_params"] for c in cats.values())
    total_bytes = sum(c["stored_bytes"] for c in cats.values())
    frac = (k / E) if (E and k and "routed_experts" in cats) else None
    ex = cats.get("routed_experts", {"logical_params": 0, "stored_bytes": 0})
    emb = cats.get("embed", {"logical_params": 0, "stored_bytes": 0})
    head = cats.get("lm_head", {"logical_params": 0, "stored_bytes": 0})
    aa = cats.get("always_active", {"logical_params": 0, "stored_bytes": 0})
    f = frac if frac is not None else 1.0
    # active params by the usual convention (embeddings counted, routed experts scaled by k/E)
    active_params = aa["logical_params"] + emb["logical_params"] + head["logical_params"] + ex["logical_params"] * f
    # bytes read per decoded token: all always-active stored bytes (incl. quant scales/biases), one embedding row,
    # the full output projection (separate lm_head, or the tied embedding matrix), and k/E of routed-expert bytes
    tied = "lm_head" not in cats
    emb_row = emb["stored_bytes"] / vocab if vocab else 0
    head_bytes = emb["stored_bytes"] if tied else head["stored_bytes"]
    bytes_read = aa["stored_bytes"] + emb_row + head_bytes + ex["stored_bytes"] * f
    # resident = everything stored
    return {
        "categories": cats,
        "quant_mix_logical_params": bits_seen,
        "num_experts": E,
        "experts_per_tok": k,
        "tied_embeddings": tied,
        "total_params": total_params,
        "active_params": active_params,
        "resident_weight_bytes": total_bytes,
        "bytes_read_per_token_measured": bytes_read,
        "bytes_read_per_token_formula_4bit": active_params * 4 / 8,
    }


def cache_bytes(cache):
    tot = 0
    for c in cache:
        st = getattr(c, "state", None)
        try:
            for a in [x for _, x in tree_flatten(st)]:
                if isinstance(a, mx.array):
                    tot += a.nbytes
        except Exception:
            pass
    return tot


def main():
    repo = sys.argv[1]
    out = sys.argv[2]
    reps = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    res = {"repo": repo, "mlx_version": mx.__version__, "ok": False, "errors": []}
    try:
        import glob; path = repo if repo.startswith("/") else sorted(glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--" + repo.replace("/", "--") + "/snapshots/*")))[-1]
        res["snapshot"] = path
        du = subprocess.run(["du", "-skL", path], capture_output=True, text=True).stdout.split()[0]
        res["on_disk_bytes"] = int(du) * 1024
        with open(os.path.join(path, "config.json")) as f:
            cfg = json.load(f)
        if isinstance(cfg.get("text_config"), dict):
            cfg = {**cfg, **cfg["text_config"]}
        res["config_excerpt"] = {k: cfg.get(k) for k in [
            "model_type", "num_hidden_layers", "hidden_size", "num_attention_heads", "num_key_value_heads",
            "head_dim", "vocab_size", "num_experts", "num_local_experts", "num_experts_per_tok",
            "experts_per_token", "moe_intermediate_size", "intermediate_size", "shared_expert_intermediate_size",
            "full_attention_interval", "sliding_window", "layer_types", "tie_word_embeddings", "quantization"]}
        res["rss_before_load"] = rss_now_bytes()
        mx.reset_peak_memory()
        t0 = time.perf_counter()
        model, tok = load(path)
        mx.eval(model.parameters())
        res["load_s"] = time.perf_counter() - t0
        res["mlx_active_after_load"] = mx.get_active_memory()
        res["rss_after_load"] = rss_now_bytes()
        res["accounting"] = accounting(model, cfg)
        prompt = mx.array(build_prompt(tok))
        sampler = make_sampler(temp=0.0)
        runs = []
        # one short warmup (kernel compile), not counted
        for _ in generate_step(prompt[:64], model, max_tokens=4, sampler=sampler):
            pass
        for r in range(reps):
            gc.collect()
            mx.clear_cache()
            mx.reset_peak_memory()
            cache = make_prompt_cache(model)
            n = 0
            toks = []
            t0 = time.perf_counter()
            t1 = None
            for tkn, _ in generate_step(prompt, model, max_tokens=GEN_TOKENS, sampler=sampler, prompt_cache=cache):
                if n == 0:
                    t1 = time.perf_counter()
                toks.append(int(tkn))
                n += 1
            t2 = time.perf_counter()
            run = {
                "rep": r,
                "prefill_s": t1 - t0,
                "prefill_tps": PROMPT_TOKENS / (t1 - t0),
                "decode_tokens": n - 1,
                "decode_s": t2 - t1,
                "decode_tps": (n - 1) / (t2 - t1),
                "total_s": t2 - t0,
                "mlx_peak_bytes": mx.get_peak_memory(),
                "kv_cache_bytes_end": cache_bytes(cache),
                "distinct_tokens_out": len(set(toks)),
            }
            if r == 0:
                run["output_head"] = tok.decode(toks[:60])
            runs.append(run)
            print(json.dumps({k: v for k, v in run.items() if k != "output_head"}), flush=True)
            del cache
        res["runs"] = runs
        res["peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss  # bytes on macOS
        res["ok"] = True
    except Exception as e:
        import traceback
        res["errors"].append(traceback.format_exc())
    res["peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    with open(out, "w") as f:
        json.dump(res, f, indent=1, default=str)
    print("DONE ok=", res["ok"], flush=True)


if __name__ == "__main__":
    main()
