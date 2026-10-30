import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from joulewise.b5.harvest import member_spans
tails=[]
for line in Path(sys.argv[2]).read_text().split():
    b=Path(line); meta=json.loads((b/"metadata.json").read_text())
    ev=[json.loads(x) for x in (b/"events.jsonl").read_text().splitlines() if x.strip()]
    s=member_spans(meta, ev)
    if s["request"]:
        tails.append((s["member"][1]-s["request"][1])/1e9)
tails.sort()
print(f"members {len(tails)}; post-request tail s: min {tails[0]:.1f} median {tails[len(tails)//2]:.1f} max {tails[-1]:.1f}")
