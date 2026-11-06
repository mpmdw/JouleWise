"""Diagnostic: does D sustain >=12 echo transitions under a given ECHO_PROMPT? Not R0, not a measurement."""
import json, sys, time
sys.path.insert(0, sys.argv[1])
from joulewise.align import r0
from joulewise.align.r0_mlx import MlxBackend
class NoGuard:
    def check(self, force=False): return None
cfg = json.load(open(sys.argv[1] + "/configs/align/v4/r0_desk.json"))
backend = MlxBackend("D", cfg["models"]["D"]["source"], cfg["shade_cache"], NoGuard())
print(json.dumps(backend.device_info())[:200], flush=True)
PROMPTS = {
 "current": r0.ECHO_PROMPT,
 "count16": "Call r0_echo with value desk-check 16 times in total, one call per turn. After each tool reply, make the next call. Do not stop, summarize or ask the user before all 16 calls are made.",
}
orig_chat = backend.chat
out = []
for name, prompt in PROMPTS.items():
    for seed in (95, 96, 97):
        r0.ECHO_PROMPT = prompt
        backend.chat = lambda m, t, cap, s, _seed=seed, **kw: orig_chat(m, t, cap, _seed, **kw)
        t = time.time()
        res = r0.generated_rewrites(backend)
        rows = res["transitions"]
        rec = {"prompt": name, "seed": seed, "status": res["status"], "transitions": len(rows),
               "closed": sum(r["closed_reasoning"] for r in rows),
               "rewritten": [r["rewritten_prefix_tokens"] for r in rows],
               "off_spec": res["off_spec_echo_turns"], "verdict": r0.checkpoint_verdict("D", res),
               "last_visible": res["turns"][-1]["visible_text"][-200:] if res["turns"] else None,
               "seconds": round(time.time() - t, 1)}
        print(json.dumps(rec), flush=True); out.append(rec)
json.dump(out, open(sys.argv[2], "w"), indent=1)
