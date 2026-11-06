import json, sys, math
import mlx.core as mx
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache
r = json.load(open(sys.argv[1]))
ids = [c for c in r["checks"] if c.get("check") == "load"][0]["nll_prompt_ids"]
model, tok = load("/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit")
def losses_of(logits, targets):
    logits = logits.astype(mx.float32)
    return mx.logsumexp(logits, axis=-1) - mx.take_along_axis(logits, targets[..., None], axis=-1).squeeze(-1)
def chunked(ids, step):
    cache = make_prompt_cache(model); tot = 0.0; n = len(ids) - 1
    for s in range(0, n, step):
        e = min(n, s + step)
        v = mx.sum(losses_of(model(mx.array([ids[s:e]]), cache=cache), mx.array([ids[s+1:e+1]])))
        mx.eval(v, [c.state for c in cache]); tot += v.item()
    return tot / n
out = {}
# one pass with a fresh cache (whole sequence in one call)
out["one_pass_cache"] = chunked(ids, 4096)
out["chunk128_cache"] = chunked(ids, 128)
# one pass, no cache argument
l = losses_of(model(mx.array([ids[:-1]])), mx.array([ids[1:]])); mx.eval(l)
out["one_pass_nocache"] = l.mean().item()
out["first64_mean_nocache"] = l[0, :64].mean().item()
out["last512_mean_nocache"] = l[0, -512:].mean().item()
txt = "The quick brown fox jumps over the lazy dog. " * 20 + "Energy measurement on laptops requires careful control of background processes, battery state and thermal conditions."
t = tok.encode(txt)
lt = losses_of(model(mx.array([t[:-1]])), mx.array([t[1:]])); mx.eval(lt)
out["natural_text_nocache"] = lt.mean().item(); out["natural_text_tokens"] = len(t)
out["decoded_head"] = tok.decode(ids[:60])
print(json.dumps(out, indent=1))
