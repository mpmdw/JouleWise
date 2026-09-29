"""Classify the round-3 failing test ids (S1-REPAIR-ROUTE-01 §5.2), a PROPOSAL the lead confirms.

Usage: classify.py <triage_out> <r3_inventory> <main_reference_run>
T1: no bundle the test read on main was exempt -> pair alone.
T2: every bundle exempt and the REAL strict validator never ran -> fixture, rebind, pair, parity.
T5: every bundle exempt and the real strict validator ran -> builder corpus + parity.
T6: some exempt and some not -> NEEDS_RULING.
T3 (mock-refusal subject) and T4 (floor root holding no bundle) need the lead's reading: flagged.
NEW: the id does not exist on main (S1's own test); NOBUNDLE: no bundle identity was read on main.
"""
import json, os, re, sys
from collections import Counter, defaultdict

out, inv, ref = sys.argv[1:4]
failing = []
for name in ("fail_ids.txt", "error_ids.txt"):
    p = os.path.join(inv, name)
    kind = name.split("_")[0]
    failing += [(line.strip(), kind) for line in open(p) if line.strip()]

records = defaultdict(list)
for f in os.listdir(os.path.join(out, "log")):
    if f.endswith(".jsonl"):
        for line in open(os.path.join(out, "log", f)):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("test"):
                records[row["test"]].append(row)

main_outcome = {}
for f in os.listdir(os.path.join(ref, "mod")):
    if f.endswith(".json"):
        main_outcome.update(json.load(open(os.path.join(ref, "mod", f)))["outcomes"])

def first_error(test_id):
    mod = ".".join(test_id.split(".")[:2])
    p = os.path.join(inv, "mod", mod + ".log")
    if not os.path.exists(p):
        return ""
    text = open(p, errors="replace").read()
    short = test_id.split(".")[-1]
    i = text.find(short + " (")
    j = text.find("\n" + "=" * 70, i + 1) if i >= 0 else -1
    block = text[i:j if j > 0 else i + 4000] if i >= 0 else ""
    errs = [l for l in block.splitlines() if re.match(r"^\w*(Error|Exception|Refusal|Failure)\b|^AssertionError", l.strip())]
    return (errs[-1].strip() if errs else "")[:160]

rows, counts = [], Counter()
for test_id, kind in sorted(failing):
    base = re.sub(r" \(.*\)$", "", test_id)
    recs = records.get(base, [])
    ids = [r for r in recs if r["kind"] == "identity"]
    strict = [r for r in recs if r["kind"] == "strict_validator"]
    ex = [r["exempt"] for r in ids]
    if base not in main_outcome:
        cls = "NEW"
    elif not ids:
        cls = "NOBUNDLE"
    elif not any(ex):
        cls = "T1"
    elif all(ex):
        cls = "T5" if strict else "T2"
    else:
        cls = "T6"
    name = base.split(".")[-1].lower()
    flags = []
    if "mock" in name and ("refus" in name or "reject" in name or "inelig" in name):
        flags.append("T3?")
    if "floor" in name and cls in ("NOBUNDLE", "T2", "T5"):
        flags.append("T4?")
    counts[cls] += 1
    rows.append((base, kind, main_outcome.get(base, "-"), cls, ",".join(flags), len(ids), len(strict),
                 first_error(base)))

print("# S1 round-3 triage (proposal; the lead confirms each row)\n")
print("| test id | cand. | main | class | flags | bundles | strict calls | candidate error |")
print("|---|---|---|---|---|---|---|---|")
for r in rows:
    print("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |")
print("\n**Counts:** " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) + f" (total {sum(counts.values())})")
