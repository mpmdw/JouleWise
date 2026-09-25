import copy, json
from forge_common import *

def new_env(r, model):
    ix = len(r["envelopes"])
    r["envelopes"].append(dict(index=ix, model=model, kind="loaded", blocks=[], voided_block_ids=[], observations=None))
    return ix

def place(r, b, ix, reserve, attempt=None, stage=None):
    r["placements"].append(dict(block_id=b["block_id"], attempt=b["attempt"] if attempt is None else attempt,
                                stage=b["retry_stage"] if stage is None else stage, reserved_s=reserve, envelope_index=ix))
    r["envelopes"][ix]["blocks"].append(b["block_id"])

results = {}

# ---------- C1: single of a single (grandchild) ----------
reg, r, P = split_roster()
r = copy.deepcopy(r)
S = f"{P}:single:0"
sb = next(b for b in r["blocks"] if b["block_id"] == S)
sb["superseded"] = True                       # pretend the single was "split"
e13 = r["envelopes"][13]; e13["blocks"].remove(S); e13["voided_block_ids"].append(S)
G = dict(block_id=f"{S}:single:0", model=sb["model"], level=sb["level"], items=list(sb["items"]),
         predicted_item_s=list(sb["predicted_item_s"]), predicted_s=sb["predicted_s"], attempt=3,
         retry_stage="single_problem", parent_block_id=S, superseded=False, late=False)
r["blocks"].append(G)
ix = new_env(r, G["model"]); place(r, G, ix, 15.0)
results["C1 grandchild single"] = reseal(reg, r)

# ---------- C2: root roster (events == []) with a pre-split parent ----------
reg, r = root()
r = copy.deepcopy(r)
P = f"{M8}:{ARM}:5:0"
pb = next(b for b in r["blocks"] if b["block_id"] == P)
pb["superseded"] = True
env = next(e for e in r["envelopes"] if P in e["blocks"]); env["blocks"].remove(P); env["voided_block_ids"].append(P)
ix = new_env(r, M8)
for j, item in enumerate(pb["items"]):
    s = dict(block_id=f"{P}:single:{j}", model=M8, level=5, items=[item], predicted_item_s=[pb["predicted_item_s"][j]],
             predicted_s=15.0, attempt=0, retry_stage="initial", parent_block_id=P, superseded=False, late=False)
    r["blocks"].append(s); place(r, s, ix, 15.0)
results["C2 root with pre-split parent"] = reseal(reg, r)

# ---------- C2b: root roster with a terminal refusal and a voided parent ----------
reg, r = root()
r = copy.deepcopy(r)
P = f"{M8}:{ARM}:5:1"
pb = next(b for b in r["blocks"] if b["block_id"] == P)
env = next(e for e in r["envelopes"] if P in e["blocks"]); env["blocks"].remove(P); env["voided_block_ids"].append(P)
for item in pb["items"]:
    r["terminal_refusals"].append(dict(type="unattributed_overrun", block_id=P, attempt=0, parent_block_id=None, item_id=item, model=M8, level=5))
results["C2b root with terminal refusal"] = reseal(reg, r)

# ---------- C3: retargeted terminal refusal ----------
reg, r, P = terminal_roster()
r = copy.deepcopy(r)
t = r["terminal_refusals"][0]
t.update(type="bogus_type", block_id=f"{M1}:{ARM}:1:3", attempt=99, parent_block_id="no-such-block", level=1)
results["C3 retargeted terminal refusal"] = reseal(reg, r)

# ---------- C4: phantom terminal refusal (unregistered item / model) ----------
reg, r = root()
r = copy.deepcopy(r)
r["terminal_refusals"].append(dict(type="ceiling_violation", block_id="ghost", attempt=7, parent_block_id=None, item_id="NOT-REGISTERED", model="no-such-model", level=42))
r["terminal_refusals"].append(dict(type="ceiling_violation", block_id="ghost", attempt=7, parent_block_id=None, item_id="NOT-REGISTERED", model="no-such-model", level=42))
results["C4 phantom terminal refusals (dup, unregistered)"] = reseal(reg, r)

# ---------- C5: flip superseded on a terminal single ----------
reg, r, P = split_roster()
obs = [dict(block_id=b, status="not_started", elapsed_s=None) for b in r["envelopes"][13]["blocks"]]
r = requeue_overrun(reg, r, 13, obs)      # both singles -> unattributed_overrun (terminal)
r = copy.deepcopy(r)
sb = next(b for b in r["blocks"] if b["block_id"] == f"{P}:single:1"); sb["superseded"] = True
results["C5 superseded flag on terminal single"] = reseal(reg, r)

# ---------- C6: placement stage/attempt forged (parent placement labelled single_problem) ----------
reg, r = root(); r = copy.deepcopy(r)
r["placements"][0]["stage"] = "single_problem"; r["placements"][0]["attempt"] = 5
results["C6 forged placement stage/attempt"] = reseal(reg, r)

# ---------- Controls expected to be refused ----------
reg, r = root(); r = copy.deepcopy(r)
P = f"{M8}:{ARM}:5:0"; ix = new_env(r, M8); place(r, next(b for b in r["blocks"] if b["block_id"]==P), ix, 4.0)
results["R1 duplicate live placement"] = reseal(reg, r)

reg, r, P = terminal_roster(); r = copy.deepcopy(r)
pb = next(b for b in r["blocks"] if b["block_id"]==P); ix = new_env(r, M8); place(r, pb, ix, 4.0)
results["R2 live + terminal"] = reseal(reg, r)

reg, r, P = split_roster(); r = copy.deepcopy(r)
r["envelopes"][12]["voided_block_ids"].remove(P); r["envelopes"][12]["blocks"].append(P)
results["R3 superseded parent still live"] = reseal(reg, r)

reg, r, P = split_roster(); r = copy.deepcopy(r)
r["blocks"] = [b for b in r["blocks"] if b["block_id"] != f"{P}:single:1"]
r["envelopes"][13]["blocks"].remove(f"{P}:single:1"); r["placements"] = [p for p in r["placements"] if p["block_id"] != f"{P}:single:1"]
results["R4 single removed"] = reseal(reg, r)

reg, r, P = split_roster(); r = copy.deepcopy(r)
next(b for b in r["blocks"] if b["block_id"]==P)["superseded"] = False
results["R5 parent not superseded but has singles"] = reseal(reg, r)

reg, r = root(); r = copy.deepcopy(r)
a, b = (x for x in r["blocks"] if x["block_id"] in (f"{M8}:{ARM}:5:0", f"{M8}:{ARM}:5:1"))
a["items"][1], b["items"][0] = b["items"][0], a["items"][1]
results["R6 items swapped between parents"] = reseal(reg, r)

reg, r, P = terminal_roster(); r = copy.deepcopy(r)
r["terminal_refusals"].pop()
results["R7 terminal refusal removed"] = reseal(reg, r)

reg, r, P = terminal_roster(); r = copy.deepcopy(r)
r["terminal_refusals"][0]["model"] = M1
results["R8 terminal refusal model swapped"] = reseal(reg, r)

reg, r, P = split_roster(); r = copy.deepcopy(r)
s0, s1 = (x for x in r["blocks"] if x["parent_block_id"] == P)
s0["items"], s1["items"] = s1["items"], s0["items"]
results["R9 single items swapped"] = reseal(reg, r)

reg, r = root(); r = copy.deepcopy(r)
extra = copy.deepcopy(r["blocks"][0]); extra["block_id"] = f"{M8}:{ARM}:1:6"; extra["items"] = ["L1I00"]; extra["predicted_item_s"]=[2.0]; extra["predicted_s"]=2.0
r["blocks"].append(extra)
results["R10 extra parent"] = reseal(reg, r)

for k, (v, _) in results.items():
    print(f"{k:50s} -> {v}")
