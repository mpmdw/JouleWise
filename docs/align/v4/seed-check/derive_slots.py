#!/usr/bin/env python3
"""Independent R15 slot derivation; stdlib only, no series-builder imports.

Written and first run before opening the merged series manifest or builder.
Only the W1 kit/config JSON and the published seed law supply input bytes.
Model source/cache paths embedded in configs are opaque strings, never opened.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[4]
KIT = ROOT / "configs/campaigns/align_v4"
PAIRS = ("spam_filter_update", "bank_transfer_2")
D_MODEL = "qwen3.8-27b"


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def episode_seed(model, pair, index):
    # sampling.py: SHA256 of this compact JSON array, first 8 bytes big-endian.
    return int.from_bytes(hashlib.sha256(compact(
        ["align-p4-v1", model, "thinking_on", "shade/" + pair, index]
    )).digest()[:8], "big")


def slot(ordinal, pair, condition, index, model, role):
    return dict(ordinal=ordinal, task_pair=pair, condition=condition,
                seed_index=index, model_id=model, role=role,
                expected_episode_seed=episode_seed(model, pair, index))


def w1_slots():
    """Use config contents; cross-check kit metadata, never execute the kit."""
    plan = json.loads((KIT / "collection_plan.json").read_bytes())
    result = []
    for member in plan["members"]:
        path = Path(member["config_path"])
        if path.is_absolute() or path.parts[:4] != (
                "configs", "campaigns", "align_v4", "stages") or ".." in path.parts:
            raise ValueError("not a kit config path")
        raw = (ROOT / path).read_bytes()
        if hashlib.sha256(raw).hexdigest() != member["config_sha256"]:
            raise ValueError("W1 config digest mismatch")
        config = json.loads(raw)
        spec = json.loads(config["workload_profile"]["prompt_text"])
        model = next(tag.removeprefix("align-model=")
                     for tag in config["run_metadata"]["tags"]
                     if tag.startswith("align-model="))
        row = slot(member["ordinal"], spec["task_kwargs"]["task_pair"],
                   spec["condition"], spec["seed"], model, member["role"])
        if any(row[key] != member[key] for key in row):
            raise ValueError("W1 config and collection-plan identity differ")
        result.append(row)
    if [row["ordinal"] for row in result] != list(range(1, 19)):
        raise ValueError("W1 must have its original 18 members")
    return result


def derive():
    w1 = w1_slots()
    windows = [dict(window_id="W1", slots=w1)]
    # R15: independent per-pair streams; each window consumes eight per pair.
    for cohort, count, first in (("C", 8, 2), ("T", 3, 66)):
        next_index = dict.fromkeys(PAIRS, first)
        for number in range(1, count + 1):
            rows = [dict(row) for row in w1[:4]]
            rows.append(slot(5, PAIRS[0], "benign", 1, D_MODEL, "sentinel_early"))
            order = PAIRS if number % 2 else PAIRS[::-1]
            for offset in range(16):
                ordinal = offset + 6
                pair = order[offset % 2]
                condition = "sabotage" if ordinal in (9, 18) else "benign"
                index = next_index[pair]
                rows.append(slot(ordinal, pair, condition, index, D_MODEL,
                                 "held_out_" + condition))
                next_index[pair] += 1
            # W1's late D sentinel is itself a replay of W1 ordinal 5.
            rows.append(slot(22, PAIRS[0], "benign", 1, D_MODEL, "sentinel_late"))
            windows.append(dict(window_id=f"{cohort}{number}", slots=rows))
        if set(next_index.values()) != {first + 8 * count}:
            raise AssertionError("incorrect per-pair seed consumption")
    return windows


if __name__ == "__main__":
    output = (json.dumps(derive(), indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_bytes(output)
    elif len(sys.argv) == 1:
        sys.stdout.buffer.write(output)
    else:
        raise SystemExit("usage: derive_slots.py [output.json]")
