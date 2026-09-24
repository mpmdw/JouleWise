"""Strict gross-energy reduction of an executed scored roster."""

from __future__ import annotations

import math

from joulewise.scored_registration import Registration
from joulewise.scored_packer import _verify_roster, PackingRefusal


class ReductionRefusal(ValueError):
    """An item, window, or roster violates the scored reduction contract."""


OUTCOMES = frozenset({"correct", "incorrect", "malformed", "truncated"})
ROW_KEYS = frozenset({"item_id", "model_id", "arm", "level", "block_id", "attempt",
    "prompt_tokens", "generated_tokens", "outcome", "stop_reason", "truncated",
    "retry_stage", "parent_block_id"})
WINDOW_KEYS = frozenset({"block_id", "attempt", "gross_j"})


def _exact(record, keys, name):
    if type(record) is not dict or set(record) != keys:
        raise ReductionRefusal(f"{name} keys differ")


def _number(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ReductionRefusal(f"{name} must be finite and nonnegative")
    return value


def reduce(registration, roster, item_rows, block_windows):
    """Reduce active attempts; preserve terminal refusals and digest bindings."""
    if not isinstance(registration, Registration):
        raise ReductionRefusal("validated Registration required")
    try:
        _verify_roster(registration, roster)
    except PackingRefusal as exc:
        raise ReductionRefusal(str(exc)) from exc
    blocks = {block["block_id"]: block for block in roster["blocks"]}
    if len(blocks) != len(roster["blocks"]):
        raise ReductionRefusal("duplicate roster block")
    active = {bid for envelope in roster["envelopes"] for bid in envelope["blocks"]}
    if len(active) != sum(len(envelope["blocks"]) for envelope in roster["envelopes"]):
        raise ReductionRefusal("block scheduled more than once")
    if not active.issubset(blocks):
        raise ReductionRefusal("unknown scheduled block")
    terminal = {}
    for refusal in roster["terminal_refusals"]:
        if type(refusal["model"]) is not str or type(refusal["item_id"]) is not str:
            raise ReductionRefusal("invalid terminal identity")
        key = (refusal["model"], refusal["item_id"])
        if refusal["type"] != "ceiling_violation" or key in terminal:
            raise ReductionRefusal("invalid or duplicate terminal refusal")
        terminal[key] = refusal
    expected = {(block["model"], item) for block in roster["blocks"]
                if block["parent_block_id"] is None for item in block["items"]}
    windows = {}
    for window in block_windows:
        _exact(window, WINDOW_KEYS, "block window")
        bid = window["block_id"]
        attempt = window["attempt"]
        if type(bid) is not str or bid not in blocks or type(attempt) is not int:
            raise ReductionRefusal("unmatched block window")
        key = (bid, attempt)
        if key in windows:
            raise ReductionRefusal("duplicate block window")
        _number(window["gross_j"], "gross_j")
        block = blocks[bid]
        latest_window_attempt = block["attempt"] - 1 if block["ceiling_violation"] else block["attempt"]
        if (attempt < block["origin_attempt"] or attempt > latest_window_attempt or
                (bid not in active and not block["superseded"] and not block["ceiling_violation"])):
            raise ReductionRefusal("unmatched block window")
        windows[key] = window["gross_j"]
    active_windows = {(bid, blocks[bid]["attempt"]) for bid in active}
    if not active_windows.issubset(windows):
        raise ReductionRefusal("missing active gross window")
    cells = {}
    seen = set()
    row_blocks = set()
    for row in item_rows:
        _exact(row, ROW_KEYS, "item row")
        model, arm, level, item, bid = (row["model_id"], row["arm"], row["level"], row["item_id"], row["block_id"])
        if type(bid) is not str:
            raise ReductionRefusal("block ID must be text")
        if bid not in active or bid not in blocks:
            raise ReductionRefusal("row does not name an active block")
        block = blocks[bid]
        if (model, arm, level) != (block["model"], block["arm"], block["level"]) or item not in block["items"]:
            raise ReductionRefusal("row does not match roster block")
        if type(row["attempt"]) is not int or row["attempt"] != block["attempt"]:
            raise ReductionRefusal("row attempt mismatch")
        if row["retry_stage"] not in registration.retry_stages or row["retry_stage"] != block["retry_stage"]:
            raise ReductionRefusal("retry stage missing, unknown, or mismatched")
        if row["parent_block_id"] != block["parent_block_id"]:
            raise ReductionRefusal("parent block mismatch")
        if type(row["outcome"]) is not str or row["outcome"] not in OUTCOMES:
            raise ReductionRefusal("invalid outcome")
        prompt = _number(row["prompt_tokens"], "prompt_tokens")
        generated = _number(row["generated_tokens"], "generated_tokens")
        if type(prompt) is not int or type(generated) is not int:
            raise ReductionRefusal("token counts must be integers")
        capped = generated >= registration.cap_tokens[arm]
        if type(row["truncated"]) is not bool or row["truncated"] != capped:
            raise ReductionRefusal("truncated flag disagrees with token cap")
        if row["stop_reason"] not in ("stop", "length") or (row["stop_reason"] == "length") != capped:
            raise ReductionRefusal("stop reason disagrees with token cap")
        if row["outcome"] == "truncated" and not capped:
            raise ReductionRefusal("truncated outcome without token cap")
        if capped and row["outcome"] == "correct":
            raise ReductionRefusal("capped attempt cannot be correct")
        item_key = (model, item)
        if item_key not in expected or item_key in seen or item_key in terminal:
            raise ReductionRefusal("duplicate or unexpected item")
        seen.add(item_key)
        row_blocks.add(bid)
        cell_key = (model, arm, level)
        if cell_key not in cells:
            cells[cell_key] = {"model": model, "arm": arm, "level": level,
                "attempts": 0, "correct": 0, "prompt_tokens": 0, "generated_tokens": 0,
                "cap_hits": 0, "blocks": [], "retry_stage_counts": {}, "terminal_refusals": [],
                "registration_sha256": registration.digest, "roster_sha256": roster["sha256"],
                "drift_lever_slots": roster["drift_lever_slots"][level],
                "drift_exceeded": roster["drift_exceeded"][level]}
        cell = cells[cell_key]
        cell["attempts"] += 1
        cell["correct"] += row["outcome"] == "correct"
        cell["cap_hits"] += capped
        cell["prompt_tokens"] += prompt
        cell["generated_tokens"] += generated
        stage = row["retry_stage"]
        counts = cell["retry_stage_counts"]
        counts[stage] = counts[stage] + 1 if stage in counts else 1
        entry = next((entry for entry in cell["blocks"] if entry["block_id"] == bid), None)
        if entry is None:
            entry = {"block_id": bid, "attempt": block["attempt"],
                "gross_j": windows[(bid, block["attempt"])], "level": level,
                "items": [], "parent_block_id": block["parent_block_id"]}
            cell["blocks"].append(entry)
        entry["items"].append({"item_id": item, "correct": row["outcome"] == "correct",
            "generated_tokens": generated, "outcome": row["outcome"], "retry_stage": stage})
    if row_blocks != active or seen | set(terminal) != expected or seen & set(terminal):
        raise ReductionRefusal("roster items or active blocks incomplete")
    for refusal in terminal.values():
        key = (refusal["model"], refusal["arm"], refusal["level"])
        if key not in cells:
            cells[key] = {"model": key[0], "arm": key[1], "level": key[2],
                "attempts": 0, "correct": 0, "prompt_tokens": 0, "generated_tokens": 0,
                "cap_hits": 0, "blocks": [], "retry_stage_counts": {}, "terminal_refusals": [],
                "registration_sha256": registration.digest, "roster_sha256": roster["sha256"],
                "drift_lever_slots": roster["drift_lever_slots"][key[2]],
                "drift_exceeded": roster["drift_exceeded"][key[2]]}
        cells[key]["terminal_refusals"].append(refusal.copy())
        counts = cells[key]["retry_stage_counts"]
        counts["ceiling_violation"] = counts["ceiling_violation"] + 1 if "ceiling_violation" in counts else 1
    for cell in cells.values():
        attempts, correct = cell["attempts"], cell["correct"]
        joules = sum(block["gross_j"] for block in cell["blocks"])
        generated = cell["generated_tokens"]
        cell["gross_j"] = joules
        cell["accuracy"] = correct / attempts if attempts else None
        cell["prompt_tokens_per_attempt"] = cell["prompt_tokens"] / attempts if attempts else None
        cell["generated_tokens_per_attempt"] = generated / attempts if attempts else None
        cell["tokens_per_attempt"] = generated / attempts if attempts else None
        cell["j_per_token"] = joules / generated if generated else None
        cell["j_per_correct"] = joules / correct if correct else None
        cell["cap_hit_fraction"] = cell["cap_hits"] / attempts if attempts else None
        cell["cap_bound"] = (cell["cap_hit_fraction"] > registration.cap_bound_fraction) if attempts else False
        cell["cap_bound_label"] = "cap-bound" if cell["cap_bound"] else ""
    return cells
