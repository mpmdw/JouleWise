"""Teacher-forced NLL on the pinned R0 SHADE ids: MLX (mlx_lm) or HF transformers (CPU).
usage: score.py {mlx|hf} MODEL_DIR IDS_JSON [--dtype float32|bfloat16] [--reencode TEXT_FILE]
Prints mean, 256-token bins, and the tail-from-900 prefix sweep (starts 0,1,40,100,300,600,900)."""
import argparse, json, hashlib, math, sys, time
ap = argparse.ArgumentParser()
ap.add_argument("backend"); ap.add_argument("model"); ap.add_argument("ids")
ap.add_argument("--dtype", default="float32"); ap.add_argument("--reencode", default=None)
ap.add_argument("--starts", default="0,1,40,100,300,600,900")
a = ap.parse_args()
ids = json.load(open(a.ids))
print("ids_sha256", hashlib.sha256(json.dumps(ids, separators=(",", ":")).encode()).hexdigest(), file=sys.stderr)
if a.reencode:
    from tokenizers import Tokenizer
    tk = Tokenizer.from_file(a.model + "/tokenizer.json")
    text = open(a.reencode).read()
    new = tk.encode(text, add_special_tokens=False).ids[:2049]
    print("reencode_identical", new == ids, "len", len(new), file=sys.stderr)
    ids = new

if a.backend == "mlx":
    import mlx.core as mx
    from mlx_lm import load
    model, _ = load(a.model)
    def losses(seq):
        lg = model(mx.array([seq[:-1]])).astype(mx.float32); t = mx.array([seq[1:]])
        l = (mx.logsumexp(lg, -1) - mx.take_along_axis(lg, t[..., None], -1).squeeze(-1))[0]
        mx.eval(l); return l.tolist()
else:
    import torch
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(4)
    dt = getattr(torch, a.dtype)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=dt).eval()
    print("hf_class", type(model).__name__, file=sys.stderr)
    def losses(seq):
        with torch.no_grad():
            x = torch.tensor([seq[:-1]])
            lg = model(input_ids=x, use_cache=False).logits.float()[0]
            t = torch.tensor(seq[1:])
            return (torch.logsumexp(lg, -1) - lg.gather(-1, t[:, None]).squeeze(-1)).tolist()

t0 = time.time()
l = losses(ids)
out = {"backend": a.backend, "model": a.model, "dtype": a.dtype, "n_targets": len(l),
       "mean": round(sum(l) / len(l), 4),
       "bins256": [round(sum(l[i:i+256]) / len(l[i:i+256]), 2) for i in range(0, len(l), 256)]}
sweep = {}
for s in [int(x) for x in a.starts.split(",")]:
    seq = ids[s:]
    ls = losses(seq) if s else l
    tail = ls[900 - s - 1:] if s < 900 else ls
    sweep[str(s)] = round(sum(tail) / len(tail), 3)
out["tail_from_900_by_start"] = sweep
out["worst8"] = sorted(((round(v, 1), i) for i, v in enumerate(l)), reverse=True)[:8]
out["seconds"] = round(time.time() - t0, 1)
print(json.dumps(out))
