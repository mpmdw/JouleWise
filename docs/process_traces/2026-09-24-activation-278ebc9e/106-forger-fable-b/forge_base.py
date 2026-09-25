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
