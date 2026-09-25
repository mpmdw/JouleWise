"""Sealed scored reducer: one executed roster plus score rows and capture windows."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re

import joulewise.scored_registration as sr
from joulewise.scored_packer import executed_status, verify_executed_roster

STOP_REASONS = {"stop": False, "length": True}
ROW_SCHEMA = "joulewise.scored_row.v1"
WINDOW_SCHEMA = "joulewise.scored_window.v1"
REDUCTION_SCHEMA = "joulewise.scored_reduction.v1"
ROW_KEYS = frozenset("schema registration_sha256 roster_sha256 scorer_id block_id attempt item_id prompt_tokens generated_tokens stop_reason extracted_answer scorer_match".split())
WINDOW_KEYS = frozenset("schema registration_sha256 roster_sha256 block_id attempt envelope_index gross_j bundle_sha256 energy_bound_terms_j".split())
ANCHOR_KEY = "E_clock_anchor_shift_bound_j"
ENERGY_MAX_J = 10**12
INT_MAX = 2**53
REDUCTION_CODES = (
    "reduce_input",
    "window_keys", "window_domain", "window_unknown", "window_binding", "window_duplicate",
    "window_envelope", "window_unstarted", "anchor_energy_envelope_unrecorded", "missing_live_window",
    "row_keys", "row_domain", "row_stop_reason_unknown", "row_scorer", "row_unknown", "row_binding",
    "row_duplicate", "row_unstarted", "row_missing", "row_tokens_over_cap", "row_cap_disagreement",
    "internal_disagreement",
)
_HEX = re.compile(r"[0-9a-f]{64}\Z")


class ReductionRefusal(ValueError):
    def __init__(self, code, detail=""):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _need(ok, code, detail=""):
    if not ok:
        raise ReductionRefusal(code, detail)


def _text(v):
    return type(v) is str and bool(v)


def _hex(v):
    return type(v) is str and _HEX.fullmatch(v) is not None


def _int(v):
    return type(v) is int and 0 <= v <= INT_MAX


def _num(v):
    return (type(v) is int or (type(v) is float and math.isfinite(v))) and v <= ENERGY_MAX_J


def _canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _in_force(roster, envelope_index):
    digest = roster["registered_sha256"]
    for event in roster["events"]:
        if event["envelope_index"] < envelope_index:
            digest = event["sha256"]
    return digest


def _classify(roster):
    """Placement key -> (placement, class, observation status), in placement order."""
    terminal_keys = {(t["block_id"], t["attempt"]) for t in roster["terminal_refusals"]}
    keys = {}
    for p in roster["placements"]:
        key = (p["block_id"], p["attempt"])
        envelope = roster["envelopes"][p["envelope_index"]]
        if p["block_id"] in envelope["blocks"]:
            kind = "live"
        elif key in terminal_keys:
            kind = "terminal"
        else:
            kind = "voided"
        status = next(o["status"] for o in envelope["observations"] if o["block_id"] == p["block_id"])
        keys[key] = (p, kind, status)
    return keys


def _check_window(w, registration, roster, keys, seen):
    _need(type(w) is dict and set(w) == WINDOW_KEYS, "window_keys", "window key set")
    anchor = w["energy_bound_terms_j"]
    _need(w["schema"] == WINDOW_SCHEMA and type(w["schema"]) is str
          and _hex(w["registration_sha256"]) and _hex(w["roster_sha256"])
          and _text(w["block_id"]) and _int(w["attempt"]) and _int(w["envelope_index"])
          and _num(w["gross_j"]) and w["gross_j"] > 0 and _hex(w["bundle_sha256"])
          and type(anchor) is dict and set(anchor) == {ANCHOR_KEY}
          and (anchor[ANCHOR_KEY] is None or (_num(anchor[ANCHOR_KEY]) and anchor[ANCHOR_KEY] >= 0)),
          "window_domain", "window field domain")
    key = (w["block_id"], w["attempt"])
    _need(key in keys, "window_unknown", repr(key))
    placement, _, status = keys[key]
    _need(w["registration_sha256"] == registration.digest
          and w["roster_sha256"] == _in_force(roster, w["envelope_index"]), "window_binding", repr(key))
    _need(key not in seen, "window_duplicate", repr(key))
    seen.add(key)
    _need(w["envelope_index"] == placement["envelope_index"], "window_envelope", repr(key))
    _need(status != "not_started", "window_unstarted", repr(key))
    return key


def _check_row(r, registration, g, roster, keys, blocks, cap_tokens_arm, seen):
    _need(type(r) is dict and set(r) == ROW_KEYS, "row_keys", "row key set")
    _need(r["schema"] == ROW_SCHEMA and type(r["schema"]) is str
          and _hex(r["registration_sha256"]) and _hex(r["roster_sha256"])
          and _text(r["scorer_id"]) and _text(r["block_id"]) and _int(r["attempt"])
          and _text(r["item_id"]) and _int(r["prompt_tokens"]) and _int(r["generated_tokens"])
          and _text(r["stop_reason"])
          and (r["extracted_answer"] is None or _text(r["extracted_answer"]))
          and type(r["scorer_match"]) is bool
          and (not r["scorer_match"] or r["extracted_answer"] is not None),
          "row_domain", "row field domain or coherence")
    _need(r["stop_reason"] in STOP_REASONS, "row_stop_reason_unknown", r["stop_reason"])
    _need(r["scorer_id"] == g["scorer_id"], "row_scorer", r["scorer_id"])
    key = (r["block_id"], r["attempt"])
    _need(key in keys and r["item_id"] in blocks[r["block_id"]]["items"], "row_unknown", repr(key + (r["item_id"],)))
    _need(r["registration_sha256"] == registration.digest and r["roster_sha256"] == roster["sha256"],
          "row_binding", repr(key + (r["item_id"],)))
    row_key = key + (r["item_id"],)
    _need(row_key not in seen, "row_duplicate", repr(row_key))
    seen.add(row_key)
    _need(keys[key][2] != "not_started", "row_unstarted", repr(row_key))
    _need(r["generated_tokens"] <= cap_tokens_arm, "row_tokens_over_cap", repr(row_key))
    _need(STOP_REASONS[r["stop_reason"]] == (r["generated_tokens"] >= cap_tokens_arm),
          "row_cap_disagreement", repr(row_key))
    return row_key


def _derived(row, cap_tokens_arm):
    capped = row["generated_tokens"] >= cap_tokens_arm
    return capped, row["scorer_match"] and not capped


def reduce(registration, roster, predicted_decode_s, score_rows, capture_windows):
    verify_executed_roster(registration, roster, predicted_decode_s)
    _need(type(score_rows) is list and type(capture_windows) is list, "reduce_input", "score_rows and capture_windows must be lists")
    g = registration.to_mapping()
    arm = g["arm"]
    cap_tokens_arm = g["cap_tokens"][arm]
    models = (g["role_to_model_id"]["8B"], g["role_to_model_id"]["1.7B"])
    blocks = {b["block_id"]: b for b in roster["blocks"]}
    keys = _classify(roster)

    seen = set()
    window_by_key = {}
    for w in capture_windows:
        window_by_key[_check_window(w, registration, roster, keys, seen)] = w
    seen = set()
    row_by_key = {}
    for r in score_rows:
        row_by_key[_check_row(r, registration, g, roster, keys, blocks, cap_tokens_arm, seen)] = r

    live = [key for key, (_, kind, _) in keys.items() if kind == "live"]
    for key in live:
        _need(key in window_by_key, "missing_live_window", repr(key))
    for w in capture_windows:
        key = (w["block_id"], w["attempt"])
        _need(keys[key][1] != "live" or w["energy_bound_terms_j"][ANCHOR_KEY] is not None,
              "anchor_energy_envelope_unrecorded", repr(key))
    for key in live:
        for item in blocks[key[0]]["items"]:
            _need(key + (item,) in row_by_key, "row_missing", repr(key + (item,)))

    status = copy.deepcopy(executed_status(registration, roster, predicted_decode_s, frozenset(live)))

    # Items: counted placement or terminal record per (model, item).
    terminal_by_item = {(t["model"], t["item_id"]): t for t in roster["terminal_refusals"]}
    counted = {}
    for key in live:
        block = blocks[key[0]]
        for item in block["items"]:
            counted[(block["model"], item)] = key
    superseded = [r for r in score_rows if keys[(r["block_id"], r["attempt"])][1] != "live"]
    root_of = {}
    for b in roster["blocks"]:
        if b["parent_block_id"] is None:
            for item in b["items"]:
                root_of[(b["model"], item)] = b["block_id"]
    partner = {models[0]: models[1], models[1]: models[0]}

    items = []
    for model in models:
        for level in sr.LEVELS:
            for item_id in g["item_ids_by_level"][str(level)]:
                entry = dict(model=model, level=level, item_id=item_id, parent_block_id=root_of[(model, item_id)])
                key = counted.get((model, item_id))
                if key is None:
                    t = terminal_by_item[(model, item_id)]
                    entry.update(outcome=t["type"], block_id=t["block_id"], attempt=t["attempt"],
                                 envelope_index=None, retry_stage=None, late=None, prompt_tokens=None,
                                 generated_tokens=None, stop_reason=None, capped=None, malformed=None,
                                 scorer_match=None, correct=None, extracted_answer=None,
                                 attempt_divergence=None, paired=None)
                else:
                    placement = keys[key][0]
                    row = row_by_key[key + (item_id,)]
                    capped, correct = _derived(row, cap_tokens_arm)
                    divergence = any(_derived(old, cap_tokens_arm)[1] != correct for old in superseded
                                     if old["item_id"] == item_id and blocks[old["block_id"]]["model"] == model)
                    entry.update(outcome="counted", block_id=key[0], attempt=key[1],
                                 envelope_index=placement["envelope_index"], retry_stage=placement["stage"],
                                 late=blocks[key[0]]["late"], prompt_tokens=row["prompt_tokens"],
                                 generated_tokens=row["generated_tokens"], stop_reason=row["stop_reason"],
                                 capped=capped, malformed=row["extracted_answer"] is None,
                                 scorer_match=row["scorer_match"], correct=correct,
                                 extracted_answer=row["extracted_answer"], attempt_divergence=divergence,
                                 paired=(partner[model], item_id) in counted)
                items.append(entry)
    item_of = {(i["model"], i["item_id"]): i for i in items}

    counted_windows = []
    for key in live:
        w = copy.deepcopy(window_by_key[key])
        w["item_ids"] = list(blocks[key[0]]["items"])
        counted_windows.append(w)
    uncounted_windows = []
    for w in capture_windows:
        kind = keys[(w["block_id"], w["attempt"])][1]
        if kind != "live":
            uncounted_windows.append(dict(copy.deepcopy(w), reason=kind))

    # Parents: energy once per counted window; position item-weighted.
    parents = []
    for b in roster["blocks"]:
        if b["parent_block_id"] is not None:
            continue
        mine = [item_of[(b["model"], item)] for item in b["items"]]
        counted_items = [i for i in mine if i["outcome"] == "counted"]
        window_keys = [key for key in live if (blocks[key[0]]["parent_block_id"] or key[0]) == b["block_id"]]
        indices = [i["envelope_index"] for i in counted_items]
        parents.append(dict(
            parent_block_id=b["block_id"], model=b["model"], level=b["level"], n_items=len(b["items"]),
            counted_item_ids=[i["item_id"] for i in counted_items],
            unpaired_item_ids=[i["item_id"] for i in counted_items if not i["paired"]],
            window_keys=[[k[0], k[1]] for k in window_keys],
            g_j=math.fsum(window_by_key[k]["gross_j"] for k in window_keys), k=len(window_keys),
            fully_counted=len(counted_items) == len(b["items"]),
            position=sum(indices) / len(indices) if indices else None,
        ))

    cells = {}
    for model in models:
        for level in sr.LEVELS:
            name = f"{model}:{level}"
            mine = [i for i in items if i["model"] == model and i["level"] == level]
            counted_items = [i for i in mine if i["outcome"] == "counted"]
            paired = [i for i in counted_items if i["paired"]]
            n = len(paired)
            n_capped = sum(i["capped"] for i in paired)
            stages = {}
            for i in paired:
                stages[i["retry_stage"]] = stages.get(i["retry_stage"], 0) + 1
            cell_parents = [p for p in parents if p["model"] == model and p["level"] == level]
            full = [p for p in cell_parents if p["fully_counted"]]
            envelopes = {keys[(k[0], k[1])][0]["envelope_index"] for p in full for k in p["window_keys"]}
            cells[name] = dict(
                model=model, level=level, n_items=len(mine), n_counted=len(counted_items), n=n,
                n_correct=sum(i["correct"] for i in paired), n_capped=n_capped,
                n_malformed=sum(i["malformed"] for i in paired),
                prompt_tokens=sum(i["prompt_tokens"] for i in paired),
                generated_tokens=sum(i["generated_tokens"] for i in paired),
                gross_j=math.fsum(window_by_key[key]["gross_j"] for key in live
                                  if blocks[key[0]]["model"] == model and blocks[key[0]]["level"] == level),
                k24_dropped=[dict(item_id=i["item_id"], partner_outcome=item_of[(partner[model], i["item_id"])]["outcome"])
                             for i in counted_items if not i["paired"]],
                uncounted={kind: sum(i["outcome"] == kind for i in mine)
                           for kind in ("ceiling_violation", "unattributed_overrun")},
                retry_stage_counts=stages,
                cap_bound=None if n == 0 else (n_capped / n) > sr.CAP_BOUND_FRACTION,
                spread_exceeded=status["spread_exceeded"].get(name),
                fully_counted_parents=len(full), distinct_envelopes=len(envelopes),
            )
    for name, cell in cells.items():
        expected = cell["fully_counted_parents"] < sr.MIN_PARENT_BLOCKS or cell["distinct_envelopes"] < sr.MIN_ENVELOPES
        _need(cell["spread_exceeded"] is expected, "internal_disagreement", name)

    max_gap = registration.max_gap
    levels = {str(level): dict(executed_drift_lever_slots=status["executed_drift_lever_slots"][str(level)],
                               drift_exceeded=status["drift_exceeded"][str(level)], max_gap=max_gap)
              for level in sr.LEVELS}

    terminal_refusals = []
    for t in roster["terminal_refusals"]:
        key = (t["block_id"], t["attempt"])
        gross = window_by_key[key]["gross_j"] if t["type"] == "ceiling_violation" and key in window_by_key else None
        terminal_refusals.append(dict(copy.deepcopy(t), window_key=[key[0], key[1]], gross_j=gross))

    out = dict(
        schema=REDUCTION_SCHEMA, registration_sha256=registration.digest, roster_sha256=roster["sha256"],
        registered_sha256=roster["registered_sha256"], scorer_id=g["scorer_id"], mode=g["mode"],
        claim_ready=roster["claim_ready"], items=items, parents=parents, cells=cells, levels=levels,
        counted_windows=counted_windows, uncounted_windows=uncounted_windows,
        terminal_refusals=terminal_refusals, superseded_rows=copy.deepcopy(superseded),
        executed_status=status,
    )
    out["sha256"] = hashlib.sha256(_canon(out)).hexdigest()
    return out
