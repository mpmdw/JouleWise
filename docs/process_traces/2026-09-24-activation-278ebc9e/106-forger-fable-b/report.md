Auto-loaded files: `/Users/edr/.claude/CLAUDE.md` (global user instructions). Nothing else.

**Result: `_seal(registration, roster, finalize=True)` accepts nine forged rosters.** The strongest are a chained single whose "parent" is itself a single (INV-12), a split forged from a parent that never reached the whole-block stage (INV-12 predicate satisfied but §2.4 `superseded` rule and §3.2 violated), and terminal refusals that name no voided placement (INV-37). All accepted rosters also pass the entry seal that every consumer runs. Only replay (`verify_executed_roster`) catches them, with `inv_38`, and the charge targets the seal.

## Reproduction code

The complete constructor code is in `forge_final.py` in this directory. Its full contents:

```python
"""Scratch harness: registration factory + legal rosters. Run from project root."""
import copy, hashlib, json
from joulewise.scored_registration import Registration, LEVELS
from joulewise import scored_packer as sp

def make_registration(n_per_level=10, block_size=2, mode="pilot"):
    ids = {str(l): [f"L{l}i{j}" for j in range(n_per_level)] for l in LEVELS}
    g = dict(
        schema="joulewise.scored_registration.v2", mode=mode,
        registration_id="reg-forge", plan_id="plan-forge", scorer_id="scorer-forge",
        arm="a", arm_to_family={"a": "fam"},
        role_to_model_id={"8B": "m8", "1.7B": "m1"},
        sizing_receipt_sha256="0"*64, predictions_sha256=None,
        alpha=0.05, n_boot=10, seed=0, floor_j=0.0, anchor_j=0.0,
        cap_tokens={"a": 100}, block_size={"a": block_size},
        item_ids_by_level=ids,
        envelope_s=25.0, interior_s=20.0, pitch_s=25.0, offset_s=0.0, guard_s=1.0,
        s_per_token_upper={"m8": {"a": 0.01}, "m1": {"a": 0.01}},
        prefill_s={"m8": {"a": 0.5}, "m1": {"a": 0.5}},
        ceiling_s={"m8": {"a": 2.0}, "m1": {"a": 2.0}},
        delta_upper_j_per_block_slot=None, budget_j=None,
        declared_sensitivities=["none"],
    )
    return Registration.from_mapping(g)

def predictions(reg, value=0.5):
    return {m: {i: value for i in sp._items(reg)} for m in sp._roles(reg)}

def root_roster(reg):
    return sp.pack(reg, predictions(reg))

def refresh(reg, roster):
    """Refresh derived fields and clear the seal so finalize=True can run."""
    roster["sha256"] = None
    roster["planned_spread_shortfall"], roster["drift_lever_slots"] = sp._checked_derived(reg, roster)
    return roster

def submit(reg, roster, label):
    try:
        out = sp._seal(reg, copy.deepcopy(roster), finalize=True)
        print(f"[{label}] ACCEPTED sha256={out['sha256'][:16]}")
        return True
    except sp.PackingRefusal as e:
        print(f"[{label}] REFUSED {e}")
        return False

def split_roster(reg):
    """Root -> keep-all on env 0 -> env 1: first block culprit cut_off, rest not_started
    (advance to whole_block + reschedules) -> report intervening envelopes all-keep until
    the whole_block envelope -> cut_off it -> split into singles."""
    r = root_roster(reg)
    obs = [dict(block_id=b, status="completed", elapsed_s=0.9) for b in r["envelopes"][0]["blocks"]]
    r = sp.requeue_overrun(reg, r, 0, obs)
    ids = r["envelopes"][1]["blocks"]
    obs = [dict(block_id=ids[0], status="cut_off", elapsed_s=5.0)] + [dict(block_id=b, status="not_started", elapsed_s=None) for b in ids[1:]]
    r = sp.requeue_overrun(reg, r, 1, obs)
    wb = next(b["block_id"] for b in r["blocks"] if b["retry_stage"] == "whole_block")
    wb_env = next(e["index"] for e in r["envelopes"] if wb in e["blocks"])
    while True:
        pending = next(e for e in r["envelopes"] if e["kind"] == "loaded" and e["observations"] is None)
        if pending["index"] == wb_env:
            obs = [dict(block_id=wb, status="cut_off", elapsed_s=5.0)]
            r = sp.requeue_overrun(reg, r, wb_env, obs)
            return r, wb
        obs = [dict(block_id=b, status="completed", elapsed_s=0.9) for b in pending["blocks"]]
        r = sp.requeue_overrun(reg, r, pending["index"], obs)

reg = make_registration()
SPLIT, WB = split_roster(reg)          # legal roster: parent m1:a:1:0 split into two singles, live in env 12
S0, S1 = f"{WB}:single:0", f"{WB}:single:1"

def env_of(r, bid):
    return next(e for e in r["envelopes"] if bid in e["blocks"])

def block(r, bid):
    return next(b for b in r["blocks"] if b["block_id"] == bid)

# C1': grandchild single (a single's "parent" is itself a single), placed in its own envelope
def c1b_grandchild_new_env():
    r = copy.deepcopy(SPLIT)
    e = env_of(r, S0)
    block(r, S0)["superseded"] = True
    e["blocks"].remove(S0); e["voided_block_ids"].append(S0)
    gid = f"{S0}:single:0"
    t = sp._new_envelope(r, "m1")
    r["blocks"].append(dict(block_id=gid, model="m1", level=1, items=["L1i0"], predicted_item_s=[0.5], predicted_s=1.5,
                            attempt=3, retry_stage="single_problem", parent_block_id=S0, superseded=False, late=False))
    r["placements"].append(dict(block_id=gid, attempt=3, stage="single_problem", reserved_s=1.5, envelope_index=t))
    r["envelopes"][t]["blocks"].append(gid)
    return refresh(reg, r)

# C2a: terminal refusal whose (block_id, attempt) names no voided placement; bogus type and level
def c2a_terminal_wrong_block():
    r = copy.deepcopy(SPLIT)
    e = env_of(r, S1)
    e["blocks"].remove(S1); e["voided_block_ids"].append(S1)
    r["terminal_refusals"].append(dict(type="bogus_type", block_id="m8:a:5:4", attempt=99,
                                       parent_block_id=None, item_id="L1i1", model="m1", level=5))
    return refresh(reg, r)

# C2b': terminal item whose block has NO placement at all; event indices repaired
def c2b_terminal_no_placement_fixed():
    r = copy.deepcopy(SPLIT)
    e = env_of(r, S1); e["blocks"].remove(S1)
    gone = next(i for i, p in enumerate(r["placements"]) if p["block_id"] == S1)
    del r["placements"][gone]
    for ev in r["events"]:
        ev["placements"] = [i - (i > gone) for i in ev["placements"] if i != gone]
    r["terminal_refusals"].append(dict(type="ceiling_violation", block_id=S1, attempt=2, parent_block_id=WB, item_id="L1i1", model="m1", level=1))
    return refresh(reg, r)

# C3: phantom terminal refusal for an unregistered item
def c3_phantom_terminal():
    r = copy.deepcopy(SPLIT)
    r["terminal_refusals"].append(dict(type="unattributed_overrun", block_id="nope", attempt=0,
                                       parent_block_id=None, item_id="GHOST", model="m1", level=1))
    return refresh(reg, r)

# C4: split forged from the initial stage (no whole_block retry ever existed)
def c4_split_from_initial(new_envelope):
    r = root_roster(reg)
    obs = [dict(block_id=b, status="completed", elapsed_s=0.9) for b in r["envelopes"][0]["blocks"]]
    r = sp.requeue_overrun(reg, r, 0, obs)         # one real event so root-only checks do not apply
    P = "m1:a:1:0"; e = r["envelopes"][1]           # unreported m1 envelope holding P at stage initial
    p = block(r, P); p["superseded"] = True         # retry_stage stays "initial", attempt 0
    e["blocks"].remove(P); e["voided_block_ids"].append(P)
    target = sp._new_envelope(r, "m1") if new_envelope else e["index"]
    for j, item in enumerate(p["items"]):
        sid = f"{P}:single:{j}"
        r["blocks"].append(dict(block_id=sid, model="m1", level=1, items=[item], predicted_item_s=[0.5], predicted_s=1.5,
                                attempt=1, retry_stage="single_problem", parent_block_id=P, superseded=False, late=False))
        r["placements"].append(dict(block_id=sid, attempt=1, stage="single_problem", reserved_s=1.5, envelope_index=target))
        r["envelopes"][target]["blocks"].append(sid)
    return refresh(reg, r)

# C5: live block at the terminal stage ceiling_violation, no terminal refusal
def c5_live_ceiling_violation():
    r = copy.deepcopy(SPLIT)
    block(r, S0)["retry_stage"] = "ceiling_violation"
    return refresh(reg, r)

# C6: event claims ownership of pack-time placements
def c6_event_placements():
    r = copy.deepcopy(SPLIT)
    r["events"][0]["placements"] = [i for i, p in enumerate(r["placements"]) if p["envelope_index"] > 0][:3]
    return refresh(reg, r)

# C7: a live single rewritten as an attempt-0 "initial" placement with a tiny reservation
def c7_single_stage_initial():
    r = copy.deepcopy(SPLIT)
    for p in r["placements"]:
        if p["block_id"] == S0: p["stage"] = "initial"; p["attempt"] = 0; p["reserved_s"] = 0.01
    block(r, S0)["attempt"] = 0; block(r, S0)["retry_stage"] = "initial"
    return refresh(reg, r)

# Refused controls
def c1_grandchild_same_env():                       # C1, grandchild sharing env 12 with S1
    r = copy.deepcopy(SPLIT); e = env_of(r, S0); block(r, S0)["superseded"] = True
    e["blocks"].remove(S0); e["voided_block_ids"].append(S0); gid = f"{S0}:single:0"
    r["blocks"].append(dict(block_id=gid, model="m1", level=1, items=["L1i0"], predicted_item_s=[0.5], predicted_s=1.5, attempt=3, retry_stage="single_problem", parent_block_id=S0, superseded=False, late=False))
    r["placements"].append(dict(block_id=gid, attempt=3, stage="single_problem", reserved_s=1.5, envelope_index=e["index"])); e["blocks"].append(gid)
    return refresh(reg, r)
def c2b_terminal_no_placement():                    # like C2b' but without repairing event indices
    r = copy.deepcopy(SPLIT); env_of(r, S1)["blocks"].remove(S1)
    r["placements"] = [p for p in r["placements"] if p["block_id"] != S1]
    r["terminal_refusals"].append(dict(type="ceiling_violation", block_id=S1, attempt=2, parent_block_id=WB, item_id="L1i1", model="m1", level=1))
    return refresh(reg, r)
def x1_parent_and_single_both_live():
    r = copy.deepcopy(SPLIT); r["envelopes"][11]["voided_block_ids"].remove(WB); r["envelopes"][11]["blocks"].append(WB); return refresh(reg, r)
def x2_single_live_twice():
    r = copy.deepcopy(SPLIT); t = sp._new_envelope(r, "m1")
    r["placements"].append(dict(block_id=S0, attempt=3, stage="single_problem", reserved_s=1.5, envelope_index=t)); r["envelopes"][t]["blocks"].append(S0); return refresh(reg, r)
def x3_terminal_plus_live():
    r = copy.deepcopy(SPLIT); r["terminal_refusals"].append(dict(type="ceiling_violation", block_id=S1, attempt=2, parent_block_id=WB, item_id="L1i1", model="m1", level=1)); return refresh(reg, r)
def x4_single_of_unsuperseded_parent():
    r = copy.deepcopy(SPLIT); block(r, WB)["superseded"] = False; return refresh(reg, r)
def x5_swapped_parent_items():
    r = root_roster(reg); a, b = block(r, "m8:a:1:0"), block(r, "m8:a:1:1"); a["items"], b["items"] = b["items"], a["items"]; return refresh(reg, r)
def x6_missing_single():
    r = copy.deepcopy(SPLIT); r["blocks"] = [b for b in r["blocks"] if b["block_id"] != S1]
    env_of(r, S1)["blocks"].remove(S1); r["placements"] = [p for p in r["placements"] if p["block_id"] != S1]; return refresh(reg, r)
def x7b_grandchild_single_not_superseded():
    r = c1b_grandchild_new_env(); block(r, S0)["superseded"] = False; return refresh(reg, r)

if __name__ == "__main__":
    for name, fn in [("C1'", c1b_grandchild_new_env), ("C2a", c2a_terminal_wrong_block), ("C2b'", c2b_terminal_no_placement_fixed),
                     ("C3", c3_phantom_terminal), ("C4 same env", lambda: c4_split_from_initial(False)), ("C4 new env", lambda: c4_split_from_initial(True)),
                     ("C5", c5_live_ceiling_violation), ("C6", c6_event_placements), ("C7", c7_single_stage_initial),
                     ("C1 same env", c1_grandchild_same_env), ("C2b unrepaired", c2b_terminal_no_placement),
                     ("X1", x1_parent_and_single_both_live), ("X2", x2_single_live_twice), ("X3", x3_terminal_plus_live),
                     ("X4", x4_single_of_unsuperseded_parent), ("X5", x5_swapped_parent_items), ("X6", x6_missing_single), ("X7b", x7b_grandchild_single_not_superseded)]:
        try: submit(reg, fn(), name)
        except Exception as exc: print(f"[{name}] CONSTRUCTOR ERROR {type(exc).__name__}: {exc}")
```

The base is a legal roster from `pack`, then a real sequence of `requeue_overrun` calls: keep-all on envelope 0, a culprit cut_off on envelope 1 that advances parent `m1:a:1:0` to whole_block, keep-all reports up to that retry, then a cut_off on it that splits it into two singles live in envelope 12.

## Accepted forgeries

| Id | `_seal` result | Rule violated |
|---|---|---|
| C1' | ACCEPTED, sha256 e3b1b3b9… | INV-12 |
| C2a | ACCEPTED, sha256 19f0e7a9… | INV-37, §2.8 |
| C2b' | ACCEPTED, sha256 4267e44d… | INV-37, §2.6 RD-3, §3.2 |
| C3 | ACCEPTED, sha256 ba747e15… | INV-37, §2.8, INV-11 ruled text |
| C4 (both variants) | ACCEPTED, e31f4be2… and 9e3a8142… | §2.4 `superseded`, §3.2 split, INV-36, INV-19 |
| C5 | ACCEPTED, sha256 a2a52784… | §3.2 advance row, RD-14, INV-37 |
| C6 | ACCEPTED, sha256 67075689… | RD-2, INV-34 |
| C7 | ACCEPTED, sha256 a5cb1058… | INV-23, INV-36, Q11 |

- **C1' chained single.** The single `m1:a:1:0:single:0` is marked `superseded`, voided, and a block `m1:a:1:0:single:0:single:0` with `parent_block_id` pointing at that single is placed live in a new envelope. INV-12 says a single's parent "exists, has the same model and level, contains the item at position j, and is superseded". Under the glossary (§0.4) a Parent is "a block created by `pack`; its `parent_block_id` is null" and a Single's `parent_block_id` "is its parent's id". This block's `parent_block_id` names a single, not a parent, and the single's `superseded: true` breaks §2.4 ("true if and only if the block is a `whole_block` retry that was split"). The seal's INV-12 pass looks the parent up in the block map without requiring `parent_block_id is None`, and its partition check only iterates over true parents, so a superseded single is never asked to have children.

- **C2a terminal refusal naming a foreign block.** Single 1 is voided and item `L1i1` gets a terminal refusal with `block_id "m8:a:5:4"`, `attempt 99`, `level 5`, `type "bogus_type"`. INV-37's predicate: "`(block_id, attempt)` names a voided placement of a block containing the item". No such placement exists. §2.8 restricts `type` to two values and `attempt` to "the attempt of that block's voided placement". The seal keys terminal refusals only by (model, item_id) and never reads the other five fields.

- **C2b' terminal item with no placement.** Single 1's only placement is deleted from the append-only list and a terminal refusal is added. INV-11's closed form is satisfied (LIVE 0, TERM 1) but INV-37 fails, RD-3 (placements list "holding every placement ever made") fails, and §3.2 requires each split single to be placed. The seal never checks that a terminal item's block ever held a placement.

- **C3 phantom terminal refusal.** A terminal refusal for item `GHOST`, which no registered level contains. The seal's conservation loop iterates only registered items, so a stray entry is never examined. §2.8 ("one entry per item") and INV-37 (a block containing the item must exist) are violated.

- **C4 split from the initial stage.** After one real event, parent `m1:a:1:0` at `retry_stage "initial"`, `attempt 0` is marked `superseded`, its pack-time placement is voided, and two singles are placed (same envelope, or a fresh one). INV-12's predicate as written is satisfied, but §2.4 (`superseded` iff a whole_block retry was split), §3.2 (split only on `whole_block` cut_off, singles' `attempt` = parent's latest + 1), INV-36 (no edge initial→split) and, for the same-envelope variant, INV-19 are violated. The seal never checks a superseded parent's stage or that it has a voided whole_block placement.

- **C5 live block at a terminal stage.** Single 0 keeps its live placement but `retry_stage` becomes `ceiling_violation`. §3.2: that advance has "no placement and no increment. One `terminal_refusals` entry". RD-14 treats a terminal refusal as the end of history. The seal only checks placement stages against the first four stages, not block stages against live state.

- **C6 event owns pack-time placements.** Event 0's `placements` list is rewritten to point at three pack-time placements. RD-2 says the list holds the indices of placements the event created. The seal only checks the targets are above the reporting index.

- **C7 single rewritten as an initial attempt.** Single 0's placement becomes `stage "initial"`, `attempt 0`, `reserved_s 0.01`. INV-23 (`reserved_s = predicted_s = worst`), INV-36 (a root holds only initial attempt-0 placements, attempts rise by 1 per placement) and Q11 are violated. Placement `stage`, `attempt` and `reserved_s` are never compared with the block.

For every accepted forgery, `_seal(reg, out)` without `finalize` also accepts the sealed output. `verify_executed_roster` refuses each with `inv_38` because replay re-derives the roster.

## Refused attempts

- **C1 in the shared envelope**: refused `inv_24: parent spread`, because the grandchild's `parent_block_id` differs from its envelope-mate's within level 1. Placing it alone bypasses this.
- **C2b without repairing event indices**: refused `inv_18: event placement target`, because deleting a placement shifted every later index.
- **X1 parent and single both live**: refused `inv_11` (derived-field refresh already raised "gate parent without full live positions").
- **X2 single live in two envelopes**: refused `inv_11`, same path.
- **X3 terminal refusal for a still-live single**: refused `inv_11: item conservation`.
- **X4 singles under a non-superseded parent**: refused `inv_12: single parent`.
- **X5 parent items swapped between k-slices**: refused `inv_10: parent formation and order`.
- **X6 one single deleted**: refused `inv_11`.
- **X7 / X7b grandchild whose "parent" single is not superseded**: refused `inv_24` in the shared envelope, `inv_12: single parent` in a fresh one.

The INV-10 formation check and the INV-11 closed form held against every direct attack I tried. The gaps are all around what the seal does not cross-check: terminal-refusal provenance, the parent-ness of a single's `parent_block_id`, the stage history behind `superseded`, and placement bookkeeping against the block.
