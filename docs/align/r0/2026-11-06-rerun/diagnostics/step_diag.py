import json, sys
import mlx.core as mx
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache
r = json.load(open(sys.argv[1]))
ids = [c for c in r["checks"] if c.get("check") == "load"][0]["nll_prompt_ids"]
model, tok = load("/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit")
out = {}
for step in (1, 16, 64):
    cache = make_prompt_cache(model); ls = []; n = len(ids) - 1
    for s in range(0, n, step):
        e = min(n, s + step)
        lg = model(mx.array([ids[s:e]]), cache=cache).astype(mx.float32); t = mx.array([ids[s+1:e+1]])
        v = (mx.logsumexp(lg, -1) - mx.take_along_axis(lg, t[..., None], -1).squeeze(-1))[0]
        mx.eval(v, [c.state for c in cache]); ls.extend(v.tolist())
    out[f"step_{step}"] = {"mean": round(sum(ls)/n, 3), "bins256": [round(sum(ls[i:i+256])/len(ls[i:i+256]), 2) for i in range(0, n, 256)]}
    print(json.dumps({f"step_{step}": out[f"step_{step}"]}), flush=True)
