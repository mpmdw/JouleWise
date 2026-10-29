"""Triage drop.out: an exit-0 drop matters when the removed subtree held a leaf that the base run binds to a
compared family (step-11 outputs: by coverage; other L9 outputs: listed whole for reading)."""
import re, sys
sys.path.insert(0, ".codex-report/rc-cmp8-opus-rev")
import probe_cmp8 as p
c = p.case(); code, err, out = p.run(c)
leaves = out["coverage"]["leaves"]
compared = {k for k, v in leaves.items() if not v.startswith("uncovered")}
LABEL = {"disclosures/<sha>.json": "disclosure", "outputs/<sha>-results-fill-input.json": "fill"}
def star(doc, ptr):
    parts, node = [], doc
    for k in ptr:
        item = node[k]
        parts.append(p.cmp.step(item) if isinstance(node, list) else str(k))
        node = item
    return "/".join(parts)
other = []
for line in open(".codex-report/rc-cmp8-opus-rev/drop.out"):
    m = re.match(r"   EXIT0 (.*?):(.*)$", line.rstrip("\n"))
    if not m:
        continue
    name, ptr = m.groups()
    full = name.replace("<sha>", "0" * 64).replace("<sens>", "1" * 64)
    ptr = [int(x) if x.isdigit() else x for x in ptr.split("/")]
    if name in LABEL:
        s = LABEL[name] + ":" + star(c.files[full], ptr)
        hit = sorted(k for k in compared if k == s or k.startswith(s + "/"))
        if hit:
            print("COMPARED-LEAF-DROP", name + ":" + "/".join(map(str, ptr)), "->", hit[:6], leaves.get(hit[0]))
    else:
        other.append(name + ":" + "/".join(map(str, ptr)))
print("\nnon-step-11 exit-0 drops:", len(other))
for o in other:
    print("  ", o)
