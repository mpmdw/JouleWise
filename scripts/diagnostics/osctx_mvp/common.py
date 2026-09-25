"""Frozen OSCTX experiment configuration and balanced block schedule."""
from __future__ import annotations

import itertools
import hashlib
import json
import random
from pathlib import Path

DEFAULT_CONFIG = Path(__file__).with_name("config.json")
STAGES = ("stage0", "stage0U", "U1", "U2", "S", "rehearsal", "C1", "P")


class LoadedConfig(dict):
    """Keep the exact bytes read by load_config available for stage opening."""


def load_config(path: str | Path | None = None) -> dict:
    source = Path(path) if path else DEFAULT_CONFIG
    raw = source.read_bytes()
    config = LoadedConfig(json.loads(raw))
    config.loaded_path = source.resolve()
    config.loaded_fingerprint = {"sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)}
    if set(config["contexts"]) != {"D", "I", "SH", "B"}:
        raise ValueError("contexts must be D, I, SH, B")
    if config["sizes"]["u_blocks"] < 6 or config["sizes"]["u_blocks"] % 6:
        raise ValueError("a Williams stage must contain all six orders per six blocks")
    raw_runs = config.get("runs_per_cell", 2)
    if type(raw_runs) is int:
        raw_runs = {stage: (0 if stage == "P" else 1 if stage in ("rehearsal", "C1") else raw_runs) for stage in STAGES}
    if not isinstance(raw_runs, dict) or set(raw_runs) - set(STAGES):
        raise ValueError("runs_per_cell must be an integer or stage mapping")
    config["runs_per_cell"] = {stage: raw_runs.get(stage, 0 if stage == "P" else 1 if stage in ("rehearsal", "C1") else 2) for stage in STAGES}
    if any(type(n) is not int or n < (0 if stage == "P" else 1)
           for stage, n in config["runs_per_cell"].items()):
        raise ValueError("runs_per_cell must contain nonnegative P and positive production counts")
    if config["sizes"]["stage0_blocks"] != 3:
        raise ValueError("stage0 needs three I/SH blocks")
    if config["runs_per_cell"]["stage0"] != 2:
        raise ValueError("stage0 needs two runs per cell")
    if config["runs_per_cell"]["stage0U"] != 2:
        raise ValueError("stage0U needs two runs per cell")
    if config["runs_per_cell"]["rehearsal"] != 1:
        raise ValueError("rehearsal needs one run per cell")
    if config["runs_per_cell"]["C1"] != 1:
        raise ValueError("C1 needs one run per cell")
    if config["runs_per_cell"]["P"] != 0:
        raise ValueError("P cannot run production")
    if config["segments"]["cpu_repeats"] != 3 or config["segments"]["cpu_seconds"] < 5:
        raise ValueError("continuation probes require three repeats of at least five seconds")
    if config.get("continuation_seed") != 20260925:
        raise ValueError("continuation seed must be 20260925")
    if config.get("rehearsal_state", "A") not in ("A", "U"):
        raise ValueError("rehearsal_state must be A or U")
    return config


def williams_orders(seed: int, stage: str) -> list[tuple[str, ...]]:
    orders = list(itertools.permutations(("D", "I", "SH")))
    random.Random(f"{seed}:{stage}").shuffle(orders)
    return orders


def blocks(config: dict, stage: str) -> list[dict]:
    sizes = config["sizes"]
    if stage == "C1":
        orders = [["I", "SH"]] * 3 + [["SH", "I"]] * 3
        random.Random(config["continuation_seed"]).shuffle(orders)
        return ([{"id": "C1-warmup", "state": "U", "arms": ["I"], "discard": True}]
                + [{"id": f"C1-{i+1:02}", "state": "U", "arms": list(order), "discard": False}
                   for i, order in enumerate(orders)])
    if stage == "P":
        return [{"id": f"P-{i+1:02}", "state": "U", "arms": [arm], "discard": False,
                 "probe_only": True}
                for i, arm in enumerate(("D", "B", "D", "B"))]
    if stage in ("stage0", "stage0U"):
        return [{"id": f"{stage}-{i+1:02}", "state": "U" if stage == "stage0U" else "A", "arms": ["I", "SH"] if i % 2 == 0 else ["SH", "I"], "discard": False}
                for i in range(sizes["stage0_blocks"])]
    if stage == "rehearsal":
        return [{"id": "rehearsal-01", "state": config.get("rehearsal_state", "A"),
                 "arms": ["I", "SH"], "discard": False}]
    if stage in ("U1", "U2"):
        result = []
        if stage == "U1":
            result.append({"id": "U1-warmup", "state": "U", "arms": ["I"] * sizes["u_warmup_cells"], "discard": True})
        result += [{"id": f"{stage}-{i+1:02}", "state": "U", "arms": list(order), "discard": False}
                   for i, order in enumerate(williams_orders(config["seed"], stage) * (sizes["u_blocks"] // 6))]
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
