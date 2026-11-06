import json, sys
import mlx.core as mx
from mlx_lm import load
r = json.load(open(sys.argv[1]))
ids = [c for c in r["checks"] if c.get("check") == "load"][0]["nll_prompt_ids"]
model, tok = load("/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit")
lg = model(mx.array([ids[:-1]])).astype(mx.float32)[0]; mx.eval(lg)
out = {}
for p in (100, 980, 1461, 1636):
    row = lg[p]; top = mx.argsort(-row)[:5].tolist()
    out[str(p)] = {"max_logit": row.max().item(), "min_logit": row.min().item(), "std": mx.std(row).item(),
                   "top5": [tok.decode([t]) for t in top], "target": tok.decode([ids[p+1]])}
def nll(seq):
    l = model(mx.array([seq[:-1]])).astype(mx.float32); t = mx.array([seq[1:]])
    v = (mx.logsumexp(l, -1) - mx.take_along_axis(l, t[..., None], -1).squeeze(-1))[0]; mx.eval(v); return v
tail = nll(ids[900:])
out["suffix_from_900_bins128"] = [round(tail[i:i+128].mean().item(),2) for i in range(0, tail.shape[0], 128)]
out["model_dtype_sample"] = str(next(iter(v for k,v in __import__('mlx.utils',fromlist=['tree_flatten']).tree_flatten(model.parameters()) if 'norm' in k)).dtype)
print(json.dumps(out, indent=1, ensure_ascii=False))
