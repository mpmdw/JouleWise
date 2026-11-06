"""Re-render the pinned SHADE prefix with the model's own chat template (apply_chat_template) and
compare to the pinned ids; also build the ablation sequences for the prefix tests."""
import json, sys
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(sys.argv[1])
ids = json.load(open(sys.argv[2])); text = open(sys.argv[3]).read()
body = text.split("<tools>\n", 1)[1].split("\n")
tools = [json.loads(l) for l in body[:-1]]  # last line is cut at token 2049
print("complete tools recovered:", len(tools))
msgs = [{"role": "system", "content": "SYSTEM"}, {"role": "user", "content": "USER"}]
out = {}
for name, kw in (("native_xhigh_default", {}), ("native_no_thinking", {"enable_thinking": False})):
    r = tok.apply_chat_template(msgs, tools=tools, tokenize=True, add_generation_prompt=True, **kw)
    r = list(r["input_ids"] if isinstance(r, dict) or hasattr(r, "keys") else r)
    n = next((i for i, (x, y) in enumerate(zip(r, ids)) if x != y), min(len(r), len(ids)))
    out[name] = {"len": len(r), "common_prefix_with_pinned": n}
    print(name, out[name], repr(tok.decode(r[:60]))[:200])
    if name == "native_no_thinking": json.dump(r[:2049 - 38], open("/private/tmp/jwd8diag/work/ids_nothink.json", "w"))
# where do the pinned ids diverge from the native render?  print 2049 = all equal
json.dump(out, open("/private/tmp/jwd8diag/work/rerender.json", "w"), indent=1)
