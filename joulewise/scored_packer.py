"""Pure roster planning for scored, fixed-length power envelopes.

Inputs: ``items_by_level`` maps level to ordered problem IDs;
``predicted_decode_s`` maps model to problem ID to seconds. The returned JSON-compatible roster contains
blocks, envelopes, and a canonical SHA-256 excluding the digest field.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import random

from joulewise.scored_registration import Registration


class PackingRefusal(ValueError):
    """A cell cannot satisfy the registered packing constraints."""

    def __init__(self, cell, reason):
        self.cell = cell
        super().__init__(f"cell {cell!r}: {reason}")


def _digest(roster):
    payload = {key: value for key, value in roster.items() if key != "sha256"}
    roster["sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return roster


def _duration(predictions, model, item):
    try:
        value = predictions[model][item]
    except (KeyError, TypeError) as exc:
        raise PackingRefusal((model, item), "missing predicted duration") from exc
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise PackingRefusal((model, item), "invalid predicted duration")
    return float(value)


def _williams_rows(count):
    base = []
    low, high = 0, count - 1
    while low <= high:
        base.append(low)
        if low != high:
            base.append(high)
        low += 1
        high -= 1
    rows = [[(v + row) % count for v in base] for row in range(count)]
    if count % 2:
        rows += [list(reversed(row)) for row in rows]
    return rows


def _balance(buckets, models, blocks, levels):
    """Place loaded captures to minimize the largest measured-cell mean gap."""
    lookup = {b["block_id"]: b for b in blocks}
    labels = [model for model in models for _ in buckets[model]]
    # An extra capture gives two odd-sized cells an exact common mean.
    if all(len(buckets[model]) % 2 for model in models):
        labels.append("idle")
    rng = random.Random(0)

    def score(order):
        positions = {model: [] for model in models}
        for index, label in enumerate(order):
            if label in positions:
                positions[label].append(index)
        gaps = []
        for level in levels:
            means = []
            for model in models:
                indices = [positions[model][i] for i, bucket in enumerate(buckets[model])
                           if any(lookup[bid]["level"] == level for bid in bucket)]
                means.append(sum(indices) / len(indices))
            gaps.append(abs(means[0] - means[1]))
        return (max(gaps), sum(gaps)), gaps

    best = None
    for restart in range(12):
        order = labels.copy()
        if restart:
            rng.shuffle(order)
        current, _ = score(order)
        for step in range(2200):
            i, j = rng.sample(range(len(order)), 2)
            if order[i] == order[j]:
                continue
            order[i], order[j] = order[j], order[i]
            trial, _ = score(order)
            temperature = max(0.02, 1.0 - step / 1800)
            if trial < current or rng.random() < math.exp((current[0] - trial[0]) / temperature):
                current = trial
            else:
                order[i], order[j] = order[j], order[i]
            if best is None or current < best[0]:
                best = (current, order.copy())
            if not best[0][0]:
                break
        if not best[0][0]:
            break
    order = best[1]
    indexed = {model: iter(buckets[model]) for model in models}
    envelopes = []
    for index, label in enumerate(order):
        if label == "idle":
            # An idle capture retains a loaded worker and a grid position.
            model = models[1]
            envelopes.append({"index": index, "model": model, "kind": "idle_slot", "blocks": [], "predicted_s": 0.0})
        else:
            envelopes.append({"index": index, "model": label, "kind": "loaded",
                              "blocks": next(indexed[label]), "predicted_s": 0.0})
    _, gaps = score(order)
    return envelopes, {level: gap for level, gap in zip(levels, gaps)}


def _arrange(blocks, models, capacity, levels):
    buckets = {}
    for model in models:
        pending = [block for block in blocks if block["model"] == model]
        buckets[model] = []
        while pending:
            picked = []
            total = 0.0
            row = _williams_rows(len(levels))[len(buckets[model]) % len(_williams_rows(len(levels)))]
            for level in (levels[i] for i in row):
                block = next((b for b in pending if b["level"] == level and
                              total + b["predicted_s"] <= capacity), None)
                if block:
                    picked.append(block["block_id"])
                    total += block["predicted_s"]
                    pending.remove(block)
            if not picked:
                block = pending[0]
                raise PackingRefusal((model, block["arm"], block["level"]), "block exceeds envelope capacity")
            buckets[model].append(picked)
    envelopes, gaps = _balance(buckets, models, blocks, levels)
    lookup = {block["block_id"]: block for block in blocks}
    for envelope in envelopes:
        envelope["predicted_s"] = sum(lookup[bid]["predicted_s"] for bid in envelope["blocks"])
    return envelopes, gaps


ROSTER_KEYS = frozenset({"schema", "models", "arm", "block_size", "interior_s", "guard_s",
    "cap_tokens_by_arm", "envelope_s", "offset_s", "pitch_s", "capacity_s", "levels", "blocks",
    "envelopes", "drift_lever_slots", "drift_exceeded", "claim_ready", "registration_sha256",
    "registered_sha256", "parent_sha256", "terminal_refusals", "sha256"})
BLOCK_KEYS = frozenset({"block_id", "model", "arm", "level", "items", "predicted_s",
    "predicted_item_s", "attempt", "origin_attempt", "retry_stage", "parent_block_id", "superseded", "ceiling_violation"})
ENVELOPE_KEYS = frozenset({"index", "model", "kind", "blocks", "predicted_s",
    "voided_block_ids", "retry_tail"})
TERMINAL_KEYS = frozenset({"type", "block_id", "parent_block_id", "item_id", "model", "arm", "level"})


def _exact(record, keys, name):
    if type(record) is not dict or set(record) != keys:
        raise PackingRefusal(name, "record keys differ")


def _verify_roster(registration, roster):
    if not isinstance(registration, Registration):
        raise PackingRefusal("registration", "validated Registration required")
    _exact(roster, ROSTER_KEYS, "roster")
    original = roster["sha256"]
    candidate = copy.deepcopy(roster)
    try:
        candidate_digest = _digest(candidate)["sha256"]
    except (TypeError, ValueError) as exc:
        raise PackingRefusal("roster", "invalid canonical JSON") from exc
    if candidate_digest != original:
        raise PackingRefusal("roster", "digest mismatch")
    if roster["registration_sha256"] != registration.digest:
        raise PackingRefusal("roster", "registration digest mismatch")
    if roster["claim_ready"] != (registration.mode == "registered"):
        raise PackingRefusal("roster", "claim readiness mismatch")
    if (roster["parent_sha256"] is None) != (roster["registered_sha256"] is None):
        raise PackingRefusal("roster", "broken root digest chain")
    if roster["arm"] != registration.arm or roster["models"] != list(registration.role_to_model_id.values()):
        raise PackingRefusal("roster", "arm or model mismatch")
    for block in roster["blocks"]:
        _exact(block, BLOCK_KEYS, "block")
        if block["model"] not in roster["models"] or block["arm"] != roster["arm"] or block["level"] not in roster["levels"]:
            raise PackingRefusal("block", "cell identity mismatch")
    for envelope in roster["envelopes"]:
        _exact(envelope, ENVELOPE_KEYS, "envelope")
    for refusal in roster["terminal_refusals"]:
        _exact(refusal, TERMINAL_KEYS, "terminal refusal")


def _executed_gaps(roster):
    blocks = {block["block_id"]: block for block in roster["blocks"]}
    gaps = {}
    for level in roster["levels"]:
        means = []
        for model in roster["models"]:
            indices = [envelope["index"] for envelope in roster["envelopes"]
                       for bid in envelope["blocks"]
                       if blocks[bid]["model"] == model and blocks[bid]["level"] == level]
            means.append(sum(indices) / len(indices) if indices else None)
        try:
            gaps[level] = abs(means[0] - means[1])
        except TypeError:
            gaps[level] = None
    return gaps


def pack(registration, items_by_level, predicted_decode_s):
    """Pack a registered five-level roster, or a provisional pilot roster."""
    if not isinstance(registration, Registration):
        raise PackingRefusal("registration", "validated Registration required")
    models = list(registration.role_to_model_id.values())
    arm = registration.arm
    block_size = registration.block_size[arm]
    capacity = registration.interior_s - registration.guard_s
    levels = registration.levels
    if type(items_by_level) is not dict or set(items_by_level) != set(levels):
        raise PackingRefusal("items", "items do not match registered levels")
    blocks = []
    all_items = set()
    for level in levels:
        if type(items_by_level[level]) not in (list, tuple):
            raise PackingRefusal(level, "items must be ordered sequence")
        items = list(items_by_level[level])
        if len(items) != registration.n_per_level or any(type(item) is not str or not item for item in items):
            raise PackingRefusal(level, "item count or item ID invalid")
        if len(set(items)) != len(items) or all_items.intersection(items):
            raise PackingRefusal(level, "duplicate item")
        all_items.update(items)
        slices = [items[i:i + block_size] for i in range(0, len(items), block_size)]
        if len(slices) < registration.min_blocks_per_cell:
            raise PackingRefusal((models[0], arm, level), "fewer than required blocks")
        for model in models:
            for index, members in enumerate(slices):
                durations = [_duration(predicted_decode_s, model, item) for item in members]
                seconds = sum(durations)
                if seconds > capacity:
                    raise PackingRefusal((model, arm, level), "block exceeds envelope capacity")
                blocks.append({"block_id": f"{model}:{arm}:{level}:{index}", "model": model,
                    "arm": arm, "level": level, "items": members, "predicted_s": seconds,
                    "predicted_item_s": durations, "attempt": 0, "origin_attempt": 0, "retry_stage": "initial",
                    "parent_block_id": None, "superseded": False, "ceiling_violation": False})
    envelopes, gaps = _arrange(blocks, models, capacity, levels)
    for envelope in envelopes:
        envelope["voided_block_ids"] = []
        envelope["retry_tail"] = False
    for level in levels:
        for model in models:
            count = sum(bool(set(envelope["blocks"]).intersection(
                block["block_id"] for block in blocks if block["level"] == level and block["model"] == model))
                for envelope in envelopes)
            if count < registration.min_envelopes_per_cell:
                raise PackingRefusal((model, arm, level), "fewer than required envelopes")
    if registration.mode == "registered":
        for level in levels:
            if gaps[level] > registration.max_drift_lever_slots:
                raise PackingRefusal(level, "drift lever exceeds registered maximum")
    roster = {"schema": "joulewise.scored_roster.v2", "models": models, "arm": arm,
        "block_size": block_size, "interior_s": registration.interior_s, "guard_s": registration.guard_s,
        "cap_tokens_by_arm": registration.cap_tokens, "envelope_s": registration.envelope_s,
        "offset_s": registration.offset_s, "pitch_s": registration.pitch_s, "capacity_s": capacity,
        "levels": levels, "blocks": blocks, "envelopes": envelopes, "drift_lever_slots": gaps,
        "drift_exceeded": {level: False for level in levels}, "claim_ready": registration.mode == "registered",
        "registration_sha256": registration.digest, "registered_sha256": None,
        "parent_sha256": None, "terminal_refusals": []}
    return _digest(roster)


def _append(result, additions):
    tail_start = len(result["envelopes"])
    for extra in additions:
        tail = result["envelopes"][-1] if result["envelopes"] else None
        if (tail and tail["index"] >= tail_start and tail["retry_tail"] and
                tail["predicted_s"] + extra["predicted_s"] <= result["capacity_s"]):
            tail["blocks"].append(extra["block_id"])
            tail["predicted_s"] += extra["predicted_s"]
        else:
            result["envelopes"].append({"index": len(result["envelopes"]), "model": extra["model"],
                "kind": "loaded", "retry_tail": True, "blocks": [extra["block_id"]],
                "predicted_s": extra["predicted_s"], "voided_block_ids": []})


def requeue_overrun(registration, roster, block_id, failed_prediction_s):
    """Append retries; single-stage elapsed seconds are keyed by affected item ID."""
    _verify_roster(registration, roster)
    result = copy.deepcopy(roster)
    if result["registered_sha256"] is None:
        result["registered_sha256"] = roster["sha256"]
    result["parent_sha256"] = roster["sha256"]
    block = next((b for b in result["blocks"] if b["block_id"] == block_id), None)
    if block is None:
        raise PackingRefusal(block_id, "unknown block")
    if block["superseded"] or block["ceiling_violation"]:
        raise PackingRefusal(block_id, "block already superseded or terminal")
    source = next((e for e in result["envelopes"] if block_id in e["blocks"]), None)
    if source is None:
        raise PackingRefusal(block_id, "block is not scheduled")
    source["blocks"].remove(block_id)
    source["voided_block_ids"].append(block_id)
    source["predicted_s"] -= block["predicted_s"]
    additions = []
    if block["attempt"] == 0:
        if type(failed_prediction_s) not in (int, float) or not math.isfinite(failed_prediction_s) or failed_prediction_s <= 0:
            raise PackingRefusal(block_id, "invalid failed prediction")
        total_worst = sum(registration.cap_tokens[block["arm"]] *
            registration.s_per_token_upper[block["model"]][block["arm"]] +
            registration.prefill_s[block["model"]][block["arm"]] for _ in block["items"])
        if failed_prediction_s > total_worst:
            raise PackingRefusal(block_id, "derived worst case below failed prediction")
        block["retry_stage"] = "whole_block"
        block["attempt"] = 1
        additions = [block]
    elif block["attempt"] == 1:
        if type(failed_prediction_s) is not dict or set(failed_prediction_s) != set(block["items"]):
            raise PackingRefusal(block_id, "per-item failed predictions required")
        block["superseded"] = True
        for index, item in enumerate(block["items"]):
            worst = (registration.cap_tokens[block["arm"]] *
                registration.s_per_token_upper[block["model"]][block["arm"]] +
                registration.prefill_s[block["model"]][block["arm"]])
            failed = failed_prediction_s[item]
            if type(failed) not in (int, float) or not math.isfinite(failed) or failed <= 0 or worst < failed:
                raise PackingRefusal((block["model"], block["arm"], block["level"]), "derived worst case below failed prediction")
            if worst > result["capacity_s"]:
                raise PackingRefusal((block["model"], block["arm"], block["level"]), "single exceeds capacity")
            split = {**block, "block_id": f"{block_id}:single:{index}", "items": [item],
                "parent_block_id": block_id, "predicted_s": worst,
                "predicted_item_s": [block["predicted_item_s"][index]],
                "attempt": 2, "origin_attempt": 2, "retry_stage": "single_problem", "superseded": False}
            result["blocks"].append(split)
            additions.append(split)
    else:
        if type(failed_prediction_s) is not dict or block["items"][0] not in failed_prediction_s:
            raise PackingRefusal(block_id, "per-item elapsed seconds required")
        affected = [block]
        for mate_id in list(source["blocks"]):
            mate = next(b for b in result["blocks"] if b["block_id"] == mate_id)
            if mate["items"][0] in failed_prediction_s:
                affected.append(mate)
                source["blocks"].remove(mate_id)
                source["voided_block_ids"].append(mate_id)
                source["predicted_s"] -= mate["predicted_s"]
        if set(failed_prediction_s) != {entry["items"][0] for entry in affected}:
            raise PackingRefusal(block_id, "elapsed seconds do not match affected singles")
        for entry in affected:
            elapsed = failed_prediction_s[entry["items"][0]]
            if type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed <= 0:
                raise PackingRefusal(entry["block_id"], "invalid elapsed seconds")
            worst = (registration.cap_tokens[entry["arm"]] *
                registration.s_per_token_upper[entry["model"]][entry["arm"]] +
                registration.prefill_s[entry["model"]][entry["arm"]])
            if elapsed > worst and entry["retry_stage"] == "single_retry":
                entry["attempt"] += 1
                entry["retry_stage"] = "ceiling_violation"
                entry["ceiling_violation"] = True
                result["terminal_refusals"].append({"type": "ceiling_violation", "block_id": entry["block_id"],
                    "parent_block_id": entry["parent_block_id"], "item_id": entry["items"][0],
                    "model": entry["model"], "arm": entry["arm"], "level": entry["level"]})
            else:
                entry["attempt"] += 1
                if elapsed > worst:
                    entry["retry_stage"] = "single_retry"
                additions.append(entry)
    _append(result, additions)
    result["drift_lever_slots"] = _executed_gaps(result)
    if registration.mode == "registered":
        exceeded = {}
        for level, gap in result["drift_lever_slots"].items():
            try:
                exceeded[level] = gap > registration.max_drift_lever_slots
            except TypeError:
                exceeded[level] = True
        result["drift_exceeded"] = exceeded
    return _digest(result)
