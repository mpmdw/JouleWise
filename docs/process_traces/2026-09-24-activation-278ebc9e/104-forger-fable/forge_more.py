import copy
from forge_common import *
from forge_candidates import new_env, place
results = {}

# C7: live placement of a single into the ALREADY-REPORTED envelope 0 (not referenced by any event)
reg, r, P = split_roster(); r = copy.deepcopy(r)
S1 = f"{P}:single:1"; sb = next(b for b in r["blocks"] if b["block_id"] == S1)
r["envelopes"][13]["blocks"].remove(S1); r["envelopes"][13]["voided_block_ids"].append(S1)
place(r, sb, 0, 15.0)                      # envelope 0 has observations recorded
results["C7 live placement into reported envelope 0"] = reseal(reg, r)
print("env0 blocks now:", r["envelopes"][0]["blocks"], "| event0 block_ids:", r["events"][0]["block_ids"])

# C8: event-less reschedule (void in 13, new placement in fresh envelope, no event records it)
reg, r, P = split_roster(); r = copy.deepcopy(r)
sb = next(b for b in r["blocks"] if b["block_id"] == S1)
r["envelopes"][13]["blocks"].remove(S1); r["envelopes"][13]["voided_block_ids"].append(S1)
ix = new_env(r, M8); place(r, sb, ix, 15.0, attempt=3)
results["C8 event-less reschedule"] = reseal(reg, r)

# R11: grandchild sharing an envelope with another level-5 parent of the same cell
reg, r, P = split_roster(); r = copy.deepcopy(r)
S = f"{P}:single:0"; sb = next(b for b in r["blocks"] if b["block_id"] == S); sb["superseded"] = True
r["envelopes"][13]["blocks"].remove(S); r["envelopes"][13]["voided_block_ids"].append(S)
G = dict(sb, block_id=f"{S}:single:0", parent_block_id=S, superseded=False, attempt=3); r["blocks"].append(G)
Q = f"{M8}:{ARM}:5:1"; qix = next(e["index"] for e in r["envelopes"] if Q in e["blocks"])
place(r, G, qix, 15.0)
results["R11 grandchild beside another parent of the cell"] = reseal(reg, r)

for k, (v, _) in results.items():
    print(f"{k:50s} -> {v}")
