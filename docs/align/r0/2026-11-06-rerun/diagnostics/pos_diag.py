import json, sys
import mlx.core as mx
from mlx_lm import load
r = json.load(open(sys.argv[1]))
ids = [c for c in r["checks"] if c.get("check") == "load"][0]["nll_prompt_ids"]
model, tok = load("/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit")
def bins(seq, w=256):
    lg = model(mx.array([seq[:-1]])).astype(mx.float32); t = mx.array([seq[1:]])
    l = (mx.logsumexp(lg, -1) - mx.take_along_axis(lg, t[..., None], -1).squeeze(-1))[0]; mx.eval(l)
    return [round(l[i:i+w].mean().item(), 2) for i in range(0, l.shape[0], w)]
para = open("/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/README.md").read()
nat = tok.encode(para)[:2049]
out = {"pinned_bins256": bins(ids), "readme_tokens": len(nat), "readme_bins256": bins(nat)}
out["pinned_tail_text"] = tok.decode(ids[-120:])
out["pinned_mid_text"] = tok.decode(ids[1000:1080])
print(json.dumps(out, indent=1))
