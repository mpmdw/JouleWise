"""Deterministic scored envelope planning and observed retry replay."""
from __future__ import annotations

import copy
import hashlib
import json
import math
from contextvars import ContextVar

from joulewise.scored_registration import (
    Registration, LEVELS, RETRY_STAGES, MIN_PARENT_BLOCKS, MIN_ENVELOPES,
    ROSTER_SCHEMA,
)


class PackingRefusal(ValueError):
    def __init__(self, code, detail=""):
        self.code = code
        super().__init__(f"{code}: {detail}")


_REPLAYING = ContextVar("scored_packer_replaying", default=False)


def _need(ok, code, detail=""):
    if not ok:
        raise PackingRefusal(code, detail)


def _canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(roster):
    pre = copy.deepcopy(roster)
    pre.pop("sha256", None)
    pre.pop("registered_sha256", None)
    for event in pre["events"]:
        event.pop("sha256", None)
    return hashlib.sha256(_canon(pre)).hexdigest()


def _roles(registration):
    roles = registration.role_to_model_id
    return (roles["8B"], roles["1.7B"])


def _items(registration):
    ids = registration.item_ids_by_level
    return [item for level in LEVELS for item in ids[str(level)]]


def _predictions(registration, predicted):
    models = _roles(registration)
    ids = set(_items(registration))
    _need(type(predicted) is dict and set(predicted) == set(models), "inv_07", "model keys")
    for model in models:
        entries = predicted[model]
        _need(type(entries) is dict and set(entries) == ids, "inv_07", "item keys")
        worst = registration.worst(model)
        _need(all(type(v) in (int, float) and math.isfinite(v) and 0 < v <= worst for v in entries.values()), "inv_07", "duration")
    try:
        digest = hashlib.sha256(_canon(predicted)).hexdigest()
    except (TypeError, ValueError, OverflowError) as exc:
        raise PackingRefusal("inv_07", "canonical JSON") from exc
    expected = registration.predictions_sha256
    _need(expected is None or digest == expected, "inv_08", "prediction digest")


def _ownership(registration, roster):
    """Rebuild the ownership view from the roster on every call."""
    blocks = {}
    for block in roster["blocks"]:
        blocks.setdefault(block["block_id"], block)
    placement = {}
    for p in roster["placements"]:
        placement.setdefault((p["block_id"], p["envelope_index"]), p)
    live = {}
    for envelope in roster["envelopes"]:
        for bid in envelope["blocks"]:
            block = blocks[bid]
            for item in dict.fromkeys(block["items"]):
                live.setdefault((block["model"], item), []).append((bid, envelope["index"]))
    term = {}
    for entry in roster["terminal_refusals"]:
        term.setdefault((entry["model"], entry["item_id"]), []).append(entry)
    return dict(blocks=blocks, live=live, term=term, placement=placement)


def _conserve(registration, view):
    for model in registration.role_to_model_id.values():
        for item in _items(registration):
            live = view["live"].get((model, item), [])
            term = view["term"].get((model, item), [])
            counts = (len(live), len(term))
            held = counts == (1, 0) and not view["blocks"][live[0][0]]["superseded"] and not any(
                view["term"].get((model, x)) for x in view["blocks"][live[0][0]]["items"])
            _need(held or counts == (0, 1), "inv_11", "item conservation")


def _formation(registration, roster):
    arm = registration.arm
    size = registration.block_size[arm]
    expected = []
    for level in LEVELS:
        items = registration.item_ids_by_level[str(level)]
        for model in _roles(registration):
            for k, start in enumerate(range(0, len(items), size)):
                expected.append((f"{model}:{arm}:{level}:{k}", model, level, items[start:start + size]))
    parents = [(b["block_id"], b["model"], b["level"], b["items"]) for b in roster["blocks"] if b["parent_block_id"] is None]
    _need(parents == expected, "inv_10", "parent formation and order")


def _parent_facts(registration, roster, captured_window_keys=None):
    view = _ownership(registration, roster)
    facts = []
    for parent in view["blocks"].values():
        if parent["parent_block_id"] is not None:
            continue
        model = parent["model"]
        indices = []
        n_terminal = 0
        for item in parent["items"]:
            if view["term"].get((model, item)):
                n_terminal += 1
                continue
            live = view["live"].get((model, item), [])
            placement = view["placement"].get(live[0]) if len(live) == 1 else None
            if placement is not None and (captured_window_keys is None or
                    (placement["block_id"], placement["attempt"]) in captured_window_keys):
                indices.append(placement["envelope_index"])
        facts.append(dict(parent_id=parent["block_id"], model=model, level=parent["level"],
                          n_items=len(parent["items"]), n_terminal=n_terminal, indices=indices))
    return facts


def _lever(registration, facts, *, executed):
    for fact in facts:
        _need(fact["n_items"] != 0, "inv_10", f"empty parent {fact['parent_id']}")
    for fact in facts:
        gate = len(fact["indices"]) == fact["n_items"] if executed else fact["n_terminal"] == 0
        if gate:
            _need(len(fact["indices"]) == fact["n_items"], "inv_11",
                  f"gate parent without full live positions {fact['parent_id']}")
    cell_flags = {}
    positions = {}
    for level in LEVELS:
        for model in _roles(registration):
            cell = [f for f in facts if f["model"] == model and f["level"] == level]
            gate = [f for f in cell if (len(f["indices"]) == f["n_items"] if executed else f["n_terminal"] == 0)]
            occupied = {index for f in gate for index in f["indices"]}
            cell_flags[f"{model}:{level}"] = len(gate) < MIN_PARENT_BLOCKS or len(occupied) < MIN_ENVELOPES
            positions[(model, level)] = ([sum(f["indices"]) / len(f["indices"]) for f in cell if f["indices"]], len(gate))
    lever = {}
    for level in LEVELS:
        (first, first_count), (second, second_count) = (positions[(model, level)] for model in _roles(registration))
        lever[str(level)] = abs(sum(first) / len(first) - sum(second) / len(second)) if first_count and second_count else None
    return cell_flags, lever


def _derived(registration, roster, captured_window_keys=None):
    return _lever(registration, _parent_facts(registration, roster, captured_window_keys), executed=captured_window_keys is not None)


def _checked_derived(registration, roster, captured_window_keys=None):
    try:
        return _derived(registration, roster, captured_window_keys)
    except PackingRefusal:
        raise
    except (KeyError, TypeError, ValueError, IndexError, StopIteration, AttributeError) as exc:
        raise PackingRefusal("inv_52", "malformed roster") from exc
    except ArithmeticError as exc:
        raise PackingRefusal("inv_52", f"internal:{type(exc).__name__}") from exc


def _structure(registration, roster):
    shapes = {
        "blocks": set("block_id model level items predicted_item_s predicted_s attempt retry_stage parent_block_id superseded late".split()),
        "envelopes": set("index model kind blocks voided_block_ids observations".split()),
        "placements": set("block_id attempt stage reserved_s envelope_index".split()),
        "terminal_refusals": set("type block_id attempt parent_block_id item_id model level".split()),
        "events": set("envelope_index block_ids observations placements sha256".split()),
    }
    for name, keys in shapes.items():
        rows = roster[name]
        _need(type(rows) is list, "inv_52", name)
        _need(all(type(row) is dict and set(row) == keys for row in rows), "inv_03", name)
    obs_keys = {"block_id", "status", "elapsed_s", "decision"}
    for e in roster["envelopes"]:
        _need(e["observations"] is None or type(e["observations"]) is list and all(type(o) is dict and set(o) == obs_keys for o in e["observations"]), "inv_03", "envelope observations")
    for event in roster["events"]:
        _need(type(event["observations"]) is list and all(type(o) is dict and set(o) == obs_keys for o in event["observations"]), "inv_03", "event observations")
    models = _roles(registration)
    bm = {}
    predictions = {model: {} for model in models}
    for block in roster["blocks"]:
        bid = block["block_id"]
        _need(type(bid) is str and bid not in bm and block["model"] in models and type(block["level"]) is int and block["level"] in LEVELS, "inv_10", "block identity")
        _need(type(block["items"]) is list and type(block["predicted_item_s"]) is list and len(block["items"]) == len(block["predicted_item_s"]), "inv_52", "block items")
        _need(len(block["items"]) >= 1, "inv_10", "empty block")
        _need(type(block["attempt"]) is int and block["attempt"] >= 0 and block["retry_stage"] in RETRY_STAGES and type(block["superseded"]) is bool and type(block["late"]) is bool, "inv_52", "block domain")
        bm[bid] = block
        if block["parent_block_id"] is None:
            _need(block["predicted_s"] == sum(block["predicted_item_s"]), "inv_21", "parent predicted sum")
            predictions[block["model"]].update(zip(block["items"], block["predicted_item_s"]))
    _predictions(registration, predictions)
    placements = roster["placements"]
    for i, envelope in enumerate(roster["envelopes"]):
        _need(envelope["index"] == i and type(envelope["index"]) is int, "inv_17", "grid")
        _need(envelope["model"] in models and envelope["kind"] in ("loaded", "idle_slot") and type(envelope["blocks"]) is list and type(envelope["voided_block_ids"]) is list, "inv_52", "envelope")
        ids = envelope["blocks"] + envelope["voided_block_ids"]
        selected = [p for p in placements if p["envelope_index"] == i]
        _need(len(ids) == len(set(ids)) and len(ids) == len(selected) and set(ids) == {p["block_id"] for p in selected}, "inv_03", "placement ownership")
        if envelope["kind"] == "idle_slot":
            _need(not ids and envelope["observations"] is None, "inv_16", "idle slot")
        else:
            _need(bool(ids), "inv_15", "empty loaded envelope")
        _need(all(bm[p["block_id"]]["model"] == envelope["model"] for p in selected), "inv_14", "model homogeneity")
        _need(sum(p["reserved_s"] for p in selected) <= registration.cap, "inv_20", "capacity")
        for level in LEVELS:
            parents = {(bm[p["block_id"]]["parent_block_id"] or p["block_id"]) for p in selected if bm[p["block_id"]]["level"] == level}
            _need(len(parents) <= 1, "inv_24", "parent spread")
    _need(all(type(p["attempt"]) is int and p["attempt"] >= 0 and p["stage"] in RETRY_STAGES[:-1] and type(p["reserved_s"]) in (int, float) and math.isfinite(p["reserved_s"]) and p["reserved_s"] > 0 and type(p["envelope_index"]) is int and 0 <= p["envelope_index"] < len(roster["envelopes"]) for p in placements), "inv_52", "placement domain")
    _conserve(registration, _ownership(registration, roster))
    _formation(registration, roster)
    loaded = [e["index"] for e in roster["envelopes"] if e["kind"] == "loaded"]
    _need([ev["envelope_index"] for ev in roster["events"]] == loaded[:len(roster["events"])], "report_order", "reported prefix")
    culprits = {}
    for event in roster["events"]:
        ix = event["envelope_index"]
        _need(roster["envelopes"][ix]["observations"] == event["observations"] and event["block_ids"] == [o["block_id"] for o in event["observations"]], "inv_29", "event observations")
        phase = 0
        any_culprit = False
        elapsed_total = 0
        for obs in event["observations"]:
            status, elapsed = obs["status"], obs["elapsed_s"]
            _need(status in ("completed", "cut_off", "not_started") and obs["decision"] in ("keep", "advance", "split", "reschedule", "unattributed_overrun"), "inv_52", "observation vocabulary")
            _need(elapsed is None if status == "not_started" else type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed > 0, "invalid_elapsed", "observation duration")
            next_phase = {"completed": 0, "cut_off": 1, "not_started": 2}[status]
            _need(next_phase >= phase and not (next_phase == phase == 1), "invalid_observation_order", "observation order")
            phase = next_phase
            elapsed_total += elapsed or 0
            bid = obs["block_id"]
            placement = next(p for p in placements if p["block_id"] == bid and p["envelope_index"] == ix)
            block = bm[bid]
            bound = block["predicted_s"] if placement["stage"] in ("initial", "whole_block") else registration.worst(block["model"])
            if elapsed is not None and elapsed > bound:
                any_culprit = True
                key = (bid if placement["stage"] == "initial" else (block["model"], block["items"][0])) if placement["stage"] != "whole_block" else None
                if key is not None:
                    culprits[key] = culprits.get(key, 0) + 1
                    _need(culprits[key] <= (1 if placement["stage"] == "initial" else 2), "culprit_limit", "culprit count")
        _need(elapsed_total <= registration.interior_s, "invalid_elapsed", "event duration")
        rescheduled = sum(obs["decision"] == "reschedule" for obs in event["observations"])
        _need(rescheduled <= len(event["block_ids"]) - 1, "inv_35c", "reschedule count")
        _need(not rescheduled or any_culprit, "reschedule_without_culprit", "reschedule cause")
        _need(all(type(i) is int and 0 <= i < len(placements) and placements[i]["envelope_index"] > ix for i in event["placements"]), "inv_18", "event placement target")
    children = {}
    for block in roster["blocks"]:
        parent_id = block["parent_block_id"]
        if parent_id is None:
            continue
        parent = bm.get(parent_id)
        _need(parent is not None and block["model"] == parent["model"] and block["level"] == parent["level"] and len(block["items"]) == 1 and parent["superseded"], "inv_12", "single parent")
        item = block["items"][0]
        _need(item in parent["items"] and block["block_id"] == f"{parent_id}:single:{parent['items'].index(item)}", "inv_12", "single item")
        children.setdefault(parent_id, []).append(item)
    for parent in roster["blocks"]:
        if parent["parent_block_id"] is None and parent["superseded"]:
            _need(sorted(children.get(parent["block_id"], [])) == sorted(parent["items"]), "inv_12", "single partition")


def _seal(registration, roster, *, finalize=False):
    """Check a supplied seal or write the sole new digest at a public exit."""
    _need(isinstance(registration, Registration), "inv_51", "Registration required")
    _need(type(roster) is dict and set(roster) == set("schema registration_sha256 claim_ready item_set_sha256 n_per_level blocks envelopes placements terminal_refusals events drift_lever_slots planned_spread_shortfall registered_sha256 sha256".split()), "inv_03", "roster keys")
    _need(roster["schema"] == ROSTER_SCHEMA, "inv_03", "roster schema")
    _need(roster["registration_sha256"] == registration.digest, "inv_01", "registration binding")
    _need(roster["claim_ready"] == (registration.mode == "registered"), "inv_05", "claim readiness")
    _need(roster["n_per_level"] == registration.n_per_level and roster["item_set_sha256"] == hashlib.sha256(_canon(_items(registration))).hexdigest(), "inv_04", "item identity")
    try:
        if not finalize:
            digest = _digest(roster)
            _need(roster["sha256"] is not None, "inv_02", "input unsealed")
            _need(roster["sha256"] == digest, "inv_02", "digest mismatch")
            _need(roster["registered_sha256"] == (digest if not roster["events"] else roster["registered_sha256"]), "inv_38", "root digest")
            if roster["events"]:
                _need(roster["events"][-1]["sha256"] == digest, "inv_38", "event digest")
        _structure(registration, roster)
        short, lever = _checked_derived(registration, roster)
    except PackingRefusal:
        raise
    except (KeyError, TypeError, ValueError, IndexError, StopIteration, AttributeError) as exc:
        raise PackingRefusal("inv_52", "malformed roster") from exc
    except ArithmeticError as exc:
        raise PackingRefusal("inv_52", f"internal:{type(exc).__name__}") from exc
    _need(roster["planned_spread_shortfall"] == short and roster["drift_lever_slots"] == lever, "stale_derived", "derived values")
    if not roster["events"]:
        _need(not any(short.values()), "spread_minima", "root spread")
        if registration.mode == "registered":
            _need(all(v is not None and v <= registration.max_gap for v in lever.values()), "inv_28", "planned drift")
    if finalize:
        _need(roster["sha256"] is None, "inv_02", "output already sealed")
        digest = _digest(roster)
        roster["sha256"] = digest
        if not roster["events"]:
            roster["registered_sha256"] = digest
        else:
            roster["events"][-1]["sha256"] = digest
    return roster


def _new_envelope(roster, model):
    index = len(roster["envelopes"])
    roster["envelopes"].append(dict(index=index, model=model, kind="loaded", blocks=[], voided_block_ids=[], observations=None))
    return index


def _place(roster, block, target, reserve, created=None):
    if target == len(roster["envelopes"]):
        _new_envelope(roster, block["model"])
    place = dict(block_id=block["block_id"], attempt=block["attempt"], stage=block["retry_stage"], reserved_s=reserve, envelope_index=target)
    if created is not None:
        created.append(len(roster["placements"]))
    roster["placements"].append(place)
    roster["envelopes"][target]["blocks"].append(block["block_id"])


def _eligible(registration, roster, reporter, block, reserve):
    last = max((ev["envelope_index"] for ev in roster["events"]), default=-1)
    bm = {b["block_id"]: b for b in roster["blocks"]}
    for e in roster["envelopes"]:
        ix = e["index"]
        if ix <= max(reporter, last) or e["observations"] is not None or e["kind"] != "loaded" or e["model"] != block["model"]:
            continue
        ids = e["blocks"] + e["voided_block_ids"]
        if any(bm[bid]["retry_stage"] == "whole_block" for bid in ids):
            continue
        if any(bm[bid]["level"] == block["level"] and (bm[bid]["parent_block_id"] or bid) != (block["parent_block_id"] or block["block_id"]) for bid in ids):
            continue
        if sum(p["reserved_s"] for p in roster["placements"] if p["envelope_index"] == ix) + reserve > registration.cap:
            continue
        return ix
    return len(roster["envelopes"])


def pack(registration, predicted_decode_s):
    _need(isinstance(registration, Registration), "inv_51", "Registration required")
    _predictions(registration, predicted_decode_s)
    arm = registration.arm
    size = registration.block_size[arm]
    blocks = []
    for level in LEVELS:
        items = registration.item_ids_by_level[str(level)]
        for model in _roles(registration):
            for k, start in enumerate(range(0, len(items), size)):
                members = items[start:start + size]
                durations = [predicted_decode_s[model][item] for item in members]
                total = sum(durations)
                _need(total <= registration.cap, "inv_20", "parent exceeds capacity")
                blocks.append(dict(block_id=f"{model}:{arm}:{level}:{k}", model=model, level=level, items=members, predicted_item_s=durations, predicted_s=total, attempt=0, retry_stage="initial", parent_block_id=None, superseded=False, late=False))
    _need(registration.blocks_per_cell >= MIN_PARENT_BLOCKS, "spread_minima", "too few parents")
    # One bucket per k keeps every cell's parents in distinct envelopes. Fill
    # each bucket with other levels while capacity permits.
    buckets = {model: [] for model in _roles(registration)}
    for model in _roles(registration):
        for block in (b for b in blocks if b["model"] == model):
            fits = next((bucket for bucket in buckets[model] if not any(x["level"] == block["level"] for x in bucket) and sum(x["predicted_s"] for x in bucket) + block["predicted_s"] <= registration.cap), None)
            if fits is None:
                fits = []
                buckets[model].append(fits)
            fits.append(block)
    roster = dict(schema=ROSTER_SCHEMA, registration_sha256=registration.digest, claim_ready=registration.mode == "registered", item_set_sha256=hashlib.sha256(_canon(_items(registration))).hexdigest(), n_per_level=registration.n_per_level, blocks=blocks, envelopes=[], placements=[], terminal_refusals=[], events=[], drift_lever_slots={}, planned_spread_shortfall={}, registered_sha256=None, sha256=None)
    models = _roles(registration)
    # Interleave workers to limit the planned mean-index gap.
    for k in range(max(map(len, buckets.values()))):
        for model in models:
            if k < len(buckets[model]):
                ix = _new_envelope(roster, model)
                roster["envelopes"][ix]["blocks"] = [b["block_id"] for b in buckets[model][k]]
    if all(len(buckets[m]) % 2 for m in models):
        roster["envelopes"].append(dict(index=len(roster["envelopes"]), model=models[1], kind="idle_slot", blocks=[], voided_block_ids=[], observations=None))
    byid = {b["block_id"]: b for b in blocks}
    for e in roster["envelopes"]:
        for bid in e["blocks"]:
            b = byid[bid]
            roster["placements"].append(dict(block_id=bid, attempt=0, stage="initial", reserved_s=b["predicted_s"], envelope_index=e["index"]))
    roster["planned_spread_shortfall"], roster["drift_lever_slots"] = _checked_derived(registration, roster)
    return _seal(registration, roster, finalize=True)


def _observations(registration, roster, envelope_index, observations):
    _need(type(envelope_index) is int and 0 <= envelope_index < len(roster["envelopes"]), "report_order", "index")
    pending = next((e["index"] for e in roster["envelopes"] if e["kind"] == "loaded" and e["observations"] is None), None)
    _need(envelope_index == pending and (not roster["events"] or envelope_index > roster["events"][-1]["envelope_index"]), "report_order", "next loaded envelope")
    ids = roster["envelopes"][envelope_index]["blocks"]
    _need(type(observations) is list and len(observations) == len(ids), "inv_29", "observation count")
    phase = 0
    total = 0
    for bid, obs in zip(ids, observations):
        _need(type(obs) is dict and set(obs) == {"block_id", "status", "elapsed_s"} and obs["block_id"] == bid, "inv_29", "observation keys/order")
        _need(type(obs["status"]) is str and obs["status"] in ("completed", "cut_off", "not_started"), "inv_29", "status")
        elapsed = obs["elapsed_s"]
        _need((elapsed is None if obs["status"] == "not_started" else type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed > 0), "invalid_elapsed", "elapsed")
        next_phase = {"completed": 0, "cut_off": 1, "not_started": 2}[obs["status"]]
        _need(next_phase >= phase and not (next_phase == phase == 1), "invalid_observation_order", "order")
        phase = next_phase
        total += elapsed or 0
    _need(total <= registration.interior_s, "invalid_elapsed", "elapsed sum")


def requeue_overrun(registration, roster, envelope_index, observations):
    _seal(registration, roster)
    if not _REPLAYING.get(): _replay_roster(registration, roster)
    _observations(registration, roster, envelope_index, observations)
    result = copy.deepcopy(roster)
    e = result["envelopes"][envelope_index]
    ids = list(e["blocks"])
    bm = {b["block_id"]: b for b in result["blocks"]}
    anyc = any(type(o["elapsed_s"]) in (int, float) and o["elapsed_s"] > (bm[o["block_id"]]["predicted_s"] if bm[o["block_id"]]["retry_stage"] in ("initial", "whole_block") else registration.worst(bm[o["block_id"]]["model"])) for o in observations)
    created = []
    recorded = []
    for bid, obs in zip(ids, observations):
        b = bm[bid]
        stage = b["retry_stage"]
        previous = next(p for p in reversed(result["placements"]) if p["block_id"] == bid)
        elapsed = obs["elapsed_s"]
        culprit = type(elapsed) in (int, float) and elapsed > (b["predicted_s"] if stage in ("initial", "whole_block") else registration.worst(b["model"]))
        status = obs["status"]
        if status == "completed":
            decision = "advance" if culprit and stage in ("single_problem", "single_retry") else "keep"
        elif stage == "whole_block":
            decision = "split" if status == "cut_off" else "unattributed_overrun"
        elif culprit:
            decision = "advance"
        else:
            decision = "reschedule" if anyc else "unattributed_overrun"
        recorded.append(dict(block_id=bid, status=status, elapsed_s=elapsed, decision=decision))
        b["late"] = status == "completed" and culprit
        if decision == "keep":
            continue
        e["blocks"].remove(bid)
        e["voided_block_ids"].append(bid)
        if decision == "unattributed_overrun" or (decision == "advance" and stage == "single_retry"):
            kind = "unattributed_overrun" if decision == "unattributed_overrun" else "ceiling_violation"
            if kind == "ceiling_violation":
                b["retry_stage"] = "ceiling_violation"
            for item in b["items"]:
                result["terminal_refusals"].append(dict(type=kind, block_id=bid, attempt=previous["attempt"], parent_block_id=b["parent_block_id"], item_id=item, model=b["model"], level=b["level"]))
        elif decision == "split":
            b["superseded"] = True
            for j, item in enumerate(b["items"]):
                single = dict(block_id=f"{bid}:single:{j}", model=b["model"], level=b["level"], items=[item], predicted_item_s=[b["predicted_item_s"][j]], predicted_s=registration.worst(b["model"]), attempt=b["attempt"] + 1, retry_stage="single_problem", parent_block_id=bid, superseded=False, late=False)
                result["blocks"].append(single)
                reserve = registration.worst(single["model"])
                _place(result, single, _eligible(registration, result, envelope_index, single, reserve), reserve, created)
        else:
            b["attempt"] += 1
            if decision == "advance":
                b["retry_stage"] = {"initial": "whole_block", "single_problem": "single_retry"}[stage]
            reserve = (min(sum(registration.worst(b["model"]) for _ in b["items"]), registration.cap) if decision == "advance" and b["retry_stage"] == "whole_block" else registration.worst(b["model"]) if decision == "advance" else previous["reserved_s"])
            target = len(result["envelopes"]) if decision == "advance" and b["retry_stage"] == "whole_block" else _eligible(registration, result, envelope_index, b, reserve)
            _place(result, b, target, reserve, created)
    e["observations"] = recorded
    result["planned_spread_shortfall"], result["drift_lever_slots"] = _checked_derived(registration, result)
    result["events"].append(dict(envelope_index=envelope_index, block_ids=ids, observations=recorded, placements=created, sha256=""))
    result["sha256"] = None
    return _seal(registration, result, finalize=True)


def _replay_roster(registration, roster, predicted_decode_s=None):
    if predicted_decode_s is None:
        predicted_decode_s = {model: {} for model in _roles(registration)}
        for block in roster["blocks"]:
            if block["parent_block_id"] is None:
                predicted_decode_s[block["model"]].update(zip(block["items"], block["predicted_item_s"]))
    root = pack(registration, predicted_decode_s)
    _need(root["sha256"] == roster["registered_sha256"], "inv_39", "root re-pack")
    state = root
    token = _REPLAYING.set(True)
    try:
        for event in roster["events"]:
            stripped = [{key: obs[key] for key in ("block_id", "status", "elapsed_s")} for obs in event["observations"]]
            state = requeue_overrun(registration, state, event["envelope_index"], stripped)
            _need(state["events"][-1] == event and state["sha256"] == event["sha256"], "inv_38", "event replay")
    finally:
        _REPLAYING.reset(token)
    _need(state == roster, "inv_38", "final replay")


def verify_executed_roster(registration, roster, predicted_decode_s):
    _seal(registration, roster)
    _replay_roster(registration, roster, predicted_decode_s)
    _need(all(e["kind"] != "loaded" or e["observations"] is not None for e in roster["envelopes"]), "unreported_envelope", "loaded envelope pending")
    return None


def executed_status(registration, roster, predicted_decode_s, captured_window_keys):
    verify_executed_roster(registration, roster, predicted_decode_s)
    _need(type(captured_window_keys) in (set, frozenset) and all(type(key) is tuple and len(key) == 2 and type(key[0]) is str and type(key[1]) is int for key in captured_window_keys), "inv_52", "window keys")
    spread, lever = _checked_derived(registration, roster, captured_window_keys)
    drift = {str(level): lever[str(level)] is not None and registration.max_gap is not None and lever[str(level)] > registration.max_gap for level in LEVELS}
    return dict(spread_exceeded=spread, executed_drift_lever_slots=lever, drift_exceeded=drift)
