"""Frozen OSCTX experiment configuration and balanced block schedule."""
from __future__ import annotations

import itertools
import json
import random
from pathlib import Path

DEFAULT_CONFIG = Path(__file__).with_name("config.json")
STAGES = ("stage0", "U1", "U2", "S")


def load_config(path: str | Path | None = None) -> dict:
    with (Path(path) if path else DEFAULT_CONFIG).open() as stream:
        config = json.load(stream)
    if set(config["contexts"]) != {"D", "I", "SH", "B"}:
        raise ValueError("contexts must be D, I, SH, B")
    if config["sizes"]["u_blocks"] != 6:
        raise ValueError("a Williams stage must contain all six orders")
    if config["segments"]["lm_tokens"] != 256 or config["segments"]["lm_repeats"] != 3:
        raise ValueError("registered LM size is 3 x 256")
    return config


def williams_orders(seed: int, stage: str) -> list[tuple[str, ...]]:
    orders = list(itertools.permutations(("D", "I", "SH")))
    random.Random(f"{seed}:{stage}").shuffle(orders)
    return orders


def blocks(config: dict, stage: str) -> list[dict]:
    sizes = config["sizes"]
    if stage == "stage0":
        return [{"id": f"stage0-{i+1:02}", "state": "A", "arms": ["I", "SH"] if i % 2 == 0 else ["SH", "I"], "discard": False}
                for i in range(sizes["stage0_blocks"])]
    if stage in ("U1", "U2"):
        result = []
        if stage == "U1":
            result.append({"id": "U1-warmup", "state": "U", "arms": ["I"] * sizes["u_warmup_cells"], "discard": True})
        result += [{"id": f"{stage}-{i+1:02}", "state": "U", "arms": list(order), "discard": False}
                   for i, order in enumerate(williams_orders(config["seed"], stage))]
        if stage == "U1":
            result += [{"id": f"U1-B-{i+1:02}", "state": "U", "arms": ["B"], "discard": False}
                       for i in range(sizes["background_cells"])]
        return result
    if stage == "S":
        return [{"id": f"S-p{phase}-{condition}-{i+1:02}", "state": condition, "arms": ["I"], "discard": False,
                 "phase": phase}
                for phase, condition in enumerate(("U", "S", "U"))
                for i in range(sizes["sandwich_cells"])]
    raise ValueError(f"unknown stage {stage}")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")
