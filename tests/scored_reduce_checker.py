"""Independent stdlib oracle for the sealed A292 reducer wire contract.

No production import is permitted here.  A refusal candidate is represented as
``{"refusal_code": code, "detail": detail}``; a successful candidate is the
reduction mapping.  Violations are plain ``{code, detail}`` mappings.
"""
from __future__ import annotations

import hashlib
import json
import math
import re

from tests.scored_roster_checker import check_executed


ROW_KEYS = frozenset("schema registration_sha256 roster_sha256 scorer_id block_id attempt item_id prompt_tokens generated_tokens stop_reason extracted_answer scorer_match".split())
WINDOW_KEYS = frozenset("schema registration_sha256 roster_sha256 block_id attempt envelope_index gross_j bundle_sha256 energy_bound_terms_j".split())
OUTPUT_KEYS = frozenset("schema registration_sha256 roster_sha256 registered_sha256 scorer_id mode claim_ready items parents cells levels counted_windows uncounted_windows terminal_refusals superseded_rows executed_status sha256".split())
ITEM_KEYS = frozenset("model level item_id parent_block_id outcome block_id attempt envelope_index retry_stage late prompt_tokens generated_tokens stop_reason capped malformed scorer_match correct extracted_answer attempt_divergence paired".split())
PARENT_KEYS = frozenset("parent_block_id model level n_items counted_item_ids unpaired_item_ids window_keys g_j k fully_counted position".split())
CELL_KEYS = frozenset("model level n_items n_counted n n_correct n_capped n_malformed prompt_tokens generated_tokens gross_j k24_dropped uncounted retry_stage_counts cap_bound spread_exceeded fully_counted_parents distinct_envelopes".split())
HEX = re.compile(r"[0-9a-f]{64}\Z")
STOP_REASONS = {"stop": False, "length": True}
CAP_BOUND_FRACTION = 1 / 5  # checked against the supplied contract, never imported


def _sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _integer(value):
    return type(value) is int and value >= 0


def _string(value):
    return type(value) is str and bool(value)


def _hex(value):
    return type(value) is str and HEX.fullmatch(value) is not None


def _violation(code, detail):
    return [{"code": code, "detail": str(detail)}]


def _key(record):
    return record["block_id"], record["attempt"]


def _in_force(roster, index):
    digest = roster["registered_sha256"]
    for event in roster["events"]:
        if event["envelope_index"] < index:
            digest = event["sha256"]
    return digest


def _row_domain(row):
    return (row["schema"] == "joulewise.scored_row.v1"
            and _hex(row["registration_sha256"]) and _hex(row["roster_sha256"])
            and all(_string(row[k]) for k in ("scorer_id", "block_id", "item_id", "stop_reason"))
            and all(_integer(row[k]) for k in ("attempt", "prompt_tokens", "generated_tokens"))
            and (row["extracted_answer"] is None or _string(row["extracted_answer"]))
            and type(row["scorer_match"]) is bool
            and (not row["scorer_match"] or row["extracted_answer"] is not None))


def _window_domain(window):
    terms = window["energy_bound_terms_j"]
    anchor_ok = (type(terms) is dict and set(terms) == {"E_clock_anchor_shift_bound_j"}
                 and (terms["E_clock_anchor_shift_bound_j"] is None
                      or (_number(terms["E_clock_anchor_shift_bound_j"])
                          and terms["E_clock_anchor_shift_bound_j"] >= 0)))
    return (window["schema"] == "joulewise.scored_window.v1"
            and _hex(window["registration_sha256"]) and _hex(window["roster_sha256"])
            and _hex(window["bundle_sha256"]) and _string(window["block_id"])
            and _integer(window["attempt"]) and _integer(window["envelope_index"])
            and _number(window["gross_j"]) and window["gross_j"] > 0 and anchor_ok)


def _expected(g, roster, rows, windows, live, status):
    """Re-derive every science output from items and accepted placement windows."""
    blocks = {b["block_id"]: b for b in roster["blocks"]}
    placements = {_key(p): p for p in roster["placements"]}
    window_by_key = {_key(w): w for w in windows}
    row_by_item = {(_key(row), row["item_id"]): row for row in rows}
    terminal = {(t["model"], t["item_id"]): t for t in roster["terminal_refusals"]}
    live_owner = {}
    for key in live:
        b = blocks[key[0]]
        for item in b["items"]:
            live_owner[(b["model"], item)] = key
    superseded = [row for row in rows if _key(row) not in live]
    roles = (g["role_to_model_id"]["8B"], g["role_to_model_id"]["1.7B"])
    cap_tokens_arm = g["cap_tokens"][g["arm"]]
    items = []
    for model in roles:
        for level in range(1, 6):
            for item_id in g["item_ids_by_level"][str(level)]:
                owner = (model, item_id)
                if owner in terminal:
                    t = terminal[owner]
                    parent_id = t["parent_block_id"] or t["block_id"]
                    item = dict(model=model, level=level, item_id=item_id,
                                parent_block_id=parent_id, outcome=t["type"],
                                block_id=t["block_id"], attempt=t["attempt"],
                                envelope_index=None, retry_stage=None, late=None,
                                prompt_tokens=None, generated_tokens=None,
                                stop_reason=None, capped=None, malformed=None,
                                scorer_match=None, correct=None, extracted_answer=None,
                                attempt_divergence=None, paired=None)
                else:
                    key = live_owner[owner]
                    block = blocks[key[0]]
                    placement = placements[key]
                    row = row_by_item[(key, item_id)]
                    capped = row["generated_tokens"] >= cap_tokens_arm
                    correct = row["scorer_match"] and not capped
                    prior = [r for r in superseded if blocks[r["block_id"]]["model"] == model
                             and r["item_id"] == item_id]
                    divergent = any((r["scorer_match"] and r["generated_tokens"] < cap_tokens_arm)
                                    != correct for r in prior)
                    item = dict(model=model, level=level, item_id=item_id,
                                parent_block_id=block["parent_block_id"] or block["block_id"],
                                outcome="counted", block_id=key[0], attempt=key[1],
                                envelope_index=placement["envelope_index"],
                                retry_stage=placement["stage"], late=block["late"],
                                prompt_tokens=row["prompt_tokens"],
                                generated_tokens=row["generated_tokens"],
                                stop_reason=row["stop_reason"], capped=capped,
                                malformed=row["extracted_answer"] is None,
                                scorer_match=row["scorer_match"], correct=correct,
                                extracted_answer=row["extracted_answer"],
                                attempt_divergence=divergent, paired=False)
                items.append(item)
    by_owner = {(i["model"], i["item_id"]): i for i in items}
    for item in items:
        if item["outcome"] == "counted":
            other = roles[1] if item["model"] == roles[0] else roles[0]
            item["paired"] = by_owner[(other, item["item_id"])]["outcome"] == "counted"
    counted_windows = []
    for placement in roster["placements"]:
        key = _key(placement)
        if key in live:
            block = blocks[key[0]]
            counted_windows.append(dict(window_by_key[key], item_ids=list(block["items"])))
    uncounted_windows = []
    terminal_keys = {(_key(t)) for t in roster["terminal_refusals"]}
    for window in windows:
        key = _key(window)
        if key not in live:
            uncounted_windows.append(dict(window, reason="terminal" if key in terminal_keys else "voided"))
    terminal_refusals = []
    for t in roster["terminal_refusals"]:
        key = _key(t)
        gross = window_by_key[key]["gross_j"] if t["type"] == "ceiling_violation" and key in window_by_key else None
        terminal_refusals.append(dict(t, window_key=list(key), gross_j=gross))
    parents = []
    for block in roster["blocks"]:
        if block["parent_block_id"] is not None:
            continue
        members = [by_owner[(block["model"], item_id)] for item_id in block["items"]]
        counted = [item for item in members if item["outcome"] == "counted"]
        keys = list(dict.fromkeys((item["block_id"], item["attempt"]) for item in counted))
        keys.sort(key=lambda key: roster["placements"].index(placements[key]))
        parents.append(dict(parent_block_id=block["block_id"], model=block["model"],
                            level=block["level"], n_items=len(members),
                            counted_item_ids=[item["item_id"] for item in counted],
                            unpaired_item_ids=[item["item_id"] for item in counted if not item["paired"]],
                            window_keys=[list(key) for key in keys],
                            g_j=math.fsum(window_by_key[key]["gross_j"] for key in keys),
                            k=len(keys), fully_counted=len(counted) == len(members),
                            position=(math.fsum(item["envelope_index"] for item in counted) / len(counted)
                                      if counted else None)))
    cells = {}
    for model in roles:
        for level in range(1, 6):
            members = [item for item in items if item["model"] == model and item["level"] == level]
            counted = [item for item in members if item["outcome"] == "counted"]
            paired = [item for item in counted if item["paired"]]
            cp = [p for p in parents if p["model"] == model and p["level"] == level and p["fully_counted"]]
            occupied = {placements[tuple(key)]["envelope_index"] for p in cp for key in p["window_keys"]}
            stage_counts = {stage: sum(item["retry_stage"] == stage for item in paired)
                            for stage in {item["retry_stage"] for item in paired}}
            stage_counts = {stage: count for stage, count in stage_counts.items() if count}
            dropped = []
            for item in counted:
                if not item["paired"]:
                    other = roles[1] if model == roles[0] else roles[0]
                    dropped.append(dict(item_id=item["item_id"], partner_outcome=by_owner[(other, item["item_id"])]["outcome"]))
            n = len(paired)
            cells[f"{model}:{level}"] = dict(model=model, level=level, n_items=len(members),
                n_counted=len(counted), n=n, n_correct=sum(i["correct"] for i in paired),
                n_capped=sum(i["capped"] for i in paired),
                n_malformed=sum(i["malformed"] for i in paired),
                prompt_tokens=sum(i["prompt_tokens"] for i in paired),
                generated_tokens=sum(i["generated_tokens"] for i in paired),
                gross_j=math.fsum(window_by_key[_key(p)]["gross_j"] for p in roster["placements"]
                                  if _key(p) in live and blocks[p["block_id"]]["model"] == model
                                  and blocks[p["block_id"]]["level"] == level),
                k24_dropped=dropped,
                uncounted={name: sum(i["outcome"] == name for i in members)
                           for name in ("ceiling_violation", "unattributed_overrun")},
                retry_stage_counts=stage_counts,
                cap_bound=None if n == 0 else sum(i["capped"] for i in paired) / n > CAP_BOUND_FRACTION,
                spread_exceeded=status["spread_exceeded"][f"{model}:{level}"],
                fully_counted_parents=len(cp), distinct_envelopes=len(occupied))
    max_gap = None
    if g["budget_j"] is not None and g["delta_upper_j_per_block_slot"] is not None:
        max_gap = g["budget_j"] / (g["delta_upper_j_per_block_slot"]
                                    * math.ceil(len(g["item_ids_by_level"]["1"]) / g["block_size"][g["arm"]]))
    levels = {str(level): dict(executed_drift_lever_slots=status["executed_drift_lever_slots"][str(level)],
                               drift_exceeded=status["drift_exceeded"][str(level)], max_gap=max_gap)
              for level in range(1, 6)}
    return dict(schema="joulewise.scored_reduction.v1", registration_sha256=_sha(g),
                roster_sha256=roster["sha256"], registered_sha256=roster["registered_sha256"],
                scorer_id=g["scorer_id"], mode=g["mode"], claim_ready=roster["claim_ready"],
                items=items, parents=parents, cells=cells, levels=levels,
                counted_windows=counted_windows, uncounted_windows=uncounted_windows,
                terminal_refusals=terminal_refusals, superseded_rows=superseded,
                executed_status=status)


def _first_refusal(g, roster, predictions, rows, windows):
    """Return the first wire refusal after the packer verifier has accepted the roster."""
    if type(rows) is not list or type(windows) is not list:
        return "reduce_input", "rows and windows must be lists"
    placements = {_key(p): p for p in roster["placements"]}
    blocks = {b["block_id"]: b for b in roster["blocks"]}
    live = {key for key, p in placements.items()
            if p["block_id"] in roster["envelopes"][p["envelope_index"]]["blocks"]}
    seen = set()
    for window in windows:
        if type(window) is not dict or set(window) != WINDOW_KEYS:
            return "window_keys", "window key set"
        if not _window_domain(window):
            return "window_domain", "window domain"
        key = _key(window)
        if key not in placements:
            return "window_unknown", repr(key)
        if window["registration_sha256"] != _sha(g) or window["roster_sha256"] != _in_force(roster, placements[key]["envelope_index"]):
            return "window_binding", repr(key)
        if key in seen:
            return "window_duplicate", repr(key)
        seen.add(key)
        if window["envelope_index"] != placements[key]["envelope_index"]:
            return "window_envelope", repr(key)
        env = roster["envelopes"][placements[key]["envelope_index"]]
        observation = next(o for o in env["observations"] if o["block_id"] == key[0])
        if observation["status"] == "not_started":
            return "window_unstarted", repr(key)
    seen_rows = set()
    cap_tokens_arm = g["cap_tokens"][g["arm"]]
    for row in rows:
        if type(row) is not dict or set(row) != ROW_KEYS:
            return "row_keys", "row key set"
        if not _row_domain(row):
            return "row_domain", "row domain"
        if row["stop_reason"] not in STOP_REASONS:
            return "row_stop_reason_unknown", row["stop_reason"]
        if row["scorer_id"] != g["scorer_id"]:
            return "row_scorer", row["scorer_id"]
        key = _key(row)
        if key not in placements or row["item_id"] not in blocks[key[0]]["items"]:
            return "row_unknown", repr((key, row["item_id"]))
        if row["registration_sha256"] != _sha(g) or row["roster_sha256"] != roster["sha256"]:
            return "row_binding", repr(key)
        row_key = (key, row["item_id"])
        if row_key in seen_rows:
            return "row_duplicate", repr(row_key)
        seen_rows.add(row_key)
        env = roster["envelopes"][placements[key]["envelope_index"]]
        observation = next(o for o in env["observations"] if o["block_id"] == key[0])
        if observation["status"] == "not_started":
            return "row_unstarted", repr(row_key)
        if row["generated_tokens"] > cap_tokens_arm:
            return "row_tokens_over_cap", repr(row_key)
        if STOP_REASONS[row["stop_reason"]] != (row["generated_tokens"] >= cap_tokens_arm):
            return "row_cap_disagreement", repr(row_key)
    for key in roster["placements"]:
        pair = _key(key)
        if pair not in live:
            continue
        window = next((w for w in windows if _key(w) == pair), None)
        if window is None:
            return "missing_live_window", repr(pair)
        if window["energy_bound_terms_j"]["E_clock_anchor_shift_bound_j"] is None:
            return "anchor_energy_envelope_unrecorded", repr(pair)
        for item in blocks[pair[0]]["items"]:
            if (pair, item) not in seen_rows:
                return "row_missing", repr((pair, item))
    return None, None


def check_reduction(registration_mapping, roster, predicted_decode_s, score_rows, capture_windows, candidate):
    """Return violations for a reducer result or its typed refusal outcome."""
    g = registration_mapping
    code, detail = _first_refusal(g, roster, predicted_decode_s, score_rows, capture_windows)
    if code is not None:
        if type(candidate) is not dict or candidate.get("refusal_code") != code:
            return _violation("refusal_mismatch", f"expected {code}; got {candidate!r}")
        if code == "missing_live_window" and str(detail) not in str(candidate.get("detail", "")):
            return _violation("refusal_detail", f"missing key {detail}")
        return []
    if type(candidate) is not dict or set(candidate) != OUTPUT_KEYS:
        return _violation("output_keys", "exact output key set")
    try:
        pre = dict(candidate)
        digest = pre.pop("sha256")
        if digest != _sha(pre):
            return _violation("output_sha256", "canonical digest")
        live = {(_key(p)) for p in roster["placements"]
                if p["block_id"] in roster["envelopes"][p["envelope_index"]]["blocks"]}
        status = check_executed(g, roster, predicted_decode_s, frozenset(live))
        if "violations" in status:
            return _violation("roster_invalid", status["violations"])
        expected = _expected(g, roster, score_rows, capture_windows, live, status)
        for key in expected:
            if pre[key] != expected[key]:
                return _violation(key, f"{key} differs from independent derivation")
        if any(set(x) != ITEM_KEYS for x in candidate["items"]):
            return _violation("items_keys", "exact item keys")
        if any(set(x) != PARENT_KEYS for x in candidate["parents"]):
            return _violation("parents_keys", "exact parent keys")
        if any(set(x) != CELL_KEYS for x in candidate["cells"].values()):
            return _violation("cells_keys", "exact cell keys")
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as exc:
        return _violation("oracle_input", f"{type(exc).__name__}: {exc}")
    return []
