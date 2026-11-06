import json, sys
import mlx.core as mx
from mlx_lm import load
r = json.load(open(sys.argv[1]))
ids = [c for c in r["checks"] if c.get("check") == "load"][0]["nll_prompt_ids"]
model, tok = load("/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit")
def nll(seq, skip=0):
    l = model(mx.array([seq[:-1]])).astype(mx.float32); t = mx.array([seq[1:]])
    v = (mx.logsumexp(l, -1) - mx.take_along_axis(l, t[..., None], -1).squeeze(-1))[0]; mx.eval(v); return round(v[skip:].mean().item(), 3)
n_tail = len(ids) - 900
out = {}
for start in (0, 1, 40, 100, 300, 600, 900):
    seq = ids[start:]
    out[f"start_{start}_tail_from_900"] = nll(seq, skip=900 - start - 1 if start < 900 else 0)
print(json.dumps(out, indent=1))
