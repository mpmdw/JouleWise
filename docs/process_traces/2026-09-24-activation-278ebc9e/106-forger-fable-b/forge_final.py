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
"""Forgery candidates against _seal(reg, roster, finalize=True). Run: python3 forge_candidates.py"""
import copy

reg = make_registration()
SPLIT, WB = split_roster(reg)          # legal roster: parent m1:a:1:0 split into two singles, live in env 12
S0, S1 = f"{WB}:single:0", f"{WB}:single:1"

def env_of(r, bid):
    return next(e for e in r["envelopes"] if bid in e["blocks"])

def block(r, bid):
    return next(b for b in r["blocks"] if b["block_id"] == bid)

# ---------- C1: chained single (a single's "parent" is itself a single) ----------
def c1_grandchild():
    r = copy.deepcopy(SPLIT)
    e = env_of(r, S0)
    s0 = block(r, S0)
    s0["superseded"] = True                       # a single marked superseded
    e["blocks"].remove(S0); e["voided_block_ids"].append(S0)
    gid = f"{S0}:single:0"
    r["blocks"].append(dict(block_id=gid, model="m1", level=1, items=["L1i0"], predicted_item_s=[0.5],
                            predicted_s=1.5, attempt=3, retry_stage="single_problem", parent_block_id=S0,
                            superseded=False, late=False))
    r["placements"].append(dict(block_id=gid, attempt=3, stage="single_problem", reserved_s=1.5, envelope_index=e["index"]))
    e["blocks"].append(gid)
    return refresh(reg, r)

# ---------- C2a: terminal refusal whose (block_id, attempt) names no voided placement ----------
def c2a_terminal_wrong_block():
    r = copy.deepcopy(SPLIT)
    e = env_of(r, S1)
    e["blocks"].remove(S1); e["voided_block_ids"].append(S1)      # S1 voided (looks like a ceiling_violation)
    r["terminal_refusals"].append(dict(type="bogus_type", block_id="m8:a:5:4", attempt=99,
                                       parent_block_id=None, item_id="L1i1", model="m1", level=5))
    return refresh(reg, r)

# ---------- C2b: terminal item whose block has NO placement at all ----------
def c2b_terminal_no_placement():
    r = copy.deepcopy(SPLIT)
    e = env_of(r, S1)
    e["blocks"].remove(S1)
    r["placements"] = [p for p in r["placements"] if p["block_id"] != S1]   # placement list no longer append-only
    r["terminal_refusals"].append(dict(type="ceiling_violation", block_id=S1, attempt=2,
                                       parent_block_id=WB, item_id="L1i1", model="m1", level=1))
    return refresh(reg, r)

# ---------- C3: phantom terminal refusal for an unregistered item ----------
def c3_phantom_terminal():
    r = copy.deepcopy(SPLIT)
    r["terminal_refusals"].append(dict(type="unattributed_overrun", block_id="nope", attempt=0,
                                       parent_block_id=None, item_id="GHOST", model="m1", level=1))
    return refresh(reg, r)

# ---------- C4: split forged from the initial stage (no whole_block retry ever existed) ----------
def c4_split_from_initial(new_envelope):
    r = root_roster(reg)
    obs = [dict(block_id=b, status="completed", elapsed_s=0.9) for b in r["envelopes"][0]["blocks"]]
    r = sp.requeue_overrun(reg, r, 0, obs)         # one real event so root-only checks do not apply
    P = "m1:a:1:0"; e = r["envelopes"][1]           # unreported m1 envelope holding P at stage initial
    p = block(r, P); p["superseded"] = True         # retry_stage stays "initial", attempt 0
    e["blocks"].remove(P); e["voided_block_ids"].append(P)
    if new_envelope:
        target = sp._new_envelope(r, "m1")
    else:
        target = e["index"]
    for j, item in enumerate(p["items"]):
        sid = f"{P}:single:{j}"
        r["blocks"].append(dict(block_id=sid, model="m1", level=1, items=[item], predicted_item_s=[0.5], predicted_s=1.5,
                                attempt=1, retry_stage="single_problem", parent_block_id=P, superseded=False, late=False))
        r["placements"].append(dict(block_id=sid, attempt=1, stage="single_problem", reserved_s=1.5, envelope_index=target))
        r["envelopes"][target]["blocks"].append(sid)
    return refresh(reg, r)

# ---------- C5: live block at the terminal stage ceiling_violation, no terminal refusal ----------
def c5_live_ceiling_violation():
    r = copy.deepcopy(SPLIT)
    block(r, S0)["retry_stage"] = "ceiling_violation"
    return refresh(reg, r)

# ---------- C6: event claims ownership of pack-time placements ----------
def c6_event_placements():
    r = copy.deepcopy(SPLIT)
    r["events"][0]["placements"] = [i for i, p in enumerate(r["placements"]) if p["envelope_index"] > 0][:3]
    return refresh(reg, r)

# ---------- C7: superseded parent whose singles have swapped attempts/placement stages ----------
def c7_single_stage_initial():
    r = copy.deepcopy(SPLIT)
    for p in r["placements"]:
        if p["block_id"] == S0: p["stage"] = "initial"; p["attempt"] = 0; p["reserved_s"] = 0.01
    block(r, S0)["attempt"] = 0; block(r, S0)["retry_stage"] = "initial"
    return refresh(reg, r)

# ---------- Controls expected to be refused ----------
def x1_parent_and_single_both_live():
    r = copy.deepcopy(SPLIT)
    r["envelopes"][11]["voided_block_ids"].remove(WB); r["envelopes"][11]["blocks"].append(WB)
    return refresh(reg, r)

def x2_single_live_twice():
    r = copy.deepcopy(SPLIT)
    t = sp._new_envelope(r, "m1")
    r["placements"].append(dict(block_id=S0, attempt=3, stage="single_problem", reserved_s=1.5, envelope_index=t))
    r["envelopes"][t]["blocks"].append(S0)
    return refresh(reg, r)

def x3_terminal_plus_live():
    r = copy.deepcopy(SPLIT)
    r["terminal_refusals"].append(dict(type="ceiling_violation", block_id=S1, attempt=2, parent_block_id=WB, item_id="L1i1", model="m1", level=1))
    return refresh(reg, r)

def x4_single_of_unsuperseded_parent():
    r = copy.deepcopy(SPLIT)
    block(r, WB)["superseded"] = False
    return refresh(reg, r)

def x5_parent_moved_between_cells():
    r = root_roster(reg)
    a, b = block(r, "m8:a:1:0"), block(r, "m8:a:1:1")
    a["items"], b["items"] = b["items"], a["items"]
    return refresh(reg, r)

def x6_missing_single():
    r = copy.deepcopy(SPLIT)
    r["blocks"] = [b for b in r["blocks"] if b["block_id"] != S1]
    env_of(r, S1)["blocks"].remove(S1); r["placements"] = [p for p in r["placements"] if p["block_id"] != S1]
    return refresh(reg, r)

def x7_grandchild_without_superseding_single():
    r = copy.deepcopy(SPLIT)
    e = env_of(r, S0); gid = f"{S0}:single:0"
    e["blocks"].remove(S0); e["voided_block_ids"].append(S0)
    r["blocks"].append(dict(block_id=gid, model="m1", level=1, items=["L1i0"], predicted_item_s=[0.5], predicted_s=1.5, attempt=3, retry_stage="single_problem", parent_block_id=S0, superseded=False, late=False))
    r["placements"].append(dict(block_id=gid, attempt=3, stage="single_problem", reserved_s=1.5, envelope_index=e["index"]))
    e["blocks"].append(gid)
    return refresh(reg, r)

if __name__ == "__main__":
    for name, fn in [("C1 grandchild single", c1_grandchild), ("C2a terminal wrong block", c2a_terminal_wrong_block),
                     ("C2b terminal no placement", c2b_terminal_no_placement), ("C3 phantom terminal", c3_phantom_terminal),
                     ("C4 split-from-initial same env", lambda: c4_split_from_initial(False)),
                     ("C4' split-from-initial new env", lambda: c4_split_from_initial(True)),
                     ("C5 live ceiling_violation", c5_live_ceiling_violation), ("C6 event placements", c6_event_placements),
                     ("C7 single stage initial", c7_single_stage_initial),
                     ("X1 parent+single live", x1_parent_and_single_both_live), ("X2 single live twice", x2_single_live_twice),
                     ("X3 terminal+live", x3_terminal_plus_live), ("X4 unsuperseded parent", x4_single_of_unsuperseded_parent),
                     ("X5 swapped parent items", x5_parent_moved_between_cells), ("X6 missing single", x6_missing_single),
                     ("X7 grandchild, single not superseded", x7_grandchild_without_superseding_single)]:
        try:
            submit(reg, fn(), name)
        except Exception as exc:
            print(f"[{name}] CONSTRUCTOR ERROR {type(exc).__name__}: {exc}")

# ---------- C1' : grandchild single placed in its own new envelope ----------
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

# ---------- C2b' : terminal item whose block has NO placement; event indices repaired ----------
def c2b_terminal_no_placement_fixed():
    r = copy.deepcopy(SPLIT)
    e = env_of(r, S1); e["blocks"].remove(S1)
    gone = next(i for i, p in enumerate(r["placements"]) if p["block_id"] == S1)
    del r["placements"][gone]
    for ev in r["events"]:
        ev["placements"] = [i - (i > gone) for i in ev["placements"] if i != gone]
    r["terminal_refusals"].append(dict(type="ceiling_violation", block_id=S1, attempt=2, parent_block_id=WB, item_id="L1i1", model="m1", level=1))
    return refresh(reg, r)

def x7b_grandchild_new_env_single_not_superseded():
    r = c1b_grandchild_new_env(); block(r, S0)["superseded"] = False
    return refresh(reg, r)
