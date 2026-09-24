"""Pure paired, block-aware inference for gross joules per correct answer."""

from __future__ import annotations

import math
import random


class BelowFloorError(ValueError):
    """A measured block window cannot clear the instrument floor."""


def _blocks(cell):
    blocks = {}
    for block in cell["blocks"]:
        items = {item["item_id"]: item for item in block["items"]}
        key = (block.get("level", cell["level"]), block.get("parent_block_id") or
               tuple(sorted(items, key=str)))
        if not items:
            raise ValueError("duplicate or empty block membership")
        if key in blocks:
            gross, existing, windows = blocks[key]
            if set(existing) & set(items):
                raise ValueError("duplicate block membership")
            blocks[key] = (gross + block["gross_j"], {**existing, **items}, windows + [block["gross_j"]])
        else:
            blocks[key] = (block["gross_j"], items, [block["gross_j"]])
    return blocks


def _quantile(values, probability):
    values = sorted(values)
    position = (len(values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    return values[lower] * (upper - position) + values[upper] * (position - lower)


def _ratio(energy8, correct8, energy17, correct17):
    if correct8 == 0 and correct17 == 0:
        return None
    if correct8 == 0:
        return math.inf
    if correct17 == 0:
        return 0.0
    if energy17 <= 0:
        return math.inf if energy8 > 0 else None
    return (energy8 / correct8) / (energy17 / correct17)


def _bounds(energy8, correct8, energy17, correct17, error8, error17):
    low = _ratio(max(0.0, energy8 - error8), correct8, energy17 + error17, correct17)
    # _ratio treats every nonpositive denominator as the same unbounded case.
    high = _ratio(energy8 + error8, correct8, energy17 - error17, correct17)
    return low, high


def _allocated_energy(gross, items, sampled):
    """Allocate a block's gross energy to sampled item draws."""
    total_tokens = sum(item["generated_tokens"] for item in items.values())
    if total_tokens == 0:
        return gross * len(sampled) / len(items)
    return gross * sum(items[item]["generated_tokens"] for item in sampled) / total_tokens


def ratio_interval(cell_8b, cell_1p7b, *, n_boot, seed, floor_j, anchor_j):
    """Bootstrap common blocks, then paired problems within each drawn block.

    A sampled block contributes its measured gross joules allocated to sampled
    attempts in proportion to their generated tokens. This allocation is only
    a bootstrap device; the point estimate uses untouched block gross energy.
    ``floor_j`` and ``anchor_j`` are nonnegative absolute bounds per block.
    """
    if isinstance(n_boot, bool) or not isinstance(n_boot, int) or n_boot < 1:
        raise ValueError("n_boot must be a positive integer")
    for name, value in (("floor_j", floor_j), ("anchor_j", anchor_j)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and nonnegative")
    blocks8, blocks17 = _blocks(cell_8b), _blocks(cell_1p7b)
    for cell in (cell_8b, cell_1p7b):
        if any(block["gross_j"] <= floor_j for block in cell["blocks"]):
            raise BelowFloorError("block window at or below instrument floor")
    # A split parent's identifier is model-specific; align it with the other
    # model's original membership by its complete item set.
    def by_membership(blocks):
        return {(key[0], tuple(sorted(value[1], key=str))): value for key, value in blocks.items()}
    blocks8, blocks17 = by_membership(blocks8), by_membership(blocks17)
    if not blocks8 or blocks8.keys() != blocks17.keys():
        raise ValueError("paired models must have identical block membership")
    keys = sorted(blocks8, key=str)
    strata = {}
    for key in keys:
        strata.setdefault(key[0], []).append(key)
    for key in keys:
        if set(blocks8[key][1]) != set(blocks17[key][1]):
            raise ValueError("unpaired problems")
    error8 = sum(len(blocks8[key][2]) for key in keys) * (floor_j + anchor_j)
    error17 = sum(len(blocks17[key][2]) for key in keys) * (floor_j + anchor_j)
    estimate = _ratio(cell_8b["gross_j"], cell_8b["correct"],
                      cell_1p7b["gross_j"], cell_1p7b["correct"])
    if estimate is None:
        raise ValueError("both cells have zero correct answers")
    point_low, point_high = _bounds(cell_8b["gross_j"], cell_8b["correct"],
                                    cell_1p7b["gross_j"], cell_1p7b["correct"], error8, error17)
    rng = random.Random(seed)
    lows, highs = [], []
    against_below = against_above = 0
    for _ in range(n_boot):
        energies = [0.0, 0.0]
        corrects = [0, 0]
        for level_keys in strata.values():
            for _ in level_keys:
                key = level_keys[rng.randrange(len(level_keys))]
                pair = (blocks8[key], blocks17[key])
                ids = sorted(pair[0][1], key=str)
                sampled = [ids[rng.randrange(len(ids))] for _ in ids]
                for model_index, (gross, items, windows) in enumerate(pair):
                    energy = _allocated_energy(gross, items, sampled)
                    energies[model_index] += energy
                    corrects[model_index] += sum(bool(items[item]["correct"]) for item in sampled)
        low, high = _bounds(energies[0], corrects[0], energies[1], corrects[1], error8, error17)
        lows.append(0.0 if low is None else low)
        highs.append(math.inf if high is None else high)
        against_below += high is None or high >= 1
        against_above += low is None or low <= 1
    interval = (min(point_low, _quantile(lows, 0.025)),
                max(point_high, _quantile(highs, 0.975)))
    return {"estimate": estimate, "interval": interval,
            "p_below": (1 + against_below) / (n_boot + 1),
            "p_above": (1 + against_above) / (n_boot + 1),
            "p_two_sided": min(1.0, 2 * min(1 + against_below, 1 + against_above) / (n_boot + 1)),
            "n_boot": n_boot, "_source": "ratio_interval"}


def _pool(cells, level):
    blocks = []
    for cell in cells:
        blocks += cell["blocks"]
    return {"level": level, "blocks": blocks,
            "gross_j": sum(c["gross_j"] for c in cells),
            "correct": sum(c["correct"] for c in cells)}


def decide(levels, *, arm, family, floor_j, anchor_j, alpha=0.05, n_boot=20000, seed=0):
    """Apply count-only sparse merges and Holm over one fixed five-level family.

    ``levels`` maps 1..5 to dictionaries with ``cell_8b`` and ``cell_1p7b``.
    A pooled hypothesis is reported once in ``groups``. Constituent level
    rows retain membership but do not inherit its decision.
    """
    if set(levels) != set(range(1, 6)):
        raise ValueError("one family must contain levels 1 through 5")
    if family not in {"primary", "secondary"}:
        raise ValueError("invalid decision family")
    for level, entry in levels.items():
        if "ratio" in entry:
            raise ValueError("unchecked ready ratios are not accepted")
        for name, model in (("cell_8b", "8B"), ("cell_1p7b", "1.7B")):
            cell = entry[name]
            if cell.get("arm") != arm or cell.get("model") != model or cell.get("level") != level:
                raise ValueError("cell role, arm, or level mismatch")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie between zero and one")
    groups = [[level] for level in range(1, 6)]

    def sparse(group):
        return any(sum(levels[level][name]["correct"] for level in group) < 3
                   for name in ("cell_8b", "cell_1p7b"))

    def merge(source, target):
        source_group = next((g for g in groups if source in g), None)
        target_group = next((g for g in groups if target in g), None)
        groups.remove(source_group)
        groups.remove(target_group)
        groups.append(sorted(source_group + target_group))

    # Registered order: high end 5→4→3, then low end 1→2→3.
    if sparse([5]) or sparse([4]):
        merge(5, 4)
        if sparse(next(g for g in groups if 5 in g)):
            merge(4, 3)
    if sparse([1]) or sparse([2]):
        merge(1, 2)
        if sparse(next(g for g in groups if 1 in g)):
            merge(2, 3)
    groups.sort(key=min)
    results = {}
    group_rows = []
    tests = []
    for group in groups:
        if sparse(group):
            ratio = None
        else:
            cells8 = _pool([levels[level]["cell_8b"] for level in group], tuple(group))
            cells17 = _pool([levels[level]["cell_1p7b"] for level in group], tuple(group))
            # The original level remains part of each block's membership key.
            ratio = ratio_interval(cells8, cells17, n_boot=n_boot,
                                   seed=seed, floor_j=floor_j, anchor_j=anchor_j)
        name = "–".join(str(level) for level in group)
        row = {"levels": group, "merged_level": name, "ratio": ratio,
               "estimable": bool(ratio),
               "status": "not resolved" if ratio else "not estimable",
               "decision": "not resolved" if ratio else "not estimable",
               "holm_significant": False}
        group_rows.append(row)
        for level in group:
            results[level] = row.copy() if len(group) == 1 else {
                "levels": group, "merged_level": name, "ratio": None,
                "estimable": False, "status": "not estimable", "decision": "not estimable",
                "holm_significant": False, "pooled_in": name}
        if ratio:
            tests.append((ratio["p_two_sided"], row, ratio))
    # Five is fixed even after merging: no smaller family is silently used.
    tests.sort(key=lambda entry: entry[0])
    still_rejecting = True
    for rank, (p_value, row, ratio) in enumerate(tests):
        significant = still_rejecting and p_value <= alpha / (5 - rank)
        still_rejecting = significant
        low, high = ratio["interval"]
        direction = ("8B cheaper" if high < 1 and ratio["p_below"] < ratio["p_above"] else
                     "1.7B cheaper" if low > 1 and ratio["p_above"] < ratio["p_below"] else
                     "not resolved")
        row["status"] = direction if significant else "not resolved"
        row["decision"] = row["status"]
        row["holm_significant"] = significant and direction != "not resolved"
        if len(row["levels"]) == 1:
            results[row["levels"][0]] = row.copy()
    crossover = None
    reason = None
    lower = [row for row in group_rows if row["status"] == "1.7B cheaper"]
    for row in group_rows:
        if row["status"] == "8B cheaper" and any(g["levels"][-1] < row["levels"][0] for g in lower):
            licenses = [g for g in lower if g["levels"][-1] < row["levels"][0]]
            if len(row["levels"]) > 1 or all(len(g["levels"]) > 1 for g in licenses):
                reason = "boundary_in_merged_group"
            else:
                crossover = row["levels"][0]
            break
    if (crossover is None and reason is None and
            any(len(row["levels"]) > 1 and
                any(g["levels"][-1] < row["levels"][-1] for g in lower)
                for row in group_rows)):
        reason = "boundary_in_merged_group"
    return {"levels": results, "groups": group_rows, "crossover_level": crossover,
            "crossover_reason": reason, "family_size": 5, "family": family,
            "can_carry_headline": family == "primary", "arm": arm}
