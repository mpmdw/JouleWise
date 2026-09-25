Auto-loaded files: `/Users/edr/.claude/CLAUDE.md` only (no project CLAUDE.md, no memory files).

**Result: nine hand-mutated rosters were accepted by `_seal(registration, roster, finalize=True)`; eleven control mutations were refused.** The INV-11 closed form itself is implemented tightly. The accepted forgeries go through gaps around it: the seal never checks that a single's parent is a pack-created parent, never checks any field of a terminal refusal except `(model, item_id)`, never binds placements or voidings to events, and with `finalize=True` skips the whole digest chain. Replay (`_replay_roster`) does catch the two I re-checked (C1, C3 refuse with `inv_38`), so the exposure is the seal alone.

All scripts are in the scratch directory: `forge_common.py`, `forge_candidates.py`, `forge_more.py`. Run `python3 forge_candidates.py && python3 forge_more.py` from this directory.

## Shared constructor (`forge_common.py`)

```python
"""Shared registration + legal roster builders for the forger seat."""
import copy, json
from joulewise.scored_registration import Registration
from joulewise.scored_packer import pack, requeue_overrun, verify_executed_roster, executed_status, _seal, _checked_derived, PackingRefusal

M8, M1 = "big-8b", "small-1.7b"
ARM = "m4"

def registration(n=12, block_size=2, mode="pilot"):
    ids = {str(l): [f"L{l}I{i:02d}" for i in range(n)] for l in range(1, 6)}
    m = dict(
        schema="joulewise.scored_registration.v2", mode=mode,
        registration_id="reg-1", plan_id="plan-1", scorer_id="scorer-1",
        arm=ARM, arm_to_family={ARM: "apple"},
        role_to_model_id={"8B": M8, "1.7B": M1},
        sizing_receipt_sha256=None, predictions_sha256=None,
        alpha=0.05, n_boot=100, seed=0, floor_j=0.0, anchor_j=0.0,
        cap_tokens={ARM: 10}, block_size={ARM: block_size},
        item_ids_by_level=ids,
        envelope_s=120.0, interior_s=100.0, pitch_s=120.0, offset_s=5.0, guard_s=10.0,
        s_per_token_upper={M8: {ARM: 1.0}, M1: {ARM: 1.0}},
        prefill_s={M8: {ARM: 5.0}, M1: {ARM: 5.0}},
        ceiling_s={M8: {ARM: 20.0}, M1: {ARM: 20.0}},
        delta_upper_j_per_block_slot=None, budget_j=None,
        declared_sensitivities=["none"],
    )
    return Registration.from_mapping(m)

def predictions(reg, v=2.0):
    ids = reg.item_ids_by_level
    return {m: {i: v for l in ids for i in ids[l]} for m in reg.role_to_model_id.values()}

def root(reg=None):
    reg = reg or registration()
    return reg, pack(reg, predictions(reg))

def report_all_ok(reg, r, upto):
    while True:
        pending = next((e["index"] for e in r["envelopes"] if e["kind"] == "loaded" and e["observations"] is None), None)
        if pending is None or pending > upto:
            return r
        obs = [dict(block_id=b, status="completed", elapsed_s=1.0) for b in r["envelopes"][pending]["blocks"]]
        r = requeue_overrun(reg, r, pending, obs)

def split_roster():
    """Legal roster: parent big-8b:m4:5:0 advanced to whole_block (env 12), then split into singles (env 13)."""
    reg, r = root()
    P = f"{M8}:{ARM}:5:0"
    e0 = r["envelopes"][0]["blocks"]
    obs = [dict(block_id=b, status=("cut_off" if b == P else "completed"), elapsed_s=(6.0 if b == P else 1.0)) for b in e0]
    r = requeue_overrun(reg, r, 0, obs)
    wb = next(p for p in reversed(r["placements"]) if p["block_id"] == P)["envelope_index"]
    r = report_all_ok(reg, r, wb - 1)
    r = requeue_overrun(reg, r, wb, [dict(block_id=P, status="cut_off", elapsed_s=30.0)])
    return reg, r, P

def terminal_roster():
    """Legal roster: parent big-8b:m4:5:0 not_started with no culprit -> unattributed_overrun terminals."""
    reg, r = root()
    P = f"{M8}:{ARM}:5:0"
    e0 = r["envelopes"][0]["blocks"]
    obs = [dict(block_id=b, status=("not_started" if b == P else "completed"), elapsed_s=(None if b == P else 1.0)) for b in e0]
    r = requeue_overrun(reg, r, 0, obs)
    return reg, r, P

def reseal(reg, r):
    """Refresh derived fields, clear the seal, submit to _seal(finalize=True)."""
    r = copy.deepcopy(r)
    try:
        r["planned_spread_shortfall"], r["drift_lever_slots"] = _checked_derived(reg, r)
    except PackingRefusal:
        pass
    r["sha256"] = None
    try:
        return "ACCEPTED", _seal(reg, r, finalize=True)
    except PackingRefusal as exc:
        return f"REFUSED {exc}", None

def new_env(r, model):
    ix = len(r["envelopes"])
    r["envelopes"].append(dict(index=ix, model=model, kind="loaded", blocks=[], voided_block_ids=[], observations=None))
    return ix

def place(r, b, ix, reserve, attempt=None, stage=None):
    r["placements"].append(dict(block_id=b["block_id"], attempt=b["attempt"] if attempt is None else attempt,
                                stage=b["retry_stage"] if stage is None else stage, reserved_s=reserve, envelope_index=ix))
    r["envelopes"][ix]["blocks"].append(b["block_id"])
```

The registration is pilot mode with 12 items per level and block size 2, giving 6 parents per cell in 12 interleaved envelopes. Unmodified root, split, and terminal rosters all reseal as accepted.

## Accepted forgeries

**C1. Single of a single (grandchild block).** Accepted.
```python
from forge_common import *
reg, r, P = split_roster(); r = copy.deepcopy(r)
S = f"{P}:single:0"
sb = next(b for b in r["blocks"] if b["block_id"] == S)
sb["superseded"] = True
e13 = r["envelopes"][13]; e13["blocks"].remove(S); e13["voided_block_ids"].append(S)
G = dict(block_id=f"{S}:single:0", model=sb["model"], level=sb["level"], items=list(sb["items"]),
         predicted_item_s=list(sb["predicted_item_s"]), predicted_s=sb["predicted_s"], attempt=3,
         retry_stage="single_problem", parent_block_id=S, superseded=False, late=False)
r["blocks"].append(G)
ix = new_env(r, G["model"]); place(r, G, ix, 15.0)
print(reseal(reg, r)[0])   # ACCEPTED
```
Rationale. Item L5I00 is now held by three blocks: parent P (superseded), single S (superseded), and G, whose `parent_block_id` is a single. §0.4 defines a Parent as "a block created by `pack`; its `parent_block_id` is null" and a Single as "a one-item block created by a split. Its `parent_block_id` is its parent's id", so a single's parent must be a pack-created parent. §2.4 `block_id` rule: single id is `"{parent_id}:single:{j}"` with `parent_id` of the form `"{model_id}:{arm}:{level}:{k}"`. §2.4 `superseded`: "true if and only if the block is a `whole_block` retry that was split", but S is at `single_problem` and §3.3's edge list has no split edge from that stage (FT-1, Q5: only a `whole_block` `cut_off` splits). INV-12 is only satisfied because the seal reads "its parent exists" as any block, not a parent; INV-10 (iv) "the parent relation" is broken. Ownership consequence: M8-by-parent (INV-24) now keys G to S rather than P.

**C2. Root roster (events == []) with a pre-split parent.** Accepted.
```python
from forge_common import *
reg, r = root(); r = copy.deepcopy(r)
P = f"{M8}:{ARM}:5:0"
pb = next(b for b in r["blocks"] if b["block_id"] == P)
pb["superseded"] = True
env = next(e for e in r["envelopes"] if P in e["blocks"]); env["blocks"].remove(P); env["voided_block_ids"].append(P)
ix = new_env(r, M8)
for j, item in enumerate(pb["items"]):
    s = dict(block_id=f"{P}:single:{j}", model=M8, level=5, items=[item], predicted_item_s=[pb["predicted_item_s"][j]],
             predicted_s=15.0, attempt=0, retry_stage="initial", parent_block_id=P, superseded=False, late=False)
    r["blocks"].append(s); place(r, s, ix, 15.0)
print(reseal(reg, r)[0])   # ACCEPTED
```
Rationale. §3.1 step 1: at pack "each parent has `attempt 0`, `retry_stage "initial"`, `superseded false`"; §3.1 step 6 output has no singles. §0.4: a single is "created by a split", and §3.2 Effects: "every decision except `keep` moves the id from the reporting envelope's `blocks` to its `voided_block_ids`", so a voided id and singles cannot exist with `events == []` (FT-4 root roster). §2.4 `superseded` iff a `whole_block` retry was split. The seal checks the INV-11 closed form and INV-12 partition and nothing about how the split came to be.

**C2b. Root roster with a terminal refusal and a voided parent.** Accepted.
```python
from forge_common import *
reg, r = root(); r = copy.deepcopy(r)
P = f"{M8}:{ARM}:5:1"
pb = next(b for b in r["blocks"] if b["block_id"] == P)
env = next(e for e in r["envelopes"] if P in e["blocks"]); env["blocks"].remove(P); env["voided_block_ids"].append(P)
for item in pb["items"]:
    r["terminal_refusals"].append(dict(type="unattributed_overrun", block_id=P, attempt=0, parent_block_id=None, item_id=item, model=M8, level=5))
print(reseal(reg, r)[0])   # ACCEPTED
```
Rationale. FT-1 and §3.2 Effects: terminal refusals and voidings are produced only by a `requeue_overrun` decision; a root roster (FT-4) has had no call. §3.1 step 6 output form. The seal's `spread_minima` check passes because six parents per cell leaves five non-terminal.

**C3. Retargeted terminal refusal.** Accepted.
```python
from forge_common import *
reg, r, P = terminal_roster(); r = copy.deepcopy(r)
t = r["terminal_refusals"][0]
t.update(type="bogus_type", block_id=f"{M1}:{ARM}:1:3", attempt=99, parent_block_id="no-such-block", level=1)
print(reseal(reg, r)[0])   # ACCEPTED
```
Rationale. §2.8: `type` is `"ceiling_violation"` or `"unattributed_overrun"`; `attempt` is "the attempt of that block's voided placement". INV-37 predicate: "`(block_id, attempt)` names a voided placement of a block containing the item". Here the entry names the other model's level-1 block, attempt 99, level 1, and a nonexistent parent, for item L5I00 of `big-8b`. INV-11 ruled text says the item is "in exactly one terminal refusal", and that refusal's ownership claim is false. The seal reads only `(model, item_id)` from a terminal refusal.

**C4. Phantom, duplicated terminal refusals for an unregistered item and model.** Accepted.
```python
from forge_common import *
reg, r = root(); r = copy.deepcopy(r)
for _ in range(2):
    r["terminal_refusals"].append(dict(type="ceiling_violation", block_id="ghost", attempt=7, parent_block_id=None,
                                       item_id="NOT-REGISTERED", model="no-such-model", level=42))
print(reseal(reg, r)[0])   # ACCEPTED
```
Rationale. §2.8: "There is one entry per item, and `(model, item_id)` is unique"; INV-37: `(block_id, attempt)` must name a voided placement of a block containing the item (no block `ghost` exists); INV-04 item identity: the item set is exactly the registered items. INV-11 is evaluated only over registered (model, item) pairs, so unregistered pairs are never conserved.

**C5. `superseded` flipped on a terminal single.** Accepted.
```python
from forge_common import *
reg, r, P = split_roster()
obs = [dict(block_id=b, status="not_started", elapsed_s=None) for b in r["envelopes"][13]["blocks"]]
r = requeue_overrun(reg, r, 13, obs)           # both singles -> unattributed_overrun
r = copy.deepcopy(r)
next(b for b in r["blocks"] if b["block_id"] == f"{P}:single:1")["superseded"] = True
print(reseal(reg, r)[0])   # ACCEPTED
```
Rationale. §2.4 `superseded` is "true if and only if the block is a `whole_block` retry that was split"; a `single_problem` block has no split edge (§3.3). INV-12's partition clause is checked only for parents, so a superseded single with no children passes.

**C6. Forged placement stage and attempt on a root placement.** Accepted.
```python
from forge_common import *
reg, r = root(); r = copy.deepcopy(r)
r["placements"][0]["stage"] = "single_problem"; r["placements"][0]["attempt"] = 5
print(reseal(reg, r)[0])   # ACCEPTED
```
Rationale. INV-36: "a root holds only `initial` placements with `attempt 0`"; Q11: attempt is 0 at the initial placement; §2.4 `attempt` is "the `attempt` of the block's latest placement" (block says 0, placement says 5). Window key is `(block_id, attempt)` (Q11, FT-11), so this forges which window the block owns. The seal checks placement `stage` and `attempt` only for type and domain.

**C7. Live placement into an already-reported envelope.** Accepted.
```python
from forge_common import *
reg, r, P = split_roster(); r = copy.deepcopy(r)
S1 = f"{P}:single:1"; sb = next(b for b in r["blocks"] if b["block_id"] == S1)
r["envelopes"][13]["blocks"].remove(S1); r["envelopes"][13]["voided_block_ids"].append(S1)
place(r, sb, 0, 15.0)                           # envelope 0 was reported by event 0
print(reseal(reg, r)[0])   # ACCEPTED
```
Rationale. INV-18: "An envelope is fixed once an observation is recorded on it; a retry or reschedule is placed only at an index above the reporting envelope's"; §3.5 eligibility requires `e.observations is None`. RD-1: an event's `block_ids` is "the reporting envelope's `blocks` list in execution order at the call", and envelope 0's `blocks` now differs from event 0's `block_ids`. The item's live position, which feeds the planned position (RD-4) and the drift lever, is forged into index 0. The seal's `inv_18` check covers only placements listed in an event's `placements`; unreferenced placements are never checked.

**C8. Event-less reschedule.** Accepted.
```python
from forge_common import *
reg, r, P = split_roster(); r = copy.deepcopy(r)
S1 = f"{P}:single:1"; sb = next(b for b in r["blocks"] if b["block_id"] == S1)
r["envelopes"][13]["blocks"].remove(S1); r["envelopes"][13]["voided_block_ids"].append(S1)
ix = new_env(r, M8); place(r, sb, ix, 15.0, attempt=3)
print(reseal(reg, r)[0])   # ACCEPTED
```
Rationale. RD-3: placements are pack-time or event-made; RD-2: `Event.placements` lists every placement an event created, and no event lists this one. §3.2 Effects: voiding happens only by a non-`keep` decision, but envelope 13 has no observations. Q11 and §2.4: the block's `attempt` is 2 while its "latest placement" carries 3.

## Refused attempts (controls)

| Mutation | Seal result |
|---|---|
| R1 second live placement of a parent in a new envelope | `inv_11: item conservation` |
| R2 terminal parent also placed live | `inv_11` |
| R3 superseded parent restored to `blocks` beside its singles | `inv_11` |
| R4 one single deleted (block, placement, envelope entry) | `inv_11` |
| R5 parent `superseded` set false while singles exist | `inv_12: single parent` |
| R6 items swapped between two parents of a cell | `inv_10: parent formation and order` |
| R7 one terminal refusal removed | `inv_11` |
| R8 terminal refusal `model` swapped to the other model | `inv_11` |
| R9 items swapped between two singles | `inv_12: single item` |
| R10 extra parent block appended | `inv_10` |
| R11 grandchild placed beside another parent of the same cell | `inv_24: parent spread` |

The closed-form INV-11 check refuses every direct live/terminal count manipulation I tried. Every accepted forgery instead exploits a rule the seal does not encode: the parent-of-a-single definition (C1), event-only provenance of splits, voidings, terminals and placements (C2, C2b, C7, C8), terminal-refusal fields beyond `(model, item_id)` (C3, C4), the `superseded` iff-split rule on singles (C5), and placement `stage`/`attempt` binding (C6).
