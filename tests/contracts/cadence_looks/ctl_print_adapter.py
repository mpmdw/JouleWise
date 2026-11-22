"""Translate the frozen toy fixture to the controls print validation seam."""

import json

from joulewise.cadence_looks import controls_print as controls

from . import synthetic_acceptance as vectors


REASONS = {
    controls.Refusal.BINDING: "freeze or evidence binding",
    controls.Refusal.PILOT_HAND_READ: "pilot hand-read",
    controls.Refusal.SPLIT_HAND_READ: "split hand-read",
    controls.Refusal.PRE_READ_FREEZE: "pre-read freeze",
    controls.Refusal.SCRIPT_DELIVERY: "toy script",
}


def _plan(row):
    leaf = row["instrument"]
    return controls.BlindPlan(
        identity=controls.LookIdentity(row["look"], row["kit"], row["kit_sha"], row["runner"]),
        master_seed=row["master_seed"],
        spans=tuple(tuple(span) for span in row["layout"]),
        pilot_pass_order=row["pilot_pass_seq"],
        remainder_start_order=row["remainder_seq"],
        split_hand_pass=row["split_hand_pass"],
        freeze_order=row["freeze_seq"],
        reservation_order=row["first_open_seq"],
        instrument=controls.InstrumentLeaf(
            leaf["look_id"], leaf["manifest_sha"], leaf["kit_id"], leaf["leg"],
            leaf["channel"], leaf["window_s"], leaf["print_id"],
        ),
        manifest_sha256=row["manifest_sha"],
        code_sha256=row["code_sha"],
        schema_sha256=row["schema_sha"],
    )


def _leg(row):
    return controls.LegBinding(*row["identity"], row["role"], row["reference"])


def _episode(work):
    return controls.Episode(
        kind=work["kind"],
        steps=tuple("turn" if step == "visible" else step for step in work["steps"]),
        delivery=controls.Delivery(tuple(work["visible"]), work["hidden_tokens"],
                                   work["cpu_s"], work["gap_s"], work["recovery_s"]),
        start_contexts=tuple(work["start_ctx"]),
        seed=work["seed"],
        prompt_sha256=work["prompt"],
    )


def _validate(committed, candidate):
    if candidate["plan"].keys() != committed["plan"].keys():
        raise ValueError("plan shape")
    if candidate["plan"]["instrument"].keys() != committed["plan"]["instrument"].keys():
        raise controls.ControlsRefusal(controls.Refusal.BINDING)
    plan = _plan(candidate["plan"])
    controls.validate_plan(plan, _plan(committed["plan"]))
    anchors = committed["legs"]
    rows = candidate["legs"]
    controls.validate_roster(plan.identity, [(row["leg"], _leg(row)) for row in rows],
                             {leg: _leg(row) for leg, row in anchors.items()})

    episodes = []
    for row, kind in zip(rows, vectors.KINDS, strict=True):
        leg = row["leg"]
        work = row["work"]
        payload = json.dumps(work, sort_keys=True, separators=(",", ":")).encode("utf-8")
        controls.validate_script_pin(payload, anchors[leg]["script_sha"])
        episode = _episode(work)
        controls.validate_episode(episode, kind=kind, envelopes=row["logged"])
        episodes.append(episode)

    split = next(episode for episode in episodes if episode.kind == "split")
    plain = next(episode for episode in episodes if episode.kind == "plain")
    controls.compare_pair(split, plain)
    for episode, hidden, cpu in zip(episodes, vectors.HIDDEN, vectors.BURN, strict=True):
        kind = episode.kind
        prescription = controls.Delivery(vectors.CAPS[kind], hidden, cpu,
                                         10 if kind == "split" else 0, 600)
        controls.validate_complete_delivery(episode.delivery, prescription)

    controls.encode_alignment_projection(candidate["private"], qualifier_ran=committed["qualifier_ran"])
    controls.encode_public_projection(candidate["public"], committed["public"])


def check_fixture(committed, candidate):
    try:
        _validate(committed, candidate)
    except controls.ControlsRefusal as error:
        message = REASONS.get(error.reason, error.reason.name.lower().replace("_", " "))
        raise ValueError(message) from error
