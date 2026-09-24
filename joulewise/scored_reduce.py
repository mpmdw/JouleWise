"""Pure gross-block reduction of scored item rows.

Rows use ``item_id``, ``model_id`` (or ``model``), ``level``, ``arm``,
``block_id`` (or ``sub_block_id``), token counts, and ``outcome``.
Block windows use ``block_id`` and ``gross_j`` (or ``energy_gross_j``).
All fields unrelated to these windows, including idle padding, are ignored.
"""

from __future__ import annotations

import math


OUTCOMES = frozenset({"correct", "incorrect", "malformed", "truncated"})


def _field(row, *names):
    for name in names:
        if name in row:
            return row[name]
    raise ValueError(f"missing field: {names[0]}")


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def reduce(item_rows, block_windows):
    """Summarize each (model, arm, level) using gross block-window joules only."""
    windows = {}
    for window in block_windows:
        block_id = _field(window, "block_id", "sub_block_id")
        if block_id in windows:
            raise ValueError(f"duplicate block window: {block_id}")
        windows[block_id] = float(_number(_field(window, "gross_j", "energy_gross_j"), "gross_j"))
    cells = {}
    block_owner = {}
    seen_items = set()
    for row in item_rows:
        model = _field(row, "model_id", "model")
        arm = _field(row, "arm")
        level = _field(row, "level")
        item = _field(row, "item_id", "problem_id")
        block_id = _field(row, "block_id", "sub_block_id")
        outcome = _field(row, "outcome")
        if outcome not in OUTCOMES:
            raise ValueError(f"invalid outcome: {outcome!r}")
        if block_id not in windows:
            raise ValueError(f"missing gross block window: {block_id}")
        cell_key = (model, arm, level)
        if block_id in block_owner and block_owner[block_id] != cell_key:
            raise ValueError(f"block crosses cells: {block_id}")
        block_owner[block_id] = cell_key
        item_key = (cell_key, item)
        if item_key in seen_items:
            raise ValueError(f"duplicate attempt: {item_key}")
        seen_items.add(item_key)
        prompt = _number(_field(row, "prompt_tokens"), "prompt_tokens")
        generated = _number(_field(row, "generated_tokens", "emitted_tokens"), "generated_tokens")
        cell = cells.setdefault(cell_key, {"model": model, "arm": arm, "level": level,
                                           "attempts": 0, "correct": 0, "prompt_tokens": 0,
                                           "generated_tokens": 0, "cap_hits": 0, "blocks": []})
        cell["attempts"] += 1
        cell["correct"] += outcome == "correct"
        cell["cap_hits"] += outcome == "truncated"
        cell["prompt_tokens"] += prompt
        cell["generated_tokens"] += generated
        block = next((b for b in cell["blocks"] if b["block_id"] == block_id), None)
        if block is None:
            block = {"block_id": block_id, "gross_j": windows[block_id], "level": level, "items": []}
            cell["blocks"].append(block)
        block["items"].append({"item_id": item, "correct": outcome == "correct",
                               "generated_tokens": generated, "outcome": outcome})
    if set(windows) != set(block_owner):
        raise ValueError("orphan gross block window")
    for cell in cells.values():
        attempts, correct = cell["attempts"], cell["correct"]
        joules = sum(block["gross_j"] for block in cell["blocks"])
        generated = cell["generated_tokens"]
        cell["gross_j"] = joules
        cell["accuracy"] = correct / attempts
        cell["prompt_tokens_per_attempt"] = cell["prompt_tokens"] / attempts
        cell["generated_tokens_per_attempt"] = generated / attempts
        cell["tokens_per_attempt"] = generated / attempts
        cell["j_per_token"] = joules / generated if generated else None
        cell["j_per_correct"] = joules / correct if correct else None
        cell["cap_hit_fraction"] = cell["cap_hits"] / attempts
        cell["cap_bound"] = cell["cap_hit_fraction"] > 0.20
        cell["cap_bound_label"] = "cap-bound" if cell["cap_bound"] else ""
    return cells
