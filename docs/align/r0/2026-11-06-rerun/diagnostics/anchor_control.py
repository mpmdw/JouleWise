import json, sys
import mlx.core as mx
from mlx_lm import load
r = json.load(open(sys.argv[1]))
ids = [c for c in r["checks"] if c.get("check") == "load"][0]["nll_prompt_ids"]
_, dtok = load(sys.argv[2], lazy=True) if False else (None, None)
from transformers import AutoTokenizer
text = AutoTokenizer.from_pretrained("/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit").decode(ids)
model, tok = load(sys.argv[2])
a = tok.encode(text, add_special_tokens=False)[:2049]
lg = model(mx.array([a[:-1]])).astype(mx.float32); t = mx.array([a[1:]])
l = (mx.logsumexp(lg, -1) - mx.take_along_axis(lg, t[..., None], -1).squeeze(-1))[0]; mx.eval(l)
print(json.dumps({"model": sys.argv[2], "tokens": len(a), "mean": l.mean().item(),
  "bins256": [round(l[i:i+256].mean().item(), 2) for i in range(0, l.shape[0], 256)]}))
