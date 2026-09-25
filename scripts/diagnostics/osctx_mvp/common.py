"""Shared configuration and file conventions for the OS context diagnostic."""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_CONFIG = Path(__file__).with_name("config.json")


def load_config(path: str | Path | None = None) -> dict:
    with (Path(path) if path else DEFAULT_CONFIG).open() as stream:
        config = json.load(stream)
    if not config["states"] or not config["order"]:
        raise ValueError("states and order must be nonempty")
    if set(config["order"]) != set(config["contexts"]):
        raise ValueError("order must cover precisely the configured contexts")
    return config


def cell_name(state: str, context: str, number: int) -> str:
    return f"{state}.{context}.{number}"


def cells(config: dict, states: list[str] | None = None):
    for state in states or config["states"]:
        if state not in config["states"]:
            raise ValueError(f"unknown state {state}")
        counts = dict.fromkeys(config["contexts"], 0)
        for context in config["order"]:
            counts[context] += 1
            yield state, context, counts[context]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")
