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
    """Report envelopes [next .. upto] as all completed within bound."""
    while True:
        pending = next((e["index"] for e in r["envelopes"] if e["kind"] == "loaded" and e["observations"] is None), None)
        if pending is None or pending > upto:
            return r
        obs = [dict(block_id=b, status="completed", elapsed_s=1.0) for b in r["envelopes"][pending]["blocks"]]
        r = requeue_overrun(reg, r, pending, obs)

def split_roster():
    """Legal roster where parent big-8b:m4:5:0 was advanced to whole_block then split into singles."""
    reg, r = root()
    P = f"{M8}:{ARM}:5:0"
    e0 = r["envelopes"][0]["blocks"]
    assert P in e0
    obs = [dict(block_id=b, status=("cut_off" if b == P else "completed"), elapsed_s=(6.0 if b == P else 1.0)) for b in e0]
    r = requeue_overrun(reg, r, 0, obs)          # P -> whole_block, new envelope at the end
    wb = next(p for p in reversed(r["placements"]) if p["block_id"] == P)["envelope_index"]
    r = report_all_ok(reg, r, wb - 1)
    r = requeue_overrun(reg, r, wb, [dict(block_id=P, status="cut_off", elapsed_s=30.0)])  # split
    return reg, r, P

def terminal_roster():
    """Legal roster where parent big-8b:m4:5:0 ended in unattributed_overrun (no culprit in the event)."""
    reg, r = root()
    P = f"{M8}:{ARM}:5:0"
    e0 = r["envelopes"][0]["blocks"]
    obs = [dict(block_id=b, status=("not_started" if b == P else "completed"), elapsed_s=(None if b == P else 1.0)) for b in e0]
    r = requeue_overrun(reg, r, 0, obs)
    return reg, r, P

def reseal(reg, r):
    """Refresh derived fields, clear the seal, and submit to _seal(finalize=True)."""
    r = copy.deepcopy(r)
    try:
        r["planned_spread_shortfall"], r["drift_lever_slots"] = _checked_derived(reg, r)
    except PackingRefusal:
        pass  # leave stale derived values; _seal will report its own refusal
    r["sha256"] = None
    try:
        out = _seal(reg, r, finalize=True)
        return "ACCEPTED", out
    except PackingRefusal as exc:
        return f"REFUSED {exc}", None
