import json, sys
import mlx.core as mx
from mlx_lm import load
r = json.load(open(sys.argv[1]))
ids = [c for c in r["checks"] if c.get("check") == "load"][0]["nll_prompt_ids"]
model, tok = load("/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit")
text = tok.decode(ids)
re_ids = tok.encode(text, add_special_tokens=False)
def nll(seq):
    lg = model(mx.array([seq[:-1]])).astype(mx.float32); t = mx.array([seq[1:]])
    l = (mx.logsumexp(lg, -1) - mx.take_along_axis(lg, t[..., None], -1).squeeze(-1))[0]; mx.eval(l); return l
l = nll(re_ids)
first_diff = next((i for i,(a,b) in enumerate(zip(ids, re_ids)) if a != b), None)
lp = nll(ids)
worst = sorted(range(lp.shape[0]), key=lambda i: -lp[i].item())[:8]
print(json.dumps({"pinned_len": len(ids), "reencoded_len": len(re_ids), "first_diff": first_diff,
  "pinned_around_diff": ids[first_diff-3:first_diff+5] if first_diff else None,
  "re_around_diff": re_ids[first_diff-3:first_diff+5] if first_diff else None,
  "reencoded_mean_nll": l.mean().item(),
  "worst_positions": [(i, round(lp[i].item(),1), tok.decode([ids[i]]), tok.decode([ids[i+1]])) for i in worst],
  "vocab_size_tok": len(tok.vocab) if hasattr(tok,'vocab') else None,
  "max_id": max(ids)}, indent=1, ensure_ascii=False))
