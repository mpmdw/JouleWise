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


def _palindrome(buckets, models):
    """Schedule model buckets symmetrically; empty slots preserve odd parity."""
    counts = {model: len(buckets[model]) for model in models}
    odd = [model for model in models if counts[model] % 2]
    if len(odd) == 2:
        counts[models[1]] += 1
    center = next((model for model in models if counts[model] % 2), None)
    remaining = {model: (counts[model] - (model == center)) // 2 for model in models}
    half = []
    while any(remaining.values()):
        eligible = [model for model in models if remaining[model]]
        chosen = next((model for model in eligible if not half or model != half[-1]), eligible[0])
        half.append(chosen)
        remaining[chosen] -= 1
    order = half + ([center] if center else []) + list(reversed(half))
    indexed = {model: iter(buckets[model]) for model in models}
    return [{"index": index, "model": model, "blocks": next(indexed[model], []),
             "predicted_s": 0.0} for index, model in enumerate(order)]


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
    envelopes = _palindrome(buckets, models)
    lookup = {block["block_id"]: block for block in blocks}
    for envelope in envelopes:
        envelope["predicted_s"] = sum(lookup[bid]["predicted_s"] for bid in envelope["blocks"])
    return envelopes


def pack(items_by_level, predicted_decode_s, models, arm, block_size, interior_s, guard_s):
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
                               "attempt": 0})
    roster = {"schema": "joulewise.scored_roster.v1", "models": models, "arm": arm,
              "block_size": block_size, "interior_s": interior_s, "guard_s": guard_s,
              "capacity_s": capacity, "levels": levels, "blocks": blocks,
              "envelopes": _arrange(blocks, models, capacity, levels)}
    return _digest(roster)


def requeue_overrun(roster, block_id):
    """Return a new roster; first overrun retries the block, second isolates items."""
    result = copy.deepcopy(roster)
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
        block["superseded"] = True
        additions = []
        for index, item in enumerate(block["items"]):
            split = {**block, "block_id": f"{block_id}:single:{index}", "items": [item],
                     "predicted_s": block["predicted_item_s"][index],
                     "predicted_item_s": [block["predicted_item_s"][index]],
                     "attempt": 2, "retry_stage": "single_problem"}
            split.pop("superseded", None)
            result["blocks"].append(split)
            additions.append(split)
    else:
        block["retry_stage"] = "single_problem"
        block["attempt"] += 1
        additions = [block]
    # Append only: capture indices already executed remain stable.
    for extra in additions:
        result["envelopes"].append({"index": len(result["envelopes"]), "model": extra["model"],
                                    "blocks": [extra["block_id"]], "predicted_s": extra["predicted_s"]})
    return _digest(result)
