"""Pure roster planning for scored, fixed-length power envelopes.

Inputs: ``items_by_level`` maps level to ordered problem IDs;
``predicted_decode_s`` maps model to problem ID to seconds (or uses
``(model, problem_id)`` keys). The returned JSON-compatible roster contains
blocks, envelopes, and a canonical SHA-256 excluding the digest field.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import random


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
    if (model, item) in predictions:
        value = predictions[(model, item)]
    else:
        value = predictions[model][item]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"invalid predicted duration for {model!r}, {item!r}")
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


def pack(items_by_level, predicted_decode_s, models, arm, block_size, interior_s, guard_s, *,
         registered_levels, cap_tokens_by_arm, envelope_s, offset_s, pitch_s):
    """Return a deterministic, spread-constrained roster or a typed refusal."""
    models = list(models)
    if len(models) != 2 or models[0] == models[1] or any(not isinstance(m, str) or not m for m in models):
        raise ValueError("exactly two distinct models are required")
    if not isinstance(block_size, int) or isinstance(block_size, bool) or block_size < 1:
        raise ValueError("block_size must be a positive integer")
    capacity = interior_s - guard_s
    if not math.isfinite(capacity) or capacity <= 0 or guard_s < 0:
        raise ValueError("invalid interior or guard")
    levels = sorted(items_by_level)
    if levels != sorted(registered_levels) or len(levels) != len(registered_levels):
        raise ValueError("items do not match registered levels")
    if arm not in cap_tokens_by_arm or not isinstance(cap_tokens_by_arm[arm], int) or cap_tokens_by_arm[arm] <= 0:
        raise ValueError("missing positive per-arm cap")
    if any(not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0
           for v in (envelope_s, pitch_s)) or not 0 <= offset_s < envelope_s:
        raise ValueError("invalid envelope timing")
    if not levels:
        raise ValueError("at least one level is required")
    blocks = []
    for level in levels:
        items = list(items_by_level[level])
        if len(set(items)) != len(items):
            raise ValueError(f"duplicate problem in level {level}")
        slices = [items[i:i + block_size] for i in range(0, len(items), block_size)]
        if len(slices) < 5:
            raise PackingRefusal((models[0], arm, level), "fewer than five blocks/envelopes")
        for model in models:
            for index, members in enumerate(slices):
                seconds = sum(_duration(predicted_decode_s, model, item) for item in members)
                if seconds > capacity:
                    raise PackingRefusal((model, arm, level), "block exceeds envelope capacity")
                blocks.append({"block_id": f"{model}:{arm}:{level}:{index}", "model": model,
                               "arm": arm, "level": level, "items": members,
                               "predicted_s": seconds, "predicted_item_s": [
                                   _duration(predicted_decode_s, model, item) for item in members],
                               "attempt": 0, "retry_stage": "initial"})
    envelopes, gaps = _arrange(blocks, models, capacity, levels)
    roster = {"schema": "joulewise.scored_roster.v1", "models": models, "arm": arm,
              "block_size": block_size, "interior_s": interior_s, "guard_s": guard_s,
              "cap_tokens_by_arm": cap_tokens_by_arm, "envelope_s": envelope_s,
              "offset_s": offset_s, "pitch_s": pitch_s,
              "capacity_s": capacity, "levels": levels, "blocks": blocks,
              "envelopes": envelopes, "drift_lever_slots": gaps}
    return _digest(roster)


def requeue_overrun(roster, block_id, *, worst_case_s_per_item=None):
    """Return a new roster; first overrun retries the block, second isolates items."""
    result = copy.deepcopy(roster)
    result.setdefault("registered_sha256", roster.get("registered_sha256", roster["sha256"]))
    result["parent_sha256"] = roster["sha256"]
    block = next((b for b in result["blocks"] if b["block_id"] == block_id), None)
    if block is None:
        raise KeyError(block_id)
    if block.get("superseded"):
        raise ValueError("block was already split")
    source = next((e for e in result["envelopes"] if block_id in e["blocks"]), None)
    if source is None:
        raise ValueError("block is not scheduled")
    source["blocks"].remove(block_id)
    source.setdefault("voided_block_ids", []).append(block_id)
    source["predicted_s"] -= block["predicted_s"]
    if block["attempt"] == 0:
        block["retry_stage"] = "whole_block"
        block["attempt"] = 1
        additions = [block]
    elif block["attempt"] == 1:
        if worst_case_s_per_item is None:
            raise ValueError("worst_case_s_per_item is required for singles")
        block["superseded"] = True
        additions = []
        for index, item in enumerate(block["items"]):
            worst = worst_case_s_per_item[item]
            if not isinstance(worst, (int, float)) or not math.isfinite(worst) or worst <= 0 or worst > result["capacity_s"]:
                raise PackingRefusal((block["model"], block["arm"], block["level"]), "single exceeds envelope capacity")
            split = {**block, "block_id": f"{block_id}:single:{index}", "items": [item],
                     "parent_block_id": block_id, "predicted_s": float(worst),
                     "predicted_item_s": [block["predicted_item_s"][index]],
                     "attempt": 2, "retry_stage": "single_problem"}
            split.pop("superseded", None)
            result["blocks"].append(split)
            additions.append(split)
    elif block["attempt"] == 2:
        block["attempt"] = 3
        block["retry_stage"] = "single_problem"
        additions = [block]
    else:
        block["retry_stage"] = "ceiling_violation"
        block["ceiling_violation"] = True
        block["attempt"] += 1
        result.setdefault("terminal_refusals", []).append({
            "type": "ceiling_violation", "block_id": block_id,
            "parent_block_id": block.get("parent_block_id"), "item_id": block["items"][0]})
        additions = []
    # Append only: capture indices already executed remain stable.
    tail_start = len(result["envelopes"])
    for extra in additions:
        tail = result["envelopes"][-1] if result["envelopes"] else None
        if (tail and tail["index"] >= tail_start and tail.get("retry_tail") and
                tail["predicted_s"] + extra["predicted_s"] <= result["capacity_s"]):
            tail["blocks"].append(extra["block_id"])
            tail["predicted_s"] += extra["predicted_s"]
        else:
            result["envelopes"].append({"index": len(result["envelopes"]), "model": extra["model"],
                                        "kind": "loaded", "retry_tail": True,
                                        "blocks": [extra["block_id"]], "predicted_s": extra["predicted_s"]})
    return _digest(result)
